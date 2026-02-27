"""Skill 加载器 - 发现并加载 SKILL.md 文件"""
import re
import shutil
from pathlib import Path

# 内置 Skills 目录
BUILTIN_SKILLS_DIR = Path(__file__).parent


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    解析 YAML frontmatter

    Returns:
        (元数据字典, 正文内容)
    """
    # 匹配 --- 之间的内容
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content

    frontmatter = match.group(1)
    body = match.group(2)

    # 简单解析 YAML (只解析需要的字段)
    metadata = {}

    # 解析 name
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if name_match:
        metadata["name"] = name_match.group(1).strip().strip('"\'')

    # 解析 description
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if desc_match:
        metadata["description"] = desc_match.group(1).strip().strip('"\'')

    # 解析 requires.bins
    bins_match = re.search(r"bins:\s*\[([^\]]+)\]", frontmatter)
    if bins_match:
        bins_str = bins_match.group(1)
        bins = [b.strip().strip('"\'') for b in bins_str.split(",")]
        metadata["requires_bins"] = bins

    return metadata, body


def _check_requirements(metadata: dict) -> tuple[bool, str]:
    """
    检查 Skill 的依赖要求

    Returns:
        (是否满足, 警告信息)
    """
    bins = metadata.get("requires_bins", [])
    missing = []
    for bin_name in bins:
        if not shutil.which(bin_name):
            missing.append(bin_name)

    if missing:
        return False, f"缺少依赖: {', '.join(missing)}"
    return True, ""


def load_skills(project_path: str, builtin_dir: Path | None = None) -> str:
    """
    加载所有适用的 Skills

    加载优先级:
    1. 项目级: <project>/.testpilot/skills/
    2. 内置: testpilot/skills/

    Args:
        project_path: 项目路径
        builtin_dir: 内置 Skills 目录 (默认使用模块目录)

    Returns:
        拼接后的 Skill 内容字符串
    """
    if builtin_dir is None:
        builtin_dir = BUILTIN_SKILLS_DIR

    skills: dict[str, str] = {}  # name -> content
    warnings: list[str] = []

    # 1. 加载内置 Skills
    for skill_dir in builtin_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8")
        metadata, body = _parse_frontmatter(content)
        name = metadata.get("name", skill_dir.name)

        # 检查依赖
        satisfied, warning = _check_requirements(metadata)
        if not satisfied:
            warnings.append(f"[{name}] {warning}")
            continue

        skills[name] = body

    # 2. 加载项目级 Skills (覆盖同名内置)
    project_skills_dir = Path(project_path) / ".testpilot" / "skills"
    if project_skills_dir.exists():
        for skill_dir in project_skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            content = skill_file.read_text(encoding="utf-8")
            metadata, body = _parse_frontmatter(content)
            name = metadata.get("name", skill_dir.name)

            satisfied, warning = _check_requirements(metadata)
            if not satisfied:
                warnings.append(f"[{name}] {warning}")
                continue

            skills[name] = body  # 覆盖同名

    # 打印警告
    for warning in warnings:
        print(f"⚠️  Skill 警告: {warning}")

    # 拼接所有 Skill 内容
    if not skills:
        return ""

    return "\n\n---\n\n".join(skills.values())
