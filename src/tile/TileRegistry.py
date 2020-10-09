import inspect
import logging
import pkgutil
from typing import List, Type

from logic import Constants
from tile.Tile import Tile

LOGGER = logging.getLogger(Constants.APP_NAME)


class TileRegistry:
    """
    Scans for available tile implementations and provides access to them via class name
    """

    def __init__(self, package: str):
        self._package = package
        self._availableTiles = {}
        self.reload()

    def reload(self):
        self._availableTiles = self.__scan_package(self._package)

    @staticmethod
    def __scan_package(package: str):
        availableTiles = {}
        imported_package = __import__(package, fromlist=['blah'])

        for _, pluginName, isPkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not isPkg:
                pluginModule = __import__(pluginName, fromlist=['blah'])
                clsMembers = inspect.getmembers(pluginModule, inspect.isclass)
                for (_, c) in clsMembers:
                    if issubclass(c, Tile) and c is not Tile:
                        availableTiles[c.__name__] = c
        LOGGER.debug(f'Found {len(availableTiles)} tiles {list(availableTiles.keys())}')
        return availableTiles

    def get_tile_by_type(self, tileType: str) -> Type[Tile]:
        return self._availableTiles[tileType]

    def get_all_available_tile_types(self) -> List[str]:
        return list(self._availableTiles.keys())
