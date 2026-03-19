import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def run():
    print("连接Chrome...")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = next(pg for pg in context.pages if 'liepin.com' in pg.url)
        await page.bring_to_front()

        # 1. 工作年限已选，确认一下
        print("确认工作年限已选 1-3年 + 3-5年...")

        # 2. 目前城市选深圳
        print("\n设置目前城市: 深圳...")
        try:
            # 找"目前城市"区域下的深圳
            city_section = await page.query_selector('text=目前城市：')
            if city_section:
                parent = await city_section.evaluate_handle('el => el.closest("div, section, li")')
                shenzhen = await parent.query_selector('text=深圳')
                if shenzhen:
                    await shenzhen.click()
                    await page.wait_for_timeout(800)
                    print("  已选: 目前城市-深圳")
                else:
                    print("  未找到深圳选项，尝试直接点击")
                    # 直接找第一个深圳文字在城市区域
                    all_sz = await page.query_selector_all('text=深圳')
                    for el in all_sz:
                        parent_text = await el.evaluate('el => el.closest("div").innerText')
                        if '目前城市' in parent_text or '期望城市' in parent_text:
                            await el.click()
                            await page.wait_for_timeout(800)
                            print("  已选深圳")
                            break
        except Exception as e:
            print(f"  城市设置失败: {e}")

        await page.screenshot(path="filter_city.png")

        # 3. 学历选硕士
        print("\n设置学历: 硕士...")
        try:
            # 找学历区域的硕士
            edu_els = await page.query_selector_all('text=硕士')
            for el in edu_els:
                try:
                    parent_text = await el.evaluate('el => el.parentElement.innerText')
                    if '不限' in parent_text and '本科' in parent_text:
                        await el.click()
                        await page.wait_for_timeout(800)
                        print("  已选: 硕士")
                        break
                except:
                    pass
        except Exception as e:
            print(f"  学历设置失败: {e}")

        await page.screenshot(path="filter_edu.png")

        # 4. 等待结果刷新
        print("\n等待结果刷新...")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="filter_final.png")
        print("截图: filter_final.png")

        # 5. 提取候选人列表
        print("\n提取候选人...")
        candidates = []
        
        # 找候选人卡片
        cards = await page.query_selector_all('.resume-card, .candidate-item, [class*=resume], [class*=candidate]')
        print(f"找到候选人卡片: {len(cards)}个")
        
        if not cards:
            # 尝试其他选择器
            cards = await page.query_selector_all('.info')
            print(f"找到info元素: {len(cards)}个")

        for i, card in enumerate(cards[:10]):
            try:
                text = await card.evaluate('el => el.innerText')
                if len(text) > 20:
                    candidates.append(text[:200])
                    print(f"  候选人[{i}]: {text[:80]}")
            except:
                pass

        # 保存结果
        content = await page.content()
        with open("final_results.html", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n完成！提取到 {len(candidates)} 个候选人，页面已保存: final_results.html")

asyncio.run(run())
