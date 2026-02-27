import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from testpilot.runtime_context import reset_project_root, set_project_root
from testpilot.tools.search_tools import search_files


class SearchToolsTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmpdir.name) / "workspace"
        self.workspace.mkdir()
        (self.workspace / "src").mkdir()
        (self.workspace / "src" / "app.py").write_text(
            "hello world\nneedle (abc\n",
            encoding="utf-8",
        )
        self.token = set_project_root(str(self.workspace))

    def tearDown(self):
        reset_project_root(self.token)
        self.tmpdir.cleanup()

    @patch("testpilot.tools.search_tools.subprocess.run", side_effect=FileNotFoundError)
    def test_fallback_when_rg_missing(self, _mock_run):
        result = search_files("hello", path=".")

        self.assertIn("app.py", result)
        self.assertIn("Found in 1 files", result)

    @patch("testpilot.tools.search_tools.subprocess.run", side_effect=FileNotFoundError)
    def test_invalid_regex_pattern_uses_plain_text_match(self, _mock_run):
        result = search_files("(abc", path=".")

        self.assertIn("(abc", result)
        self.assertIn("Found in 1 files", result)

    @patch("testpilot.tools.search_tools.subprocess.run")
    def test_empty_result_returns_no_match_message(self, mock_run):
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="")

        result = search_files("not_exists_keyword_123", path=".")

        self.assertEqual(result, "No matches found for 'not_exists_keyword_123'")


if __name__ == "__main__":
    unittest.main()
