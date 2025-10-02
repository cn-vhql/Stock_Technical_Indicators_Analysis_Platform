"""
条件配置模块
支持多指标组合条件设置，包括数值比较、技术形态和逻辑组合
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union, Callable
from enum import Enum
import logging
import re


class ConditionType(Enum):
    """条件类型枚举"""
    NUMERIC_COMPARE = "numeric_compare"  # 数值比较
    SIGNAL_CROSS = "signal_cross"        # 交叉信号
    TECHNICAL_PATTERN = "technical_pattern"  # 技术形态
    LOGIC_OPERATOR = "logic_operator"    # 逻辑操作符


class ComparisonOperator(Enum):
    """比较操作符枚举"""
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="


class LogicOperator(Enum):
    """逻辑操作符枚举"""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class Condition:
    """条件基类"""

    def __init__(self, condition_type: ConditionType, description: str = ""):
        """
        初始化条件

        Args:
            condition_type: 条件类型
            description: 条件描述
        """
        self.condition_type = condition_type
        self.description = description
        self.id = id(self)  # 使用对象ID作为唯一标识

    def evaluate(self, data: pd.DataFrame) -> pd.Series:
        """
        评估条件，返回布尔序列

        Args:
            data: 输入数据

        Returns:
            布尔序列，True表示条件满足
        """
        raise NotImplementedError("子类必须实现evaluate方法")

    def to_dict(self) -> Dict[str, Any]:
        """将条件转换为字典格式"""
        return {
            'id': self.id,
            'type': self.condition_type.value,
            'description': self.description
        }


class NumericCompareCondition(Condition):
    """数值比较条件类"""

    def __init__(self,
                 column: str,
                 operator: ComparisonOperator,
                 value: float,
                 description: str = ""):
        """
        初始化数值比较条件

        Args:
            column: 比较的列名
            operator: 比较操作符
            value: 比较值
            description: 条件描述
        """
        super().__init__(ConditionType.NUMERIC_COMPARE, description)
        self.column = column
        self.operator = operator
        self.value = value

        if not description:
            self.description = f"{column} {operator.value} {value}"

    def evaluate(self, data: pd.DataFrame) -> pd.Series:
        """评估数值比较条件"""
        if self.column not in data.columns:
            raise ValueError(f"数据中缺少列: {self.column}")

        series = data[self.column]

        if self.operator == ComparisonOperator.GREATER_THAN:
            return series > self.value
        elif self.operator == ComparisonOperator.GREATER_EQUAL:
            return series >= self.value
        elif self.operator == ComparisonOperator.LESS_THAN:
            return series < self.value
        elif self.operator == ComparisonOperator.LESS_EQUAL:
            return series <= self.value
        elif self.operator == ComparisonOperator.EQUAL:
            return series == self.value
        elif self.operator == ComparisonOperator.NOT_EQUAL:
            return series != self.value
        else:
            raise ValueError(f"不支持的操作符: {self.operator}")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict()
        result.update({
            'column': self.column,
            'operator': self.operator.value,
            'value': self.value
        })
        return result


class SignalCrossCondition(Condition):
    """信号交叉条件类"""

    def __init__(self,
                 fast_col: str,
                 slow_col: str,
                 cross_type: str = "golden",  # golden: 金叉, death: 死叉
                 description: str = ""):
        """
        初始化信号交叉条件

        Args:
            fast_col: 快速线列名
            slow_col: 慢速线列名
            cross_type: 交叉类型
            description: 条件描述
        """
        super().__init__(ConditionType.SIGNAL_CROSS, description)
        self.fast_col = fast_col
        self.slow_col = slow_col
        self.cross_type = cross_type

        if not description:
            cross_name = "金叉" if cross_type == "golden" else "死叉"
            self.description = f"{fast_col} 与 {slow_col} {cross_name}"

    def evaluate(self, data: pd.DataFrame) -> pd.Series:
        """评估信号交叉条件"""
        required_cols = [self.fast_col, self.slow_col]
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"数据中缺少列: {missing_cols}")

        fast = data[self.fast_col]
        slow = data[self.slow_col]

        signals = pd.Series(False, index=data.index)

        if self.cross_type == "golden":
            # 金叉：快线上穿慢线
            signals = (fast > slow) & (fast.shift(1) <= slow.shift(1))
        elif self.cross_type == "death":
            # 死叉：快线下穿慢线
            signals = (fast < slow) & (fast.shift(1) >= slow.shift(1))
        else:
            raise ValueError(f"不支持的交叉类型: {self.cross_type}")

        return signals

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict()
        result.update({
            'fast_col': self.fast_col,
            'slow_col': self.slow_col,
            'cross_type': self.cross_type
        })
        return result


class TechnicalPatternCondition(Condition):
    """技术形态条件类"""

    def __init__(self,
                 pattern_name: str,
                 pattern_func: Callable[[pd.DataFrame], pd.Series],
                 description: str = ""):
        """
        初始化技术形态条件

        Args:
            pattern_name: 形态名称
            pattern_func: 形态检测函数
            description: 条件描述
        """
        super().__init__(ConditionType.TECHNICAL_PATTERN, description)
        self.pattern_name = pattern_name
        self.pattern_func = pattern_func

        if not description:
            self.description = f"技术形态: {pattern_name}"

    def evaluate(self, data: pd.DataFrame) -> pd.Series:
        """评估技术形态条件"""
        try:
            return self.pattern_func(data)
        except Exception as e:
            raise ValueError(f"技术形态检测失败: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict()
        result.update({
            'pattern_name': self.pattern_name
        })
        return result


class LogicCondition(Condition):
    """逻辑操作条件类"""

    def __init__(self,
                 operator: LogicOperator,
                 conditions: List[Condition],
                 description: str = ""):
        """
        初始化逻辑操作条件

        Args:
            operator: 逻辑操作符
            conditions: 子条件列表
            description: 条件描述
        """
        super().__init__(ConditionType.LOGIC_OPERATOR, description)
        self.operator = operator
        self.conditions = conditions

        if not description:
            condition_descs = [cond.description for cond in conditions]
            self.description = f" {operator.value} ".join(condition_descs)

    def evaluate(self, data: pd.DataFrame) -> pd.Series:
        """评估逻辑操作条件"""
        if not self.conditions:
            return pd.Series(False, index=data.index)

        results = [condition.evaluate(data) for condition in self.conditions]

        if self.operator == LogicOperator.AND:
            result = results[0]
            for r in results[1:]:
                result = result & r
            return result

        elif self.operator == LogicOperator.OR:
            result = results[0]
            for r in results[1:]:
                result = result | r
            return result

        elif self.operator == LogicOperator.NOT:
            if len(self.conditions) != 1:
                raise ValueError("NOT操作符只能应用于单个条件")
            return ~results[0]

        else:
            raise ValueError(f"不支持的逻辑操作符: {self.operator}")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict()
        result.update({
            'operator': self.operator.value,
            'conditions': [cond.to_dict() for cond in self.conditions]
        })
        return result


class ConditionBuilder:
    """条件构建器类，用于创建和组合条件"""

    def __init__(self):
        """初始化条件构建器"""
        self.logger = logging.getLogger(__name__)

    def create_numeric_condition(self,
                               column: str,
                               operator: str,
                               value: float) -> NumericCompareCondition:
        """
        创建数值比较条件

        Args:
            column: 列名
            operator: 操作符字符串
            value: 比较值

        Returns:
            数值比较条件对象
        """
        try:
            op = ComparisonOperator(operator)
            return NumericCompareCondition(column, op, value)
        except ValueError:
            raise ValueError(f"不支持的操作符: {operator}")

    def create_cross_condition(self,
                             fast_col: str,
                             slow_col: str,
                             cross_type: str = "golden") -> SignalCrossCondition:
        """
        创建交叉信号条件

        Args:
            fast_col: 快速线列名
            slow_col: 慢速线列名
            cross_type: 交叉类型

        Returns:
            交叉信号条件对象
        """
        if cross_type not in ["golden", "death"]:
            raise ValueError("cross_type必须是'golden'或'death'")

        return SignalCrossCondition(fast_col, slow_col, cross_type)

    def create_pattern_condition(self,
                               pattern_name: str,
                               pattern_func: Callable[[pd.DataFrame], pd.Series]) -> TechnicalPatternCondition:
        """
        创建技术形态条件

        Args:
            pattern_name: 形态名称
            pattern_func: 形态检测函数

        Returns:
            技术形态条件对象
        """
        return TechnicalPatternCondition(pattern_name, pattern_func)

    def create_and_condition(self, conditions: List[Condition]) -> LogicCondition:
        """创建AND条件"""
        if len(conditions) < 2:
            raise ValueError("AND条件需要至少2个子条件")
        return LogicCondition(LogicOperator.AND, conditions)

    def create_or_condition(self, conditions: List[Condition]) -> LogicCondition:
        """创建OR条件"""
        if len(conditions) < 2:
            raise ValueError("OR条件需要至少2个子条件")
        return LogicCondition(LogicOperator.OR, conditions)

    def create_not_condition(self, condition: Condition) -> LogicCondition:
        """创建NOT条件"""
        return LogicCondition(LogicOperator.NOT, [condition])

    def parse_condition_string(self, condition_str: str) -> Condition:
        """
        解析条件字符串，创建条件对象

        Args:
            condition_str: 条件字符串，如 "RSI > 30 AND MACD > 0"

        Returns:
            条件对象
        """
        try:
            # 这是一个简化的解析器，实际应用中可能需要更复杂的语法解析
            condition_str = condition_str.strip()

            # 处理NOT操作符
            if condition_str.startswith("NOT "):
                inner_str = condition_str[4:].strip()
                inner_condition = self.parse_condition_string(inner_str)
                return self.create_not_condition(inner_condition)

            # 处理括号
            if condition_str.startswith("(") and condition_str.endswith(")"):
                inner_str = condition_str[1:-1].strip()
                return self.parse_condition_string(inner_str)

            # 处理AND操作符
            if " AND " in condition_str:
                parts = [part.strip() for part in condition_str.split(" AND ")]
                conditions = [self.parse_condition_string(part) for part in parts]
                return self.create_and_condition(conditions)

            # 处理OR操作符
            if " OR " in condition_str:
                parts = [part.strip() for part in condition_str.split(" OR ")]
                conditions = [self.parse_condition_string(part) for part in parts]
                return self.create_or_condition(conditions)

            # 处理数值比较条件
            return self._parse_numeric_condition(condition_str)

        except Exception as e:
            raise ValueError(f"解析条件字符串失败: {condition_str}, 错误: {e}")

    def _parse_numeric_condition(self, condition_str: str) -> NumericCompareCondition:
        """
        解析数值比较条件字符串

        Args:
            condition_str: 条件字符串，如 "RSI > 30"

        Returns:
            数值比较条件对象
        """
        # 使用正则表达式解析条件
        pattern = r'^(\w+)\s*(>=|<=|>|<|==|!=)\s*([-\d\.]+)$'
        match = re.match(pattern, condition_str.strip())

        if not match:
            raise ValueError(f"无效的条件格式: {condition_str}")

        column, operator, value_str = match.groups()

        try:
            value = float(value_str)
        except ValueError:
            raise ValueError(f"无效的数值: {value_str}")

        return self.create_numeric_condition(column, operator, value)


class ConditionValidator:
    """条件验证器类"""

    def __init__(self):
        """初始化条件验证器"""
        self.logger = logging.getLogger(__name__)

    def validate_condition(self, condition: Condition, data_columns: List[str]) -> Dict[str, Any]:
        """
        验证条件的有效性

        Args:
            condition: 要验证的条件
            data_columns: 可用的数据列名

        Returns:
            验证结果字典
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        try:
            # 检查条件中引用的列是否存在
            if isinstance(condition, NumericCompareCondition):
                if condition.column not in data_columns:
                    result['valid'] = False
                    result['errors'].append(f"列 '{condition.column}' 不存在")

            elif isinstance(condition, SignalCrossCondition):
                missing_cols = [col for col in [condition.fast_col, condition.slow_col]
                               if col not in data_columns]
                if missing_cols:
                    result['valid'] = False
                    result['errors'].append(f"列 {missing_cols} 不存在")

            elif isinstance(condition, LogicCondition):
                # 递归验证子条件
                for sub_condition in condition.conditions:
                    sub_result = self.validate_condition(sub_condition, data_columns)
                    if not sub_result['valid']:
                        result['valid'] = False
                        result['errors'].extend(sub_result['errors'])
                    result['warnings'].extend(sub_result['warnings'])

        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"验证过程中出现错误: {e}")

        return result

    def validate_condition_list(self,
                              conditions: List[Condition],
                              data_columns: List[str]) -> Dict[str, Any]:
        """
        验证条件列表

        Args:
            conditions: 条件列表
            data_columns: 可用的数据列名

        Returns:
            验证结果字典
        """
        all_errors = []
        all_warnings = []
        all_valid = True

        for i, condition in enumerate(conditions):
            result = self.validate_condition(condition, data_columns)
            if not result['valid']:
                all_valid = False
                all_errors.extend([f"条件{i+1}: {error}" for error in result['errors']])
            all_warnings.extend([f"条件{i+1}: {warning}" for warning in result['warnings']])

        return {
            'valid': all_valid,
            'errors': all_errors,
            'warnings': all_warnings
        }