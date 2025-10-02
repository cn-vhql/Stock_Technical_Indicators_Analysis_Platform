# 🤝 贡献指南

感谢您对股票技术指标回测分析平台的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 报告错误和问题
- 💡 提出新功能建议
- 🔧 提交代码改进
- 📖 完善文档和示例
- 🌟 推广项目

## 📋 开始之前

### 行为准则

在参与本项目之前，请阅读并同意我们的行为准则：

- 🤝 **友善互助**：对所有贡献者保持尊重和友善
- 💬 **积极沟通**：及时回应反馈和讨论
- 🎯 **专注贡献**：提交高质量、相关的贡献
- 📚 **持续学习**：保持开放心态，相互学习

### 开发环境

确保您的开发环境满足以下要求：

```bash
# Python版本
python --version  # 需要3.8+

# 验证环境
pip list | grep streamlit
pip list | grep pandas
pip list | grep numpy
```

## 🚀 快速开始

### 1. Fork 和克隆

```bash
# 1. 在GitHub上Fork项目
# 2. 克隆您的Fork
git clone https://github.com/YOUR_USERNAME/stock-technical-indicators-platform.git
cd stock-technical-indicators-platform

# 3. 添加原始仓库为上游仓库
git remote add upstream https://github.com/original-owner/stock-technical-indicators-platform.git
```

### 2. 设置开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install pytest black flake8 mypy
```

### 3. 验证安装

```bash
# 运行应用
streamlit run app.py

# 运行测试
pytest tests/

# 代码格式检查
black --check src/
flake8 src/
```

## 📝 贡献类型

### 🐛 报告问题

提交Issue时，请包含以下信息：

```markdown
## 问题描述
简要描述遇到的问题

## 复现步骤
1. 步骤一
2. 步骤二
3. 步骤三

## 期望行为
描述您期望发生的情况

## 实际行为
描述实际发生的情况

## 环境信息
- 操作系统：
- Python版本：
- 浏览器：
- 其他相关信息：

## 附加信息
- 错误截图
- 相关日志
- 其他有助于解决问题的信息
```

### 💡 功能建议

提出新功能时，请考虑：

```markdown
## 功能描述
清晰描述您建议的新功能

## 使用场景
说明这个功能的实际应用场景

## 实现建议（可选）
- 建议的实现方式
- 涉及的文件/模块
- 技术方案

## 替代方案（可选）
是否有其他方式可以解决这个问题？
```

### 🔧 代码贡献

#### 开发流程

1. **创建分支**
```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/issue-number-description
```

2. **开发和测试**
```bash
# 编写代码
# 运行测试
pytest tests/

# 格式化代码
black src/ tests/

