from abc import ABC, abstractmethod
from typing import Any
import json

from ollama._types import ResponseError

from app.config import get_ollama_api_settings
from app.exceptions import AIProviderModelError


class AIProvider(ABC):
    @abstractmethod
    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Send a provider-specific request to the model backend and return a
        normalised raw response shape for the application to process.
        """
        raise NotImplementedError
    

class MockAIProvider(AIProvider):
    def generate(self) -> dict[str, Any]:
        return {"report_text": "This is a mock AI-generated report.",
                "summary_text": "This is a mock AI-generated summary."}
    

class OpenAIProvider(AIProvider):
    def __init__(self, client: Any):
        self.client = client

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        response = self.client.responses.create(model=request["model_name"],
                                                input=[
                                                    {"role": "system",
                                                     "content": request["system_prompt"]},
                                                    {"role": "user",
                                                     "content": request["user_prompt"]}
                                                ],
                                                tools=request.get("tools", []))
        return self._normalise_response(response)
    
    def _normalise_response(self, response: Any) -> dict[str, Any]:
        raw_text = getattr(response, "output_text", None)

        if not raw_text:
            raise ValueError("OpenAI response did not contain output text.")
        
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError("OpenAI response was not valid JSON") from e
        
        report_text = parsed.get("report_text")
        summary_text = parsed.get("summary_text")

        if not report_text:
            raise ValueError("OpenAI response did not contain report_text")
        
        return {"report_text": report_text,
                "summary_text": summary_text}
    
class OllamaProvider(AIProvider):
    def __init__(self, client: Any):
        self.client = client
        self.settings = get_ollama_api_settings()

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Response will look like:
        {
            "model": "codellama:python",
            "created_at": "...",
            "message": {
                "role": "assistant",
                "content": "{\"report_text\":\"...\",\"summary_text\":\"...\"}"
            },
            "done": true
        }
        """
        try:
            # response is of type ChatResponse
            response = self.client.chat(model=request["model_name"],
                                        messages=[{"role": "system",
                                                "content": request["system_prompt"]},
                                                {"role": "user",
                                                    "content": request["user_prompt"]}],
                                        tools=request.get("tools", []),
                                    format="json")
        except ResponseError as e:
            raise AIProviderModelError(f"Ollama API request failed with status {e.status_code}: {e}") from e
        except ConnectionError as e:
            raise ConnectionError(f"{e}. If already installed and accessible, check configuration values.") from e

        return self._normalise_response(response)
    
    def _normalise_response(self, response) -> dict[str, Any]:
        raw_text = response.message.content
        if not raw_text:
            raise ValueError("Ollama response did not contain message content.")
        
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError("Ollama response was not valid JSON.")
        
        report_text = parsed.get("report_text")
        summary_text = parsed.get("summary_text")

        if not report_text:
            raise ValueError("Ollama response did not contain report_text.")
        
        return {"report_text": report_text,
                "summary_text": summary_text}
