import sys
from tqdm import tqdm
import asyncio
import aiohttp
import tqdm
import string
import random
import uvloop

COURSERA_COURSES_XML = 'https://www.coursera.org/sitemap~www~courses.xml'
COURSES_COUNT = 50
OUTPUT_XSLX_FILENAME = 'Coursera_courses.xslx'


def enable_win_unicode_console():
    """
    Включаем правильное отображение unicode в консоли под MS Windows
    """
    if sys.platform == 'win32':
        import win_unicode_console
        win_unicode_console.enable()

async def fetch(url):
    #with asyncio.timeout(TIMEOUT, loop=loop)
    import async_timeout
    with async_timeout.timeout(20, loop=session.loop):
        async with session.get(url) as resp:
            return await resp.text()

async def loop(urls):
    tasks = [fetch(url) for url in urls]
    responses = []
    for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
        responses.append(await f)
    for item in responses:
        print(item[:25])

if __name__ == '__main__':

    enable_win_unicode_console()

    print('Получаем данные по курсам Coursera с сервера')
    courses_urls = [
        'https://www.coursera.org/learn/wharton-marketing',
        'https://www.coursera.org/learn/wealth-planning-capstone',
        'https://www.coursera.org/learn/mikroekonomika',
        'https://www.coursera.org/learn/strategy-law-ethics',
        'https://www.coursera.org/learn/marketing-plan',
        'https://www.coursera.org/learn/python-data-analysis',
        'https://www.coursera.org/learn/upravlinnya-chasom',
        'https://www.coursera.org/learn/upravlenie-lichnymi-finansami',
        'https://www.coursera.org/learn/converter-circuits']

    semaphore = asyncio.Semaphore(5)
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=1))

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    main_loop = asyncio.get_event_loop()
    main_loop.run_until_complete(loop(courses_urls))
    main_loop.close()
    session.close()