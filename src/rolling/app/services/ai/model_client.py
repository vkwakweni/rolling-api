from typing import Any

from rolling.app.models.ai import AIPrompt, AIModelOutput
from rolling.app.services.ai.provider import AIProvider

class AIModelClient:
    """
    This class instantiates an AI model, prepares the request, and normalises the AI model's output.

    The main steps of sending a request for an AI analysis report request include:
    1. Build a provider request that notes the model name, the prompts, and the allowed tools.
    2. Generate the AI analysis report with the provider request.
    3. Normalise the provider response (following the prompt into a structured object

    Attributes
    ----------
        model_name (str): The name of the model to use as the AI service.
        provider (AIProvider): An instance of the AIProvider class used to communicate with the AI service.
    """
    def __init__(self, model_name: str, provider: AIProvider):
        """Initialises the AIModelClient class with the provided model name and AI service provider."""
        self.model_name = model_name
        self.provider = provider

    def generate_ai_analyis_report(self, # TODO rename to generate_ai_analysis_report_request
                        prompt_payload: AIPrompt
                        ) -> AIModelOutput:
        """
        Generate an AI analysis report.

        Args:
            prompt_payload (AIPrompt): An instance of the AIPrompt class containing the prompts

        Returns:
            AIModelOutput: An instance of the AIModelOutput class containing the report and the model name that generated it.
        """
        provider_request = self._build_provider_request(prompt_payload)
        provider_response = self.provider.generate(provider_request)
        return self._normalise_provider_response(provider_response)

    def _build_provider_request(self, prompt_payload: AIPrompt) -> dict:
        """
        Build a provider request for an AI analysis report.

        Args:
            prompt_payload (AIPrompt): An instance of the AIPrompt class containing the prompts.

        Returns:
            dict: A dictionary containing the prompts and operating parameters for the AI service.
                - "model_name": The name of the model to use as the AI service.
                - "system_prompt": The system prompt for the AI service.
                - "user_prompt": The user prompt for the AI service.
                - "tools": The allowed tools for the AI service.
        """
        return {"model_name": self.model_name,
                "system_prompt": prompt_payload.system_prompt,
                "user_prompt": prompt_payload.user_prompt,
                "tools": prompt_payload.tools}
    
    def _normalise_provider_response(self, provider_response: dict) -> AIModelOutput:
        """
        Normalises the provider response for an AI analysis report into a structured object.

        Args:
            provider_response (dict): A dictionary containing the provider response

        Returns:
            AIModelOutput: An instance of the AIModelOutput class containing the report and the model name
        """
        return AIModelOutput(model_name=self.model_name,
                             report_text=provider_response["report_text"],
                             summary_text=provider_response.get("summary_text"))
