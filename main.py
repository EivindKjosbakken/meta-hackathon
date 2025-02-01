import streamlit as st
import PyPDF2
from io import BytesIO
from nebius_inference import inference
import os
from datetime import datetime
from fuzzywuzzy import fuzz
from nebius_vision import vision_inference

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


def get_document_response(text, question, images=None):
    base_prompt = f"""This is a patient journal, showing the medical history of the patient. Use this information if relevant when answering questions.

{text}

Please answer this question: {question}

Base your answer only on the information provided in the document and images (if any). If the answer cannot be found in the provided information, please say so."""

    if images:
        try:
            # Create a temporary directory if it doesn't exist
            import tempfile
            temp_dir = tempfile.gettempdir()
            
            # Get temporary file paths for the images
            image_paths = []
            for idx, image in enumerate(images):
                temp_path = os.path.join(temp_dir, f"temp_image_{idx}.jpg")
                with open(temp_path, "wb") as f:
                    f.write(image.getbuffer())
                image_paths.append(temp_path)

            # Use vision inference when images are present
            response = vision_inference(image_paths, base_prompt)

            # Clean up temporary files
            for path in image_paths:
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Error removing temporary file {path}: {e}")

            return response
        except Exception as e:
            st.error(f"Error processing images: {e}")
            # Fallback to text-only response
            return inference(base_prompt)
    else:
        # Use regular inference when no images
        return inference(base_prompt)


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


def fuzzy_search(query, choices, threshold=65):
    """
    Perform fuzzy search on a list of choices and return matches above threshold.
    """
    results = []
    for choice in choices:
        ratio = fuzz.partial_ratio(query.lower(), choice.lower())
        if ratio >= threshold:
            results.append((choice, ratio))
    return sorted(results, key=lambda x: x[1], reverse=True)


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
        # Fuzzy search through available journals
        journal_keys = list(st.session_state.patient_journals.keys())
        matching_results = fuzzy_search(search_query, journal_keys)

        if matching_results:
            # Limit to top 3 matches
            top_matches = matching_results[:3]
            matching_journals = {
                key: st.session_state.patient_journals[key]
                for key, score in top_matches
            }

            # Show match scores in the selection
            selected_journal = st.selectbox(
                "Select patient journal:",
                options=[key for key, score in top_matches],
                format_func=lambda x: f"{x.split(' ')[0].title()} {x.split(' ')[1].title()}",
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
# Display summary if available
st.subheader("Document Summary")
if st.session_state.pdf_text is not None:
    st.write(st.session_state.summary)
else:
    st.write(
        "No journal loaded. Please search and load a patient journal from the sidebar."
    )

# Add camera capture functionality
st.subheader("Take Patient Photos")

# Initialize session state for storing multiple images if not exists
if "patient_images" not in st.session_state:
    st.session_state.patient_images = []
if "show_camera" not in st.session_state:
    st.session_state.show_camera = False

# Add button to toggle camera
if st.button("Toggle Camera"):
    st.session_state.show_camera = not st.session_state.show_camera
    st.rerun()

# Show camera only when toggled on
if st.session_state.show_camera:
    camera_image = st.camera_input("Take a picture")

    if camera_image:
        # Show loading spinner while processing
        with st.spinner("Processing and saving image..."):
            # Create a directory for storing images if it doesn't exist
            os.makedirs("data/patient_images", exist_ok=True)

            # Generate timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"data/patient_images/patient_photo_{timestamp}.jpg"

            # Save the captured image
            with open(image_path, "wb") as f:
                f.write(camera_image.getbuffer())

            # Add image to session state
            st.session_state.patient_images.append(camera_image)

            st.success("Image saved successfully!")
            # Remove automatic camera toggle
            st.session_state.show_camera = False
            st.rerun()

# Display all captured images in a grid layout
if st.session_state.patient_images:
    st.write("Captured patient photos:")

    # Create a grid layout with 4 columns
    cols = st.columns(4)

    # Create a list to store indices of images to remove
    images_to_remove = []

    for idx, image in enumerate(st.session_state.patient_images):
        col_idx = idx % 4  # Determine which column to place the image
        with cols[col_idx]:
            # Display image with reduced size
            st.image(image, caption=f"Photo {idx + 1}", width=150)
            # Add delete button for each image
            if st.button("❌", key=f"delete_{idx}"):
                images_to_remove.append(idx)

    # Remove marked images (in reverse order to maintain correct indices)
    for idx in sorted(images_to_remove, reverse=True):
        st.session_state.patient_images.pop(idx)
        st.rerun()

    # Add button to clear all images
    if st.button("Clear all photos"):
        st.session_state.patient_images = []
        st.rerun()

    # Add analyze button
    if st.button("Analyze Patient Images and Journal"):
        if st.session_state.pdf_text is None:
            st.warning("Please load a patient journal before analyzing.")
        else:
            with st.spinner("Analyzing patient data..."):
                analysis_prompt = """You are an expert medical professional.
                The images are taken on-scene from an ambulance helping the patient with what might be a medical emergency.
                Analyze the patient's medical journal and current images and provide a structured assessment with clear action points for the ambulance personel.

                ASSESSMENT:
                1. Critical Findings:
                   - Identify immediate life-threatening conditions
                   - Note vital sign abnormalities
                   - Document concerning physical findings from images
                
                2. Medical History Context:
                   - List relevant past conditions
                   - Note current medications
                   - Highlight allergies and contraindications
                
                ACTION POINTS:
                1. Immediate Actions Required:
                   - List specific interventions needed
                   - Prioritize by urgency (immediate/urgent/non-urgent)
                
                2. Monitoring Requirements:
                   - Specify vital signs to track
                   - Define monitoring intervals
                
                3. Treatment Plan:
                   - Recommend medications with dosages
                   - Specify care procedures
                
                4. Transport/Referral Decisions:
                   - Determine appropriate destination
                   - Specify level of care needed
                
                5. Additional Resources Needed:
                   - List required equipment/specialists
                   - Identify backup support needed

                Please provide clear, actionable recommendations based on the findings."""

                analysis = get_document_response(
                    st.session_state.pdf_text,
                    analysis_prompt,
                    images=st.session_state.patient_images,
                )

                st.subheader("Analysis Results")
                st.write(analysis)

# Chat interface
st.subheader("Chat with your patient")
user_question = st.text_input("Ask a question about your patient:")

if st.button("Send"):
    if user_question:
        if st.session_state.pdf_text is None:
            st.warning("Please load a patient journal first to ask questions.")
        else:
            # Add user question to chat history
            st.session_state.chat_history.append(("user", user_question))

            # Get response using both text and images
            with st.spinner("Getting response..."):
                response = get_document_response(
                    st.session_state.pdf_text,
                    user_question,
                    images=(
                        st.session_state.patient_images
                        if st.session_state.patient_images
                        else None
                    ),
                )

            # Add response to chat history
            st.session_state.chat_history.append(("assistant", response))

# Display chat history
st.subheader("Chat History")
if st.session_state.chat_history:
    for role, message in st.session_state.chat_history:
        if role == "user":
            st.write("You: " + message)
        else:
            st.write("Assistant: " + message)
            st.write("---")
else:
    st.write("No chat history yet.")
