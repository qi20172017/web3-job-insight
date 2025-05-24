"""
Web3招聘数据分析器
提供各种数据分析和可视化功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.db.models import JobPosting, ProcessedJobData, CompanyInfo, create_session

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)

class JobAnalyzer:
    """Web3招聘数据分析器"""
    
    def __init__(self):
        self.session = create_session()
    
    def get_job_dataframe(self, include_processed: bool = True) -> pd.DataFrame:
        """获取职位数据的DataFrame"""
        try:
            if include_processed:
                # 连接查询，包含处理后的数据
                query = self.session.query(
                    JobPosting,
                    ProcessedJobData
                ).outerjoin(
                    ProcessedJobData, JobPosting.id == ProcessedJobData.job_id
                )
                
                data = []
                for job, processed in query.all():
                    row = {
                        'id': job.id,
                        'title': job.title,
                        'company': job.company,
                        'location': job.location,
                        'salary_min': job.salary_min,
                        'salary_max': job.salary_max,
                        'source_platform': job.source_platform,
                        'crawl_date': job.crawl_date,
                        'is_web3_related': job.is_web3_related,
                        'web3_skills': job.web3_skills,
                    }
                    
                    if processed:
                        row.update({
                            'job_category': processed.job_category,
                            'seniority_level': processed.seniority_level,
                            'remote_work': processed.remote_work,
                            'defi_related': processed.defi_related,
                            'nft_related': processed.nft_related,
                            'dao_related': processed.dao_related,
                            'smart_contract': processed.smart_contract,
                            'confidence_score': processed.confidence_score,
                        })
                    
                    data.append(row)
            
            else:
                # 只获取基础职位数据
                jobs = self.session.query(JobPosting).all()
                data = []
                for job in jobs:
                    data.append({
                        'id': job.id,
                        'title': job.title,
                        'company': job.company,
                        'location': job.location,
                        'salary_min': job.salary_min,
                        'salary_max': job.salary_max,
                        'source_platform': job.source_platform,
                        'crawl_date': job.crawl_date,
                        'is_web3_related': job.is_web3_related,
                    })
            
            df = pd.DataFrame(data)
            return df
            
        except Exception as e:
            logger.error(f"获取职位数据失败: {e}")
            return pd.DataFrame()
    
    def analyze_salary_distribution(self, save_plot: bool = True) -> Dict:
        """分析薪资分布"""
        df = self.get_job_dataframe()
        
        if df.empty:
            return {}
        
        # 过滤有效薪资数据
        salary_df = df[(df['salary_min'].notna()) & (df['salary_max'].notna())]
        
        if salary_df.empty:
            return {}
        
        # 计算平均薪资
        salary_df['avg_salary'] = (salary_df['salary_min'] + salary_df['salary_max']) / 2
        
        analysis = {
            'total_jobs_with_salary': len(salary_df),
            'avg_min_salary': salary_df['salary_min'].mean(),
            'avg_max_salary': salary_df['salary_max'].mean(),
            'median_avg_salary': salary_df['avg_salary'].median(),
            'salary_std': salary_df['avg_salary'].std(),
            'salary_percentiles': {
                '25%': salary_df['avg_salary'].quantile(0.25),
                '50%': salary_df['avg_salary'].quantile(0.50),
                '75%': salary_df['avg_salary'].quantile(0.75),
                '90%': salary_df['avg_salary'].quantile(0.90),
            }
        }
        
        if save_plot:
            # 创建薪资分布图
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # 薪资分布直方图
            axes[0, 0].hist(salary_df['avg_salary'], bins=30, alpha=0.7, color='skyblue')
            axes[0, 0].set_title('薪资分布直方图')
            axes[0, 0].set_xlabel('平均薪资 (元)')
            axes[0, 0].set_ylabel('职位数量')
            
            # 薪资箱线图
            axes[0, 1].boxplot(salary_df['avg_salary'])
            axes[0, 1].set_title('薪资分布箱线图')
            axes[0, 1].set_ylabel('平均薪资 (元)')
            
            # Web3 vs 非Web3薪资对比
            web3_salaries = salary_df[salary_df['is_web3_related'] == True]['avg_salary']
            non_web3_salaries = salary_df[salary_df['is_web3_related'] == False]['avg_salary']
            
            axes[1, 0].hist([web3_salaries, non_web3_salaries], 
                           bins=20, alpha=0.7, label=['Web3相关', '非Web3'], 
                           color=['orange', 'lightblue'])
            axes[1, 0].set_title('Web3 vs 非Web3 薪资分布')
            axes[1, 0].set_xlabel('平均薪资 (元)')
            axes[1, 0].set_ylabel('职位数量')
            axes[1, 0].legend()
            
            # 平台薪资对比
            platform_salaries = salary_df.groupby('source_platform')['avg_salary'].mean()
            axes[1, 1].bar(platform_salaries.index, platform_salaries.values, color='lightgreen')
            axes[1, 1].set_title('各平台平均薪资')
            axes[1, 1].set_xlabel('招聘平台')
            axes[1, 1].set_ylabel('平均薪资 (元)')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig('reports/salary_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("薪资分析图表已保存至 reports/salary_analysis.png")
        
        return analysis
    
    def analyze_job_categories(self, save_plot: bool = True) -> Dict:
        """分析职位类别分布"""
        df = self.get_job_dataframe()
        
        if df.empty or 'job_category' not in df.columns:
            return {}
        
        # 职位类别统计
        category_counts = df['job_category'].value_counts()
        
        # Web3特征分析
        web3_features = ['defi_related', 'nft_related', 'dao_related', 'smart_contract']
        feature_stats = {}
        
        for feature in web3_features:
            if feature in df.columns:
                feature_stats[feature] = df[feature].sum()
        
        analysis = {
            'category_distribution': category_counts.to_dict(),
            'web3_features': feature_stats,
            'total_categorized_jobs': len(df[df['job_category'].notna()])
        }
        
        if save_plot and not category_counts.empty:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # 职位类别饼图
            if len(category_counts) > 0:
                axes[0, 0].pie(category_counts.values[:10], labels=category_counts.index[:10], autopct='%1.1f%%')
                axes[0, 0].set_title('Top 10 职位类别分布')
            
            # 职位类别柱状图
            category_counts[:15].plot(kind='bar', ax=axes[0, 1], color='lightcoral')
            axes[0, 1].set_title('职位类别分布')
            axes[0, 1].set_xlabel('职位类别')
            axes[0, 1].set_ylabel('职位数量')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Web3特征分布
            if feature_stats:
                feature_names = list(feature_stats.keys())
                feature_values = list(feature_stats.values())
                axes[1, 0].bar(feature_names, feature_values, color='lightblue')
                axes[1, 0].set_title('Web3特征分布')
                axes[1, 0].set_xlabel('Web3特征')
                axes[1, 0].set_ylabel('职位数量')
                axes[1, 0].tick_params(axis='x', rotation=45)
            
            # 资历级别分布
            if 'seniority_level' in df.columns:
                seniority_counts = df['seniority_level'].value_counts()
                seniority_counts.plot(kind='bar', ax=axes[1, 1], color='lightgreen')
                axes[1, 1].set_title('资历级别分布')
                axes[1, 1].set_xlabel('资历级别')
                axes[1, 1].set_ylabel('职位数量')
                axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig('reports/category_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("职位类别分析图表已保存至 reports/category_analysis.png")
        
        return analysis
    
    def analyze_location_distribution(self, save_plot: bool = True) -> Dict:
        """分析地区分布"""
        df = self.get_job_dataframe()
        
        if df.empty:
            return {}
        
        # 地区统计
        location_counts = df['location'].value_counts()
        
        # Web3职位地区分布
        web3_location_counts = df[df['is_web3_related'] == True]['location'].value_counts()
        
        analysis = {
            'total_locations': len(location_counts),
            'top_locations': location_counts.head(10).to_dict(),
            'web3_top_locations': web3_location_counts.head(10).to_dict()
        }
        
        if save_plot and not location_counts.empty:
            fig, axes = plt.subplots(2, 1, figsize=(15, 10))
            
            # 总体地区分布
            location_counts.head(15).plot(kind='bar', ax=axes[0], color='skyblue')
            axes[0].set_title('职位地区分布 (Top 15)')
            axes[0].set_xlabel('地区')
            axes[0].set_ylabel('职位数量')
            axes[0].tick_params(axis='x', rotation=45)
            
            # Web3职位地区分布
            web3_location_counts.head(15).plot(kind='bar', ax=axes[1], color='orange')
            axes[1].set_title('Web3职位地区分布 (Top 15)')
            axes[1].set_xlabel('地区')
            axes[1].set_ylabel('职位数量')
            axes[1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig('reports/location_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("地区分析图表已保存至 reports/location_analysis.png")
        
        return analysis
    
    def analyze_company_insights(self, save_plot: bool = True) -> Dict:
        """分析公司洞察"""
        df = self.get_job_dataframe()
        
        if df.empty:
            return {}
        
        # 公司职位数量统计
        company_counts = df['company'].value_counts()
        
        # Web3公司统计
        web3_companies = df[df['is_web3_related'] == True]['company'].value_counts()
        
        # 平均薪资最高的公司
        salary_df = df[(df['salary_min'].notna()) & (df['salary_max'].notna())]
        if not salary_df.empty:
            salary_df['avg_salary'] = (salary_df['salary_min'] + salary_df['salary_max']) / 2
            company_avg_salary = salary_df.groupby('company')['avg_salary'].mean().sort_values(ascending=False)
        else:
            company_avg_salary = pd.Series()
        
        analysis = {
            'total_companies': len(company_counts),
            'top_hiring_companies': company_counts.head(20).to_dict(),
            'top_web3_companies': web3_companies.head(20).to_dict(),
            'highest_paying_companies': company_avg_salary.head(20).to_dict() if not company_avg_salary.empty else {}
        }
        
        if save_plot:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            
            # 招聘最多的公司
            if not company_counts.empty:
                company_counts.head(15).plot(kind='barh', ax=axes[0, 0], color='lightblue')
                axes[0, 0].set_title('招聘职位最多的公司 (Top 15)')
                axes[0, 0].set_xlabel('职位数量')
                axes[0, 0].set_ylabel('公司名称')
            
            # Web3公司招聘情况
            if not web3_companies.empty:
                web3_companies.head(15).plot(kind='barh', ax=axes[0, 1], color='orange')
                axes[0, 1].set_title('Web3职位最多的公司 (Top 15)')
                axes[0, 1].set_xlabel('职位数量')
                axes[0, 1].set_ylabel('公司名称')
            
            # 薪资最高的公司
            if not company_avg_salary.empty:
                company_avg_salary.head(15).plot(kind='barh', ax=axes[1, 0], color='lightgreen')
                axes[1, 0].set_title('平均薪资最高的公司 (Top 15)')
                axes[1, 0].set_xlabel('平均薪资 (元)')
                axes[1, 0].set_ylabel('公司名称')
            
            # 公司规模分布
            company_size_dist = company_counts.value_counts()
            axes[1, 1].hist(company_counts.values, bins=20, alpha=0.7, color='lightcoral')
            axes[1, 1].set_title('公司招聘规模分布')
            axes[1, 1].set_xlabel('招聘职位数量')
            axes[1, 1].set_ylabel('公司数量')
            
            plt.tight_layout()
            plt.savefig('reports/company_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("公司分析图表已保存至 reports/company_analysis.png")
        
        return analysis
    
    def generate_comprehensive_report(self) -> Dict:
        """生成综合分析报告"""
        logger.info("开始生成综合分析报告")
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'salary_analysis': self.analyze_salary_distribution(),
            'category_analysis': self.analyze_job_categories(),
            'location_analysis': self.analyze_location_distribution(),
            'company_analysis': self.analyze_company_insights(),
        }
        
        # 保存报告到JSON文件
        with open('reports/comprehensive_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info("综合分析报告已生成并保存至 reports/comprehensive_report.json")
        
        return report
    
    def close(self):
        """关闭数据库连接"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 