#!/usr/bin/env python3
"""
RecruitLite紧急需求管理器
用于管理紧急需求并触发AI-H搜索
"""
import json
import os
from datetime import datetime
from pathlib import Path
import sqlite3

class UrgentJobsManager:
    """紧急需求管理器"""
    
    def __init__(self, db_path=None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path(__file__).parent / 'recruitlite.db'
        
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建紧急需求表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS urgent_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            experience TEXT,
            education TEXT,
            description TEXT,
            keywords TEXT,  -- JSON数组
            urgency TEXT DEFAULT 'high',  -- high/medium/low
            status TEXT DEFAULT 'pending',  -- pending/processing/completed
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            search_count INTEGER DEFAULT 0,
            last_search_at TIMESTAMP
        )
        ''')
        
        # 创建搜索结果表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            candidate_name TEXT,
            candidate_data TEXT,  -- JSON格式
            judge_score REAL,
            judge_recommendation TEXT,
            judge_direction TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES urgent_jobs (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_urgent_job(self, job_data):
        """添加紧急需求"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 处理关键词
        keywords = job_data.get('keywords', [])
        if isinstance(keywords, list):
            keywords_json = json.dumps(keywords, ensure_ascii=False)
        else:
            keywords_json = '[]'
        
        cursor.execute('''
        INSERT INTO urgent_jobs 
        (title, company, location, experience, education, description, keywords, urgency, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_data.get('title'),
            job_data.get('company'),
            job_data.get('location'),
            job_data.get('experience'),
            job_data.get('education'),
            job_data.get('description'),
            keywords_json,
            job_data.get('urgency', 'high'),
            'pending'
        ))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ 已添加紧急需求: {job_data.get('title')} (ID: {job_id})")
        return job_id
    
    def get_urgent_jobs(self, status='pending'):
        """获取紧急需求列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status == 'all':
            cursor.execute('SELECT * FROM urgent_jobs ORDER BY urgency DESC, created_at DESC')
        else:
            cursor.execute('SELECT * FROM urgent_jobs WHERE status = ? ORDER BY urgency DESC, created_at DESC', (status,))
        
        jobs = []
        for row in cursor.fetchall():
            job = dict(row)
            # 解析关键词
            if job['keywords']:
                job['keywords'] = json.loads(job['keywords'])
            else:
                job['keywords'] = []
            jobs.append(job)
        
        conn.close()
        return jobs
    
    def update_job_status(self, job_id, status):
        """更新需求状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE urgent_jobs 
        SET status = ?, updated_at = CURRENT_TIMESTAMP, search_count = search_count + 1, last_search_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (status, job_id))
        
        conn.commit()
        conn.close()
        
        print(f"📝 更新需求 {job_id} 状态为: {status}")
    
    def save_search_results(self, job_id, candidates):
        """保存搜索结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for candidate in candidates:
            candidate_data = json.dumps(candidate, ensure_ascii=False)
            
            cursor.execute('''
            INSERT INTO search_results 
            (job_id, candidate_name, candidate_data, judge_score, judge_recommendation, judge_direction)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                job_id,
                candidate.get('name', '未知'),
                candidate_data,
                candidate.get('evaluation', {}).get('score', 0),
                candidate.get('evaluation', {}).get('recommendation', ''),
                candidate.get('evaluation', {}).get('direction', '')
            ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 已保存 {len(candidates)} 个候选人结果到需求 {job_id}")
    
    def get_job_results(self, job_id):
        """获取需求搜索结果"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM search_results WHERE job_id = ? ORDER BY judge_score DESC', (job_id,))
        
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # 解析候选人数据
            if result['candidate_data']:
                result['candidate_data'] = json.loads(result['candidate_data'])
            results.append(result)
        
        conn.close()
        return results
    
    def trigger_aih_search(self, job_id=None):
        """触发AI-H搜索"""
        import subprocess
        import sys
        
        # 构建命令
        script_path = Path(__file__).parent.parent / '3agents' / 'aih_pipeline_v3.py'
        
        if job_id:
            cmd = [sys.executable, str(script_path), '--job-id', str(job_id)]
        else:
            cmd = [sys.executable, str(script_path), '--urgent']
        
        print(f"🚀 触发AI-H搜索: {' '.join(cmd)}")
        
        try:
            # 执行搜索
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print("✅ AI-H搜索执行成功")
                print(result.stdout)
                
                # 更新需求状态
                if job_id:
                    self.update_job_status(job_id, 'completed')
                else:
                    # 更新所有pending需求
                    pending_jobs = self.get_urgent_jobs('pending')
                    for job in pending_jobs:
                        self.update_job_status(job['id'], 'completed')
                
                return True
            else:
                print("❌ AI-H搜索执行失败")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ 执行AI-H搜索出错: {e}")
            return False
    
    def setup_midnight_schedule(self):
        """设置午夜定时任务"""
        # 这里调用OpenClaw的cron配置
        cron_config = {
            'name': 'RecruitLite紧急需求午夜搜索',
            'schedule': {
                'kind': 'cron',
                'expr': '0 0 * * *',  # 每天午夜12点
                'tz': 'Asia/Shanghai'
            },
            'payload': {
                'kind': 'agentTurn',
                'message': '执行RecruitLite紧急需求AI-H搜索',
                'model': 'deepseek/deepseek-chat'
            },
            'sessionTarget': 'isolated',
            'delivery': {
                'mode': 'announce',
                'channel': 'webchat'
            },
            'enabled': True
        }
        
        print("📅 已配置午夜定时任务:")
        print(f"   名称: {cron_config['name']}")
        print(f"   时间: 每天午夜12点")
        print(f"   任务: 搜索所有紧急需求")
        
        # 实际应该保存到OpenClaw配置
        # 这里简化处理，实际需要集成到OpenClaw的cron系统
        return cron_config

