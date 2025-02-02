from os import environ
from dotenv import load_dotenv
from openai import OpenAI
import base64
from PIL import Image
import io

load_dotenv()

api_key = environ.get("NEBIUS_API_KEY")
temperature = environ.get("TEMPERATURE", 0.1)

MODEL = "llava-hf/llava-1.5-7b-hf"

assert api_key is not None, "NEBIUS_API_KEY is not set"
assert temperature is not None, "TEMPERATURE is not set"

client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key=api_key,
)


def encode_image(image_input, target_size=(512, 512)):
    # If the input is already a base64 string, return it directly
    if isinstance(image_input, str) and image_input.startswith("data:image"):
        return image_input.split(",")[1] if "," in image_input else image_input

    # Handle Streamlit UploadedFile objects
    if hasattr(image_input, "getvalue"):
        image_data = image_input.getvalue()
    # If it's a file path, read it
    elif isinstance(image_input, (str, bytes)):
        with open(image_input, "rb") as image_file:
            image_data = image_file.read()
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    # Open and resize the image
    try:
        img = Image.open(io.BytesIO(image_data))
        img = img.convert('RGB')  # Convert to RGB mode
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Save the resized image to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to process image input: {e}")


def vision_inference(image_paths, prompt, max_tokens=500):
    # Ensure image_paths is a list
    if not isinstance(image_paths, list):
        image_paths = [image_paths]

    # Create content list with prompt
    content = [{"type": "text", "text": prompt}]

    # Process each image
    for image_path in image_paths:
        try:
            base64_image = encode_image(image_path)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                }
            )
        except Exception as e:
            print(f"Warning: Failed to process image {image_path}: {e}")
            continue

    # Only proceed if we have at least one successfully processed image
    if len(content) < 2:  # Just the prompt, no images
        raise ValueError("No images were successfully processed")

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": content}],
            temperature=float(temperature),
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error during API call: {e}")
        raise


# # Example usage
# if __name__ == "__main__":
#     image_path = "picture.jpg"
#     prompt = "What do you see in this image?"
#     response = vision_inference(image_path, prompt)
#     print(response)
