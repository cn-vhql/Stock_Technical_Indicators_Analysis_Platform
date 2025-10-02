"""
工具函数模块
提供异常处理、数据验证等通用功能
"""

import pandas as pd
import numpy as np
import re
from typing import Any, List, Dict, Optional, Union
import logging
from functools import wraps


class StockAnalysisError(Exception):
    """股票分析异常基类"""
    pass


class DataValidationError(StockAnalysisError):
    """数据验证异常"""
    pass


class IndicatorCalculationError(StockAnalysisError):
    """指标计算异常"""
    pass


class BacktestError(StockAnalysisError):
    """回测异常"""
    pass


def validate_stock_code(stock_code: str) -> bool:
    """
    验证股票代码格式

    Args:
        stock_code: 股票代码

    Returns:
        是否为有效格式
    """
    # 支持的股票代码格式：6位数字
    pattern = r'^\d{6}$'
    return bool(re.match(pattern, stock_code))


def validate_date_format(date_str: str) -> bool:
    """
    验证日期格式

    Args:
        date_str: 日期字符串

    Returns:
        是否为有效格式
    """
    pattern = r'^\d{8}$'  # YYYYMMDD格式
    return bool(re.match(pattern, date_str))


def validate_dataframe(df: pd.DataFrame, required_columns: List[str] = None) -> bool:
    """
    验证DataFrame格式和内容

    Args:
        df: 要验证的DataFrame
        required_columns: 必需的列名列表

    Returns:
        是否通过验证

    Raises:
        DataValidationError: 验证失败时
    """
    if df is None or df.empty:
        raise DataValidationError("DataFrame为空")

    if required_columns:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise DataValidationError(f"缺少必需的列: {missing_columns}")

    # 检查是否有重复索引
    if df.index.duplicated().any():
        raise DataValidationError("DataFrame包含重复的索引")

    return True


def validate_numeric_data(series: pd.Series, allow_nan: bool = True) -> bool:
    """
    验证数值数据

    Args:
        series: 要验证的数据序列
        allow_nan: 是否允许NaN值

    Returns:
        是否通过验证

    Raises:
        DataValidationError: 验证失败时
    """
    if not pd.api.types.is_numeric_dtype(series):
        raise DataValidationError(f"序列 {series.name} 不是数值类型")

    if not allow_nan and series.isna().any():
        raise DataValidationError(f"序列 {series.name} 包含NaN值")

    return True


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误

    Args:
        numerator: 分子
        denominator: 分母
        default: 除零时的默认值

    Returns:
        除法结果或默认值
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def handle_errors(error_type: type = StockAnalysisError, default_return: Any = None):
    """
    错误处理装饰器

    Args:
        error_type: 要捕获的异常类型
        default_return: 发生异常时的默认返回值
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_type as e:
                logging.error(f"函数 {func.__name__} 执行失败: {e}")
                return default_return
            except Exception as e:
                logging.error(f"函数 {func.__name__} 发生未知错误: {e}")
                raise StockAnalysisError(f"未知错误: {e}")
        return wrapper
    return decorator


def clean_data(df: pd.DataFrame,
               remove_nan: bool = True,
               remove_inf: bool = True,
               fill_method: str = 'forward') -> pd.DataFrame:
    """
    清理数据

    Args:
        df: 要清理的DataFrame
        remove_nan: 是否移除NaN值
        remove_inf: 是否移除无穷大值
        fill_method: 填充方法 ('forward', 'backward', 'mean', 'zero')

    Returns:
        清理后的DataFrame
    """
    cleaned_df = df.copy()

    # 处理无穷大值
    if remove_inf:
        cleaned_df = cleaned_df.replace([np.inf, -np.inf], np.nan)

    # 填充或移除NaN值
    if remove_nan:
        if fill_method == 'forward':
            cleaned_df = cleaned_df.fillna(method='ffill')
        elif fill_method == 'backward':
            cleaned_df = cleaned_df.fillna(method='bfill')
        elif fill_method == 'mean':
            cleaned_df = cleaned_df.fillna(cleaned_df.mean())
        elif fill_method == 'zero':
            cleaned_df = cleaned_df.fillna(0)
        else:
            cleaned_df = cleaned_df.dropna()

    return cleaned_df


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    标准化列名

    Args:
        df: 要标准化的DataFrame

    Returns:
        列名标准化后的DataFrame
    """
    normalized_df = df.copy()

    # 转换为小写，替换空格和特殊字符
    new_columns = []
    for col in df.columns:
        new_col = str(col).lower().strip()
        new_col = re.sub(r'[^a-z0-9_]', '_', new_col)
        new_col = re.sub(r'_+', '_', new_col)
        new_columns.append(new_col)

    normalized_df.columns = new_columns

    return normalized_df


