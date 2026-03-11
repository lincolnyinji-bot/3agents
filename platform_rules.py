"""
平台规则库 - 猎聘平台详细规则
"""

class LiepinRules:
    """猎聘平台规则"""
    
    @staticmethod
    def generate_keywords(domain_keywords, position_keywords):
        """
        生成猎聘平台关键词组合
        规则：领域词 + 空格 + 职位词
        """
        keywords = []
        
        # 核心组合：每个领域词与每个投资词组合
        for domain in domain_keywords:
            for invest in position_keywords:
                keyword = f"{domain} {invest}"
                if len(keyword) <= 50:  # 猎聘关键词长度限制
                    keywords.append(keyword)
        
        return keywords
    
    @staticmethod
    def apply_filters(parsed_jd, strict_level="严格"):
        """
        应用猎聘筛选条件
        """
        filters = {}
        
        # 1. 城市筛选
        if parsed_jd.get("location"):
            filters["city"] = [parsed_jd["location"]]
        
        # 2. 工作年限
        exp_years = parsed_jd.get("experience_years")
        if exp_years:
            min_exp, max_exp = exp_years
            # 根据严格级别调整
            if strict_level == "严格":
                filters["experience"] = f"{min_exp}-{max_exp+2}年"
            elif strict_level == "适中":
                filters["experience"] = f"{max(1, min_exp-1)}-{max_exp+3}年"
            else:  # 宽松
                filters["experience"] = f"{max(1, min_exp-2)}-{max_exp+5}年"
        
        # 3. 学历要求
        education = parsed_jd.get("education")
        if education:
            from config import EDUCATION_MAPPING
            filters["education"] = EDUCATION_MAPPING.get(education, ["硕士", "博士"])
        
        # 4. 院校要求
        school_tier = parsed_jd.get("school_tier")
        if school_tier:
            from config import SCHOOL_TIER_MAPPING
            filters["school_tier"] = SCHOOL_TIER_MAPPING.get(school_tier, ["985", "海外留学"])
        
        return filters
    
    @staticmethod
    def get_platform_notes():
        """
        猎聘平台注意事项
        """
        return [
            "关键词用空格分隔，例如：'脑科学 投资'",
            "工作年限可自定义输入，例如：'3-10年'",
            "学历和院校可多选，建议同时选择",
            "不要选择年龄、性别等JD未明确要求的条件",
            "保存搜索条件便于每天执行"
        ]


class BossRules:
    """BOSS直聘平台规则"""
    
    @staticmethod
    def generate_keywords(domain_keywords, position_keywords):
        """
        BOSS直聘关键词更简洁
        """
        keywords = []
        for domain in domain_keywords[:3]:  # BOSS只取前3个核心词
            for invest in ["投资", "投资经理"]:  # BOSS偏好简洁
                keywords.append(f"{domain}{invest}")
        return keywords
    
    @staticmethod
    def apply_filters(parsed_jd, strict_level="严格"):
        """BOSS直聘筛选条件"""
        # BOSS平台特有规则
        filters = {}
        # ... 具体实现
        return filters


# 平台规则映射
PLATFORM_RULES = {
    "猎聘": LiepinRules,
    "BOSS直聘": BossRules,
    # 其他平台...
}


def get_platform_rules(platform_name):
    """获取平台规则类"""
    return PLATFORM_RULES.get(platform_name, LiepinRules)