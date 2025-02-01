import streamlit as st
from utils.pdf_utils import extract_text_from_pdf, get_pdf_summary, get_document_response
from utils.health_utils import analyze_health_image, search_relevant_health_info

# Load secrets
NEBIUS_API_KEY = st.secrets["NEBIUS_API_KEY"]
NORSK_GPT_API_KEY = st.secrets["NORSK_GPT_API_KEY"]
TEMPERATURE = st.secrets["TEMPERATURE"]

# Set up the Streamlit page with custom styling
st.set_page_config(page_title="Medical Document Assistant", layout="wide")

# Custom CSS with responsive design
st.markdown("""
    <style>
    /* Base styles */
    .main {
        padding: 1rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 5px;
        background-color: #4CAF50;
        color: white;
        margin: 0.5rem 0;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .chat-message {
        padding: 0.8rem;
        border-radius: 5px;
        margin-bottom: 0.8rem;
        word-wrap: break-word;
    }
    .user-message {
        background-color: #e6f3ff;
    }
    .assistant-message {
        background-color: #f0f0f0;
    }
    
    /* Responsive styles */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        .chat-message {
            padding: 0.5rem;
            margin-bottom: 0.5rem;
        }
        /* Make sure text doesn't overflow on small screens */
        .stMarkdown, .stText {
            word-wrap: break-word;
        }
        /* Adjust image sizes for mobile */
        .stImage img {
            max-width: 100%;
            height: auto;
        }
    }
    
    /* Custom container for better mobile spacing */
    .mobile-container {
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title with responsive styling
st.markdown("<h1 style='text-align: center; color: #2E4053; font-size: clamp(1.5rem, 4vw, 2.5rem);'>Medical Document Assistant</h1>", unsafe_allow_html=True)

# Initialize session state
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_camera" not in st.session_state:
    st.session_state.show_camera = False
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "document"  # or "camera"

# Sidebar (collapses to top menu on mobile)
with st.sidebar:
    st.markdown("### 📄 Document Upload")
    uploaded_file = st.file_uploader("Upload your medical document", type=["pdf"])
    
    if st.session_state.pdf_text is not None:
        st.markdown("---")
        if st.button("🔄 Process New Document"):
            st.session_state.pdf_text = None
            st.session_state.summary = None
            st.session_state.chat_history = []
            st.experimental_rerun()

# Mode selection for mobile (Document/Camera toggle)
mode_col1, mode_col2 = st.columns(2)
with mode_col1:
    if st.button("📄 Document View", use_container_width=True):
        st.session_state.view_mode = "document"
with mode_col2:
    if st.button("📸 Camera View", use_container_width=True):
        st.session_state.view_mode = "camera"

# Process uploaded document
if uploaded_file is not None and st.session_state.pdf_text is None:
    with st.spinner("📑 Processing document..."):
        st.session_state.pdf_text = extract_text_from_pdf(uploaded_file)
        st.session_state.summary = get_pdf_summary(st.session_state.pdf_text)

# Main content area
if st.session_state.view_mode == "camera":
    # Camera section
    st.markdown("### 📸 Camera")
    camera_image = st.camera_input("Take a picture")
    
    if camera_image is not None:
        st.image(camera_image, caption="Captured Image", use_column_width=True)
        
        with st.spinner("🔍 Analyzing image..."):
            analysis = analyze_health_image(camera_image)
        
        st.markdown("### 🏥 Health Analysis Results")
        st.info(analysis)

        if st.session_state.pdf_text:
            with st.spinner("🔎 Searching medical records..."):
                relevant_info = search_relevant_health_info(st.session_state.pdf_text, analysis)
            st.markdown("### 📋 Relevant Medical Information")
            st.success(relevant_info)

else:  # Document view
    if st.session_state.summary:
        st.markdown("### 📝 Document Summary")
        st.info(st.session_state.summary)
        
        st.markdown("### 💬 Chat with your document")
        user_question = st.text_input("Ask a question:")
        
        if st.button("📤 Send", use_container_width=True):
            if user_question:
                st.session_state.chat_history.append(("user", user_question))
                with st.spinner("Thinking..."):
                    response = get_document_response(st.session_state.pdf_text, user_question)
                st.session_state.chat_history.append(("assistant", response))

        # Chat history
        if st.session_state.chat_history:
            st.markdown("### 📜 Chat History")
            for role, message in st.session_state.chat_history:
                if role == "user":
                    st.markdown(f"""
                        <div class="chat-message user-message">
                            <b>You:</b> {message}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="chat-message assistant-message">
                            <b>Assistant:</b> {message}
                        </div>
                    """, unsafe_allow_html=True)
# Add some bottom padding for mobile
st.markdown("<div style='height: 50px'></div>", unsafe_allow_html=True)

