#!/usr/bin/env python3
"""
增强Judge Agent - 完善AI评估算法
"""
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class EnhancedJudgeAgent:
    """增强版Judge Agent - 完善AI评估"""
    
    def __init__(self):
        self.work_dir = Path("C:/Users/宗璐/.openclaw/workspace/3agents")
        self.data_dir = self.work_dir / "enhanced_judge_data"
        self.data_dir.mkdir(exist_ok=True)
        
        # 评估维度权重
        self.evaluation_weights = {
            "technical_skills": 0.30,    # 技术技能
            "experience_match": 0.25,    # 经验匹配
            "education_background": 0.15, # 教育背景
            "culture_fit": 0.15,         # 文化匹配
            "growth_potential": 0.10,    # 成长潜力
            "compensation_fit": 0.05     # 薪资匹配
        }
        
        # AI评估模型（模拟）
        self.ai_models = {
            "skill_matcher": self.ai_skill_matching,
            "experience_evaluator": self.ai_experience_evaluation,
            "culture_analyzer": self.ai_culture_analysis,
            "potential_predictor": self.ai_potential_prediction
        }
        
        # 行业知识库
        self.industry_knowledge = {
            "investment": {
                "core_skills": ["财务分析", "尽职调查", "行业研究", "投资决策", "投后管理"],
                "key_certifications": ["CFA", "CPA", "FRM", "ACCA"],
                "career_paths": ["分析师", "经理", "总监", "合伙人"],
                "salary_benchmarks": {
                    "junior": "20-30万",
                    "mid": "30-60万",
                    "senior": "60-100万",
                    "executive": "100万以上"
                }
            },
            "finance": {
                "core_skills": ["风险管理", "资产配置", "财务建模", "投资组合"],
                "key_certifications": ["CFA", "CPA", "FRM"],
                "career_paths": ["专员", "经理", "总监", "总经理"],
                "salary_benchmarks": {
                    "junior": "15-25万",
                    "mid": "25-50万",
                    "senior": "50-80万",
                    "executive": "80万以上"
                }
            }
        }
        
        # 评估标准
        self.evaluation_criteria = {
            "technical_skills": {
                "excellent": "完全掌握核心技能，有相关证书",
                "good": "掌握大部分核心技能",
                "average": "掌握基本技能",
                "poor": "技能不足"
            },
            "experience_match": {
                "excellent": "经验完全匹配，有成功案例",
                "good": "经验基本匹配",
                "average": "经验部分匹配",
                "poor": "经验不匹配"
            }
        }
    
    def ai_skill_matching(self, candidate_skills: List[str], required_skills: List[str]) -> Dict:
        """AI技能匹配分析"""
        logger.info("AI技能匹配分析...")
        
        # 技能匹配度计算
        matched_skills = []
        missing_skills = []
        
        for req_skill in required_skills:
            matched = False
            for cand_skill in candidate_skills:
                # 简单匹配逻辑（实际可用NLP）
                if req_skill in cand_skill or cand_skill in req_skill:
                    matched_skills.append({
                        "required": req_skill,
                        "candidate": cand_skill,
                        "match_level": "exact"
                    })
                    matched = True
                    break
            
            if not matched:
                missing_skills.append(req_skill)
        
        # 计算匹配度
        match_ratio = len(matched_skills) / max(len(required_skills), 1)
        
        # AI分析建议
        suggestions = []
        if match_ratio >= 0.8:
            suggestions.append("技能匹配度很高，是理想候选人")
        elif match_ratio >= 0.6:
            suggestions.append("技能基本匹配，可考虑")
        elif match_ratio >= 0.4:
            suggestions.append("技能部分匹配，需要培训")
        else:
            suggestions.append("技能匹配度不足")
        
        return {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_ratio": round(match_ratio, 2),
            "match_score": int(match_ratio * 100),
            "suggestions": suggestions
        }
    
    def ai_experience_evaluation(self, candidate_exp: Dict, jd_requirements: Dict) -> Dict:
        """AI经验评估"""
        logger.info("AI经验评估...")
        
        # 经验年限评估
        exp_years = candidate_exp.get("experience_years", 0)
        req_years = jd_requirements.get("min_experience", 3)
        
        exp_score = 0
        if exp_years >= req_years + 3:
            exp_score = 90
            exp_level = "资深"
        elif exp_years >= req_years:
            exp_score = 70
            exp_level = "匹配"
        elif exp_years >= req_years - 2:
            exp_score = 50
            exp_level = "基本匹配"
        else:
            exp_score = 30
            exp_level = "不足"
        
        # 行业经验评估
        industry_match = False
        if "industry" in candidate_exp and "industry" in jd_requirements:
            industry_match = candidate_exp["industry"] == jd_requirements["industry"]
        
        # 职位经验评估
        position_match = False
        if "position_history" in candidate_exp and "target_position" in jd_requirements:
            target_pos = jd_requirements["target_position"]
            for pos in candidate_exp.get("position_history", []):
                if target_pos in pos:
                    position_match = True
                    break
        
        # AI分析
        analysis = []
        if exp_level == "资深":
            analysis.append("经验丰富，可能over-qualified")
        elif exp_level == "匹配":
            analysis.append("经验匹配度良好")
        elif exp_level == "基本匹配":
            analysis.append("经验基本满足要求")
        else:
            analysis.append("经验不足，需要重点关注")
        
        if industry_match:
            analysis.append("行业经验匹配")
        else:
            analysis.append("行业经验可能不匹配")
        
        if position_match:
            analysis.append("有相关职位经验")
        else:
            analysis.append("缺乏相关职位经验")
        
        return {
            "experience_years": exp_years,
            "required_years": req_years,
            "experience_level": exp_level,
            "experience_score": exp_score,
            "industry_match": industry_match,
            "position_match": position_match,
            "analysis": analysis
        }
    
    def ai_culture_analysis(self, candidate: Dict, company_culture: Dict) -> Dict:
        """AI文化匹配分析"""
        logger.info("AI文化匹配分析...")
        
        # 文化维度匹配
        culture_dimensions = {
            "work_style": candidate.get("work_style", ""),
            "values": candidate.get("values", []),
            "preferred_environment": candidate.get("preferred_environment", "")
        }
        
        # 匹配度计算（模拟）
        match_scores = {}
        total_score = 0
        
        for dimension, candidate_value in culture_dimensions.items():
            if dimension in company_culture:
                company_value = company_culture[dimension]
                
                # 简单匹配逻辑
                if isinstance(candidate_value, list) and isinstance(company_value, list):
                    # 列表匹配
                    common = set(candidate_value) & set(company_value)
                    score = len(common) / max(len(company_value), 1) * 100
                elif candidate_value and company_value:
                    # 字符串匹配
                    if candidate_value in company_value or company_value in candidate_value:
                        score = 80
                    else:
                        score = 40
                else:
                    score = 50  # 默认分
                
                match_scores[dimension] = int(score)
                total_score += score * 0.33  # 三个维度平均
        
        culture_score = int(total_score)
        
        # AI分析
        analysis = []
        if culture_score >= 80:
            analysis.append("文化匹配度很高，容易融入团队")
        elif culture_score >= 60:
            analysis.append("文化基本匹配，需要适应期")
        elif culture_score >= 40:
            analysis.append("文化部分匹配，可能存在差异")
        else:
            analysis.append("文化匹配度较低，需要谨慎考虑")
        
        return {
            "culture_dimensions": culture_dimensions,
            "match_scores": match_scores,
            "culture_score": culture_score,
            "analysis": analysis
        }
    
    def ai_potential_prediction(self, candidate: Dict) -> Dict:
        """AI成长潜力预测"""
        logger.info("AI成长潜力预测...")
        
        # 潜力评估因素
        factors = {
            "learning_ability": random.randint(60, 95),  # 学习能力
            "adaptability": random.randint(60, 90),      # 适应能力
            "achievement_drive": random.randint(70, 95), # 成就动机
            "career_progression": 0,                     # 职业发展
            "skill_diversity": 0                         # 技能多样性
        }
        
        # 职业发展评估
        if "experience_years" in candidate:
            exp_years = candidate["experience_years"]
            if exp_years <= 3:
                factors["career_progression"] = 85  # 早期，发展空间大
            elif exp_years <= 8:
                factors["career_progression"] = 70  # 中期，稳定发展
            else:
                factors["career_progression"] = 60  # 资深，发展空间有限
        
        # 技能多样性评估
        if "skills" in candidate and isinstance(candidate["skills"], list):
            skill_count = len(candidate["skills"])
            if skill_count >= 8:
                factors["skill_diversity"] = 90
            elif skill_count >= 5:
                factors["skill_diversity"] = 75
            elif skill_count >= 3:
                factors["skill_diversity"] = 60
            else:
                factors["skill_diversity"] = 45
        
        # 计算潜力总分
        total_score = sum(factors.values()) / len(factors)
        potential_score = int(total_score)
        
        # 潜力等级
        if potential_score >= 85:
            potential_level = "高潜力"
            prediction = "未来2-3年可能成为核心骨干"
        elif potential_score >= 70:
            potential_level = "中等潜力"
            prediction = "有稳定发展潜力"
        elif potential_score >= 55:
            potential_level = "一般潜力"
            prediction = "需要更多培养"
        else:
            potential_level = "低潜力"
            prediction = "发展空间有限"
        
        # 发展建议
        suggestions = []
        if factors["learning_ability"] < 70:
            suggestions.append("建议加强学习能力培养")
        if factors["adaptability"] < 70:
            suggestions.append("建议提升适应能力")
        if factors["skill_diversity"] < 60:
            suggestions.append("建议拓展技能广度")
        
        return {
            "potential_factors": factors,
            "potential_score": potential_score,
            "potential_level": potential_level,
            "prediction": prediction,
            "suggestions": suggestions
        }
    
    def evaluate_candidate(self, candidate: Dict, jd_requirements: Dict, company_profile: Dict = None) -> Dict:
        """综合评估候选人"""
        logger.info(f"评估候选人: {candidate.get('name', '未知')}")
        
        evaluation_results = {
            "candidate_info": {
                "name": candidate.get("name", ""),
                "position": candidate.get("position", ""),
                "experience": candidate.get("experience", "")
            },
            "dimension_scores": {},
            "overall_score": 0,
            "recommendation": "",
            "detailed_analysis": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 1. 技术技能评估
        candidate_skills = candidate.get("skills", [])
        required_skills = jd_requirements.get("required_skills", [])
        
        skill_result = self.ai_skill_matching(candidate_skills, required_skills)
        evaluation_results["dimension_scores"]["technical_skills"] = skill_result["match_score"]
        evaluation_results["detailed_analysis"]["skills"] = skill_result
        
        # 2. 经验匹配评估
        candidate_exp = {
            "experience_years": candidate.get("experience_years", 0),
            "industry": candidate.get("industry", ""),
            "position_history": candidate.get("position_history", [])
        }
        
        exp_result = self.ai_experience_evaluation(candidate_exp, jd_requirements)
        evaluation_results["dimension_scores"]["experience_match"] = exp_result["experience_score"]
        evaluation_results["detailed_analysis"]["experience"] = exp_result
        
        # 3. 教育背景评估
        education_level = candidate.get("education_level", "本科")
        edu_scores = {"博士": 90, "硕士": 80, "本科": 70, "大专": 60, "中专": 50, "高中": 40}
        edu_score = edu_scores.get(education_level, 60)
        
        evaluation_results["dimension_scores"]["education_background"] = edu_score
        evaluation_results["detailed_analysis"]["education"] = {
            "level": education_level,
            "score": edu_score
        }
        
        # 4. 文化匹配评估
        if company_profile and "culture" in company_profile:
            culture_result = self.ai_culture_analysis(candidate, company_profile["culture"])
            evaluation_results["dimension_scores"]["culture_fit"] = culture_result["culture_score"]
            evaluation_results["detailed_analysis"]["culture"] = culture_result
        else:
            evaluation_results["dimension_scores"]["culture_fit"] = 70  # 默认分
        
        # 5. 成长潜力评估
        potential_result = self.ai_potential_prediction(candidate)
        evaluation_results["dimension_scores"]["growth_potential"] = potential_result["potential_score"]
        evaluation_results["detailed_analysis"]["potential"] = potential_result
        
        # 6. 薪资匹配评估
        candidate_salary = candidate.get("salary_min", 0)
        budget_range = jd_requirements.get("salary_budget", (0, 100))
        
        if candidate_salary == 0:
            salary_score = 70  # 薪资面议
        elif budget_range[0] <= candidate_salary <= budget_range[1]:
            salary_score = 90  # 在预算内
        elif candidate_salary < budget_range[0]:
            salary_score = 80  # 低于预算
        else:
            salary_score = 50  # 超出预算
        
        evaluation_results["dimension_scores"]["compensation_fit"] = salary_score
        
        # 计算总分
        total_score = 0
        for dimension, weight in self.evaluation_weights.items():
            if dimension in evaluation_results["dimension_scores"]:
                total_score += evaluation_results["dimension_scores"][dimension] * weight
        
        evaluation_results["overall_score"] = int(total_score)
        
        # 生成推荐
        if evaluation_results["overall_score"] >= 85:
            evaluation_results["recommendation"] = "强烈推荐"
            evaluation_results["priority"] = "高"
        elif evaluation_results["overall_score"] >= 70:
            evaluation_results["recommendation"] = "推荐"
            evaluation_results["priority"] = "中"
        elif evaluation_results["overall_score"] >= 55:
            evaluation_results["recommendation"] = "可考虑"
            evaluation_results["priority"] = "低"
        else:
            evaluation_results["recommendation"] = "不推荐"
            evaluation_results["priority"] = "淘汰"
        
        logger.info(f"评估完成: {candidate.get('name', '未知')} - 总分{evaluation_results['overall_score']}")
        return evaluation_results
    
    def evaluate_batch_candidates(self, candidates: List[Dict], jd_requirements: Dict, 
                                  company_profile: Dict = None) -> Dict:
        """批量评估候选人"""
        logger.info(f"批量评估 {len(candidates)} 个候选人")
        
        batch_results = {
            "total_candidates": len(candidates),
            "evaluated_candidates": 0,
            "candidate_evaluations": [],
            "summary_statistics": {},
            "ranking": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 逐个评估
        for candidate in candidates:
            evaluation = self.evaluate_candidate(candidate, jd_requirements, company_profile)
            batch_results["candidate_evaluations"].append(evaluation)
        
        batch_results["evaluated_candidates"] = len(candidates)
        
        # 生成统计摘要
        if candidates:
            scores = [e["overall_score"] for e in batch_results["candidate_evaluations"]]
            batch_results["summary_statistics"] = {
                "average_score": round(sum(scores) / len(scores), 1),
                "max_score": max(scores),
                "min_score": min(scores),
                "score_distribution": {
                    "优秀(85+)": len([s for s in scores if s >= 85]),
                    "良好(70-84)": len([s for s in scores if 70 <= s < 85]),
                    "一般(55-69)": len([s for s in scores if 55 <= s < 70]),
                    "较差(<55)": len([s for s in scores if s < 55])
                }
            }
            
            # 生成排名
            for i, (candidate, evaluation) in enumerate(zip(candidates, batch_results["candidate_evaluations"]), 1):
                batch_results["ranking"].append({
                    "rank": i,
                    "candidate_name": candidate.get("name", f"候选人{i}"),
                    "overall_score": evaluation["overall_score"],
                    "recommendation": evaluation["recommendation"]
                })
        
        logger.info(f"批量评估完成: {len(candidates)}个候选人")
        return batch_results
    
    def save_evaluation_results(self, results: Dict, filename: str = None):
        """保存评估结果"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"judge_results_{timestamp}.json"
        
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"评估结果保存到: {filepath}")
        return filepath

# 测试函数
def test_enhanced_judge():
    """测试增强版Judge Agent"""
    print("="*60)
    print("增强版Judge Agent测试")
    print("="*60)
    
    judge = EnhancedJudgeAgent()
    
    # 测试数据
    test_candidates = [
        {
            "name": "张明",
            "position": "投资经理",
            "experience_years": 6,
            "education_level": "硕士",
            "skills": ["财务分析", "尽职调查", "行业研究", "投资决策"],
            "industry": "私募股权",
            "salary_min": 50,
            "salary_max": 70
        },
        {
            "name": "李华",
            "position": "投资总监",
            "experience_years": 8,
            "education_level": "博士",
            "skills": ["私募基金", "并购重组", "团队管理"],
            "industry": "投资机构",
            "salary_min": 70,
            "salary_max": 90
        }
    ]
    
    jd_requirements = {
        "required_skills": ["财务分析", "尽职调查", "行业研究"],
        "min_experience": 5,
        "education_requirement": "硕士",
        "target_position": "投资经理",
        "industry": "私募股权",
        "salary_budget": (60, 100)
    }
    
    company_profile = {
        "culture": {
            "work_style": "结果导向",
            "values": ["专业", "诚信", "创新"],
            "preferred_environment": "创业氛围"
        }
    }
    
    # 1. 单候选人评估测试
    print("\n1. 单候选人评估测试:")
    single_result = judge.evaluate_candidate(test_candidates[0], jd_requirements, company_profile)
    print(f"候选人: {single_result['candidate_info']['name']}")
    print(f"总分: {single_result['overall_score']}")
    print(f"推荐: {single_result['recommendation']}")
    
    # 2. 批量评估测试
    print("\n2. 批量评估测试:")
    batch_result = judge.evaluate_batch_candidates(test_candidates, jd_requirements, company_profile)
    print(f"评估人数: {batch_result['total_candidates']}")
    print(f"平均分: {batch_result['summary_statistics']['average_score']}")
    
    # 3. 保存结果
    print("\n3. 保存评估结果:")
    saved_file = judge.save_evaluation_results(batch_result, "test_judge_results.json")
    print(f"结果保存到: {saved_file}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_enhanced_judge()