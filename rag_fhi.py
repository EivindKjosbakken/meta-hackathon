import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict
# from load_json import load_fhi_recommendations
import re
import json
from llama_index.core.schema import Document
from typing import List, Optional
import requests
import os
from datetime import datetime, timedelta

def is_health_recommendations_outdated(filename):
    # Check if file exists
    if not os.path.exists(filename):
        return True
    
    # Get file's modification time
    file_time = datetime.fromtimestamp(os.path.getmtime(filename))
    current_time = datetime.now()
    
    # Check if file is older than 1 day
    return (current_time - file_time) > timedelta(days=1)

def load_json_documents(json_path: str) -> List[Document]:
    """
    Load JSON file and convert entries to Documents with graceful error handling.
    Returns empty list if file cannot be read or parsed.
    
    Args:
        json_path: Path to JSON file
        
    Returns:
        List of Document objects
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            return []
            
        documents = []
        for item in data:
            # Use get() with empty string defaults for missing fields
            doc_id = item.get('id', '')
            title = item.get('tittel', '')
            text = item.get('tekst', '')
            
            content = f"Tittel: {title}\n\nInnhold:\n{text}"
            doc = Document(
                text=content,
                metadata={
                    "id": doc_id,
                    "title": title
                }
            )
            documents.append(doc)
            
        print(f"Loaded {len(documents)} documents")
        return documents
        
    except (json.JSONDecodeError, FileNotFoundError, Exception):
        return []




def load_fhi_recommendations():
    health_recommendations_file = "fhi-recommendations.json"

    if is_health_recommendations_outdated(health_recommendations_file):
        health_api_url = "https://api-qa.helsedirektoratet.no/innhold/anbefalinger"
        headers = {
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": "38221be99087442e97984dfaea18eebb"
        }

        # Make the GET request
        response = requests.get(health_api_url, headers=headers)

        # Save the response to a JSON file
        with open(health_recommendations_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Downloaded new health recommendations to {health_recommendations_file}")
    else:
        print(f"Health recommendations in {health_recommendations_file} are up to date (less than 1 day old)")

    return load_json_documents(health_recommendations_file)



def remove_html_tags(text):
    # Remove all HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    # Remove extra whitespace
    clean_text = ' '.join(clean_text.split())
    return clean_text

class FHI_recommendations:
    def __init__(self, collection_name: str = "fhi_recommendations"):
        """Initialize the document store with ChromaDB."""
        self.client = chromadb.Client()
        self.collection_name = collection_name
        # Use the default all-MiniLM-L6-v2 embedding function
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Create or get existing collection
        self.collection = self.client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

        docs = load_fhi_recommendations()  # Your existing function
        self.load(docs[:50])

    def load(self, documents: List[Dict[str, str]]) -> None:
        """
        Load documents into the ChromaDB collection.
        
        Args:
            documents: List of document dictionaries containing text and metadata
        """
        # Extract required fields from documents
        texts = [remove_html_tags(doc.text) for doc in documents]
        ids = [doc.metadata["id"] for doc in documents]
        metadatas = [{"title": doc.metadata["title"]} for doc in documents]
        
        # Add documents to collection
        self.collection.add(
            documents=texts,
            ids=ids,
            metadatas=metadatas
        )

    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        Query the document store for relevant documents.
        
        Args:
            query_text: The search query
            n_results: Number of results to return (default: 5)
            
        Returns:
            List of relevant documents with their metadata
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Format results into document-like structure
        documents = []
        for i in range(len(results['ids'][0])):
            documents.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i]
            })
            
        return documents
    
    def get_relevant_fhi_recommendations(self, query):
        # Query documents
        results = self.query(query)

        relevant_fhi_recommendations = "Helsedirektoratet Nasjonale krav og anbefalinger. Retningslinjer, råd, veiledere, forløp, rundskriv, standarder og Normen-dokumenter:\n\n"

        for i, doc in enumerate(results, 1):
            relevant_fhi_recommendations += f"Source {i}: {doc['metadata']['title']}\n"
            relevant_fhi_recommendations += f"Document ID: {doc['id']}\n"
            relevant_fhi_recommendations += f"Content: {doc['text'][:800]}\n"
            relevant_fhi_recommendations += "_______________\n\n"

        return relevant_fhi_recommendations


# Example usage:
if __name__ == "__main__":
    rag = FHI_recommendations()
    recommendations = rag.get_relevant_fhi_recommendations("Hva er behandlingsresistent hypertensjon?")
    print(recommendations)

