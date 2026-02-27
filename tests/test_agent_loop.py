import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from testpilot.agent import run_agent
from testpilot.config import LLMConfig
from testpilot.llm import LLMResponse, ToolCall


class AgentLoopTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmpdir.name) / "workspace"
        self.workspace.mkdir()

    def tearDown(self):
        self.tmpdir.cleanup()

    @staticmethod
    def _build_responses():
        return [
            LLMResponse(
                tool_calls=[ToolCall(id="tool-1", name="read_file", input={"path": "src/app.py"})],
                stop_reason="tool_use",
            ),
            LLMResponse(
                text="done",
                stop_reason="end_turn",
            ),
        ]

    @patch("testpilot.agent.load_skills", return_value="")
    @patch("testpilot.agent.get_tools_schema", return_value=[])
    @patch("testpilot.agent.execute_tool", return_value="ok")
    def test_non_verbose_mode_hides_tool_logs(self, _mock_exec, _mock_schema, _mock_skills):
        responses = self._build_responses()

        with patch("testpilot.agent.llm_call", side_effect=responses):
            buf = io.StringIO()
            with redirect_stdout(buf):
                result = run_agent(
                    "test request",
                    str(self.workspace),
                    verbose=False,
                    llm_config=LLMConfig.custom("anthropic", "test-model", "test-key"),
                )

        self.assertEqual(result.output, "done")
        self.assertNotIn("[read_file]", buf.getvalue())

    @patch("testpilot.agent.load_skills", return_value="")
    @patch("testpilot.agent.get_tools_schema", return_value=[])
    @patch("testpilot.agent.execute_tool", return_value="ok")
    def test_verbose_mode_prints_tool_logs(self, _mock_exec, _mock_schema, _mock_skills):
        responses = self._build_responses()

        with patch("testpilot.agent.llm_call", side_effect=responses):
            buf = io.StringIO()
            with redirect_stdout(buf):
                run_agent(
                    "test request",
                    str(self.workspace),
                    verbose=True,
                    llm_config=LLMConfig.custom("anthropic", "test-model", "test-key"),
                )

        self.assertIn("[read_file]", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
