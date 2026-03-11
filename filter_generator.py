"""
筛选条件生成器 - 生成猎聘平台筛选条件
"""

from typing import Dict, List, Any
from config import EDUCATION_MAPPING, SCHOOL_TIER_MAPPING, EXPERIENCE_RULES


class FilterGenerator:
    """筛选条件生成器"""
    
    def __init__(self, platform="猎聘", strict_level="严格"):
        self.platform = platform
        self.strict_level = strict_level
    
    def generate_filters(self, parsed_jd: Dict, supplement: str = "") -> Dict[str, Any]:
        """
        生成筛选条件
        """
        filters = {}
        
        # 1. 城市筛选
        city = self._generate_city_filter(parsed_jd, supplement)
        if city:
            filters["city"] = city
        
        # 2. 工作年限
        experience = self._generate_experience_filter(parsed_jd, supplement)
        if experience:
            filters["experience"] = experience
        
        # 3. 学历要求
        education = self._generate_education_filter(parsed_jd, supplement)
        if education:
            filters["education"] = education
        
        # 4. 院校要求
        school_tier = self._generate_school_filter(parsed_jd, supplement)
        if school_tier:
            filters["school_tier"] = school_tier
        
        # 5. 其他条件（根据补充说明）
        other_filters = self._generate_other_filters(parsed_jd, supplement)
        if other_filters:
            filters.update(other_filters)
        
        return filters
    
    def _generate_city_filter(self, parsed_jd: Dict, supplement: str) -> List[str]:
        """生成城市筛选条件"""
        location = parsed_jd.get("location", "")
        
        if not location:
            return []
        
        # 检查补充说明是否有城市相关指示
        if "不选" in supplement or "放宽" in supplement:
            # 苛刻客户可能希望不限制城市
            return []
        
        return [location]
    
    def _generate_experience_filter(self, parsed_jd: Dict, supplement: str) -> str:
        """生成工作年限筛选条件"""
        experience_years = parsed_jd.get("experience_years")
        
        if not experience_years:
            return ""
        
        min_exp, max_exp = experience_years
        
        # 根据严格级别调整
        rules = EXPERIENCE_RULES.get(self.strict_level, EXPERIENCE_RULES["严格"])
        min_offset = rules["min_offset"]
        max_offset = rules["max_offset"]
        
        # 计算最终范围
        final_min = max(1, min_exp + min_offset)
        final_max = max_exp + max_offset
        
        # 补充说明处理
        if "放宽" in supplement:
            final_min = max(1, final_min - 1)
            final_max = final_max + 1
        
        # 猎聘平台格式
        if self.platform == "猎聘":
            # 检查是否匹配预设选项
            preset_options = {
                "1-3年": (1, 3),
                "3-5年": (3, 5),
                "5-10年": (5, 10),
                "10年以上": (10, 99)
            }
            
            for option, (opt_min, opt_max) in preset_options.items():
                if final_min >= opt_min and final_max <= opt_max:
                    return option
            
            # 不匹配预设选项，使用自定义输入
            return f"{final_min}-{final_max}年"
        
        return f"{final_min}-{final_max}年"
    
    def _generate_education_filter(self, parsed_jd: Dict, supplement: str) -> List[str]:
        """生成学历筛选条件"""
        education = parsed_jd.get("education", "")
        
        if not education:
            return []
        
        # 映射到平台选项
        platform_options = EDUCATION_MAPPING.get(education, [])
        
        if not platform_options:
            # 默认处理
            if "硕士及以上" in education or "硕士" in education:
                platform_options = ["硕士", "博士"]
            elif "本科及以上" in education or "本科" in education:
                platform_options = ["本科", "硕士", "博士"]
            elif "博士" in education:
                platform_options = ["博士"]
        
        # 补充说明处理
        if "苛刻" in supplement:
            # 苛刻客户：只选最高学历
            if "博士" in platform_options:
                return ["博士"]
            elif "硕士" in platform_options:
                return ["硕士"]
        
        return platform_options
    
    def _generate_school_filter(self, parsed_jd: Dict, supplement: str) -> List[str]:
        """生成院校筛选条件"""
        school_tier = parsed_jd.get("school_tier", "")
        
        if not school_tier:
            return []
        
        # 映射到平台选项
        platform_options = SCHOOL_TIER_MAPPING.get(school_tier, [])
        
        if not platform_options:
            # 解析学校要求
            if "985" in school_tier and "海外" in school_tier:
                platform_options = ["985", "海外留学"]
            elif "985" in school_tier:
                platform_options = ["985"]
            elif "211" in school_tier:
                platform_options = ["211"]
            elif "海外" in school_tier:
                platform_options = ["海外留学"]
        
        # 补充说明处理
        if "苛刻" in supplement:
            # 苛刻客户：只选最高要求
            if "985" in platform_options and "海外留学" in platform_options:
                return ["985"]  # 或 ["海外留学"]，根据偏好
        
        return platform_options
    
    def _generate_other_filters(self, parsed_jd: Dict, supplement: str) -> Dict[str, Any]:
        """生成其他筛选条件"""
        other_filters = {}
        
        # 年龄筛选（仅当JD明确要求时）
        age_requirement = self._extract_age_requirement(parsed_jd)
        if age_requirement:
            other_filters["age_range"] = age_requirement
        
        # 薪资范围（通常不设置，避免过滤高薪候选人）
        # 除非补充说明明确要求
        
        # 公司性质（通常不设置，投资机构类型多样）
        
        return other_filters
    
    def _extract_age_requirement(self, parsed_jd: Dict) -> str:
        """提取年龄要求（仅当JD明确要求时）"""
        # 在实际实现中，需要从JD文本中提取年龄要求
        # 这里简化为空
        return ""
    
    def get_filter_instructions(self, filters: Dict) -> List[str]:
        """获取筛选条件操作说明"""
        instructions = []
        
        if "city" in filters:
            cities = filters["city"]
            if cities:
                instructions.append(f"期望城市: 选择 {', '.join(cities)}")
            else:
                instructions.append("期望城市: 不选择（放宽地域限制）")
        
        if "experience" in filters:
            exp = filters["experience"]
            if exp in ["1-3年", "3-5年", "5-10年", "10年以上"]:
                instructions.append(f"工作年限: 选择 '{exp}'")
            else:
                instructions.append(f"工作年限: 自定义输入 '{exp}'")
        
        if "education" in filters:
            edu = filters["education"]
            instructions.append(f"学历要求: 选择 {', '.join(edu)}")
        
        if "school_tier" in filters:
            schools = filters["school_tier"]
            instructions.append(f"院校要求: 选择 {', '.join(schools)}")
        
        # 不选择的项目
        instructions.append("不选择: 年龄、性别、婚姻状况（JD无明确要求）")
        instructions.append("不选择: 薪资范围（避免过滤高薪候选人）")
        instructions.append("不选择: 公司性质（投资机构类型多样）")
        
        return instructions


# 使用示例
if __name__ == "__main__":
    generator = FilterGenerator(platform="猎聘", strict_level="严格")
    
    test_parsed_jd = {
        "position_title": "医健基金高级投资经理/投资总监 -（脑/神经科学）",
        "domain_keywords": ["脑科学", "神经科学"],
        "experience_years": (5, 10),
        "education": "硕士及以上",
        "school_tier": "985/海外知名院校",
        "location": "上海",
        "skills": ["投资", "基金", "尽职调查"]
    }
    
    test_supplement = "苛刻客户"
    
    # 生成筛选条件
    filters = generator.generate_filters(test_parsed_jd, test_supplement)
    
    print("生成的筛选条件:")
    for key, value in filters.items():
        print(f"{key}: {value}")
    
    print("\n操作说明:")
    instructions = generator.get_filter_instructions(filters)
    for instr in instructions:
        print(f"- {instr}")