import os
import time
from google.genai import errors
from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.config import GEMINI_MODEL

load_dotenv()
gemini_client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_structured(prompt:str, schema, temprature:float=0.2,max_tries=3):
    for attempt in range(1,max_tries+1):
        try:
            response=gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=temprature
                )
            )
            return schema.model_validate_json(response.text)
        except errors.ServerError:
            if attempt==max_tries:
                raise
            time.sleep(2**attempt)


def generate_text(prompt: str, temperature: float = 0.3, max_retries: int = 3) -> str:
    for attempt in range(1, max_retries + 1):
        try:
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature),
            )
            return response.text

        except errors.ServerError:
            if attempt == max_retries:
                raise
            time.sleep(2 ** attempt)