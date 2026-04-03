from app.config import OpenAISettings
from openai import OpenAI

def create_openai_client() -> OpenAI:
    return OpenAI(api_key=OpenAISettings.api_key)