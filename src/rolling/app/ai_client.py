import requests
from openai import OpenAI
from ollama import Client as OllamaClient

from rolling.app.config import OpenAISettings, OllamaSettings

def create_openai_client() -> OpenAI:
    """Creates a new OpenAI client using custom settings."""
    return OpenAI(api_key=OpenAISettings.api_key)

def create_ollama_client() -> OllamaClient:
    """Creates a new Ollama API client using custom settings."""
    return OllamaClient(host=OllamaSettings.host,
                        headers=OllamaSettings.headers)