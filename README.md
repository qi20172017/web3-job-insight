# Web3 Job Insight - Web3领域招聘岗位分析

## 项目简介

本项目旨在通过数据科学的方法分析Web3领域的招聘趋势，为求职者和招聘方提供有价值的洞察。

## 项目目标

1. **数据采集**: 从各大招聘网站爬取Web3相关职位信息
2. **数据清洗**: 使用Meta-Llama-3.1-8B-Instruct模型提取关键信息
3. **数据分析**: 通过机器学习和统计分析发现行业趋势和价值

## 项目结构

```
web3-job-insight/
├── src/                    # 源代码
│   ├── crawler/           # 数据爬取模块
│   ├── db/                # 数据库操作模块
│   ├── nlp/               # NLP处理模块
│   └── analysis/          # 数据分析模块
├── data/                  # 数据存储
│   ├── raw/              # 原始数据
│   └── processed/        # 处理后数据
├── notebooks/            # Jupyter notebooks
├── reports/              # 分析报告
├── requirements.txt      # 依赖包
└── README.md            # 项目说明
```

## 安装和设置

### 1. 克隆项目
```bash
git clone <repository-url>
cd web3-job-insight
```

### 2. 创建虚拟环境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置数据库
- 安装MySQL数据库
- 创建数据库和表结构
- 配置数据库连接参数

### 5. 配置环境变量
创建 `.env` 文件并配置必要的环境变量。

## 使用方法

### 数据采集
```bash
python src/crawler/main.py
```

### 数据处理
```bash
python src/nlp/process_data.py
```

### 数据分析
```bash
jupyter notebook notebooks/
```

## 功能特性

- 🕷️ **智能爬虫**: 支持多个招聘网站的数据采集
- 🧠 **AI处理**: 使用大语言模型进行信息提取
- 📊 **数据分析**: 多维度的数据分析和可视化
- 📈 **趋势预测**: 基于机器学习的趋势分析

## 贡献指南

欢迎提交问题和拉取请求！

## 许可证

MIT License
