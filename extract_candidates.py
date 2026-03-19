import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup
import json
import re

with open('final_results.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

cards = soup.find_all('div', class_='tlog-common-resume-card')
print(f'找到候选人卡片: {len(cards)}个')

candidates = []
for i, card in enumerate(cards):
    try:
        # 姓名
        name_el = card.find(class_=re.compile('name|title'))
        name = name_el.get_text(strip=True) if name_el else '未知'

        # 年龄
        age_el = card.find('span', class_='personal-detail-age')
        age = age_el.get_text(strip=True) if age_el else ''

        # 工作年限
        detail = card.find('div', class_='new-resume-personal-detail')
        detail_text = detail.get_text(' ', strip=True) if detail else ''

        # 当前职位/公司
        job_el = card.find(class_=re.compile('job|position|work'))
        job = job_el.get_text(strip=True) if job_el else ''

        # 学历
        edu_el = card.find(class_=re.compile('edu|degree'))
        edu = edu_el.get_text(strip=True) if edu_el else ''

        # 完整文本
        full_text = card.get_text(' ', strip=True)[:300]

        c = {
            'index': i+1,
            'name': name,
            'age': age,
            'detail': detail_text,
            'full': full_text
        }
        candidates.append(c)
        print(f'\n[{i+1}] {name} | {age} | {detail_text[:80]}')
        print(f'     {full_text[:120]}')
    except Exception as e:
        print(f'[{i+1}] 解析失败: {e}')

with open('candidates_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(candidates, f, ensure_ascii=False, indent=2)

print(f'\n共提取 {len(candidates)} 个候选人，已保存: candidates_extracted.json')
