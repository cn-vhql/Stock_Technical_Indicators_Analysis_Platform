"""
技术指标计算模块
基于talib库实现各种技术指标的计算，支持参数配置和扩展
"""

import talib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
import logging


class IndicatorCalculator:
    """技术指标计算器类，负责计算各种技术指标"""

    def __init__(self):
        """初始化指标计算器"""
        self.logger = logging.getLogger(__name__)

        # 预定义的指标配置
        self.indicator_configs = {
            'SMA': {
                'name': '简单移动平均线',
                'params': {'timeperiod': [5, 10, 20, 30, 60]},
                'function': talib.SMA,
                'input_cols': ['close'],
                'output_names': lambda params: [f"SMA_{params['timeperiod']}"]
            },
            'EMA': {
                'name': '指数移动平均线',
                'params': {'timeperiod': [5, 10, 20, 30, 60]},
                'function': talib.EMA,
                'input_cols': ['close'],
                'output_names': lambda params: [f"EMA_{params['timeperiod']}"]
            },
            'MACD': {
                'name': 'MACD指标',
                'params': {
                    'fastperiod': [12, 15, 20],
                    'slowperiod': [26, 30, 35],
                    'signalperiod': [9, 10, 12]
                },
                'function': talib.MACD,
                'input_cols': ['close'],
                'output_names': lambda params: [
                    f"MACD_{params['fastperiod']}_{params['slowperiod']}_{params['signalperiod']}",
                    f"MACD_signal_{params['fastperiod']}_{params['slowperiod']}_{params['signalperiod']}",
                    f"MACD_hist_{params['fastperiod']}_{params['slowperiod']}_{params['signalperiod']}"
                ]
            },
            'RSI': {
                'name': '相对强弱指标',
                'params': {'timeperiod': [6, 12, 14, 21]},
                'function': talib.RSI,
                'input_cols': ['close'],
                'output_names': lambda params: [f"RSI_{params['timeperiod']}"]
            },
            'BOLL': {
                'name': '布林带',
                'params': {
                    'timeperiod': [20, 30],
                    'nbdevup': [2, 3],
                    'nbdevdn': [2, 3]
                },
                'function': talib.BBANDS,
                'input_cols': ['close'],
                'output_names': lambda params: [
                    f"BOLL_upper_{params['timeperiod']}_{params['nbdevup']}_{params['nbdevdn']}",
                    f"BOLL_middle_{params['timeperiod']}_{params['nbdevup']}_{params['nbdevdn']}",
                    f"BOLL_lower_{params['timeperiod']}_{params['nbdevup']}_{params['nbdevdn']}"
                ]
            },
            'KDJ': {
                'name': '随机指标KDJ',
                'params': {
                    'fastk_period': [9, 14],
                    'slowk_period': [3, 5],
                    'slowd_period': [3, 5]
                },
                'function': talib.STOCH,
                'input_cols': ['high', 'low', 'close'],
                'output_names': lambda params: [
                    f"KDJ_slowk_{params['fastk_period']}_{params['slowk_period']}_{params['slowd_period']}",
                    f"KDJ_slowd_{params['fastk_period']}_{params['slowk_period']}_{params['slowd_period']}"
                ]
            },
            'CCI': {
                'name': '商品通道指标',
                'params': {'timeperiod': [14, 20, 30]},
                'function': talib.CCI,
                'input_cols': ['high', 'low', 'close'],
                'output_names': lambda params: [f"CCI_{params['timeperiod']}"]
            },
            'WILLR': {
                'name': '威廉指标',
                'params': {'timeperiod': [14, 20]},
                'function': talib.WILLR,
                'input_cols': ['high', 'low', 'close'],
                'output_names': lambda params: [f"WILLR_{params['timeperiod']}"]
            },
            'ATR': {
                'name': '平均真实波幅',
                'params': {'timeperiod': [14, 20]},
                'function': talib.ATR,
                'input_cols': ['high', 'low', 'close'],
                'output_names': lambda params: [f"ATR_{params['timeperiod']}"]
            },
            'OBV': {
                'name': '能量潮',
                'params': {},
                'function': talib.OBV,
                'input_cols': ['close', 'volume'],
                'output_names': lambda params: ["OBV"]
            },
            'VOLUME_SMA': {
                'name': '成交量移动平均',
                'params': {'timeperiod': [5, 10, 20]},
                'function': talib.SMA,
                'input_cols': ['volume'],
                'output_names': lambda params: [f"VOLUME_SMA_{params['timeperiod']}"]
            }
        }

    def get_available_indicators(self) -> Dict[str, str]:
        """
        获取可用的技术指标列表

        Returns:
            指标代码到指标名称的映射
        """
        return {code: config['name'] for code, config in self.indicator_configs.items()}

    def get_indicator_params(self, indicator_code: str) -> Dict[str, List[Any]]:
        """
        获取指标的参数选项

        Args:
            indicator_code: 指标代码

        Returns:
            参数字典，键为参数名，值为可选参数值列表
        """
        if indicator_code not in self.indicator_configs:
            raise ValueError(f"不支持的指标: {indicator_code}")

        return self.indicator_configs[indicator_code]['params']

    def calculate_indicator(self,
                          data: pd.DataFrame,
                          indicator_code: str,
                          params: Dict[str, Any]) -> pd.DataFrame:
        """
        计算单个技术指标

        Args:
            data: 股票数据DataFrame
            indicator_code: 指标代码
            params: 指标参数

        Returns:
            包含计算结果的DataFrame

        Raises:
            ValueError: 当指标代码无效或参数错误时
        """
        if indicator_code not in self.indicator_configs:
            raise ValueError(f"不支持的指标: {indicator_code}")

        config = self.indicator_configs[indicator_code]
        function = config['function']
        input_cols = config['input_cols']

        # 检查输入数据是否包含所需列
        missing_cols = [col for col in input_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"数据缺少必需列: {missing_cols}")

        # 准备输入参数
        input_args = []
        for col in input_cols:
            # 确保数据类型为float64，避免类型错误
            series = data[col].astype(np.float64).values
            # 转换为numpy数组
            input_args.append(series)

        # 添加指标参数
        for param_name, param_value in params.items():
            if param_name in config['params']:
                input_args.append(param_value)

        try:
            # 计算指标
            result = function(*input_args)

            # 处理返回结果
            if isinstance(result, tuple):
                # 多个输出值的指标（如MACD, BOLL等）
                output_names = config['output_names'](params)
                result_dict = {}
                for i, name in enumerate(output_names):
                    if i < len(result):
                        result_dict[name] = result[i]
                result_df = pd.DataFrame(result_dict, index=data.index)
            else:
                # 单个输出值的指标
                output_name = config['output_names'](params)[0]
                result_df = pd.DataFrame({output_name: result}, index=data.index)

            return result_df

        except Exception as e:
            self.logger.error(f"计算指标失败: {indicator_code}, 参数: {params}, 错误: {e}")
            raise ValueError(f"计算指标失败: {e}")

    def calculate_multiple_indicators(self,
                                    data: pd.DataFrame,
                                    indicator_configs: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        计算多个技术指标

        Args:
            data: 股票数据DataFrame
            indicator_configs: 指标配置列表，每个配置包含'code'和'params'字段

        Returns:
            包含所有计算结果的DataFrame
        """
        result_df = data.copy()

        for config in indicator_configs:
            indicator_code = config['code']
            params = config['params']

            try:
                indicator_result = self.calculate_indicator(data, indicator_code, params)
                result_df = pd.concat([result_df, indicator_result], axis=1)
            except Exception as e:
                self.logger.warning(f"跳过指标计算: {indicator_code}, 错误: {e}")
                continue

        return result_df

    def add_custom_indicator(self,
                           code: str,
                           name: str,
                           function,
                           input_cols: List[str],
                           output_names: callable,
                           params: Dict[str, List[Any]] = None):
        """
        添加自定义指标

        Args:
            code: 指标代码
            name: 指标名称
            function: 指标计算函数
            input_cols: 输入列名列表
            output_names: 输出列名生成函数
            params: 参数配置
        """
        self.indicator_configs[code] = {
            'name': name,
            'params': params or {},
            'function': function,
            'input_cols': input_cols,
            'output_names': output_names
        }

    def validate_params(self, indicator_code: str, params: Dict[str, Any]) -> bool:
        """
        验证指标参数是否有效

        Args:
            indicator_code: 指标代码
            params: 参数字典

        Returns:
            参数是否有效
        """
        if indicator_code not in self.indicator_configs:
            return False

        valid_params = self.indicator_configs[indicator_code]['params']

        for param_name, param_value in params.items():
            if param_name not in valid_params:
                return False
            if param_value not in valid_params[param_name]:
                return False

        return True

    def generate_indicator_display_name(self, indicator_code: str, params: Dict[str, Any]) -> str:
        """
        生成指标显示名称

        Args:
            indicator_code: 指标代码
            params: 参数字典

        Returns:
            指标显示名称
        """
        if indicator_code not in self.indicator_configs:
            return f"未知指标_{indicator_code}"

        config = self.indicator_configs[indicator_code]
        output_names = config['output_names'](params)

        if isinstance(output_names, list) and len(output_names) > 0:
            # 对于多输出指标的复杂名称，使用第一个输出名
            base_name = output_names[0]
        else:
            # 使用指标代码和参数组合
            param_str = "_".join([str(v) for v in params.values()])
            base_name = f"{indicator_code}_{param_str}"

        return base_name

    def get_indicator_description(self, indicator_code: str) -> str:
        """
        获取指标描述

        Args:
            indicator_code: 指标代码

        Returns:
            指标描述字符串
        """
        if indicator_code not in self.indicator_configs:
            return "未知指标"

        config = self.indicator_configs[indicator_code]
        name = config['name']
        params = config['params']

        description = f"{name}\n参数:\n"
        for param_name, param_values in params.items():
            description += f"  {param_name}: {param_values}\n"

        return description


class TechnicalSignalDetector:
    """技术信号检测器，用于检测各种技术形态和信号"""

    def __init__(self):
        """初始化信号检测器"""
        self.logger = logging.getLogger(__name__)

    def detect_ma_cross(self, data: pd.DataFrame, fast_period: int = 5, slow_period: int = 20) -> pd.Series:
        """
        检测均线交叉信号

        Args:
            data: 包含价格数据的DataFrame
            fast_period: 快速均线周期
            slow_period: 慢速均线周期

        Returns:
            信号序列 (1: 金叉, -1: 死叉, 0: 无信号)
        """
        if 'close' not in data.columns:
            raise ValueError("数据缺少close列")

        fast_ma = talib.SMA(data['close'].values, timeperiod=fast_period)
        slow_ma = talib.SMA(data['close'].values, timeperiod=slow_period)

        signals = pd.Series(0, index=data.index)

        # 金叉：快线上穿慢线
        fast_ma_series = pd.Series(fast_ma, index=data.index)
        slow_ma_series = pd.Series(slow_ma, index=data.index)
        signals[(fast_ma_series > slow_ma_series) & (fast_ma_series.shift(1) <= slow_ma_series.shift(1))] = 1

        # 死叉：快线下穿慢线
        signals[(fast_ma_series < slow_ma_series) & (fast_ma_series.shift(1) >= slow_ma_series.shift(1))] = -1

        return signals

    def detect_macd_cross(self, data: pd.DataFrame, macd_col: str, signal_col: str) -> pd.Series:
        """
        检测MACD交叉信号

        Args:
            data: 包含MACD数据的DataFrame
            macd_col: MACD列名
            signal_col: Signal列名

        Returns:
            信号序列 (1: 金叉, -1: 死叉, 0: 无信号)
        """
        if macd_col not in data.columns or signal_col not in data.columns:
            raise ValueError(f"数据缺少列: {macd_col} 或 {signal_col}")

        macd = data[macd_col]
        signal = data[signal_col]

        signals = pd.Series(0, index=data.index)

        # MACD线上穿信号线
        signals[(macd > signal) & (macd.shift(1) <= signal.shift(1))] = 1

        # MACD线下穿信号线
        signals[(macd < signal) & (macd.shift(1) >= signal.shift(1))] = -1

        return signals

    def detect_rsi_overbought_oversold(self,
                                     data: pd.DataFrame,
                                     rsi_col: str,
                                     overbought: float = 70,
                                     oversold: float = 30) -> pd.Series:
        """
        检测RSI超买超卖信号

        Args:
            data: 包含RSI数据的DataFrame
            rsi_col: RSI列名
            overbought: 超买阈值
            oversold: 超卖阈值

        Returns:
            信号序列 (1: 超卖反弹, -1: 超买回调, 0: 无信号)
        """
        if rsi_col not in data.columns:
            raise ValueError(f"数据缺少列: {rsi_col}")

        rsi = data[rsi_col]
        signals = pd.Series(0, index=data.index)

        # 超卖反弹：RSI从下往上突破oversold
        signals[(rsi > oversold) & (rsi.shift(1) <= oversold)] = 1

        # 超买回调：RSI从上往下跌破overbought
        signals[(rsi < overbought) & (rsi.shift(1) >= overbought)] = -1

        return signals

    def detect_bollinger_bands_breakout(self,
                                      data: pd.DataFrame,
                                      upper_col: str,
                                      lower_col: str,
                                      close_col: str = 'close') -> pd.Series:
        """
        检测布林带突破信号

        Args:
            data: 包含布林带数据的DataFrame
            upper_col: 上轨列名
            lower_col: 下轨列名
            close_col: 收盘价列名

        Returns:
            信号序列 (1: 向上突破, -1: 向下突破, 0: 无信号)
        """
        required_cols = [upper_col, lower_col, close_col]
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"数据缺少列: {missing_cols}")

        close = data[close_col]
        upper = data[upper_col]
        lower = data[lower_col]

        signals = pd.Series(0, index=data.index)

        # 向上突破上轨
        signals[(close > upper) & (close.shift(1) <= upper.shift(1))] = 1

        # 向下突破下轨
        signals[(close < lower) & (close.shift(1) >= lower.shift(1))] = -1

        return signals