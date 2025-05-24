"""
爬虫主程序
协调各个爬虫的运行，并将数据保存到数据库
"""

import logging
import sys
import os
from datetime import datetime
from typing import List, Dict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.crawler.boss_crawler import BossCrawler
from src.db.models import create_session, JobPosting, CompanyInfo, init_database
from src.db.data_manager import JobDataManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CrawlerManager:
    """爬虫管理器"""
    
    def __init__(self):
        self.data_manager = JobDataManager()
        
        # Web3相关搜索关键词
        self.web3_keywords = [
            'web3', '区块链', 'blockchain', 'DeFi', 'NFT', 'DAO',
            '智能合约', 'smart contract', 'solidity', 'ethereum',
            '以太坊', '比特币', 'bitcoin', 'crypto', '加密货币'
        ]
    
    def run_all_crawlers(self, pages_per_keyword: int = 3):
        """运行所有爬虫"""
        logger.info("开始运行Web3招聘数据爬虫")
        
        # 初始化数据库
        try:
            init_database()
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            return
        
        total_jobs = 0
        
        # 运行Boss直聘爬虫
        try:
            boss_jobs = self._run_boss_crawler(pages_per_keyword)
            total_jobs += len(boss_jobs)
            logger.info(f"Boss直聘爬取完成，获得 {len(boss_jobs)} 个职位")
        except Exception as e:
            logger.error(f"Boss直聘爬虫运行失败: {e}")
        
        # TODO: 添加其他招聘网站爬虫
        # 例如：拉勾网、猎聘网等
        
        logger.info(f"所有爬虫运行完成，总共获得 {total_jobs} 个Web3相关职位")
    
    def _run_boss_crawler(self, pages: int) -> List[Dict]:
        """运行Boss直聘爬虫"""
        logger.info("开始运行Boss直聘爬虫")
        
        with BossCrawler() as crawler:
            jobs = crawler.crawl_jobs(self.web3_keywords, pages)
            
            # 获取职位详细信息
            detailed_jobs = []
            for i, job in enumerate(jobs):
                logger.info(f"获取职位详情 {i+1}/{len(jobs)}: {job.get('title', '')}")
                
                if job.get('source_url'):
                    detail = crawler.parse_job_detail(job['source_url'])
                    job.update(detail)
                
                detailed_jobs.append(job)
                
                # 保存到数据库
                try:
                    self.data_manager.save_job(job)
                except Exception as e:
                    logger.error(f"保存职位失败: {e}")
                
                # 控制请求频率
                crawler.random_delay(1, 3)
            
            return detailed_jobs
    
    def get_crawl_statistics(self):
        """获取爬取统计信息"""
        stats = self.data_manager.get_statistics()
        
        logger.info("=== 爬取统计信息 ===")
        logger.info(f"总职位数: {stats.get('total_jobs', 0)}")
        logger.info(f"Web3相关职位: {stats.get('web3_jobs', 0)}")
        logger.info(f"今日新增: {stats.get('today_jobs', 0)}")
        logger.info(f"待处理职位: {stats.get('unprocessed_jobs', 0)}")
        
        return stats

def main():
    """主函数"""
    manager = CrawlerManager()
    
    try:
        # 运行爬虫
        manager.run_all_crawlers(pages_per_keyword=2)
        
        # 显示统计信息
        manager.get_crawl_statistics()
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        raise

if __name__ == "__main__":
    main() 