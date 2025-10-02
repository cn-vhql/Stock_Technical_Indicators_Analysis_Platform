"""
基础使用示例
演示如何使用股票技术指标回测分析平台的核心功能
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_fetcher import DataFetcher
from indicators import IndicatorCalculator
from conditions import ConditionBuilder
from backtest import BacktestAnalyzer


def main():
    """主函数：演示完整的使用流程"""
    print("🚀 股票技术指标回测分析平台 - 基础使用示例")
    print("=" * 60)

    # 1. 数据获取
    print("\n📊 步骤1: 获取股票数据")
    data_fetcher = DataFetcher()

    try:
        # 获取平安银行(000001)的历史数据
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

        data = data_fetcher.get_stock_data(
            symbol="000001",
            start_date=start_date,
            end_date=end_date,
            period="daily",
            adjust="qfq"
        )

        print(f"✅ 成功获取 {len(data)} 条数据")
        print(f"   数据范围: {data.index[0].date()} 至 {data.index[-1].date()}")
        print(f"   价格范围: {data['close'].min():.2f} - {data['close'].max():.2f}")

    except Exception as e:
        print(f"❌ 数据获取失败: {e}")
        return

    # 2. 技术指标计算
    print("\n📈 步骤2: 计算技术指标")
    indicator_calc = IndicatorCalculator()

    # 配置要计算的指标
    indicator_configs = [
        {'code': 'SMA', 'params': {'timeperiod': 5}},
        {'code': 'SMA', 'params': {'timeperiod': 20}},
        {'code': 'RSI', 'params': {'timeperiod': 14}},
        {'code': 'MACD', 'params': {'fastperiod': 12, 'slowperiod': 26, 'signalperiod': 9}}
    ]

    try:
        indicators_data = indicator_calc.calculate_multiple_indicators(data, indicator_configs)
        print("✅ 技术指标计算完成")
        print(f"   计算了 {len(indicator_configs)} 个指标")
        print("   指标列表:")
        for config in indicator_configs:
            indicator_name = indicator_calc.generate_indicator_display_name(config['code'], config['params'])
            print(f"   - {indicator_name}")

    except Exception as e:
        print(f"❌ 指标计算失败: {e}")
        return

    # 3. 条件配置
    print("\n🎯 步骤3: 设置交易条件")
    condition_builder = ConditionBuilder()

    # 创建一个简单的交易条件：5日均线上穿20日均线
    try:
        # 金叉条件
        golden_cross = condition_builder.create_cross_condition(
            fast_col="SMA_5",
            slow_col="SMA_20",
            cross_type="golden"
        )

        print(f"✅ 交易条件创建成功: {golden_cross.description}")

        # 检查条件在数据中的信号
        signals = golden_cross.evaluate(indicators_data)
        signal_count = signals.sum()
        print(f"   在数据中找到 {signal_count} 个信号")

    except Exception as e:
        print(f"❌ 条件创建失败: {e}")
        return

    # 4. 回测分析
    print("\n🔍 步骤4: 运行回测分析")
    backtest_analyzer = BacktestAnalyzer()

    try:
        # 运行回测，持有期设为10天
        result = backtest_analyzer.run_backtest(
            data=indicators_data,
            condition=golden_cross,
            holding_period=10
        )

        print("✅ 回测分析完成")
        print(f"   总信号数: {result.total_signals}")
        print(f"   胜率: {result.win_rate:.2%}")
        print(f"   平均收益: {result.avg_return:.2%}")
        print(f"   最大收益: {result.max_return:.2%}")
        print(f"   最小收益: {result.min_return:.2%}")

        if result.total_signals > 0:
            print(f"\n📊 详细统计:")
            print(f"   盈利信号: {result.profitable_signals}")
            print(f"   亏损信号: {result.losing_signals}")
            print(f"   收益标准差: {result.std_return:.2%}")
            print(f"   平均持有期: {result.avg_holding_period:.1f} 天")

            # 显示前5个信号
            if result.signals:
                print(f"\n📋 信号示例 (前5个):")
                for i, signal in enumerate(result.signals[:5]):
                    print(f"   {i+1}. {signal.timestamp.strftime('%Y-%m-%d')} - "
                          f"信号价格: {signal.signal_price:.2f}")

    except Exception as e:
        print(f"❌ 回测分析失败: {e}")
        return

    # 5. 生成报告
    print("\n📄 步骤5: 生成分析报告")
    try:
        report = backtest_analyzer.generate_report(result)
        print(report)

    except Exception as e:
        print(f"❌ 报告生成失败: {e}")

    print("\n" + "=" * 60)
    print("🎉 示例演示完成！")
    print("\n💡 提示:")
    print("- 这个示例展示了基本的API使用方法")
    print("- 您可以通过修改参数来尝试不同的策略")
    print("- 更多功能请参考完整的Web界面: streamlit run app.py")
    print("- 查看文档了解更多高级功能")


def advanced_example():
    """高级使用示例：多条件组合策略"""
    print("\n🚀 高级示例：多条件组合策略")
    print("=" * 60)

    # 这里可以添加更复杂的策略示例
    # 比如RSI过滤的均线突破策略等
    pass


if __name__ == "__main__":
    try:
        main()
        # 取消注释下面的行来运行高级示例
        # advanced_example()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"\n\n❌ 程序执行出错: {e}")
        print("请检查环境配置和依赖安装")