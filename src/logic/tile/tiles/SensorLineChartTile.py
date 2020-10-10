import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict

from flask import Blueprint

from logic import Constants, Helpers
from logic.service.ServiceManager import ServiceManager
from logic.tile.Tile import Tile

LOGGER = logging.getLogger(Constants.APP_NAME)


class SensorLineChartTile(Tile):
    EXAMPLE_SETTINGS = {
        "title": "My Room",
        "url": "http://127.0.0.1:10003",
        "sensorID": 1,
        "numberOfHoursToShow": 4,
        "decimals": 1,
        "lineColor": "rgba(254, 151, 0, 1)",
        "fillColor": "rgba(254, 151, 0, 0.2)"
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
            'fetchType': 'all',
            'fetchLimit': 1000,
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
            value = float(measurement['value'])
            y.append(Helpers.round_to_decimals(value, self._settings['decimals']))

        LOGGER.debug(f'Filtered {len(data["sensorValue"])} to {len(x)} for sensor {self._settings["sensorID"]}')

        x.reverse()
        y.reverse()
        latest = y[0] if y else ''

        return Tile.render_template(os.path.dirname(__file__), __class__.__name__,
                                    x=x, y=y, latest=latest, unit=unit,
                                    icon=icon, title=self._settings['title'],
                                    lineColor=self._settings['lineColor'],
                                    fillColor=self._settings['fillColor'],
                                    chartId=str(uuid.uuid4()))

    def construct_blueprint(self, *args, **kwargs):
        return Blueprint('simpleSensorValue_{}'.format(self.get_uniqueName()), __name__)
