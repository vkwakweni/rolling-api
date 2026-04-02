from typing import Any

from app.models.ai import AIReportInput, AIPrompt

class AIReportPromptBuilder:

    def __init__(self):
        ...

    def build_prompt(self,
                     ai_input: AIReportInput
                     ) -> AIPrompt:
        ...


