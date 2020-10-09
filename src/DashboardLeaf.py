import json
import logging
import os

from TheCodeLabs_BaseUtils.DefaultLogger import DefaultLogger
from TheCodeLabs_FlaskUtils.FlaskBaseApp import FlaskBaseApp
from flask import Flask
from flask_socketio import SocketIO

from blueprints import Routes
from logic import Constants
from logic.services.JenkinsSingleJobService import JenkinsSingleJobService
from page.PageManager import PageManager
from tile.TileRegistry import TileRegistry
from tile.TileService import TileService

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class DashboardLeaf(FlaskBaseApp):
    SERVICES = {
        'JenkinsSingleJob': JenkinsSingleJobService
    }

    def __init__(self, appName: str):
        super().__init__(appName, os.path.dirname(__file__), LOGGER, serveRobotsTxt=True)
        self._pageManager = PageManager(Constants.ROOT_DIR)
        self._tileRegistry = TileRegistry('tile.tiles')
        self._socketio = None
        self._tileService = None

    def _create_flask_app(self):
        app = Flask(self._rootDir)
        self._socketio = SocketIO(app)
        logging.getLogger('flask_socketio').setLevel(logging.ERROR)

        @self._socketio.on('refresh', namespace='/update')
        def Refresh(tileName):
            raise NotImplementedError
            # tileService.ForceRefresh(tileName)

        @self._socketio.on('connect', namespace='/update')
        def Connect():
            raise NotImplementedError
            # LOGGER.debug('Client connected')
            # tileService.EmitFromCache()

        self._tileService = self.__register_tiles(app)

        return app

    def _register_blueprints(self, app):
        app.register_blueprint(Routes.construct_blueprint(self._settings, self._pageManager))
        return app

    def __register_tiles(self, app) -> TileService:
        tileService = TileService(self._socketio)

        with open(os.path.join(Constants.ROOT_DIR, 'pageSettings.json'), 'r') as f:
            config = json.load(f)

        # TODO
        for tileConfig in config[0]['tiles']:
            tileType = tileConfig['tileType']
            if tileType not in self._tileRegistry.get_all_available_tile_types():
                LOGGER.error(f'Skipping unknown tile with type "{tileType}"')
                continue

            tile = self._tileRegistry.get_tile_by_type(tileType)(uniqueName=tileConfig['uniqueName'],
                                                                 settings=tileConfig['settings'],
                                                                 intervalInSeconds=tileConfig['intervalInSeconds'])
            tileService.RegisterTile(tile)
            app.register_blueprint(tile.ConstructBlueprint(tileService=tileService))

        tileService.Run()
        return tileService


if __name__ == '__main__':
    website = DashboardLeaf(Constants.APP_NAME)
    website.start_server()
