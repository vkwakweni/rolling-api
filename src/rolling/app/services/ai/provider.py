from abc import ABC, abstractmethod
from typing import Any
import json

from ollama._types import ResponseError

from rolling.app.config import get_ollama_api_settings
from rolling.app.exceptions import AIProviderModelError


class AIProvider(ABC):
    """
    A base class for interfacing with the AI service.

    To work with a specific AI service, there must be a class that inherits from this base class. The child classes will
    structure the payloads for the AI services.
    """
    @abstractmethod
    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Send a provider-specific request to the model backend and return a
        normalised raw response shape for the application to process.
        """
        raise NotImplementedError
    

class MockAIProvider(AIProvider):
    """
    A mock provider class for testing the AI provider interface.
    """

    def generate(self) -> dict[str, Any]:
        """
        Send a provider-specific request to the model backend and return a
        normalised raw response shape for the application to process.
        """
        return {"report_text": "This is a mock AI-generated report.",
                "summary_text": "This is a mock AI-generated summary."}
    

class OpenAIProvider(AIProvider):
    """
    A child class of AIProvider that interfaces with the OpenAI API for AI analysis report generation.
    """
    def __init__(self, client: Any):
        """Initialise an OpenAI provider."""
        self.client = client

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Send a provider-specific request to the OpenAI API backend and return a
        normalised raw response shape for the application to process.

        Args:
            request (dict[str, Any]): A request to an AI service to generate an analysis report.

        Returns:
            dict[str, Any]: A normalised response from the AI service.
                - "report_text": the raw report text of the AI-generated report.
                - "summary_text": the raw summary text of the AI-generated report.
        """
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
        """
        Normalises the output from the AI service so that other components can use the response.

        Args:
            response (Any): Output from the AI service.

        Returns:
            dict[str, Any]: A dictionary of normalised output from the AI service.
                - "report_text": the raw report text of the AI-generated report.
                - "summary_text": the raw summary text of the AI-generated report.

        Raises:
            ValueError: If the raw text is empty; if the response was not valid JSON; if the raw report text was empty.
        """
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
    """
    A child class of AIProvider that interfaces with the Ollama API for AI analysis report generation.
    """
    def __init__(self, client: Any):
        """Initialise an Ollama provider."""
        self.client = client
        self.settings = get_ollama_api_settings()

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Send a provider-specific request to the OpenAI API backend and return a
        normalised raw response shape for the application to process.

        The structure of the response from the Ollama provider is:
            {
                "model": "codellama:python",
                "created_at": "...",
                "message": {
                    "role": "assistant",
                    "content": "{\"report_text\":\"...\",\"summary_text\":\"...\"}"
                    },
                "done": true
            }

        Args:
            request (dict[str, Any]): A request to an AI service to generate an analysis report.

        Returns:
            dict[str, Any]: A normalised response from the AI service.
                - "report_text": the raw report text of the AI-generated report.
                - "summary_text": the raw summary text of the AI-generated report.

        Raises:
            ollama._types.ResponseError: If the request to the Ollama API failed.
            ConnectionError: If the service is not accessible.
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
        """
        Normalises the output from the AI service so that other components can use the response.

        Args:
            response (Any): Output from the AI service.

        Returns:
            dict[str, Any]: A dictionary of normalised output from the AI service.
                - "report_text": the raw report text of the AI-generated report.
                - "summary_text": the raw summary text of the AI-generated report.

        Raises:
            ValueError: If the raw text is empty; if the response was not valid JSON; if the raw report text was empty.
        """
        raw_text = response.message.content
        if not raw_text:
            raise ValueError("Ollama API response did not contain message content.")
        
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError("Ollama API response was not valid JSON.")
        
        report_text = parsed.get("report_text")
        summary_text = parsed.get("summary_text")

        if not report_text:
            raise ValueError("Ollama API response did not contain report_text.")
        
        return {"report_text": report_text,
                "summary_text": summary_text}
