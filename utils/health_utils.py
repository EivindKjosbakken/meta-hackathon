import tempfile
from nebius_vision import vision_inference
from nebius_inference import inference

def analyze_health_image(image_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(image_data.getvalue())
        tmp_path = tmp_file.name
    
    health_prompt = """Please analyze this image for any visible health issues or concerns. 
    Focus on:
    1. Any visible symptoms
    2. Skin conditions
    3. Physical abnormalities
    4. Signs of distress or discomfort
    
    Provide a professional medical observation based on what you can see."""
    
    return vision_inference(tmp_path, health_prompt)

def search_relevant_health_info(pdf_text, analysis):
    prompt = f"""Given the following health analysis from a patient's photo:

{analysis}

And this medical journal/document content:

{pdf_text}

Please find and summarize any relevant information from the document that relates to the observed symptoms or conditions."""

    return inference(prompt) 