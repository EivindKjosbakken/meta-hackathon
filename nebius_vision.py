from os import environ
from dotenv import load_dotenv
from openai import OpenAI
import base64

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


def encode_image(image_input):
    # If the input is already a base64 string, return it directly
    if isinstance(image_input, str) and image_input.startswith("data:image"):
        # Extract the base64 part if it's a data URL
        return image_input.split(",")[1] if "," in image_input else image_input

    # Handle Streamlit UploadedFile objects
    if hasattr(image_input, "getvalue"):
        return base64.b64encode(image_input.getvalue()).decode("utf-8")

    # If it's a file path, read and encode it
    try:
        if isinstance(image_input, (str, bytes)):
            with open(image_input, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")
    except Exception as e:
        raise ValueError(f"Failed to process image input: {e}")


def vision_inference(image_inputs, prompt: str) -> str:
    # Ensure image_inputs is a list
    if not isinstance(image_inputs, list):
        image_inputs = [image_inputs]

    # Create content list with prompt
    content = [{"type": "text", "text": prompt}]

    # Process each image
    for image_input in image_inputs:
        try:
            base64_image = encode_image(image_input)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                }
            )
        except Exception as e:
            print(f"Warning: Failed to process image {image_input}: {e}")
            continue

    # Only proceed if we have at least one successfully processed image
    if len(content) < 2:  # Just the prompt, no images
        raise ValueError("No images were successfully processed")

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": content}],
            temperature=float(temperature),
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
