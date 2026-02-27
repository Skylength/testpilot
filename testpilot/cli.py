"""TestPilot CLI 入口"""
import sys
from pathlib import Path
import click
from testpilot import __version__
from testpilot.config import (
    validate_config,
    LLMConfig,
    PRESET_MODELS,
    set_llm_config,
    get_llm_config,
)


def _list_presets():
    """列出所有预设模型"""
    lines = ["可用预设:"]
    for name, cfg in PRESET_MODELS.items():
        lines.append(f"  {name}: {cfg['provider']} / {cfg['model']}")
    return "\n".join(lines)


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(__version__, prog_name="TestPilot")
def cli(ctx):
    """TestPilot - 测试专精 AI Agent"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command("run")
@click.argument("request")
@click.option(
    "-p", "--project",
    default=".",
    help="项目路径，默认当前目录"
)
@click.option(
    "--preset",
    default=None,
    help=f"使用预设模型配置"
)
@click.option(
    "--provider",
    type=click.Choice(["anthropic", "openai", "openai-compatible"]),
    default=None,
    help="LLM 提供商"
)
@click.option(
    "-m", "--model",
    default=None,
    help="模型名称 (自定义)"
)
@click.option(
    "--base-url",
    default=None,
    help="API Base URL (用于 openai-compatible)"
)
@click.option(
    "--api-key",
    default=None,
    help="API Key (也可通过环境变量设置)"
)
@click.option(
    "--max-tokens",
    default=4096,
    type=int,
    help="最大输出 token 数"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="打印详细日志"
)
def run_cmd(
    request: str,
    project: str,
    preset: str | None,
    provider: str | None,
    model: str | None,
    base_url: str | None,
    api_key: str | None,
    max_tokens: int,
    verbose: bool,
):
    """
    运行测试任务

    REQUEST: 测试请求描述，例如 "帮我测试登录是否正常"

    \b
    示例:
        testpilot run "测试计算器" --preset litellm-opus
        testpilot run "测试登录" -p ./my-project --preset gpt-4o
    """
    from testpilot.agent import run_agent

    # 构建 LLM 配置
    llm_config = None
    try:
        if preset:
            llm_config = LLMConfig.from_preset(preset)
            if api_key:
                llm_config.api_key = api_key
            if max_tokens:
                llm_config.max_tokens = max_tokens
        elif provider or model or base_url:
            import os
            _provider = provider or "anthropic"
            _model = model or "claude-sonnet-4-5-20250929"
            _api_key = api_key or os.environ.get("TESTPILOT_API_KEY") or ""

            if _provider == "anthropic" and not _api_key:
                _api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            elif _provider == "openai" and not _api_key:
                _api_key = os.environ.get("OPENAI_API_KEY", "")

            llm_config = LLMConfig.custom(
                provider=_provider,
                model=_model,
                api_key=_api_key,
                base_url=base_url,
                max_tokens=max_tokens,
            )
        else:
            llm_config = LLMConfig.from_env()

        set_llm_config(llm_config)
        validate_config()

    except ValueError as e:
        click.echo(f"❌ 配置错误: {e}", err=True)
        sys.exit(1)

    # 转换为绝对路径
    project_path = Path(project).resolve()
    if not project_path.exists():
        click.echo(f"❌ 项目路径不存在: {project_path}", err=True)
        sys.exit(1)

    # 打印启动信息
    click.echo(f"🚀 TestPilot v{__version__}")
    click.echo(f"📁 项目: {project_path}")
    click.echo(f"📝 任务: {request}")
    click.echo(f"🤖 模型: {llm_config.provider} / {llm_config.model}")
    click.echo("─" * 40)

    # 运行 Agent
    try:
        from testpilot import tools  # noqa

        result = run_agent(request, str(project_path), verbose=verbose, llm_config=llm_config)

        # 输出报告
        click.echo("\n" + "═" * 40)
        click.echo(result.output)

        # 输出统计信息
        stats = result.stats
        click.echo("\n" + "─" * 40)
        click.echo("📊 执行统计")
        click.echo(f"   ⏱️  耗时: {stats.duration_formatted}")
        click.echo(f"   🔄 轮次: {stats.total_turns}")
        click.echo(f"   📥 输入 Token: {stats.input_tokens:,}")
        click.echo(f"   📤 输出 Token: {stats.output_tokens:,}")
        click.echo(f"   📦 总 Token: {stats.total_tokens:,}")

    except KeyboardInterrupt:
        click.echo("\n⚠️ 用户中断")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ 执行错误: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command("web")
@click.option(
    "--host",
    default="127.0.0.1",
    help="监听地址，默认 127.0.0.1"
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="监听端口，默认 8000"
)
def web_cmd(host: str, port: int):
    """
    启动 Web 界面

    \b
    示例:
        testpilot web
        testpilot web --host 0.0.0.0 --port 3000
    """
    try:
        from testpilot.web import run_server
    except ImportError:
        click.echo("❌ Web 依赖未安装，请运行: pip install testpilot[web]", err=True)
        sys.exit(1)

    click.echo(f"🚀 TestPilot Web v{__version__}")
    click.echo(f"🌐 启动服务: http://{host}:{port}")
    click.echo("─" * 40)

    try:
        run_server(host=host, port=port)
    except KeyboardInterrupt:
        click.echo("\n⚠️ 服务已停止")


@cli.command("presets")
def presets_cmd():
    """列出所有预设模型"""
    click.echo(_list_presets())


def main():
    """CLI 入口"""
    cli()


if __name__ == "__main__":
    main()
