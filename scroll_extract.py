import asyncio
import sys
import json
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

MAX_PAGES = 5
PAGE_SIZE = 10  # 每页约10个

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = next(pg for pg in context.pages if 'liepin.com' in pg.url)
        await page.bring_to_front()

        all_candidates = []
        prev_count = 0

        for scroll_round in range(MAX_PAGES):
            # 统计当前卡片数
            cards = await page.query_selector_all('.tlog-common-resume-card')
            current_count = len(cards)
            print(f"第{scroll_round+1}轮: 当前{current_count}个候选人")

            if current_count == prev_count and scroll_round > 0:
                print("没有新内容，已到最后一页")
                break

            # 提取当前页新增的卡片
            for i in range(prev_count, current_count):
                try:
                    text = await cards[i].evaluate('el => el.innerText')
                    all_candidates.append({'index': len(all_candidates)+1, 'raw': text[:400]})
                except:
                    pass

            prev_count = current_count

            if scroll_round < MAX_PAGES - 1:
                # 滚动到底部触发加载
                print(f"  滚动加载第{scroll_round+2}页...")
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(3000)  # 等待加载

                # 检查是否有新卡片
                new_cards = await page.query_selector_all('.tlog-common-resume-card')
                if len(new_cards) == current_count:
                    print("  滚动后无新内容，已到末页")
                    break

        print(f"\n共提取 {len(all_candidates)} 个候选人")
        for c in all_candidates:
            import re
            clean = re.sub(r'^(今天活跃|在线|\d+天内活跃|隐藏\s*活跃状态|30天内活跃|7天内活跃|3天内活跃)\s*', '', c['raw'])
            print(f"[{c['index']}] {clean[:80]}")

        with open('all_candidates.json', 'w', encoding='utf-8') as f:
            json.dump(all_candidates, f, ensure_ascii=False, indent=2)
        print(f"\n已保存: all_candidates.json")

asyncio.run(run())
