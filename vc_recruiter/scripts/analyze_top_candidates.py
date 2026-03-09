#!/usr/bin/env python3
"""
手动分析5位顶级候选人
基于你提供的专业判断标准
"""

def analyze_candidate(candidate):
    """手动分析候选人"""
    name = candidate['name']
    print(f"\n{'='*60}")
    print(f"候选人: {name} ({candidate['gender']}, {candidate['age']}岁)")
    print(f"级别标注: {candidate['notes']}")
    print('-'*60)
    
    # 学历分析
    print("【学历分析】")
    print(f"本科: {candidate['bachelor_school']} - {candidate['bachelor_major']}")
    print(f"硕士: {candidate['master_school']} - {candidate['master_major']}")
    if candidate.get('phd_school'):
        print(f"博士: {candidate['phd_school']} - {candidate['phd_major']}")
    
    # 学历评分（根据你的标准）
    edu_score = 0
    edu_reasons = []
    
    # 学校评分 (40分)
    school_score = 0
    if candidate['bachelor_school'] in ['北京大学', '清华大学']:
        school_score += 20
        edu_reasons.append("顶级本科学校(20分)")
    elif candidate['bachelor_school'] in ['中山大学', '华南理工大学', '香港中文大学']:
        school_score += 15
        edu_reasons.append("优秀本科学校(15分)")
    
    if candidate['master_school'] in ['北京大学', '清华大学']:
        school_score += 20
        edu_reasons.append("顶级硕士学校(20分)")
    elif candidate['master_school'] in ['中山大学', '香港中文大学', '加州大学']:
        school_score += 15
        edu_reasons.append("优秀硕士学校(15分)")
    
    edu_score += min(40, school_score)
    
    # 专业评分
    bachelor_major = candidate['bachelor_major']
    master_major = candidate['master_major']
    
    # 理工科专业列表（根据你的标准）
    stem_keywords = ['力学', '电子', '能源', '动力', '工程', '物理', '数学', '科学', 
                     '技术', '计算机', '软件', '硬件', '信息', '通信', '微电子', '自动化']
    
    is_bachelor_stem = any(keyword in bachelor_major for keyword in stem_keywords)
    is_master_stem = any(keyword in master_major for keyword in stem_keywords)
    
    if is_bachelor_stem:
        edu_score += 10
        edu_reasons.append("本科理工科专业(10分)")
    else:
        edu_score += 2
        edu_reasons.append("本科非理工科专业(2分)")
    
    if is_master_stem:
        edu_score += 10
        edu_reasons.append("硕士理工科专业(10分)")
    elif '金融' in master_major or '经济' in master_major or '工商管理' in master_major:
        edu_score += 5
        edu_reasons.append("硕士商科专业(5分)")
    else:
        edu_score += 2
        edu_reasons.append("硕士其他专业(2分)")
    
    print(f"学历总分: {edu_score}/40")
    print(f"评分理由: {'; '.join(edu_reasons)}")
    
    # 经验分析
    print("\n【经验分析】")
    print(f"总投资经验: {candidate['total_experience']}")
    print(f"VC经验: {candidate['vc_experience']}")
    print(f"案例数: {candidate['deal_count']}个")
    print(f"当前职位: {candidate['current_position']} ({candidate['current_company']})")
    
    # 经验评分 (30分)
    exp_score = 0
    exp_reasons = []
    
    vc_years = int(candidate['vc_experience'].replace('年', ''))
    deal_num = int(candidate['deal_count'])
    
    # VC经验年数 (12分)
    if vc_years >= 5:
        exp_score += 12
        exp_reasons.append(f"{vc_years}年VC经验(12分)")
    elif vc_years >= 3:
        exp_score += 9
        exp_reasons.append(f"{vc_years}年VC经验(9分)")
    elif vc_years >= 1:
        exp_score += 6
        exp_reasons.append(f"{vc_years}年VC经验(6分)")
    
    # 投成案例 (15分)
    if deal_num >= 10:
        exp_score += 15
        exp_reasons.append(f"{deal_num}个投成案例(15分)")
    elif deal_num >= 5:
        exp_score += 12
        exp_reasons.append(f"{deal_num}个投成案例(12分)")
    elif deal_num >= 3:
        exp_score += 8
        exp_reasons.append(f"{deal_num}个投成案例(8分)")
    elif deal_num >= 1:
        exp_score += 5
        exp_reasons.append(f"{deal_num}个投成案例(5分)")
    else:
        exp_reasons.append("无明确投成案例(0分)")
    
    print(f"经验总分: {exp_score}/30")
    print(f"评分理由: {'; '.join(exp_reasons)}")
    
    # 薪资分析
    print("\n【薪资分析】")
    print(f"当前薪资: {candidate['current_annual']}")
    print(f"期望薪资: {candidate['expected_annual']}")
    
    # 薪资评分 (10分)
    salary_score = 8  # 基础分
    salary_reasons = ["薪资合理性基础分(8分)"]
    
    # 判断期望是否合理
    current_str = candidate['current_annual']
    expected_str = candidate['expected_annual']
    
    current_match = re.search(r'(\d+)', current_str)
    if current_match:
        current = int(current_match.group(1))
        
        if '面议' in expected_str:
            # 面议情况，判断期望涨幅
            expected = int(current * 1.2)  # 20%合理涨幅
            salary_reasons.append(f"期望薪资面议，推断合理期望{expected}万")
        else:
            expected_match = re.search(r'(\d+)', expected_str)
            if expected_match:
                expected = int(expected_match.group(1))
                increase_rate = (expected - current) / current * 100 if current > 0 else 0
                if 0 <= increase_rate <= 30:
                    salary_score += 1
                    salary_reasons.append(f"期望涨幅合理({increase_rate:.0f}%)(+1分)")
                elif increase_rate > 50:
                    salary_score -= 1
                    salary_reasons.append(f"期望涨幅过高({increase_rate:.0f}%)(-1分)")
    
    print(f"薪资总分: {salary_score}/10")
    print(f"评分理由: {'; '.join(salary_reasons)}")
    
    # 技能评分 (10分) - 简化版
    print("\n【技能分析】")
    skill_score = 6  # 基础投资技能分
    skill_reasons = ["基础投资技能(6分)"]
    
    position = candidate['current_position']
    if '总监' in position or 'VP' in position or 'ED' in position:
        skill_score += 2
        skill_reasons.append("总监/VP级别技能(+2分)")
    
    # 行业专精加分
    notes = candidate['notes']
    if '硬科技' in notes or 'AI' in notes or '半导体' in notes or '机器人' in notes:
        skill_score += 2
        skill_reasons.append("硬科技/AI领域专精(+2分)")
    
    skill_score = min(10, skill_score)
    print(f"技能总分: {skill_score}/10")
    print(f"评分理由: {'; '.join(skill_reasons)}")
    
    # 案例评分 (10分) - 简化版
    print("\n【案例专项】")
    case_score = 0
    
    if deal_num >= 5:
        case_score = 10
        print(f"案例总分: {case_score}/10 - {deal_num}个投成案例，经验丰富(10分)")
    elif deal_num >= 3:
        case_score = 8
        print(f"案例总分: {case_score}/10 - {deal_num}个投成案例，经验较好(8分)")
    elif deal_num >= 1:
        case_score = 5
        print(f"案例总分: {case_score}/10 - {deal_num}个投成案例，有实操经验(5分)")
    else:
        print(f"案例总分: {case_score}/10 - 无明确投成案例(0分)")
    
    # 总分
    total_score = edu_score + exp_score + salary_score + skill_score + case_score
    print(f"\n{'='*60}")
    print(f"【总分: {total_score}/100】")
    
    # 推荐状态
    if total_score >= 75:
        status = "✅ 推荐"
    elif total_score >= 50:
        status = "⚠️ 可面试"
    else:
        status = "❌ 不推荐"
    
    print(f"【状态: {status}】")
    
    # 评估级别
    print(f"【系统评估级别:】")
    if vc_years >= 5 and deal_num >= 5:
        level = "投资副总裁/总监"
    elif vc_years >= 3 or deal_num >= 3:
        level = "高级投资经理"
    elif vc_years >= 1 or deal_num >= 1:
        level = "投资经理"
    else:
        level = "投资分析师"
    
    print(f"{level} (VC经验{vc_years}年，案例{deal_num}个)")
    
    return {
        'name': name,
        'total_score': total_score,
        'status': status,
        'level': level,
        'edu_score': edu_score,
        'exp_score': exp_score,
        'salary_score': salary_score,
        'skill_score': skill_score,
        'case_score': case_score
    }

