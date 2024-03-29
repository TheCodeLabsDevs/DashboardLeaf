import json
from datetime import datetime

import pytz
import requests

from dashboard_leaf.logic import Constants


def join_url_parts(*args: str) -> str:
    return '/'.join(part.strip('/') for part in args)


def round_to_decimals(value, decimals) -> str:
    return '{:.{}f}'.format(value, decimals)


def determine_color_for_temperature(temperature: float) -> str:
    if temperature < 0:
        return Constants.BLUE.to_rgba()
    elif temperature < 20:
        return Constants.GREEN.to_rgba()
    elif temperature < 25:
        return Constants.ORANGE.to_rgba()
    else:
        return Constants.RED.to_rgba()


def determine_color_for_wind(windSpeed: float) -> str:
    if windSpeed < 20:
        return Constants.WHITE.to_rgba()
    elif windSpeed < 60:
        return Constants.ORANGE.to_rgba()
    else:
        return Constants.RED.to_rgba()


def determine_color_for_weather_icon(iconId: int, isDayTime: bool):
    if 200 <= iconId < 300:  # thunderstorm
        return Constants.RED.to_rgba()
    elif 300 <= iconId < 400:  # drizzle
        return Constants.BLUE.to_rgba()
    elif 500 <= iconId < 600:  # rain
        return Constants.BLUE.to_rgba()
    elif 600 <= iconId < 700:  # snow
        return Constants.WHITE.to_rgba()
    elif 700 <= iconId < 800:  # fog
        return Constants.WHITE.to_rgba()
    elif 800 <= iconId < 802:  # clear or partly cloudy (up to 25%)
        if isDayTime:
            return Constants.ORANGE.to_rgba()
        return Constants.WHITE.to_rgba()
    elif 802 <= iconId < 805:  # clouds > 25%
        return Constants.WHITE.to_rgba()


def is_dayTime(sunrise: datetime, sunset: datetime, currentTimestamp: datetime) -> bool:
    if not currentTimestamp:
        currentTimestamp = datetime.now()
    return sunrise.time() < currentTimestamp.time() < sunset.time()


def timestamp_to_timezone(timestamp: int, timeZone: datetime.tzinfo) -> datetime:
    timestamp = datetime.fromtimestamp(timestamp, pytz.timezone('UTC'))
    return timestamp.astimezone(timeZone)


PUSHBULLET_PUSH_URL = 'https://api.pushbullet.com/v2/pushes'


def send_notification_via_pushbullet(token: str, title: str, body: str):
    data = {
        'type': 'note',
        'title': title,
        'body': body
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(PUSHBULLET_PUSH_URL, data=json.dumps(data), headers=headers)
    if response.status_code != 200:
        raise Exception(f'Error sending notification via pushbullet (status code: "{response.status_code}")')
