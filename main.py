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


def get_journal_summary(text):
    prompt = f"""This is a patient journal, showing the medical history of the patient. Return 3 main points that are most relevant to the patient's health, for emergency responders to know.
{text}

Please make the summary concise but include all important points.
Only return the summary, no other text."""
    return inference(prompt)



def get_emergency_log_summary(patient_info):
    """given patient name - personal number, retrieve summary of emergency call log"""
    # first load the log
    patient_info = "Kari Nordmann – 250795 67890"
    log_path = os.path.join("data", "emergency_call_logs", f"{patient_info}.txt")
    log_text = open(log_path, "r").read()
    prompt = f"""This is an emergency call log, showing the patient's emergency call history. Return 3 main points that are most relevant to the patient's health, for emergency responders to know.
{log_text}

Please make the summary concise but include all important points.
Only return the summary, no other text."""
    return inference(prompt)



def get_document_response(text, question, images=None):
    base_prompt = f"""
                This is a patient journal, showing the medical history of the patient. Use this information if relevant when answering questions.
                {text}

                Please answer this question: {question}

                Base your answer only on the information provided in the document and images (if any). If the answer cannot be found in the provided information, please say so.
                """
    print("NUM IMAGES", len(images))
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
st.set_page_config(page_title="Ambulance Assistant", layout="wide")

# Initialize session state variables
if "step" not in st.session_state:
    st.session_state.step = 1
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "patient_journals" not in st.session_state:
    st.session_state.patient_journals = load_patient_journals()
if "patient_images" not in st.session_state:
    st.session_state.patient_images = []
if "additional_info" not in st.session_state:
    st.session_state.additional_info = ""
if "show_camera" not in st.session_state:
    st.session_state.show_camera = False

# Create three columns for the step indicators
col1, col2, col3 = st.columns(3)

# Style for the active and inactive steps
active_style = "background-color: #0066cc; color: white; padding: 10px; border-radius: 5px; text-align: center;"
inactive_style = "background-color: #e6e6e6; padding: 10px; border-radius: 5px; text-align: center;"

with col1:
    st.markdown(f"<div style='{active_style if st.session_state.step == 1 else inactive_style}'>1. Patient Search</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div style='{active_style if st.session_state.step == 2 else inactive_style}'>2. Assessment</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div style='{active_style if st.session_state.step == 3 else inactive_style}'>3. Analysis & Chat</div>", unsafe_allow_html=True)

st.markdown("---")

# Step 1: Patient Search
if st.session_state.step == 1:
    st.title("Patient Search")
    search_query = st.text_input("Search by name or number:").lower()

    if search_query:
        journal_keys = list(st.session_state.patient_journals.keys())
        matching_results = fuzzy_search(search_query, journal_keys)

        if matching_results:
            top_matches = matching_results[:3]
            matching_journals = {
                key: st.session_state.patient_journals[key]
                for key, score in top_matches
            }

            selected_journal = st.selectbox(
                "Select patient journal:",
                options=[key for key, score in top_matches],
                format_func=lambda x: f"{x.split(' ')[0].title()} {x.split(' ')[1].title()}",
            )

            if st.button("Load Patient Data"):
                with open(matching_journals[selected_journal], "rb") as file:
                    st.session_state.pdf_text = extract_text_from_pdf(file)
                    patient_info = os.path.basename(file.name).replace(".pdf", "")
                    st.session_state.patient_info = get_emergency_log_summary(patient_info)
                    with st.spinner("Analyzing patient emergency call log and journal..."):
                        st.session_state.summary = get_journal_summary(st.session_state.pdf_text)
                    st.rerun()

        else:
            st.warning("No matching patients found")

    # Show summaries if available
    if st.session_state.pdf_text is not None:
        st.subheader("📞 Recent Emergency Calls")
        st.error(
            """
            ### 🚨 Emergency Call History
            {}
            """.format(st.session_state.patient_info)
        )
        
        st.subheader("📋 Journal Summary")
        st.info(st.session_state.summary)

        if st.button("Continue to Assessment"):
            st.session_state.step = 2
            st.rerun()

# Step 2: Assessment
elif st.session_state.step == 2:
    st.title("Patient Assessment")
    
    # Additional information text area
    st.subheader("Additional Information")
    st.session_state.additional_info = st.text_area(
        "Enter any additional observations or notes:",
        value=st.session_state.additional_info,
        height=100
    )

    st.subheader("Patient Photos")
    if st.button("Toggle Camera"):
        st.session_state.show_camera = not st.session_state.show_camera
        st.rerun()

    if st.session_state.show_camera:
        camera_image = st.camera_input("Take a picture")
        if camera_image:
            with st.spinner("Processing and saving image..."):
                os.makedirs("data/patient_images", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f"data/patient_images/patient_photo_{timestamp}.jpg"
                with open(image_path, "wb") as f:
                    f.write(camera_image.getbuffer())
                st.session_state.patient_images.append(camera_image)
                st.session_state.show_camera = False
                st.rerun()

    if st.session_state.patient_images:
        st.write("Captured patient photos:")
        cols = st.columns(4)
        images_to_remove = []

        for idx, image in enumerate(st.session_state.patient_images):
            col_idx = idx % 4
            with cols[col_idx]:
                st.image(image, caption=f"Photo {idx + 1}", width=150)
                if st.button("❌", key=f"delete_{idx}"):
                    images_to_remove.append(idx)

        for idx in sorted(images_to_remove, reverse=True):
            st.session_state.patient_images.pop(idx)
            st.rerun()

        if st.button("Clear all photos"):
            st.session_state.patient_images = []
            st.rerun()

    if st.button("Analyze Case"):
        if len(st.session_state.patient_images) == 0:
            st.warning("Please take at least one photo before proceeding.")
        else:
            st.session_state.step = 3
            st.rerun()

# Step 3: Analysis & Chat
else:
    st.title("Analysis & Chat")
    
    with st.spinner("Analyzing all patient data..."):
        analysis_prompt = f"""
        You are an expert medical professional.
        The images are taken on-scene from an ambulance helping the patient with what might be a medical emergency.
        Analyze the patient's medical journal, current images, and the following additional information:
        
        ADDITIONAL NOTES:
        {st.session_state.additional_info}
        
        Provide a structured assessment with clear action points for the ambulance personnel.

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

        Please provide clear, actionable recommendations based on the findings."""

        analysis = vision_inference(
            st.session_state.patient_images,
            analysis_prompt,
        )

        st.subheader("Analysis Results")
        st.write(analysis)

    st.markdown("---")

    # Chat interface
    st.subheader("Chat with Assistant")
    user_question = st.text_input("Ask a question about the patient:")

    if st.button("Send"):
        if user_question:
            st.session_state.chat_history.append(("user", user_question))
            with st.spinner("Getting response..."):
                response = get_document_response(
                    st.session_state.pdf_text,
                    user_question,
                    images=st.session_state.patient_images
                )
            st.session_state.chat_history.append(("assistant", response))

    if st.session_state.chat_history:
        for role, message in st.session_state.chat_history:
            if role == "user":
                st.write("You: " + message)
            else:
                st.write("Assistant: " + message)
                st.write("---")

# Add a "Start Over" button that's always visible at the bottom
if st.button("Start Over"):
    st.session_state.step = 1
    st.session_state.pdf_text = None
    st.session_state.summary = None
    st.session_state.chat_history = []
    st.session_state.patient_images = []
    st.session_state.additional_info = ""
    st.session_state.show_camera = False
    st.rerun()
