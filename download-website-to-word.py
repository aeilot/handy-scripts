# Require pypandoc and playwright
import pypandoc
import time
import os
import asyncio
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

# Config
download_list = ['https://hsefz.aeilot.top/fluffy-scientist动物保护协会', 'https://hsefz.aeilot.top/socista社会科学沙龙', 'https://hsefz.aeilot.top/vocaloid社', 'https://hsefz.aeilot.top/数独社', 'https://hsefz.aeilot.top/涟译翻译社', 'https://hsefz.aeilot.top/中国象棋社', 'https://hsefz.aeilot.top/地球科学社', 'https://hsefz.aeilot.top/游泳社', 'https://hsefz.aeilot.top/acg社', 'https://hsefz.aeilot.top/efzgo-围棋社', 'https://hsefz.aeilot.top/efztv', 'https://hsefz.aeilot.top/frc机器人', 'https://hsefz.aeilot.top/girl-upefz', 'https://hsefz.aeilot.top/gk模型社', 'https://hsefz.aeilot.top/i-debate英语辩论社', 'https://hsefz.aeilot.top/incomplete翻唱社', 'https://hsefz.aeilot.top/mit街舞社', 'https://hsefz.aeilot.top/mun模拟联合国', 'https://hsefz.aeilot.top/project-fermat-社', 'https://hsefz.aeilot.top/sage赛智社', 'https://hsefz.aeilot.top/talk-in-efz脱口秀社', 'https://hsefz.aeilot.top/vortex-学生乐队', 'https://hsefz.aeilot.top/一期一会话剧社', 'https://hsefz.aeilot.top/专攻化学实验社',
                 'https://hsefz.aeilot.top/中华历史社', 'https://hsefz.aeilot.top/乒乓社', 'https://hsefz.aeilot.top/剑道社', 'https://hsefz.aeilot.top/吉他社', 'https://hsefz.aeilot.top/天文社', 'https://hsefz.aeilot.top/心理社', 'https://hsefz.aeilot.top/拳击boxing', 'https://hsefz.aeilot.top/排球社', 'https://hsefz.aeilot.top/推理社', 'https://hsefz.aeilot.top/摄影社', 'https://hsefz.aeilot.top/方舟文学社', 'https://hsefz.aeilot.top/晨晖爱乐乐团', 'https://hsefz.aeilot.top/生物化学社', 'https://hsefz.aeilot.top/生物社', 'https://hsefz.aeilot.top/田径社', 'https://hsefz.aeilot.top/科幻社', 'https://hsefz.aeilot.top/篮球社', 'https://hsefz.aeilot.top/网球社', 'https://hsefz.aeilot.top/羽毛球社', 'https://hsefz.aeilot.top/翰墨书法社', 'https://hsefz.aeilot.top/艺创社', 'https://hsefz.aeilot.top/英美剧社', 'https://hsefz.aeilot.top/语晖辩论社', 'https://hsefz.aeilot.top/语言学社', 'https://hsefz.aeilot.top/足球社', 'https://hsefz.aeilot.top/非遗社', 'https://hsefz.aeilot.top/魔方社']


async def run(playwright, link, num):
    chromium = playwright.chromium
    browser = await chromium.launch()
    page = await browser.new_page()
    await page.goto(link)
    htmlContent = await page.content()
    f = open("%d.html" % num, "w", encoding='utf-8')
    f.write(str(htmlContent))
    f.close()
    # await page.emulate_media(media="print")
    # await page.pdf(path=("%d.pdf") % num, scale=0.7)
    html_file = "%d.html" % num
    docx_file = "%d.docx" % num
    pypandoc.convert_file(html_file, "docx", outputfile=docx_file)
    os.remove(html_file)
    await browser.close()


async def main(i):
    async with async_playwright() as playwright:
        link = download_list[i]
        await run(playwright, link, i)

tasks = []

for i in range(len(download_list)):
    tasks.append(asyncio.ensure_future(main(i)))

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))
loop.close()

print("Converted: %d Websites" % len(download_list))
