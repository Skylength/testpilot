"""搜索工具 - search_files"""
import os
import re
import subprocess
from pathlib import Path
from .registry import register_tool
from testpilot.runtime_context import get_project_root, resolve_path_in_project

# 支持搜索的文件扩展名
SEARCH_EXTENSIONS = {".py", ".java", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".rb", ".php", ".c", ".cpp", ".h"}


def search_files(pattern: str, path: str = ".", max_results: int = 20) -> str:
    """在项目中搜索包含指定关键词的文件和行"""
    try:
        search_path = resolve_path_in_project(path)
    except PermissionError:
        return f"Error: path is outside workspace: {path}"

    if not search_path.exists():
        return f"Error: directory not found: {path}"
    if not search_path.is_dir():
        return f"Error: not a directory: {path}"

    max_results = max(1, min(max_results, 100))
    results: list[str] = []

    # 优先使用 ripgrep（不经过 shell，避免注入）
    try:
        cmd = [
            "rg",
            "--line-number",
            "--no-heading",
            "--color",
            "never",
            "--no-messages",
        ]
        for ext in sorted(SEARCH_EXTENSIONS):
            cmd.extend(["-g", f"*{ext}"])
        cmd.extend(["--", pattern, str(search_path)])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode in (0, 1) and result.stdout.strip():
            results = result.stdout.strip().split("\n")[:max_results]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # rg 不可用，使用 Python fallback
        results = _python_search(search_path, pattern, max_results)

    if not results:
        # Python fallback
        results = _python_search(search_path, pattern, max_results)

    if not results:
        return f"No matches found for '{pattern}'"

    # 统计匹配的文件数
    files = set()
    for line in results:
        if ":" in line:
            files.add(line.split(":")[0])

    output = "\n".join(results)
    output += f"\n\nFound in {len(files)} files (showing first {len(results)} matches)"
    return output


def _python_search(search_path: Path, pattern: str, max_results: int) -> list[str]:
    """Python 实现的文件搜索"""
    results = []
    workspace = get_project_root()
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        # 如果正则无效，使用简单字符串匹配
        regex = None

    skip_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules"}

    for root, dirs, files in os.walk(search_path):
        # 跳过特定目录
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for filename in files:
            if len(results) >= max_results:
                break

            filepath = Path(root) / filename
            try:
                filepath.resolve().relative_to(workspace)
            except ValueError:
                continue

            if filepath.suffix not in SEARCH_EXTENSIONS:
                continue

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        if len(results) >= max_results:
                            break
                        if regex:
                            if regex.search(line):
                                results.append(f"{filepath}:{line_num}: {line.strip()[:100]}")
                        else:
                            if pattern.lower() in line.lower():
                                results.append(f"{filepath}:{line_num}: {line.strip()[:100]}")
            except (IOError, UnicodeDecodeError):
                continue

    return results


# 注册工具
register_tool(
    name="search_files",
    description="在项目中搜索包含指定关键词的文件和行",
    input_schema={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "搜索关键词或正则表达式"
            },
            "path": {
                "type": "string",
                "description": "搜索起始目录，默认当前目录",
                "default": "."
            },
            "max_results": {
                "type": "integer",
                "description": "最大结果数，默认20",
                "default": 20
            }
        },
        "required": ["pattern"]
    },
    handler=search_files
)
