import os
import random
from typing import Dict

from flask import Blueprint

from logic.service.ServiceManager import ServiceManager
from logic.tile.Tile import Tile


class BoardGameTile(Tile):
    EXAMPLE_SETTINGS_FILE = {
        "games": [
            {
                "name": "Carcassonne",
                "minPlayers": 2,
                "maxPlayers": 6
            }
        ]
    }

    EXAMPLE_SETTINGS = {
        "path": "path/to/my/games.json"
    }

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)
        self._previousRandomGame = None

    def fetch(self, pageName: str) -> Dict:
        jsonService = ServiceManager.get_instance().get_service_by_type_name('JsonService')

        cacheKey = f'{pageName}_{self._uniqueName}_{self._settings["path"]}'
        games = jsonService.get_data(cacheKey, self._intervalInSeconds, self._settings)['data']['games']
        games = sorted(games, key=lambda game: game['name'])

        gamesForTwo = [game for game in games if game['maxPlayers'] == 2 and game['minPlayers'] == 2]
        gamesAtLeastThree = [game for game in games if game['minPlayers'] >= 3]
        gamesForThreeOrMore = [game for game in games if game['maxPlayers'] > 2]

        randomGame = random.choice(games)
        while randomGame == self._previousRandomGame:
            randomGame = random.choice(games)
        self._previousRandomGame = randomGame

        return {
            'gamesForTwo': gamesForTwo,
            'gamesAtLeastThree': gamesAtLeastThree,
            'gamesForThreeOrMore': gamesForThreeOrMore,
            'randomGame': randomGame
        }

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__,
                                    gamesForTwo=data['gamesForTwo'],
                                    gamesAtLeastThree=data['gamesAtLeastThree'],
                                    gamesForThreeOrMore=data['gamesForThreeOrMore'],
                                    randomGame=data['randomGame'])

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
