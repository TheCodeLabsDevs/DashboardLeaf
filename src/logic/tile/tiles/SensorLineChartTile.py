import os
from typing import Dict

from flask import Blueprint

from logic.service.ServiceManager import ServiceManager
from logic.tile.Tile import Tile


class SensorLineChartTile(Tile):
    UNIT_BY_SENSOR_TYPE = {
        'temperature': '&degC',
        'humidity': '%'
    }

    ICON_BY_SENSOR_TYPE = {
        'temperature': 'wi-thermometer',
        'humidity': 'wi-humidity'
    }

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, pageName: str) -> Dict:
        storageLeafService = ServiceManager.get_instance().get_service_by_type_name('StorageLeafService')
        cacheKey = f'{pageName}_{self._uniqueName}'

        return storageLeafService.get_data(cacheKey, self._intervalInSeconds, self._settings)

    def render(self, data: Dict) -> str:
        sensorType = data['sensorInfo']['type']
        unit = self.UNIT_BY_SENSOR_TYPE.get(sensorType, '')
        icon = self.ICON_BY_SENSOR_TYPE.get(sensorType, '')

        return Tile.render_template(os.path.dirname(__file__), __class__.__name__,
                                    data=data, unit=unit, icon=icon, title=self._settings['title'])

    def construct_blueprint(self, *args, **kwargs):
        return Blueprint('simpleSensorValue_{}'.format(self.get_uniqueName()), __name__)

