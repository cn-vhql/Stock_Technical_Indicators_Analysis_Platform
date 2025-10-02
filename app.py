"""
主应用程序 - Streamlit UI界面
股票技术指标回测分析平台的用户界面
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

# 导入自定义模块
from data_fetcher import DataFetcher
from indicators import IndicatorCalculator, TechnicalSignalDetector
from conditions import ConditionBuilder, ConditionValidator
from backtest import BacktestAnalyzer, PerformanceAnalyzer


# 配置页面
st.set_page_config(
    page_title="股票技术指标回测分析平台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_session_state():
    """初始化会话状态"""
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'indicators_data' not in st.session_state:
        st.session_state.indicators_data = None
    if 'backtest_results' not in st.session_state:
        st.session_state.backtest_results = None
    if 'condition' not in st.session_state:
        st.session_state.condition = None
    if 'configured_indicators' not in st.session_state:
        st.session_state.configured_indicators = []
    if 'editing_indicator' not in st.session_state:
        st.session_state.editing_indicator = None
    if 'last_indicator_configs' not in st.session_state:
        st.session_state.last_indicator_configs = []


def sidebar_data_input():
    """侧边栏数据输入区域"""
    st.sidebar.markdown("## 📊 数据获取")

    # 股票代码输入
    symbol = st.sidebar.text_input(
        "股票代码",
        value="000001",
        help="请输入6位股票代码，如：000001（平安银行）、600000（浦发银行）"
    )

    # 日期范围选择
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date_input = st.date_input(
            "开始日期",
            value=datetime.strptime(start_date, "%Y%m%d"),
            help="选择开始日期"
        )
    with col2:
        end_date_input = st.date_input(
            "结束日期",
            value=datetime.strptime(end_date, "%Y%m%d"),
            help="选择结束日期"
        )

    # 数据周期选择
    period = st.sidebar.selectbox(
        "数据周期",
        ["daily", "weekly", "monthly"],
        format_func=lambda x: {"daily": "日线", "weekly": "周线", "monthly": "月线"}[x],
        help="选择K线数据周期"
    )

    # 复权方式选择
    adjust = st.sidebar.selectbox(
        "复权方式",
        ["qfq", "hfq", ""],
        format_func=lambda x: {"qfq": "前复权", "hfq": "后复权", "": "不复权"}[x],
        help="选择价格复权方式"
    )

    # 获取数据按钮
    if st.sidebar.button("🔄 获取数据", type="primary"):
        if symbol:
            try:
                with st.spinner(f"正在获取股票 {symbol} 的数据..."):
                    # 初始化数据获取器
                    data_fetcher = DataFetcher()

                    # 格式化日期
                    start_str = start_date_input.strftime("%Y%m%d")
                    end_str = end_date_input.strftime("%Y%m%d")

                    # 获取数据
                    data = data_fetcher.get_stock_data(
                        symbol=symbol,
                        start_date=start_str,
                        end_date=end_str,
                        period=period,
                        adjust=adjust
                    )

                    # 保存到会话状态
                    st.session_state.data = data

                    st.sidebar.success(f"✅ 成功获取 {len(data)} 条数据")
                    st.rerun()

            except Exception as e:
                st.sidebar.error(f"❌ 获取数据失败: {str(e)}")
        else:
            st.sidebar.error("❌ 请输入股票代码")


def sidebar_indicators_config():
    """侧边栏指标配置区域"""
    st.sidebar.markdown("## 📈 技术指标配置")

    if st.session_state.data is None:
        st.sidebar.info("请先获取股票数据")
        return

    # 初始化指标计算器
    indicator_calc = IndicatorCalculator()
    available_indicators = indicator_calc.get_available_indicators()

    # 检查是否已配置指标
    if 'configured_indicators' not in st.session_state:
        st.session_state.configured_indicators = []

    st.sidebar.markdown("### 📋 已配置的指标")

    # 显示已配置的指标
    if st.session_state.configured_indicators:
        for i, config in enumerate(st.session_state.configured_indicators):
            indicator_name = config['display_name']
            params_desc = ", ".join([f"{k}={v}" for k, v in config['params'].items()])

            col1, col2, col3 = st.sidebar.columns([3, 1, 1])
            with col1:
                st.sidebar.write(f"• {indicator_name}")
                st.sidebar.caption(f"  {params_desc}")
            with col2:
                if st.sidebar.button("✏️", key=f"edit_{i}", help="编辑"):
                    # 切换到编辑模式
                    st.session_state.editing_indicator = i
                    st.rerun()
            with col3:
                if st.sidebar.button("🗑️", key=f"delete_{i}", help="删除"):
                    st.session_state.configured_indicators.pop(i)
                    st.rerun()
    else:
        st.sidebar.info("暂无配置的指标")

    st.sidebar.markdown("---")

    # 检查是否在编辑模式
    editing_index = st.session_state.get('editing_indicator', None)

    if editing_index is not None and editing_index < len(st.session_state.configured_indicators):
        st.sidebar.markdown("### ✏️ 编辑指标")
        editing_config = st.session_state.configured_indicators[editing_index]
        selected_indicator = editing_config['code']
        default_params = editing_config['params']
    else:
        st.sidebar.markdown("### ➕ 添加新指标")
        # 指标选择
        selected_indicator = st.sidebar.selectbox(
            "选择技术指标",
            options=list(available_indicators.keys()),
            format_func=lambda x: available_indicators[x],
            key="new_indicator_select",
            help="选择要计算的技术指标"
        )
        default_params = None

    # 参数配置区域
    if selected_indicator:
        params = indicator_calc.get_indicator_params(selected_indicator)
        config_params = {}

        with st.sidebar.expander(f"{available_indicators[selected_indicator]} 参数设置", expanded=True):
            for param_name, param_options in params.items():
                if default_params and param_name in default_params:
                    default_index = param_options.index(default_params[param_name]) if default_params[param_name] in param_options else len(param_options) // 2
                else:
                    default_index = len(param_options) // 2 if param_options else 0

                param_value = st.selectbox(
                    f"{param_name}",
                    options=param_options,
                    index=default_index,
                    key=f"param_{selected_indicator}_{param_name}_{editing_index}"
                )
                config_params[param_name] = param_value

        # 生成指标显示名称
        display_name = indicator_calc.generate_indicator_display_name(selected_indicator, config_params)

        # 显示预览
        st.sidebar.info(f"📊 预览: {display_name}")

        # 按钮区域
        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.sidebar.button("💾 保存指标", type="primary", key="save_indicator"):
                new_config = {
                    'code': selected_indicator,
                    'params': config_params,
                    'display_name': display_name
                }

                if editing_index is not None:
                    # 更新现有配置
                    st.session_state.configured_indicators[editing_index] = new_config
                    st.session_state.editing_indicator = None
                    st.sidebar.success("✅ 指标已更新")
                else:
                    # 添加新配置
                    st.session_state.configured_indicators.append(new_config)
                    st.sidebar.success("✅ 指标已添加")

                st.rerun()

        with col2:
            if editing_index is not None:
                if st.sidebar.button("❌ 取消", key="cancel_edit"):
                    st.session_state.editing_indicator = None
                    st.rerun()

    st.sidebar.markdown("---")

    # 计算指标按钮
    if st.sidebar.button("🧮 计算所有指标", type="primary") and st.session_state.configured_indicators:
        try:
            with st.spinner("正在计算技术指标..."):
                # 准备指标配置列表
                indicator_configs = []
                for config in st.session_state.configured_indicators:
                    indicator_configs.append({
                        'code': config['code'],
                        'params': config['params']
                    })

                # 计算指标
                indicators_data = indicator_calc.calculate_multiple_indicators(
                    st.session_state.data, indicator_configs
                )

                # 保存到会话状态
                st.session_state.indicators_data = indicators_data
                st.session_state.last_indicator_configs = st.session_state.configured_indicators.copy()

                st.sidebar.success(f"✅ 已计算 {len(indicator_configs)} 个指标")
                st.rerun()

        except Exception as e:
            st.sidebar.error(f"❌ 指标计算失败: {str(e)}")

    # 显示上次的计算结果信息
    if 'last_indicator_configs' in st.session_state and st.session_state.indicators_data is not None:
        last_count = len(st.session_state.last_indicator_configs)
        st.sidebar.caption(f"💡 上次计算了 {last_count} 个指标")
        if st.sidebar.button("🔄 重新计算上次指标"):
            indicator_configs = []
            for config in st.session_state.last_indicator_configs:
                indicator_configs.append({
                    'code': config['code'],
                    'params': config['params']
                })

            try:
                with st.spinner("正在重新计算..."):
                    indicators_data = indicator_calc.calculate_multiple_indicators(
                        st.session_state.data, indicator_configs
                    )
                    st.session_state.indicators_data = indicators_data
                    st.sidebar.success("✅ 重新计算完成")
                    st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ 重新计算失败: {str(e)}")


def sidebar_condition_config():
    """侧边栏条件配置区域"""
    st.sidebar.markdown("## 🎯 条件设置")

    if st.session_state.indicators_data is None:
        st.sidebar.info("请先计算技术指标")
        return

    # 获取可用列名
    available_columns = list(st.session_state.indicators_data.columns)

    # 条件类型选择
    condition_type = st.sidebar.selectbox(
        "条件类型",
        ["数值比较", "交叉信号", "条件组合"],
        help="选择条件类型"
    )

    condition_builder = ConditionBuilder()

    if condition_type == "数值比较":
        # 数值比较条件
        col1, col2, col3 = st.sidebar.columns(3)

        with col1:
            column = st.selectbox("指标列", available_columns)

        with col2:
            operator = st.selectbox("操作符", [">", ">=", "<", "<=", "==", "!="])

        with col3:
            value = st.number_input("比较值", value=0.0, step=0.1)

        if st.sidebar.button("➕ 添加条件", type="primary"):
            try:
                condition = condition_builder.create_numeric_condition(column, operator, value)
                st.session_state.condition = condition
                st.sidebar.success(f"✅ 条件已添加: {condition.description}")
            except Exception as e:
                st.sidebar.error(f"❌ 条件添加失败: {str(e)}")

    elif condition_type == "交叉信号":
        # 交叉信号条件
        col1, col2 = st.sidebar.columns(2)

        with col1:
            fast_col = st.selectbox("快速线", available_columns)

        with col2:
            slow_col = st.selectbox("慢速线", available_columns)

        cross_type = st.sidebar.selectbox("交叉类型", ["golden", "death"],
                                       format_func=lambda x: {"golden": "金叉", "death": "死叉"}[x])

        if st.sidebar.button("➕ 添加交叉条件", type="primary"):
            try:
                condition = condition_builder.create_cross_condition(fast_col, slow_col, cross_type)
                st.session_state.condition = condition
                st.sidebar.success(f"✅ 条件已添加: {condition.description}")
            except Exception as e:
                st.sidebar.error(f"❌ 条件添加失败: {str(e)}")


def sidebar_backtest_config():
    """侧边栏回测配置区域"""
    st.sidebar.markdown("## 📊 回测设置")

    if st.session_state.condition is None:
        st.sidebar.info("请先设置触发条件")
        return

    # 持有期设置
    holding_period = st.sidebar.slider(
        "持有天数",
        min_value=1,
        max_value=60,
        value=5,
        help="信号触发后持有股票的天数"
    )

    # 运行回测按钮
    if st.sidebar.button("🚀 运行回测", type="primary"):
        try:
            with st.spinner("正在运行回测分析..."):
                # 初始化回测分析器
                backtest_analyzer = BacktestAnalyzer()

                # 运行回测
                result = backtest_analyzer.run_backtest(
                    st.session_state.indicators_data,
                    st.session_state.condition,
                    holding_period=holding_period
                )

                # 保存结果
                st.session_state.backtest_results = result

                st.sidebar.success("✅ 回测完成")
                st.rerun()

        except Exception as e:
            st.sidebar.error(f"❌ 回测失败: {str(e)}")


def main_data_display():
    """主要数据展示区域"""
    st.markdown("## 📈 股票数据")

    if st.session_state.data is None:
        st.info("请在左侧侧边栏获取股票数据")
        return

    # 显示数据概览
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("数据条数", len(st.session_state.data))

    with col2:
        if 'close' in st.session_state.data.columns:
            latest_price = st.session_state.data['close'].iloc[-1]
            st.metric("最新价格", f"{latest_price:.2f}")

    with col3:
        if 'volume' in st.session_state.data.columns:
            latest_volume = st.session_state.data['volume'].iloc[-1]
            st.metric("最新成交量", f"{latest_volume:,.0f}")

    with col4:
        date_range = f"{st.session_state.data.index[0].date()} 至 {st.session_state.data.index[-1].date()}"
        st.metric("数据时间范围", date_range)

    # 显示数据表格
    with st.expander("查看原始数据", expanded=False):
        st.dataframe(
            st.session_state.data.tail(100),
            use_container_width=True,
            height=400
        )


def indicators_display():
    """技术指标展示区域"""
    st.markdown("## 📊 技术指标")

    if st.session_state.indicators_data is None:
        st.info("请在左侧配置并计算技术指标")
        return

    # 指标数据概览
    col1, col2 = st.columns(2)

    with col1:
        st.metric("指标数量", len(st.session_state.indicators_data.columns))

    with col2:
        non_null_count = st.session_state.indicators_data.count().sum()
        total_count = len(st.session_state.indicators_data) * len(st.session_state.indicators_data.columns)
        completeness = (non_null_count / total_count) * 100
        st.metric("数据完整性", f"{completeness:.1f}%")

    # 显示指标数据表格
    with st.expander("查看指标数据", expanded=False):
        st.dataframe(
            st.session_state.indicators_data.tail(100),
            use_container_width=True,
            height=400
        )


def price_chart():
    """价格走势图表"""
    st.markdown("## 📈 价格走势图")

    if st.session_state.data is None:
        st.info("请先获取股票数据")
        return

    if st.session_state.indicators_data is not None:
        # 获取技术指标分类
        indicator_types = {
            '趋势指标': [col for col in st.session_state.indicators_data.columns
                       if any(x in col for x in ['MA', 'EMA', 'MACD', 'BOLL'])],
            '摆荡指标': [col for col in st.session_state.indicators_data.columns
                       if any(x in col for x in ['RSI', 'KDJ', 'CCI', 'WILLR'])],
            '成交量指标': [col for col in st.session_state.indicators_data.columns
                         if any(x in col for x in ['OBV', 'VOLUME'])],
            '波动率指标': [col for col in st.session_state.indicators_data.columns
                         if any(x in col for x in ['ATR'])]
        }

        # 计算需要的子图数量
        subplot_count = 2  # K线图 + 成交量
        for indicators in indicator_types.values():
            if indicators:
                subplot_count += 1

        # 设置高度比例：主图占40%，每个副图各占15%
        # 成交量作为特殊副图，占10%
        row_heights = [0.4]  # 主图K线图
        if 'volume' in st.session_state.data.columns:
            row_heights.append(0.1)  # 成交量
        else:
            row_heights.append(0.15)  # 如果没有成交量，给第一个副图更多空间

        # 其他技术指标副图，每个占15%
        indicator_subplot_count = subplot_count - len(row_heights)
        row_heights.extend([0.15] * indicator_subplot_count)

        # 创建子图标题
        subplot_titles = ['K线图', '成交量']
        for type_name, indicators in indicator_types.items():
            if indicators:
                subplot_titles.append(type_name)
    else:
        subplot_count = 2
        row_heights = [0.4, 0.1] if 'volume' in st.session_state.data.columns else [0.5, 0.5]
        subplot_titles = ['K线图', '成交量']

    # 创建K线图
    fig = make_subplots(
        rows=subplot_count, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=subplot_titles,
        row_heights=row_heights
    )

    # K线图（只显示K线，不叠加指标）
    fig.add_trace(
        go.Candlestick(
            x=st.session_state.data.index,
            open=st.session_state.data['open'],
            high=st.session_state.data['high'],
            low=st.session_state.data['low'],
            close=st.session_state.data['close'],
            name='K线',
            increasing=dict(line=dict(color='#ef4444'), fillcolor='#ef4444'),
            decreasing=dict(line=dict(color='#22c55e'), fillcolor='#22c55e')
        ),
        row=1, col=1
    )

    # 成交量
    if 'volume' in st.session_state.data.columns:
        # 根据涨跌设置颜色
        colors = []
        for i in range(len(st.session_state.data)):
            if i == 0:
                colors.append('rgba(0,0,255,0.3)')
            else:
                if st.session_state.data['close'].iloc[i] >= st.session_state.data['close'].iloc[i-1]:
                    colors.append('rgba(239,68,68,0.5)')  # 涨：红色
                else:
                    colors.append('rgba(34,197,94,0.5)')  # 跌：绿色

        fig.add_trace(
            go.Bar(
                x=st.session_state.data.index,
                y=st.session_state.data['volume'],
                name='成交量',
                marker_color=colors
            ),
            row=2, col=1
        )

    # 技术指标显示在副图中
    if st.session_state.indicators_data is not None:
        current_row = 3

        # 趋势指标
        if indicator_types['趋势指标']:
            colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']
            for i, col in enumerate(indicator_types['趋势指标'][:5]):  # 最多显示5个
                fig.add_trace(
                    go.Scatter(
                        x=st.session_state.indicators_data.index,
                        y=st.session_state.indicators_data[col],
                        name=col,
                        line=dict(width=1.5, color=colors[i % len(colors)])
                    ),
                    row=current_row, col=1
                )
            current_row += 1

        # 摆荡指标
        if indicator_types['摆荡指标']:
            colors = ['#8b5cf6', '#ec4899', '#f59e0b', '#14b8a6']
            for i, col in enumerate(indicator_types['摆荡指标'][:4]):  # 最多显示4个
                fig.add_trace(
                    go.Scatter(
                        x=st.session_state.indicators_data.index,
                        y=st.session_state.indicators_data[col],
                        name=col,
                        line=dict(width=1.5, color=colors[i % len(colors)])
                    ),
                    row=current_row, col=1
                )

            # 为RSI和KDJ添加参考线
            for col in indicator_types['摆荡指标']:
                if 'RSI' in col:
                    fig.add_hline(y=70, line_dash="dash", line_color="red",
                                 opacity=0.5, row=current_row-1, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green",
                                 opacity=0.5, row=current_row-1, col=1)
                    break
            current_row += 1

        # 成交量指标
        if indicator_types['成交量指标']:
            colors = ['#059669', '#7c3aed', '#dc2626']
            for i, col in enumerate(indicator_types['成交量指标'][:3]):  # 最多显示3个
                fig.add_trace(
                    go.Scatter(
                        x=st.session_state.indicators_data.index,
                        y=st.session_state.indicators_data[col],
                        name=col,
                        line=dict(width=1.5, color=colors[i % len(colors)])
                    ),
                    row=current_row, col=1
                )
            current_row += 1

        # 波动率指标
        if indicator_types['波动率指标']:
            for col in indicator_types['波动率指标']:
                fig.add_trace(
                    go.Scatter(
                        x=st.session_state.indicators_data.index,
                        y=st.session_state.indicators_data[col],
                        name=col,
                        line=dict(width=2, color='#dc2626')
                    ),
                    row=current_row, col=1
                )

    # 更新布局
    fig.update_layout(
        title='股票价格走势与技术指标分析',
        xaxis_rangeslider_visible=False,
        height=1000,  # 固定高度，让row_heights控制各子图高度
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)  # 调整边距
    )

    # 更新坐标轴 - 设置自适应高度
    for i in range(1, subplot_count + 1):
        # Y轴自适应数据范围
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            autorange=True,  # 自动调整Y轴范围
            row=i, col=1
        )

        # X轴设置
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            row=i, col=1
        )

    # 只在最后一个子图显示X轴标签
    fig.update_xaxes(showticklabels=True, row=subplot_count, col=1)
    for i in range(1, subplot_count):
        fig.update_xaxes(showticklabels=False, row=i, col=1)

    fig.update_xaxes(showspikes=True, spikethickness=1, spikedash="solid")

    st.plotly_chart(fig, use_container_width=True)


def backtest_results_display():
    """回测结果展示区域"""
    st.markdown("## 📊 回测分析结果")

    if st.session_state.backtest_results is None:
        st.info("请先设置条件并运行回测")
        return

    result = st.session_state.backtest_results

    # 关键指标展示
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("总信号数", result.total_signals)

    with col2:
        st.metric("胜率", f"{result.win_rate:.2%}")

    with col3:
        st.metric("平均收益", f"{result.avg_return:.2%}")

    with col4:
        st.metric("最大收益", f"{result.max_return:.2%}")

    # 详细统计信息
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 收益统计")
        st.write(f"- **最小收益**: {result.min_return:.2%}")
        st.write(f"- **收益标准差**: {result.std_return:.2%}")
        st.write(f"- **盈利信号数**: {result.profitable_signals}")
        st.write(f"- **亏损信号数**: {result.losing_signals}")
        st.write(f"- **平均持有期**: {result.avg_holding_period:.1f} 天")

    with col2:
        st.markdown("### ⚙️ 回测参数")
        for key, value in result.parameters.items():
            st.write(f"- **{key}**: {value}")

    # 信号列表
    if result.signals:
        st.markdown("### 📋 信号详情")

        signals_data = []
        for signal in result.signals:
            signals_data.append({
                '时间': signal.timestamp.strftime('%Y-%m-%d'),
                '信号价格': f"{signal.signal_price:.2f}",
                '信号类型': signal.signal_type
            })

        signals_df = pd.DataFrame(signals_data)
        st.dataframe(signals_df, use_container_width=True)

    # 收益分布图
    if result.returns:
        st.markdown("### 📊 收益分布")

        # 创建收益分布直方图
        fig = go.Figure()

        fig.add_trace(
            go.Histogram(
                x=[r * 100 for r in result.returns],  # 转换为百分比
                nbinsx=20,
                name='收益分布',
                marker_color='lightblue',
                opacity=0.7
            )
        )

        # 添加平均收益线
        fig.add_vline(
            x=result.avg_return * 100,
            line_dash="dash",
            line_color="red",
            annotation_text=f"平均收益: {result.avg_return:.2%}"
        )

        fig.update_layout(
            title='信号收益分布直方图',
            xaxis_title='收益率 (%)',
            yaxis_title='频次',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # 生成分析报告
    st.markdown("### 📄 分析报告")
    analyzer = BacktestAnalyzer()
    report = analyzer.generate_report(result)
    st.markdown(report)


def main():
    """主函数"""
    # 初始化会话状态
    init_session_state()

    # 页面标题
    st.title("📈 股票技术指标回测分析平台")
    st.markdown("---")

    # 创建侧边栏
    sidebar_data_input()
    st.sidebar.markdown("---")
    sidebar_indicators_config()
    st.sidebar.markdown("---")
    sidebar_condition_config()
    st.sidebar.markdown("---")
    sidebar_backtest_config()

    # 主要内容区域
    main_data_display()
    st.markdown("---")
    indicators_display()
    st.markdown("---")
    price_chart()
    st.markdown("---")
    backtest_results_display()

    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "© 2024 股票技术指标回测分析平台 | 仅供学习研究使用"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()