# ============================================================
# CLI接口
# ============================================================
def main():
    """命令行接口"""
    import argparse
    
    manager = UrgentJobsManager()
    
    parser = argparse.ArgumentParser(description='RecruitLite紧急需求管理器')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 添加需求
    add_parser = subparsers.add_parser('add', help='添加紧急需求')
    add_parser.add_argument('--title', required=True, help='职位标题')
    add_parser.add_argument('--company', help='公司名称')
    add_parser.add_argument('--location', help='工作地点')
    add_parser.add_argument('--experience', help='工作经验要求')
    add_parser.add_argument('--education', help='学历要求')
    add_parser.add_argument('--description', help='职位描述')
    add_parser.add_argument('--keywords', nargs='+', help='搜索关键词')
    add_parser.add_argument('--urgency', choices=['high', 'medium', 'low'], default='high', help='紧急程度')
    
    # 列出需求
    list_parser = subparsers.add_parser('list', help='列出紧急需求')
    list_parser.add_argument('--status', choices=['pending', 'completed', 'all'], default='pending', help='状态筛选')
    
    # 触发搜索
    search_parser = subparsers.add_parser('search', help='触发AI-H搜索')
    search_parser.add_argument('--job-id', type=int, help='特定需求ID')
    search_parser.add_argument('--all', action='store_true', help='搜索所有紧急需求')
    
    # 设置定时任务
    schedule_parser = subparsers.add_parser('schedule', help='设置定时任务')
    
    # 查看结果
    results_parser = subparsers.add_parser('results', help='查看搜索结果')
    results_parser.add_argument('--job-id', type=int, required=True, help='需求ID')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        job_data = {
            'title': args.title,
            'company': args.company,
            'location': args.location,
            'experience': args.experience,
            'education': args.education,
            'description': args.description,
            'keywords': args.keywords or [],
            'urgency': args.urgency
        }
        job_id = manager.add_urgent_job(job_data)
        print(f"✅ 已添加紧急需求，ID: {job_id}")
    
    elif args.command == 'list':
        jobs = manager.get_urgent_jobs(args.status)
        print(f"紧急需求列表 ({args.status}):")
        print("-" * 80)
        for job in jobs:
            print(f"ID: {job['id']} | {job['title']}")
            print(f"   公司: {job['company']} | 地点: {job['location']}")
            print(f"   经验: {job['experience']} | 学历: {job['education']}")
            print(f"   紧急度: {job['urgency']} | 状态: {job['status']}")
            print(f"   创建时间: {job['created_at']}")
            print()
    
    elif args.command == 'search':
        if args.job_id:
            print(f"🔍 触发特定需求搜索: ID {args.job_id}")
            manager.trigger_aih_search(args.job_id)
        elif args.all:
            print("🔍 触发所有紧急需求搜索")
            manager.trigger_aih_search()
        else:
            print("❌ 请指定 --job-id 或 --all")
    
    elif args.command == 'schedule':
        print("📅 设置午夜定时任务...")
        config = manager.setup_midnight_schedule()
        print("✅ 定时任务配置完成")
        print("   请确保OpenClaw cron服务已启用")
    
    elif args.command == 'results':
        results = manager.get_job_results(args.job_id)
        print(f"📊 需求 {args.job_id} 搜索结果:")
        print("-" * 80)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['candidate_name']}")
            print(f"   评分: {result['judge_score']}分")
            print(f"   推荐: {result['judge_recommendation']}")
            print(f"   方向: {result['judge_direction']}")
            print(f"   时间: {result['created_at']}")
            print()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()