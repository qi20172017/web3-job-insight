# Web3 Job Insight 使用说明

## 项目概述

Web3 Job Insight 是一个专门分析Web3领域招聘岗位的数据科学项目。项目分为三个主要阶段：

1. **数据采集**：从招聘网站爬取Web3相关职位信息
2. **数据清洗**：使用Meta-Llama-3.1-8B-Instruct模型提取结构化信息
3. **数据分析**：生成多维度的数据分析报告和可视化图表

## 环境准备

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 数据库配置

安装MySQL数据库，并创建数据库：

```sql
CREATE DATABASE web3_jobs CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 环境变量配置

创建 `.env` 文件（参考 `config.py` 中的配置项）：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=your_password
DB_NAME=web3_jobs

# 模型配置
MODEL_PATH=meta-llama/Meta-Llama-3.1-8B-Instruct
USE_GPU=true
BATCH_SIZE=10

# 爬虫配置
CRAWLER_DELAY_MIN=1
CRAWLER_DELAY_MAX=3
CRAWLER_PAGES_PER_KEYWORD=3
CRAWLER_HEADLESS=true

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### 4. Chrome浏览器

安装Chrome浏览器和ChromeDriver（用于Selenium爬虫）。

## 使用方法

### 方式一：使用主程序（推荐）

#### 运行完整流水线
```bash
python main.py pipeline --pages 5 --batch-size 10 --show-stats
```

#### 单独运行各模块

**1. 数据爬取**
```bash
python main.py crawl --pages 3
```

**2. NLP数据处理**
```bash
python main.py process --batch-size 10
```

**3. 数据分析**
```bash
python main.py analyze --show-stats
```

### 方式二：直接运行模块

#### 1. 数据爬取
```bash
python src/crawler/main.py
```

#### 2. NLP处理
```bash
# 处理所有未处理的职位
python src/nlp/process_data.py

# 处理指定职位
python src/nlp/process_data.py --job-id 123

# 重新处理所有职位
python src/nlp/process_data.py --reprocess

# 显示处理统计
python src/nlp/process_data.py --stats
```

#### 3. 数据分析
```bash
python -c "
from src.analysis.job_analyzer import JobAnalyzer
with JobAnalyzer() as analyzer:
    analyzer.generate_comprehensive_report()
"
```

### 方式三：使用Jupyter Notebook

```bash
jupyter notebook notebooks/data_exploration.ipynb
```

## 输出结果

### 1. 数据库表

- `job_postings`: 原始职位数据
- `processed_job_data`: AI处理后的结构化数据
- `company_info`: 公司信息

### 2. 分析报告

- `reports/comprehensive_report.json`: 综合分析报告（JSON格式）
- `reports/salary_analysis.png`: 薪资分析图表
- `reports/category_analysis.png`: 职位类别分析图表
- `reports/location_analysis.png`: 地区分布分析图表
- `reports/company_analysis.png`: 公司洞察分析图表

### 3. 日志文件

- `crawler.log`: 爬虫运行日志
- `nlp_processing.log`: NLP处理日志
- `app.log`: 主程序日志

## 项目结构说明

```
web3-job-insight/
├── src/                    # 源代码
│   ├── crawler/           # 数据爬取模块
│   │   ├── base_crawler.py    # 基础爬虫类
│   │   ├── boss_crawler.py    # Boss直聘爬虫
│   │   └── main.py           # 爬虫主程序
│   ├── db/                # 数据库操作模块
│   │   ├── models.py         # 数据库模型
│   │   └── data_manager.py   # 数据管理器
│   ├── nlp/               # NLP处理模块
│   │   ├── llama_processor.py # Llama模型处理器
│   │   └── process_data.py   # 数据处理主程序
│   └── analysis/          # 数据分析模块
│       └── job_analyzer.py   # 职位数据分析器
├── notebooks/            # Jupyter notebooks
├── reports/              # 分析报告输出目录
├── data/                 # 数据存储目录
│   ├── raw/              # 原始数据
│   └── processed/        # 处理后数据
├── main.py              # 主入口程序
├── config.py            # 配置文件
├── requirements.txt     # 依赖包列表
└── README.md           # 项目说明
```

## 扩展功能

### 添加新的招聘网站爬虫

1. 继承 `BaseCrawler` 类
2. 实现 `crawl_jobs` 和 `parse_job_detail` 方法
3. 在 `CrawlerManager` 中添加新爬虫

### 自定义分析维度

1. 修改 `JobAnalyzer` 类，添加新的分析方法
2. 在 `generate_comprehensive_report` 中调用新方法

### 使用本地Llama模型

1. 下载Llama模型到本地
2. 修改 `MODEL_PATH` 环境变量为本地路径

## 注意事项

1. **爬虫使用**：请遵守网站的robots.txt和使用条款，合理控制爬取频率
2. **模型资源**：Llama模型需要较大的GPU内存，建议使用GPU加速
3. **数据隐私**：处理招聘数据时请注意隐私保护
4. **网络环境**：首次运行可能需要下载模型，请确保网络连接稳定

## 故障排除

### 常见问题

1. **ChromeDriver错误**：确保Chrome浏览器和ChromeDriver版本匹配
2. **数据库连接失败**：检查数据库配置和连接参数
3. **模型加载失败**：检查GPU内存和网络连接
4. **爬虫被阻止**：调整爬取频率和请求头

### 获取帮助

```bash
python main.py --help
python main.py crawl --help
python main.py process --help
python main.py analyze --help
``` 