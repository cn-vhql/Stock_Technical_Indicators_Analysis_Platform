"""
股票技术指标回测分析平台 - 安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# 版本信息
VERSION = "1.0.0"

setup(
    name="stock-technical-indicators-platform",
    version=VERSION,
    author="Stock Analysis Platform Team",
    author_email="contact@example.com",
    description="一个功能强大的股票技术指标回测分析平台",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stock-technical-indicators-platform",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/stock-technical-indicators-platform/issues",
        "Documentation": "https://github.com/yourusername/stock-technical-indicators-platform/wiki",
        "Source Code": "https://github.com/yourusername/stock-technical-indicators-platform",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Framework :: Streamlit",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "isort>=5.10.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stock-analysis=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "LICENSE"],
    },
    zip_safe=False,
    keywords=[
        "stock",
        "technical-analysis",
        "backtesting",
        "financial",
        "trading",
        "indicators",
        "streamlit",
        "quantitative",
        "investment",
    ],
)