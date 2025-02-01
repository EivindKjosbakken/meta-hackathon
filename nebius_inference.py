from os import environ
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = environ.get("NEBIUS_API_KEY")
temperature = environ.get("TEMPERATURE", 0.0)

# MODEL = "meta-llama/Llama-3.3-70B-Instruct"
MODEL = "meta-llama/Llama-3.3-70B-Instruct-fast"

assert api_key is not None, "NEBIUS_API_KEY is not set"
assert temperature is not None, "TEMPERATURE is not set"

client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key=api_key,
)


def inference(prompt: str) -> str:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=float(temperature),
    )
    return completion.choices[0].message.content


inference("hi, how are you?")
