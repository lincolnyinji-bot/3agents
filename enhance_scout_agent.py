#!/usr/bin/env python3
"""
增强Scout Agent - 完善搜索策略和简历解析
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class EnhancedScoutAgent:
    """增强版Scout Agent - 完善搜索逻辑"""
    
    def __init__(self):
        self.work_dir = Path("C:/Users/宗璐/.openclaw/workspace/3agents")
        self.data_dir = self.work_dir / "enhanced_scout_data"
        self.data_dir.mkdir(exist_ok=True)
        
        # 搜索策略配置
        self.search_strategies = {
            "strict": {
                "experience_min": 5,
                "education_level": "本科",
                "location_match": True,
                "skill_match_threshold": 0.8
            },
            "loose": {
                "experience_min": 3,
                "education_level": "大专",
                "location_match": False,
                "skill_match_threshold": 0.5
            }
        }
        
        # 简历解析规则
        self.resume_parsing_rules = {
            "experience_patterns": [
                r"(\d+)[年|年多|年以上]",
                r"工作经验.*?(\d+)年",
                r"(\d+).*?年经验"
            ],
            "education_patterns": [
                "本科", "硕士", "博士", "大专", "中专"
            ],
            "skill_keywords": {
                "投资": ["投资", "股权", "私募", "基金", "融资"],
                "金融": ["金融", "财务", "会计", "审计", "风控"],
                "技术": ["Python", "Java", "数据分析", "AI", "机器学习"]
            }
        }
    
    def parse_jd_to_strategy(self, jd_text: str, client_info: Dict) -> Dict:
        """解析JD生成搜索策略"""
        logger.info("解析JD生成搜索策略...")
        
        strategy = {
            "keywords": [],
            "filters": {},
            "sort_by": "relevance",
            "max_results": 100,
            "screening_type": "strict"
        }
        
        # 关键词提取
        jd_lower = jd_text.lower()
        
        # 职位关键词
        position_keywords = ["投资经理", "投资总监", "投资分析师", "基金经理", "投资顾问"]
        for keyword in position_keywords:
            if keyword in jd_lower:
                strategy["keywords"].append(keyword)
                break
        
        # 行业关键词
        industry_keywords = ["私募", "股权", "金融", "投资", "基金"]
        for keyword in industry_keywords:
            if keyword in jd_lower:
                strategy["keywords"].append(keyword)
        
        # 技能关键词
        skill_keywords = ["财务分析", "尽职调查", "行业研究", "投资决策", "投后管理"]
        for keyword in skill_keywords:
            if keyword in jd_lower:
                strategy["keywords"].append(keyword)
        
        # 筛选条件
        if "5年" in jd_text or "五年" in jd_text:
            strategy["filters"]["experience"] = "5年以上"
        elif "3年" in jd_text or "三年" in jd_text:
            strategy["filters"]["experience"] = "3年以上"
        
        if "本科" in jd_text:
            strategy["filters"]["education"] = "本科以上"
        elif "硕士" in jd_text:
            strategy["filters"]["education"] = "硕士以上"
        
        # 客户信息整合
        if "location" in client_info:
            strategy["filters"]["location"] = client_info["location"]
        
        if "industry" in client_info:
            strategy["keywords"].append(client_info["industry"])
        
        # 去重
        strategy["keywords"] = list(set(strategy["keywords"]))
        
        logger.info(f"生成的搜索策略: {strategy}")
        return strategy
    
    def simulate_search_results(self, strategy: Dict) -> List[Dict]:
        """模拟搜索结果（实际对接猎聘前）"""
        logger.info(f"模拟搜索: {strategy['keywords']}")
        
        # 模拟简历数据
        mock_resumes = [
            {
                "id": "resume_001",
                "name": "张明",
                "position": "投资经理",
                "company": "某知名私募基金",
                "experience": "6年",
                "education": "硕士",
                "location": "深圳",
                "skills": ["股权投资", "财务分析", "行业研究", "尽职调查"],
                "salary": "40-60万",
                "status": "在职看机会"
            },
            {
                "id": "resume_002",
                "name": "李华",
                "position": "投资总监",
                "company": "某大型投资机构",
                "experience": "8年",
                "education": "博士",
                "location": "北京",
                "skills": ["私募基金", "并购重组", "投后管理", "团队管理"],
                "salary": "60-80万",
                "status": "在职看机会"
            },
            {
                "id": "resume_003",
                "name": "王强",
                "position": "投资分析师",
                "company": "某证券公司",
                "experience": "4年",
                "education": "本科",
                "location": "上海",
                "skills": ["行业研究", "财务建模", "数据分析", "报告撰写"],
                "salary": "30-40万",
                "status": "在职看机会"
            },
            {
                "id": "resume_004",
                "name": "赵敏",
                "position": "基金经理",
                "company": "某公募基金",
                "experience": "7年",
                "education": "硕士",
                "location": "深圳",
                "skills": ["资产配置", "风险控制", "投资组合", "市场分析"],
                "salary": "50-70万",
                "status": "在职看机会"
            },
            {
                "id": "resume_005",
                "name": "刘伟",
                "position": "投资顾问",
                "company": "某财富管理公司",
                "experience": "5年",
                "education": "本科",
                "location": "广州",
                "skills": ["客户关系", "产品推荐", "资产规划", "风险管理"],
                "salary": "35-45万",
                "status": "在职看机会"
            }
        ]
        
        # 根据策略筛选
        filtered_resumes = []
        for resume in mock_resumes:
            # 地点筛选
            if "location" in strategy["filters"]:
                if resume["location"] != strategy["filters"]["location"]:
                    continue
            
            # 经验筛选
            if "experience" in strategy["filters"]:
                exp_years = int(resume["experience"].replace("年", ""))
                if exp_years < 5 and strategy["filters"]["experience"] == "5年以上":
                    continue
            
            # 关键词匹配
            keyword_match = False
            for keyword in strategy["keywords"]:
                if (keyword in resume["position"] or 
                    keyword in " ".join(resume["skills"]) or
                    keyword in resume["company"]):
                    keyword_match = True
                    break
            
            if keyword_match:
                filtered_resumes.append(resume)
        
        logger.info(f"模拟搜索到 {len(filtered_resumes)} 份简历")
        return filtered_resumes
    
    def screen_resumes(self, resumes: List[Dict], screening_type: str = "strict") -> Dict:
        """筛选简历（严格/宽松）"""
        logger.info(f"执行{screening_type}筛选...")
        
        strategy = self.search_strategies[screening_type]
        passed = []
        rejected = []
        need_detail = []
        
        for resume in resumes:
            score = 0
            reasons = []
            
            # 经验评分
            exp_years = int(resume["experience"].replace("年", ""))
            if exp_years >= strategy["experience_min"]:
                score += 30
            else:
                reasons.append(f"经验不足{strategy['experience_min']}年")
            
            # 教育评分
            education_map = {"博士": 40, "硕士": 30, "本科": 20, "大专": 10, "中专": 0}
            edu_score = education_map.get(resume["education"], 0)
            score += edu_score
            
            # 技能匹配度
            skill_match = 0
            for skill in resume["skills"]:
                for category, keywords in self.resume_parsing_rules["skill_keywords"].items():
                    if any(keyword in skill for keyword in keywords):
                        skill_match += 1
            
            skill_ratio = skill_match / max(len(resume["skills"]), 1)
            if skill_ratio >= strategy["skill_match_threshold"]:
                score += 30
            else:
                reasons.append(f"技能匹配度不足{strategy['skill_match_threshold']*100}%")
            
            # 分类
            if score >= 70:
                passed.append({
                    **resume,
                    "screening_score": score,
                    "screening_reasons": ["通过筛选"]
                })
            elif score >= 50:
                need_detail.append({
                    **resume,
                    "screening_score": score,
                    "screening_reasons": ["需要详细评估"]
                })
            else:
                rejected.append({
                    **resume,
                    "screening_score": score,
                    "screening_reasons": reasons
                })
        
        result = {
            "screening_type": screening_type,
            "total_resumes": len(resumes),
            "passed": passed,
            "need_detail": need_detail,
            "rejected": rejected,
            "pass_rate": len(passed) / max(len(resumes), 1)
        }
        
        logger.info(f"筛选结果: 通过{len(passed)}个, 待评估{len(need_detail)}个, 拒绝{len(rejected)}个")
        return result
    
    def save_search_results(self, results: Dict, filename: str = None):
        """保存搜索结果"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scout_results_{timestamp}.json"
        
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果保存到: {filepath}")
        return filepath

