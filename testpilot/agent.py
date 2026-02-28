"""Agent 主循环 - TestPilot 核心"""
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
from testpilot.config import MAX_TURNS, LLMConfig
from testpilot.llm import llm_call, LLMResponse
from testpilot.tools import get_tools_schema, execute_tool
from testpilot.skills import load_skills
from testpilot.runtime_context import set_project_root, reset_project_root

# Prompt 文件目录
PROMPTS_DIR = Path(__file__).parent / "prompts"


@dataclass
class AgentStats:
    """Agent 执行统计"""
    total_turns: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: float = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def duration_formatted(self) -> str:
        """格式化的耗时"""
        seconds = self.duration_seconds
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"

    def add_usage(self, response: LLMResponse):
        """累加 token 使用"""
        if response.usage:
            self.input_tokens += response.usage.input_tokens
            self.output_tokens += response.usage.output_tokens

    def finish(self):
        """标记结束"""
        self.end_time = time.time()


@dataclass
class AgentResult:
    """Agent 执行结果"""
    output: str
    stats: AgentStats


def _load_prompt(filename: str) -> str:
    """加载 prompt 文件"""
    filepath = PROMPTS_DIR / filename
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return ""


def _summarize_input(tool_input: dict) -> str:
    """简要摘要工具输入参数"""
    if not tool_input:
        return ""
    # 取第一个参数值
    first_value = str(list(tool_input.values())[0])
    if len(first_value) > 60:
        first_value = first_value[:57] + "..."
    return first_value


def _tool_call_to_dict(tc) -> dict:
    """将 ToolCall 转换为字典"""
    return {
        "type": "tool_use",
        "id": tc.id,
        "name": tc.name,
        "input": tc.input,
    }


def run_agent(
    user_request: str,
    project_path: str,
    verbose: bool = False,
    llm_config: LLMConfig | None = None,
    on_progress: Callable[[str, str], None] | None = None,
) -> AgentResult:
    """
    运行 TestPilot Agent

    Args:
        user_request: 用户的测试请求
        project_path: 项目路径
        verbose: 是否打印详细日志
        llm_config: LLM 配置 (可选)
        on_progress: 进度回调 (event_type, content)，event_type 为 "tool_call"|"tool_result"|"text"

    Returns:
        AgentResult 包含输出和统计信息
    """
    stats = AgentStats()
    project_root_path = Path(project_path).resolve()
    if not project_root_path.exists():
        raise ValueError(f"项目路径不存在: {project_root_path}")
    if not project_root_path.is_dir():
        raise ValueError(f"项目路径不是目录: {project_root_path}")

    project_root = str(project_root_path)
    context_token = set_project_root(project_root)

    try:
        # 1. 组装 system prompt
        agents_md = _load_prompt("AGENTS.md")
        soul_md = _load_prompt("SOUL.md")
        skills = load_skills(project_root, PROMPTS_DIR.parent / "skills")

        system_prompt = agents_md
        if soul_md:
            system_prompt += "\n\n" + soul_md
        if skills:
            system_prompt += "\n\n---\n\n# 技能 (Skills)\n\n" + skills

        # 2. 构造初始 messages
        messages = [
            {
                "role": "user",
                "content": f"项目路径: {project_root}\n请测试: {user_request}"
            }
        ]

        # 3. 获取工具 schema
        tools = get_tools_schema()

        # 4. 主循环
        turn = 0
        final_output = ""

        while turn < MAX_TURNS:
            turn += 1
            stats.total_turns = turn

            if verbose:
                print(f"\n[Turn {turn}]")

            # 调用 LLM
            response: LLMResponse = llm_call(messages, tools, system_prompt, llm_config)

            # 累加 token 使用
            stats.add_usage(response)

            # 构造 assistant 消息内容
            assistant_content = []
            if response.text:
                assistant_content.append({"type": "text", "text": response.text})
            if response.tool_calls:
                for tc in response.tool_calls:
                    assistant_content.append(_tool_call_to_dict(tc))

            messages.append({"role": "assistant", "content": assistant_content})

            # 检查是否有 tool_use
            if not response.has_tool_calls:
                # 纯文本响应 → Agent 认为任务完成
                final_output = response.text or ""
                if on_progress and response.text:
                    on_progress("text", response.text[:200])
                break

            # 执行所有 tool calls, 收集结果
            tool_results = []
            for tc in response.tool_calls:
                # 打印进度
                if verbose:
                    print(f"  [{tc.name}] {_summarize_input(tc.input)}")
                if on_progress:
                    on_progress("tool_call", f"[{tc.name}] {_summarize_input(tc.input)}")

                result = execute_tool(tc.name, tc.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": result,
                })

                if verbose:
                    print(f"    → {result[:200]}..." if len(result) > 200 else f"    → {result}")
                if on_progress:
                    on_progress("tool_result", result[:200])

            messages.append({"role": "user", "content": tool_results})

        if not final_output:
            final_output = "[Agent 达到最大轮次限制, 未完成任务]"

        stats.finish()
        return AgentResult(output=final_output, stats=stats)

    finally:
        reset_project_root(context_token)
