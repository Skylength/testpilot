"""ask_user 工具 - Agent 主动询问用户"""
import click
import threading
from contextvars import ContextVar
from typing import Callable

from .registry import register_tool

# ContextVar 区分 CLI / Web 模式
_ask_mode: ContextVar[str] = ContextVar("_ask_mode", default="cli")
# Web 模式下的回调: (questions, suggestion) -> answer
_ask_callback: ContextVar[Callable[[list[str], str], str] | None] = ContextVar(
    "_ask_callback", default=None,
)


def set_ask_web_mode(callback: Callable[[list[str], str], str]):
    """切换到 Web 模式并设置回调"""
    _ask_mode.set("web")
    _ask_callback.set(callback)


def set_ask_cli_mode():
    """切换到 CLI 模式（默认）"""
    _ask_mode.set("cli")
    _ask_callback.set(None)


def _handle_ask_user(questions: list[str], suggestion: str = "") -> str:
    """ask_user 工具的处理函数"""
    mode = _ask_mode.get()

    if mode == "web":
        cb = _ask_callback.get()
        if cb is None:
            return "[ask_user] Web 模式但未设置回调，跳过询问"
        return cb(questions, suggestion)

    # CLI 模式: 用 click.prompt 阻塞等待
    click.echo("\n" + "=" * 40)
    click.echo("Agent 需要你的输入:")
    click.echo("=" * 40)
    if suggestion:
        click.echo(f"(建议: {suggestion})")

    answers = []
    for i, q in enumerate(questions, 1):
        answer = click.prompt(f"  Q{i}: {q}")
        answers.append(answer)

    click.echo("=" * 40 + "\n")
    return "\n".join(f"Q{i}: {q}\nA{i}: {a}" for i, (q, a) in enumerate(zip(questions, answers), 1))


# 注册工具
register_tool(
    name="ask_user",
    description=(
        "向用户提问以澄清需求。当测试请求模糊、范围不明确、或需要用户决策时使用。"
        "一次最多问 3 个问题。仅在确实需要澄清时调用，明确的请求不要调用。"
    ),
    input_schema={
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "maxItems": 3,
                "description": "要问用户的问题列表 (1-3 个)",
            },
            "suggestion": {
                "type": "string",
                "description": "可选的建议或默认选项，帮助用户快速决策",
            },
        },
        "required": ["questions"],
    },
    handler=_handle_ask_user,
)
