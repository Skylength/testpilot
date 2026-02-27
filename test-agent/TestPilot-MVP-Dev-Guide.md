# TestPilot MVP 开发文档

> 面向开发者的实现指南。按此文档可从零构建出可运行的最小版本。

---

## 一、MVP 边界

### 做什么

```
输入: testpilot "帮我测试登录是否正常" -p ./my-project
输出: 终端打印测试报告

中间产物:
  .testpilot/features/login.md   ← 功能文档 (持久化)
  tests/test_login.py            ← 测试代码 (持久化)
```

### 不做什么

- 不做 Web UI
- 不做 Docker 沙箱
- 不做多模型切换
- 不做 CI/CD 集成
- 不做跨会话记忆 (Feature Doc 已经够用)

### 技术选型

```
语言:     Python 3.10+
LLM:      Anthropic Claude API (tool use)
模型:     claude-sonnet-4-5-20250929 (性价比)
依赖:     anthropic (SDK), click (CLI)
仅此两个依赖, 不引入框架
```

---

## 二、文件结构与模块职责

```
testpilot/
├── cli.py                 # 命令行入口
├── agent.py               # Agent 主循环
├── llm.py                 # LLM 客户端封装
├── tools/
│   ├── __init__.py        # 导出 registry
│   ├── registry.py        # 工具注册表
│   ├── file_tools.py      # list_dir / read_file / write_file
│   ├── search_tools.py    # search_files
│   └── exec_tools.py      # run_command
├── skills/
│   ├── loader.py          # Skill 加载器
│   └── testing-python/
│       └── SKILL.md       # Python 测试技能
├── prompts/
│   ├── AGENTS.md          # Agent 行为规范
│   └── SOUL.md            # 角色定义
└── config.py              # 配置项
```

### 模块依赖关系 (单向向下)

```
cli.py
  └─→ agent.py
        ├─→ llm.py
        ├─→ tools/registry.py
        │     └─→ tools/file_tools.py
        │     └─→ tools/search_tools.py
        │     └─→ tools/exec_tools.py
        └─→ skills/loader.py
```

---

## 三、各模块详细设计

### 3.1 config.py — 配置

```
职责: 集中管理所有配置项

配置项:
  ANTHROPIC_API_KEY    环境变量读取, 无默认值, 缺失则报错退出
  MODEL                默认 "claude-sonnet-4-5-20250929"
  MAX_TURNS            默认 40 (单次 Agent 最大循环轮次)
  MAX_TOKENS           默认 4096 (单次 LLM 响应最大 token)
  COMMAND_TIMEOUT      默认 120 (run_command 超时秒数)
  TESTPILOT_DIR        默认 ".testpilot" (项目内的工作目录名)
  FEATURES_DIR         默认 ".testpilot/features"

加载顺序:
  1. 环境变量
  2. 项目目录下 .testpilot/config.json (如果存在)
  3. 代码内默认值
```

### 3.2 tools/registry.py — 工具注册表

```
职责: 注册/发现/执行工具

核心数据结构:
  _TOOLS: dict[str, ToolDef]

  ToolDef = {
      "name": str,
      "description": str,
      "input_schema": dict,       # JSON Schema
      "handler": Callable,        # 实际执行函数
  }

对外接口:
  register_tool(name, description, input_schema, handler) → None
    注册一个工具, name 重复则覆盖

  get_tools_schema() → list[dict]
    返回所有工具的 schema (传给 Anthropic API 的 tools 参数)
    格式: [{"name": "...", "description": "...", "input_schema": {...}}, ...]

  execute_tool(name, params) → str
    执行工具, 返回结果字符串
    工具不存在 → 返回 "Error: unknown tool '...'"
    工具执行异常 → 捕获异常, 返回 "Error: ..." (不让 Agent 循环崩溃)
    结果超过 50000 字符 → 截断 + 提示 "[truncated]"
```

### 3.3 tools/file_tools.py — 文件工具

**list_dir**

