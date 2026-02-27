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

    @staticmethod
    def _build_config():
        return LLMConfig.custom("anthropic", "test-model", "test-key")

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
                    llm_config=self._build_config(),
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
                    llm_config=self._build_config(),
                )

        self.assertIn("[read_file]", buf.getvalue())

    @patch("testpilot.agent.MAX_TURNS", 2)
    @patch("testpilot.agent.load_skills", return_value="")
    @patch("testpilot.agent.get_tools_schema", return_value=[])
    @patch("testpilot.agent.execute_tool", return_value="ok")
    @patch("testpilot.agent.llm_call")
    def test_max_turns_cutoff(self, mock_llm, _mock_exec, _mock_schema, _mock_skills):
        mock_llm.return_value = LLMResponse(
            tool_calls=[ToolCall(id="tool-1", name="read_file", input={"path": "src/app.py"})],
            stop_reason="tool_use",
        )

        result = run_agent("test request", str(self.workspace), llm_config=self._build_config())

        self.assertEqual(result.output, "[Agent 达到最大轮次限制, 未完成任务]")
        self.assertEqual(result.stats.total_turns, 2)

    @patch("testpilot.agent.load_skills", return_value="")
    @patch("testpilot.agent.get_tools_schema", return_value=[])
    @patch("testpilot.agent.execute_tool", side_effect=["file-a", "file-b"])
    @patch("testpilot.agent.llm_call")
    def test_multiple_tool_calls_in_single_turn(self, mock_llm, mock_exec, _mock_schema, _mock_skills):
        mock_llm.side_effect = [
            LLMResponse(
                tool_calls=[
                    ToolCall(id="tool-1", name="read_file", input={"path": "a.py"}),
                    ToolCall(id="tool-2", name="read_file", input={"path": "b.py"}),
                ],
                stop_reason="tool_use",
            ),
            LLMResponse(text="done", stop_reason="end_turn"),
        ]

        result = run_agent("test request", str(self.workspace), llm_config=self._build_config())

        self.assertEqual(result.output, "done")
        self.assertEqual(mock_exec.call_count, 2)

    @patch("testpilot.agent.load_skills", return_value="")
    @patch("testpilot.agent.get_tools_schema", return_value=[])
    @patch("testpilot.agent.execute_tool", return_value="Error: RuntimeError: boom")
    @patch("testpilot.agent.llm_call")
    def test_tool_error_result_does_not_break_loop(self, mock_llm, _mock_exec, _mock_schema, _mock_skills):
        mock_llm.side_effect = [
            LLMResponse(
                tool_calls=[ToolCall(id="tool-1", name="run_command", input={"command": "pytest"})],
                stop_reason="tool_use",
            ),
            LLMResponse(text="final report", stop_reason="end_turn"),
        ]

        result = run_agent("test request", str(self.workspace), llm_config=self._build_config())

        self.assertEqual(result.output, "final report")
        self.assertEqual(mock_llm.call_count, 2)

    @patch("testpilot.agent.load_skills", return_value="")
    @patch("testpilot.agent.get_tools_schema", return_value=[])
    @patch("testpilot.agent.execute_tool")
    @patch("testpilot.agent.llm_call")
    def test_plain_text_response_ends_immediately(self, mock_llm, mock_exec, _mock_schema, _mock_skills):
        mock_llm.return_value = LLMResponse(text="all done", stop_reason="end_turn")

        result = run_agent("test request", str(self.workspace), llm_config=self._build_config())

        self.assertEqual(result.output, "all done")
        self.assertEqual(result.stats.total_turns, 1)
        mock_exec.assert_not_called()


if __name__ == "__main__":
    unittest.main()
