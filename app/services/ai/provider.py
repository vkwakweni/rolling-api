from abc import ABC, abstractmethod
from typing import Any
import json

class AIProvider(ABC):
    @abstractmethod
    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Send a provider-specific request to the model backend and return a
        normalised raw response shape for the application to process.
        """
        raise NotImplementedError
    

class MockAIProvider(AIProvider):
    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        return {"report_text": "This is a mock AI-generated report.",
                "summary_text": "This is a mock AI-generated summary."}
    

class OpenAIProvider(AIProvider):
    def __init__(self, client: Any):
        self.client = client

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        response = self.client.responses.create(model=request["model"],
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
            parsed = json.loads(raw_text) # TODO investigate what else could end up here
        except json.JSONDecodeError as e:
            raise ValueError("OpenAI response was not valid JSON") from e
        
        report_text = parsed.get("report_text")
        summary_text = parsed.get("summary_text")

        if not report_text:
            raise ValueError("OpenAI response did not contain report_text")
        
        return {"report_text": report_text,
                "summary_text": summary_text}
