#!/usr/bin/env python3
"""
AI-H 飞书表格写入
读取 pipeline_merged.json，创建新表格并写入所有候选人数据
需要先运行 aih_pipeline.py 生成数据
"""
import sys
import json
import subprocess
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def run_feishu_write():
    with open('pipeline_merged.json', 'r', encoding='utf-8') as f:
        candidates = json.load(f)

    print(f"准备写入 {len(candidates)} 个候选人到飞书...")
    print("请通过B仔（AI助手）调用飞书API写入数据")
    print("\n候选人数据预览:")
    for c in candidates[:5]:
        print(f"  {c['name']} | {c['age']} {c['exp']} {c['degree']} | {c['school']} | 分:{c['score']} {c['rec']}")
    if len(candidates) > 5:
        print(f"  ... 共{len(candidates)}条")

    print("\n数据已就绪，等待写入飞书表格")

if __name__ == "__main__":
    run_feishu_write()
