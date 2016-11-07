# -*- coding: utf-8 -*-
import argparse
import json
import os
import random
import re
import requests
import sys
from lxml import etree
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import babel

CONNECT_TIMEOUT = 9
READ_TIMEOUT = 9

from openpyxl import Workbook

COURSERA_COURSES_XML = 'https://www.coursera.org/sitemap~www~courses.xml'
COURSERA_API_URL = 'https://api.coursera.org/api/courses.v1'
COURSES_COUNT = 20


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
        except requests.ConnectionError:
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
    :param url: url XML файла
    :return: список всех url курсов
    """
    response = requests.get(url)
    response.raise_for_status()
    tree = etree.XML(response.content)
    return [element[0].text for element in tree]


def get_course_info(course_slug: str) -> list:
    """
    Получаем данные по курсу с его веб-страницы
    :param course_slug: url курса
    :return: список данных по курсу
    """
    try:
        response = requests.get(course_slug, timeout=(
            CONNECT_TIMEOUT, READ_TIMEOUT))
        response.raise_for_status()
    except (requests.ConnectionError, requests.HTTPError, requests.Timeout,
            requests.TooManyRedirects):
        return [None, None, None, None, None]

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
def get_course_info_from_api(course_slug: str) -> list:
    """
    Получаем данные по курсу из api
    https://building.coursera.org/app-platform/catalog/
    :param course_slug: url курса
    :return: список данных по курсу (без рейтинга)
    """
    slug = course_slug.split('/')[-1]
    url = COURSERA_API_URL
    params = {'q': 'slug', 'slug': slug, 'includes': 'courseDerivatives',
              'fields': 'name,primaryLanguages,subtitleLanguages,' +
                        'courseDerivatives.v1(averageFiveStarRating),' +
                        'startDate,workload'}
    try:
        response = requests.get(url, timeout=(
            CONNECT_TIMEOUT, READ_TIMEOUT), params=params)
        response.raise_for_status()
    except (requests.ConnectionError, requests.HTTPError, requests.Timeout,
            requests.TooManyRedirects):
        return [None, None, None, None, None]

    course = response.json()

    title = course['elements'][0]['name']

    lang = course['elements'][0]['primaryLanguages'] + \
        course['elements'][0]['subtitleLanguages']
    lang = ', '.join(
        list(map(lambda x: babel.Locale.parse(x, sep='-').display_name, lang)))

    # coursera api дает epoch time в миллисекундах, или строку с описанием даты
    start_date = course['elements'][0]['startDate']
    if start_date:
        try:
            start_date = int(start_date) / 1000
            start_date = time.strftime('%Y-%m-%d ', time.localtime(start_date))
        except ValueError:
            pass

    weeks = course['elements'][0]['workload']

    try:
        ratings = course['linked']['courseDerivatives.v1'][0]
        ratings = ratings['averageFiveStarRating']
    except KeyError:
        ratings = None

    return [title, lang, start_date, weeks, ratings]


def output_courses_info_to_xlsx(courses: list, filepath: str):
    """
    Вывводим данные по курсам в файл
    :param courses: список данных по курсам
    :param filepath: путь к файлу
    """
    wb = Workbook()
    ws = wb.active
    for course in courses:
        ws.append(course)
    wb.save(filepath)


def set_file_extension(file_name: str, new_ext: str):
    """ Меняем расширение файла """
    return '{}.{}'.format(os.path.splitext(file_name)[0], new_ext)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', '--m',
                        help='Введите "api" или "html" без кавычек',
                        choices=['api', 'html'],
                        default='api')
    parser.add_argument('--count', '--c',
                        help='Введите количество курсов',
                        default=COURSES_COUNT,
                        type=int)
    parser.add_argument('--outfile', '--o', help='Путь к файлу с результатами',
                        # required=True
                        )

    output_file = parser.parse_args().outfile
    if not output_file:
        print('Ошибка: вы не задали путь к файлу .xlsx')
        parser.print_usage()
        exit(1)
    output_file = set_file_extension(output_file, 'xlsx')

    # тут проверка, целое ли это число будет в argparse
    courses_count = abs(parser.parse_args().count)
    courses_fetch_mode = parser.parse_args().mode

    enable_win_unicode_console()

    print('Получаем данные по %s курсам Coursera' % courses_count)
    courses_urls = get_courses_list(COURSERA_COURSES_XML)

    random.shuffle(courses_urls)
    courses_urls = courses_urls[:courses_count]

    fetched_courses = []
    for course_url in tqdm(courses_urls):
        if courses_fetch_mode == 'api':
            fetched_courses.append(get_course_info_from_api(course_url))
        else:  # courses_fetch_mode == 'html'
            fetched_courses.append(get_course_info(course_url))

    try:
        print('Выводим результаты в файл %s' % output_file)
        output_courses_info_to_xlsx(fetched_courses, output_file)
    except OSError as error:
        print('Ошибка: %s в файле: %s' % (error.strerror, error.filename))
        exit(1)


if __name__ == '__main__':

    main()
