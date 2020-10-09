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
from tile.TileScheduler import TileScheduler

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class DashboardLeaf(FlaskBaseApp):
    SERVICES = {
        'JenkinsSingleJob': JenkinsSingleJobService
    }

    def __init__(self, appName: str):
        super().__init__(appName, os.path.dirname(__file__), LOGGER, serveRobotsTxt=True)
        self._tileRegistry = TileRegistry('tile.tiles')
        self._tileService = None
        self._pageManager = None

    def _create_flask_app(self):
        app = Flask(self._rootDir)
        socketio = SocketIO(app)

        # TODO
        logging.getLogger('flask_socketio').setLevel(logging.ERROR)

        @socketio.on('refresh', namespace='/update')
        def Refresh(tileName):
            self._tileScheduler.ForceRefresh(tileName)

        @socketio.on('connect', namespace='/update')
        def Connect():
            LOGGER.debug('Client connected')
            self._tileScheduler.EmitFromCache()

        self._tileScheduler = TileScheduler(socketio)
        self._pageManager = PageManager(Constants.ROOT_DIR, self._tileRegistry, self._tileScheduler)
        self._tileScheduler.Run()
        return app

    def _register_blueprints(self, app):
        app.register_blueprint(Routes.construct_blueprint(self._settings, self._pageManager))
        return app


if __name__ == '__main__':
    website = DashboardLeaf(Constants.APP_NAME)
    website.start_server()