# 主程序
import csv
import re

print("="*70)
print("5位顶级候选人手动分析报告")
print("基于你的专业判断标准")
print("="*70)

# 读取数据
candidates = []
with open('../data/updated_assessment.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        candidates.append(row)

results = []
for candidate in candidates:
    result = analyze_candidate(candidate)
    results.append(result)

print("\n" + "="*70)
print("分析结果汇总")
print("="*70)

print(f"\n{'姓名':<6} {'总分':<5} {'状态':<8} {'级别':<12} {'学历':<4} {'经验':<4} {'薪资':<4} {'技能':<4} {'案例':<4}")
print("-"*60)

for res in results:
    print(f"{res['name']:<6} {res['total_score']:<5} {res['status']:<8} {res['level']:<12} "
          f"{res['edu_score']:<4} {res['exp_score']:<4} {res['salary_score']:<4} "
          f"{res['skill_score']:<4} {res['case_score']:<4}")

# 统计
recommended = sum(1 for r in results if r['total_score'] >= 75)
interviewable = sum(1 for r in results if 50 <= r['total_score'] < 75)
not_recommended = sum(1 for r in results if r['total_score'] < 50)

print("\n" + "="*70)
print(f"统计: 推荐{recommended}人 | 可面试{interviewable}人 | 不推荐{not_recommended}人")
print(f"推荐率: {recommended/len(results)*100:.1f}%")
print("="*70)

# 与你的判断对比
print("\n与你的专业判断对比:")
print(f"{'姓名':<6} {'我的判断':<15} {'系统评分':<8} {'匹配度':<8}")
print("-"*40)

expert_judgments = {
    '聂彩明': '顶级投资总监',
    '符晓': '顶级投资总监', 
    '胡独巍': '优秀VP级',
    '何远迪': '优秀ED级',
    '施忠鑫': '优秀VP级'
}

for res in results:
    expert = expert_judgments.get(res['name'], '未知')
    match = "✅ 匹配" if (res['total_score'] >= 75 and ('顶级' in expert or '优秀' in expert)) else "⚠️ 偏差"
    if res['total_score'] < 50 and ('顶级' in expert or '优秀' in expert):
        match = "❌ 严重低估"
    
    print(f"{res['name']:<6} {expert:<15} {res['total_score']:<8} {match:<8}")