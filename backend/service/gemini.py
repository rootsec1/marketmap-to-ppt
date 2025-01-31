import google.generativeai as genai
import json

from PIL import Image

# Local
from constants import GEMINI_API_KEY


genai.configure(api_key=GEMINI_API_KEY)

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-exp-1206",
    generation_config=generation_config
)


def prompt_gemini(prompt: str, file_path: str = None) -> str:
    parts = [prompt]
    if file_path:
        parts.append(Image.open(file_path))
    response = model.generate_content(parts)
    try:
        return json.loads(response.text.strip())  # Ensure valid JSON output
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "raw_output": response.text.strip()}
