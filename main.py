"""
JDdog-agent-LP 主程序
"""

import json
from typing import Dict, Any
from jd_parser import JDParser
from keyword_generator import KeywordGenerator
from filter_generator import FilterGenerator
from platform_rules import get_platform_rules


class JDDogAgent:
    """JDdog-agent-LP 主类"""
    
    def __init__(self, platform="猎聘", strict_level="严格"):
        self.platform = platform
        self.strict_level = strict_level
        
        # 初始化组件
        self.parser = JDParser()
        self.keyword_gen = KeywordGenerator(platform)
        self.filter_gen = FilterGenerator(platform, strict_level)
        self.platform_rules = get_platform_rules(platform)
    
    def generate_search_conditions(self, jd_text: str, supplement: str = "") -> Dict[str, Any]:
        """
        生成搜索条件
        输入: JD文本, 补充说明
        输出: 搜索关键词和筛选条件
        """
        # 1. 解析JD
        print("步骤1: 解析JD...")
        parsed_jd = self.parser.parse_with_rules(jd_text)
        
        # 2. 生成关键词
        print("步骤2: 生成搜索关键词...")
        keyword_result = self.keyword_gen.generate_all_combinations(parsed_jd)
        
        # 3. 生成筛选条件
        print("步骤3: 生成筛选条件...")
        filters = self.filter_gen.generate_filters(parsed_jd, supplement)
        
        # 4. 平台注意事项
        print("步骤4: 生成平台注意事项...")
        platform_notes = self.platform_rules.get_platform_notes()
        
        # 5. 搜索策略
        print("步骤5: 生成搜索策略...")
        search_strategy = self.keyword_gen.get_search_strategy(keyword_result)
        
        # 6. 操作说明
        filter_instructions = self.filter_gen.get_filter_instructions(filters)
        
        # 构建最终结果
        result = {
            "input": {
                "jd_preview": jd_text[:100] + "..." if len(jd_text) > 100 else jd_text,
                "supplement": supplement,
                "platform": self.platform,
                "strict_level": self.strict_level
            },
            "parsed_jd": parsed_jd,
            "search_keywords": {
                "core": keyword_result["core"],
                "expanded": keyword_result["expanded"],
                "position": keyword_result["position"],
                "all": keyword_result["all"],
                "total_count": keyword_result["total_count"]
            },
            "filters": filters,
            "execution": {
                "search_strategy": search_strategy,
                "execution_mode": "单日完成",
                "keywords_count": len(keyword_result["all"]),
                "minimum_required": 25,
                "meets_requirement": len(keyword_result["all"]) >= 25
            },
            "instructions": {
                "filter_operations": filter_instructions,
                "platform_notes": platform_notes,
                "quality_focus": [
                    "不以候选人数量评判关键词效果",
                    "关注初筛通过率而非搜索结果数",
                    "一个高质量候选人胜过十个低质量候选人"
                ],
                "execution_tips": [
                    "所有关键词组合在一天内搜索完成",
                    "建议分批次执行，避免平台限制",
                    "保存搜索结果便于后续处理"
                ]
            }
        }
        
        return result
    
    def save_to_file(self, result: Dict, filename: str = "jddog_output.json"):
        """保存结果到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {filename}")
    
    def print_summary(self, result: Dict):
        """打印结果摘要"""
        print("\n" + "="*80)
        print("JDdog-agent-LP 生成结果摘要")
        print("="*80)
        
        # 输入信息
        print(f"\n📋 输入信息:")
        print(f"  平台: {result['input']['platform']}")
        print(f"  严格级别: {result['input']['strict_level']}")
        print(f"  补充说明: {result['input']['supplement']}")
        
        # 关键词信息
        keywords = result["search_keywords"]
        print(f"\n🔍 搜索关键词:")
        print(f"  核心组合 ({len(keywords['core'])}个):")
        for kw in keywords["core"]:
            print(f"    • {kw}")
        
        print(f"  扩展组合 ({len(keywords['expanded'])}个，示例):")
        for kw in keywords["expanded"][:3]:  # 显示前3个
            print(f"    • {kw}")
        if len(keywords["expanded"]) > 3:
            print(f"    ... 还有{len(keywords['expanded'])-3}个")
        
        print(f"  总计: {keywords['total_count']}个关键词组合")
        
        # 筛选条件
        filters = result["filters"]
        print(f"\n🎯 筛选条件:")
        for key, value in filters.items():
            print(f"  {key}: {value}")
        
        # 执行策略
        execution = result["execution"]
        print(f"\n📅 执行策略:")
        print(f"  执行模式: {execution['execution_mode']}")
        print(f"  关键词总数: {execution['keywords_count']}个")
        print(f"  最低要求: {execution['minimum_required']}个")
        print(f"  符合要求: {'✅' if execution['meets_requirement'] else '❌'}")
        print(f"  示例关键词（前5个）: {', '.join(execution['search_strategy'][0]['keywords'][:5])}")
        
        # 操作说明
        print(f"\n📝 操作说明:")
        for instr in result["instructions"]["filter_operations"][:5]:  # 显示前5条
            print(f"  • {instr}")
        
        # 平台注意事项
        print(f"\n⚠️  平台注意事项:")
        for note in result["instructions"]["platform_notes"][:3]:  # 显示前3条
            print(f"  • {note}")
        
        print("\n" + "="*80)
        print("✅ 生成完成！")
        print("="*80)


def main():
    """主函数"""
    # 测试用例
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
    
    test_supplement = "苛刻客户"
    
    # 创建agent
    print("初始化 JDdog-agent-LP...")
    agent = JDDogAgent(platform="猎聘", strict_level="严格")
    
    # 生成搜索条件
    result = agent.generate_search_conditions(test_jd, test_supplement)
    
    # 打印摘要
    agent.print_summary(result)
    
    # 保存到文件
    agent.save_to_file(result, "jddog_output.json")
    
    # 保存单日搜索计划
    search_plan = result["execution"]["search_strategy"][0]  # 单日计划
    with open("single_day_search_plan.json", 'w', encoding='utf-8') as f:
        json.dump(search_plan, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 单日搜索计划已保存到: single_day_search_plan.json")
    print(f"   包含{search_plan['count']}个关键词组合")


if __name__ == "__main__":
    main()