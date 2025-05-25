"""
数据库模型定义
定义web3招聘职位相关的数据表结构
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class JobPosting(Base):
    """招聘职位表"""
    __tablename__ = 'job_postings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 基本信息
    job_id = Column(String(255), nullable=False, comment='职位ID')
    title = Column(String(255), nullable=False, comment='职位名称')
    company = Column(String(255), nullable=False, comment='公司名称')
    company_id = Column(String(255), nullable=False, comment='公司ID')
    company_logo = Column(String(500), comment='公司Logo')
    company_twitter = Column(String(255), comment='公司Twitter')
    company_website = Column(String(255), comment='公司官网')
    location = Column(String(255), comment='工作地点')
    job_type = Column(String(50), comment='工作类型（全职/兼职/实习）')
    experience_level = Column(String(50), comment='经验要求')
    education_level = Column(String(50), comment='学历要求')

    # 薪资信息
    salary_min = Column(Integer, comment='最低薪资')
    salary_max = Column(Integer, comment='最高薪资')
    unit_text = Column(String(50), comment='薪资单位')
    salary_currency = Column(String(10), default='CNY', comment='货币单位')
    
    # 职位描述
    description = Column(Text, comment='职位描述原文')
    requirements = Column(Text, comment='职位要求')
    benefits = Column(Text, comment='福利待遇')
    application_count = Column(Integer, comment='申请人数')
    tags = Column(String(500), comment='标签')

    # 来源信息
    source_url = Column(String(500), comment='原始链接')
    source_platform = Column(String(50), comment='来源平台')
    
    # 时间信息
    posted_date = Column(DateTime, comment='发布时间')
    last_updated_date = Column(DateTime, comment='最后更新时间')
    last_application_date = Column(DateTime, comment='最后申请时间')
    crawl_date = Column(DateTime, default=datetime.now, comment='爬取时间')
    updated_date = Column(DateTime, default=datetime.now, comment='更新时间')
    # Web3相关字段
    blockchain_platforms = Column(String(500), comment='区块链平台')
    programming_languages = Column(String(500), comment='编程语言')
    web3_skills = Column(String(500), comment='Web3技能')
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment='是否有效')
    processed = Column(Boolean, default=False, comment='是否已处理')
    
    def __repr__(self):
        return f"<JobPosting(title='{self.title}', company='{self.company}')>"

class CompanyInfo(Base):
    """公司信息表"""
    __tablename__ = 'company_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, comment='公司名称')
    industry = Column(String(100), comment='所属行业')
    size = Column(String(50), comment='公司规模')
    location = Column(String(255), comment='公司地址')
    description = Column(Text, comment='公司描述')
    website = Column(String(255), comment='公司官网')
    
    # Web3相关信息
    is_web3_company = Column(Boolean, default=False, comment='是否Web3公司')
    focus_areas = Column(String(500), comment='专注领域')
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<CompanyInfo(name='{self.name}', industry='{self.industry}')>"

class ProcessedJobData(Base):
    """AI处理后的职位数据"""
    __tablename__ = 'processed_job_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, nullable=False, comment='关联的原始职位ID')
    
    # AI提取的结构化信息
    extracted_skills = Column(Text, comment='提取的技能要求(JSON格式)')
    required_experience = Column(String(100), comment='经验要求')
    education_requirement = Column(String(100), comment='学历要求')
    key_responsibilities = Column(Text, comment='核心职责')
    
    # 分类信息
    job_category = Column(String(100), comment='职位类别')
    seniority_level = Column(String(50), comment='资历级别')
    remote_work = Column(Boolean, comment='是否支持远程')
    
    # Web3特征
    defi_related = Column(Boolean, default=False, comment='是否DeFi相关')
    nft_related = Column(Boolean, default=False, comment='是否NFT相关')
    dao_related = Column(Boolean, default=False, comment='是否DAO相关')
    smart_contract = Column(Boolean, default=False, comment='是否涉及智能合约')
    
    # AI处理信息
    model_used = Column(String(100), comment='使用的AI模型')
    confidence_score = Column(Float, comment='置信度分数')
    processing_date = Column(DateTime, default=datetime.now, comment='处理时间')
    
    def __repr__(self):
        return f"<ProcessedJobData(job_id={self.job_id}, category='{self.job_category}')>"

# 数据库连接配置
def get_database_url():
    """获取数据库连接URL"""
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '3306')
    username = os.getenv('DB_USERNAME', 'root')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'web3_jobs')
    
    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"

def create_database_engine():
    """创建数据库引擎"""
    engine = create_engine(
        get_database_url(),
        echo=False,  # 设置为True可以打印SQL语句
        pool_recycle=3600,  # 连接池回收时间
        pool_size=10,  # 连接池大小
        max_overflow=20  # 最大溢出连接数
    )
    return engine

def create_session():
    """创建数据库会话"""
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_database():
    """初始化数据库，创建所有表"""
    engine = create_database_engine()
    Base.metadata.create_all(engine)
    print("数据库表创建成功！") 


if __name__ == "__main__":
    init_database()