def calculate_returns(prices: pd.Series, periods: int = 1) -> pd.Series:
    """
    计算收益率

    Args:
        prices: 价格序列
        periods: 计算周期

    Returns:
        收益率序列
    """
    return prices.pct_change(periods=periods)


def calculate_log_returns(prices: pd.Series, periods: int = 1) -> pd.Series:
    """
    计算对数收益率

    Args:
        prices: 价格序列
        periods: 计算周期

    Returns:
        对数收益率序列
    """
    return np.log(prices / prices.shift(periods=periods))


def calculate_volatility(returns: pd.Series, window: int = 252, annualize: bool = True) -> float:
    """
    计算波动率

    Args:
        returns: 收益率序列
        window: 滚动窗口大小
        annualize: 是否年化

    Returns:
        波动率
    """
    vol = returns.rolling(window=window).std().iloc[-1]

    if annualize:
        vol = vol * np.sqrt(252)  # 年化因子

    return vol


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    计算夏普比率

    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率

    Returns:
        夏普比率
    """
    excess_returns = returns - risk_free_rate
    if excess_returns.std() == 0:
        return 0.0

    return excess_returns.mean() / excess_returns.std()


def calculate_max_drawdown(prices: pd.Series) -> Dict[str, Any]:
    """
    计算最大回撤

    Args:
        prices: 价格序列

    Returns:
        包含回撤信息的字典
    """
    cumulative_returns = (1 + prices.pct_change()).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max

    max_drawdown = drawdown.min()
    max_drawdown_date = drawdown.idxmin()

    # 计算回撤期间
    drawdown_periods = []
    in_drawdown = False
    start_date = None

    for date, dd in drawdown.items():
        if dd < 0 and not in_drawdown:
            in_drawdown = True
            start_date = date
        elif dd >= 0 and in_drawdown:
            in_drawdown = False
            drawdown_periods.append({
                'start': start_date,
                'end': date,
                'duration': (date - start_date).days
            })

    return {
        'max_drawdown': max_drawdown,
        'max_drawdown_date': max_drawdown_date,
        'drawdown_periods': drawdown_periods,
        'current_drawdown': drawdown.iloc[-1]
    }


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    格式化百分比显示

    Args:
        value: 数值
        decimal_places: 小数位数

    Returns:
        格式化后的百分比字符串
    """
    return f"{value:.{decimal_places}%}"


def format_number(value: Union[int, float], decimal_places: int = 2) -> str:
    """
    格式化数字显示

    Args:
        value: 数值
        decimal_places: 小数位数

    Returns:
        格式化后的数字字符串
    """
    if pd.isna(value):
        return "N/A"

    if isinstance(value, int) or value.is_integer():
        return f"{int(value):,}"
    else:
        return f"{value:,.{decimal_places}f}"


def convert_chinese_number(chinese_str: str) -> Union[int, float]:
    """
    转换中文数字字符串为数字

    Args:
        chinese_str: 中文数字字符串

    Returns:
        转换后的数字
    """
    chinese_numbers = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '十': 10, '百': 100, '千': 1000, '万': 10000,
        '亿': 100000000
    }

    result = 0
    temp = 0

    for char in chinese_str:
        if char in chinese_numbers:
            num = chinese_numbers[char]
            if num >= 10:
                if temp == 0:
                    temp = 1
                result += temp * num
                temp = 0
            else:
                temp = temp * 10 + num

    result += temp
    return result


def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    验证日期范围是否有效

    Args:
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        是否有效

    Raises:
        DataValidationError: 日期范围无效时
    """
    try:
        start = pd.to_datetime(start_date, format='%Y%m%d')
        end = pd.to_datetime(end_date, format='%Y%m%d')

        if start >= end:
            raise DataValidationError("开始日期必须早于结束日期")

        if end > pd.to_datetime('today'):
            raise DataValidationError("结束日期不能晚于今天")

        return True

    except ValueError as e:
        raise DataValidationError(f"日期格式错误: {e}")


def check_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    检查数据质量

    Args:
        df: 要检查的DataFrame

    Returns:
        数据质量报告
    """
    report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'null_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'data_types': df.dtypes.to_dict(),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'completeness_rate': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    }

    # 检查数值列的基本统计
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 0:
        report['numeric_summary'] = df[numeric_columns].describe().to_dict()

    return report


def log_performance(func):
    """
    性能日志装饰器

    Args:
        func: 要装饰的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.info(f"函数 {func.__name__} 执行成功，耗时: {execution_time:.2f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"函数 {func.__name__} 执行失败，耗时: {execution_time:.2f}秒，错误: {e}")
            raise

    return wrapper