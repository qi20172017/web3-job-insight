"""
数据管理器
负责招聘数据的保存、查询和统计
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, func, desc
from datetime import datetime, date
from typing import Dict, List, Optional
import json
import logging

from .models import JobPosting, CompanyInfo, ProcessedJobData, create_session

logger = logging.getLogger(__name__)

class JobDataManager:
    """招聘数据管理器"""
    
    def __init__(self):
        self.session = create_session()
    
    def save_job(self, job_data: Dict) -> Optional[int]:
        """保存职位数据到数据库"""
        try:
            # 检查是否已存在相同职位
            existing_job = self._find_existing_job(job_data)
            if existing_job:
                logger.info(f"职位已存在: {job_data.get('title', '')} - {job_data.get('company', '')}")
                return existing_job.id
            
            # 创建新的职位记录
            job = JobPosting(
                title=job_data.get('title', ''),
                company=job_data.get('company', ''),
                location=job_data.get('location', ''),
                salary_min=job_data.get('salary_min'),
                salary_max=job_data.get('salary_max'),
                description=job_data.get('description', ''),
                source_url=job_data.get('source_url', ''),
                source_platform=job_data.get('source_platform', ''),
                is_web3_related=job_data.get('is_web3_related', False),
                web3_skills=','.join(job_data.get('web3_skills', [])) if job_data.get('web3_skills') else '',
            )
            
            self.session.add(job)
            self.session.commit()
            
            logger.info(f"职位保存成功: {job_data.get('title', '')}")
            return job.id
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"保存职位失败: {e}")
            raise
    
    def _find_existing_job(self, job_data: Dict) -> Optional[JobPosting]:
        """查找是否已存在相同职位"""
        if job_data.get('source_url'):
            return self.session.query(JobPosting).filter(
                JobPosting.source_url == job_data['source_url']
            ).first()
        return None
    
    def get_statistics(self) -> Dict:
        """获取数据统计信息"""
        try:
            total_jobs = self.session.query(JobPosting).count()
            web3_jobs = self.session.query(JobPosting).filter(
                JobPosting.is_web3_related == True
            ).count()
            
            today = date.today()
            today_jobs = self.session.query(JobPosting).filter(
                func.date(JobPosting.crawl_date) == today
            ).count()
            
            unprocessed_jobs = self.session.query(JobPosting).filter(
                JobPosting.processed == False
            ).count()
            
            return {
                'total_jobs': total_jobs,
                'web3_jobs': web3_jobs,
                'today_jobs': today_jobs,
                'unprocessed_jobs': unprocessed_jobs
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        self.session.close() 