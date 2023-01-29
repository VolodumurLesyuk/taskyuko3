import datetime
import json
from typing import Dict
from urllib.request import urlopen

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import requests

from config import tg_bot_token, open_weather_token


bot = Bot(token=tg_bot_token)   # Create bot
dp = Dispatcher(bot)


def get_ip_data() -> Dict:
    """
    Send query for display data location
    """
    url = 'http://ipinfo.io/json'
    response = urlopen(url)
    return json.load(response)


def get_coordinates() -> Dict[str, str]:
    """Returns current coordinates using IP address"""
    data = get_ip_data()
    coordinate = dict()
    coordinate["latitude"] = data['loc'].split(',')[0]
    coordinate["longitude"] = data['loc'].split(',')[1]
    return coordinate


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    """
    Start button
    """
    await message.reply("Hello! Send some message")


@dp.message_handler()
async def get_weather(message: types.Message) -> None:
    """
    Main function for take weather
    """
    code_to_smile = { # Create emojy for telegram
        "Clear": "Ясно \U00002600",
        "Clouds": "Хмарно \U00002601",
        "Rain": "Дощ \U00002614",
        "Drizzle": "Дощ \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Сніг \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        location = get_coordinates() # Get coordinates
    except:
        await message.reply("\U00002620 Провір  \U00002620")

    try:
        r = requests.get( # Send request to OpenWeather to take informations
            f"https://api.openweathermap.org/data/2.5/weather?lat={location['latitude']}&lon={location['longitude']}"
            f"&appid={open_weather_token}&units=metric"
        )

        data = r.json() # Convert data to json
        # Get data
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Look at the window, I can't recognize what's there!"
        city = data['name']
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        # Send data to user
        await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
              f"Weather in the settlement: {city}\nTemperature: {cur_weather}C° {wd}\n"
              f"Humidity: {humidity}%\n Wind: {wind} м/с\n"
              f"Sunrise: {sunrise_timestamp}\nSunset: {sunset_timestamp}\nDay length: {length_of_the_day}\n"
              f"***Good day!***"
              )

    except:
        await message.reply("\U00002620 Провір назву населеного пункту \U00002620")


if __name__ == '__main__':
    executor.start_polling(dp)
