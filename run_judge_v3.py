import sys
import json
import re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('C:/Users/宗璐/.openclaw/workspace/3agents')

JD_REQUIREMENTS = {
    "position": "AI/前沿科技方向投资经理",
    "location": "深圳",
    "experience_years": 3,
    "required_years": 3,
    "education": "985理工科本硕 或 985理工科本科+985商科硕士 或 海外QS100",
    "required_skills": ["投资", "行业研究", "尽职调查", "AI", "科技投资", "VC", "PE", "股权投资"],
    "industry": "AI/前沿科技投资"
}

def parse_candidate(raw_text, index):
    # 清理活跃状态前缀
    clean = re.sub(r'^(今天活跃|在线|\d+天内活跃|\d+天内活跃|隐藏\s*活跃状态|30天内活跃|7天内活跃|3天内活跃)\s*', '', raw_text.strip())
    
    # 姓名（中文2-4字，可能带猎/阅标记）
    name_match = re.match(r'([\u4e00-\u9fa5]{2,5}(?:\s*(?:先生|女士))?)', clean)
    name = name_match.group(1).strip() if name_match else f"候选人{index}"
    
    # 年龄
    age_match = re.search(r'(\d+)岁', clean)
    age = int(age_match.group(1)) if age_match else 0
    
    # 工作年限
    exp_match = re.search(r'工作(\d+)年', clean)
    exp_years = int(exp_match.group(1)) if exp_match else 0
    
    # 学历
    degree = "硕士" if '硕士' in clean else ("博士" if '博士' in clean else "本科")
    
    # 技能关键词
    skill_keywords = ['投资', 'PE', 'VC', '行业研究', '尽职调查', 'AI', '人工智能',
                      'CPA', 'CFA', '量化', '科技', '创投', '股权投资', '财务分析',
                      '尽职', '投后管理', '项目评估', 'python', 'sql']
    skills = [k for k in skill_keywords if k.lower() in clean.lower()]
    
    # 学校
    schools = re.findall(r'([\u4e00-\u9fa5]{2,8}(?:大学|学院|理工|交通|科技大学))', clean)
    foreign_schools = re.findall(r'([A-Z][a-zA-Z\s]{3,30}(?:University|College|School|Institute))', clean)
    all_schools = schools[:2] + foreign_schools[:2]
    
    # 当前职位
    role_match = re.search(r'·\s*([\u4e00-\u9fa5\s/]+?)\s*\d{4}', clean)
    current_role = role_match.group(1).strip() if role_match else ""

    return {
        "name": name,
        "age": age,
        "experience_years": exp_years,
        "degree": degree,
        "education_level": degree,
        "skills": skills,
        "schools": all_schools,
        "current_role": current_role,
        "location": "深圳",
        "raw": clean[:300],
        "position": current_role,
        "experience": [{"years": exp_years, "role": current_role}]
    }

with open('final_10_candidates.json', 'r', encoding='utf-8') as f:
    raw_candidates = json.load(f)

from enhance_judge_agent import EnhancedJudgeAgent
judge = EnhancedJudgeAgent()

parsed = [parse_candidate(c['raw'], c['index']) for c in raw_candidates]

# 打印解析结果确认
print("=== 解析结果确认 ===")
for p in parsed:
    print(f"[{p['name']}] {p['age']}岁 {p['experience_years']}年 {p['degree']} 技能:{p['skills'][:3]} 学校:{p['schools'][:2]}")

print("\n=== Judge评估中 ===")
results = judge.evaluate_batch_candidates(parsed, JD_REQUIREMENTS)

# 提取排名
evals = results.get('candidate_evaluations', [])
ranked = sorted(evals, key=lambda x: x.get('overall_score', 0), reverse=True)

print("\n=== 最终排名 ===")
for i, r in enumerate(ranked):
    name = r.get('candidate_info', {}).get('name', '未知')
    score = r.get('overall_score', 0)
    rec = r.get('recommendation', '')
    print(f"#{i+1} {name} | 总分:{score} | {rec}")

with open('judge_ranked.json', 'w', encoding='utf-8') as f:
    json.dump(ranked, f, ensure_ascii=False, indent=2)
print("\n已保存: judge_ranked.json")
