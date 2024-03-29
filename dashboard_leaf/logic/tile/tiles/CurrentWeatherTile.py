import os
from datetime import datetime
from typing import Dict

import pytz
from flask import Blueprint

from dashboard_leaf.logic import Helpers
from dashboard_leaf.logic.service.ServiceManager import ServiceManager
from dashboard_leaf.logic.tile.Tile import Tile


class CurrentWeatherTile(Tile):
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
        currentWeather = weatherData['current']
        currentTemperature = currentWeather['temp']
        feelsLike = currentWeather['feels_like']
        windSpeed = currentWeather['wind_speed'] * 3.6
        icon = currentWeather['weather'][0]['id']
        sunrise = Helpers.timestamp_to_timezone(currentWeather['sunrise'], timeZone)
        sunset = Helpers.timestamp_to_timezone(currentWeather['sunset'], timeZone)
        isDayTime = Helpers.is_dayTime(sunrise, sunset, datetime.now(tz=timeZone))

        temperatureRounded = Helpers.round_to_decimals(currentTemperature, 1)
        feelsLikeRounded = Helpers.round_to_decimals(feelsLike, 0)

        return {
            'temperature': temperatureRounded,
            'temperatureColor': Helpers.determine_color_for_temperature(float(temperatureRounded)),
            'feelsLike': feelsLikeRounded,
            'feelsLikeColor': Helpers.determine_color_for_temperature(float(feelsLikeRounded)),
            'icon': icon,
            'iconColor': Helpers.determine_color_for_weather_icon(icon, isDayTime),
            'windDegrees': currentWeather['wind_deg'],
            'windSpeed': f'{Helpers.round_to_decimals(windSpeed, 1)} km/h',
            'windSpeedColor': Helpers.determine_color_for_wind(windSpeed),
            'isDayTime': isDayTime,
            'description':  currentWeather['weather'][0]['description']
        }

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__, data=data)

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
