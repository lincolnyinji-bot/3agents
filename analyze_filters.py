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
        print(f"当前页面: {page.url}")

        # 先截图看当前筛选状态
        await page.screenshot(path="filter_before.png")

        # 分析页面上的筛选器
        print("\n分析筛选器...")
        
        # 找工作年限筛选
        print("查找工作年限筛选...")
        exp_els = await page.query_selector_all('text=工作年限')
        for el in exp_els:
            try:
                parent = await el.evaluate_handle('el => el.closest(".filter-item, .condition-item, div[class*=filter], div[class*=condition]")')
                text = await parent.evaluate('el => el.innerText')
                print(f"  工作年限区域: {text[:100]}")
            except Exception as e:
                print(f"  工作年限: {e}")

        # 找城市筛选 - 深圳
        print("\n查找城市筛选...")
        shenzhen_els = await page.query_selector_all('text=深圳')
        print(f"  找到深圳相关元素: {len(shenzhen_els)}个")
        for i, el in enumerate(shenzhen_els[:5]):
            try:
                tag = await el.evaluate('el => el.tagName')
                cls = await el.evaluate('el => el.className')
                text = await el.evaluate('el => el.innerText')
                print(f"  [{i}] tag={tag} class={cls[:50]} text={text[:30]}")
            except Exception as e:
                print(f"  [{i}] {e}")

        # 找学历筛选
        print("\n查找学历筛选...")
        edu_els = await page.query_selector_all('text=学历')
        for el in edu_els[:3]:
            try:
                text = await el.evaluate('el => el.parentElement.innerText')
                print(f"  学历区域: {text[:100]}")
            except Exception as e:
                print(f"  学历: {e}")

        # 保存完整页面结构
        content = await page.content()
        with open("filter_page.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("\n页面已保存: filter_page.html")
        await page.screenshot(path="filter_analysis.png")
        print("截图: filter_analysis.png")

asyncio.run(run())
