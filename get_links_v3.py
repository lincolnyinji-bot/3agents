import asyncio
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = next(pg for pg in context.pages if 'liepin.com' in pg.url)
        await page.bring_to_front()

        cards = await page.query_selector_all('.tlog-common-resume-card')
        print(f"共{len(cards)}个候选人，逐一点击获取链接...")

        links = []
        for i, card in enumerate(cards):
            try:
                async with context.expect_page(timeout=8000) as new_page_info:
                    await card.click()
                new_page = await new_page_info.value
                await new_page.wait_for_load_state('domcontentloaded', timeout=8000)
                url = new_page.url
                # 提取res_id_encode作为简洁标识
                import re
                res_id = re.search(r'res_id_encode=([^&]+)', url)
                clean_url = f"https://h.liepin.com/resume/showresumedetail/?res_id_encode={res_id.group(1)}" if res_id else url
                links.append({'index': i+1, 'url': clean_url})
                print(f"[{i+1}] {clean_url[:80]}")
                await new_page.wait_for_timeout(2500)  # 模拟人类阅读时间
                await new_page.close()
                await page.wait_for_timeout(1500)  # 关闭后间隔
            except Exception as e:
                print(f"[{i+1}] 失败: {e}")
                links.append({'index': i+1, 'url': ''})

        with open('candidate_links.json', 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=2)
        print(f"\n已保存: candidate_links.json ({len(links)}条)")

asyncio.run(run())
