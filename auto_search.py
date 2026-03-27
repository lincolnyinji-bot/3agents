import asyncio
import sys
import json
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

JD_KEYWORDS = ["投资经理", "AI投资", "科技投资", "前沿科技投资", "VC投资"]
LOCATION = "深圳"

async def run():
    print("连接Chrome...")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]

        # 找猎聘页面
        liepin_page = None
        for pg in context.pages:
            if 'liepin.com' in pg.url:
                liepin_page = pg
                break

        if not liepin_page:
            print("未找到猎聘页面，新开一个...")
            liepin_page = await context.new_page()
            await liepin_page.goto("https://h.liepin.com", wait_until="load", timeout=30000)
            await liepin_page.wait_for_timeout(3000)

        print(f"当前页面: {liepin_page.url}")
        await liepin_page.bring_to_front()

        # 截图确认登录状态
        await liepin_page.screenshot(path="step1_current.png")
        print("截图: step1_current.png")

        # 导航到找人页面
        print("导航到搜索页面...")
        try:
            find_btn = await liepin_page.query_selector('text=找人')
            if find_btn:
                await find_btn.click()
                await liepin_page.wait_for_timeout(3000)
                print(f"点击找人后: {liepin_page.url}")
            else:
                await liepin_page.goto("https://h.liepin.com/search/getConditionItem", wait_until="load", timeout=30000)
                await liepin_page.wait_for_timeout(3000)
        except Exception as e:
            print(f"导航失败: {e}")
            await liepin_page.goto("https://h.liepin.com/search/getConditionItem", wait_until="load", timeout=30000)
            await liepin_page.wait_for_timeout(3000)

        await liepin_page.screenshot(path="step2_search_page.png")
        print(f"搜索页面: {liepin_page.url}")
        print("截图: step2_search_page.png")

        # 填写关键词
        keywords = " ".join(JD_KEYWORDS[:3])
        print(f"填写关键词: {keywords}")

        inputs = await liepin_page.query_selector_all('input')
        print(f"找到 {len(inputs)} 个输入框")
        filled = False
        for i, inp in enumerate(inputs):
            try:
                placeholder = await inp.get_attribute('placeholder') or ''
                visible = await inp.is_visible()
                print(f"  [{i}] placeholder='{placeholder}' visible={visible}")
                if visible and any(k in placeholder for k in ['关键词', '职位', '搜索', '请输入']):
                    await inp.click()
                    await inp.fill(keywords)
                    await liepin_page.wait_for_timeout(500)
                    await liepin_page.keyboard.press('Enter')
                    filled = True
                    print(f"已填写到输入框[{i}]")
                    break
            except Exception as e:
                print(f"  [{i}] 失败: {e}")

        if not filled:
            print("未找到匹配输入框，尝试第一个可见输入框")
            for inp in inputs:
                try:
                    if await inp.is_visible():
                        await inp.click()
                        await inp.fill(keywords)
                        await liepin_page.keyboard.press('Enter')
                        filled = True
                        print("已填写到第一个可见输入框")
                        break
                except:
                    pass

        await liepin_page.wait_for_timeout(4000)
        await liepin_page.screenshot(path="step3_results.png")
        print(f"结果页面: {liepin_page.url}")
        print("截图: step3_results.png")

        # 保存页面内容
        content = await liepin_page.content()
        with open("search_results.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("页面已保存: search_results.html")

        print("\n完成！请查看截图确认结果。")

asyncio.run(run())
