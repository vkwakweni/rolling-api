import unittest
from types import SimpleNamespace

from rolling.app.services.ai.provider import OllamaProvider

# Helper builders
def make_response_with_content(content: str):
    return SimpleNamespace(message=SimpleNamespace(content=content))


def make_invalid_json():
    return make_response_with_content(
        '{"report_text": "This is not valid JSON.", "summary_text": "This is not valid JSON."'
        )

def make_json_missing_report_text():
    return make_response_with_content('{"summary_text": "Mock summary."}')

def make_json_with_empty_content():
    return make_response_with_content("")

class TestProvider(unittest.TestCase):
    provider = OllamaProvider("mock_client")

    def test_empty_content_invalid(self):
        with self.assertRaises(expected_exception=ValueError) as e:
            self.provider._normalise_response(make_json_with_empty_content())
        self.assertIn("not contain message", str(e.exception).lower())

    def test_missing_report_text_invalid(self):
        with self.assertRaises(expected_exception=ValueError) as e:
            self.provider._normalise_response(make_json_missing_report_text())
        self.assertIn("not contain report_text", str(e.exception).lower())

    def test_invalid_json_invalid(self):
        with self.assertRaises(expected_exception=ValueError) as e:
            self.provider._normalise_response(make_invalid_json())
        self.assertIn("not valid json", str(e.exception).lower())