import streamlit as st
import PyPDF2
from io import BytesIO
from nebius_inference import inference
import os
from datetime import datetime

# Load secrets
NEBIUS_API_KEY = st.secrets["NEBIUS_API_KEY"]
NORSK_GPT_API_KEY = st.secrets["NORSK_GPT_API_KEY"]
TEMPERATURE = st.secrets["TEMPERATURE"]


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


def load_patient_journals():
    journals_dir = "data/journals"
    journals = {}
    for filename in os.listdir(journals_dir):
        if filename.endswith(".pdf"):
            try:
                if " - " in filename:
                    # Original format: "Ola Hansen - 120384 12345.pdf"
                    name_part, numbers = filename.replace(".pdf", "").split(" - ")
                    dob, personal_number = numbers.split(" ")
                    search_string = f"{name_part.lower()} {dob} {personal_number}"
                else:
                    # New format: "patient_journal_PT10426.pdf"
                    search_string = filename.replace(".pdf", "").lower()

                journals[search_string] = os.path.join(journals_dir, filename)
            except ValueError:
                # Log error without showing warning
                print(f"Could not parse filename: {filename}")
                continue
    return journals


# Set up the Streamlit page
st.set_page_config(page_title="PDF Chat Assistant", layout="wide")
st.title("Ambulance assistant")

# Initialize session state variables
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "patient_journals" not in st.session_state:
    st.session_state.patient_journals = load_patient_journals()

# Sidebar content
with st.sidebar:
    st.subheader("Patient Search")
    search_query = st.text_input("Search by name or number:").lower()

    if search_query:
        # Search through available journals
        matching_journals = {
            key: path
            for key, path in st.session_state.patient_journals.items()
            if search_query in key
        }

        if matching_journals:
            selected_journal = st.selectbox(
                "Select patient journal:",
                options=list(matching_journals.keys()),
                format_func=lambda x: x.split(" ")[0].title()
                + " "
                + x.split(" ")[1].title(),  # Format name for display
            )

            if st.button("Load Journal"):
                # Load the selected PDF
                with open(matching_journals[selected_journal], "rb") as file:
                    st.session_state.pdf_text = extract_text_from_pdf(file)
                    # Generate summary
                    with st.spinner("Generating summary..."):
                        st.session_state.summary = get_pdf_summary(
                            st.session_state.pdf_text
                        )
                    st.rerun()
        else:
            st.warning("No matching patients found")

    if st.session_state.pdf_text is not None:
        if st.button("Clear current journal"):
            st.session_state.pdf_text = None
            st.session_state.summary = None
            st.session_state.chat_history = []
            st.rerun()

# Main content
if st.session_state.pdf_text is not None:
    # Display summary if available
    st.subheader("Document Summary")
    st.write(st.session_state.summary)

    # Chat interface
    st.subheader("Chat with your patient    ")
    user_question = st.text_input("Ask a question about your patient:")

    if st.button("Send"):
        if user_question:
            # Add user question to chat history
            st.session_state.chat_history.append(("user", user_question))

            # Get response
            with st.spinner("Getting response..."):
                response = get_document_response(
                    st.session_state.pdf_text, user_question
                )

            # Add response to chat history
            st.session_state.chat_history.append(("assistant", response))

    # Display chat history
    st.subheader("Chat History")
    for role, message in st.session_state.chat_history:
        if role == "user":
            st.write("You: " + message)
        else:
            st.write("Assistant: " + message)
            st.write("---")
