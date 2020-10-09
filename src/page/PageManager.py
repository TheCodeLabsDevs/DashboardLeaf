import json
import logging
import os
from typing import List, Dict

from flask import Flask

from logic import Constants
from page.PageInstance import PageInstance, TileLayoutSettings
from tile import TileScheduler
from tile.TileRegistry import TileRegistry

LOGGER = logging.getLogger(Constants.APP_NAME)


class PageManager:
    """
    Handles the pages and provides access to the corresponding page instances.
    Creates and registers tiles according to settings.
    """

    def __init__(self, settingsFolder: str, tileRegistry: TileRegistry, tileScheduler: TileScheduler, flaskApp: Flask):
        self._settingsFolder = settingsFolder
        self._tileRegistry = tileRegistry
        self._tileScheduler = tileScheduler
        self._flaskApp = flaskApp

        self._pageSettingsPath = os.path.join(self._settingsFolder, 'pageSettings.json')
        self._pageSettings = self.__load_settings()
        self._pageInstances = self.__create_page_instances()

    def __load_settings(self) -> List[Dict]:
        if not os.path.exists(self._pageSettingsPath):
            self.__save_settings()

        with open(self._pageSettingsPath, encoding='UTF-8') as f:
            return json.load(f)

    def __save_settings(self):
        with open(self._pageSettingsPath, 'w', encoding='UTF-8') as f:
            json.dump(self._pageSettings, f)

    def __create_page_instances(self) -> Dict:
        pageInstances = {}
        for pageSetting in self._pageSettings:

            tileLayouts = {}
            for tileSettings in pageSetting['tiles']:
                tileLayouts[tileSettings['uniqueName']] = TileLayoutSettings(x=tileSettings['x'],
                                                                             y=tileSettings['y'],
                                                                             width=tileSettings['width'],
                                                                             height=tileSettings['height'])
                self.__register_tile(tileSettings)

            uniqueName = pageSetting['uniqueName']
            pageInstance = PageInstance(uniqueName, tileLayouts)
            pageInstances[uniqueName] = pageInstance
        return pageInstances

    def __register_tile(self, tileSettings: Dict):
        tileType = tileSettings['tileType']
        if tileType not in self._tileRegistry.get_all_available_tile_types():
            LOGGER.error(f'Skipping unknown tile with type "{tileType}"')
            return

        tile = self._tileRegistry.get_tile_by_type(tileType)(uniqueName=tileSettings['uniqueName'],
                                                             settings=tileSettings['settings'],
                                                             intervalInSeconds=tileSettings['intervalInSeconds'])
        self._tileScheduler.RegisterTile(tile)
        self._flaskApp.register_blueprint(tile.construct_blueprint(tileScheduler=self._tileScheduler))

    def save_and_load(self):
        self.__save_settings()
        self._pageSettings = self.__load_settings()
        # self._pageInstances = self.__create_page_instances()

    def add_page(self, index: int, pageName: str, uniqueName: str, settings: Dict):
        self._pageSettings.insert(index, {'pageName': pageName, 'uniqueName': uniqueName, 'settings': settings})
        self.save_and_load()

    def remove_page(self, index: int):
        del self._pageSettings[index]
        self.save_and_load()

    def get_all_available_page_names(self):
        return [page['uniqueName'] for page in self._pageSettings]

    def get_page_instance_by_name(self, name: str):
        return self._pageInstances[name]
