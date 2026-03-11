"""
JD解析模块 - 使用规则+大模型解析职位描述
"""

import re
from typing import Dict, List, Tuple, Optional


class JDParser:
    """职位描述解析器"""
    
    def __init__(self):
        # 预定义规则
        self.education_patterns = {
            "博士": r"博士|PhD|phd",
            "硕士": r"硕士|研究生|master",
            "本科": r"本科|学士|bachelor",
            "大专": r"大专|专科"
        }
        
        self.experience_patterns = {
            r"(\d+)[-~](\d+)年": lambda m: (int(m.group(1)), int(m.group(2))),
            r"(\d+)年以上": lambda m: (int(m.group(1)), int(m.group(1)) + 5),
            r"(\d+)年以下": lambda m: (1, int(m.group(1))),
            r"(\d+)年": lambda m: (int(m.group(1)), int(m.group(1)) + 2)
        }
        
        self.location_patterns = {
            "上海": r"上海|上海市|shanghai",
            "北京": r"北京|北京市|beijing",
            "深圳": r"深圳|深圳市|shenzhen",
            "广州": r"广州|广州市|guangzhou"
        }
        
        self.school_tier_patterns = {
            "985": r"985|九八五",
            "211": r"211|二一一",
            "海外留学": r"海外|留学|国外|境外|海内外"
        }
    
    def parse_with_rules(self, jd_text: str) -> Dict:
        """使用规则解析JD"""
        result = {
            "position_title": "",
            "domain_keywords": [],
            "experience_years": None,
            "education": "",
            "school_tier": "",
            "location": "",
            "skills": [],
            "requirements": []
        }
        
        # 1. 提取职位标题（第一行）
        lines = jd_text.strip().split('\n')
        if lines:
            result["position_title"] = lines[0].strip()
        
        # 2. 提取领域关键词
        result["domain_keywords"] = self._extract_domain_keywords(jd_text)
        
        # 3. 提取工作经验
        result["experience_years"] = self._extract_experience(jd_text)
        
        # 4. 提取学历要求
        result["education"] = self._extract_education(jd_text)
        
        # 5. 提取院校要求
        result["school_tier"] = self._extract_school_tier(jd_text)
        
        # 6. 提取工作地点
        result["location"] = self._extract_location(jd_text)
        
        # 7. 提取技能关键词
        result["skills"] = self._extract_skills(jd_text)
        
        return result
    
    def _extract_domain_keywords(self, text: str) -> List[str]:
        """提取领域关键词"""
        # 脑科学相关关键词检测
        brain_keywords = []
        brain_patterns = [
            r"脑科学", r"神经科学", r"认知科学", r"神经工程",
            r"脑机接口", r"脑神经", r"神经调控", r"脑疾病"
        ]
        
        for pattern in brain_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                keyword = re.search(pattern, text, re.IGNORECASE).group()
                if keyword not in brain_keywords:
                    brain_keywords.append(keyword)
        
        return brain_keywords
    
    def _extract_experience(self, text: str) -> Optional[Tuple[int, int]]:
        """提取工作经验要求"""
        for pattern, handler in self.experience_patterns.items():
            match = re.search(pattern, text)
            if match:
                return handler(match)
        return None
    
    def _extract_education(self, text: str) -> str:
        """提取学历要求"""
        # 按优先级检查
        for level in ["博士", "硕士", "本科", "大专"]:
            if re.search(self.education_patterns[level], text, re.IGNORECASE):
                # 检查是否有"及以上"修饰
                if re.search(rf"{level}及以上|{level}以上", text):
                    return f"{level}及以上"
                return level
        return ""
    
    def _extract_school_tier(self, text: str) -> str:
        """提取院校要求"""
        tiers_found = []
        for tier, pattern in self.school_tier_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                tiers_found.append(tier)
        
        if not tiers_found:
            return ""
        
        # 组合描述
        if "985" in tiers_found and "海外留学" in tiers_found:
            return "985/海外知名院校"
        elif "985" in tiers_found and "211" in tiers_found:
            return "985/211"
        elif "海外留学" in tiers_found:
            return "海外知名院校"
        elif "985" in tiers_found:
            return "985"
        elif "211" in tiers_found:
            return "211"
        
        return ""
    
    def _extract_location(self, text: str) -> str:
        """提取工作地点"""
        for city, pattern in self.location_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return city
        return ""
    
    def _extract_skills(self, text: str) -> List[str]:
        """提取技能关键词"""
        skills = []
        skill_patterns = [
            r"投资", r"基金", r"PE", r"VC", r"尽职调查",
            r"估值", r"财务分析", r"项目管理", r"退出方案"
        ]
        
        for pattern in skill_patterns:
            if re.search(pattern, text):
                skills.append(pattern)
        
        return skills
    
    def parse_with_llm(self, jd_text: str) -> Dict:
        """
        使用大模型解析JD（待实现）
        可集成DeepSeek/GLM等API
        """
        # 这里可以调用大模型API进行更智能的解析
        # 暂时返回规则解析结果
        return self.parse_with_rules(jd_text)


# 使用示例
if __name__ == "__main__":
    parser = JDParser()
    
    test_jd = """医健基金高级投资经理/投资总监 -（脑/神经科学）
岗位职责：
1. 在相关领域内对细分行业赛道开展系统性分析研究，输出投资逻辑和观点；
2. 协助团队领导/独立进行项目投资，完成交易结构设计、财务分析、尽职调查、估值及回报分析等；
3. 协助团队领导/独立进行已投项目管理，对已投资的项目进行定期分析、评估、管理，协助设计退出方案等；
4. 协助团队领导完成公司安排的其他工作。
任职要求：
1. 985/211/其他海内外知名院校，硕士及以上学历，具有生物医学工程、脑科学、神经科学等相关专业背景（必备条件）；
2. 5年以上医疗健康产业及投资领域工作经验，其中3年以上PE/VC投资经验，在脑科学/神经科学的器械领域有丰富经验；
3. 对一级市场有热情，性格开朗、为人真诚、自驱力强；
4. 具有优秀的沟通能力、执行能力、团队协作能力、学习能力，能承受一定的工作压力。
工作地点：上海。"""
    
    result = parser.parse_with_rules(test_jd)
    print("解析结果:")
    for key, value in result.items():
        print(f"{key}: {value}")