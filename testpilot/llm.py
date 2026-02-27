"""LLM 客户端封装 - 支持多提供商"""
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from testpilot.config import LLMConfig, get_llm_config


# ============================================================
# 统一响应格式
# ============================================================

@dataclass
class ToolCall:
    """工具调用"""
    id: str
    name: str
    input: dict


@dataclass
class TokenUsage:
    """Token 使用统计"""
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class LLMResponse:
    """统一的 LLM 响应格式"""
    text: str | None = None
    tool_calls: list[ToolCall] | None = None
    stop_reason: str = "end_turn"
    raw_response: Any = None
    usage: TokenUsage | None = None

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


# ============================================================
# 提供商基类
# ============================================================

class LLMProvider(ABC):
    """LLM 提供商基类"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None

    @abstractmethod
    def _create_client(self) -> Any:
        """创建客户端"""
        pass

    @abstractmethod
    def call(
        self,
        messages: list[dict],
        tools: list[dict],
        system: str,
    ) -> LLMResponse:
        """调用 LLM"""
        pass

    def get_client(self) -> Any:
        """获取客户端单例"""
        if self._client is None:
            self._client = self._create_client()
        return self._client


# ============================================================
# Anthropic 提供商
# ============================================================

class AnthropicProvider(LLMProvider):
    """Anthropic Claude API"""

    def _create_client(self):
        import anthropic
        return anthropic.Anthropic(api_key=self.config.api_key)

    def call(
        self,
        messages: list[dict],
        tools: list[dict],
        system: str,
    ) -> LLMResponse:
        import anthropic

        client = self.get_client()
        max_retries = 2

        for attempt in range(max_retries):
            try:
                response = client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    system=system,
                    messages=messages,
                    tools=tools,
                )

                # 解析响应
                text_parts = []
                tool_calls = []

                for block in response.content:
                    if block.type == "text":
                        text_parts.append(block.text)
                    elif block.type == "tool_use":
                        tool_calls.append(ToolCall(
                            id=block.id,
                            name=block.name,
                            input=block.input,
                        ))

                # 提取 token 使用信息
                usage = None
                if hasattr(response, 'usage') and response.usage:
                    usage = TokenUsage(
                        input_tokens=response.usage.input_tokens,
                        output_tokens=response.usage.output_tokens,
                    )

                return LLMResponse(
                    text="\n".join(text_parts) if text_parts else None,
                    tool_calls=tool_calls if tool_calls else None,
                    stop_reason=response.stop_reason,
                    raw_response=response,
                    usage=usage,
                )

            except anthropic.APIConnectionError:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise

            except anthropic.RateLimitError:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                raise


# ============================================================
# OpenAI 提供商
# ============================================================

class OpenAIProvider(LLMProvider):
    """OpenAI API (官方和兼容)"""

    def _create_client(self):
        from openai import OpenAI
        if self.config.base_url:
            return OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
        return OpenAI(api_key=self.config.api_key)

    def _convert_tools_to_openai_format(self, tools: list[dict]) -> list[dict]:
        """将 Anthropic 格式的工具转换为 OpenAI 格式"""
        openai_tools = []
        for tool in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                }
            })
        return openai_tools

    def _convert_messages_to_openai_format(self, messages: list[dict], system: str) -> list[dict]:
        """将消息格式转换为 OpenAI 格式"""
        import json

        openai_messages = [{"role": "system", "content": system}]

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                if isinstance(content, str):
                    openai_messages.append({"role": "user", "content": content})
                elif isinstance(content, list):
                    # 处理 tool_result
                    for item in content:
                        if item.get("type") == "tool_result":
                            openai_messages.append({
                                "role": "tool",
                                "tool_call_id": item["tool_use_id"],
                                "content": item["content"],
                            })
                        else:
                            openai_messages.append({"role": "user", "content": str(item)})

            elif role == "assistant":
                if isinstance(content, str):
                    openai_messages.append({"role": "assistant", "content": content})
                elif isinstance(content, list):
                    # 处理包含 tool_use 的 assistant 消息
                    text_parts = []
                    tool_calls = []

                    for item in content:
                        if item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif item.get("type") == "tool_use":
                            tool_calls.append({
                                "id": item["id"],
                                "type": "function",
                                "function": {
                                    "name": item["name"],
                                    "arguments": json.dumps(item["input"]),
                                }
                            })

                    assistant_msg = {"role": "assistant"}
                    if text_parts:
                        assistant_msg["content"] = "\n".join(text_parts)
                    if tool_calls:
                        assistant_msg["tool_calls"] = tool_calls
                    openai_messages.append(assistant_msg)

        return openai_messages

    def call(
        self,
        messages: list[dict],
        tools: list[dict],
        system: str,
    ) -> LLMResponse:
        import json
        from openai import APIConnectionError, RateLimitError

        client = self.get_client()
        max_retries = 2

        openai_messages = self._convert_messages_to_openai_format(messages, system)
        openai_tools = self._convert_tools_to_openai_format(tools)

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    messages=openai_messages,
                    tools=openai_tools if openai_tools else None,
                )

                # 解析响应
                choice = response.choices[0]
                message = choice.message

                text = message.content
                tool_calls = None

                if message.tool_calls:
                    tool_calls = []
                    for tc in message.tool_calls:
                        tool_calls.append(ToolCall(
                            id=tc.id,
                            name=tc.function.name,
                            input=json.loads(tc.function.arguments),
                        ))

                # 提取 token 使用信息
                usage = None
                if hasattr(response, 'usage') and response.usage:
                    usage = TokenUsage(
                        input_tokens=response.usage.prompt_tokens,
                        output_tokens=response.usage.completion_tokens,
                    )

                return LLMResponse(
                    text=text,
                    tool_calls=tool_calls,
                    stop_reason=choice.finish_reason,
                    raw_response=response,
                    usage=usage,
                )

            except APIConnectionError:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise

            except RateLimitError:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                raise


# ============================================================
# 提供商工厂
# ============================================================

_provider_instance: LLMProvider | None = None


def get_provider(config: LLMConfig | None = None) -> LLMProvider:
    """获取 LLM 提供商实例"""
    global _provider_instance

    if config is None:
        config = get_llm_config()

    # 如果配置改变，重新创建
    if _provider_instance is not None and _provider_instance.config != config:
        _provider_instance = None

    if _provider_instance is None:
        if config.provider == "anthropic":
            _provider_instance = AnthropicProvider(config)
        elif config.provider in ("openai", "openai-compatible"):
            _provider_instance = OpenAIProvider(config)
        else:
            raise ValueError(f"未知提供商: {config.provider}")

    return _provider_instance


def reset_provider():
    """重置提供商实例 (用于切换配置)"""
    global _provider_instance
    _provider_instance = None


# ============================================================
# 便捷接口
# ============================================================

def llm_call(
    messages: list[dict],
    tools: list[dict],
    system: str,
    config: LLMConfig | None = None,
) -> LLMResponse:
    """
    调用 LLM (统一接口)

    Args:
        messages: 消息列表
        tools: 工具 schema 列表
        system: 系统提示词
        config: LLM 配置 (可选，默认使用全局配置)

    Returns:
        统一格式的响应
    """
    provider = get_provider(config)
    return provider.call(messages, tools, system)
