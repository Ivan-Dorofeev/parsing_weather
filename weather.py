# -*- coding: utf-8 -*-


import datetime
import os
from urllib.parse import urljoin
import cv2
import peewee
import requests
from PIL import Image, ImageDraw
from bs4 import BeautifulSoup

weather_dict = {}
db = peewee.SqliteDatabase('weather.db')


class BassTable(peewee.Model):
    class Meta:
        database = db


class WeatherDatabase(BassTable):
    """Создадим базу данных"""
    data = peewee.DateField()
    temperature = peewee.CharField()
    forecast = peewee.TextField()


db.create_tables([WeatherDatabase])


class WeatherMaker:
    """для получения и формирования предсказаний"""

    def parsing(self, data):
        """получающий прогноз с выбранного сайта в словарь"""
        today_url = urljoin('https://darksky.net/details/55.7415,37.6156/', str(data) + '/')
        today_url = urljoin(today_url, 'si12/en')
        response = requests.get(today_url)
        if response.status_code == 200:
            html_doc = BeautifulSoup(response.text, features='html.parser')
            forecast = str(html_doc.find_all('p', id='summary'))[17:-5:]
            rain = ', ожидается ' + str(html_doc.find_all('span', {'class': 'num swip'}))[24:25] + 'мм осадков'
            if forecast.find('rain') != -1 or forecast.find('Overcast') != -1 or forecast.find('Rain') != -1:
                forecast = 'Дождливо' + rain
            elif forecast.find('sun') != -1 or forecast.find('Clear') != -1:
                forecast = 'Солнечно'
            elif forecast.find('cloud') != -1:
                forecast = 'Облачно'
            elif forecast.find('snow') != -1:
                forecast = 'light_blue'
            temperature = str(html_doc.find_all('span', {'class': 'temp'}))[-11:-9:]
            weather_dict[str(data)] = temperature, forecast
            return weather_dict


class ImageMaker:

    def gradient(self, color):
        """Рисует изображение шаблона градиент"""
        gradient_image = Image.open('python_snippets/external_data/probe.jpg')
        draw = ImageDraw.Draw(gradient_image)
        choose = {
            'yellow': {'fill': (255, 200, 0), 'r': 255, 'g': 200, 'b': 0},
            'blue': {'fill': (0, 0, 255), 'r': 0, 'g': 0, 'b': 255},
            'light_blue': {'fill': (0, 150, 255), 'r': 0, 'g': 150, 'b': 255},
            'grey': {'fill': (100, 100, 100), 'r': 100, 'g': 100, 'b': 100}
        }
        r = choose[color]['r']
        g = choose[color]['g']
        b = choose[color]['b']
        for i in range(gradient_image.size[0]):
            draw.line((i, 0, i, gradient_image.size[1]), fill=(r, g, b), width=2)
            if i % 2 == 0:
                r += 1
                g += 1
                b += 1
        if not os.path.exists('cards'):
            os.makedirs('cards/weather_cards')
        gradient_image.save('cards/gradient.jpg')
        return gradient_image

    def draw_card(self, date, temp, forecast):
        """Рисует открытку по типу погоды"""

        gradient = str
        pict_weather = str

        if str(forecast).startswith('Дождливо'):
            pict_weather = r'python_snippets/external_data/weather_img/rain.jpg'
            gradient = 'blue'
        elif str(forecast).startswith('Солнечно'):
            pict_weather = r'python_snippets/external_data/weather_img/sun.jpg'
            gradient = 'yellow'
        elif str(forecast).startswith('Облачно'):
            pict_weather = r'python_snippets/external_data/weather_img/cloud.jpg'
            gradient = 'grey'
        elif str(forecast).startswith('Облачно'):
            pict_weather = r'python_snippets/external_data/weather_img/snow.jpg'
            gradient = ''

        self.gradient(color=gradient)
        template = cv2.imread('cards/gradient.jpg')
        picture = cv2.imread(pict_weather)

        y_pic = 40
        x_pic = 10

        """"наложим картинку-погода на шаблон"""
        template[y_pic: picture.shape[0] + y_pic, x_pic: picture.shape[1] + x_pic] = picture

        """"наложим дату на шаблон"""
        cv2.putText(template, date.strftime("%d.%m.%Y"), org=(10, 25), fontFace=cv2.cv2.FONT_HERSHEY_COMPLEX,
                    fontScale=0.8, color=(255, 0, 255))

        """"наложим температуру на шаблон"""
        cv2.putText(template, str(temp) + ' C', org=(250, 50), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1,
                    color=(255, 255, 0))

        """"наложим описание температуры на шаблон"""
        cv2.putText(template, str(forecast), org=(150, 100), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1,
                    color=(255, 255, 0))

        # cv2.imshow('img',template)
        cv2.imwrite(filename=f'cards/weather_cards/{date}.jpg', img=template)
        path = f'cards/weather_cards/{date}.jpg'
        img = Image.open(path)
        img.show()


weather = WeatherMaker()
image = ImageMaker()
weather_datebase = WeatherDatabase()


def input_dates():
    month = int(input('месяц (цифра)= '))
    day = int(input('день начало = '))
    day2 = int(input('день окончание = '))
    date_start = datetime.date(year=2020, month=month, day=day)
    date_end = datetime.date(year=2020, month=month, day=day2 + 1)
    delta_1_day = datetime.timedelta(days=1)
    return date_start, date_end, delta_1_day


def console_add_parsing_weather_to_datebase(weatherclass=weather, weather_db=weather_datebase):
    """Добавление прогнозов за диапазон дат в базу данных"""
    dict_to_db = {}
    get_dates = input_dates()
    date_start = get_dates[0]
    date_end = get_dates[1]
    delta_1_day = get_dates[2]
    while date_start != date_end:
        dict_to_db = weatherclass.parsing(data=date_start)
        date_start = date_start + delta_1_day
    print("dict_to_db = ", dict_to_db)
    for date_to_db, elements_to_db in dict_to_db.items():
        weather_db.get_or_create(
            data=date_to_db,
            temperature=elements_to_db[0],
            forecast=elements_to_db[1],
        )
    query = WeatherDatabase.select().order_by(WeatherDatabase.data)
    query.execute()
    return dict_to_db


def console_get_weather_from_datebase():
    """"Получение прогнозов за диапазон дат из базы"""
    get_dates = input_dates()
    date_start = get_dates[0]
    date_end = get_dates[1]
    delta_1_day = get_dates[2]
    while date_start != date_end:
        for datebase in WeatherDatabase.select().where(WeatherDatabase.data == date_start):
            print(f'{datebase.data} = {datebase.temperature} С, {datebase.forecast}')
        date_start = date_start + delta_1_day


def console_get_card_from_weather_date():
    """Создание открыток из полученных прогнозов"""
    month = int(input('месяц (цифра)= '))
    day = int(input('день = '))
    date_for_card = datetime.date(year=2020, month=month, day=day)
    for elements in WeatherDatabase.select().where(WeatherDatabase.data == date_for_card):
        image.draw_card(date=date_for_card, temp=elements.temperature, forecast=elements.forecast)

# console_add_parsing_weather_to_datebase()
# console_get_weather_from_datebase()
# console_get_card_from_weather_date()
