"""工具注册表 - 管理所有可用工具"""
from typing import Callable, Any
from testpilot.config import MAX_OUTPUT_CHARS

# 工具注册表
_TOOLS: dict[str, dict] = {}


def register_tool(
    name: str,
    description: str,
    input_schema: dict,
    handler: Callable[..., str]
) -> None:
    """
    注册一个工具

    Args:
        name: 工具名称
        description: 工具描述
        input_schema: JSON Schema 格式的输入参数定义
        handler: 实际执行函数
    """
    _TOOLS[name] = {
        "name": name,
        "description": description,
        "input_schema": input_schema,
        "handler": handler,
    }


def get_tools_schema() -> list[dict]:
    """
    获取所有工具的 schema (传给 Anthropic API)

    Returns:
        工具 schema 列表
    """
    return [
        {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": tool["input_schema"],
        }
        for tool in _TOOLS.values()
    ]


def execute_tool(name: str, params: dict) -> str:
    """
    执行指定工具

    Args:
        name: 工具名称
        params: 工具参数

    Returns:
        执行结果字符串
    """
    if name not in _TOOLS:
        return f"Error: unknown tool '{name}'"

    try:
        result = _TOOLS[name]["handler"](**params)

        # 截断过长输出
        if len(result) > MAX_OUTPUT_CHARS:
            result = result[:MAX_OUTPUT_CHARS] + "\n\n[truncated at 50000 chars]"

        return result
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"
