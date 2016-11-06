# Решение задачи [№10](https://devman.org/challenges/10/) с сайта [devman.org](https://devman.org)

## Условие задачи:

В этой задаче требуется собрать информацию о разных курсах на Курсере, 
привести её в удобный для обработки вид и выгрузить в эксель-файл.

Порядок действий такой:

Вытащить список курсов из [xml-фида](https://www.coursera.org/sitemap~www~courses.xml) 
Курсеры, хотя бы случайные 20. Для парсинга xml подойдёт, например, lxml.
Зайти на страницу курса и вытащить оттуда название, язык, 
ближайшую дату начала, количество недель и среднюю оценку. 
Для получения данных хорошо использовать requests, а для парсинга - beautifulsoup4.
Выгрузить эти данные в xlsx-файл, один курс – одна строка. 
Для работы с эксель-файлами можно использовать openpyxl.
Задача довольно большая и что-то может быть совсем непонятно, 
не работать, не устанавливаться, быть недокументированным и сырым. 
Это нормально. Борись с этим.


## Системные требования

```
Python 3.5.2+
Внешний модуль requests
Внешний модуль win-unicode-console
Внешний модуль lxml
Внешний модуль beautifulsoup4
Внешний модуль openpyxl
Внешний модуль babel
```

## Установка

Windows

Пакет lxml может не установиться, качаем его wheel 
[отсюда](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)
и ставим нужную библиотеку под вашу версию питона вручную,
пример - pip install lxml-3.6.4-cp35-cp35m-win32.whl

```    
git clone https://github.com/ram0973/10_coursera.git
cd 10_coursera
pip install -r requirements.txt
```

Linux
```    
git clone https://github.com/ram0973/10_coursera.git
cd 10_coursera
pip3 install -r requirements.txt
```
    
    
## Описание работы
Пользователь вводит два необязательных аргумента - 
1) mode - способ получения данных - через сайт или через api 
(по умолчанию через сайт),
2) count - число курсов для вывода (по умолчанию 20)

Скрипт загружает url курсов из XML-файла COURSERA_COURSES_XML,
полученные url курсов перемешиваются случайным образом, 
отбирается COURSES_COUNT курсов.

Далее, зависимости от выбранного способа загрузки информации:

Страницы курсов парсятся, или скрипт получает данные из 
(api)[https://building.coursera.org/app-platform/catalog/]   

Далее полученные данные выводятся в файл OUTPUT_XSLX_FILENAME.

## Настройки

```
COURSERA_COURSES_XML - путь к xml-файлу 
COURSES_COUNT - количество курсы для вывода в файл по умолчанию
OUTPUT_XSLX_FILENAME
```

## Запуск

Windows

```
python coursera.py
```
 
Linux

``` 
python3 coursera.py
```
 
## Лицензия

[MIT](http://opensource.org/licenses/MIT)