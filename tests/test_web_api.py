import importlib.util
import os
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from testpilot.agent import AgentResult, AgentStats


FASTAPI_AVAILABLE = importlib.util.find_spec("fastapi") is not None

if FASTAPI_AVAILABLE:
    from fastapi.testclient import TestClient
    from testpilot.web import create_app


def _fake_agent_result(output: str) -> AgentResult:
    stats = AgentStats(total_turns=1, input_tokens=10, output_tokens=5)
    stats.finish()
    return AgentResult(output=output, stats=stats)


@unittest.skipUnless(FASTAPI_AVAILABLE, "fastapi not installed")
class WebApiTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmpdir.name) / "workspace"
        self.workspace.mkdir()
        self.app = create_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        self.client.close()
        self.tmpdir.cleanup()

    @patch("testpilot.web.run_agent")
    def test_concurrent_requests_isolation(self, mock_run_agent):
        project_a = self.workspace / "project-a"
        project_b = self.workspace / "project-b"
        project_a.mkdir()
        project_b.mkdir()

        def _side_effect(user_request: str, project_path: str, **_kwargs):
            time.sleep(0.05)
            return _fake_agent_result(f"{user_request}|{Path(project_path).name}")

        mock_run_agent.side_effect = _side_effect

        payload_a = {
            "request": "test-a",
            "project_path": str(project_a),
            "provider": "openai",
            "model": "gpt-4o-mini",
            "api_key": "k-a",
        }
        payload_b = {
            "request": "test-b",
            "project_path": str(project_b),
            "provider": "openai",
            "model": "gpt-4o-mini",
            "api_key": "k-b",
        }

        def _post(payload: dict):
            return self.client.post("/api/test", json=payload)

        with ThreadPoolExecutor(max_workers=2) as pool:
            fut_a = pool.submit(_post, payload_a)
            fut_b = pool.submit(_post, payload_b)
            resp_a = fut_a.result(timeout=5)
            resp_b = fut_b.result(timeout=5)

        self.assertEqual(resp_a.status_code, 200)
        self.assertEqual(resp_b.status_code, 200)
        self.assertEqual(resp_a.json()["output"], "test-a|project-a")
        self.assertEqual(resp_b.json()["output"], "test-b|project-b")
        self.assertEqual(mock_run_agent.call_count, 2)

    @patch("testpilot.web.run_agent")
    def test_invalid_config_returns_400(self, mock_run_agent):
        with patch.dict(os.environ, {}, clear=True):
            resp = self.client.post(
                "/api/test",
                json={
                    "request": "test",
                    "project_path": str(self.workspace),
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                },
            )

        self.assertEqual(resp.status_code, 400)
        self.assertIn("OPENAI_API_KEY 未设置", resp.json()["detail"])
        mock_run_agent.assert_not_called()

    @patch("testpilot.web.run_agent")
    def test_missing_project_path_returns_400(self, mock_run_agent):
        missing = self.workspace / "not-exists"

        resp = self.client.post(
            "/api/test",
            json={
                "request": "test",
                "project_path": str(missing),
                "provider": "openai",
                "model": "gpt-4o-mini",
                "api_key": "k",
            },
        )

        self.assertEqual(resp.status_code, 400)
        self.assertIn("项目路径不存在", resp.json()["detail"])
        mock_run_agent.assert_not_called()


if __name__ == "__main__":
    unittest.main()
