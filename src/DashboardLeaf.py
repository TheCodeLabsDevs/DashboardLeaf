import os

from TheCodeLabs_BaseUtils.DefaultLogger import DefaultLogger
from TheCodeLabs_FlaskUtils.FlaskBaseApp import FlaskBaseApp
from flask import Flask
from flask_socketio import SocketIO

from blueprints import Routes
from logic import Constants
from logic.Constants import CONFIG_DIR
from logic.page.PageManager import PageManager
from logic.service.ServiceRegistry import ServiceRegistry
from logic.tile.TileScheduler import TileScheduler

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class DashboardLeaf(FlaskBaseApp):
    def __init__(self, appName: str):
        super().__init__(appName, os.path.dirname(__file__), LOGGER, serveRobotsTxt=True,
                         settingsPath=os.path.join(CONFIG_DIR, 'settings.json'))
        self._tileService = None
        self._pageManager = None
        ServiceRegistry.get_instance()

    def _create_flask_app(self):
        app = Flask(self._rootDir)
        socketio = SocketIO(app)

        @socketio.on('refresh', namespace='/update')
        def Refresh(tileName):
            self._tileScheduler.force_refresh(tileName)

        @socketio.on('connect', namespace='/update')
        def Connect():
            LOGGER.debug('Client connected')
            self._tileScheduler.emit_from_cache()

        self._tileScheduler = TileScheduler(socketio)
        self._pageManager = PageManager(Constants.CONFIG_DIR, self._tileScheduler, app)
        self._tileScheduler.run()
        return app

    def _register_blueprints(self, app):
        app.register_blueprint(Routes.construct_blueprint(self._settings, self._pageManager))
        return app


if __name__ == '__main__':
    website = DashboardLeaf(Constants.APP_NAME)
    website.start_server()
