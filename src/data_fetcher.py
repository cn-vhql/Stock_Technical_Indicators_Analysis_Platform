"""
数据获取模块
使用akshare库获取股票历史行情数据，支持缓存机制
"""

import akshare as ak
import pandas as pd
import os
import pickle
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging


class DataFetcher:
    """数据获取器类，负责从akshare获取股票数据并实现缓存机制"""

    def __init__(self, cache_dir: str = "cache"):
        """
        初始化数据获取器

        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = cache_dir
        self._ensure_cache_dir()

        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_file_path(self, symbol: str, period: str = "daily") -> str:
        """
        获取缓存文件路径

        Args:
            symbol: 股票代码
            period: 数据周期 (daily, weekly, monthly)

        Returns:
            缓存文件的完整路径
        """
        return os.path.join(self.cache_dir, f"{symbol}_{period}.pkl")

    def _is_cache_valid(self, cache_file_path: str, max_age_days: int = 1) -> bool:
        """
        检查缓存是否有效

        Args:
            cache_file_path: 缓存文件路径
            max_age_days: 缓存最大有效天数

        Returns:
            缓存是否有效
        """
        if not os.path.exists(cache_file_path):
            return False

        file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_file_path))
        if datetime.now() - file_mtime > timedelta(days=max_age_days):
            return False

        return True

    def _load_from_cache(self, cache_file_path: str) -> Optional[pd.DataFrame]:
        """
        从缓存加载数据

        Args:
            cache_file_path: 缓存文件路径

        Returns:
            缓存的DataFrame或None
        """
        try:
            with open(cache_file_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            self.logger.warning(f"加载缓存失败: {e}")
            return None

    def _save_to_cache(self, data: pd.DataFrame, cache_file_path: str):
        """
        保存数据到缓存

        Args:
            data: 要缓存的数据
            cache_file_path: 缓存文件路径
        """
        try:
            with open(cache_file_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            self.logger.warning(f"保存缓存失败: {e}")

    def get_stock_data(self,
                      symbol: str,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                      period: str = "daily",
                      adjust: str = "qfq",
                      use_cache: bool = True) -> pd.DataFrame:
        """
        获取股票历史行情数据

        Args:
            symbol: 股票代码 (如: '000001', '600000')
            start_date: 开始日期 (格式: '20200101')
            end_date: 结束日期 (格式: '20231231')
            period: 数据周期 ('daily', 'weekly', 'monthly')
            adjust: 复权方式 ('qfq': 前复权, 'hfq': 后复权, '': 不复权)
            use_cache: 是否使用缓存

        Returns:
            包含股票数据的DataFrame

        Raises:
            ValueError: 当股票代码无效或数据获取失败时
        """
        cache_file_path = self._get_cache_file_path(symbol, period)

        # 检查缓存
        if use_cache and self._is_cache_valid(cache_file_path):
            cached_data = self._load_from_cache(cache_file_path)
            if cached_data is not None:
                self.logger.info(f"从缓存加载数据: {symbol}")
                return self._filter_data_by_date(cached_data, start_date, end_date)

        try:
            # 格式化股票代码
            if len(symbol) == 6:
                if symbol.startswith('6') or symbol.startswith('9'):
                    full_symbol = f"sh{symbol}"
                else:
                    full_symbol = f"sz{symbol}"
            else:
                full_symbol = symbol

            self.logger.info(f"正在获取股票数据: {full_symbol}")

            # 获取股票数据
            if period == "daily":
                data = ak.stock_zh_a_hist(symbol=symbol,
                                        start_date=start_date or "20200101",
                                        end_date=end_date or "20991231",
                                        adjust=adjust)
            elif period == "weekly":
                data = ak.stock_zh_a_hist(symbol=symbol,
                                        start_date=start_date or "20200101",
                                        end_date=end_date or "20991231",
                                        period="weekly",
                                        adjust=adjust)
            elif period == "monthly":
                data = ak.stock_zh_a_hist(symbol=symbol,
                                        start_date=start_date or "20200101",
                                        end_date=end_date or "20991231",
                                        period="monthly",
                                        adjust=adjust)
            else:
                raise ValueError(f"不支持的数据周期: {period}")

            if data.empty:
                raise ValueError(f"未获取到股票 {symbol} 的数据")

            # 标准化列名
            data = self._standardize_columns(data)

            # 保存到缓存
            if use_cache:
                self._save_to_cache(data, cache_file_path)

            self.logger.info(f"成功获取股票数据: {symbol}, 共 {len(data)} 条记录")
            return data

        except Exception as e:
            self.logger.error(f"获取股票数据失败: {symbol}, 错误: {e}")
            raise ValueError(f"获取股票数据失败: {e}")

    def _standardize_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        标准化DataFrame列名

        Args:
            data: 原始数据DataFrame

        Returns:
            标准化列名后的DataFrame
        """
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            '振幅': 'amplitude',
            '涨跌幅': 'change_pct',
            '涨跌额': 'change_amount',
            '换手率': 'turnover'
        }

        # 重命名列
        data = data.rename(columns=column_mapping)

        # 确保日期列为datetime格式
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            data.set_index('date', inplace=True)

        # 确保数值列为float类型
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
        for col in numeric_columns:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')

        return data.sort_index()

    def _filter_data_by_date(self,
                           data: pd.DataFrame,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """
        按日期范围过滤数据

        Args:
            data: 原始数据
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            过滤后的数据
        """
        if start_date is not None:
            start_date = pd.to_datetime(start_date)
            data = data[data.index >= start_date]

        if end_date is not None:
            end_date = pd.to_datetime(end_date)
            data = data[data.index <= end_date]

        return data

    def clear_cache(self, symbol: Optional[str] = None):
        """
        清理缓存

        Args:
            symbol: 要清理的股票代码，如果为None则清理所有缓存
        """
        if symbol:
            cache_file = self._get_cache_file_path(symbol)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                self.logger.info(f"已清理缓存: {symbol}")
        else:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    os.remove(os.path.join(self.cache_dir, filename))
            self.logger.info("已清理所有缓存")

    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存信息

        Returns:
            包含缓存统计信息的字典
        """
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]

        cache_info = {
            'cache_count': len(cache_files),
            'cache_files': cache_files,
            'cache_size_mb': sum(
                os.path.getsize(os.path.join(self.cache_dir, f))
                for f in cache_files
            ) / (1024 * 1024)
        }

        return cache_info