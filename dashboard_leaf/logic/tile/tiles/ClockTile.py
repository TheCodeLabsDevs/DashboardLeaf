import os
from datetime import datetime
from typing import Dict

from flask import Blueprint

from dashboard_leaf.logic.tile.Tile import Tile


class ClockTile(Tile):
    EXAMPLE_SETTINGS = {}

    DATE_FORMAT = '%H:%M:%S'

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, pageName: str) -> Dict:
        return {'time': datetime.strftime(datetime.now(), self.DATE_FORMAT)}

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__, time=data['time'])

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