```
名称:        list_dir
描述:        列出目录下的文件和子目录
输入 schema:
  path: string (required) — 目录路径
  max_depth: integer (optional, default=1) — 递归深度, 最大3
输出:        目录树的文本表示

实现逻辑:
  1. os.walk 遍历, 受 max_depth 限制
  2. 跳过隐藏目录 (.git, .venv, __pycache__) 和 node_modules
  3. 每行格式: "  " * depth + name + "/" (如果是目录)
  4. 文件数量上限 500, 超过则截断 + 提示

示例输出:
  src/
    auth/
      router.py
      service.py
    models/
      user.py
  tests/
    conftest.py
  pyproject.toml
  README.md
```

**read_file**

```
名称:        read_file
描述:        读取文件内容
输入 schema:
  path: string (required) — 文件路径
输出:        文件内容文本

实现逻辑:
  1. 检查文件是否存在, 不存在返回 "Error: file not found: ..."
  2. 检查是否为二进制文件 (简单判断: 读前 1024 字节有 \x00)
     是 → 返回 "Error: binary file, cannot read"
  3. 读取全文, utf-8 编码, errors='ignore'
  4. 内容超过 50000 字符 → 截断 + 提示 "[truncated at 50000 chars]"
```

**write_file**

```
名称:        write_file
描述:        写入文件内容, 自动创建父目录
输入 schema:
  path: string (required) — 文件路径
  content: string (required) — 文件内容
输出:        "OK: written N bytes to <path>"

实现逻辑:
  1. os.makedirs(parent, exist_ok=True)
  2. 写入内容, utf-8 编码
  3. 返回确认信息

安全限制:
  path 不得包含 ".." (防止路径穿越)
  不得写入 .git/ 目录下
```

### 3.4 tools/search_tools.py — 搜索工具

**search_files**

```
名称:        search_files
描述:        在项目中搜索包含指定关键词的文件和行
输入 schema:
  pattern: string (required) — 搜索关键词或正则
  path: string (optional, default=".") — 搜索起始目录
  max_results: integer (optional, default=20) — 最大结果数
输出:        匹配结果的文本表示

实现逻辑:
  优先尝试调用系统 grep:
    grep -rn --include="*.py" --include="*.java" --include="*.js"
         --include="*.ts" --include="*.go"
         -l <pattern> <path>
  grep 不可用时 fallback 到 Python 实现:
    遍历文件, 逐行匹配

输出格式:
  src/auth/service.py:45: def login(username, password):
  src/auth/router.py:12: @router.post("/login")
  src/models/user.py:8: class User(Base):

  Found in 3 files (showing first 20 matches)
```

### 3.5 tools/exec_tools.py — 执行工具

**run_command**

```
名称:        run_command
描述:        在项目目录下执行 shell 命令
输入 schema:
  command: string (required) — 要执行的命令
  timeout: integer (optional, default=120) — 超时秒数, 上限 300
输出:        命令输出文本

实现逻辑:
  1. subprocess.run(
       command, shell=True, capture_output=True, text=True,
       timeout=timeout, cwd=project_path
     )
  2. 拼接输出:
     "Exit code: {returncode}\n\n--- stdout ---\n{stdout}\n\n--- stderr ---\n{stderr}"
  3. stdout + stderr 总长超过 50000 字符 → 截断

安全限制 (MVP 阶段最小限制):
  禁止的命令前缀: ["rm -rf /", "mkfs", "dd if=", "> /dev/"]
  这些直接返回 "Error: command blocked for safety"
```

### 3.6 llm.py — LLM 客户端

```
职责: 封装 Anthropic API 调用, 对 agent.py 暴露一个简单接口

对外接口:
  llm_call(
      messages: list[dict],
      tools: list[dict],
      system: str,
      model: str = MODEL,
      max_tokens: int = MAX_TOKENS,
  ) → Response

  Response 的结构 (直接使用 anthropic SDK 的返回对象):
    response.content: list[ContentBlock]
      ContentBlock 有两种:
        TextBlock:    { type: "text", text: "..." }
        ToolUseBlock: { type: "tool_use", id: "...", name: "...", input: {...} }
    response.stop_reason: "end_turn" | "tool_use"

实现逻辑:
  1. 创建 anthropic.Anthropic(api_key=API_KEY)  — 模块级单例
  2. 调用 client.messages.create(...)
  3. 处理常见错误:
     - APIConnectionError → 重试 1 次, 再失败则抛出
     - RateLimitError → sleep 5s 后重试 1 次
     - 其他异常 → 直接抛出
```

### 3.7 skills/loader.py — Skill 加载器

