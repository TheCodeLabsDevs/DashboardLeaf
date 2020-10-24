import os
from typing import Dict

from flask import Blueprint

from logic import Helpers
from logic.service.ServiceManager import ServiceManager
from logic.tile.Tile import Tile


class CurrentWeatherTile(Tile):
    EXAMPLE_SETTINGS = {
        "lat": "51.012825",
        "lon": "13.666365",
        "apiKey": "myApiKey"
    }

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, pageName: str) -> Dict:
        weatherService = ServiceManager.get_instance().get_service_by_type_name('WeatherService')

        fetchIntervalInSeconds = 60 * 10  # query api less often

        # cache key will be determined in service
        weatherData = weatherService.get_data('', fetchIntervalInSeconds, self._settings)
        currentWeather = weatherData['current']
        currentTemperature = currentWeather['temp']
        feelsLike = currentWeather['feels_like']
        windSpeed = currentWeather['wind_speed'] * 3.6
        icon = currentWeather['weather'][0]['id']

        return {
            'temperature': Helpers.round_to_decimals(currentTemperature, 1),
            'temperatureColor': Helpers.determine_color_for_temperature(currentTemperature),
            'feelsLike': Helpers.round_to_decimals(feelsLike, 1),
            'feelsLikeColor': Helpers.determine_color_for_temperature(feelsLike),
            'icon': icon,
            'iconColor': Helpers.determine_color_for_weather_icon(icon),
            'windDegrees': currentWeather['wind_deg'],
            'windSpeed': f'{Helpers.round_to_decimals(windSpeed, 1)} km/h',
            'windSpeedColor': Helpers.determine_color_for_wind(windSpeed)
        }

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__, data=data)

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
