import os
from typing import Dict

from flask import Blueprint

from logic.service.ServiceManager import ServiceManager
from logic.tile.Tile import Tile


class SimpleSensorValueTile(Tile):
    UNITS_BY_SENSOR_TYPE = {
        'temperature': '&degC',
        'humidity': '%'
    }

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, pageName: str) -> Dict:
        storageLeafService = ServiceManager.get_instance().get_service_by_type_name('StorageLeafService')
        cacheKey = f'{pageName}_{self._uniqueName}'

        return storageLeafService.get_data(cacheKey, self._intervalInSeconds, self._settings)

    def render(self, data: Dict) -> str:
        sensorType = data['sensorInfo']['type']
        unit = self.UNITS_BY_SENSOR_TYPE.get(sensorType, '')

        return Tile.render_template(os.path.dirname(__file__), __class__.__name__, data=data, unit=unit)

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)

