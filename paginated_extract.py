import asyncio
import sys
import json
import re
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

MAX_PAGES = 5

async def extract_page_candidates(page):
    cards = await page.query_selector_all('.tlog-common-resume-card')
    candidates = []
    for card in cards:
        try:
            text = await card.evaluate('el => el.innerText')
            candidates.append(text[:400])
        except:
            pass
    return candidates

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = next(pg for pg in context.pages if 'liepin.com' in pg.url)
        await page.bring_to_front()

        all_candidates = []

        for page_num in range(1, MAX_PAGES + 1):
            print(f"\n第{page_num}页...")
            await page.wait_for_timeout(2000)

            # 提取当前页候选人
            candidates = await extract_page_candidates(page)
            print(f"  提取到 {len(candidates)} 个候选人")
            for c in candidates:
                all_candidates.append({'index': len(all_candidates)+1, 'raw': c})

            # 找下一页按钮
            next_page_num = page_num + 1
            next_btn = await page.query_selector(f'li.ant-pagination-item-{next_page_num}')
            if not next_btn:
                print(f"  没有第{next_page_num}页，结束")
                break

            print(f"  点击第{next_page_num}页...")
            await next_btn.click()
            await page.wait_for_timeout(3000)  # 等待加载

        print(f"\n共提取 {len(all_candidates)} 个候选人")
        with open('all_candidates_paged.json', 'w', encoding='utf-8') as f:
            json.dump(all_candidates, f, ensure_ascii=False, indent=2)
        print("已保存: all_candidates_paged.json")

asyncio.run(run())
