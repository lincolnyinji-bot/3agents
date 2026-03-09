#!/usr/bin/env python3
"""
构建泛硬科技投资人标准化数据集
覆盖28位候选人，从投资经理到总监
"""

import csv
import re
from datetime import datetime

print("="*80)
print("泛硬科技投资人标准化数据集构建")
print("="*80)

def standardize_experience(exp_str):
    """标准化经验年数"""
    if not exp_str:
        return 0
    # 处理"8年+"、"10+年"等格式
    match = re.search(r'(\d+)', str(exp_str))
    return float(match.group(1)) if match else 0

def standardize_salary(salary_str):
    """标准化薪资"""
    if not salary_str or '面议' in str(salary_str):
        return None
    match = re.search(r'(\d+)', str(salary_str))
    return float(match.group(1)) if match else None

def extract_deal_count(deal_str):
    """提取案例数"""
    if not deal_str:
        return 0
    # 处理"5+"、"10+"等格式
    match = re.search(r'(\d+)', str(deal_str))
    return int(match.group(1)) if match else 0

def categorize_school(school):
    """学校分级"""
    if not school:
        return '其他'
    
    school_lower = school.lower()
    
    # Tier 1: 顶尖学校
    t1_keywords = ['北京大', '清华', '牛津', '剑桥', '斯坦福', '麻省理工', '加州理工']
    for kw in t1_keywords:
        if kw in school_lower:
            return 'T1'
    
    # Tier 2: 优秀学校
    t2_keywords = ['上海交通', '复旦', '浙江大', '南京大', '华中科技', '中山大', 
                  '华南理工', '香港中文', '香港科技', '哥伦比亚', '宾夕法尼亚', 
                  '加州大学', '伦敦大学', '爱丁堡', '帝国理工']
    for kw in t2_keywords:
        if kw in school_lower:
            return 'T2'
    
    # Tier 3: 985/211
    t3_keywords = ['哈尔滨工业', '重庆大', '四川大', '西安交通', '武汉大', 
                  '南开', '天津大', '山东大', '吉林大']
    for kw in t3_keywords:
        if kw in school_lower:
            return 'T3'
    
    return '其他'

def categorize_major(major):
    """专业分类"""
    if not major:
        return '其他'
    
    major_lower = str(major).lower()
    
    # 硬科技核心专业
    core_tech = ['计算机', '软件', '电子', '微电子', '通信', '信息', '自动化',
                '人工智能', 'AI', '数据科学', '数学', '物理', '统计']
    for kw in core_tech:
        if kw in major_lower:
            return '核心硬科技'
    
    # 工程类专业
    engineering = ['机械', '材料', '化工', '能源', '动力', '车辆', '航空', '航天',
                  '土木', '建筑', '地质', '焊接', '封装']
    for kw in engineering:
        if kw in major_lower:
            return '工程类'
    
    # 商科/金融
    business = ['金融', '经济', '工商管理', 'MBA', '财经', '管理', '商业']
    for kw in business:
        if kw in major_lower:
            return '商科'
    
    return '其他'

def infer_age_from_experience(total_exp, vc_exp):
    """从经验推断大致年龄"""
    # 假设硕士25岁毕业
    base_age = 25
    total_years = standardize_experience(total_exp)
    return base_age + total_years if total_years > 0 else None

# 读取合并后的数据
input_file = '../data/all_historical_candidates_merged.csv'
output_file = '../data/hardtech_investors_standardized.csv'

print(f"读取数据: {input_file}")

candidates = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        candidates.append(row)

print(f"共读取 {len(candidates)} 位候选人")

# 标准化处理
standardized = []

for cand in candidates:
    name = cand['姓名']
    
    # 基础信息
    total_exp = standardize_experience(cand['工作经验'])
    vc_exp = standardize_experience(cand['投资经验'])
    deal_count = extract_deal_count(cand['投成案例数'])
    
    # 推断年龄
    inferred_age = infer_age_from_experience(cand['工作经验'], cand['投资经验'])
    
    # 学历评估
    bachelor_school = cand['本科学历']
    bachelor_major = cand['本科专业']
    master_school = cand['硕士学历']
    master_major = cand['硕士专业']
    
    # 学校分级
    bachelor_tier = categorize_school(bachelor_school)
    master_tier = categorize_school(master_school)
    
    # 专业分类
    bachelor_major_type = categorize_major(bachelor_major)
    master_major_type = categorize_major(master_major)
    
    # 职位级别初步推断
    position = cand['当前职位']
    position_level = '未知'
    
    if '合伙人' in position or 'partner' in position.lower():
        position_level = '合伙人'
    elif '总监' in position or 'director' in position.lower():
        position_level = '总监'
    elif 'vp' in position.lower() or '副总裁' in position:
        position_level = 'VP'
    elif '高级' in position or 'senior' in position.lower():
        position_level = '高级投资经理'
    elif '经理' in position or 'manager' in position.lower():
        position_level = '投资经理'
    elif '分析' in position or 'analyst' in position.lower():
        position_level = '分析师'
    elif '实习' in position:
        position_level = '实习生'
    
    # 构建标准化记录
    std_record = {
        '姓名': name,
        '当前职位': position,
        '推断职位级别': position_level,
        '当前公司': cand['当前公司'],
        
        # 经验数据
        '总工作经验年数': total_exp,
        'VC投资经验年数': vc_exp,
        '投成案例数': deal_count,
        '推断年龄': inferred_age,
        
        # 学历数据
        '本科学校': bachelor_school,
        '本科学校层级': bachelor_tier,
        '本科专业': bachelor_major,
        '本科专业类型': bachelor_major_type,
        
        '硕士学校': master_school,
        '硕士学校层级': master_tier,
        '硕士专业': master_major,
        '硕士专业类型': master_major_type,
        
        # 薪资数据
        '当前年薪(万)': standardize_salary(cand['当前年薪(万)']),
        '期望年薪(万)': standardize_salary(cand['期望年薪(万)']),
        
        # 原始数据链接
        '项目经验描述': cand.get('项目经验', '')[:200],  # 截断
        '数据来源文件': cand.get('source_file', ''),
        
        # 硬科技专项标记
        '硬科技相关专业': '是' if bachelor_major_type in ['核心硬科技', '工程类'] or 
                            master_major_type in ['核心硬科技', '工程类'] else '否',
        'STEM背景': '是' if bachelor_major_type in ['核心硬科技', '工程类'] else '否'
    }
    
    standardized.append(std_record)

