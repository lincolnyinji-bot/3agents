#!/usr/bin/env python3
"""
AI-H 与 RecruitLite（猎头系统网页端）集成模块
负责将AI-H评估的候选人推送到RecruitLite系统
"""
import requests
import json
import os
from datetime import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

class RecruitLiteClient:
    """RecruitLite API客户端"""
    
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        
    def check_connection(self):
        """检查RecruitLite服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def push_candidates_to_job(self, job_id, candidates):
        """推送候选人到指定职位
        
        Args:
            job_id: 职位ID
            candidates: 候选人列表，每个候选人应包含以下字段：
                - name: 姓名
                - company: 公司
                - title: 职位
                - experience: 经验
                - skills: 技能
                - judge_score: Judge评分
                - judge_grade: Judge等级
                - judge_reason: Judge理由
                - source: 来源（默认'liepin'）
                - raw_data: 原始数据（可选）
        """
        if not candidates:
            print("⚠️ 没有候选人可推送")
            return {"success": False, "message": "没有候选人"}
        
        # 准备请求数据
        payload = {
            "job_id": job_id,
            "candidates": []
        }
        
        for candidate in candidates:
            # 处理skills字段：如果是列表，转换为逗号分隔的字符串
            skills = candidate.get("skills", "")
            if isinstance(skills, list):
                skills = ", ".join(skills)
            
            # 处理title字段：优先使用title，如果没有则使用role
            title = candidate.get("title", "")
            if not title:
                title = candidate.get("role", "未知职位")
            
            # 处理experience字段：优先使用experience，如果没有则使用exp
            experience = candidate.get("experience", "")
            if not experience:
                experience = candidate.get("exp", "")
            
            # 从evaluation字典中提取评分信息
            evaluation = candidate.get("evaluation", {})
            if isinstance(evaluation, dict):
                judge_score = evaluation.get("score", 0)
                judge_reason = evaluation.get("recommendation", "未评估")
                # 从details中提取grade
                details = evaluation.get("details", {})
                if isinstance(details, dict):
                    judge_grade = details.get("recommendation", "C")
                else:
                    judge_grade = "C"
            else:
                judge_score = candidate.get("judge_score", 0)
                judge_grade = candidate.get("judge_grade", "C")
                judge_reason = candidate.get("judge_reason", "未评估")
            
            # 确保有必要的字段
            candidate_data = {
                "name": candidate.get("name", "未知"),
                "company": candidate.get("company", "未知公司"),
                "title": title,
                "experience": experience,
                "skills": skills,
                "judge_score": judge_score,
                "judge_grade": judge_grade,
                "judge_reason": judge_reason,
                "source": candidate.get("source", "liepin"),
                "raw_data": json.dumps(candidate, ensure_ascii=False) if candidate.get("raw_data") is None else candidate.get("raw_data")
            }
            
            # 可选字段
            optional_fields = ["phone", "email", "school", "salary", "history", "education", "notes", "degree", "age"]
            for field in optional_fields:
                if field in candidate:
                    candidate_data[field] = candidate[field]
            
            payload["candidates"].append(candidate_data)
        
        try:
            # 发送请求
            response = requests.post(
                f"{self.api_url}/talents/batch",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"成功推送 {result.get('inserted', 0)} 个候选人到职位 {job_id}")
                print(f"跳过 {result.get('skipped', 0)} 个重复候选人")
                return {
                    "success": True,
                    "inserted": result.get("inserted", 0),
                    "skipped": result.get("skipped", 0),
                    "talent_ids": result.get("talent_ids", [])
                }
            else:
                print(f"推送失败: HTTP {response.status_code}")
                print(f"响应: {response.text}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": response.text
                }
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_urgent_jobs(self):
        """获取紧急职位列表"""
        try:
            response = requests.get(f"{self.api_url}/jobs/urgent", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取紧急职位失败: HTTP {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"获取紧急职位网络错误: {e}")
            return []
    
    def get_job_details(self, job_id):
        """获取职位详情"""
        try:
            response = requests.get(f"{self.api_url}/jobs/{job_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取职位详情失败: HTTP {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"获取职位详情网络错误: {e}")
            return None


def test_connection():
    """测试连接"""
    client = RecruitLiteClient()
    if client.check_connection():
        print("✅ RecruitLite服务可用")
        return True
    else:
        print("❌ RecruitLite服务不可用，请确保已启动服务")
        print("   启动命令: cd recruitlite-api && python app.py")
        return False


def test_push():
    """测试推送功能"""
    client = RecruitLiteClient()
    
    if not client.check_connection():
        print("❌ 无法连接到RecruitLite")
        return False
    
    # 测试数据
    test_candidates = [
        {
            "name": "测试候选人1",
            "company": "测试公司",
            "title": "测试职位",
            "experience": "3年",
            "skills": "Python, Java",
            "judge_score": 85,
            "judge_grade": "A",
            "judge_reason": "技能匹配度高",
            "source": "test"
        },
        {
            "name": "测试候选人2",
            "company": "另一家公司",
            "title": "高级工程师",
            "experience": "5年",
            "skills": "AI, 机器学习",
            "judge_score": 92,
            "judge_grade": "A+",
            "judge_reason": "经验丰富，技术全面",
            "source": "test"
        }
    ]
    
    # 假设职位ID为1
    result = client.push_candidates_to_job(1, test_candidates)
    return result.get("success", False)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='RecruitLite集成测试')
    parser.add_argument('--test-connection', action='store_true', help='测试连接')
    parser.add_argument('--test-push', action='store_true', help='测试推送')
    parser.add_argument('--get-urgent', action='store_true', help='获取紧急职位')
    
    args = parser.parse_args()
    
    if args.test_connection:
        test_connection()
    elif args.test_push:
        test_push()
    elif args.get_urgent:
        client = RecruitLiteClient()
        jobs = client.get_urgent_jobs()
        print(f"找到 {len(jobs)} 个紧急职位:")
        for job in jobs:
            print(f"  ID: {job.get('id')} - {job.get('title')} ({job.get('priority')})")
    else:
        print("请指定一个操作:")
        print("  --test-connection: 测试连接")
        print("  --test-push: 测试推送候选人")
        print("  --get-urgent: 获取紧急职位")