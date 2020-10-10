import logging
from typing import Type

from logic import Constants
from logic.Registry import Registry
from logic.tile.Tile import Tile

LOGGER = logging.getLogger(Constants.APP_NAME)


class TileRegistry(Registry):
    """
    Scans for available tile implementations and provides access to them via class name
    """

    __instance = None

    @staticmethod
    def get_instance():
        if TileRegistry.__instance is None:
            TileRegistry()
        return TileRegistry.__instance

    def __init__(self):
        if TileRegistry.__instance is None:
            super().__init__()
            TileRegistry.__instance = self
        else:
            raise Exception("This class is a singleton!")

    def _get_package(self) -> str:
        return 'logic.tile.tiles'

    def _get_implementation_type(self) -> Type:
        return Tile