# 测试函数
def test_enhanced_scout():
    """测试增强版Scout Agent"""
    print("="*60)
    print("增强版Scout Agent测试")
    print("="*60)
    
    scout = EnhancedScoutAgent()
    
    # 测试数据
    jd_text = """
    职位：投资经理
    要求：5年以上投资经验，本科以上学历
    职责：负责私募股权投资，进行尽职调查和投后管理
    """
    
    client_info = {
        "location": "深圳",
        "industry": "私募股权",
        "company_size": "中型"
    }
    
    # 1. 解析JD生成策略
    strategy = scout.parse_jd_to_strategy(jd_text, client_info)
    
    # 2. 模拟搜索
    resumes = scout.simulate_search_results(strategy)
    
    # 3. 严格筛选
    strict_results = scout.screen_resumes(resumes, "strict")
    
    # 4. 宽松筛选
    loose_results = scout.screen_resumes(resumes, "loose")
    
    # 5. 保存结果
    scout.save_search_results({
        "strategy": strategy,
        "raw_resumes": resumes,
        "strict_screening": strict_results,
        "loose_screening": loose_results,
        "timestamp": datetime.now().isoformat()
    }, "test_scout_results.json")
    
    print("\n测试完成!")
    print(f"原始简历: {len(resumes)}份")
    print(f"严格筛选通过: {len(strict_results['passed'])}份")
    print(f"宽松筛选通过: {len(loose_results['passed'])}份")

if __name__ == "__main__":
    test_enhanced_scout()