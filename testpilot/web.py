"""TestPilot Web 界面"""
import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from testpilot.config import (
    LLMConfig,
    PRESET_MODELS,
)
from testpilot.agent import run_agent

app = FastAPI(title="TestPilot", description="测试专精 AI Agent")

# 存储运行中的任务
_tasks: dict[str, dict] = {}


class TestRequest(BaseModel):
    """测试请求"""
    request: str
    project_path: str = "."
    preset: str | None = None
    provider: str | None = None
    model: str | None = None
    base_url: str | None = None
    api_key: str | None = None


class PresetInfo(BaseModel):
    """预设信息"""
    name: str
    provider: str
    model: str


# ============================================================
# API 端点
# ============================================================

@app.get("/api/presets")
async def list_presets() -> list[PresetInfo]:
    """获取所有预设模型"""
    return [
        PresetInfo(name=name, provider=cfg["provider"], model=cfg["model"])
        for name, cfg in PRESET_MODELS.items()
    ]


@app.post("/api/test")
async def run_test(req: TestRequest) -> dict:
    """运行测试"""
    import os

    # 构建 LLM 配置
    try:
        if req.preset:
            llm_config = LLMConfig.from_preset(req.preset)
            if req.api_key:
                llm_config.api_key = req.api_key
        elif req.provider or req.model or req.base_url:
            _provider = req.provider or "anthropic"
            _model = req.model or "claude-sonnet-4-5-20250929"
            _api_key = req.api_key or os.environ.get("TESTPILOT_API_KEY") or ""

            if _provider == "anthropic" and not _api_key:
                _api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            elif _provider == "openai" and not _api_key:
                _api_key = os.environ.get("OPENAI_API_KEY", "")

            llm_config = LLMConfig.custom(
                provider=_provider,
                model=_model,
                api_key=_api_key,
                base_url=req.base_url,
            )
        else:
            llm_config = LLMConfig.from_env()

        llm_config.validate()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 验证项目路径
    project_path = Path(req.project_path).resolve()
    if not project_path.exists():
        raise HTTPException(status_code=400, detail=f"项目路径不存在: {project_path}")

    # 导入工具模块
    from testpilot import tools  # noqa

    # 运行 Agent
    try:
        result = await asyncio.to_thread(
            run_agent,
            req.request,
            str(project_path),
            llm_config=llm_config,
        )
        return {
            "success": True,
            "output": result.output,
            "stats": {
                "duration": result.stats.duration_formatted,
                "total_turns": result.stats.total_turns,
                "input_tokens": result.stats.input_tokens,
                "output_tokens": result.stats.output_tokens,
                "total_tokens": result.stats.total_tokens,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 前端页面
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TestPilot - 测试专精 AI Agent</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            text-align: center;
            padding: 40px 0;
        }
        header h1 {
            font-size: 2.5em;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        header p {
            color: #888;
            font-size: 1.1em;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .card h2 {
            font-size: 1.2em;
            margin-bottom: 16px;
            color: #00d4ff;
        }
        .form-group {
            margin-bottom: 16px;
        }
        .form-group label {
            display: block;
            margin-bottom: 6px;
            font-weight: 500;
            color: #aaa;
        }
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.3);
            color: #fff;
            font-size: 14px;
        }
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #00d4ff;
        }
        .form-group textarea {
            min-height: 80px;
            resize: vertical;
        }
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }
        .btn {
            padding: 14px 28px;
            border-radius: 8px;
            border: none;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            color: #fff;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
        }
        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .output-card {
            background: rgba(0, 0, 0, 0.4);
        }
        .output-content {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 13px;
            line-height: 1.6;
            padding: 16px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            max-height: 500px;
            overflow-y: auto;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }
        .stat-item {
            background: rgba(0, 212, 255, 0.1);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #00d4ff;
        }
        .stat-label {
            font-size: 0.85em;
            color: #888;
            margin-top: 4px;
        }
        .loading {
            display: none;
            align-items: center;
            gap: 10px;
            color: #00d4ff;
        }
        .loading.active {
            display: flex;
        }
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid rgba(0, 212, 255, 0.3);
            border-top-color: #00d4ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .hidden {
            display: none;
        }
        .error {
            color: #ff6b6b;
            background: rgba(255, 107, 107, 0.1);
            padding: 12px;
            border-radius: 8px;
            margin-top: 16px;
        }
        .toggle-advanced {
            color: #00d4ff;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 16px;
        }
        .advanced-options {
            display: none;
        }
        .advanced-options.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 TestPilot</h1>
            <p>测试专精 AI Agent - 一句话驱动的自主测试工具</p>
        </header>

        <div class="card">
            <h2>📝 测试配置</h2>
            <form id="testForm">
                <div class="form-group">
                    <label for="request">测试请求</label>
                    <textarea id="request" placeholder="例如: 帮我测试登录是否正常" required></textarea>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="projectPath">项目路径</label>
                        <input type="text" id="projectPath" value="." placeholder="项目目录路径">
                    </div>
                    <div class="form-group">
                        <label for="preset">预设模型</label>
                        <select id="preset">
                            <option value="">-- 选择预设 --</option>
                        </select>
                    </div>
                </div>

                <div class="toggle-advanced" onclick="toggleAdvanced()">
                    ▶ 高级选项
                </div>

                <div class="advanced-options" id="advancedOptions">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="provider">提供商</label>
                            <select id="provider">
                                <option value="">自动</option>
                                <option value="anthropic">Anthropic</option>
                                <option value="openai">OpenAI</option>
                                <option value="openai-compatible">OpenAI 兼容</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="model">模型名称</label>
                            <input type="text" id="model" placeholder="自定义模型名称">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="baseUrl">Base URL</label>
                            <input type="text" id="baseUrl" placeholder="API Base URL">
                        </div>
                        <div class="form-group">
                            <label for="apiKey">API Key</label>
                            <input type="password" id="apiKey" placeholder="可选，覆盖默认 Key">
                        </div>
                    </div>
                </div>

                <div style="display: flex; align-items: center; gap: 20px; margin-top: 20px;">
                    <button type="submit" class="btn btn-primary" id="submitBtn">
                        🧪 开始测试
                    </button>
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <span>正在执行测试...</span>
                    </div>
                </div>
            </form>
        </div>

        <div class="card output-card hidden" id="resultCard">
            <h2>📊 测试结果</h2>
            <div class="output-content" id="output"></div>
            <div class="stats" id="stats"></div>
            <div class="error hidden" id="error"></div>
        </div>
    </div>

    <script>
        // 加载预设列表
        async function loadPresets() {
            try {
                const res = await fetch('/api/presets');
                const presets = await res.json();
                const select = document.getElementById('preset');
                presets.forEach(p => {
                    const option = document.createElement('option');
                    option.value = p.name;
                    option.textContent = `${p.name} (${p.provider})`;
                    select.appendChild(option);
                });
            } catch (e) {
                console.error('Failed to load presets:', e);
            }
        }

        function toggleAdvanced() {
            const el = document.getElementById('advancedOptions');
            const toggle = document.querySelector('.toggle-advanced');
            el.classList.toggle('show');
            toggle.textContent = el.classList.contains('show') ? '▼ 高级选项' : '▶ 高级选项';
        }

        document.getElementById('testForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const resultCard = document.getElementById('resultCard');
            const output = document.getElementById('output');
            const stats = document.getElementById('stats');
            const error = document.getElementById('error');

            // 收集表单数据
            const data = {
                request: document.getElementById('request').value,
                project_path: document.getElementById('projectPath').value || '.',
                preset: document.getElementById('preset').value || null,
                provider: document.getElementById('provider').value || null,
                model: document.getElementById('model').value || null,
                base_url: document.getElementById('baseUrl').value || null,
                api_key: document.getElementById('apiKey').value || null,
            };

            // 显示加载状态
            submitBtn.disabled = true;
            loading.classList.add('active');
            resultCard.classList.remove('hidden');
            output.textContent = '正在执行测试，请稍候...';
            stats.innerHTML = '';
            error.classList.add('hidden');

            try {
                const res = await fetch('/api/test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });

                const result = await res.json();

                if (!res.ok) {
                    throw new Error(result.detail || '请求失败');
                }

                // 显示结果
                output.textContent = result.output;

                // 显示统计
                const s = result.stats;
                stats.innerHTML = `
                    <div class="stat-item">
                        <div class="stat-value">${s.duration}</div>
                        <div class="stat-label">耗时</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${s.total_turns}</div>
                        <div class="stat-label">轮次</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${s.input_tokens.toLocaleString()}</div>
                        <div class="stat-label">输入 Token</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${s.output_tokens.toLocaleString()}</div>
                        <div class="stat-label">输出 Token</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${s.total_tokens.toLocaleString()}</div>
                        <div class="stat-label">总 Token</div>
                    </div>
                `;

            } catch (err) {
                error.textContent = '❌ 错误: ' + err.message;
                error.classList.remove('hidden');
                output.textContent = '';
            } finally {
                submitBtn.disabled = false;
                loading.classList.remove('active');
            }
        });

        // 初始化
        loadPresets();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index():
    """首页"""
    return HTML_TEMPLATE


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    return app


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """启动 Web 服务器"""
    import uvicorn
    uvicorn.run(app, host=host, port=port)
