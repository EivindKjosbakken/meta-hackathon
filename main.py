import nltk 
nltk.download("stopwords", download_dir="./")
import streamlit as st
import PyPDF2
from io import BytesIO
from nebius_inference import inference
import os
from datetime import datetime
from fuzzywuzzy import fuzz
from nebius_vision import vision_inference
from rag_fhi import FHI_recommendations
from tts import text_to_speech

# ------------------------------
# 1. PAGE CONFIG & CUSTOM STYLES
# ------------------------------

st.set_page_config(page_title="Ambulance Assistant", layout="centered")

# Inject custom CSS to improve the visual appearance for mobile
st.markdown(
    """
    <style>
    /* Overall body styling */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #333;
        margin: 0;
        padding: 0;
    }

    /* Card style for grouping content */
    .card {
        background-color: #fff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* Primary button style override */
    .stButton button {
        background-color: #0066cc !important;
        color: #fff !important;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        margin: 5px 0;
    }

    /* Margin tweaks for smaller screens */
    @media (max-width: 600px) {
        .card {
            margin: 10px;
            padding: 10px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------
# 2. HELPER FUNCTIONS
# ------------------------------

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
    """Given patient name - personal number, retrieve summary of emergency call log."""
    try:
        log_path = os.path.join("data", "emergency_call_logs", f"{patient_info}.txt")
        log_text = open(log_path, "r").read()
    except FileNotFoundError:
        return "No previous emergency calls recorded for this patient."
    except Exception as e:
        print(f"Error reading emergency log: {e}")
        return "Unable to retrieve emergency call history."

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
    if images:
        try:
            import tempfile

            temp_dir = tempfile.gettempdir()
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
        # Regular text-only inference
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

# Function to display step indicators vertically
def render_step_indicator(current_step):
    style_active = """
        background-color: #0066cc;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    """
    style_inactive = """
        background-color: #e6e6e6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    """

    steps = [
        ("Step 1: Patient Search", 1),
        ("Step 2: Assessment", 2),
        ("Step 3: Analysis & Chat", 3),
    ]

    for label, number in steps:
        if number == current_step:
            st.markdown(f"<div style='{style_active}'>{label}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='{style_inactive}'>{label}</div>", unsafe_allow_html=True)

# Chat bubble renderer
def chat_bubble(message, sender="user"):
    # Different color for user vs. assistant
    color = "#e1f5fe" if sender == "user" else "#c8e6c9"
    align = "right" if sender == "user" else "left"
    return f"""
    <div style="
        background-color: {color}; 
        padding: 10px; 
        border-radius: 10px;
        margin: 5px; 
        text-align: {align}; 
        max-width: 80%;
        ">
        {message}
    </div>
    """

# ------------------------------
# 3. SESSION STATE INIT
# ------------------------------

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
if "rag" not in st.session_state:
    st.session_state.rag = FHI_recommendations()
if "patient_info" not in st.session_state:
    st.session_state.patient_info = ""

# ------------------------------
# 4. PAGE STRUCTURE
# ------------------------------

# Main Title
st.markdown("<h2 style='text-align:center;'>🚑 Ambulance Assistant</h2>", unsafe_allow_html=True)

# Vertical Step Indicator
render_step_indicator(st.session_state.step)

st.markdown("---")

# ------------------------------
# STEP 1: PATIENT SEARCH
# ------------------------------
if st.session_state.step == 1:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.title("🔍 Patient Search")
        search_query = st.text_input("Search by name or number:").lower()

        if search_query:
            journal_keys = list(st.session_state.patient_journals.keys())
            matching_results = fuzzy_search(search_query, journal_keys)

            if matching_results:
                top_matches = matching_results[:3]
                matching_journals = { key: st.session_state.patient_journals[key] for key, _ in top_matches }

                selected_journal = st.selectbox(
                    "Select patient journal:",
                    options=[key for key, _ in top_matches],
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
                st.warning("No matching patients found.")

        if st.session_state.pdf_text is not None:
            st.subheader("📞 Recent Emergency Calls")
            st.error(f"### 🚨 Emergency Call History\n{st.session_state.patient_info}")

            st.subheader("📋 Journal Summary")
            st.info(st.session_state.summary)

            # Add audio version button
            if st.button("🔊 Listen to Audio Version"):
                audio_text = f"""
                Emergency Call History: {st.session_state.patient_info}
                
                Journal Summary: {st.session_state.summary}
                """
                text_to_speech(audio_text)

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

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------
# STEP 2: ASSESSMENT
# ------------------------------
elif st.session_state.step == 2:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
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

        # Display captured images
        if st.session_state.patient_images:
            st.write("Captured patient photos:")
            # Display in columns or stacked
            cols = st.columns(2)
            images_to_remove = []

            for idx, image in enumerate(st.session_state.patient_images):
                col_idx = idx % 2
                with cols[col_idx]:
                    st.image(image, caption=f"Photo {idx + 1}", width=150)
                    if st.button(f"❌ Remove Photo {idx + 1}", key=f"delete_{idx}"):
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

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------
# STEP 3: ANALYSIS & CHAT
# ------------------------------
else:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        with st.spinner("Analyzing all patient data..."):
            # Get relevant FHI recommendations
            fhi_recommendations = st.session_state.rag.get_relevant_fhi_recommendations(
                st.session_state.additional_info
            )

            # Summarize recommendations
            summary_prompt = f"""
            Please summarize the following health recommendations in a clear and concise way, 
            focusing on the most relevant points for this emergency situation. 
            Format your response as follows:

            SUMMARY:
            [Your summary of the key points]

            SOURCES:
            - List each source title and its key recommendation

            Original recommendations:
            {fhi_recommendations}
            """
            recommendations_summary = inference(summary_prompt)

            # Main analysis prompt
            analysis_prompt = f"""
            You are an expert medical professional.
            The images are taken on-scene from an ambulance helping the patient with what might be a medical emergency.

            Consider these relevant health recommendations:
            {recommendations_summary}

            Analyze the patient's medical journal, current images, and the following additional information:

            ADDITIONAL NOTES FROM AMBULANCE PERSONNEL ON SCENE:
            {st.session_state.additional_info}

            Patient journal (medical history):
            {st.session_state.pdf_text}

            Emergency call log:
            {st.session_state.patient_info}

            Provide a structured assessment with clear action points for the ambulance personnel.

            1. Key insights (headline 1, two - three bullet points)
            2. Action points (headline 2, two - three bullet points)

            Respond in the following format:
            ## 🔑 Key insights
            - Bullet point 1
            - Bullet point 2
            ## ⚡ Action points
            - Bullet point 1
            - Bullet point 2

            Make the analysis concise and to the point.
            """

            # Use vision inference for final analysis
            analysis = vision_inference(
                st.session_state.patient_images,
                analysis_prompt,
            )

            # Display analysis
            st.write(analysis)

            # Add audio version for analysis
            if st.button("🔊 Listen to Analysis"):
                text_to_speech(analysis)

            # Display recommendations summary
            st.subheader("Relevant Health Recommendations")
            st.info(recommendations_summary)

            # Add audio version for recommendations
            if st.button("🔊 Listen to Recommendations"):
                text_to_speech(recommendations_summary)

            with st.expander("View Original Recommendations"):
                st.write(fhi_recommendations)

        st.markdown("</div>", unsafe_allow_html=True)

    # --------------
    # CHAT INTERFACE
    # --------------
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
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
                st.experimental_rerun()

        # Display conversation with chat bubbles
        if st.session_state.chat_history:
            for role, message in st.session_state.chat_history:
                st.markdown(chat_bubble(message, sender=role), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------
# OPTIONAL: START OVER
# ------------------------------
# if st.button("Start Over"):
#     st.session_state.step = 1
#     st.session_state.pdf_text = None
#     st.session_state.summary = None
#     st.session_state.chat_history = []
#     st.session_state.patient_images = []
#     st.session_state.additional_info = ""
#     st.session_state.show_camera = False
#     st.session_state.patient_info = ""
#     st.experimental_rerun()
