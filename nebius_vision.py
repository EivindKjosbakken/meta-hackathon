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

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def vision_inference(image_path: str, prompt: str) -> str:
    base64_image = encode_image(image_path)
    
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=float(temperature),
    )
    return completion.choices[0].message.content

# Example usage
if __name__ == "__main__":
    image_path = "picture.jpg"
    prompt = "What do you see in this image?"
    response = vision_inference(image_path, prompt)
    print(response)