```
职责: 发现并加载 SKILL.md 文件, 拼接成 prompt 片段

对外接口:
  load_skills(project_path: str, builtin_dir: str) → str
    返回拼接后的 Skill 内容字符串

加载逻辑:
  1. 扫描内置 Skill 目录: testpilot/skills/*/SKILL.md
  2. 扫描项目级 Skill: <project_path>/.testpilot/skills/*/SKILL.md
  3. 项目级同名 Skill 覆盖内置
  4. 每个 SKILL.md:
     - 读取全文
     - 解析 YAML frontmatter (--- 之间的部分)
     - 检查 requires.bins (用 shutil.which 检查命令是否存在)
     - 不满足 requires 的 Skill 跳过并打印警告
  5. 拼接所有满足条件的 Skill 内容, 用 "\n\n---\n\n" 分隔
  6. 返回拼接结果

YAML frontmatter 解析:
  只需要简单解析, 不引入 PyYAML 依赖
  用正则提取 --- 之间的内容
  只解析 name, description, requires.bins 三个字段
  其余字段忽略
```

### 3.8 agent.py — Agent 主循环

```
职责: TestPilot 的核心, 驱动整个测试流程

对外接口:
  run_agent(user_request: str, project_path: str) → str
    返回最终的文本输出 (测试报告)

内部流程:

  def run_agent(user_request, project_path):

      # 1. 组装 system prompt
      agents_md = read("prompts/AGENTS.md")
      soul_md = read("prompts/SOUL.md")
      skills = load_skills(project_path, builtin_dir)
      system_prompt = agents_md + "\n\n" + soul_md + "\n\n" + skills

      # 2. 构造初始 messages
      messages = [
          {
              "role": "user",
              "content": f"项目路径: {project_path}\n请测试: {user_request}"
          }
      ]

      # 3. 获取工具 schema
      tools = get_tools_schema()

      # 4. 主循环
      turn = 0
      final_output = ""

      while turn < MAX_TURNS:
          turn += 1

          # 调用 LLM
          response = llm_call(messages, tools, system_prompt)

          # 处理响应
          assistant_content = response.content
          messages.append({"role": "assistant", "content": assistant_content})

          # 检查是否有 tool_use
          tool_calls = [b for b in assistant_content if b.type == "tool_use"]

          if not tool_calls:
              # 纯文本响应 → Agent 认为任务完成
              final_output = "".join(
                  b.text for b in assistant_content if b.type == "text"
              )
              break

          # 执行所有 tool calls, 收集结果
          tool_results = []
          for tc in tool_calls:
              # 打印进度
              print(f"  [{tc.name}] {_summarize(tc.input)}")

              result = execute_tool(tc.name, tc.input)
              tool_results.append({
                  "type": "tool_result",
                  "tool_use_id": tc.id,
                  "content": result,
              })

          messages.append({"role": "user", "content": tool_results})

      if not final_output:
          final_output = "[Agent 达到最大轮次限制, 未完成任务]"

      return final_output

进度打印:
  每次 tool_call 时打印一行, 让用户知道 Agent 在做什么
  格式: "  [tool_name] 简要参数摘要"
  例: "  [list_dir] ."
      "  [search_files] login"
      "  [run_command] pytest tests/test_login.py -v"

_summarize(tool_input) 逻辑:
  取 input 的第一个参数值, 截断到 60 字符
```

### 3.9 cli.py — 命令行入口

```
职责: 解析命令行参数, 调用 agent.run_agent()

命令格式:
  testpilot <request> [-p <project_path>] [-m <model>] [-v]

参数:
  request         必填, 用户的测试请求 (字符串)
  -p, --project   可选, 项目路径, 默认 "." (当前目录)
  -m, --model     可选, 模型名, 默认 claude-sonnet-4-5-20250929
  -v, --verbose   可选, 打印完整的 LLM 交互日志

执行流程:
  1. 解析参数
  2. 检查 ANTHROPIC_API_KEY 是否设置
  3. 将 project_path 转为绝对路径
  4. 注册所有工具 (import tools 模块触发注册)
  5. 打印启动信息
  6. 调用 run_agent(request, project_path)
  7. 打印返回的报告
  8. exit(0)

启动信息格式:
  TestPilot v0.1.0
  项目: /absolute/path/to/project
  任务: 帮我测试登录是否正常
  ──────────────────────────────────
```

