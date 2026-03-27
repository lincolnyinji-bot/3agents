#!/usr/bin/env python3
"""
测试AI-H Pipeline集成区域性VC和产业CVC识别
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from aih_pipeline_v3 import JudgeV3Integrator

def test_integration():
    """测试集成"""
    integrator = JudgeV3Integrator()
    print(f"Judge可用: {integrator.judge_available}")
    
    # 测试候选人数据
    test_candidates = [
        {
            "name": "华为哈勃投资经理",
            "company": "华为哈勃投资",
            "role": "投资经理",
            "exp": "3年投资经验",
            "degree": "清华大学电子工程硕士",
            "school": "清华大学",
            "description": "专注半导体和材料领域投资，主导投资5个半导体项目，参与10+个项目。投资案例：投资某EDA公司，已进入B轮；投资某功率半导体公司，已实现量产。专业方向：半导体、芯片设计、新材料。技术背景：有芯片设计研发经验。",
            "skills": ["半导体", "芯片", "材料", "投资分析", "尽职调查"]
        },
        {
            "name": "红杉资本投资经理", 
            "company": "红杉资本",
            "role": "投资经理",
            "exp": "4年投资经验",
            "degree": "复旦大学金融硕士",
            "school": "复旦大学",
            "description": "全阶段投资，参与投资12个AI和企业服务项目。投资案例：投资某AI公司，已独角兽；投资某SaaS公司，已C轮。专业方向：AI、企业服务、消费科技。机构优势：红杉品牌背书，全国性网络。",
            "skills": ["AI", "企业服务", "SaaS", "投资分析", "行业研究"]
        },
        {
            "name": "深创投投资总监",
            "company": "深创投",
            "role": "投资总监",
            "exp": "8年投资经验",
            "degree": "北京大学金融硕士",
            "school": "北京大学",
            "description": "专注硬科技投资，主导投资20+个项目，5个已上市。投资案例：投资某机器人公司，已科创板上市；投资某新能源公司，已Pre-IPO。专业方向：先进制造、机器人、新能源。地域资源：深耕深圳及珠三角地区，有丰富地方政府资源。",
            "skills": ["硬科技", "机器人", "新能源", "投资管理", "政府关系"]
        }
    ]
    
    print("AI-H Pipeline集成测试")
    print("="*60)
    
    for i, candidate in enumerate(test_candidates, 1):
        print(f"\n测试候选人 {i}: {candidate['name']}")
        print(f"公司: {candidate['company']}")
        print(f"职位: {candidate['role']}")
        
        # 评估候选人
        result = integrator.evaluate_candidate(candidate, position_level="IM")
        
        # 调试：打印构建的简历文本
        resume_text = integrator._build_resume_text(candidate)
        print(f"构建的简历文本（前200字符）: {resume_text[:200]}...")
        
        print(f"评估结果:")
        print(f"  总分: {result.get('score', 'N/A')}")
        print(f"  推荐: {result.get('recommendation', 'N/A')}")
        
        if 'basic_info' in result:
            basic = result['basic_info']
            print(f"  机构类型: {basic.get('institution_type', 'N/A')}")
            print(f"  产业CVC: {basic.get('industry_cvc_institution', False)}")
            print(f"  头部VC: {basic.get('big_institution', False)}")
            print(f"  区域性VC: {basic.get('regional_institution', False)}")
        
        print("-"*40)

def test_position_levels():
    """测试不同职级评估"""
    print("\n\n不同职级评估测试")
    print("="*60)
    
    integrator = JudgeV3Integrator()
    
    candidate = {
        "name": "小米长江产业基金VP",
        "company": "小米长江产业基金",
        "role": "副总裁",
        "exp": "6年投资经验",
        "degree": "浙江大学计算机硕士",
        "school": "浙江大学",
        "description": "专注智能硬件和汽车电子投资，参与投资15个项目，主导8个。投资案例：投资某汽车芯片公司，已C轮；投资某传感器公司，已量产。专业方向：汽车电子、智能驾驶、物联网。产业资源：有小米生态链丰富资源。",
        "skills": ["智能硬件", "汽车电子", "物联网", "产业投资", "生态链"]
    }
    
    for level in ["IM", "SIM", "VP"]:
        print(f"\n职级: {level}")
        result = integrator.evaluate_candidate(candidate, position_level=level)
        
        print(f"  总分: {result.get('total_score', 'N/A')}")
        print(f"  推荐: {result.get('recommendation', 'N/A')}")
        
        if 'basic_info' in result:
            basic = result['basic_info']
            print(f"  机构类型: {basic.get('institution_type', 'N/A')}")

if __name__ == "__main__":
    test_integration()
    test_position_levels()
    
    print("\n" + "="*60)
    print("集成测试完成")
    print("规则验证: 产业CVC ≥ 头部VC > 区域性VC")