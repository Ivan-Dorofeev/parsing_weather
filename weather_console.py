import argparse
from weather import console_get_card_from_weather_date, console_add_parsing_weather_to_datebase, \
    console_get_weather_from_datebase

parser = argparse.ArgumentParser(description='Прогноз погоды.')
subparser = parser.add_subparsers()

"""Парсинг погоды в базу данных"""
parser_weather_date = subparser.add_parser('date')
parser_weather_date.set_defaults(func=console_add_parsing_weather_to_datebase)

"""Вывести погоду по датам"""
parser_show_forecast = subparser.add_parser('show')
parser_show_forecast.set_defaults(func=console_get_weather_from_datebase)

"""Вывести картинку погоды"""
parser_weather_card = subparser.add_parser('card')
parser_weather_card.set_defaults(func=console_get_card_from_weather_date)

args = parser.parse_args()
args.func()