print(f"\n标准化处理完成: {len(standardized)} 位候选人")

# 保存标准化数据
fieldnames = ['姓名', '当前职位', '推断职位级别', '当前公司',
             '总工作经验年数', 'VC投资经验年数', '投成案例数', '推断年龄',
             '本科学校', '本科学校层级', '本科专业', '本科专业类型',
             '硕士学校', '硕士学校层级', '硕士专业', '硕士专业类型',
             '当前年薪(万)', '期望年薪(万)', '项目经验描述', '数据来源文件',
             '硬科技相关专业', 'STEM背景']

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(standardized)

print(f"标准化数据已保存至: {output_file}")

# 统计分析
print("\n" + "="*80)
print("数据集统计分析")
print("="*80)

# 按职位级别统计
level_counts = {}
for cand in standardized:
    level = cand['推断职位级别']
    level_counts[level] = level_counts.get(level, 0) + 1

print("\n1. 职位级别分布:")
for level, count in sorted(level_counts.items()):
    print(f"  {level}: {count}人")

# 按经验年数统计
print("\n2. VC经验分布:")
exp_groups = {'0-2年': 0, '3-5年': 0, '6-10年': 0, '10年以上': 0}
for cand in standardized:
    exp = cand['VC投资经验年数']
    if exp <= 2:
        exp_groups['0-2年'] += 1
    elif exp <= 5:
        exp_groups['3-5年'] += 1
    elif exp <= 10:
        exp_groups['6-10年'] += 1
    else:
        exp_groups['10年以上'] += 1

for group, count in exp_groups.items():
    print(f"  {group}: {count}人")

# 按案例数统计
print("\n3. 投成案例分布:")
deal_groups = {'0案例': 0, '1-3案例': 0, '4-7案例': 0, '8+案例': 0}
for cand in standardized:
    deals = cand['投成案例数']
    if deals == 0:
        deal_groups['0案例'] += 1
    elif deals <= 3:
        deal_groups['1-3案例'] += 1
    elif deals <= 7:
        deal_groups['4-7案例'] += 1
    else:
        deal_groups['8+案例'] += 1

for group, count in deal_groups.items():
    print(f"  {group}: {count}人")

# STEM背景统计
print("\n4. 专业背景统计:")
stem_count = sum(1 for c in standardized if c['STEM背景'] == '是')
hardtech_count = sum(1 for c in standardized if c['硬科技相关专业'] == '是')
print(f"  STEM背景: {stem_count}人 ({stem_count/len(standardized)*100:.1f}%)")
print(f"  硬科技相关专业: {hardtech_count}人 ({hardtech_count/len(standardized)*100:.1f}%)")

# 学校层级统计
print("\n5. 最高学历学校层级:")
highest_tier_counts = {'T1': 0, 'T2': 0, 'T3': 0, '其他': 0}
for cand in standardized:
    # 取硕士或本科中较高的层级
    master_tier = cand['硕士学校层级']
    bachelor_tier = cand['本科学校层级']
    
    if master_tier in ['T1', 'T2', 'T3']:
        highest_tier_counts[master_tier] += 1
    elif bachelor_tier in ['T1', 'T2', 'T3']:
        highest_tier_counts[bachelor_tier] += 1
    else:
        highest_tier_counts['其他'] += 1

for tier, count in highest_tier_counts.items():
    print(f"  {tier}: {count}人")

print("\n" + "="*80)
print("数据集构建完成，可用于算法开发")
print("="*80)

# 显示部分样本
print("\n样本数据（前3位）:")
for i, cand in enumerate(standardized[:3], 1):
    print(f"\n{i}. {cand['姓名']}")
    print(f"   职位: {cand['当前职位']} ({cand['推断职位级别']})")
    print(f"   经验: VC{cand['VC投资经验年数']}年, 案例{cand['投成案例数']}个")
    print(f"   学历: {cand['本科学校']}({cand['本科学校层级']}) → {cand['硕士学校']}({cand['硕士学校层级']})")
    print(f"   专业: {cand['本科专业类型']} + {cand['硕士专业类型']}")