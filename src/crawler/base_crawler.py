"""
基础爬虫类
提供通用的爬虫功能和接口
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import time
import random
from abc import ABC, abstractmethod
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    """基础爬虫抽象类"""
    
    def __init__(self, use_selenium=False, headless=True):
        self.use_selenium = use_selenium
        self.headless = headless
        self.ua = UserAgent()
        self.session = requests.Session()
        self.driver = None
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        if self.use_selenium:
            self._setup_selenium()
    
    def _setup_selenium(self):
        """设置Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'--user-agent={self.ua.random}')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            logger.error(f"Selenium WebDriver setup failed: {e}")
            raise
    
    def get_page(self, url: str, **kwargs) -> str:
        """获取页面内容"""
        if self.use_selenium:
            return self._get_page_selenium(url, **kwargs)
        else:
            return self._get_page_requests(url, **kwargs)
    
    def _get_page_requests(self, url: str, **kwargs) -> str:
        """使用requests获取页面"""
        try:
            response = self.session.get(url, timeout=10, **kwargs)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            logger.error(f"Failed to get page {url}: {e}")
            return ""
    
    def _get_page_selenium(self, url: str, wait_time=10, **kwargs) -> str:
        """使用Selenium获取页面"""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Failed to get page {url} with Selenium: {e}")
            return ""
    
    def parse_page(self, html: str) -> BeautifulSoup:
        """解析页面HTML"""
        return BeautifulSoup(html, 'html.parser')
    
    def extract_text(self, element, default="") -> str:
        """安全提取元素文本"""
        if element:
            return element.get_text(strip=True)
        return default
    
    def extract_attribute(self, element, attr: str, default="") -> str:
        """安全提取元素属性"""
        if element:
            return element.get(attr, default)
        return default
    
    def random_delay(self, min_delay=1, max_delay=3):
        """随机延迟"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def save_data(self, data: List[Dict], filename: str):
        """保存数据到JSON文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"data/raw/{filename}_{timestamp}.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
    
    @abstractmethod
    def crawl_jobs(self, keywords: List[str], pages: int = 1) -> List[Dict]:
        """抽象方法：爬取职位信息"""
        pass
    
    @abstractmethod
    def parse_job_detail(self, url: str) -> Dict:
        """抽象方法：解析职位详情"""
        pass
    
    def close(self):
        """关闭资源"""
        if self.driver:
            self.driver.quit()
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class Web3JobFilter:
    """Web3相关职位过滤器"""
    
    WEB3_KEYWORDS = [
        'web3', 'blockchain', '区块链', '比特币', 'bitcoin', 'ethereum', '以太坊',
        'defi', 'nft', 'dao', '智能合约', 'smart contract', 'dapp', 'cryptocurrency',
        '加密货币', 'solidity', 'rust', 'move', 'cosmos', 'polkadot', 'polygon',
        'binance', 'metamask', 'uniswap', 'opensea', 'compound', 'aave'
    ]
    
    @classmethod
    def is_web3_related(cls, text: str) -> bool:
        """判断文本是否与Web3相关"""
        if not text:
            return False
        
        text_lower = text.lower()
        for keyword in cls.WEB3_KEYWORDS:
            if keyword.lower() in text_lower:
                return True
        return False
    
    @classmethod
    def extract_web3_skills(cls, text: str) -> List[str]:
        """提取Web3相关技能"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = []
        
        for keyword in cls.WEB3_KEYWORDS:
            if keyword.lower() in text_lower:
                found_skills.append(keyword)
        
        return list(set(found_skills))  # 去重 