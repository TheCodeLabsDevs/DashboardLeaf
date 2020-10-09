import os
from datetime import datetime
from typing import Dict

from flask import Blueprint

from tile.Tile import Tile


class ClockTile(Tile):
    DATE_FORMAT = '%H:%M:%S'

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, services: Dict) -> Dict:
        return {'time': datetime.strftime(datetime.now(), self.DATE_FORMAT)}

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__, time=data['time'])

    def ConstructBlueprint(self, *args, **kwargs):
        return Blueprint('clock_{}'.format(self.get_uniqueName()), __name__)
