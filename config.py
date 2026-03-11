"""
JDdog-agent-LP 配置文件
"""

# 平台配置
PLATFORMS = {
    "猎聘": {
        "name": "猎聘",
        "keyword_separator": " ",  # 关键词分隔符
        "max_keyword_length": 50,  # 最大关键词长度
        "filters": {
            "city": {"type": "multi_select", "label": "期望城市"},
            "experience": {"type": "dropdown_custom", "label": "工作年限", 
                          "options": ["1-3年", "3-5年", "5-10年", "10年以上"]},
            "education": {"type": "multi_select", "label": "学历要求",
                         "options": ["大专", "本科", "硕士", "博士"]},
            "school_tier": {"type": "multi_select", "label": "院校要求",
                           "options": ["985", "211", "海外留学"]}
        }
    },
    "BOSS直聘": {
        "name": "BOSS直聘",
        "keyword_separator": " ",
        "max_keyword_length": 30,
        # ... 其他配置
    }
}

# 脑科学领域关键词扩展映射
BRAIN_SCIENCE_KEYWORDS = {
    "核心领域": ["脑科学", "神经科学", "认知科学", "神经工程"],
    "技术方向": ["脑机接口", "脑机融合", "神经接口", "脑电控制"],
    "疾病相关": ["脑疾病", "神经退行", "帕金森", "阿尔茨海默", "癫痫", "脑卒中"],
    "治疗方法": ["神经调控", "深部脑刺激", "神经刺激"],
    "检测技术": ["脑电图", "磁共振", "神经影像", "脑成像"],
    "交叉学科": ["计算神经", "人工智能 脑科学", "系统神经科学"]
}

# 投资相关关键词
INVESTMENT_KEYWORDS = [
    "投资", "投资经理", "投资总监", "基金投资", 
    "风险投资", "PE", "VC", "私募股权"
]

# 学历映射
EDUCATION_MAPPING = {
    "硕士及以上": ["硕士", "博士"],
    "本科及以上": ["本科", "硕士", "博士"],
    "博士": ["博士"]
}

# 院校映射
SCHOOL_TIER_MAPPING = {
    "985/211": ["985", "211"],
    "985/211/海外知名院校": ["985", "海外留学"],
    "海外知名院校": ["海外留学"]
}

# 经验年限计算规则
EXPERIENCE_RULES = {
    "严格": {"min_offset": 0, "max_offset": 2},   # 完全匹配或略高
    "适中": {"min_offset": -1, "max_offset": 3},  # 适当放宽
    "宽松": {"min_offset": -2, "max_offset": 5}   # 大幅放宽
}

# 默认配置
DEFAULT_PLATFORM = "猎聘"
DEFAULT_STRICT_LEVEL = "严格"  # 苛刻客户对应严格模式