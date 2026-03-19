#!/usr/bin/env python3
"""
AI-H 猎头自动化系统 - 完整流程
输入JD → Chrome搜索 → 筛选 → 翻页提取 → 获取链接 → Judge评估 → 飞书表格

使用前提：
1. 用调试模式启动Chrome并登录猎聘：
   taskkill /F /IM chrome.exe
   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\宗璐\chrome-debug-profile"
2. 运行本脚本
"""
import asyncio
import sys
import json
import re
import os
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent))

# ============================================================
# 配置区 - 修改这里输入JD
# ============================================================
JD = """
职位：AI或前沿科技方向投资经理
工作地点：深圳
工作经验：1-5年
学历要求：985理工科本硕、985理工科本科+985商科硕士、海外QS100以内名校
职责：AI/前沿科技领域投资项目研究、尽职调查、投资决策支持
"""

SEARCH_KEYWORDS = ["投资经理", "AI投资", "科技投资"]  # Scout生成或手动指定

FILTERS = {
    "exp_years": ["1-3年", "3-5年"],       # 工作年限
    "current_city": "深圳",                 # 目前城市
    "expect_city": "深圳",                  # 期望城市
    "education": "硕士",                    # 学历
    "school": ["985", "海外留学"],          # 院校要求
}

MAX_PAGES = 5
CDP_URL = "http://127.0.0.1:9222"

JD_REQUIREMENTS = {
    "position": "AI/前沿科技方向投资经理",
    "location": "深圳",
    "experience_years": 3,
    "required_years": 3,
    "education": "985理工科本硕 或 985理工科本科+985商科硕士 或 海外QS100",
    "required_skills": ["投资", "行业研究", "尽职调查", "AI", "科技投资", "VC", "PE", "股权投资"],
    "industry": "AI/前沿科技投资"
}
# ============================================================

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def parse_candidate(raw_text, index):
    clean = re.sub(r'^(今天活跃|在线|\d+天内活跃|隐藏\s*活跃状态|30天内活跃|7天内活跃|3天内活跃)\s*', '', raw_text.strip())
    name_match = re.match(r'([\u4e00-\u9fa5]{2,5}(?:\s*(?:先生|女士))?)', clean)
    name = name_match.group(1).strip() if name_match else f"候选人{index}"
    age_match = re.search(r'(\d+)岁', clean)
    exp_match = re.search(r'工作(\d+)年', clean)
    degree = "硕士" if '硕士' in clean else ("博士" if '博士' in clean else "本科")
    skill_keywords = ['投资', 'PE', 'VC', '行业研究', '尽职调查', 'AI', '人工智能',
                      'CPA', 'CFA', '量化', '科技', '创投', '股权投资', '财务分析', 'python', 'sql']
    skills = [k for k in skill_keywords if k.lower() in clean.lower()]
    schools = re.findall(r'([\u4e00-\u9fa5]{2,8}(?:大学|学院|理工|交通|科技大学))', clean)
    foreign_schools = re.findall(r'([A-Z][a-zA-Z\s]{3,30}(?:University|College|School|Institute))', clean)
    role_match = re.search(r'·\s*([\u4e00-\u9fa5\s/]+?)\s*\d{4}', clean)
    company_match = re.search(r'([\u4e00-\u9fa5A-Za-z\(\)（）\s·]+?)\s*·\s*[\u4e00-\u9fa5\s/]+?\s*\d{4}', clean)
    return {
        "name": name,
        "age": int(age_match.group(1)) if age_match else 0,
        "experience_years": int(exp_match.group(1)) if exp_match else 0,
        "degree": degree,
        "education_level": degree,
        "skills": skills,
        "schools": (schools + foreign_schools)[:2],
        "current_role": role_match.group(1).strip() if role_match else "",
        "current_company": company_match.group(1).strip() if company_match else "",
        "location": "深圳",
        "raw": clean[:300],
        "position": role_match.group(1).strip() if role_match else "",
        "experience": [{"years": int(exp_match.group(1)) if exp_match else 0}]
    }

