"""
数据处理主程序
使用Llama模型处理招聘数据，提取结构化信息
"""

import sys
import os
import logging
from typing import List, Dict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.nlp.llama_processor import LlamaJobProcessor
from src.db.data_manager import JobDataManager
from src.db.models import JobPosting

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nlp_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, model_path: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"):
        """
        初始化数据处理器
        
        Args:
            model_path: Llama模型路径
        """
        self.data_manager = JobDataManager()
        self.llama_processor = LlamaJobProcessor(model_path)
        
    def process_unprocessed_jobs(self, batch_size: int = 10):
        """处理未处理的职位数据"""
        logger.info("开始处理未处理的职位数据")
        
        try:
            # 获取未处理的职位
            unprocessed_jobs = self.data_manager.get_unprocessed_jobs(limit=1000)
            logger.info(f"找到 {len(unprocessed_jobs)} 个未处理的职位")
            
            if not unprocessed_jobs:
                logger.info("没有需要处理的职位")
                return
            
            # 分批处理
            for i in range(0, len(unprocessed_jobs), batch_size):
                batch_jobs = unprocessed_jobs[i:i + batch_size]
                logger.info(f"处理第 {i//batch_size + 1} 批，共 {len(batch_jobs)} 个职位")
                
                self._process_job_batch(batch_jobs)
                
                logger.info(f"第 {i//batch_size + 1} 批处理完成")
            
            logger.info("所有职位处理完成")
            
        except Exception as e:
            logger.error(f"处理职位数据失败: {e}")
            raise
        finally:
            self.cleanup()
    
    def _process_job_batch(self, jobs: List[JobPosting]):
        """处理一批职位数据"""
        # 准备数据
        job_data = []
        for job in jobs:
            job_dict = {
                'id': job.id,
                'title': job.title,
                'description': job.description or '',
                'requirements': job.requirements or '',
                'company': job.company,
                'location': job.location
            }
            job_data.append(job_dict)
        
        try:
            # 使用Llama模型提取信息
            processed_results = self.llama_processor.batch_process_jobs(job_data)
            
            # 保存处理结果
            for result in processed_results:
                job_id = result.get('job_id')
                if job_id:
                    try:
                        self.data_manager.save_processed_data(job_id, result)
                        logger.info(f"职位 {job_id} 处理结果保存成功")
                    except Exception as e:
                        logger.error(f"保存职位 {job_id} 处理结果失败: {e}")
            
        except Exception as e:
            logger.error(f"批量处理失败: {e}")
            raise
    
    def process_single_job(self, job_id: int) -> Dict:
        """处理单个职位"""
        try:
            # 获取职位信息
            session = self.data_manager.session
            job = session.query(JobPosting).get(job_id)
            
            if not job:
                raise ValueError(f"职位 {job_id} 不存在")
            
            # 提取信息
            description = (job.description or '') + " " + (job.requirements or '')
            extracted_info = self.llama_processor.extract_job_info(description, job.title)
            
            # 保存结果
            self.data_manager.save_processed_data(job_id, extracted_info)
            
            logger.info(f"职位 {job_id} 处理完成")
            return extracted_info
            
        except Exception as e:
            logger.error(f"处理职位 {job_id} 失败: {e}")
            raise
    
    def reprocess_jobs(self, job_ids: List[int] = None):
        """重新处理指定的职位"""
        if job_ids:
            logger.info(f"重新处理指定的 {len(job_ids)} 个职位")
            for job_id in job_ids:
                try:
                    self.process_single_job(job_id)
                except Exception as e:
                    logger.error(f"重新处理职位 {job_id} 失败: {e}")
        else:
            logger.info("重新处理所有职位")
            # 标记所有职位为未处理
            session = self.data_manager.session
            session.query(JobPosting).update({'processed': False})
            session.commit()
            
            # 处理所有职位
            self.process_unprocessed_jobs()
    
    def get_processing_statistics(self) -> Dict:
        """获取处理统计信息"""
        stats = self.data_manager.get_statistics()
        
        # 添加AI处理相关统计
        session = self.data_manager.session
        
        # 已处理职位数
        processed_count = session.query(JobPosting).filter(
            JobPosting.processed == True
        ).count()
        
        # 各类Web3特征统计
        from src.db.models import ProcessedJobData
        
        defi_count = session.query(ProcessedJobData).filter(
            ProcessedJobData.defi_related == True
        ).count()
        
        nft_count = session.query(ProcessedJobData).filter(
            ProcessedJobData.nft_related == True
        ).count()
        
        dao_count = session.query(ProcessedJobData).filter(
            ProcessedJobData.dao_related == True
        ).count()
        
        smart_contract_count = session.query(ProcessedJobData).filter(
            ProcessedJobData.smart_contract == True
        ).count()
        
        stats.update({
            'processed_jobs': processed_count,
            'web3_features': {
                'defi_jobs': defi_count,
                'nft_jobs': nft_count,
                'dao_jobs': dao_count,
                'smart_contract_jobs': smart_contract_count
            }
        })
        
        return stats
    
    def cleanup(self):
        """清理资源"""
        try:
            self.llama_processor.cleanup()
            self.data_manager.close()
            logger.info("资源清理完成")
        except Exception as e:
            logger.error(f"资源清理失败: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='处理招聘数据')
    parser.add_argument('--model-path', type=str, default="meta-llama/Meta-Llama-3.1-8B-Instruct",
                        help='Llama模型路径')
    parser.add_argument('--batch-size', type=int, default=10,
                        help='批处理大小')
    parser.add_argument('--job-id', type=int,
                        help='处理指定的职位ID')
    parser.add_argument('--reprocess', action='store_true',
                        help='重新处理所有职位')
    parser.add_argument('--stats', action='store_true',
                        help='显示处理统计信息')
    
    args = parser.parse_args()
    
    processor = DataProcessor(args.model_path)
    
    try:
        if args.stats:
            # 显示统计信息
            stats = processor.get_processing_statistics()
            logger.info("=== 数据处理统计 ===")
            for key, value in stats.items():
                logger.info(f"{key}: {value}")
        
        elif args.job_id:
            # 处理指定职位
            processor.process_single_job(args.job_id)
        
        elif args.reprocess:
            # 重新处理所有职位
            processor.reprocess_jobs()
        
        else:
            # 处理未处理的职位
            processor.process_unprocessed_jobs(args.batch_size)
            
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        raise
    finally:
        processor.cleanup()

if __name__ == "__main__":
    main() 