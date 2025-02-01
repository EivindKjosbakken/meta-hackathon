import streamlit as st
import PyPDF2
from io import BytesIO
from nebius_inference import inference

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


# Set up the Streamlit page
st.set_page_config(page_title="PDF Chat Assistant", layout="wide")
st.title("PDF Document Chat Assistant")

# Initialize session state variables
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Move file upload to sidebar
with st.sidebar:
    uploaded_file = st.file_uploader("Upload your PDF document", type=["pdf"])
    # Replace image uploader with camera input
    camera_image = st.camera_input("Take a picture")

    if camera_image is not None:
        st.image(camera_image, caption='Captured Image', use_column_width=True)

    if st.session_state.pdf_text is not None:
        if st.button("Process another document"):
            st.session_state.pdf_text = None
            st.session_state.summary = None
            st.session_state.chat_history = []
            st.experimental_rerun()

# Main content
if uploaded_file is not None and st.session_state.pdf_text is None:
    # Extract text from PDF
    st.session_state.pdf_text = extract_text_from_pdf(uploaded_file)

    # Generate summary
    with st.spinner("Generating summary..."):
        st.session_state.summary = get_pdf_summary(st.session_state.pdf_text)

# Display summary if available
if st.session_state.summary:
    st.subheader("Document Summary")
    st.write(st.session_state.summary)

    # Chat interface
    st.subheader("Chat with your document")
    user_question = st.text_input("Ask a question about your document:")

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
