from typing import Any
import json

from app.models.ai import AIReportInput, AIPrompt

class AIReportPromptBuilder:
    SYSTEM_PROMPT = ("You are assisting with descriptive research reporting for a hormone "
                     "analysis of cyclists. Rewrite the provided traditional report into a "
                     "clearer, more cohesive narrative and provide a concise summary of the "
                     "descriptive results. Stay grounded in the supplied data. Do not provide "
                     "diagnosis, treatment advice, or unsupported claims.")

    # TODO allow an analyst to submit they're own prompts.

    def build_prompt(self,
                     ai_input: AIReportInput
                     ) -> AIPrompt:
        user_prompt = ("Use the following structured descriptive analysis outputs and traditional report.\n\n"
                       f"Summary:\n{json.dumps(ai_input.summary, indent=2)}\n"
                       f"Tables:\n{json.dumps(ai_input.tables, indent=2)}\n"
                       f"Traditional report:\n{ai_input.report_text or ''}\n"
                       f"Traditional summary:\n{ai_input.summary_text or ''}\n"
                       f"Metadata:\n{json.dumps(ai_input.metadata, indent=2)}\n"
                       "Return:\n"
                       "1. A rewritten report_text\n"
                       "2. A concise summary_text\n")
        return AIPrompt(system_prompt=self.SYSTEM_PROMPT,
                        user_prompt=user_prompt)


