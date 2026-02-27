"""运行时上下文 - 按请求隔离项目根目录。"""
from contextvars import ContextVar, Token
from pathlib import Path


_project_root: ContextVar[Path | None] = ContextVar("testpilot_project_root", default=None)


def set_project_root(project_path: str) -> Token:
    """设置当前请求的项目根目录。"""
    return _project_root.set(Path(project_path).resolve())


def reset_project_root(token: Token) -> None:
    """恢复项目根目录上下文。"""
    _project_root.reset(token)


def get_project_root() -> Path:
    """获取当前请求项目根目录，未设置时回退到当前工作目录。"""
    root = _project_root.get()
    if root is None:
        return Path.cwd().resolve()
    return root


def resolve_path_in_project(path: str) -> Path:
    """将输入路径解析为绝对路径，并限制在项目根目录内。"""
    root = get_project_root()
    target = Path(path)
    if not target.is_absolute():
        target = root / target

    resolved = target.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise PermissionError(f"path is outside workspace: {path}") from exc

    return resolved
