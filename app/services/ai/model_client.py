from typing import Any

from app.models.ai import AIPrompt

class AIModelClient:

    def __init__(self):
        ...

    def generate_report(self,
                        prompt_payload: AIPrompt
                        ) -> dict[str, Any]:
        ...
