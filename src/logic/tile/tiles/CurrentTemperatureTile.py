import os
from typing import Dict

from flask import Blueprint

from logic import Helpers
from logic.service.ServiceManager import ServiceManager
from logic.tile.Tile import Tile


class CurrentTemperatureTile(Tile):
    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, pageName: str) -> Dict:
        weatherService = ServiceManager.get_instance().get_service_by_type_name('WeatherService')
        cacheKey = f'{pageName}_{self._uniqueName}'

        fetchIntervalInSeconds = 60 * 10  # query api less often
        weatherData = weatherService.get_data(cacheKey, fetchIntervalInSeconds, self._settings)
        currentWeather = weatherData['current']
        currentTemperature = currentWeather['temp']
        feelsLike = currentWeather['feels_like']

        return {
            'temperature': Helpers.round_to_decimals(currentTemperature, 1),
            'temperatureColor': self.__determine_color_for_temperature(currentTemperature),
            'feelsLike': Helpers.round_to_decimals(feelsLike, 1),
            'feelsLikeColor': self.__determine_color_for_temperature(feelsLike),
            'icon': currentWeather['weather'][0]['id'],
            'windDegrees': currentWeather['wind_deg'],
            'windSpeed': f'{currentWeather["wind_speed"] * 3.6} km/h',
        }

    @staticmethod
    def __determine_color_for_temperature(temperature: float):
        if temperature < 0:
            return 'rgba(75, 123, 236, 1)'
        elif temperature < 10:
            return 'rgba(149, 224, 108, 1)'
        elif temperature < 20:
            return 'rgba(254, 151, 0, 1)',
        else:
            return 'rgba(230, 76, 60, 1)'

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__, data=data)

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
