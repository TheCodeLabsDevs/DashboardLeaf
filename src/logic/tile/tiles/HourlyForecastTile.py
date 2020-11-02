import os
from datetime import datetime
from typing import Dict

import pytz
from flask import Blueprint

from logic import Helpers
from logic.service.ServiceManager import ServiceManager
from logic.tile.Tile import Tile


class HourlyForecastTile(Tile):
    EXAMPLE_SETTINGS = {
        "lat": "51.012825",
        "lon": "13.666365",
        "apiKey": "myApiKey",
        "timeZone": "Europe/Berlin"
    }

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, pageName: str) -> Dict:
        weatherService = ServiceManager.get_instance().get_service_by_type_name('WeatherService')

        fetchIntervalInSeconds = 60 * 10  # query api less often

        timeZone = pytz.timezone(self._settings['timeZone'])

        # cache key will be determined in service
        weatherData = weatherService.get_data('', fetchIntervalInSeconds, self._settings)

        sunrise = Helpers.timestamp_to_timezone(weatherData['current']['sunrise'], timeZone)
        sunset = Helpers.timestamp_to_timezone(weatherData['current']['sunset'], timeZone)

        hourData = []
        hourlyForecast = weatherData['hourly']
        for entry in hourlyForecast[:12]:
            timestamp = Helpers.timestamp_to_timezone(entry['dt'], timeZone)

            temperature = entry['temp']
            icon = entry['weather'][0]['id']
            rainProbability = round(entry['pop'] * 100, -1)  # -1 rounds to the next ten
            windSpeed = entry['wind_speed'] * 3.6

            isDayTime = Helpers.is_dayTime(sunrise, sunset, currentTimestamp=timestamp)

            hourData.append({
                'hour': timestamp.strftime('%H'),
                'temperature': Helpers.round_to_decimals(temperature, 0),
                'temperatureColor': Helpers.determine_color_for_temperature(temperature),
                'icon': icon,
                'iconColor': Helpers.determine_color_for_weather_icon(icon, isDayTime),
                'windSpeed': f'{Helpers.round_to_decimals(windSpeed, 0)} km/h',
                'windSpeedColor': Helpers.determine_color_for_wind(windSpeed),
                'rainProbability': f'{Helpers.round_to_decimals(rainProbability, 0)} %',
                'isDayTime': isDayTime
            })

        return {
            'hours': hourData
        }

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__, data=data['hours'])

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
