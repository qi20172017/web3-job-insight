"""
Boss直聘爬虫
爬取Boss直聘平台的Web3相关职位信息
"""

import re
from urllib.parse import urljoin, quote
from typing import List, Dict
from .base_crawler import BaseCrawler, Web3JobFilter
import logging

logger = logging.getLogger(__name__)

class BossCrawler(BaseCrawler):
    """Boss直聘爬虫"""
    
    def __init__(self):
        super().__init__(use_selenium=True, headless=True)
        self.base_url = "https://www.zhipin.com"
        self.search_url = "https://www.zhipin.com/web/geek/job"
    
    def crawl_jobs(self, keywords: List[str], pages: int = 1) -> List[Dict]:
        """爬取职位信息"""
        all_jobs = []
        
        for keyword in keywords:
            logger.info(f"开始爬取关键词: {keyword}")
            
            for page in range(1, pages + 1):
                logger.info(f"爬取第 {page} 页")
                
                # 构建搜索URL
                search_params = {
                    'query': keyword,
                    'city': '100010000',  # 全国
                    'page': page
                }
                
                url = f"{self.search_url}?query={quote(keyword)}&city=100010000&page={page}"
                
                try:
                    html = self.get_page(url)
                    if not html:
                        continue
                    
                    soup = self.parse_page(html)
                    job_items = self._parse_job_list(soup)
                    
                    # 过滤Web3相关职位
                    web3_jobs = [job for job in job_items if self._is_web3_job(job)]
                    all_jobs.extend(web3_jobs)
                    
                    logger.info(f"本页找到 {len(web3_jobs)} 个Web3相关职位")
                    
                    # 随机延迟
                    self.random_delay(2, 5)
                    
                except Exception as e:
                    logger.error(f"爬取页面失败: {e}")
                    continue
        
        logger.info(f"总共找到 {len(all_jobs)} 个Web3相关职位")
        return all_jobs
    
    def _parse_job_list(self, soup) -> List[Dict]:
        """解析职位列表页面"""
        jobs = []
        
        # 查找职位列表容器
        job_cards = soup.select('.job-card-wrapper') or soup.select('.job-card-body')
        
        for card in job_cards:
            try:
                job_data = self._extract_job_basic_info(card)
                if job_data:
                    jobs.append(job_data)
            except Exception as e:
                logger.error(f"解析职位卡片失败: {e}")
                continue
        
        return jobs
    
    def _extract_job_basic_info(self, card) -> Dict:
        """从职位卡片提取基本信息"""
        try:
            # 职位标题和链接
            title_element = card.select_one('.job-name a') or card.select_one('.job-title a')
            title = self.extract_text(title_element)
            job_url = self.extract_attribute(title_element, 'href')
            if job_url:
                job_url = urljoin(self.base_url, job_url)
            
            # 公司名称
            company_element = card.select_one('.company-name a') or card.select_one('.company-name')
            company = self.extract_text(company_element)
            
            # 薪资
            salary_element = card.select_one('.salary') or card.select_one('.job-limit .red')
            salary = self.extract_text(salary_element)
            
            # 工作地点
            location_element = card.select_one('.job-area') or card.select_one('.job-limit .gray')
            location = self.extract_text(location_element)
            
            # 经验要求
            experience_element = card.select_one('.job-limit') or card.select_one('.job-desc')
            experience_text = self.extract_text(experience_element)
            
            # 职位描述/标签
            tags_elements = card.select('.tag-list .tag') or card.select('.job-desc .tag')
            tags = [self.extract_text(tag) for tag in tags_elements]
            
            # 解析薪资范围
            salary_min, salary_max = self._parse_salary(salary)
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'salary_text': salary,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_currency': 'CNY',
                'experience_level': experience_text,
                'tags': tags,
                'source_url': job_url,
                'source_platform': 'Boss直聘',
                'is_web3_related': False,  # 后续会更新
                'web3_skills': [],
            }
            
            return job_data
            
        except Exception as e:
            logger.error(f"提取职位基本信息失败: {e}")
            return {}
    
    def parse_job_detail(self, url: str) -> Dict:
        """解析职位详情页面"""
        try:
            html = self.get_page(url)
            if not html:
                return {}
            
            soup = self.parse_page(html)
            
            # 职位描述
            desc_element = soup.select_one('.job-detail-section') or soup.select_one('.detail-content')
            description = self.extract_text(desc_element)
            
            # 职位要求
            req_element = soup.select_one('.job-detail .text') or soup.select_one('.detail-content .text')
            requirements = self.extract_text(req_element) if req_element else description
            
            # 公司信息
            company_info = self._extract_company_info(soup)
            
            detail_data = {
                'description': description,
                'requirements': requirements,
                'company_info': company_info,
            }
            
            return detail_data
            
        except Exception as e:
            logger.error(f"解析职位详情失败 {url}: {e}")
            return {}
    
    def _extract_company_info(self, soup) -> Dict:
        """提取公司信息"""
        try:
            company_info = {}
            
            # 公司规模
            size_element = soup.select_one('.company-info .gray')
            if size_element:
                company_info['size'] = self.extract_text(size_element)
            
            # 公司行业
            industry_element = soup.select_one('.company-info .company-industry')
            if industry_element:
                company_info['industry'] = self.extract_text(industry_element)
            
            return company_info
            
        except Exception as e:
            logger.error(f"提取公司信息失败: {e}")
            return {}
    
    def _parse_salary(self, salary_text: str) -> tuple:
        """解析薪资文本，返回最低和最高薪资（月薪，单位：千元）"""
        if not salary_text:
            return None, None
        
        # 匹配薪资范围，如 "15-25K", "8-12K·13薪", "面议"
        pattern = r'(\d+)-(\d+)K'
        match = re.search(pattern, salary_text)
        
        if match:
            min_salary = int(match.group(1)) * 1000
            max_salary = int(match.group(2)) * 1000
            return min_salary, max_salary
        
        # 匹配单一薪资，如 "20K以上"
        pattern_single = r'(\d+)K'
        match_single = re.search(pattern_single, salary_text)
        if match_single:
            salary = int(match_single.group(1)) * 1000
            return salary, salary
        
        return None, None
    
    def _is_web3_job(self, job_data: Dict) -> bool:
        """判断是否为Web3相关职位"""
        # 检查标题、公司名、标签等字段
        text_to_check = f"{job_data.get('title', '')} {job_data.get('company', '')} {' '.join(job_data.get('tags', []))}"
        
        is_web3 = Web3JobFilter.is_web3_related(text_to_check)
        
        if is_web3:
            job_data['is_web3_related'] = True
            job_data['web3_skills'] = Web3JobFilter.extract_web3_skills(text_to_check)
        
        return is_web3 