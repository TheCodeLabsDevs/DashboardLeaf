from __future__ import annotations

import logging
from typing import Type

from dashboard_leaf.logic import Constants
from dashboard_leaf.logic.Registry import Registry
from dashboard_leaf.logic.tile.Tile import Tile

LOGGER = logging.getLogger(Constants.APP_NAME)


class TileRegistry(Registry):
    """
    Scans for available tile implementations and provides access to them via class name
    """

    __instance = None

    @staticmethod
    def get_instance() -> TileRegistry:
        if TileRegistry.__instance is None:
            TileRegistry()

        return TileRegistry.__instance

    def __init__(self):
        if TileRegistry.__instance is None:
            super().__init__()
            TileRegistry.__instance = self
            self.__safety_check()
        else:
            raise Exception('This class is a singleton!')

    def _get_package(self) -> str:
        return 'logic.tile.tiles'

    def _get_implementation_type(self) -> Type:
        return Tile

    def __safety_check(self):
        for implementationTypeName in self.get_all_available_implementation_types():
            implementation = self.get_implementation_by_type_name(implementationTypeName)
            if not hasattr(implementation, 'EXAMPLE_SETTINGS'):
                raise AttributeError(f'Missing attribute "EXAMPLE_SETTINGS" in {implementationTypeName}')

