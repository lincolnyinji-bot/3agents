#!/usr/bin/env python3
"""
简单测试RecruitLite API推送
"""
import requests
import json

def test_push():
    """测试推送功能"""
    url = "http://127.0.0.1:5000/api/talents/batch"
    
    # 测试数据
    payload = {
        "job_id": 1,
        "candidates": [
            {
                "name": "测试候选人A",
                "company": "测试公司A",
                "title": "测试工程师",
                "experience": "3年",
                "skills": "Python, Java",
                "judge_score": 85,
                "judge_grade": "A",
                "judge_reason": "技能匹配度高",
                "source": "test"
            }
        ]
    }
    
    try:
        print(f"发送请求到: {url}")
        print(f"请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 推送成功!")
            return True
        else:
            print("❌ 推送失败")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    test_push()