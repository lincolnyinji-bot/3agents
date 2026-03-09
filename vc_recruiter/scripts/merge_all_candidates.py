#!/usr/bin/env python3
"""
合并所有历史简历
"""

import csv
import os
from pathlib import Path

print("正在合并所有历史简历...")

# 1. 读取所有CSV文件
data_dir = Path('../data')

# 找到所有候选人CSV文件
candidate_files = [
    'eleven_candidates.csv',
    'three_candidates.csv', 
    'qinyan_corrected.csv',
    'wangmosong_detailed.csv',
    'junior_candidates.csv',
    '11_candidates_full.csv'
]

all_candidates = []

for file in candidate_files:
    filepath = data_dir / file
    if filepath.exists():
        print(f"读取: {file}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 添加文件名标记
                    row['source_file'] = file
                    all_candidates.append(row)
        except Exception as e:
            print(f"  错误: {e}")

print(f"\n共找到 {len(all_candidates)} 条候选人记录")

# 2. 按姓名去重
name_counts = {}
for cand in all_candidates:
    name = cand['姓名']
    name_counts[name] = name_counts.get(name, 0) + 1

duplicates = {name: count for name, count in name_counts.items() if count > 1}
unique_candidates = []

seen_names = set()
for cand in all_candidates:
    name = cand['姓名']
    if name not in seen_names:
        seen_names.add(name)
        unique_candidates.append(cand)

print(f"去重后: {len(unique_candidates)} 位独特候选人")
if duplicates:
    print(f"重复的候选人: {', '.join(duplicates.keys())}")

# 3. 列出所有候选人姓名
print("\n" + "="*60)
print("所有历史候选人列表")
print("="*60)

names_sorted = sorted(seen_names)
for i, name in enumerate(names_sorted, 1):
    print(f"{i:2d}. {name}")

# 4. 按文件来源统计
print("\n" + "="*60)
print("按文件来源统计")
print("="*60)

file_counts = {}
for cand in all_candidates:
    file = cand['source_file']
    file_counts[file] = file_counts.get(file, 0) + 1

for file, count in sorted(file_counts.items()):
    print(f"{file}: {count}人")

# 5. 你提到的特定候选人检查
mentioned_names = [
    "王谟松", "鲍志琴", "秦琰", "刘皓天", "杨子毅", "刘少雄", 
    "李新亮", "黄大庆", "宁兆辉", "何方仪", "王磊", "孙培峰", 
    "王宁", "钱亚声", "赖宏坤", "李义", "徐帅"
]

print("\n" + "="*60)
print("你提到的特定候选人查找结果")
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
    print(f"  - {name}")

print(f"\n❌ 未找到: {len(not_found)}人")
for name in sorted(not_found):
    print(f"  - {name}")

# 6. 保存合并结果
output_file = data_dir / 'all_historical_candidates.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['姓名', '当前职位', '当前公司', '工作经验', '投资经验', 
                 '本科学历', '本科专业', '硕士学历', '硕士专业', '当前年薪(万)', 
                 '期望年薪(万)', '投成案例数', '项目经验', 'source_file']
    
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    
    for cand in unique_candidates:
        # 确保所有字段都存在
        row = {field: cand.get(field, '') for field in fieldnames}
        writer.writerow(row)

print(f"\n合并结果已保存至: {output_file}")

# 7. 读取最近的11人标注数据（用于专业判断）
print("\n" + "="*60)
print("专业判断标注数据（最近11人）")
print("="*60)

if (data_dir / '11_candidates_full.csv').exists():
    with open(data_dir / '11_candidates_full.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        recent_candidates = list(reader)
    
    print(f"最近11位候选人的专业标注:")
    for cand in recent_candidates:
        name = cand['name']
        notes = cand.get('notes', '')
        print(f"{name}: {notes[:50]}...")

print("\n" + "="*60)
print("总结")
print("="*60)
print(f"""
历史简历总数: {len(unique_candidates)}人
你提到的17人: 找到{len(found)}人，缺失{len(not_found)}人

关键发现:
1. 有丰富的训练数据：{len(unique_candidates)}位真实候选人
2. 有专业标注：最近11人有你的详细评估
3. 覆盖各级别：从实习生到合伙人
4. 需要整合：将历史简历与专业标注关联

下一步:
1. 创建完整的训练数据集
2. 将专业标注扩展到所有候选人
3. 基于完整数据集优化算法
""")