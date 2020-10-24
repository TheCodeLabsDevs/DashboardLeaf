import os
import uuid
from datetime import datetime
from typing import Dict

from flask import Blueprint

from logic import Helpers
from logic.service.ServiceManager import ServiceManager
from logic.tile.Tile import Tile


class SevenDaysForecastTile(Tile):
    EXAMPLE_SETTINGS = {
        "lat": "51.012825",
        "lon": "13.666365",
        "apiKey": "myApiKey"
    }

    DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, pageName: str) -> Dict:
        weatherService = ServiceManager.get_instance().get_service_by_type_name('WeatherService')

        fetchIntervalInSeconds = 60 * 10  # query api less often

        # cache key will be determined in service
        weatherData = weatherService.get_data('', fetchIntervalInSeconds, self._settings)

        forecast = weatherData['daily']

        forecastData = {}
        icons = []
        for day in forecast:
            date = day['dt']
            date = datetime.fromtimestamp(date)
            date = datetime.strftime(date, self.DATE_FORMAT)
            icon = day['weather'][0]['id']
            icons.append(icon)
            forecastData[date] = (int(day['temp']['min']), int(day['temp']['max']))

        minValues = [x[0] for x in forecastData.values()]
        maxValues = [x[1] for x in forecastData.values()]

        return {
            'formattedDates': list(forecastData.keys()),
            'minValues': minValues,
            'maxValues': maxValues,
            'icons': icons
        }

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__,
                                    formattedDates=data['formattedDates'],
                                    minValues=data['minValues'],
                                    maxValues=data['maxValues'],
                                    icons=data['icons'],
                                    chartId=str(uuid.uuid4()))

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
