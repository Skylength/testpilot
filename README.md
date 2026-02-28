# TestPilot

测试专精 AI Agent — 一句话驱动的自主测试工具。

TestPilot 接收一句自然语言描述，自动探索项目结构、阅读源码、生成并执行测试，最终输出一份有证据支撑的**可靠性报告**。

## 功能特性

- **自主测试流程** — Explore → Read → Generate + Execute → Report 四阶段自动完成
- **多 LLM 支持** — Anthropic Claude、OpenAI GPT、DeepSeek 及任意 OpenAI 兼容 API
- **CLI + Web 双模式** — 命令行直接运行，或启动 Web UI 在浏览器中操作
- **SSE 实时进度** — Web 端实时展示工具调用、执行结果等进度流
- **AskUser 交互** — Agent 遇到模糊需求时主动询问用户，缩小测试范围
- **Markdown 报告** — 结构化报告包含通过项、发现的问题、未覆盖风险

## 快速开始

### 安装

```bash
pip install -e ".[all]"
```

### 环境变量

根据使用的 LLM 提供商设置对应的 API Key：

```bash
# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# OpenAI 兼容 (DeepSeek / LiteLLM 等)
export TESTPILOT_API_KEY="your-key"
```

### CLI 用法

```bash
# 使用预设模型运行测试
testpilot run "测试登录功能" -p ./my-project --preset claude-sonnet

# 详细日志模式
testpilot run "测试计算器模块" -p ./calculator --preset gpt-4o -v

# 查看可用预设
testpilot presets
```

### Web 用法

```bash
testpilot web                          # 默认 127.0.0.1:9527
testpilot web --host 0.0.0.0 --port 3000  # 自定义地址
```

浏览器打开后，填写测试请求和项目路径，点击「开始测试」即可看到实时进度和最终报告。

## 可用预设

| 预设名 | 提供商 | 模型 |
|--------|--------|------|
| `claude-sonnet` | Anthropic | claude-sonnet-4-5 |
| `claude-opus` | Anthropic | claude-opus-4-5 |
| `claude-haiku` | Anthropic | claude-haiku-3-5 |
| `gpt-4o` | OpenAI | gpt-4o |
| `gpt-4o-mini` | OpenAI | gpt-4o-mini |
| `gpt-4-turbo` | OpenAI | gpt-4-turbo |
| `deepseek` | DeepSeek | deepseek-chat |
| `deepseek-reasoner` | DeepSeek | deepseek-reasoner |

也可通过 `--provider`、`--model`、`--base-url` 指定任意 OpenAI 兼容端点。

## 项目结构

```
testpilot/
├── agent.py              # Agent 主循环 (on_progress 回调)
├── cli.py                # CLI 入口 (click)
├── web.py                # Web 服务 (FastAPI, SSE 流式)
├── config.py             # 配置与预设模型
├── llm.py                # LLM 调用封装
├── runtime_context.py    # 运行时上下文管理
├── prompts/
│   ├── AGENTS.md         # Agent 系统 prompt (含 Phase 1.5 范围确认)
│   └── SOUL.md           # Agent 性格 prompt
├── skills/               # 可扩展技能模块
├── templates/
│   └── index.html        # Web 前端 (SSE + AskUser + Markdown 报告)
└── tools/
    ├── registry.py       # 工具注册表
    ├── file_tools.py     # list_dir, read_file, write_file
    ├── search_tools.py   # search_files
    ├── exec_tools.py     # run_command
    └── ask_tools.py      # ask_user (CLI/Web 双模式)
```

## 环境变量参考

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `ANTHROPIC_API_KEY` | Anthropic API Key | - |
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `TESTPILOT_API_KEY` | 通用 API Key (OpenAI 兼容) | - |
| `TESTPILOT_PROVIDER` | 默认提供商 | `anthropic` |
| `TESTPILOT_MODEL` | 默认模型 | `claude-sonnet-4-5-20250929` |
| `TESTPILOT_BASE_URL` | 默认 Base URL | - |
| `TESTPILOT_MAX_TURNS` | Agent 最大轮次 | `40` |
| `TESTPILOT_COMMAND_TIMEOUT` | 命令执行超时 (秒) | `120` |
| `TESTPILOT_MAX_TOKENS` | 最大输出 token | `4096` |

## License

MIT
