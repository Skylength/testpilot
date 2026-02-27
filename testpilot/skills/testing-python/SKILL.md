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
