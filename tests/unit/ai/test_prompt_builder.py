import unittest

from rolling.app.models.ai import AIAnalysisReportInput
from rolling.app.services.ai.prompt_builder import AIReportPromptBuilder


class TestPromptBuilder(unittest.TestCase):
    prompt_builder = AIReportPromptBuilder()

    def build_prompt(self):
        ai_input = AIAnalysisReportInput(summary={"results": []},
                                         tables=[],
                                         report_text="report",
                                         summary_text="summary",
                                         metadata={"analysis_run_id": "run-1"})
        return self.prompt_builder.build_prompt(ai_input)

    def test_report_title_is_spelt_correctly(self):
        prompt = self.build_prompt()

        self.assertIn("Descriptive Analysis AI Report of Hormone Changes in Elite Cyclists", prompt.user_prompt)
        self.assertNotIn("Cyclsts", prompt.user_prompt)

    def test_prompt_asks_for_json_with_report_and_summary(self):
        prompt = self.build_prompt()

        self.assertIn('"report_text"', prompt.user_prompt)
        self.assertIn('"summary_text"', prompt.user_prompt)
