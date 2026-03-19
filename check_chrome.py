import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        contexts = browser.contexts
        print(f'OK contexts: {len(contexts)}')
        if contexts:
            for pg in contexts[0].pages:
                print(f'  page: {pg.url}')

asyncio.run(test())
