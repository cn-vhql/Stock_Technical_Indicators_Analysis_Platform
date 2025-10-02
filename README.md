# 📈 股票技术指标回测分析平台

<div align="center">

![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

[![Stars](https://img.shields.io/github/stars/cn-vhql/stock-technical-indicators-platform.svg?style=social&label=Star)](https://github.com/cn-vhql/stock-technical-indicators-platform)
[![Forks](https://img.shields.io/github/forks/cn-vhql/stock-technical-indicators-platform.svg?style=social&label=Fork)](https://github.com/cn-vhql/stock-technical-indicators-platform)
[![Issues](https://img.shields.io/github/issues/cn-vhql/stock-technical-indicators-platform.svg)](https://github.com/cn-vhql/stock-technical-indicators-platform/issues)

一个功能强大、界面美观的**交互式股票技术指标回测分析平台**，基于Python构建，使用Streamlit提供Web界面，支持多种技术指标计算、条件配置和回测分析。

</div>

## ✨ 项目特色

- 🎯 **专业级回测分析**：支持多指标组合策略的精确回测
- 📊 **丰富的技术指标**：基于talib库内置多种主流技术指标，支持参数自定义
- 🎨 **现代化界面**：基于Streamlit的响应式Web界面，美观易用
- ⚡ **高性能处理**：智能缓存机制，支持大规模数据分析
- 🔧 **高度可扩展**：模块化设计，易于添加自定义指标和策略
- 📈 **专业图表**：集成Plotly绘制交互式K线图和技术指标图

## 🌟 核心功能

### 📊 数据获取模块
- **多市场支持**：A股、期货等市场数据
- **智能缓存**：自动缓存机制，提高查询效率
- **灵活配置**：支持日线、周线、月线，前复权、后复权等
- **实时更新**：基于akshare库获取市场数据

### 📈 技术指标计算
- **趋势指标**：SMA、EMA、MACD、布林带
- **摆荡指标**：RSI、KDJ、CCI、威廉指标
- **成交量指标**：OBV、成交量均线
- **波动率指标**：ATR
- **多版本支持**：同一指标不同参数（如SMA_5、SMA_10、SMA_20）

### 🎯 条件配置系统
- **数值比较**：RSI>70、MACD>0等
- **交叉信号**：金叉、死叉 detection
- **逻辑组合**：AND、OR、NOT复杂条件
- **动态管理**：添加、编辑、删除条件配置

### 🔍 回测分析引擎
- **精确回测**：信号触发后的收益分析
- **统计指标**：胜率、平均收益、最大回撤等
- **风险分析**：收益分布、波动率计算
- **详细报告**：完整的回测结果和策略评估

### 📊 可视化展示
- **交互式K线图**：价格走势与技术指标叠加
- **分类副图**：趋势、摆荡、成交量指标分离显示
- **信号标记**：交易信号在图表上的可视化
- **收益分析图**：回测结果的专业图表展示

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 操作系统：Windows / macOS / Linux

### 一键安装

```bash
# 克隆项目
git clone https://github.com/cn-vhql/stock-technical-indicators-platform.git
cd stock-technical-indicators-platform

# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app.py
```

应用将在浏览器中自动打开：**http://localhost:8501**


## 📖 详细文档

### 基础使用指南

#### 1. 数据获取
- 输入6位股票代码（如：000001、600000）
- 选择时间范围和数据周期
- 选择复权方式
- 点击"获取数据"

#### 2. 指标配置
- 选择技术指标类型
- 设置指标参数（周期、倍数等）
- 支持同一指标多参数配置
- 批量计算所有配置指标

#### 3. 条件设置
- 创建交易条件（数值比较、交叉信号）
- 组合多个条件（AND、OR逻辑）
- 预览条件描述和影响

#### 4. 回测分析
- 设置持有期天数
- 运行回测分析
- 查看详细报告和图表

### 高级功能

#### 多指标策略示例

```
策略示例：均线突破 + RSI过滤
条件：SMA_5 > SMA_20 AND RSI_14 < 70
解释：短期均线上穿长期均线，且RSI未超买
```

#### 风险控制参数
- 持有期：1-60天可调
- 止损条件：可自定义

## 🏗️ 技术架构

```
stock-technical-indicators-platform/
├── 📁 src/                     # 核心模块
│   ├── data_fetcher.py        # 数据获取
│   ├── indicators.py          # 技术指标计算
│   ├── conditions.py          # 条件配置
│   ├── backtest.py            # 回测分析
│   └── utils.py               # 工具函数
├── 📁 tests/                   # 测试用例
├── 📁 docs/                    # 文档
├── 📁 examples/                # 示例代码
├── app.py                     # 主应用
├── requirements.txt           # 依赖清单
├── LICENSE                    # GPL协议
└── README.md                  # 项目说明
```

### 技术栈
- **前端**：Streamlit + Plotly
- **后端**：Python + Pandas + NumPy
- **数据源**：AKShare
- **指标计算**：TA-Lib
- **可视化**：Plotly.js

## 📊 功能演示

### 主界面展示
- 📈 K线图与技术指标叠加显示
- 📊 分类副图展示不同类型指标
- 🎯 信号点标记和说明
- 📋 回测结果统计面板

![alt text](/docs/image.png)
![alt text](/docs/image-1.png)
![alt text](/docs/image-2.png)
![alt text](/docs/image-3.png)
![alt text](/docs/image-4.png)

### 回测报告
- 📊 胜率和收益率统计
- 📈 收益分布直方图
- 📋 详细信号列表
- ⚠️ 风险提示和建议

## 🔧 开发指南

### 添加自定义指标

```python
# 在 src/indicators.py 中添加
def add_custom_indicator(self):
    def custom_indicator(data, timeperiod=14):
        # 自定义指标计算逻辑
        return result

    self.indicator_configs['CUSTOM'] = {
        'name': '自定义指标',
        'params': {'timeperiod': [5, 10, 20]},
        'function': custom_indicator,
        'input_cols': ['close', 'volume'],
        'output_names': lambda params: [f"CUSTOM_{params['timeperiod']}"]
    }
```

### 自定义条件类型

```python
from conditions import Condition

class CustomCondition(Condition):
    def evaluate(self, data):
        # 自定义条件评估逻辑
        return signals
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 贡献方式
- 🐛 **报告问题**：提交Issue描述bug或建议
- 💡 **功能建议**：提出新功能或改进想法
- 🔧 **代码贡献**：提交Pull Request
- 📖 **文档完善**：改进文档和示例


## 📋 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新详情。

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- 📊 完整技术指标支持
- 🎯 回测分析功能
- 🎨 Streamlit Web界面

## 📄 许可证

本项目基于 **GPL v3** 开源协议。查看 [LICENSE](LICENSE) 了解详情。

```
股票技术指标回测分析平台
Copyright (C) 2024  Stock Analysis Platform Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
```

## ⚠️ 免责声明

**重要提示**：本工具仅供学习和研究使用，不构成任何投资建议。

- 📊 历史回测结果不代表未来表现
- 💰 投资有风险，决策需谨慎
- 🔍 使用前请充分理解工具原理和限制
- 📈 建议结合其他分析方法综合判断

## 🙏 致谢

感谢以下开源项目的支持：
- [Streamlit](https://streamlit.io/) - Web应用框架
- [AKShare](https://akshare.akfamily.xyz/) - 金融数据接口
- [TA-Lib](https://ta-lib.org/) - 技术分析库
- [Plotly](https://plotly.com/) - 交互式图表
- [Pandas](https://pandas.pydata.org/) - 数据处理

## 📞 联系作者

- 📧 **邮箱**：yl_zhangqiang@foxmail.com
- 🐛 **Issues**：[GitHub Issues](https://github.com/cn-vhql/stock-technical-indicators-platform/issues)
- 💬 **讨论**：[GitHub Discussions](https://github.com/cn-vhql/stock-technical-indicators-platform/discussions)

---

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐ Star！**

Made with ❤️ by Stock Analysis Platform Team

</div>