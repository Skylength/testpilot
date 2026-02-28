"""TestPilot Web 界面"""
import asyncio
import json
import os
import threading
import uuid
from pathlib import Path
from queue import Queue, Empty

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from testpilot.config import (
    LLMConfig,
    PRESET_MODELS,
)
from testpilot.agent import run_agent

app = FastAPI(title="TestPilot", description="测试专精 AI Agent")

# 模板目录
TEMPLATES_DIR = Path(__file__).parent / "templates"

# AskUser 待处理问答: task_id -> { "event": threading.Event, "answer": str }
_pending_asks: dict[str, dict] = {}


class TestRequest(BaseModel):
    """测试请求"""
    request: str
    project_path: str = "."
    preset: str | None = None
    provider: str | None = None
    model: str | None = None
    base_url: str | None = None
    api_key: str | None = None


class AnswerRequest(BaseModel):
    """用户回答"""
    answer: str


class PresetInfo(BaseModel):
    """预设信息"""
    name: str
    provider: str
    model: str


def _build_llm_config(req: TestRequest) -> LLMConfig:
    """从请求构建 LLM 配置"""
    if req.preset:
        llm_config = LLMConfig.from_preset(req.preset)
        if req.api_key:
            llm_config.api_key = req.api_key
    elif req.provider or req.model or req.base_url:
        _provider = req.provider or "anthropic"
        _model = req.model or "claude-sonnet-4-5-20250929"
        _api_key = req.api_key or os.environ.get("TESTPILOT_API_KEY") or ""

        if _provider == "anthropic" and not _api_key:
            _api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        elif _provider == "openai" and not _api_key:
            _api_key = os.environ.get("OPENAI_API_KEY", "")

        llm_config = LLMConfig.custom(
            provider=_provider,
            model=_model,
            api_key=_api_key,
            base_url=req.base_url,
        )
    else:
        llm_config = LLMConfig.from_env()

    llm_config.validate()
    return llm_config


def _sse_event(event_type: str, data: dict | str) -> str:
    """格式化 SSE 事件"""
    payload = json.dumps(data, ensure_ascii=False) if isinstance(data, dict) else json.dumps({"content": data}, ensure_ascii=False)
    return f"event: {event_type}\ndata: {payload}\n\n"


# ============================================================
# API 端点
# ============================================================

@app.get("/api/presets")
async def list_presets() -> list[PresetInfo]:
    """获取所有预设模型"""
    return [
        PresetInfo(name=name, provider=cfg["provider"], model=cfg["model"])
        for name, cfg in PRESET_MODELS.items()
    ]


@app.post("/api/test")
async def run_test(req: TestRequest) -> dict:
    """运行测试（向后兼容，非流式）"""
    try:
        llm_config = _build_llm_config(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    project_path = Path(req.project_path).resolve()
    if not project_path.exists():
        raise HTTPException(status_code=400, detail=f"项目路径不存在: {project_path}")
    if not project_path.is_dir():
        raise HTTPException(status_code=400, detail=f"项目路径不是目录: {project_path}")

    from testpilot import tools  # noqa

    try:
        result = await asyncio.to_thread(
            run_agent,
            req.request,
            str(project_path),
            llm_config=llm_config,
        )
        return {
            "success": True,
            "output": result.output,
            "stats": {
                "duration": result.stats.duration_formatted,
                "total_turns": result.stats.total_turns,
                "input_tokens": result.stats.input_tokens,
                "output_tokens": result.stats.output_tokens,
                "total_tokens": result.stats.total_tokens,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/test/stream")
async def stream_test(req: TestRequest):
    """流式运行测试 (SSE)"""
    try:
        llm_config = _build_llm_config(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    project_path = Path(req.project_path).resolve()
    if not project_path.exists():
        raise HTTPException(status_code=400, detail=f"项目路径不存在: {project_path}")
    if not project_path.is_dir():
        raise HTTPException(status_code=400, detail=f"项目路径不是目录: {project_path}")

    from testpilot import tools  # noqa

    task_id = str(uuid.uuid4())[:8]
    progress_queue: Queue = Queue()

    def on_progress(event_type: str, content: str):
        progress_queue.put((event_type, content))

    def ask_user_web_handler(questions: list[str], suggestion: str) -> str:
        """Web 模式 ask_user 处理: 推事件到 queue, 阻塞等待回答"""
        question_id = str(uuid.uuid4())[:8]
        wait_event = threading.Event()
        _pending_asks[question_id] = {"event": wait_event, "answer": ""}

        # 推 ask_user 事件给前端
        progress_queue.put(("ask_user", json.dumps({
            "task_id": question_id,
            "questions": questions,
            "suggestion": suggestion,
        }, ensure_ascii=False)))

        # 阻塞等待用户回答 (最多 5 分钟)
        wait_event.wait(timeout=300)

        answer = _pending_asks.pop(question_id, {}).get("answer", "[超时未回答]")

        # 拼接 Q&A 返回给 Agent
        lines = []
        for i, q in enumerate(questions, 1):
            lines.append(f"Q{i}: {q}")
        lines.append(f"用户回答: {answer}")
        return "\n".join(lines)

    def agent_thread():
        """在子线程中运行 agent"""
        from testpilot.tools.ask_tools import set_ask_web_mode
        set_ask_web_mode(ask_user_web_handler)

        try:
            result = run_agent(
                req.request,
                str(project_path),
                llm_config=llm_config,
                on_progress=on_progress,
            )
            # 推送最终报告和统计
            progress_queue.put(("report", result.output))
            progress_queue.put(("stats", json.dumps({
                "duration": result.stats.duration_formatted,
                "total_turns": result.stats.total_turns,
                "input_tokens": result.stats.input_tokens,
                "output_tokens": result.stats.output_tokens,
                "total_tokens": result.stats.total_tokens,
            }, ensure_ascii=False)))
        except Exception as e:
            progress_queue.put(("error", {"message": str(e)}))
        finally:
            progress_queue.put(("done", ""))

    # 启动 agent 线程
    t = threading.Thread(target=agent_thread, daemon=True)
    t.start()

    async def event_generator():
        """SSE 事件生成器"""
        while True:
            try:
                event_type, content = await asyncio.to_thread(progress_queue.get, timeout=30)
            except Empty:
                # 超时发 ping 保活
                yield _sse_event("ping", "")
                continue

            if event_type == "done":
                yield _sse_event("done", "")
                break
            elif event_type == "ask_user":
                # ask_user 事件 content 已是 JSON 字符串
                yield f"event: ask_user\ndata: {content}\n\n"
            elif event_type in ("stats",):
                # stats content 已是 JSON 字符串
                yield f"event: {event_type}\ndata: {content}\n\n"
            else:
                yield _sse_event(event_type, content)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/test/{question_id}/answer")
async def submit_answer(question_id: str, req: AnswerRequest):
    """接收用户对 ask_user 的回答"""
    pending = _pending_asks.get(question_id)
    if not pending:
        raise HTTPException(status_code=404, detail="问题不存在或已超时")

    pending["answer"] = req.answer
    pending["event"].set()
    return {"ok": True}


# ============================================================
# 前端页面
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def index():
    """首页"""
    template_path = TEMPLATES_DIR / "index.html"
    return template_path.read_text(encoding="utf-8")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    return app


def run_server(host: str = "127.0.0.1", port: int = 9527):
    """启动 Web 服务器"""
    import uvicorn
    uvicorn.run(app, host=host, port=port)
