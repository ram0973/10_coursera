# -*- coding: utf-8 -*-
import argparse
import os
import random
import requests
from lxml import etree
from tqdm import tqdm
import time
import babel
from openpyxl import Workbook

COURSERA_COURSES_XML = 'https://www.coursera.org/sitemap~www~courses.xml'
COURSERA_API_URL = 'https://api.coursera.org/api/courses.v1'
COURSES_COUNT = 20


def get_courses_list(url):
    response = requests.get(url)
    tree = etree.XML(response.content)
    return [element[0].text for element in tree]


def get_course_info(course_slug):
    slug = course_slug.split('/')[-1]
    url = COURSERA_API_URL
    payload = {'q': 'slug', 'slug': slug, 'includes': 'courseDerivatives',
               'fields': 'name,primaryLanguages,subtitleLanguages,' +
                         'courseDerivatives.v1(averageFiveStarRating),' +
                         'startDate,workload'}
    course = requests.get(url, params=payload).json()
    title = course['elements'][0]['name']
    lang = course['elements'][0]['primaryLanguages'] + \
           course['elements'][0]['subtitleLanguages']
    lang = ', '.join(list(map(
        lambda x: babel.Locale.parse(x, sep='-').display_name, lang)))
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


def output_courses_info_to_xlsx(courses, filepath):
    wb = Workbook()
    ws = wb.active
    for course in courses:
        ws.append(course)
    wb.save(filepath)


def set_file_extension(file_name: str, new_ext: str):
    return '{}.{}'.format(os.path.splitext(file_name)[0], new_ext)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', '--c',
                        help='Courses count', default=COURSES_COUNT, type=int)
    parser.add_argument('--outfile', '--o', help='Output file path',
                        required=True)
    output_file = set_file_extension(parser.parse_args().outfile, 'xlsx')
    courses_count = abs(parser.parse_args().count)
    print('Fetching data on %s Coursera courses' % courses_count)
    courses_urls = get_courses_list(COURSERA_COURSES_XML)
    random.shuffle(courses_urls)
    fetched_courses = []
    for course_url in tqdm(courses_urls[:courses_count]):
        fetched_courses.append(get_course_info(course_url))
    print('Saving to file %s' % output_file)
    output_courses_info_to_xlsx(fetched_courses, output_file)

if __name__ == '__main__':
    main()
