import unittest

from app.services.ai.validator import AIReportValidator
from app.models.ai import AIModelOutput


class TestAIValidator(unittest.TestCase):
    validator = AIReportValidator()

    empty_report_text_output = AIModelOutput(model_name="mock model",
                                             report_text="",
                                             summary_text="mock summary")
    whitespace_report_text_output = AIModelOutput(model_name="mock model",
                                                  report_text="  ",
                                                  summary_text="mock summary")
    whitespace_model_name_output = AIModelOutput(model_name="  ",
                                                 report_text="mock report",
                                                 summary_text="mock summary")
    empty_model_name_output = AIModelOutput(model_name="",
                                            report_text="mock report",
                                            summary_text="mock summary")
    null_summary_text_output = AIModelOutput(model_name="mock model",
                                             report_text="mock report",
                                             summary_text=None)
    def test_empty_report_text(self):
        with self.assertRaises(ValueError) as e:
            self.validator.validate_generated_report(self.empty_report_text_output)
        self.assertIn("non-empty report_text", str(e.exception))

    def test_whitespace_only_report_text(self):
        with self.assertRaises(ValueError) as e:
            self.validator.validate_generated_report(self.whitespace_report_text_output)
        self.assertIn("non-empty report_text", str(e.exception))

    def test_whitespace_only_model_name(self):
        with self.assertRaises(ValueError) as e:
            self.validator.validate_generated_report(self.whitespace_model_name_output)
        self.assertIn("include a model_name", str(e.exception))

    def test_empty_model_name(self):
        with self.assertRaises(ValueError) as e:
            self.validator.validate_generated_report(self.empty_model_name_output)
        self.assertIn("include a model_name", str(e.exception))

    def test_null_summary_text(self):
        self.assertEqual(self.validator.validate_generated_report(self.null_summary_text_output),
                         self.null_summary_text_output)
        