---

## 四、Prompt 内容

### 4.1 prompts/AGENTS.md

```markdown
# TestPilot

你是 TestPilot，一个专精于软件测试的 AI Agent。

## 你的能力
你有 5 个工具: list_dir, read_file, write_file, search_files, run_command。
你可以用这些工具探索项目、阅读代码、生成测试、执行测试。

## 工作流程
收到用户的测试请求后，按以下顺序执行:

### 第一步: 检查已有功能文档
- 调用 list_dir 查看项目中是否存在 .testpilot/features/ 目录
- 如果有匹配当前功能的文档，读取它，直接跳到第四步
- 如果没有，继续下一步

### 第二步: 探索项目
- list_dir 查看项目顶层结构
- 读取配置文件 (pyproject.toml / package.json / pom.xml 等) 确定技术栈
- search_files 搜索与用户描述功能相关的关键词
- read_file 阅读找到的相关代码文件

### 第三步: 生成功能文档
将探索结果写入 .testpilot/features/<功能名>.md，格式:

```
# 功能: <名称>
> 生成时间: <日期>

## 技术栈
## 实现文件
## 核心流程
## 外部依赖
## 已有测试数据
## 测试策略
```

### 第四步: 阅读源码
- 按功能文档中的文件列表逐个 read_file
- 同时检查项目中是否有可用的测试数据:
  tests/fixtures/, tests/data/, conftest.py, seed 文件
- 重点理解: 输入输出、分支条件、异常处理、外部依赖

### 第五步: 生成测试代码
- 一次生成 5-8 个测试函数
- 用 write_file 写入测试文件
- 如果项目有 tests/ 目录，放在 tests/ 下；否则放项目根目录

### 第六步: 执行测试
- run_command 执行测试命令 (如 pytest xxx -v --tb=short)
- 分析执行结果

### 第七步: 处理失败
- 语法错误/导入错误 → 修复测试代码，重新执行 (最多 3 次)
- 断言失败 → 判断是测试写错还是源码有 bug
  - 测试写错 → 修复
  - 源码 bug → 记入报告

### 第八步: 输出报告
以纯文本输出最终报告，不再调用任何工具。

## 约束
- 不要修改用户的源码，只创建/修改测试文件和 .testpilot/ 下的文件
- 不要编造测试数据，优先使用项目已有的 fixture/seed 数据
- 不要生成 assert True 这种无意义断言
- 每个测试函数必须有至少一个有意义的断言
- 测试函数命名: test_<行为>_<条件>_<预期结果>
- Mock 策略: 只 mock 外部 IO (数据库/网络/文件系统)，不 mock 被测逻辑本身

## 报告格式

# 测试报告: <功能名>

## 概览
- 项目: <路径>
- 技术栈: <语言 + 框架>
- 测试文件: <路径>
- 测试数量: <N> 个

## 结果
- 通过: N 个
- 失败: N 个

## 详细结果

### [通过] test_xxx — 描述
### [失败] test_yyy — 描述
- 失败原因: ...
- 源码位置: file:line
- 建议: ...

## 发现的问题
(如果有源码 bug，列出位置和描述)

## 覆盖率
(如果执行了覆盖率检测)
```

### 4.2 prompts/SOUL.md

```markdown
## 角色
你是一个经验丰富的测试工程师。你的工作风格:
- 直接、简洁，不说废话
- 先理解再动手，不急于生成代码
- 关注测试质量而非数量
- 发现源码问题时明确指出位置和原因，给出修复建议
- 全程自主完成，不反复向用户确认
```

### 4.3 skills/testing-python/SKILL.md

```markdown
---
name: testing-python
description: Python + pytest 测试技能
requires:
  bins: ["python3", "pytest"]
---

# Python 测试技能

## 适用条件
当项目包含 pyproject.toml, setup.py, requirements.txt,
或主要代码文件为 .py 时，使用此技能。

## 技术栈约定
- 测试框架: pytest
- Mock: unittest.mock (标准库) 或 pytest-mock
- 覆盖率: pytest-cov (如果可用)

## 测试代码模板

```python
"""Tests for <功能名>"""
import pytest
from unittest.mock import patch, MagicMock

# 根据实际 import 路径调整
# from src.module import function_under_test


