import inspect
import logging
import pkgutil
from typing import List, Type

from TheCodeLabs_BaseUtils import CachedService

from logic import Constants
from logic.tile.Tile import Tile

LOGGER = logging.getLogger(Constants.APP_NAME)


class Registry:
    """
    Scans for available implementations and provides access to them via class name
    """

    def __init__(self, package: str, implementationType: Type):
        self._package = package
        self._implementationType = implementationType
        self._availableImplementations = {}

        self.reload()

    def reload(self):
        self._availableImplementations = self.__scan_package()

    def __scan_package(self):
        availableImplementations = {}
        imported_package = __import__(self._package, fromlist=['blah'])

        for _, pluginName, isPkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not isPkg:
                pluginModule = __import__(pluginName, fromlist=['blah'])
                clsMembers = inspect.getmembers(pluginModule, inspect.isclass)
                for (_, c) in clsMembers:
                    if issubclass(c, self._implementationType) and c is not self._implementationType:
                        availableImplementations[c.__name__] = c
        LOGGER.debug(f'Found {len(availableImplementations)} implementations of type "{self._implementationType}" '
                     f'{list(availableImplementations.keys())}')
        return availableImplementations

    def get_implementation_by_type(self, implementationType: str) -> Type:
        return self._availableImplementations[implementationType]

    def get_all_available_implementation_types(self) -> List[str]:
        return list(self._availableImplementations.keys())
