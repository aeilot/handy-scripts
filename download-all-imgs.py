# Playwright Required
import os
import urllib.request
from playwright.async_api import async_playwright
import asyncio

# Config
# List of Pages
list = ['https://hsefz.aeilot.top/fluffy-scientist动物保护协会']


async def run(playwright, url):
    chromium = playwright.chromium
    browser = await chromium.launch(headless=True)
    page = await browser.new_page()
    # Go to each page
    await page.goto(url)
    title = await page.title()
    try:
        os.mkdir(title)
    except OSError as error:
        print(error)
    await page.wait_for_selector('img')
    imgs = await page.query_selector_all('img')
    i = 0
    for img in imgs:
        src = await img.get_attribute('src')
        if not src.startswith('http'):
            # TODO: Not Starting with HTTP
            pass
        urllib.request.urlretrieve(src, "%s/%d.png" % (title, i))
        i += 1
    browser.close()


async def main(url):
    async with async_playwright() as playwright:
        await run(playwright, url)

tasks = []

for i in list:
    tasks.append(asyncio.ensure_future(main(i)))

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
