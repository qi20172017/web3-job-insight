#!/usr/bin/env python3
"""
Web3 Job Insight 主程序
Web3领域招聘岗位分析项目的主入口
"""

import argparse
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(__file__))

from src.crawler.main import CrawlerManager
from src.nlp.process_data import DataProcessor
from src.analysis.job_analyzer import JobAnalyzer
from config import LOGGING_CONFIG

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_crawler(args):
    """运行数据爬取"""
    logger.info("开始运行数据爬取模块")
    
    manager = CrawlerManager()
    try:
        manager.run_all_crawlers(pages_per_keyword=args.pages)
        manager.get_crawl_statistics()
    except Exception as e:
        logger.error(f"爬取失败: {e}")
        raise

def run_nlp_processing(args):
    """运行NLP数据处理"""
    logger.info("开始运行NLP数据处理模块")
    
    processor = DataProcessor(args.model_path)
    try:
        if args.job_id:
            processor.process_single_job(args.job_id)
        elif args.reprocess:
            processor.reprocess_jobs()
        else:
            processor.process_unprocessed_jobs(args.batch_size)
    except Exception as e:
        logger.error(f"NLP处理失败: {e}")
        raise
    finally:
        processor.cleanup()

def run_analysis(args):
    """运行数据分析"""
    logger.info("开始运行数据分析模块")
    
    with JobAnalyzer() as analyzer:
        try:
            # 生成综合分析报告
            report = analyzer.generate_comprehensive_report()
            logger.info("数据分析完成，报告已生成")
            
            if args.show_stats:
                # 显示统计信息
                print("\n=== 分析结果概览 ===")
                for section, data in report.items():
                    if section != 'generated_at':
                        print(f"\n{section}:")
                        if isinstance(data, dict):
                            for key, value in data.items():
                                print(f"  {key}: {value}")
                        
        except Exception as e:
            logger.error(f"数据分析失败: {e}")
            raise

def run_full_pipeline(args):
    """运行完整的数据处理流水线"""
    logger.info("开始运行完整的数据处理流水线")
    
    try:
        # 1. 数据爬取
        logger.info("步骤 1/3: 数据爬取")
        run_crawler(args)
        
        # 2. NLP处理
        logger.info("步骤 2/3: NLP数据处理")
        run_nlp_processing(args)
        
        # 3. 数据分析
        logger.info("步骤 3/3: 数据分析")
        run_analysis(args)
        
        logger.info("完整流水线执行完成！")
        
    except Exception as e:
        logger.error(f"流水线执行失败: {e}")
        raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Web3招聘岗位分析工具')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 爬虫命令
    crawler_parser = subparsers.add_parser('crawl', help='运行数据爬取')
    crawler_parser.add_argument('--pages', type=int, default=3, help='每个关键词爬取的页数')
    
    # NLP处理命令
    nlp_parser = subparsers.add_parser('process', help='运行NLP数据处理')
    nlp_parser.add_argument('--model-path', type=str, 
                           default="meta-llama/Meta-Llama-3.1-8B-Instruct",
                           help='Llama模型路径')
    nlp_parser.add_argument('--batch-size', type=int, default=10, help='批处理大小')
    nlp_parser.add_argument('--job-id', type=int, help='处理指定的职位ID')
    nlp_parser.add_argument('--reprocess', action='store_true', help='重新处理所有职位')
    
    # 分析命令
    analysis_parser = subparsers.add_parser('analyze', help='运行数据分析')
    analysis_parser.add_argument('--show-stats', action='store_true', help='显示统计信息')
    
    # 完整流水线命令
    pipeline_parser = subparsers.add_parser('pipeline', help='运行完整的数据处理流水线')
    pipeline_parser.add_argument('--pages', type=int, default=3, help='每个关键词爬取的页数')
    pipeline_parser.add_argument('--model-path', type=str, 
                                default="meta-llama/Meta-Llama-3.1-8B-Instruct",
                                help='Llama模型路径')
    pipeline_parser.add_argument('--batch-size', type=int, default=10, help='批处理大小')
    pipeline_parser.add_argument('--show-stats', action='store_true', help='显示统计信息')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'crawl':
            run_crawler(args)
        elif args.command == 'process':
            run_nlp_processing(args)
        elif args.command == 'analyze':
            run_analysis(args)
        elif args.command == 'pipeline':
            run_full_pipeline(args)
            
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 