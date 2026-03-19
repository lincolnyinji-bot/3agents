#!/usr/bin/env python3
"""
增强Butler Agent - 完善数据处理流水线
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class EnhancedButlerAgent:
    """增强版Butler Agent - 完善数据处理"""
    
    def __init__(self):
        self.work_dir = Path("C:/Users/宗璐/.openclaw/workspace/3agents")
        self.data_dir = self.work_dir / "enhanced_butler_data"
        self.data_dir.mkdir(exist_ok=True)
        
        # 数据处理管道
        self.processing_pipeline = [
            "data_validation",
            "data_cleaning",
            "data_enrichment",
            "data_normalization",
            "data_storage"
        ]
        
        # 数据清洗规则
        self.cleaning_rules = {
            "experience": {
                "patterns": [
                    r"(\d+)[年|年多|年以上]",
                    r"工作经验.*?(\d+)年",
                    r"(\d+).*?年经验"
                ],
                "default": "0年"
            },
            "salary": {
                "patterns": [
                    r"(\d+)[-~](\d+)[万|k|K]",
                    r"(\d+)[万|k|K]以上",
                    r"面议|保密"
                ],
                "default": "面议"
            },
            "education": {
                "values": ["博士", "硕士", "本科", "大专", "中专", "高中"],
                "default": "本科"
            }
        }
        
        # 数据丰富源
        self.enrichment_sources = {
            "skill_synonyms": {
                "投资": ["股权投资", "私募投资", "风险投资", "天使投资"],
                "财务": ["财务分析", "财务管理", "财务会计", "财务建模"],
                "研究": ["行业研究", "市场研究", "数据分析", "策略研究"]
            },
            "company_tiers": {
                "知名": ["知名", "领先", "头部", "顶级", "一流"],
                "中型": ["中型", "成长型", "发展型"],
                "初创": ["初创", "创业", "早期"]
            }
        }
    
    def validate_candidate_data(self, candidate: Dict) -> Dict:
        """验证候选人数据完整性"""
        logger.info(f"验证候选人数据: {candidate.get('name', '未知')}")
        
        validation_result = {
            "is_valid": True,
            "missing_fields": [],
            "invalid_fields": [],
            "suggestions": []
        }
        
        required_fields = ["name", "position", "experience", "location"]
        for field in required_fields:
            if field not in candidate or not candidate[field]:
                validation_result["missing_fields"].append(field)
                validation_result["is_valid"] = False
        
        # 经验验证
        if "experience" in candidate:
            exp_match = re.search(r'\d+', str(candidate["experience"]))
            if not exp_match:
                validation_result["invalid_fields"].append("experience")
                validation_result["suggestions"].append("经验格式应为'X年'")
        
        # 薪资验证
        if "salary" in candidate and candidate["salary"]:
            salary_str = str(candidate["salary"])
            if not (re.search(r'\d+', salary_str) or salary_str in ["面议", "保密"]):
                validation_result["invalid_fields"].append("salary")
                validation_result["suggestions"].append("薪资格式应为'XX-XX万'或'面议'")
        
        return validation_result
    
    def clean_candidate_data(self, candidate: Dict) -> Dict:
        """清洗候选人数据"""
        logger.info(f"清洗候选人数据: {candidate.get('name', '未知')}")
        
        cleaned = candidate.copy()
        
        # 清洗经验
        if "experience" in cleaned:
            exp_str = str(cleaned["experience"])
            for pattern in self.cleaning_rules["experience"]["patterns"]:
                match = re.search(pattern, exp_str)
                if match:
                    years = match.group(1)
                    cleaned["experience"] = f"{years}年"
                    cleaned["experience_years"] = int(years)
                    break
            else:
                cleaned["experience"] = self.cleaning_rules["experience"]["default"]
                cleaned["experience_years"] = 0
        
        # 清洗薪资
        if "salary" in cleaned and cleaned["salary"]:
            salary_str = str(cleaned["salary"])
            for pattern in self.cleaning_rules["salary"]["patterns"]:
                match = re.search(pattern, salary_str)
                if match:
                    if len(match.groups()) == 2:
                        min_salary, max_salary = match.groups()
                        cleaned["salary_range"] = f"{min_salary}-{max_salary}万"
                        cleaned["salary_min"] = int(min_salary)
                        cleaned["salary_max"] = int(max_salary)
                    else:
                        cleaned["salary_range"] = salary_str
                    break
            else:
                cleaned["salary_range"] = self.cleaning_rules["salary"]["default"]
        
        # 清洗教育
        if "education" in cleaned:
            edu_str = str(cleaned["education"])
            for edu_level in self.cleaning_rules["education"]["values"]:
                if edu_level in edu_str:
                    cleaned["education_level"] = edu_level
                    break
            else:
                cleaned["education_level"] = self.cleaning_rules["education"]["default"]
        
        # 清洗技能（列表转字符串）
        if "skills" in cleaned and isinstance(cleaned["skills"], list):
            cleaned["skills_str"] = ", ".join(cleaned["skills"])
        
        return cleaned
    
    def enrich_candidate_data(self, candidate: Dict) -> Dict:
        """丰富候选人数据"""
        logger.info(f"丰富候选人数据: {candidate.get('name', '未知')}")
        
        enriched = candidate.copy()
        
        # 技能同义词扩展
        if "skills" in enriched and isinstance(enriched["skills"], list):
            skill_categories = []
            for skill in enriched["skills"]:
                for category, synonyms in self.enrichment_sources["skill_synonyms"].items():
                    if any(synonym in skill for synonym in synonyms):
                        skill_categories.append(category)
                        break
            
            enriched["skill_categories"] = list(set(skill_categories))
        
        # 公司层级判断
        if "company" in enriched:
            company_str = str(enriched["company"])
            for tier, keywords in self.enrichment_sources["company_tiers"].items():
                if any(keyword in company_str for keyword in keywords):
                    enriched["company_tier"] = tier
                    break
            else:
                enriched["company_tier"] = "普通"
        
        # 计算匹配度基础分
        score = 0
        
        # 经验分
        if "experience_years" in enriched:
            if enriched["experience_years"] >= 8:
                score += 30
            elif enriched["experience_years"] >= 5:
                score += 20
            elif enriched["experience_years"] >= 3:
                score += 10
        
        # 教育分
        if "education_level" in enriched:
            edu_scores = {"博士": 25, "硕士": 20, "本科": 15, "大专": 10, "中专": 5}
            score += edu_scores.get(enriched["education_level"], 0)
        
        # 公司层级分
        if "company_tier" in enriched:
            tier_scores = {"知名": 20, "中型": 15, "普通": 10, "初创": 5}
            score += tier_scores.get(enriched["company_tier"], 0)
        
        enriched["basic_match_score"] = min(score, 100)
        
        return enriched
    
    def normalize_candidate_data(self, candidate: Dict) -> Dict:
        """标准化候选人数据结构"""
        logger.info(f"标准化候选人数据: {candidate.get('name', '未知')}")
        
        normalized = {
            "candidate_id": candidate.get("id", f"cand_{datetime.now().timestamp()}"),
            "basic_info": {
                "name": candidate.get("name", ""),
                "position": candidate.get("position", ""),
                "company": candidate.get("company", ""),
                "company_tier": candidate.get("company_tier", "普通"),
                "location": candidate.get("location", ""),
                "status": candidate.get("status", "未知")
            },
            "qualifications": {
                "experience": candidate.get("experience", ""),
                "experience_years": candidate.get("experience_years", 0),
                "education": candidate.get("education", ""),
                "education_level": candidate.get("education_level", "本科")
            },
            "compensation": {
                "salary": candidate.get("salary", ""),
                "salary_range": candidate.get("salary_range", "面议"),
                "salary_min": candidate.get("salary_min", 0),
                "salary_max": candidate.get("salary_max", 0)
            },
            "skills": {
                "skill_list": candidate.get("skills", []),
                "skill_categories": candidate.get("skill_categories", []),
                "skills_str": candidate.get("skills_str", "")
            },
            "scores": {
                "basic_match_score": candidate.get("basic_match_score", 0),
                "validation_score": candidate.get("validation_score", 0)
            },
            "metadata": {
                "source": "scout_agent",
                "processing_time": datetime.now().isoformat(),
                "processing_steps": self.processing_pipeline
            }
        }
        
        return normalized
    
    def process_candidate_pipeline(self, candidate: Dict) -> Dict:
        """处理候选人数据管道"""
        logger.info(f"开始处理候选人管道: {candidate.get('name', '未知')}")
        
        results = {
            "original": candidate,
            "validation": None,
            "cleaned": None,
            "enriched": None,
            "normalized": None,
            "processing_log": []
        }
        
        # 1. 验证
        validation = self.validate_candidate_data(candidate)
        results["validation"] = validation
        results["processing_log"].append({
            "step": "validation",
            "status": "success" if validation["is_valid"] else "failed",
            "timestamp": datetime.now().isoformat()
        })
        
        if not validation["is_valid"]:
            logger.warning(f"数据验证失败: {validation['missing_fields']}")
            return results
        
        # 2. 清洗
        cleaned = self.clean_candidate_data(candidate)
        results["cleaned"] = cleaned
        results["processing_log"].append({
            "step": "cleaning",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
        
        # 3. 丰富
        enriched = self.enrich_candidate_data(cleaned)
        results["enriched"] = enriched
        results["processing_log"].append({
            "step": "enrichment",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
        
        # 4. 标准化
        normalized = self.normalize_candidate_data(enriched)
        results["normalized"] = normalized
        results["processing_log"].append({
            "step": "normalization",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"候选人管道处理完成: {candidate.get('name', '未知')}")
        return results
    
    def process_batch_candidates(self, candidates: List[Dict]) -> Dict:
        """批量处理候选人"""
        logger.info(f"批量处理 {len(candidates)} 个候选人")
        
        batch_results = {
            "total_candidates": len(candidates),
            "processed_candidates": 0,
            "valid_candidates": 0,
            "invalid_candidates": 0,
            "candidate_results": [],
            "summary": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for candidate in candidates:
            result = self.process_candidate_pipeline(candidate)
            batch_results["candidate_results"].append(result)
            
            if result["validation"]["is_valid"]:
                batch_results["valid_candidates"] += 1
            else:
                batch_results["invalid_candidates"] += 1
        
        batch_results["processed_candidates"] = len(candidates)
        
        # 生成摘要
        if batch_results["valid_candidates"] > 0:
            valid_results = [r for r in batch_results["candidate_results"] if r["validation"]["is_valid"]]
            
            # 平均经验
            avg_experience = sum(
                r["normalized"]["qualifications"]["experience_years"] 
                for r in valid_results if r["normalized"]
            ) / len(valid_results)
            
            # 平均匹配分
            avg_score = sum(
                r["normalized"]["scores"]["basic_match_score"]
                for r in valid_results if r["normalized"]
            ) / len(valid_results)
            
            batch_results["summary"] = {
                "average_experience_years": round(avg_experience, 1),
                "average_match_score": round(avg_score, 1),
                "education_distribution": {},
                "location_distribution": {},
                "top_skills": []
            }
        
        logger.info(f"批量处理完成: 有效{batch_results['valid_candidates']}个, 无效{batch_results['invalid_candidates']}个")
        return batch_results
    
    def save_processing_results(self, results: Dict, filename: str = None):
        """保存处理结果"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"butler_results_{timestamp}.json"
        
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"处理结果保存到: {filepath}")
        return filepath

