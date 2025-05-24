"""
项目配置文件
"""

import os
from dotenv import load_dotenv

load_dotenv()

# 数据库配置
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'username': os.getenv('DB_USERNAME', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'web3_jobs'),
}

# Llama模型配置
MODEL_CONFIG = {
    'model_path': os.getenv('MODEL_PATH', 'meta-llama/Meta-Llama-3.1-8B-Instruct'),
    'device': 'cuda' if os.getenv('USE_GPU', 'true').lower() == 'true' else 'cpu',
    'batch_size': int(os.getenv('BATCH_SIZE', 10)),
}

# 爬虫配置
CRAWLER_CONFIG = {
    'delay_min': float(os.getenv('CRAWLER_DELAY_MIN', 1)),
    'delay_max': float(os.getenv('CRAWLER_DELAY_MAX', 3)),
    'pages_per_keyword': int(os.getenv('CRAWLER_PAGES_PER_KEYWORD', 3)),
    'headless': os.getenv('CRAWLER_HEADLESS', 'true').lower() == 'true',
}

# Web3关键词
WEB3_KEYWORDS = [
    'web3', '区块链', 'blockchain', 'DeFi', 'NFT', 'DAO',
    '智能合约', 'smart contract', 'solidity', 'ethereum',
    '以太坊', '比特币', 'bitcoin', 'crypto', '加密货币',
    'dapp', 'metamask', 'uniswap', 'opensea'
]

# 日志配置
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'file': os.getenv('LOG_FILE', 'app.log'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
} 