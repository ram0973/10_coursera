import asyncio
import os
import urllib.request
import json
import random
import re
from io import BytesIO

import aiohttp
import requests
import sys
from lxml import etree
from bs4 import BeautifulSoup
from tqdm import tqdm
import time


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


def handle_requests_library_exceptions(decorated):
    """
    Декоратор, обрабатывающий ошибки в requests
    :param decorated: Функция, в которой надо отловить requests exceptions
    :return: декоратор
    """
    def decorator(*args, **kwargs):
        try:
            return decorated(*args, **kwargs)
        except ConnectionError:
            print('Ошибка сетевого соединения')
            exit(1)
        except requests.HTTPError as e:
            print('Сервер вернул неудачный код статуса ответа: %s %i' %
                  (e.response.reason, e.response.status_code))
            exit(1)
        except requests.Timeout:
            print('Вышло время ожидания ответа от сервера')
            exit(1)
        except requests.TooManyRedirects:
            print('Слишком много редиректов')
            exit(1)

    return decorator


@handle_requests_library_exceptions
def get_courses_list(url: str) -> list:
    """
    Получаем список url курсов с сервера
    :param url:
    :return:
    """
    response = requests.get(url)
    response.raise_for_status()
    tree = etree.XML(response.content)
    return [element[0].text for element in tree]


import asyncio
import aiohttp
import tqdm

import string
import random


# get content and write it to file
def write_to_file(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)


# a helper coroutine to perform GET requests:
@asyncio.coroutine
def get(*args, **kwargs):
    response = yield from session.request('GET', *args, **kwargs)
    response.release()
    return (yield from response.text())


@asyncio.coroutine
def download_file(url):
    # this routine is protected by a semaphore
    with (yield from r_semaphore):
        content = yield from aiohttp.ensure_future(get(url))

    # create random filename
    length = 10
    file_string = ''.join(random.choice(
        string.ascii_lowercase + string.digits) for _ in range(length)
                          )
    filename = '{}.html'.format(file_string)

    write_to_file(filename, str.encode(content))


# make nice progressbar install it by using `pip install tqdm`
@asyncio.coroutine
def wait_with_progressbar(coros):
    for f in tqdm.tqdm(asyncio.as_completed(coros), total=len(coros)):
        yield from f


if __name__ == '__main__':

    enable_win_unicode_console()

    print('Получаем данные по курсам Coursera с сервера')

    courses_urls = get_courses_list(COURSERA_COURSES_XML)
    random.shuffle(courses_urls)
    courses_urls = courses_urls[:10]
    print(courses_urls)
    # avoid to many requests(coroutines) the same time.
    # limit them by setting semaphores (simultaneous requests)
    r_semaphore = asyncio.Semaphore(1)
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=1))

    coroutines = [download_file(url) for url in courses_urls]

    #eloop = asyncio.get_event_loop()
    eloop = uvloop.new_event_loop()
    asyncio.set_event_loop(eloop)
    eloop.run_until_complete(wait_with_progressbar(coroutines))
    eloop.close()
    session.close()