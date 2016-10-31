# -*- coding: utf-8 -*-
import json
import random
import re
import requests
import sys
from lxml import etree
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

from openpyxl import Workbook

COURSERA_COURSES_XML = 'https://www.coursera.org/sitemap~www~courses.xml'
COURSES_COUNT = 10
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


@handle_requests_library_exceptions
def get_course_info(course_slug: str) -> list:
    """
    Получаем данные по курсу с его веб-страницы, а если их там нет, из API
    :param course_slug:
    :return:
    """
    response = requests.get(course_slug)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('div', class_='title').text
    title = title if title else None

    lang = soup.find('div', class_='language-info').text
    lang = lang if lang else None

    try:
        course_json = soup.select('script[type="application/ld+json"]')[0]
        course_info = json.loads(course_json.text) if course_json else None
        start_date = course_info['hasCourseInstance'][0]['startDate']
    except (KeyError, IndexError):
        start_date = None

    weeks = len(soup.find_all('div', class_='week'))
    weeks = weeks if weeks else None

    ratings = soup.find('div', class_='ratings-text')
    ratings = re.search('\d\.\d', ratings.text) if ratings else None
    ratings = float(ratings.group()) if ratings else None

    return [title, lang, start_date, weeks, ratings]


@handle_requests_library_exceptions
def get_course_info_from_api(course_slug: str) -> dict:
    """
    :param course_slug:
    :return:
    """
    COURSES_API_URL_HEAD = 'https://www.coursera.org/learn/'
    shorted_slug = course_slug.replace(COURSES_API_URL_HEAD, '')
    url = 'https://api.coursera.org/api/courses.v1?q=slug&slug=%s' % \
        shorted_slug + '&fields=name,primaryLanguages,subtitleLanguages,' + \
        'startDate,workload'
    response = requests.get(url)
    response.raise_for_status()
    course = response.json()

    title = course['elements'][0]['name']

    lang = course['elements'][0]['primaryLanguages'] + \
        course['elements'][0]['subtitleLanguages']

    # coursera api дает epoch time в миллисекундах, или строку с описанем даты
    start_date = course['elements'][0]['startDate']
    if start_date:
        try:
            start_date = int(start_date) / 1000
            start_date = time.strftime('%Y-%m-%d ', time.localtime(start_date))
        except ValueError:
            pass

    weeks = course['elements'][0]['workload']

    return dict(title=title, lang=lang, start_date=start_date, weeks=weeks)


def output_courses_info_to_xlsx(courses: list, filepath: str):
    wb = Workbook()
    ws = wb.active
    for course in courses:
        ws.append(course)
    wb.save(filepath)


if __name__ == '__main__':

    enable_win_unicode_console()

    print('Получаем данные по курсам Coursera с сервера')

    courses_urls = get_courses_list(COURSERA_COURSES_XML)
    random.shuffle(courses_urls)
    selected_courses = []
    for course_url in tqdm(courses_urls[:COURSES_COUNT]):
        selected_courses.append(get_course_info(course_url))

    try:
        output_courses_info_to_xlsx(selected_courses, OUTPUT_XSLX_FILENAME)
    except OSError as error:
        print('Ошибка: %s в файле: %s' % (error.strerror, error.filename))
        exit(1)
