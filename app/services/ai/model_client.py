from typing import Any

from app.models.ai import AIPrompt, AIModelOutput
from app.services.ai.provider import AIProvider

class AIModelClient:
    def __init__(self, model_name: str, provider: AIProvider):
        self.model_name = model_name
        self.provider = provider

    def generate_report(self,
                        prompt_payload: AIPrompt
                        ) -> AIModelOutput:
        provider_request = self._build_provider_request(prompt_payload)
        provider_response = self.provider.generate(provider_request)
        return self._normalise_provider_response(provider_response)

    def _build_provider_request(self, prompt_payload: AIPrompt) -> dict:
        return {"model": self.model_name,
                "system_prompt": prompt_payload.system_prompt,
                "user_prompt": prompt_payload.user_prompt,
                "tools": prompt_payload.tools}
    
    def _normalise_provider_response(self, provider_response: dict) -> AIModelOutput:
        return AIModelOutput(model_name=self.model_name,
                             report_text=provider_response["report_text"],
                             summary_text=provider_response.get("summary_text"))
