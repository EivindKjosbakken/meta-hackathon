import PyPDF2
from nebius_inference import inference

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def get_pdf_summary(text):
    prompt = f"""Please provide a comprehensive summary of the following text:
    
{text}

Please make the summary concise but include all important points."""

    return inference(prompt)

def get_document_response(text, question):
    prompt = f"""Given the following document content:

{text}

Please answer this question: {question}

Base your answer only on the information provided in the document. If the answer cannot be found in the document, please say so."""

    return inference(prompt) 