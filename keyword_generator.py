"""
关键词生成器 - 生成25个脑科学相关搜索组合
"""

from typing import List, Dict
from config import BRAIN_SCIENCE_KEYWORDS, INVESTMENT_KEYWORDS


class KeywordGenerator:
    """关键词生成器"""
    
    def __init__(self, platform="猎聘"):
        self.platform = platform
        
    def generate_core_combinations(self, domain_keywords: List[str]) -> List[str]:
        """
        生成核心关键词组合（4个）
        规则：领域词 + 投资
        """
        core_domains = ["脑神经", "脑科学", "脑机接口", "神经科学"]
        
        # 使用传入的领域词或默认核心词
        domains_to_use = domain_keywords if domain_keywords else core_domains
        
        combinations = []
        for domain in domains_to_use[:4]:  # 最多取4个核心词
            combinations.append(f"{domain} 投资")
        
        return combinations
    
    def generate_expanded_combinations(self, domain_keywords: List[str]) -> List[str]:
        """
        生成扩展关键词组合（21个）
        脑科学相关概念 + 投资
        """
        expanded = []
        
        # 1. 脑科学所有相关领域
        all_domains = []
        for category, keywords in BRAIN_SCIENCE_KEYWORDS.items():
            all_domains.extend(keywords)
        
        # 去重并优先使用传入的领域词
        unique_domains = list(set(all_domains))
        if domain_keywords:
            # 将传入的领域词放在前面
            unique_domains = domain_keywords + [d for d in unique_domains if d not in domain_keywords]
        
        # 2. 投资相关词
        investment_words = INVESTMENT_KEYWORDS
        
        # 3. 生成组合（限制数量）
        count = 0
        for domain in unique_domains:
            if count >= 21:  # 总共21个扩展组合
                break
                
            for invest in investment_words[:3]:  # 每个领域词配前3个投资词
                combination = f"{domain} {invest}"
                
                # 平台特定格式
                if self.platform == "猎聘":
                    combination = combination.replace("+", " ")  # 猎聘用空格
                
                if combination not in expanded:
                    expanded.append(combination)
                    count += 1
                    
                    if count >= 21:
                        break
        
        return expanded
    
    def generate_position_combinations(self, position_title: str) -> List[str]:
        """
        生成职位相关组合
        """
        position_combinations = []
        
        # 从职位标题提取关键词
        title_keywords = []
        if "投资经理" in position_title:
            title_keywords.append("投资经理")
        if "投资总监" in position_title:
            title_keywords.append("投资总监")
        if "基金" in position_title:
            title_keywords.append("基金")
        
        # 脑科学领域词
        brain_domains = BRAIN_SCIENCE_KEYWORDS["核心领域"]
        
        # 生成组合
        for domain in brain_domains[:3]:  # 前3个核心领域
            for title in title_keywords[:2]:  # 前2个职位词
                combination = f"{domain} {title}"
                if combination not in position_combinations:
                    position_combinations.append(combination)
        
        return position_combinations
    
    def generate_all_combinations(self, parsed_jd: Dict) -> Dict[str, List[str]]:
        """
        生成所有关键词组合（去重）
        返回：{
            "core": 核心组合（4个）,
            "expanded": 扩展组合（21个）,
            "position": 职位组合（可选）,
            "all": 所有组合（25+个，去重）
        }
        """
        domain_keywords = parsed_jd.get("domain_keywords", [])
        position_title = parsed_jd.get("position_title", "")
        
        # 1. 核心组合
        core = self.generate_core_combinations(domain_keywords)
        
        # 2. 扩展组合
        expanded = self.generate_expanded_combinations(domain_keywords)
        
        # 3. 职位组合
        position = self.generate_position_combinations(position_title)
        
        # 4. 所有组合（去重）
        all_combinations = []
        seen = set()
        
        for combo_list in [core, expanded, position]:
            for combo in combo_list:
                if combo not in seen:
                    seen.add(combo)
                    all_combinations.append(combo)
        
        # 确保不低于25个组合
        if len(all_combinations) < 25:
            all_combinations = self._ensure_minimum_combinations(all_combinations, 25)
        
        return {
            "core": core,
            "expanded": expanded,
            "position": position,
            "all": all_combinations,
            "total_count": len(all_combinations)
        }
    
    def _ensure_minimum_combinations(self, combinations: List[str], minimum: int) -> List[str]:
        """确保不低于指定数量的组合"""
        if len(combinations) >= minimum:
            return combinations
        
        from config import BRAIN_SCIENCE_KEYWORDS, INVESTMENT_KEYWORDS
        
        result = combinations.copy()
        seen = set(combinations)
        
        # 补充组合
        for category in ["技术方向", "疾病相关", "治疗方法", "检测技术", "交叉学科"]:
            if len(result) >= minimum:
                break
                
            domains = BRAIN_SCIENCE_KEYWORDS.get(category, [])
            for domain in domains:
                if len(result) >= minimum:
                    break
                    
                for invest in INVESTMENT_KEYWORDS:
                    combo = f"{domain} {invest}"
                    if combo not in seen:
                        seen.add(combo)
                        result.append(combo)
                        
                        if len(result) >= minimum:
                            break
        
        return result
    
    def get_search_strategy(self, combinations: Dict) -> List[Dict]:
        """
        生成搜索执行策略
        一天内完成所有关键词搜索
        """
        all_combos = combinations["all"]
        
        # 确保不低于25个组合
        if len(all_combos) < 25:
            # 补充到25个
            additional = 25 - len(all_combos)
            # 使用扩展组合补充
            from config import BRAIN_SCIENCE_KEYWORDS, INVESTMENT_KEYWORDS
            for category in ["技术方向", "疾病相关", "治疗方法"]:
                if additional <= 0:
                    break
                for domain in BRAIN_SCIENCE_KEYWORDS.get(category, []):
                    if additional <= 0:
                        break
                    for invest in INVESTMENT_KEYWORDS[:2]:
                        combo = f"{domain} {invest}"
                        if combo not in all_combos:
                            all_combos.append(combo)
                            additional -= 1
                            if additional <= 0:
                                break
        
        # 单日完成所有搜索
        strategy = [{
            "day": "当天完成",
            "keywords": all_combos,
            "count": len(all_combos),
            "note": f"总计{len(all_combos)}个关键词组合，一天内全部搜索完成"
        }]
        
        return strategy