class TestFeatureName:
    """<功能名> 测试"""

    def test_behavior_condition_expected(self):
        """描述: 在什么条件下，期望什么结果"""
        # Arrange
        # Act
        # Assert

    def test_behavior_error_case(self):
        """描述: 异常场景"""
        with pytest.raises(ExpectedException):
            ...
```

## 执行命令
- 基本执行: pytest <test_file> -v --tb=short
- 带覆盖率: pytest <test_file> -v --tb=short --cov=<source_module> --cov-report=term-missing
- 如果 pytest 不在 PATH 中，尝试: python3 -m pytest ...

## 常见问题处理
- ModuleNotFoundError → 检查 import 路径，可能需要用 PYTHONPATH=. pytest ...
- fixture not found → 检查 conftest.py 是否在正确位置
- mock 路径错误 → mock 的路径应该是"被测模块看到的路径"，而非定义路径

## Mock 策略
- 数据库操作 → mock ORM 查询 (patch session/query)
- HTTP 请求 → mock requests.get/post 或 httpx
- 文件读写 → mock open 或用 tmp_path fixture
- 时间相关 → mock datetime.now / time.time
- 不要 mock 纯计算逻辑 (这是你要测的东西)
```

---

## 五、数据流

### 5.1 一次完整调用的消息序列

```
Turn 1:
User → "项目路径: /app\n请测试: 登录"
LLM  ← tool_use: list_dir(path="/app")

Turn 2:
User → tool_result: "src/\n  auth/\n    ..."
LLM  ← tool_use: list_dir(path="/app/.testpilot/features")

Turn 3:
User → tool_result: "Error: directory not found"   ← 首次，无 Feature Doc
LLM  ← tool_use: search_files(pattern="login", path="/app")

Turn 4:
User → tool_result: "src/auth/router.py:12: ..."
LLM  ← tool_use: read_file(path="/app/src/auth/router.py")

Turn 5:
User → tool_result: (文件内容)
LLM  ← tool_use: read_file(path="/app/src/auth/service.py")

Turn 6:
User → tool_result: (文件内容)
LLM  ← tool_use: write_file(path="/app/.testpilot/features/login.md", content="...")

Turn 7:
User → tool_result: "OK: written 856 bytes"        ← Feature Doc 写入
LLM  ← tool_use: write_file(path="/app/tests/test_login.py", content="...")

Turn 8:
User → tool_result: "OK: written 2340 bytes"       ← 测试代码写入
LLM  ← tool_use: run_command(command="cd /app && python3 -m pytest tests/test_login.py -v --tb=short")

Turn 9:
User → tool_result: "Exit code: 1\n--- stdout ---\n... 5 passed, 1 failed ..."
LLM  ← tool_use: read_file(path="/app/src/auth/service.py")  ← 分析失败原因

Turn 10:
User → tool_result: (文件内容)
LLM  ← text: "# 测试报告: 用户登录\n..."           ← 最终报告，循环结束

典型轮次: 8-15 轮
```

### 5.2 Anthropic API 消息格式

```json
// messages 数组中的一轮 tool_use + tool_result 交互:

// Assistant 消息 (包含 tool_use)
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "让我先查看项目结构。"
    },
    {
      "type": "tool_use",
      "id": "toolu_01ABC",
      "name": "list_dir",
      "input": { "path": "/app" }
    }
  ]
}

// User 消息 (包含 tool_result)
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01ABC",
      "content": "src/\n  auth/\n    router.py\n    service.py\ntests/\npyproject.toml"
    }
  ]
}
```

### 5.3 工具 schema 传给 API 的格式

```json
// tools 参数示例 (以 list_dir 为例)
{
  "name": "list_dir",
  "description": "列出目录下的文件和子目录",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "目录路径"
      },
      "max_depth": {
        "type": "integer",
        "description": "递归深度, 默认1, 最大3",
        "default": 1
      }
    },
    "required": ["path"]
  }
}
```

---

## 六、错误处理策略

### 6.1 分层错误处理

