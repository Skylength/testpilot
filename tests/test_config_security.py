import os
import unittest
from unittest.mock import patch

from testpilot.config import LLMConfig


class ConfigSecurityTests(unittest.TestCase):
    def test_litellm_preset_reads_api_key_from_env(self):
        with patch.dict(os.environ, {"TESTPILOT_API_KEY": "env-key"}, clear=True):
            config = LLMConfig.from_preset("litellm-opus")
        self.assertEqual(config.api_key, "env-key")

    def test_litellm_preset_has_no_default_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            config = LLMConfig.from_preset("litellm-opus")
        self.assertEqual(config.api_key, "")


if __name__ == "__main__":
    unittest.main()
