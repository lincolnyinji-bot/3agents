#!/usr/bin/env python3
"""
快速分析11位候选人
"""

import csv
import re

def analyze_candidate(candidate):
    name = candidate['name']
    age_str = candidate['age']
    age = int(re.search(r'\d+', age_str).group()) if re.search(r'\d+', age_str) else 0
    
    # 提取VC经验年数
    vc_exp = candidate['vc_experience']
    vc_years_match = re.search(r'(\d+)', str(vc_exp))
    vc_years = int(vc_years_match.group(1)) if vc_years_match else 0
    
    # 提取案例数
    deal_count = candidate['deal_count']
    deal_match = re.search(r'(\d+)', str(deal_count))
    deal_num = int(deal_match.group(1)) if deal_match else 0
    
    # 根据你的标准评估
    print(f"\n{'='*50}")
    print(f"候选人: {name} ({candidate['gender']}, {age}岁)")
    print(f"当前职位: {candidate['current_position']}")
    print(f"你的标注: {candidate['notes']}")
    print('-'*50)
    
    # 1. 学历评估
    bachelor_school = candidate['bachelor_school']
    master_school = candidate['master_school']
    
    edu_score = 0
    edu_notes = []
    
    # 学校评估
    top_schools = ['北京大学', '清华大学', '牛津大学', '剑桥大学']
    excellent_schools = ['上海交通大学', '华中科技大学', '中山大学', '华南理工大学', 
                        '香港中文大学', '加州大学', '宾夕法尼亚州立大学']
    
    if bachelor_school in top_schools:
        edu_score += 20
        edu_notes.append(f"顶尖本科({bachelor_school})")
    elif bachelor_school in excellent_schools:
        edu_score += 15
        edu_notes.append(f"优秀本科({bachelor_school})")
    
    if master_school in top_schools:
        edu_score += 20
        edu_notes.append(f"顶尖硕士({master_school})")
    elif master_school in excellent_schools:
        edu_score += 15
        edu_notes.append(f"优秀硕士({master_school})")
    
    print(f"学历评估: {edu_score}/40 - {'; '.join(edu_notes)}")
    
    # 2. 经验评估（基于你的晋升标准）
    exp_score = 0
    exp_notes = []
    
    # 硕士24岁毕业标准
    expected_years = max(0, age - 24)
    
    if vc_years >= 5:
        exp_score += 12
        exp_notes.append(f"{vc_years}年VC经验(总监级经验)")
    elif vc_years >= 3:
        exp_score += 9
        exp_notes.append(f"{vc_years}年VC经验(VP级经验)")
    elif vc_years >= 1:
        exp_score += 6
        exp_notes.append(f"{vc_years}年VC经验(高级经理级经验)")
    
    if deal_num >= 10:
        exp_score += 15
        exp_notes.append(f"{deal_num}个案例(极其丰富)")
    elif deal_num >= 5:
        exp_score += 12
        exp_notes.append(f"{deal_num}个案例(丰富)")
    elif deal_num >= 3:
        exp_score += 8
        exp_notes.append(f"{deal_num}个案例(较好)")
    elif deal_num >= 1:
        exp_score += 5
        exp_notes.append(f"{deal_num}个案例(有经验)")
    
    print(f"经验评估: {exp_score}/27 - {'; '.join(exp_notes)}")
    
    # 3. 级别评估（基于你的标准）
    print("\n【级别评估】")
    
    # 经验级别
    if vc_years >= 8 and deal_num >= 10:
        exp_level = "投资执行董事/董事总经理(ED/MD)级"
    elif vc_years >= 5 and deal_num >= 5:
        exp_level = "投资总监(Director)级"
    elif vc_years >= 3 and deal_num >= 3:
        exp_level = "投资副总裁(VP)级"
    elif vc_years >= 1 and deal_num >= 1:
        exp_level = "高级投资经理(Senior Associate)级"
    else:
        exp_level = "投资分析师/投资经理(Analyst/Associate)级"
    
    print(f"经验级别: {exp_level}")
    
    # 年龄级别
    if age >= 35:
        age_level = "总监级年龄(35+)"
    elif age >= 30:
        age_level = "VP级年龄(30-35)"
    elif age >= 28:
        age_level = "高级投资经理年龄(28-30)"
    else:
        age_level = "投资经理年龄(<28)"
    
    print(f"年龄级别: {age_level}")
    
    # 一致性检查
    issues = []
    if (exp_level in ["投资总监(Director)级", "投资执行董事/董事总经理(ED/MD)级"] and 
        age_level == "投资经理年龄(<28)"):
        issues.append("⚠️ 经验级别高但年龄偏小，可能职位虚高")
    elif (exp_level == "投资分析师/投资经理(Analyst/Associate)级" and 
          age_level == "总监级年龄(35+)"):
        issues.append("⚠️ 年龄偏大但经验级别低，可能发展缓慢")
    
    # 4. 与你的判断对比
    print("\n【系统判断 vs 你的判断】")
    my_judgment = candidate['notes']
    
    # 简单匹配逻辑
    if '顶级投资总监' in my_judgment:
        expected_exp_level = "投资总监(Director)级或更高"
    elif '优秀VP级' in my_judgment or 'VP级' in my_judgment:
        expected_exp_level = "投资副总裁(VP)级"
    elif '总监' in my_judgment and '优秀' in my_judgment:
        expected_exp_level = "投资总监(Director)级"
    elif '培养' in my_judgment or '易获面试' in my_judgment:
        expected_exp_level = "投资经理/高级投资经理级"
    else:
        expected_exp_level = "待判断"
    
    print(f"你的判断: {my_judgment}")
    print(f"系统判断: {exp_level}")
    
    # 匹配度
    match = ""
    if ('总监' in my_judgment and '总监' in exp_level) or \
       ('VP' in my_judgment and 'VP' in exp_level) or \
       ('经理' in my_judgment and '经理' in exp_level):
        match = "✅ 基本匹配"
    elif ('总监' in my_judgment and 'VP' in exp_level):
        match = "⚠️ 系统低估一级"
    elif ('VP' in my_judgment and '总监' in exp_level):
        match = "⚠️ 系统高估一级"
    else:
        match = "❌ 不匹配"
    
    print(f"匹配度: {match}")
    
    if issues:
        print(f"注意: {'; '.join(issues)}")
    
    total_score = edu_score + exp_score
    recommendation = ""
    
    if total_score >= 60:
        if '总监' in exp_level:
            recommendation = "✅ 推荐（总监级）"
        elif 'VP' in exp_level:
            recommendation = "✅ 推荐（VP级）"
        elif '高级' in exp_level:
            recommendation = "⚠️ 可面试（高级经理级）"
        else:
            recommendation = "⚠️ 需进一步评估"
    else:
        recommendation = "❌ 不推荐"
    
    print(f"综合推荐: {recommendation}")
    
    return {
        'name': name,
        'age': age,
        'vc_years': vc_years,
        'deal_num': deal_num,
        'exp_level': exp_level,
        'age_level': age_level,
        'match': match,
        'recommendation': recommendation,
        'total_score': total_score
    }

