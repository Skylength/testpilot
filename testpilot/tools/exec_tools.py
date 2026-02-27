"""执行工具 - run_command"""
import subprocess
from .registry import register_tool
from testpilot.config import COMMAND_TIMEOUT, MAX_OUTPUT_CHARS

# 禁止的危险命令前缀
BLOCKED_COMMANDS = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "dd if=",
    "> /dev/",
    ":(){ :|:& };:",  # fork bomb
]


def run_command(command: str, timeout: int = COMMAND_TIMEOUT) -> str:
    """在项目目录下执行 shell 命令"""
    # 安全检查
    for blocked in BLOCKED_COMMANDS:
        if blocked in command:
            return "Error: command blocked for safety"

    # 限制超时
    timeout = min(timeout, 300)

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = f"Exit code: {result.returncode}\n\n"
        output += f"--- stdout ---\n{result.stdout}\n\n"
        output += f"--- stderr ---\n{result.stderr}"

        # 截断过长输出
        if len(output) > MAX_OUTPUT_CHARS:
            output = output[:MAX_OUTPUT_CHARS] + "\n\n[truncated]"

        return output
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


# 注册工具
register_tool(
    name="run_command",
    description="在项目目录下执行 shell 命令",
    input_schema={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "要执行的命令"
            },
            "timeout": {
                "type": "integer",
                "description": "超时秒数，默认120，上限300",
                "default": 120
            }
        },
        "required": ["command"]
    },
    handler=run_command
)
