"""
回测分析模块
对技术指标条件进行回测，分析信号出现后的股价表现
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from .conditions import Condition


@dataclass
class SignalEvent:
    """信号事件数据类"""
    timestamp: datetime
    signal_price: float
    signal_type: str  # buy, sell, neutral
    condition_description: str


@dataclass
class BacktestResult:
    """回测结果数据类"""
    signals: List[SignalEvent]
    returns: List[float]
    holding_periods: List[int]
    win_rate: float
    avg_return: float
    max_return: float
    min_return: float
    std_return: float
    total_signals: int
    profitable_signals: int
    losing_signals: int
    avg_holding_period: float
    parameters: Dict[str, Any]


class BacktestAnalyzer:
    """回测分析器类"""

    def __init__(self):
        """初始化回测分析器"""
        self.logger = logging.getLogger(__name__)

    def run_backtest(self,
                    data: pd.DataFrame,
                    condition: Condition,
                    holding_period: int = 5,
                    price_column: str = 'close') -> BacktestResult:
        """
        运行回测分析

        Args:
            data: 股票数据DataFrame
            condition: 触发条件
            holding_period: 持有天数
            price_column: 价格列名

        Returns:
            回测结果对象

        Raises:
            ValueError: 当输入数据无效时
        """
        if data.empty:
            raise ValueError("输入数据为空")

        if price_column not in data.columns:
            raise ValueError(f"数据中缺少价格列: {price_column}")

        self.logger.info(f"开始回测分析，持有期: {holding_period}天")

        # 计算条件信号
        signals = self._calculate_signals(data, condition)

        if not signals.any():
            self.logger.warning("未找到满足条件的信号")
            return self._create_empty_result(condition, holding_period)

        # 计算每个信号的收益
        signal_events, returns, holding_periods = self._calculate_signal_returns(
            data, signals, holding_period, price_column
        )

        # 计算统计指标
        stats = self._calculate_statistics(returns, holding_periods)

        result = BacktestResult(
            signals=signal_events,
            returns=returns,
            holding_periods=holding_periods,
            win_rate=stats['win_rate'],
            avg_return=stats['avg_return'],
            max_return=stats['max_return'],
            min_return=stats['min_return'],
            std_return=stats['std_return'],
            total_signals=len(returns),
            profitable_signals=stats['profitable_count'],
            losing_signals=stats['losing_count'],
            avg_holding_period=stats['avg_holding_period'],
            parameters={
                'condition': condition.description,
                'holding_period': holding_period,
                'price_column': price_column,
                'data_period': f"{data.index[0]} to {data.index[-1]}"
            }
        )

        self.logger.info(f"回测完成，总信号数: {result.total_signals}, 胜率: {result.win_rate:.2%}")
        return result

    def _calculate_signals(self, data: pd.DataFrame, condition: Condition) -> pd.Series:
        """
        计算条件信号

        Args:
            data: 股票数据
            condition: 条件对象

        Returns:
            布尔序列，True表示信号触发
        """
        try:
            return condition.evaluate(data)
        except Exception as e:
            self.logger.error(f"计算条件信号失败: {e}")
            raise ValueError(f"计算条件信号失败: {e}")

    def _calculate_signal_returns(self,
                                data: pd.DataFrame,
                                signals: pd.Series,
                                holding_period: int,
                                price_column: str) -> Tuple[List[SignalEvent], List[float], List[int]]:
        """
        计算每个信号的收益

        Args:
            data: 股票数据
            signals: 信号序列
            holding_period: 持有天数
            price_column: 价格列名

        Returns:
            信号事件列表、收益率列表、持有期列表
        """
        signal_events = []
        returns = []
        holding_periods = []

        # 获取信号日期
        signal_dates = signals[signals].index

        for signal_date in signal_dates:
            if signal_date not in data.index:
                continue

            signal_price = data.loc[signal_date, price_column]

            # 计算目标日期
            target_date = signal_date + timedelta(days=holding_period)

            # 找到目标日期或最接近的交易日
            target_price = self._find_target_price(data, target_date, price_column)

            if target_price is None:
                continue

            # 计算收益率
            return_rate = (target_price - signal_price) / signal_price

            # 创建信号事件
            signal_event = SignalEvent(
                timestamp=signal_date,
                signal_price=signal_price,
                signal_type="buy",  # 默认为买入信号
                condition_description=""
            )

            signal_events.append(signal_event)
            returns.append(return_rate)
            holding_periods.append(holding_period)

        return signal_events, returns, holding_periods

    def _find_target_price(self,
                          data: pd.DataFrame,
                          target_date: datetime,
                          price_column: str) -> Optional[float]:
        """
        查找目标日期的价格

        Args:
            data: 股票数据
            target_date: 目标日期
            price_column: 价格列名

        Returns:
            目标价格或None（如果找不到）
        """
        # 尝试精确匹配
        if target_date in data.index:
            return data.loc[target_date, price_column]

        # 寻找最接近的日期
        available_dates = data.index[data.index >= target_date]
        if not available_dates.empty:
            closest_date = available_dates[0]
            return data.loc[closest_date, price_column]

        # 如果没有未来的日期，使用最后一个可用日期
        if not data.empty:
            return data.iloc[-1][price_column]

        return None

    def _calculate_statistics(self,
                            returns: List[float],
                            holding_periods: List[int]) -> Dict[str, Any]:
        """
        计算统计指标

        Args:
            returns: 收益率列表
            holding_periods: 持有期列表

        Returns:
            统计指标字典
        """
        if not returns:
            return {
                'win_rate': 0.0,
                'avg_return': 0.0,
                'max_return': 0.0,
                'min_return': 0.0,
                'std_return': 0.0,
                'profitable_count': 0,
                'losing_count': 0,
                'avg_holding_period': 0.0
            }

        returns_array = np.array(returns)
        profitable_count = np.sum(returns_array > 0)
        losing_count = np.sum(returns_array < 0)

        return {
            'win_rate': profitable_count / len(returns) if returns else 0.0,
            'avg_return': np.mean(returns_array),
            'max_return': np.max(returns_array),
            'min_return': np.min(returns_array),
            'std_return': np.std(returns_array),
            'profitable_count': int(profitable_count),
            'losing_count': int(losing_count),
            'avg_holding_period': np.mean(holding_periods) if holding_periods else 0.0
        }

    def _create_empty_result(self, condition: Condition, holding_period: int) -> BacktestResult:
        """
        创建空的回测结果

        Args:
            condition: 条件对象
            holding_period: 持有期

        Returns:
            空的回测结果
        """
        return BacktestResult(
            signals=[],
            returns=[],
            holding_periods=[],
            win_rate=0.0,
            avg_return=0.0,
            max_return=0.0,
            min_return=0.0,
            std_return=0.0,
            total_signals=0,
            profitable_signals=0,
            losing_signals=0,
            avg_holding_period=0.0,
            parameters={
                'condition': condition.description,
                'holding_period': holding_period,
                'note': 'No signals found'
            }
        )

    def run_multiple_backtests(self,
                             data: pd.DataFrame,
                             conditions: List[Condition],
                             holding_periods: List[int] = None) -> List[BacktestResult]:
        """
        运行多个回测

        Args:
            data: 股票数据
            conditions: 条件列表
            holding_periods: 持有期列表

        Returns:
            回测结果列表
        """
        if holding_periods is None:
            holding_periods = [3, 5, 10, 20]

        results = []
        total_tests = len(conditions) * len(holding_periods)

        self.logger.info(f"开始运行 {total_tests} 个回测")

        test_count = 0
        for condition in conditions:
            for holding_period in holding_periods:
                test_count += 1
                try:
                    result = self.run_backtest(data, condition, holding_period)
                    results.append(result)
                    self.logger.info(f"完成测试 {test_count}/{total_tests}")
                except Exception as e:
                    self.logger.error(f"测试失败 {test_count}/{total_tests}: {e}")
                    continue

        return results

    def compare_results(self, results: List[BacktestResult]) -> pd.DataFrame:
        """
        比较多个回测结果

        Args:
            results: 回测结果列表

        Returns:
            比较结果DataFrame
        """
        if not results:
            return pd.DataFrame()

        comparison_data = []
        for result in results:
            comparison_data.append({
                '条件': result.parameters['condition'],
                '持有期': result.parameters['holding_period'],
                '信号数': result.total_signals,
                '胜率': f"{result.win_rate:.2%}",
                '平均收益': f"{result.avg_return:.2%}",
                '最大收益': f"{result.max_return:.2%}",
                '最小收益': f"{result.min_return:.2%}",
                '收益标准差': f"{result.std_return:.2%}",
                '盈利信号': result.profitable_signals,
                '亏损信号': result.losing_signals
            })

        df = pd.DataFrame(comparison_data)

        # 按胜率排序
        df = df.sort_values('胜率', ascending=False)

        return df

    def generate_report(self, result: BacktestResult) -> str:
        """
        生成回测报告

        Args:
            result: 回测结果

        Returns:
            报告字符串
        """
        report = f"""
