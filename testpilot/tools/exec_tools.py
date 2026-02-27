"""执行工具 - run_command"""
import re
import shlex
import subprocess
from .registry import register_tool
from testpilot.config import COMMAND_TIMEOUT, MAX_OUTPUT_CHARS
from testpilot.runtime_context import get_project_root

# 允许的命令（首个可执行命令）
ALLOWED_COMMANDS = (
    "pytest",
    "python",
    "python3",
    "pip",
    "pip3",
    "git",
    "cat",
    "ls",
    "find",
    "cd",
    "echo",
    "pwd",
    "which",
    "env",
)

_ENV_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=.*$")


def _is_allowed_command(command: str) -> bool:
    """白名单检查：支持前置环境变量赋值。"""
    command_stripped = command.strip()
    if not command_stripped:
        return False

    try:
        tokens = shlex.split(command_stripped)
    except ValueError:
        return False

    if not tokens:
        return False

    idx = 0
    while idx < len(tokens) and _ENV_ASSIGNMENT_RE.match(tokens[idx]):
        idx += 1

    if idx >= len(tokens):
        return False

    return tokens[idx] in ALLOWED_COMMANDS


def run_command(command: str, timeout: int = COMMAND_TIMEOUT) -> str:
    """在项目目录下执行 shell 命令"""
    # 白名单检查
    if not _is_allowed_command(command):
        return (
            "Error: command not in allowed list. "
            "Allowed: pytest, python, python3, pip, pip3, git, cat, ls, find, "
            "cd, echo, pwd, which, env"
        )

    # 限制超时
    timeout = min(timeout, 300)
    project_root = get_project_root()

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(project_root),
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
