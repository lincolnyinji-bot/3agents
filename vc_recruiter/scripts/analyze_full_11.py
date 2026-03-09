#!/usr/bin/env python3
"""
完整分析11位候选人
基于你的投资行业标准和真实简历
"""

import csv
import re

print("="*80)
print("11份面试级候选人深度分析")
print("基于你提供的：1)职级划分 2)晋升年龄标准 3)各级别定位")
print("="*80)

def analyze_candidate(candidate):
    name = candidate['name']
    age_str = candidate['age']
    age = int(re.search(r'\d+', age_str).group()) if re.search(r'\d+', age_str) else 0
    
    # 提取经验
    vc_exp = candidate['vc_experience']
    vc_years_match = re.search(r'(\d+)', str(vc_exp))
    vc_years = int(vc_years_match.group(1)) if vc_years_match else 0
    
    deal_count = candidate['deal_count']
    deal_match = re.search(r'(\d+)', str(deal_count))
    deal_num = int(deal_match.group(1)) if deal_match else 0
    
    position = candidate['current_position']
    notes = candidate['notes']
    
    print(f"\n{'='*60}")
    print(f"候选人: {name} ({candidate['gender']}, {age}岁, {candidate['marital_status']})")
    print(f"当前: {position} @ {candidate['current_company']}")
    print(f"你的标注: {notes}")
    print('-'*60)
    
    # 1. 学历评估
    bachelor_school = candidate['bachelor_school']
    master_school = candidate['master_school']
    phd_school = candidate.get('phd_school', '')
    
    # 学校层级
    tier1_schools = ['北京大学', '清华大学', '牛津大学', '剑桥大学']
    tier2_schools = ['上海交通大学', '华中科技大学', '中山大学', '华南理工大学', 
                    '香港中文大学', '加州大学', '宾夕法尼亚州立大学', '诺丁汉大学']
    tier3_schools = ['重庆大学', '四川大学', '辽宁工业大学']
    
    school_score = 0
    school_notes = []
    
    if bachelor_school in tier1_schools:
        school_score += 20
        school_notes.append(f"T1本科({bachelor_school})")
    elif bachelor_school in tier2_schools:
        school_score += 15
        school_notes.append(f"T2本科({bachelor_school})")
    elif bachelor_school in tier3_schools:
        school_score += 10
        school_notes.append(f"T3本科({bachelor_school})")
    
    if master_school in tier1_schools:
        school_score += 20
        school_notes.append(f"T1硕士({master_school})")
    elif master_school in tier2_schools:
        school_score += 15
        school_notes.append(f"T2硕士({master_school})")
    elif master_school in tier3_schools:
        school_score += 10
        school_notes.append(f"T3硕士({master_school})")
    
    if phd_school in tier1_schools:
        school_score += 10
        school_notes.append(f"T1博士({phd_school})")
    elif phd_school:
        school_score += 5
        school_notes.append(f"博士({phd_school})")
    
    # 2. 经验评估（基于你的标准：硕士24岁毕业）
    # A/Associate(24-28) → SA(28-30) → VP(30-35) → D(35-40) → ED(40-45) → MD(45+)
    exp_score = 0
    exp_notes = []
    
    # VC经验评分
    if vc_years >= 8:
        exp_score += 12
        exp_notes.append(f"{vc_years}年VC(D/ED级经验)")
    elif vc_years >= 5:
        exp_score += 9
        exp_notes.append(f"{vc_years}年VC(D级经验)")
    elif vc_years >= 3:
        exp_score += 7
        exp_notes.append(f"{vc_years}年VC(VP级经验)")
    elif vc_years >= 1:
        exp_score += 5
        exp_notes.append(f"{vc_years}年VC(SA级经验)")
    else:
        exp_score += 2
        exp_notes.append(f"{vc_years}年VC(A级经验)")
    
    # 案例评分
    if deal_num >= 10:
        exp_score += 15
        exp_notes.append(f"{deal_num}案例(极其丰富)")
    elif deal_num >= 5:
        exp_score += 12
        exp_notes.append(f"{deal_num}案例(丰富)")
    elif deal_num >= 3:
        exp_score += 8
        exp_notes.append(f"{deal_num}案例(较好)")
    elif deal_num >= 1:
        exp_score += 5
        exp_notes.append(f"{deal_num}案例(有经验)")
    
    # 3. 级别评估（核心逻辑）
    print("【级别评估】")
    
    # 基于经验的级别
    if vc_years >= 8 and deal_num >= 10:
        exp_based_level = "投资执行董事/董事总经理(ED/MD)"
    elif vc_years >= 5 and deal_num >= 5:
        exp_based_level = "投资总监(Director)"
    elif vc_years >= 3 and deal_num >= 3:
        exp_based_level = "投资副总裁(VP)"
    elif vc_years >= 1 and deal_num >= 1:
        exp_based_level = "高级投资经理(Senior Associate)"
    else:
        exp_based_level = "投资分析师/投资经理(Analyst/Associate)"
    
    # 基于年龄的合理级别（你的标准）
    if age >= 40:
        age_appropriate_level = "投资执行董事/董事总经理(ED/MD)"
    elif age >= 35:
        age_appropriate_level = "投资总监(Director)"
    elif age >= 30:
        age_appropriate_level = "投资副总裁(VP)"
    elif age >= 28:
        age_appropriate_level = "高级投资经理(Senior Associate)"
    else:
        age_appropriate_level = "投资分析师/投资经理(Analyst/Associate)"
    
    print(f"经验级别: {exp_based_level} ({vc_years}年VC, {deal_num}案例)")
    print(f"年龄合理级别: {age_appropriate_level} ({age}岁)")
    print(f"当前职位: {position}")
    
    # 一致性检查
    issues = []
    if '总监' in exp_based_level and '经理' in age_appropriate_level:
        issues.append("经验达到总监级但年龄偏小，可能职位虚高")
    elif '经理' in exp_based_level and '总监' in age_appropriate_level:
        issues.append("年龄达到总监级但经验不足，可能发展缓慢")
    
    if '总监' in position and '经理' in exp_based_level:
        issues.append("职位为总监但经验仅为经理级，职位可能虚高")
    elif '经理' in position and '总监' in exp_based_level:
        issues.append("经验达到总监级但职位为经理，可能被低估")
    
    # 4. 与你的判断对比
    print("\n【系统判断 vs 你的判断】")
    print(f"你的判断: {notes}")
    
    # 从你的标注中提取级别关键词
    your_level = "未知"
    if '顶级投资总监' in notes:
        your_level = "投资总监(Director)或更高"
    elif '优秀VP级' in notes or 'VP级' in notes:
        your_level = "投资副总裁(VP)"
    elif '优秀总监' in notes or '总监级' in notes:
        your_level = "投资总监(Director)"
    elif '优秀ED级' in notes:
        your_level = "投资执行董事(ED)"
    elif '培养' in notes or '易获面试' in notes:
        your_level = "投资经理/高级投资经理"
    
    print(f"你判断的级别: {your_level}")
    print(f"系统判断的级别: {exp_based_level}")
    
    # 匹配分析
    match_analysis = ""
    if ('总监' in your_level and '总监' in exp_based_level) or \
       ('VP' in your_level and 'VP' in exp_based_level) or \
       ('经理' in your_level and '经理' in exp_based_level) or \
       ('ED' in your_level and 'ED' in exp_based_level):
        match_analysis = "✅ 级别匹配"
    elif ('总监' in your_level and 'VP' in exp_based_level):
        match_analysis = "⚠️ 系统低估一级（总监→VP）"
    elif ('VP' in your_level and '总监' in exp_based_level):
        match_analysis = "⚠️ 系统高估一级（VP→总监）"
    elif ('VP' in your_level and '经理' in exp_based_level):
        match_analysis = "⚠️ 系统低估两级（VP→经理）"
    elif ('经理' in your_level and 'VP' in exp_based_level):
        match_analysis = "⚠️ 系统高估两级（经理→VP）"
    else:
        match_analysis = "❌ 级别不匹配"
    
    print(f"匹配度: {match_analysis}")
    
    # 5. 面试/推荐建议
    print("\n【面试/推荐建议】")
    
    total_score = school_score + exp_score
    
    if total_score >= 70:
        if '总监' in exp_based_level or 'ED' in exp_based_level:
            recommendation = "✅ 强烈推荐（总监/ED级人才）"
        elif 'VP' in exp_based_level:
            recommendation = "✅ 推荐（VP级人才）"
        else:
            recommendation = "✅ 推荐（高级经理级人才）"
    elif total_score >= 60:
        if '易获面试' in notes or '硬条件好' in notes:
            recommendation = "⚠️ 可给面试机会（硬条件好，但需评估深度）"
        else:
            recommendation = "⚠️ 需进一步评估"
    else:
        if '培养' in notes:
            recommendation = "⚠️ 可作为培养对象（从SA开始）"
        else:
            recommendation = "❌ 暂不推荐"
    
    print(f"综合推荐: {recommendation}")
    
    if issues:
        print(f"注意: {'; '.join(issues)}")
    
    # 特殊备注
    if '前沿科技不合格' in notes:
        print(f"⚠️ 特殊备注: 仅适合汽车方向，不适合前沿科技")
    if '沉淀有限' in notes or '宽而不深' in notes:
        print(f"⚠️ 特殊备注: 工作内容宽泛，细分领域深度不足")
    if '年轻有活力' in notes or '学习能力强' in notes:
        print(f"💡 优势: 年轻有潜力，学习能力强")
    
    return {
        'name': name,
        'age': age,
        'vc_years': vc_years,
        'deal_num': deal_num,
        'school_score': school_score,
        'exp_score': exp_score,
        'total_score': total_score,
        'exp_based_level': exp_based_level,
        'age_appropriate_level': age_appropriate_level,
        'your_level': your_level,
        'match_analysis': match_analysis,
        'recommendation': recommendation,
        'issues': issues
    }