```
层级            错误类型                处理方式
─────────────────────────────────────────────────────
LLM 层          API 连接失败           重试 1 次
                Rate Limit             sleep 5s + 重试 1 次
                其他 API 错误          打印错误, exit(1)

Tool 层         文件不存在             返回 "Error: ..." 给 LLM
                命令超时               返回 "Error: timeout" 给 LLM
                命令执行失败           返回 stderr 给 LLM
                结果过长               截断 + 提示

Agent 层        LLM 不调用工具也不结束  MAX_TURNS 兜底
                LLM 返回无效 JSON      当作文本处理
                LLM 调用不存在的工具    返回错误, LLM 自己修正
```

### 6.2 关键原则

```
不要让任何异常导致 Agent 循环崩溃。

Tool 执行失败 → 把错误信息返回给 LLM → LLM 自己决定怎么处理。
这是 Agent 的核心韧性: 所有错误都变成 LLM 可处理的信息。
```

---

## 七、测试 Agent 本身

### 7.1 手动验收测试

准备一个简单的 Python 项目作为测试目标:

```
test-project/
├── src/
│   └── calculator.py     # 一个简单的计算器类
├── pyproject.toml
└── tests/
    └── (空)
```

calculator.py 内容:
```python
class Calculator:
    def add(self, a, b):
        return a + b

    def divide(self, a, b):
        return a / b     # 故意不处理除零
```

验收标准:
1. testpilot "测试计算器功能" -p ./test-project
2. Agent 应该:
    - 探索项目结构
    - 找到 calculator.py
    - 生成 .testpilot/features/calculator.md
    - 生成测试代码 (包含除零测试)
    - 执行测试
    - 报告中指出 divide 方法未处理除零异常
3. 再次运行同样命令:
    - 应该读取已有 Feature Doc，不重新探索

### 7.2 边界情况测试

```
场景                              预期行为
─────────────────────────────────────────────────────
空项目 (无代码文件)               Agent 报告"未找到相关代码"
超大文件 (>50000 字符)            截断读取, Agent 仍能工作
项目无 tests/ 目录                测试文件创建在根目录
pytest 未安装                     Skill 加载时警告
API Key 未设置                    启动时报错退出
网络中断                          重试 1 次后报错
```

---

## 八、安装与运行

### 8.1 安装方式

```bash
# 开发模式
git clone <repo>
cd testpilot
pip install -e .

# 或直接运行
python -m testpilot "测试请求" -p ./project
```

### 8.2 pyproject.toml

```toml
[project]
name = "testpilot"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "anthropic>=0.40.0",
    "click>=8.0",
]

[project.scripts]
testpilot = "testpilot.cli:main"
```

### 8.3 环境变量

```bash
# 必须
export ANTHROPIC_API_KEY="sk-..."

# 可选
export TESTPILOT_MODEL="claude-sonnet-4-5-20250929"
export TESTPILOT_MAX_TURNS=40
```

---

## 九、代码量估算

```
文件                    预估行数    说明
──────────────────────────────────────────
config.py               30         配置读取
cli.py                  35         Click 命令定义
agent.py                80         主循环
llm.py                  50         API 封装 + 重试
tools/registry.py       45         注册表
tools/file_tools.py     80         3 个文件工具
tools/search_tools.py   40         搜索工具
tools/exec_tools.py     35         命令执行工具
skills/loader.py        55         Skill 加载
──────────────────────────────────────────
Python 代码合计         ~450 行

prompts/AGENTS.md       ~80 行     Agent 行为规范
prompts/SOUL.md         ~10 行     角色定义
skills/.../SKILL.md     ~60 行     Python 测试技能
──────────────────────────────────────────
Markdown 合计           ~150 行

总计                    ~600 行
```

---

## 十、开发顺序

```
Step 1: 基础设施
  config.py + llm.py + tools/registry.py
  目标: 能调通 Anthropic API 的 tool use

Step 2: 工具实现
  file_tools.py + search_tools.py + exec_tools.py
  目标: 5 个工具各自能独立运行

Step 3: Agent 循环
  agent.py
  目标: 工具 + LLM 串起来, 能循环执行

Step 4: Prompt 与 Skill
  AGENTS.md + SOUL.md + SKILL.md + loader.py
  目标: Agent 能按照指令自主完成测试流程

Step 5: CLI 入口
  cli.py + pyproject.toml
  目标: testpilot "xxx" -p ./project 能跑通

Step 6: 验收
  用 test-project 跑通完整流程
  首次运行生成 Feature Doc
  二次运行复用 Feature Doc
```
