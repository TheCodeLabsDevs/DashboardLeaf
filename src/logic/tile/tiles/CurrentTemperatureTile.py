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
        return {
            'temperature': Helpers.round_to_decimals(weatherData['current']['temp'], 1),
            'feelsLike': Helpers.round_to_decimals(weatherData['current']['feels_like'], 1)
        }

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__, data=data)

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)