## 回测分析报告

### 基本信息
- **条件**: {result.parameters['condition']}
- **持有期**: {result.parameters['holding_period']} 天
- **数据期间**: {result.parameters['data_period']}
- **价格列**: {result.parameters['price_column']}

### 信号统计
- **总信号数**: {result.total_signals}
- **盈利信号数**: {result.profitable_signals}
- **亏损信号数**: {result.losing_signals}
- **平均持有期**: {result.avg_holding_period:.1f} 天

### 收益统计
- **胜率**: {result.win_rate:.2%}
- **平均收益**: {result.avg_return:.2%}
- **最大收益**: {result.max_return:.2%}
- **最小收益**: {result.min_return:.2%}
- **收益标准差**: {result.std_return:.2%}

### 分析结论
"""

        if result.total_signals == 0:
            report += "- **未找到满足条件的信号**\n"
        elif result.win_rate >= 0.6:
            report += "- **策略表现优秀**，胜率较高，建议进一步验证\n"
        elif result.win_rate >= 0.5:
            report += "- **策略表现一般**，有一定参考价值\n"
        else:
            report += "- **策略表现较差**，胜率低于50%，不建议使用\n"

        if result.avg_return > 0:
            report += f"- **平均正收益**，每笔交易平均盈利 {result.avg_return:.2%}\n"
        else:
            report += f"- **平均负收益**，每笔交易平均亏损 {abs(result.avg_return):.2%}\n"

        return report


class PerformanceAnalyzer:
    """性能分析器类"""

    def __init__(self):
        """初始化性能分析器"""
        self.logger = logging.getLogger(__name__)

    def calculate_returns_distribution(self, returns: List[float], bins: int = 20) -> Dict[str, Any]:
        """
        计算收益率分布

        Args:
            returns: 收益率列表
            bins: 分箱数量

        Returns:
            分布统计字典
        """
        if not returns:
            return {'histogram': [], 'bins': [], 'statistics': {}}

        returns_array = np.array(returns)

        # 计算直方图
        hist, bin_edges = np.histogram(returns_array, bins=bins)

        # 计算统计指标
        statistics = {
            'mean': np.mean(returns_array),
            'median': np.median(returns_array),
            'std': np.std(returns_array),
            'min': np.min(returns_array),
            'max': np.max(returns_array),
            'skewness': self._calculate_skewness(returns_array),
            'kurtosis': self._calculate_kurtosis(returns_array)
        }

        return {
            'histogram': hist.tolist(),
            'bins': bin_edges.tolist(),
            'statistics': statistics
        }

    def _calculate_skewness(self, data: np.ndarray) -> float:
        """计算偏度"""
        if len(data) < 3:
            return 0.0

        mean = np.mean(data)
        std = np.std(data)

        if std == 0:
            return 0.0

        return np.mean(((data - mean) / std) ** 3)

    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """计算峰度"""
        if len(data) < 4:
            return 0.0

        mean = np.mean(data)
        std = np.std(data)

        if std == 0:
            return 0.0

        return np.mean(((data - mean) / std) ** 4) - 3

    def calculate_rolling_performance(self,
                                    data: pd.DataFrame,
                                    condition: Condition,
                                    window_size: int = 252) -> pd.DataFrame:
        """
        计算滚动窗口性能

        Args:
            data: 股票数据
            condition: 条件对象
            window_size: 窗口大小（交易日数）

        Returns:
            滚动性能DataFrame
        """
        if len(data) < window_size:
            raise ValueError(f"数据长度 {len(data)} 小于窗口大小 {window_size}")

        performance_data = []

        for i in range(window_size, len(data)):
            window_data = data.iloc[i-window_size:i]

            try:
                # 在窗口期内运行回测
                result = self._run_simple_backtest(window_data, condition)

                performance_data.append({
                    'date': data.index[i],
                    'win_rate': result.win_rate,
                    'avg_return': result.avg_return,
                    'total_signals': result.total_signals
                })

            except Exception as e:
                self.logger.warning(f"滚动窗口回测失败: {e}")
                continue

        if not performance_data:
            return pd.DataFrame()

        df = pd.DataFrame(performance_data)
        df.set_index('date', inplace=True)

        return df

    def _run_simple_backtest(self, data: pd.DataFrame, condition: Condition) -> BacktestResult:
        """运行简单回测（内部方法）"""
        analyzer = BacktestAnalyzer()
        return analyzer.run_backtest(data, condition, holding_period=5)