# 测试函数
def test_enhanced_butler():
    """测试增强版Butler Agent"""
    print("="*60)
    print("增强版Butler Agent测试")
    print("="*60)
    
    butler = EnhancedButlerAgent()
    
    # 测试数据
    test_candidates = [
        {
            "id": "test_001",
            "name": "张明",
            "position": "投资经理",
            "company": "某知名私募基金",
            "experience": "6年工作经验",
            "education": "硕士学历",
            "location": "深圳",
            "skills": ["股权投资", "财务分析", "行业研究"],
            "salary": "40-60万",
            "status": "在职看机会"
        },
        {
            "id": "test_002",
            "name": "李华",
            "position": "投资总监",
            "company": "某大型投资机构",
            "experience": "8年",
            "education": "博士",
            "location": "北京",
            "skills": ["私募基金", "并购重组"],
            "salary": "面议",
            "status": "在职看机会"
        },
        {
            "id": "test_003",
            "name": "测试无效",
            "position": "",
            "experience": "未知",
            "location": ""
        }
    ]
    
    # 1. 单候选人处理测试
    print("\n1. 单候选人处理测试:")
    single_result = butler.process_candidate_pipeline(test_candidates[0])
    print(f"处理结果: {single_result['normalized']['basic_info']['name']}")
    print(f"匹配分数: {single_result['normalized']['scores']['basic_match_score']}")
    
    # 2. 批量处理测试
    print("\n2. 批量处理测试:")
    batch_result = butler.process_batch_candidates(test_candidates)
    print(f"总计: {batch_result['total_candidates']}个候选人")
    print(f"有效: {batch_result['valid_candidates']}个")
    print(f"无效: {batch_result['invalid_candidates']}个")
    
    # 3. 保存结果
    print("\n3. 保存处理结果:")
    saved_file = butler.save_processing_results(batch_result, "test_butler_results.json")
    print(f"结果保存到: {saved_file}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_enhanced_butler()