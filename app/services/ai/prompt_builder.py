from typing import Any
import json

from app.models.ai import AIAnalysisReportInput, AIPrompt

class AIReportPromptBuilder:
    SYSTEM_PROMPT = ("You are assisting with descriptive research reporting for a hormone "
                     "analysis of cyclists. Rewrite the provided traditional report into a "
                     "clearer, more cohesive narrative and provide a concise summary of the "
                     "descriptive results. If multiple result summaries and tables are provided, "
                     "integrate them into one coherent report for the same analysis run. "
                     "Stay grounded in the supplied data. Do not provide "
                     "diagnosis, treatment advice, or unsupported claims.")

    # TODO allow an analyst to submit their own prompts.

    def build_prompt(self,
                     ai_input: AIAnalysisReportInput
                     ) -> AIPrompt:
        summary_section = self._build_summary_section(ai_input)
        tables_section = self._build_tables_section(ai_input)

        user_prompt = ("Use the following structured descriptive analysis outputs and traditional report.\n\n"
                       f"{summary_section}\n"
                       f"{tables_section}\n"
                       f"Traditional report:\n{ai_input.report_text or ''}\n"
                       f"Traditional summary:\n{ai_input.summary_text or ''}\n"
                       f"Metadata:\n{json.dumps(ai_input.metadata, indent=2)}\n"
                       "Return valid JSON with exactly these keys:\n"
                       "{\n"
                       "\t\"report_text\": \"...\",\n"
                       "\t\"summary_text\": \"...\"\n"
                       "}\n"
                       "Do not include any text outside the JSON object.")
        
        return AIPrompt(system_prompt=self.SYSTEM_PROMPT,
                        user_prompt=user_prompt)

    # HELPERS
    def _build_summary_section(self, ai_input: AIAnalysisReportInput) -> str:
        summary_payload = ai_input.summary
        result_summaries = summary_payload.get("results", [])
        return ("Result summaries:\n"
                f"{json.dumps(result_summaries, indent=2)}")
    
    def _build_tables_section(self, ai_input: AIAnalysisReportInput) -> str:
        return ("Approved tables:\n"
                f"{json.dumps(ai_input.tables, indent=2)}")

