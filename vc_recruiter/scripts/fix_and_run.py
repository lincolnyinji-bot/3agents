#!/usr/bin/env python3
# 修复数据格式并运行分析的临时脚本

import csv
import re

def fix_data_format(input_file, output_file):
    """修复数据格式：年+、10+等格式"""
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # 修复每个字段
    for row in rows:
        # 修复 vc_experience
        vc_exp = row['vc_experience']
        if '年+' in vc_exp or '+年' in vc_exp:
            match = re.search(r'(\d+)', vc_exp)
            if match:
                row['vc_experience'] = f"{match.group(1)}年"
        
        # 修复 total_experience
        total_exp = row['total_experience']
        if '年+' in total_exp or '+年' in total_exp:
            match = re.search(r'(\d+)', total_exp)
            if match:
                row['total_experience'] = f"{match.group(1)}年"
        
        # 修复 deal_count
        deal = row['deal_count']
        if '+' in deal:
            match = re.search(r'(\d+)\+', deal)
            if match:
                row['deal_count'] = match.group(1)
        
        # 修复 current_annual
        salary = row['current_annual']
        if '约' in salary:
            match = re.search(r'(\d+)', salary)
            if match:
                row['current_annual'] = f"{match.group(1)}万"
    
    # 写入修复后的文件
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"修复完成！修复了 {len(rows)} 行数据")
    print("修复后的数据：")
    for i, row in enumerate(rows[:3], 1):
        print(f"{i}. {row['name']}: vc_exp={row['vc_experience']}, deal={row['deal_count']}, salary={row['current_annual']}")

if __name__ == "__main__":
    fix_data_format('../data/updated_assessment.csv', '../data/fixed_assessment.csv')
    
    # 现在运行系统
    import subprocess
    print("\n" + "="*70)
    print("运行系统分析...")
    print("="*70)
    
    # 创建临时脚本运行
    with open('../data/updated_assessment.csv.bak', 'w', encoding='utf-8') as bak:
        with open('../data/updated_assessment.csv', 'r', encoding='utf-8') as src:
            bak.write(src.read())
    
    # 用修复后的文件替换原文件
    with open('../data/fixed_assessment.csv', 'r', encoding='utf-8') as src:
        with open('../data/updated_assessment.csv', 'w', encoding='utf-8') as dst:
            dst.write(src.read())
    
    # 运行系统
    subprocess.run(['python3', 'resume_filter_enhanced.py'])