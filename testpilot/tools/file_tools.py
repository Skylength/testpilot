"""文件操作工具 - list_dir, read_file, write_file"""
from pathlib import Path
from .registry import register_tool
from testpilot.config import MAX_OUTPUT_CHARS
from testpilot.runtime_context import get_project_root, resolve_path_in_project

# 要跳过的目录
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".testpilot"}


def _is_within_workspace(path: Path, workspace: Path) -> bool:
    """检查路径（resolve 后）是否在工作区内。"""
    try:
        path.resolve().relative_to(workspace)
        return True
    except (ValueError, OSError):
        return False


def list_dir(path: str, max_depth: int = 1) -> str:
    """列出目录下的文件和子目录"""
    try:
        dir_path = resolve_path_in_project(path)
    except PermissionError:
        return f"Error: path is outside workspace: {path}"

    if not dir_path.exists():
        return f"Error: directory not found: {path}"
    if not dir_path.is_dir():
        return f"Error: not a directory: {path}"

    max_depth = min(max_depth, 3)  # 最大深度限制
    lines = []
    file_count = 0
    max_files = 500
    workspace = get_project_root()

    def _walk(dir_path: Path, depth: int, prefix: str = ""):
        nonlocal file_count
        if depth > max_depth or file_count >= max_files:
            return

        try:
            items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            lines.append(f"{prefix}[permission denied]")
            return

        for item in items:
            if file_count >= max_files:
                break
            if item.name in SKIP_DIRS:
                continue
            if not _is_within_workspace(item, workspace):
                continue

            file_count += 1
            if item.is_dir():
                lines.append(f"{prefix}{item.name}/")
                _walk(item, depth + 1, prefix + "  ")
            else:
                lines.append(f"{prefix}{item.name}")

    _walk(dir_path, 1)

    if file_count >= max_files:
        lines.append(f"\n[truncated at {max_files} items]")

    return "\n".join(lines) if lines else "(empty directory)"


def read_file(path: str) -> str:
    """读取文件内容"""
    try:
        file_path = resolve_path_in_project(path)
    except PermissionError:
        return f"Error: path is outside workspace: {path}"

    if not file_path.exists():
        return f"Error: file not found: {path}"
    if not file_path.is_file():
        return f"Error: not a file: {path}"

    # 检查是否为二进制文件
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return "Error: binary file, cannot read"
    except IOError as e:
        return f"Error: cannot read file: {e}"

    # 读取文本内容
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if len(content) > MAX_OUTPUT_CHARS:
            content = content[:MAX_OUTPUT_CHARS] + f"\n\n[truncated at {MAX_OUTPUT_CHARS} chars]"

        return content
    except IOError as e:
        return f"Error: cannot read file: {e}"


def write_file(path: str, content: str) -> str:
    """写入文件内容，自动创建父目录"""
    try:
        file_path = resolve_path_in_project(path)
    except PermissionError:
        return f"Error: path is outside workspace: {path}"

    workspace = get_project_root()
    rel_parts = file_path.relative_to(workspace).parts
    if ".git" in rel_parts:
        return "Error: cannot write to .git directory"

    try:
        # 创建父目录
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入内容
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"OK: written {len(content.encode('utf-8'))} bytes to {file_path.relative_to(workspace)}"
    except IOError as e:
        return f"Error: cannot write file: {e}"


# 注册工具
register_tool(
    name="list_dir",
    description="列出目录下的文件和子目录",
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "目录路径"
            },
            "max_depth": {
                "type": "integer",
                "description": "递归深度，默认1，最大3",
                "default": 1
            }
        },
        "required": ["path"]
    },
    handler=list_dir
)

register_tool(
    name="read_file",
    description="读取文件内容",
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "文件路径"
            }
        },
        "required": ["path"]
    },
    handler=read_file
)

register_tool(
    name="write_file",
    description="写入文件内容，自动创建父目录",
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "文件路径"
            },
            "content": {
                "type": "string",
                "description": "文件内容"
            }
        },
        "required": ["path", "content"]
    },
    handler=write_file
)