async def step1_search_and_filter(page):
    """步骤1: 搜索关键词 + 设置筛选条件"""
    log("步骤1: 导航到搜索页面...")
    try:
        btn = await page.query_selector('text=找人')
        if btn:
            await btn.click()
            await page.wait_for_timeout(3000)
        else:
            await page.goto("https://h.liepin.com/search/getConditionItem", wait_until="load", timeout=30000)
            await page.wait_for_timeout(3000)
    except:
        await page.goto("https://h.liepin.com/search/getConditionItem", wait_until="load", timeout=30000)
        await page.wait_for_timeout(3000)

    log(f"填写关键词: {' '.join(SEARCH_KEYWORDS[:3])}")
    inputs = await page.query_selector_all('input')
    keywords = " ".join(SEARCH_KEYWORDS[:3])
    for inp in inputs:
        try:
            if await inp.is_visible():
                placeholder = await inp.get_attribute('placeholder') or ''
                if any(k in placeholder for k in ['关键词', '职位', '搜索', '请输入']) or placeholder == '':
                    await inp.click()
                    await inp.fill(keywords)
                    await page.keyboard.press('Enter')
                    break
        except:
            pass
    await page.wait_for_timeout(3000)

    log("设置筛选条件...")
    # 工作年限
    for yr in FILTERS["exp_years"]:
        try:
            el = await page.query_selector(f'text={yr}')
            if el: await el.click(); await page.wait_for_timeout(500)
        except: pass

    # 目前城市
    try:
        city_el = await page.query_selector('text=目前城市：')
        if city_el:
            parent = await city_el.evaluate_handle('el => el.closest("div, li, section")')
            sz = await parent.query_selector(f'text={FILTERS["current_city"]}')
            if sz: await sz.click(); await page.wait_for_timeout(500)
    except: pass

    # 期望城市
    try:
        city_els = await page.query_selector_all('text=城市')
        for el in city_els:
            parent_text = await el.evaluate('el => el.parentElement.innerText')
            if '期望城市' in parent_text:
                parent = await el.evaluate_handle('el => el.closest("div, li, section")')
                sz = await parent.query_selector(f'text={FILTERS["expect_city"]}')
                if sz: await sz.click(); await page.wait_for_timeout(500); break
    except: pass

    # 学历
    try:
        edu_els = await page.query_selector_all(f'text={FILTERS["education"]}')
        for el in edu_els:
            parent_text = await el.evaluate('el => el.parentElement.innerText')
            if '不限' in parent_text and '本科' in parent_text:
                await el.click(); await page.wait_for_timeout(500); break
    except: pass

    # 院校
    try:
        school_el = await page.query_selector('text=院校要求：')
        if school_el:
            parent = await school_el.evaluate_handle('el => el.closest("div, li, section")')
            for s in FILTERS["school"]:
                el = await parent.query_selector(f'text={s}')
                if el: await el.click(); await page.wait_for_timeout(500)
    except: pass

    await page.wait_for_timeout(2000)
    log("筛选条件设置完成")

async def step2_extract_all_pages(page):
    """步骤2: 翻页提取所有候选人"""
    log("步骤2: 开始翻页提取候选人...")
    all_raw = []

    for page_num in range(1, MAX_PAGES + 1):
        await page.wait_for_timeout(2000)
        cards = await page.query_selector_all('.tlog-common-resume-card')
        log(f"  第{page_num}页: {len(cards)}个候选人")
        for card in cards:
            try:
                text = await card.evaluate('el => el.innerText')
                all_raw.append(text[:400])
            except: pass

        # 找下一页
        next_btn = await page.query_selector(f'li.ant-pagination-item-{page_num + 1}')
        if not next_btn:
            log(f"  已到最后一页（共{page_num}页）")
            break
        await next_btn.click()

    log(f"共提取 {len(all_raw)} 个候选人")
    return all_raw

