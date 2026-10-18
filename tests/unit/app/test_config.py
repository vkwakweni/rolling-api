import os
import unittest
from unittest import mock


class TestOllamaSettings(unittest.TestCase):
    def setUp(self):
        try:
            from rolling.app import config
        except ImportError:
            self.skipTest("the api extra is not installed")
        self.config = config

    def test_missing_api_key_gives_no_auth_header(self):
        env = {k: v for k, v in os.environ.items() if k != "OLLAMA_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(self.config.get_ollama_api_settings().headers, {})

    def test_api_key_gives_bearer_header(self):
        with mock.patch.dict(os.environ, {"OLLAMA_API_KEY": "abc"}):
            self.assertEqual(self.config.get_ollama_api_settings().headers, {"Authorization": "Bearer abc"})

    def test_ollama_provider_lookup_works(self):
        self.assertEqual(self.config.get_ai_api_settings("ollama").host, self.config.get_ollama_api_settings().host)
