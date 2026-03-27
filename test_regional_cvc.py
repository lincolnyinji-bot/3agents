#!/usr/bin/env python3
"""
测试区域性VC和产业CVC识别
"""

from optimized_judge_v3 import OptimizedJudgeV3

def test_candidate(text, name="测试候选人", level="IM"):
    """测试单个候选人"""
    judge = OptimizedJudgeV3(position_level=level)
    result = judge.analyze_resume(text, candidate_name=name)
    
    print(f"\n{'='*60}")
    print(f"候选人: {name} | 职级: {level}")
    print(f"{'='*60}")
    
    print(f"基本信息:")
    print(f"  姓名: {result['basic_info']['name']}")
    print(f"  教育背景: {result['basic_info']['education_tier']}")
    print(f"  投资年限: {result['basic_info']['investment_years']}年")
    print(f"  项目数量: {result['basic_info']['project_count']}个")
    print(f"  机构类型: {result['basic_info']['institution_type']}")
    print(f"  产业CVC: {result['basic_info']['industry_cvc_institution']}")
    print(f"  区域性VC: {result['basic_info']['regional_institution']}")
    print(f"  头部VC: {result['basic_info']['big_institution']}")
    
    print(f"\n方向识别:")
    print(f"  主方向: {result['direction']}")
    print(f"  检测到的方向: {result['detected_direction']}")
    
    print(f"\n维度分数:")
    for dim, score in result['dimension_scores'].items():
        print(f"  {dim}: {score:.1f}")
    
    print(f"\n总分: {result['total_score']:.1f}")
    print(f"推荐: {result['recommendation']}")
    print(f"{'='*60}")

# 测试用例
test_cases = [
    {
        "name": "华为哈勃投资经理",
        "level": "IM",
        "text": """
        姓名：张明
        教育背景：清华大学电子工程硕士，本科上海交通大学
        工作经历：华为哈勃投资投资经理，专注半导体和材料领域
        投资经验：3年，主导投资5个半导体项目，参与10+个项目
        项目案例：投资某EDA公司，已进入B轮；投资某功率半导体公司，已实现量产
        专业方向：半导体、芯片设计、新材料
        技术背景：有芯片设计研发经验
        """
    },
    {
        "name": "深创投投资总监",
        "level": "SIM",
        "text": """
        姓名：李华
        教育背景：北京大学金融硕士
        工作经历：深创投投资总监，专注硬科技投资
        投资经验：8年，主导投资20+个项目，5个已上市
        项目案例：投资某机器人公司，已科创板上市；投资某新能源公司，已Pre-IPO
        专业方向：先进制造、机器人、新能源
        地域资源：深耕深圳及珠三角地区，有丰富地方政府资源
        """
    },
    {
        "name": "小米长江产业基金VP",
        "level": "VP",
        "text": """
        姓名：王强
        教育背景：浙江大学计算机硕士
        工作经历：小米长江产业基金副总裁，专注智能硬件和汽车电子
        投资经验：6年，参与投资15个项目，主导8个
        项目案例：投资某汽车芯片公司，已C轮；投资某传感器公司，已量产
        专业方向：汽车电子、智能驾驶、物联网
        产业资源：有小米生态链丰富资源
        """
    },
    {
        "name": "元禾控股投资经理",
        "level": "IM",
        "text": """
        姓名：陈磊
        教育背景：苏州大学本科
        工作经历：元禾控股投资经理，专注苏州地区硬科技
        投资经验：2年，参与投资8个项目
        项目案例：投资某生物医药公司，已B轮；投资某智能制造公司
        专业方向：生物医药、智能制造
        地域优势：熟悉苏州工业园区企业，有本地政府关系
        """
    },
    {
        "name": "红杉资本投资经理",
        "level": "IM",
        "text": """
        姓名：赵敏
        教育背景：复旦大学金融硕士
        工作经历：红杉资本投资经理，全阶段投资
        投资经验：4年，参与投资12个项目
        项目案例：投资某AI公司，已独角兽；投资某SaaS公司，已C轮
        专业方向：AI、企业服务、消费科技
        机构优势：红杉品牌背书，全国性网络
        """
    }
]

if __name__ == "__main__":
    print("区域性VC和产业CVC识别测试")
    print("="*60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['name']}")
        test_candidate(test_case['text'], test_case['name'], test_case['level'])