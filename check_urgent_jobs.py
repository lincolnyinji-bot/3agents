#!/usr/bin/env python3
"""
检查紧急需求状态
"""
import sqlite3
from datetime import datetime

def check_urgent_jobs():
    """检查紧急需求"""
    try:
        conn = sqlite3.connect('recruitlite.db')
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urgent_jobs'")
        if not cursor.fetchone():
            print("紧急需求表不存在")
            return
        
        # 获取活跃需求
        cursor.execute("SELECT COUNT(*) FROM urgent_jobs WHERE status='active'")
        active_count = cursor.fetchone()[0]
        
        # 获取所有需求
        cursor.execute("SELECT COUNT(*) FROM urgent_jobs")
        total_count = cursor.fetchone()[0]
        
        # 获取最近更新的需求
        cursor.execute("SELECT title, company, created_at FROM urgent_jobs WHERE status='active' ORDER BY created_at DESC LIMIT 3")
        recent_jobs = cursor.fetchall()
        
        print(f"紧急需求状态检查 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"活跃需求: {active_count}个")
        print(f"总需求: {total_count}个")
        
        if recent_jobs:
            print("\n最近活跃需求:")
            for title, company, created_at in recent_jobs:
                print(f"  - {title} ({company}) - 创建于: {created_at}")
        else:
            print("\n暂无活跃紧急需求")
        
        conn.close()
        
        # 判断是否需要执行AI-H
        if active_count > 0:
            print(f"\n[注意] 有{active_count}个活跃紧急需求，建议执行AI-H搜索")
            return True
        else:
            print("\n[完成] 无活跃紧急需求")
            return False
            
    except Exception as e:
        print(f"检查紧急需求时出错: {e}")
        return False

if __name__ == "__main__":
    needs_action = check_urgent_jobs()
    
    # 根据HEARTBEAT规则，有待处理任务则执行
    if needs_action:
        print("\n执行AI-H搜索...")
        # 这里可以调用AI-H Pipeline
        # 暂时只输出提示
        print("提示: 执行 'python aih_pipeline_v3.py' 启动AI-H搜索")
    else:
        print("\n无待处理任务")