print("="*70)
print("11份面试级候选人快速分析")
print("基于你提供的行业晋升标准")
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

# 汇总
print("\n" + "="*70)
print("分析结果汇总")
print("="*70)

print(f"\n{'姓名':<6} {'年龄':<4} {'VC经验':<6} {'案例':<6} {'系统级别':<20} {'匹配度':<10} {'推荐'}")
print("-"*70)

for result in results:
    print(f"{result['name']:<6} {result['age']:<4} {result['vc_years']:<6} "
          f"{result['deal_num']:<6} {result['exp_level']:<20} "
          f"{result['match']:<10} {result['recommendation']}")

# 统计匹配度
matches = sum(1 for r in results if '匹配' in r['match'])
underestimates = sum(1 for r in results if '低估' in r['match'])
overestimates = sum(1 for r in results if '高估' in r['match'])
mismatches = sum(1 for r in results if '不匹配' in r['match'])

print("\n" + "="*70)
print(f"匹配度统计: 匹配{matches}人 | 低估{underestimates}人 | 高估{overestimates}人 | 不匹配{mismatches}人")
print(f"准确率: {matches/len(results)*100:.1f}%")
print("="*70)

# 按级别分类
print("\n按级别分类统计:")
level_counts = {}
for result in results:
    level = result['exp_level']
    level_counts[level] = level_counts.get(level, 0) + 1

for level, count in sorted(level_counts.items()):
    print(f"{level}: {count}人")

# 发现的问题和优化建议
print("\n" + "="*70)
print("系统优化建议")
print("="*70)

print("\n1. 发现的问题:")
for result in results:
    if '低估' in result['match'] or '高估' in result['match']:
        print(f"- {result['name']}: {result['match']}")

print("\n2. 需要优化的维度:")
print("- 学历权重调整：不同学校的专业匹配度")
print("- 经验评估细化：VC经验 vs 总工作经验")
print("- 年龄因素：年龄与级别的匹配度检查")
print("- 专业领域：硬科技 vs 汽车 vs 前沿科技差异")
print("- 案例质量：不只关注数量，还要看质量（IRR、退出情况）")

print("\n3. 基于11份简历的关键学习:")
print("- 总监级：5+年VC经验，5+案例，35+岁")
print("- VP级：3+年VC经验，3+案例，30+岁")
print("- 优秀背景但经验少：可作为培养对象")
print("- 年龄与经验需匹配：避免'职位虚高'或'发展缓慢'")