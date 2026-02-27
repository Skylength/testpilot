"""TestPilot 配置模块 - 支持多 LLM 提供商"""
import os
import json
from pathlib import Path
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Literal

# ============================================================
# LLM 配置
# ============================================================

# 支持的提供商类型
LLMProvider = Literal["anthropic", "openai", "openai-compatible"]

# 预设模型配置
PRESET_MODELS = {
    # Anthropic 官方
    "claude-sonnet": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5-20250929",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "claude-opus": {
        "provider": "anthropic",
        "model": "claude-opus-4-5-20250929",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "claude-haiku": {
        "provider": "anthropic",
        "model": "claude-haiku-3-5-20241022",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    # OpenAI 官方
    "gpt-4o": {
        "provider": "openai",
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
    },
    "gpt-4o-mini": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
    },
    "gpt-4-turbo": {
        "provider": "openai",
        "model": "gpt-4-turbo",
        "api_key_env": "OPENAI_API_KEY",
    },
    # DeepSeek
    "deepseek": {
        "provider": "openai-compatible",
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
    },
    "deepseek-reasoner": {
        "provider": "openai-compatible",
        "model": "deepseek-reasoner",
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
    },
    # ============================================================
    # LiteLLM 代理 (自定义)
    # ============================================================
    "litellm-opus": {
        "provider": "openai-compatible",
        "model": "us.anthropic.claude-opus-4-5-20251101-v1:0",
        "api_key_env": "TESTPILOT_API_KEY",
        "base_url": "https://litellm-us.leapwatt.ai/v1",
    },
}


@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: LLMProvider = "anthropic"
    model: str = "claude-sonnet-4-5-20250929"
    api_key: str = ""
    base_url: str | None = None  # 仅 openai-compatible 需要
    max_tokens: int = 4096

    @classmethod
    def from_preset(cls, preset_name: str) -> "LLMConfig":
        """从预设创建配置"""
        if preset_name not in PRESET_MODELS:
            raise ValueError(f"未知预设: {preset_name}，可用: {list(PRESET_MODELS.keys())}")

        preset = PRESET_MODELS[preset_name]

        # 仅从环境变量读取 API Key，避免明文硬编码
        api_key = os.environ.get(preset.get("api_key_env", ""), "")

        return cls(
            provider=preset["provider"],
            model=preset["model"],
            api_key=api_key,
            base_url=preset.get("base_url"),
        )

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """从环境变量创建配置"""
        provider = os.environ.get("TESTPILOT_PROVIDER", "anthropic")
        model = os.environ.get("TESTPILOT_MODEL", "claude-sonnet-4-5-20250929")
        base_url = os.environ.get("TESTPILOT_BASE_URL")
        max_tokens = int(os.environ.get("TESTPILOT_MAX_TOKENS", "4096"))

        # 根据提供商获取对应的 API Key
        if provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        elif provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY", "")
        else:
            # openai-compatible 优先用通用 key，否则用 OpenAI key
            api_key = os.environ.get("TESTPILOT_API_KEY") or os.environ.get("OPENAI_API_KEY", "")

        return cls(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            max_tokens=max_tokens,
        )

    @classmethod
    def custom(
        cls,
        provider: LLMProvider,
        model: str,
        api_key: str,
        base_url: str | None = None,
        max_tokens: int = 4096,
    ) -> "LLMConfig":
        """创建自定义配置"""
        return cls(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            max_tokens=max_tokens,
        )

    def validate(self):
        """验证配置"""
        if not self.api_key:
            if self.provider == "anthropic":
                raise ValueError("ANTHROPIC_API_KEY 未设置")
            elif self.provider == "openai":
                raise ValueError("OPENAI_API_KEY 未设置")
            else:
                raise ValueError("API Key 未设置 (TESTPILOT_API_KEY 或 OPENAI_API_KEY)")

        if self.provider == "openai-compatible" and not self.base_url:
            raise ValueError("openai-compatible 提供商需要设置 base_url")


# ============================================================
# 全局配置
# ============================================================

# Agent 配置
MAX_TURNS = int(os.environ.get("TESTPILOT_MAX_TURNS", "40"))
COMMAND_TIMEOUT = int(os.environ.get("TESTPILOT_COMMAND_TIMEOUT", "120"))

# 目录配置
TESTPILOT_DIR = ".testpilot"
FEATURES_DIR = ".testpilot/features"

# 结果截断限制
MAX_OUTPUT_CHARS = 50000

# 请求级 LLM 配置实例 (避免并发串扰)
_llm_config: ContextVar[LLMConfig | None] = ContextVar("testpilot_llm_config", default=None)


def get_llm_config() -> LLMConfig:
    """获取请求级 LLM 配置"""
    config = _llm_config.get()
    if config is None:
        return LLMConfig.from_env()
    return config


def set_llm_config(config: LLMConfig):
    """设置请求级 LLM 配置"""
    _llm_config.set(config)


def load_project_config(project_path: str) -> dict:
    """加载项目级配置 (如果存在)"""
    config_file = Path(project_path) / TESTPILOT_DIR / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def validate_config(config: LLMConfig | None = None):
    """验证必要配置是否存在"""
    (config or get_llm_config()).validate()
