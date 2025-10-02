#!/usr/bin/env python3
"""
股票技术指标回测分析平台 - 快速启动脚本

这个脚本提供了多种启动方式，方便用户快速体验项目。
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误：需要Python 3.8或更高版本")
        print(f"当前版本：Python {sys.version}")
        return False
    return True


def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import pandas
        import numpy
        import akshare
        import talib
        import plotly
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖：{e}")
        print("请运行：pip install -r requirements.txt")
        return False


def start_streamlit():
    """启动Streamlit应用"""
    print("🚀 启动股票技术指标回测分析平台...")
    print("正在启动Streamlit服务器...")

    try:
        subprocess.run([
            "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true",
            "--server.fileWatcherType=none"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败：{e}")


def run_basic_example():
    """运行基础示例"""
    print("📊 运行基础使用示例...")

    try:
        subprocess.run([sys.executable, "examples/basic_usage.py"])
    except Exception as e:
        print(f"❌ 运行示例失败：{e}")


def install_dependencies():
    """安装依赖"""
    print("📦 安装项目依赖...")

    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ 依赖安装完成")
    except Exception as e:
        print(f"❌ 安装失败：{e}")


def show_info():
    """显示项目信息"""
    print("📈 股票技术指标回测分析平台")
    print("=" * 50)
    print("📋 项目信息：")
    print("   许可证：GPL v3")
    print("   版本：1.0.0")
    print("   GitHub：https://github.com/yourusername/stock-technical-indicators-platform")
    print()
    print("🚀 启动选项：")
    print("   1. 启动Web界面 (streamlit)")
    print("   2. 运行基础示例")
    print("   3. 安装依赖")
    print("   4. 显示帮助")
    print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="股票技术指标回测分析平台启动器")
    parser.add_argument("--mode", choices=["streamlit", "example", "install", "info"],
                      default="streamlit", help="启动模式")
    parser.add_argument("--check", action="store_true", help="检查环境和依赖")

    args = parser.parse_args()

    if args.check:
        print("🔍 检查环境和依赖...")
        if not check_python_version():
            return
        if not check_dependencies():
            return
        print("✅ 环境检查通过")
        return

    if args.mode == "streamlit":
        if not check_python_version():
            return
        if not check_dependencies():
            return
        start_streamlit()

    elif args.mode == "example":
        if not check_python_version():
            return
        run_basic_example()

    elif args.mode == "install":
        install_dependencies()

    elif args.mode == "info":
        show_info()


if __name__ == "__main__":
    main()