async def step3_get_links(page, count):
    """步骤3: 点击每个候选人获取简历链接"""
    log("步骤3: 获取候选人简历链接...")
    links = []
    cards = await page.query_selector_all('.tlog-common-resume-card')

    for i, card in enumerate(cards[:count]):
        try:
            async with page.context.expect_page(timeout=8000) as new_page_info:
                await card.click()
            new_page = await new_page_info.value
            await new_page.wait_for_load_state('domcontentloaded', timeout=8000)
            url = new_page.url
            res_id = re.search(r'res_id_encode=([^&]+)', url)
            clean_url = f"https://h.liepin.com/resume/showresumedetail/?res_id_encode={res_id.group(1)}" if res_id else url
            links.append(clean_url)
            log(f"  [{i+1}] 链接获取成功")
            await new_page.wait_for_timeout(2500)
            await new_page.close()
            await page.wait_for_timeout(1500)
        except Exception as e:
            log(f"  [{i+1}] 链接获取失败: {e}")
            links.append('')

    return links

def step4_judge(raw_list):
    """步骤4: Judge评估"""
    log("步骤4: Judge评估...")
    try:
        from enhance_judge_agent import EnhancedJudgeAgent
        judge = EnhancedJudgeAgent()
        parsed = [parse_candidate(raw, i+1) for i, raw in enumerate(raw_list)]
        results = judge.evaluate_batch_candidates(parsed, JD_REQUIREMENTS)
        evals = results.get('candidate_evaluations', [])
        log(f"评估完成，共{len(evals)}个候选人")
        return parsed, evals
    except Exception as e:
        log(f"Judge失败: {e}")
        return [parse_candidate(raw, i+1) for i, raw in enumerate(raw_list)], []

def step5_write_feishu(parsed_list, evals, links):
    """步骤5: 写入飞书表格"""
    import subprocess, sys
    log("步骤5: 写入飞书表格...")

    # 合并数据
    score_map = {}
    for i, e in enumerate(evals):
        score_map[i] = {
            'score': e.get('overall_score', 0),
            'rec': e.get('recommendation', '')
        }

    merged = []
    for i, p in enumerate(parsed_list):
        merged.append({
            'name': p['name'],
            'age': f"{p['age']}岁" if p['age'] else '',
            'exp': f"{p['experience_years']}年" if p['experience_years'] else '',
            'degree': p['degree'],
            'school': p['schools'][0] if p['schools'] else '',
            'company': p['current_company'],
            'role': p['current_role'],
            'score': score_map.get(i, {}).get('score', 0),
            'rec': score_map.get(i, {}).get('rec', ''),
            'link': links[i] if i < len(links) else ''
        })

    with open('pipeline_merged.json', 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    log(f"数据已保存: pipeline_merged.json ({len(merged)}条)")
    return merged

async def main():
    log("="*50)
    log("AI-H 猎头自动化系统启动")
    log("="*50)

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        liepin_pages = [pg for pg in context.pages if 'liepin.com' in pg.url]

        if not liepin_pages:
            log("未找到猎聘页面，新开...")
            page = await context.new_page()
            await page.goto("https://h.liepin.com", wait_until="load", timeout=30000)
        else:
            page = liepin_pages[0]

        log(f"当前页面: {page.url}")

        # 步骤1: 搜索+筛选
        await step1_search_and_filter(page)

        # 步骤2: 翻页提取
        raw_list = await step2_extract_all_pages(page)

        if not raw_list:
            log("未提取到候选人，退出")
            return

        # 步骤3: 获取链接（只取第一页，避免过多请求）
        first_page_count = min(30, len(raw_list))
        links = await step3_get_links(page, first_page_count)
        # 其余页候选人链接留空
        links += [''] * (len(raw_list) - first_page_count)

    # 步骤4: Judge评估
    parsed_list, evals = step4_judge(raw_list)

    # 步骤5: 保存数据
    merged = step5_write_feishu(parsed_list, evals, links)

    log("="*50)
    log(f"流程完成！共处理 {len(merged)} 个候选人")
    log("数据已保存至 pipeline_merged.json")
    log("请运行 write_to_feishu.py 将数据写入飞书表格")
    log("="*50)

if __name__ == "__main__":
    asyncio.run(main())