# 主程序
candidates = []
with open('../data/11_candidates_full.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        candidates.append(row)

results = []
for candidate in candidates:
    result = analyze_candidate(candidate)
    results.append(result)

# 汇总分析
print("\n" + "="*80)
print("11位候选人分析结果汇总")
print("="*80)

print(f"\n{'姓名':<6} {'年龄':<4} {'VC经验':<6} {'案例':<6} {'总分':<6} {'系统级别':<20} {'你的级别':<15} {'匹配度':<15} {'推荐'}")
print("-"*90)

for result in results:
    print(f"{result['name']:<6} {result['age']:<4} {result['vc_years']:<6} "
          f"{result['deal_num']:<6} {result['total_score']:<6} "
          f"{result['exp_based_level']:<20} {result['your_level']:<15} "
          f"{result['match_analysis']:<15} {result['recommendation'][:20]}")

# 统计分析
print("\n" + "="*80)
print("匹配度统计")
print("="*80)

matches = sum(1 for r in results if '匹配' in r['match_analysis'])
underestimates = sum(1 for r in results if '低估' in r['match_analysis'])
overestimates = sum(1 for r in results if '高估' in r['match_analysis'])
mismatches = sum(1 for r in results if '不匹配' in r['match_analysis'])

print(f"✅ 级别匹配: {matches}人")
print(f"⚠️ 系统低估: {underestimates}人")
print(f"⚠️ 系统高估: {overestimates}人")
print(f"❌ 级别不匹配: {mismatches}人")
print(f"准确率: {matches/len(results)*100:.1f}%")

# 按级别分类
print("\n" + "="*80)
print("按系统判断级别分类")
print("="*80)

level_counts = {}
for result in results:
    level = result['exp_based_level']
    level_counts[level] = level_counts.get(level, 0) + 1

for level, count in sorted(level_counts.items()):
    names = [r['name'] for r in results if r['exp_based_level'] == level]
    print(f"{level}: {count}人 - {', '.join(names)}")

# 发现的问题和改进建议
print("\n" + "="*80)
print("关键发现与系统优化建议")
print("="*80)

print("\n1. 发现的问题案例:")
for result in results:
    if '低估' in result['match_analysis'] or '高估' in result['match_analysis']:
        print(f"- {result['name']}: {result['match_analysis']} (你的判断:{result['your_level']}, 系统:{result['exp_based_level']})")

print("\n2. 需要重点优化的维度:")
print("""
A. 券商行研/产业经验权重不足
   - 胡独巍：4年券商行研+3年产业资本，系统低估
   - 需要增加"产业背景转投资"专项加分

B. 学历与经验的综合评估
   - 施忠鑫：优秀学历(UCSD MBA)但仅2年经验，系统低估
   - 需要"优秀学历+短期经验"的特殊通道评估

C. 案例质量 vs 数量
   - 李垚慰：高IRR案例(63.7%-334%)应更高权重
   - 需要增加IRR、退出倍数等质量指标

D. 年龄与级别匹配度
   - 姜玮常：35岁但经验丰富，系统判断准确
   - 需要"年龄偏大但经验丰富" vs "年轻有潜力"的不同评估逻辑

E. 专业方向匹配度
   - 李世清：汽车方向VP vs 前沿科技不合格
   - 需要按投资方向差异化评估
""")

print("\n3. 基于11份简历的系统优化建议:")
print("""
1. 增加产业背景专项评估模块
   - 券商行研、产业公司经验
   - 技术研发、产品经理经验

2. 优化年龄-经验匹配度检查
   - 硕士24岁毕业基准
   - 2年SA(28+), 3年VP(30+), 3-5年D(35+)

3. 增加案例质量评估
   - IRR > 50% 加分
   - 有退出/上市案例加分
   - 独角兽/行业龙头加分

4. 专业方向匹配度评估
   - 硬科技/AI vs 汽车/制造 vs 消费/互联网
   - 按目标岗位方向调整权重

5. 潜力候选人识别
   - 年轻(28-30) + 优秀学历 + 有案例
   - 可作为培养对象从SA开始
""")

# 输出到文件
output_file = '../output/11_candidates_detailed_analysis.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['name', 'age', 'vc_years', 'deal_num', 'school_score', 'exp_score', 
                 'total_score', 'exp_based_level', 'age_appropriate_level', 'your_level',
                 'match_analysis', 'recommendation', 'issues']
    
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    
    for result in results:
        writer.writerow({
            'name': result['name'],
            'age': result['age'],
            'vc_years': result['vc_years'],
            'deal_num': result['deal_num'],
            'school_score': result['school_score'],
            'exp_score': result['exp_score'],
            'total_score': result['total_score'],
            'exp_based_level': result['exp_based_level'],
            'age_appropriate_level': result['age_appropriate_level'],
            'your_level': result['your_level'],
            'match_analysis': result['match_analysis'],
            'recommendation': result['recommendation'],
            'issues': '; '.join(result['issues']) if result['issues'] else ''
        })

print(f"\n详细分析结果已保存至: {output_file}")
print("="*80)