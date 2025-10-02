"""
股票技术指标回测分析平台 - 核心模块

这是一个基于Python的交互式股票技术指标回测分析平台，允许用户
通过配置技术指标条件对历史行情进行回测，分析策略表现。

主要模块：
- data_fetcher: 数据获取模块
- indicators: 技术指标计算模块
- conditions: 条件配置模块
- backtest: 回测分析模块
- utils: 工具函数模块
"""

__version__ = "1.0.0"
__author__ = "Stock Analysis Platform Team"
__email__ = "contact@example.com"
__license__ = "GPL-3.0"

from .data_fetcher import DataFetcher
from .indicators import IndicatorCalculator, TechnicalSignalDetector
from .conditions import ConditionBuilder, ConditionValidator
from .backtest import BacktestAnalyzer, PerformanceAnalyzer
from .utils import *

__all__ = [
    'DataFetcher',
    'IndicatorCalculator',
    'TechnicalSignalDetector',
    'ConditionBuilder',
    'ConditionValidator',
    'BacktestAnalyzer',
    'PerformanceAnalyzer'
]