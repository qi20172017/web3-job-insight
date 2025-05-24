"""
基于Meta-Llama-3.1-8B-Instruct的职位信息处理器
用于从招聘JD中提取结构化信息
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import json
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class LlamaJobProcessor:
    """基于Llama模型的职位信息处理器"""
    
    def __init__(self, model_path: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"):
        """
        初始化Llama处理器
        
        Args:
            model_path: 模型路径，可以是本地路径或HuggingFace模型名称
        """
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.generator = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Using device: {self.device}")
        
    def load_model(self):
        """加载模型"""
        try:
            logger.info(f"Loading model: {self.model_path}")
            
            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            # 创建生成pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def extract_job_info(self, job_description: str, job_title: str = "") -> Dict:
        """
        从职位描述中提取结构化信息
        
        Args:
            job_description: 职位描述文本
            job_title: 职位标题
            
        Returns:
            提取的结构化信息
        """
        if not self.generator:
            self.load_model()
        
        prompt = self._create_extraction_prompt(job_description, job_title)
        
        try:
            # 生成响应
            response = self.generator(
                prompt,
                max_new_tokens=512,
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                return_full_text=False
            )
            
            generated_text = response[0]['generated_text']
            
            # 解析生成的JSON
            extracted_info = self._parse_response(generated_text)
            
            logger.info(f"Successfully extracted info for: {job_title}")
            return extracted_info
            
        except Exception as e:
            logger.error(f"Failed to extract job info: {e}")
            return self._get_default_info()
    
    def _create_extraction_prompt(self, job_description: str, job_title: str = "") -> str:
        """创建信息提取的提示词"""
        prompt = f"""你是一个专业的HR分析师，请从以下职位描述中提取关键信息，并以JSON格式返回。

职位标题: {job_title}
职位描述: {job_description}

请提取以下信息并以严格的JSON格式返回（不要添加任何其他文字）:

{{
    "skills": ["技能1", "技能2", "技能3"],
    "experience": "经验要求（如：3-5年）",
    "education": "学历要求（如：本科及以上）",
    "responsibilities": "核心职责描述",
    "category": "职位类别（如：后端开发、前端开发、产品经理等）",
    "seniority": "资历级别（如：初级、中级、高级、专家）",
    "remote": true/false,
    "defi": true/false,
    "nft": true/false,
    "dao": true/false,
    "smart_contract": true/false,
    "confidence": 0.85
}}

注意：
1. skills应包含具体的技术技能、工具、编程语言等
2. 布尔值判断Web3相关特征：DeFi、NFT、DAO、智能合约
3. confidence表示提取信息的置信度(0-1)
4. 只返回JSON，不要添加任何解释文字

JSON:"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """解析模型响应，提取JSON信息"""
        try:
            # 尝试直接解析JSON
            # 查找JSON部分
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            
            if matches:
                json_str = matches[0]
                # 清理可能的问题字符
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                return json.loads(json_str)
            
            # 如果无法解析，返回默认值
            logger.warning("Failed to parse JSON from response")
            return self._get_default_info()
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return self._get_default_info()
        except Exception as e:
            logger.error(f"Response parsing error: {e}")
            return self._get_default_info()
    
    def _get_default_info(self) -> Dict:
        """获取默认的信息结构"""
        return {
            "skills": [],
            "experience": "",
            "education": "",
            "responsibilities": "",
            "category": "",
            "seniority": "",
            "remote": False,
            "defi": False,
            "nft": False,
            "dao": False,
            "smart_contract": False,
            "confidence": 0.0
        }
    
    def batch_process_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """批量处理职位信息"""
        results = []
        
        for i, job in enumerate(jobs):
            logger.info(f"Processing job {i+1}/{len(jobs)}: {job.get('title', '')}")
            
            try:
                description = job.get('description', '') + " " + job.get('requirements', '')
                extracted_info = self.extract_job_info(description, job.get('title', ''))
                
                # 添加模型信息
                extracted_info['model'] = self.model_path
                extracted_info['job_id'] = job.get('id')
                
                results.append(extracted_info)
                
            except Exception as e:
                logger.error(f"Error processing job {job.get('title', '')}: {e}")
                default_info = self._get_default_info()
                default_info['job_id'] = job.get('id')
                results.append(default_info)
        
        return results
    
    def analyze_web3_features(self, text: str) -> Dict:
        """专门分析Web3特征"""
        web3_keywords = {
            'defi': ['defi', 'decentralized finance', '去中心化金融', 'yield farming', 'liquidity mining', 'amm'],
            'nft': ['nft', 'non-fungible token', '非同质化代币', 'opensea', 'collectibles'],
            'dao': ['dao', 'decentralized autonomous organization', '去中心化自治组织', 'governance'],
            'smart_contract': ['smart contract', '智能合约', 'solidity', 'contract development']
        }
        
        text_lower = text.lower()
        features = {}
        
        for feature, keywords in web3_keywords.items():
            features[feature] = any(keyword in text_lower for keyword in keywords)
        
        return features
    
    def cleanup(self):
        """清理资源"""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        if self.generator:
            del self.generator
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Model resources cleaned up") 