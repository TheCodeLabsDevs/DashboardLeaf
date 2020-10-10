import os
from datetime import datetime, timedelta
from typing import Dict

from flask import Blueprint

from logic.service.ServiceManager import ServiceManager
from logic.tile.Tile import Tile


class SensorLineChartTile(Tile):
    EXAMPLE_SETTINGS = {
        "title": "My Room",
        "url": "http://127.0.0.1:10003",
        "sensorID": 1,
        "numberOfHoursToShow": 4
    }

    UNIT_BY_SENSOR_TYPE = {
        'temperature': '&degC',
        'humidity': '%'
    }

    ICON_BY_SENSOR_TYPE = {
        'temperature': 'wi-thermometer',
        'humidity': 'wi-humidity'
    }

    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, pageName: str) -> Dict:
        storageLeafService = ServiceManager.get_instance().get_service_by_type_name('StorageLeafService')
        cacheKey = f'{pageName}_{self._uniqueName}'

        serviceSettings = {
            'url': self._settings['url'],
            'sensorID': self._settings['sensorID'],
            'fetchType': 'all'
        }
        return storageLeafService.get_data(cacheKey, self._intervalInSeconds, serviceSettings)

    def render(self, data: Dict) -> str:
        sensorType = data['sensorInfo']['type']
        unit = self.UNIT_BY_SENSOR_TYPE.get(sensorType, '')
        icon = self.ICON_BY_SENSOR_TYPE.get(sensorType, '')

        timeLimit = datetime.now() - timedelta(hours=self._settings['numberOfHoursToShow'])

        x = []
        y = []
        for measurement in data['sensorValue']:
            timestamp = measurement['timestamp']
            parsedTime = datetime.strptime(timestamp, self.DATE_FORMAT)
            if parsedTime < timeLimit:
                break
            x.append(timestamp)
            y.append(measurement['value'])
        x.reverse()
        y.reverse()
        print(f'Filtered {len(data["sensorValue"])} to {len(x)}')
        latest = y[0] if y else '-.-'

        return Tile.render_template(os.path.dirname(__file__), __class__.__name__,
                                    x=x, y=y, latest=latest, unit=unit, icon=icon, title=self._settings['title'])

    def construct_blueprint(self, *args, **kwargs):
        return Blueprint('simpleSensorValue_{}'.format(self.get_uniqueName()), __name__)
