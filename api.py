from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from fuzzywuzzy import fuzz
import PyPDF2
from nebius_vision import vision_inference
from nebius_inference import inference
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint
from os import environ
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",  # Development
            "http://localhost:5173",  # Vite default
            "https://your-production-domain.com"  # Add your production domain
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"]
    }
})

# Swagger configuration
SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Patient Journal API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Create static folder if it doesn't exist
os.makedirs("static", exist_ok=True)

# Create swagger.json
swagger_config = {
    "swagger": "2.0",
    "info": {
        "title": "Patient Journal API",
        "description": "API for managing patient journals and health analysis",
        "version": "1.0",
    },
    "paths": {
        "/api/search_patients": {
            "get": {
                "summary": "Search for patients",
                "parameters": [
                    {
                        "name": "query",
                        "in": "query",
                        "type": "string",
                        "required": True,
                        "description": "Search query for patient name or ID",
                    }
                ],
                "responses": {"200": {"description": "List of matching patients"}},
            }
        },
        "/api/load_journal": {
            "get": {
                "summary": "Load a patient's journal",
                "parameters": [
                    {
                        "name": "patient_id",
                        "in": "query",
                        "type": "string",
                        "required": True,
                        "description": "Patient ID",
                    }
                ],
                "responses": {"200": {"description": "Journal text and summary"}},
            }
        },
        "/api/ask_question": {
            "post": {
                "summary": "Ask a question about a patient's journal",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"},
                                "text": {"type": "string"},
                            },
                        },
                    }
                ],
                "responses": {"200": {"description": "Answer to the question"}},
            }
        },
        "/api/analyze_image": {
            "post": {
                "summary": "Analyze a medical image",
                "consumes": ["multipart/form-data"],
                "parameters": [
                    {
                        "name": "image",
                        "in": "formData",
                        "type": "file",
                        "required": True,
                        "description": "Image file to analyze",
                    },
                    {
                        "name": "journal_text",
                        "in": "formData",
                        "type": "string",
                        "required": False,
                        "description": "Optional journal text for context",
                    },
                ],
                "responses": {"200": {"description": "Image analysis results"}},
            }
        },
    },
}

# Write swagger.json
with open("static/swagger.json", "w") as f:
    import json

    json.dump(swagger_config, f)

# Configure upload folders
UPLOAD_FOLDER = "data/uploads"
PATIENT_IMAGES_FOLDER = "data/patient_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PATIENT_IMAGES_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size


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
    prompt = f"""This is a patient journal, showing the medical history of the patient. Use this information if relevant when answering questions

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
                    name_part, numbers = filename.replace(".pdf", "").split(" - ")
                    dob, personal_number = numbers.split(" ")
                    search_string = f"{name_part.lower()} {dob} {personal_number}"
                else:
                    search_string = filename.replace(".pdf", "").lower()
                journals[search_string] = os.path.join(journals_dir, filename)
            except ValueError:
                print(f"Could not parse filename: {filename}")
                continue
    return journals


def fuzzy_search(query, choices, threshold=65):
    results = []
    for choice in choices:
        ratio = fuzz.partial_ratio(query.lower(), choice.lower())
        if ratio >= threshold:
            results.append((choice, ratio))
    return sorted(results, key=lambda x: x[1], reverse=True)


# Load patient journals on startup
patient_journals = load_patient_journals()


@app.route("/api/search_patients", methods=["GET"])
def search_patients():
    query = request.args.get("query", "").lower()
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    journal_keys = list(patient_journals.keys())
    matching_results = fuzzy_search(query, journal_keys)

    return jsonify(
        {
            "matches": [
                {"name": key, "score": score} for key, score in matching_results[:3]
            ]
        }
    )


@app.route("/api/load_journal", methods=["GET"])
def load_journal():
    patient_id = request.args.get("patient_id")
    if not patient_id or patient_id not in patient_journals:
        return jsonify({"error": "Invalid patient_id"}), 400

    try:
        with open(patient_journals[patient_id], "rb") as file:
            text = extract_text_from_pdf(file)
            summary = get_pdf_summary(text)
            return jsonify({"text": text, "summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ask_question", methods=["POST"])
def ask_question():
    data = request.json
    if not data or "question" not in data or "text" not in data:
        return jsonify({"error": "Question and text are required"}), 400

    response = get_document_response(data["text"], data["question"])
    return jsonify({"response": response})


@app.route("/api/analyze_image", methods=["POST"])
def analyze_image():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(f"patient_photo_{timestamp}.jpg")
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Create a temporary file for analysis
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            file.seek(0)
            tmp_file.write(file.read())
            tmp_path = tmp_file.name

        # Analyze the image
        health_prompt = """Please analyze this image for any visible health issues or concerns. 
        Focus on:
        1. Any visible symptoms
        2. Skin conditions
        3. Physical abnormalities
        4. Signs of distress or discomfort
        
        Provide a professional medical observation based on what you can see."""

        analysis = vision_inference(tmp_path, health_prompt)

        # If journal text is provided, search for relevant information
        journal_text = request.form.get("journal_text")
        relevant_info = None
        if journal_text:
            relevant_info = search_relevant_health_info(journal_text, analysis)

        # Clean up temporary file
        os.unlink(tmp_path)

        return jsonify(
            {"filename": filename, "analysis": analysis, "relevant_info": relevant_info}
        )

if __name__ == '__main__':
    # Use PORT environment variable if available (for Render deployment)
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 
