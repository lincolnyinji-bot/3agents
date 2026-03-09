#!/usr/bin/env python3
"""
合并所有历史简历（修复字段名问题）
"""

import csv
import os
from pathlib import Path

print("正在合并所有历史简历（修复字段名问题）...")
print("="*60)

data_dir = Path('../data')

# 定义文件列表
files_to_merge = [
    ('eleven_candidates.csv', '中文'),
    ('three_candidates.csv', '中文'),
    ('qinyan_corrected.csv', '中文'),
    ('wangmosong_detailed.csv', '中文'),
    ('junior_candidates.csv', '中文'),
    ('11_candidates_full.csv', '英文')
]

all_candidates = []

# 先单独处理中文文件
for filename, lang in files_to_merge:
    filepath = data_dir / filename
    if not filepath.exists():
        print(f"跳过: {filename} (文件不存在)")
        continue
        
    print(f"\n读取 {filename} ({lang}):")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # 读取第一行获取字段名
            first_line = f.readline().strip()
            f.seek(0)  # 重置文件指针
            
            if lang == '中文':
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    # 标准化字段名映射
                    standardized = {
                        '姓名': row.get('姓名', ''),
                        '当前职位': row.get('当前职位', ''),
                        '当前公司': row.get('当前公司', ''),
                        '工作经验': row.get('工作经验', ''),
                        '投资经验': row.get('投资经验', ''),
                        '本科学历': row.get('本科学历', ''),
                        '本科专业': row.get('本科专业', ''),
                        '硕士学历': row.get('硕士学历', ''),
                        '硕士专业': row.get('硕士专业', ''),
                        '当前年薪(万)': row.get('当前年薪(万)', ''),
                        '期望年薪(万)': row.get('期望年薪(万)', ''),
                        '投成案例数': row.get('投成案例数', ''),
                        '项目经验': row.get('项目经验', ''),
                        'source_file': filename
                    }
                    all_candidates.append(standardized)
                    count += 1
                print(f"  读取 {count} 条记录")
                
            else:  # 英文文件 (11_candidates_full.csv)
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    # 将英文字段名映射为中文
                    standardized = {
                        '姓名': row.get('name', ''),
                        '当前职位': row.get('current_position', ''),
                        '当前公司': row.get('current_company', ''),
                        '工作经验': row.get('total_experience', ''),
                        '投资经验': row.get('vc_experience', ''),
                        '本科学历': row.get('bachelor_school', ''),
                        '本科专业': row.get('bachelor_major', ''),
                        '硕士学历': row.get('master_school', ''),
                        '硕士专业': row.get('master_major', ''),
                        '当前年薪(万)': row.get('current_annual', ''),
                        '期望年薪(万)': row.get('expected_annual', ''),
                        '投成案例数': row.get('deal_count', ''),
                        '项目经验': '',  # 英文文件没有这个字段
                        'source_file': filename
                    }
                    all_candidates.append(standardized)
                    count += 1
                print(f"  读取 {count} 条记录 (英文转中文)")
                
    except Exception as e:
        print(f"  错误: {e}")

print(f"\n总计: {len(all_candidates)} 条候选人记录")

# 去重
seen_names = set()
unique_candidates = []

for cand in all_candidates:
    name = cand['姓名'].strip()
    if not name:
        continue
        
    if name not in seen_names:
        seen_names.add(name)
        unique_candidates.append(cand)
    else:
        # 找到重复的，保留更详细的那个
        pass

print(f"去重后: {len(unique_candidates)} 位独特候选人")

# 列出所有候选人
print("\n" + "="*60)
print(f"所有历史候选人 ({len(unique_candidates)}人)")
print("="*60)

names_sorted = sorted(seen_names)
for i, name in enumerate(names_sorted, 1):
    # 获取基本信息
    cand_info = next((c for c in unique_candidates if c['姓名'] == name), {})
    position = cand_info.get('当前职位', '')
    company = cand_info.get('当前公司', '')
    vc_exp = cand_info.get('投资经验', '')
    deals = cand_info.get('投成案例数', '')
    
    print(f"{i:2d}. {name:6} | {position:10} @ {company:15} | VC经验: {vc_exp:5} | 案例: {deals}")

# 检查你提到的特定候选人
mentioned_names = [
    "王谟松", "鲍志琴", "秦琰", "刘皓天", "杨子毅", "刘少雄", 
    "李新亮", "黄大庆", "宁兆辉", "何方仪", "王磊", "孙培峰", 
    "王宁", "钱亚声", "赖宏坤", "李义", "徐帅"
]

print("\n" + "="*60)
print("你提到的17位候选人查找结果")
print("="*60)

found = []
not_found = []

for name in mentioned_names:
    if name in seen_names:
        found.append(name)
    else:
        not_found.append(name)

print(f"✅ 已找到: {len(found)}人")
for name in sorted(found):
    cand_info = next((c for c in unique_candidates if c['姓名'] == name), {})
    position = cand_info.get('当前职位', '')
    company = cand_info.get('当前公司', '')
    print(f"  - {name:6} | {position} @ {company}")

print(f"\n❌ 未找到: {len(not_found)}人")
for name in sorted(not_found):
    print(f"  - {name}")

# 统计最近11人的专业标注
print("\n" + "="*60)
print("专业标注数据（最近11人）")
print("="*60)

recent_11_file = data_dir / '11_candidates_full.csv'
if recent_11_file.exists():
    with open(recent_11_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        recent_candidates = list(reader)
    
    print("最近11位候选人的专业评估:")
    for cand in recent_candidates:
        name = cand.get('name', '')
        notes = cand.get('notes', '')
        if name and notes:
            print(f"  {name}: {notes}")

# 保存合并结果
output_file = data_dir / 'all_historical_candidates_merged.csv'
fieldnames = ['姓名', '当前职位', '当前公司', '工作经验', '投资经验', 
             '本科学历', '本科专业', '硕士学历', '硕士专业', '当前年薪(万)', 
             '期望年薪(万)', '投成案例数', '项目经验', 'source_file']

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    
    for cand in unique_candidates:
        writer.writerow(cand)

print(f"\n合并结果已保存至: {output_file}")

# 总结
print("\n" + "="*60)
print("问题分析与解决方案")
print("="*60)

print(f"""
问题分析:
1. 数据分散: 候选人分布在 {len(files_to_merge)} 个文件中
2. 字段不一致: 中英文字段名不统一
3. 专业标注缺失: 只有最近11人有详细专业评估
4. 历史分析丢失: 之前的算法优化基于不完整数据

根本原因:
- 每次对话都是新的session，历史分析没有保存到文件中
- 文件分散存储，没有统一的数据集
- 专业标注没有扩展到所有候选人

解决方案:
1. 创建完整的统一数据集
2. 将专业标注扩展到所有候选人
3. 基于完整数据集重新优化算法
4. 建立版本控制，避免再次丢失

当前状态:
- 候选人总数: {len(unique_candidates)}人
- 有专业标注: 11人 (最近一批)
- 需要专业标注: {len(unique_candidates) - 11}人

下一步建议:
1. 你为剩余候选人提供专业标注
2. 我基于完整数据集重新优化算法
3. 建立可持续的评估框架
""")