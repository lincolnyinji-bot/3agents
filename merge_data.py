import sys
import json
import re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('C:/Users/宗璐/.openclaw/workspace/3agents')

# 加载数据
with open('final_10_candidates.json', 'r', encoding='utf-8') as f:
    raw_candidates = json.load(f)

with open('candidate_links.json', 'r', encoding='utf-8') as f:
    links = json.load(f)

with open('judge_ranked.json', 'r', encoding='utf-8') as f:
    ranked = json.load(f)

# 建立index->link映射
link_map = {l['index']: l['url'] for l in links}

# 建立index->score映射（ranked顺序对应原始index）
# judge_ranked是按分数排序的，需要重建index->score
score_map = {}
for i, r in enumerate(ranked):
    # ranked里没有原始index，按顺序对应
    score_map[i+1] = {
        'score': r.get('overall_score', 0),
        'recommendation': r.get('recommendation', ''),
        'name': r.get('candidate_info', {}).get('name', '')
    }

# 重新解析候选人基本信息
def parse_name(raw):
    clean = re.sub(r'^(今天活跃|在线|\d+天内活跃|隐藏\s*活跃状态|30天内活跃|7天内活跃|3天内活跃)\s*', '', raw.strip())
    m = re.match(r'([\u4e00-\u9fa5]{2,5}(?:\s*(?:先生|女士))?)', clean)
    return m.group(1).strip() if m else '未知'

def parse_field(raw, pattern, default=''):
    m = re.search(pattern, raw)
    return m.group(1) if m else default

# 组合最终数据
final_data = []
for c in raw_candidates:
    idx = c['index']
    raw = c['raw']
    
    name = parse_name(raw)
    age = parse_field(raw, r'(\d+)岁', '')
    exp = parse_field(raw, r'工作(\d+)年', '')
    degree = '硕士' if '硕士' in raw else ('博士' if '博士' in raw else '本科')
    
    # 当前公司职位
    role_match = re.search(r'([\u4e00-\u9fa5\(\)（）\s·]+?)\s*·\s*([\u4e00-\u9fa5\s/]+?)\s*\d{4}', raw)
    company = role_match.group(1).strip() if role_match else ''
    role = role_match.group(2).strip() if role_match else ''
    
    # 学校
    schools = re.findall(r'([\u4e00-\u9fa5]{2,8}(?:大学|学院))', raw)
    foreign = re.findall(r'([A-Z][a-zA-Z\s]{3,25}(?:University|College|School|Institute))', raw)
    school = (schools + foreign)[0] if (schools or foreign) else ''
    
    # judge分数（按ranked顺序，需要匹配名字）
    judge_score = 0
    judge_rec = ''
    for r in ranked:
        rname = r.get('candidate_info', {}).get('name', '')
        if rname and rname in name or name in rname:
            judge_score = r.get('overall_score', 0)
            judge_rec = r.get('recommendation', '')
            break
    if not judge_score:
        # 按index顺序取
        if idx <= len(ranked):
            judge_score = ranked[idx-1].get('overall_score', 0)
            judge_rec = ranked[idx-1].get('recommendation', '')

    final_data.append({
        'index': idx,
        'name': name,
        'age': age,
        'exp': f"{exp}年" if exp else '',
        'degree': degree,
        'school': school,
        'company': company,
        'role': role,
        'score': judge_score,
        'recommendation': judge_rec,
        'link': link_map.get(idx, '')
    })

with open('final_merged.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print("合并完成，预览:")
for d in final_data:
    print(f"[{d['index']}] {d['name']} | {d['age']}岁 {d['exp']} {d['degree']} | {d['school']} | 分:{d['score']} {d['recommendation']}")
    print(f"     链接: {d['link'][:60]}")
