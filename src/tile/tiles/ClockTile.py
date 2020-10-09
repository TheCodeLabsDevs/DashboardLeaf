from datetime import datetime
from typing import Dict

from flask import Blueprint

from tile.Tile import Tile


class ClockTile(Tile):
    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, services: Dict) -> Dict:
        return {'time': datetime.now()}

    def render(self, data: Dict) -> str:
        return f'Current time: {data["time"]}'

    def ConstructBlueprint(self, *args, **kwargs):
        return Blueprint('clock_{}'.format(self.get_uniqueName()), __name__)