# 类型检查
mypy src/
```

3. **提交更改**
```bash
git add .
git commit -m "feat: add new feature description"
# 或
git commit -m "fix: resolve issue #123"
```

#### 提交规范

使用[Conventional Commits](https://www.conventionalcommits.org/)规范：

- `feat:` 新功能
- `fix:` 错误修复
- `docs:` 文档更新
- `style:` 代码格式化
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```bash
git commit -m "feat: add Bollinger Bands indicator"
git commit -m "fix: resolve RSI calculation NaN values"
git commit -m "docs: update installation guide"
```

#### 代码规范

1. **Python代码风格**
   - 遵循PEP 8规范
   - 使用Black进行格式化
   - 使用类型提示

2. **文档字符串**
```python
def calculate_sma(data: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    计算简单移动平均线

    Args:
        data: 包含价格数据的DataFrame
        period: 移动平均周期

    Returns:
        SMA序列

    Raises:
        ValueError: 当period <= 0时

    Example:
        >>> sma = calculate_sma(data, 20)
        >>> print(sma.tail())
    """
```

3. **变量命名**
   - 使用描述性名称
   - 避免缩写（除非是通用缩写）
   - 常量使用全大写

4. **错误处理**
```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

#### 测试要求

1. **单元测试**
```python
# tests/test_indicators.py
import pytest
import pandas as pd
from src.indicators import IndicatorCalculator

class TestIndicatorCalculator:
    def test_sma_calculation(self):
        """测试SMA计算"""
        # Arrange
        data = pd.DataFrame({'close': [1, 2, 3, 4, 5]})
        calc = IndicatorCalculator()

        # Act
        result = calc.calculate_indicator(data, 'SMA', {'timeperiod': 3})

        # Assert
        assert not result.empty
        assert 'SMA_3' in result.columns
```

2. **测试覆盖率**
   - 新功能需要包含测试
   - 测试覆盖率应达到80%以上
   - 关键业务逻辑需要100%覆盖

### 📖 文档贡献

#### 文档类型

1. **API文档**
   - 函数和类的文档字符串
   - 参数说明和返回值
   - 使用示例

2. **用户文档**
   - 安装指南
   - 使用教程
   - 常见问题解答

3. **开发文档**
   - 架构设计
   - 开发指南
   - 部署说明

#### 文档格式

使用Markdown格式，遵循以下约定：

```markdown
# 一级标题
## 二级标题
### 三级标题

- 列表项1
- 列表项2

`代码行`

```python
# 代码块
def function():
    pass
```

> 引用文本

[链接文本](URL)
```

## 🔄 Pull Request 流程

### 提交前检查

- [ ] 代码通过所有测试
- [ ] 代码符合项目规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 提交信息符合规范

### PR 模板

```markdown
## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 其他

## 变更描述
简要描述此PR的变更内容

## 相关Issue
Fixes #(issue number)

## 测试
- [ ] 添加了新的测试用例
- [ ] 所有测试通过
- [ ] 手动测试通过

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 自我审查了代码
- [ ] 添加了必要的注释
- [ - 更新了相关文档
- [ ] 提交信息清晰明确

## 截图（如适用）
如果是UI变更，请提供截图对比

## 其他信息
其他需要审查者了解的信息
```

### 审查流程

1. **自动检查**
   - 代码格式检查
   - 测试执行
   - 类型检查

2. **人工审查**
   - 代码逻辑审查
   - 架构合理性
   - 性能影响

3. **合并要求**
   - 至少一个审查者批准
   - 所有检查通过
   - 解决所有审查意见

## 🏷️ 发布管理

### 版本号规范

使用[语义化版本](https://semver.org/)：

- `MAJOR.MINOR.PATCH`
- `MAJOR`: 不兼容的API变更
- `MINOR`: 向后兼容的功能新增
- `PATCH`: 向后兼容的问题修正

### 发布流程

1. **更新版本号**
2. **更新CHANGELOG**
3. **创建发布标签**
4. **自动构建和发布**

## 🌟 贡献者认可

### 贡献者列表

所有贡献者将被添加到以下文件：
- `README.md` - 主要贡献者
- `AUTHORS.md` - 详细贡献者列表

### 贡献类型徽章

根据贡献类型，我们会在GitHub上给予相应的徽章：
- 🐛 Bug Hunter
- 💡 Feature Creator
- 📝 Documentation Writer
- 🌟 Community Leader

## 💬 沟通渠道

- **GitHub Issues**: 报告问题和功能请求
- **GitHub Discussions**: 一般讨论和问答
- **邮件列表**: 重要公告和讨论

## 📚 学习资源

### 推荐阅读

- [Python官方文档](https://docs.python.org/)
- [Pandas用户指南](https://pandas.pydata.org/docs/user_guide/)
- [Streamlit文档](https://docs.streamlit.io/)
- [TA-Lib文档](https://ta-lib.org/function_doc.html)

### 技术博客

- [量化投资相关文章]
- [技术分析最佳实践]
- [Python金融编程指南]

## 🆘 获取帮助

如果您在贡献过程中遇到任何问题：

1. 查看现有Issues
2. 搜索文档
3. 在GitHub Discussions中提问
4. 联系维护者

---

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

您的每一份贡献都让这个项目变得更好！

---

**再次感谢您的贡献！让我们一起构建更好的股票技术分析工具！** 🚀