# 使用示例
if __name__ == "__main__":
    generator = KeywordGenerator(platform="猎聘")
    
    # 模拟解析结果
    test_parsed_jd = {
        "position_title": "医健基金高级投资经理/投资总监 -（脑/神经科学）",
        "domain_keywords": ["脑科学", "神经科学"],
        "experience_years": (5, 10),
        "education": "硕士及以上",
        "school_tier": "985/海外知名院校",
        "location": "上海",
        "skills": ["投资", "基金", "尽职调查"]
    }
    
    # 生成所有组合
    combinations = generator.generate_all_combinations(test_parsed_jd)
    
    print("核心组合（4个）:")
    for kw in combinations["core"]:
        print(f"  - {kw}")
    
    print(f"\n扩展组合（{len(combinations['expanded'])}个）:")
    for i, kw in enumerate(combinations["expanded"][:5], 1):  # 显示前5个
        print(f"  {i}. {kw}")
    print(f"  ... 还有{len(combinations['expanded'])-5}个")
    
    print(f"\n职位组合（{len(combinations['position'])}个）:")
    for kw in combinations["position"]:
        print(f"  - {kw}")
    
    print(f"\n总计: {combinations['total_count']}个关键词组合")
    
    # 搜索策略
    strategy = generator.get_search_strategy(combinations)
    print(f"\n搜索执行策略（{len(strategy)}天）:")
    for day_plan in strategy[:3]:  # 显示前3天
        print(f"{day_plan['day']}: {', '.join(day_plan['keywords'])}")