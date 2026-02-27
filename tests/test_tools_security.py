import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from testpilot.runtime_context import reset_project_root, set_project_root
from testpilot.tools.file_tools import list_dir, read_file, write_file
from testpilot.tools.search_tools import search_files


class ToolsSecurityTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmpdir.name) / "workspace"
        self.workspace.mkdir()
        (self.workspace / "src").mkdir()
        (self.workspace / "src" / "app.py").write_text("hello world\n", encoding="utf-8")

        self.token = set_project_root(str(self.workspace))

    def tearDown(self):
        reset_project_root(self.token)
        self.tmpdir.cleanup()

    def test_file_tools_reject_paths_outside_workspace(self):
        self.assertIn("outside workspace", read_file("../secret.txt"))
        self.assertIn("outside workspace", write_file("../escape.txt", "x"))
        self.assertIn("outside workspace", list_dir(".."))
        self.assertFalse((self.workspace.parent / "escape.txt").exists())

    def test_search_files_reject_paths_outside_workspace(self):
        result = search_files("hello", path="..")
        self.assertIn("outside workspace", result)

    @patch("testpilot.tools.search_tools.subprocess.run")
    def test_search_files_does_not_use_shell(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stdout="src/app.py:1: hello world\n", stderr="")

        result = search_files("hello", path=".")

        self.assertIn("Found in 1 files", result)
        self.assertTrue(mock_run.called)
        args, kwargs = mock_run.call_args
        self.assertIsInstance(args[0], list)
        self.assertNotIn("shell", kwargs)


if __name__ == "__main__":
    unittest.main()
