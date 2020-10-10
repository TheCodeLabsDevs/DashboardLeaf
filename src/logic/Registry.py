import inspect
import logging
import pkgutil
from abc import ABC, abstractmethod
from typing import List, Type

from logic import Constants

LOGGER = logging.getLogger(Constants.APP_NAME)


class Registry(ABC):
    """
    Scans for available implementations and provides access to them via class name.
    Note: The scanning process will not recursively descend into subdirectories.
    """

    __instance = None

    def __init__(self):
        self._availableImplementations = self.__scan_package()

    @abstractmethod
    def _get_package(self) -> str:
        pass

    @abstractmethod
    def _get_implementation_type(self) -> Type:
        pass

    def __scan_package(self):
        availableImplementations = {}
        imported_package = __import__(self._get_package(), fromlist=['blah'])
        implementationType = self._get_implementation_type()

        for _, pluginName, isPkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not isPkg:
                pluginModule = __import__(pluginName, fromlist=['blah'])
                clsMembers = inspect.getmembers(pluginModule, inspect.isclass)
                for (_, c) in clsMembers:
                    if issubclass(c, implementationType) and c is not implementationType:
                        availableImplementations[c.__name__] = c
        LOGGER.debug(f'Found {len(availableImplementations)} implementations of type "{implementationType}" '
                     f'{list(availableImplementations.keys())}')
        return availableImplementations

    def get_implementation_by_type(self, implementationType: str) -> Type:
        return self._availableImplementations[implementationType]

    def get_all_available_implementation_types(self) -> List[str]:
        return list(self._availableImplementations.keys())
