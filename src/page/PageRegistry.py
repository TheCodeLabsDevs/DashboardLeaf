import inspect
import logging
import pkgutil

from logic import Constants
from page.Page import Page

LOGGER = logging.getLogger(Constants.APP_NAME)


class PageRegistry:
    """
    Scans for available page implementations and provides access to them via class name
    """
    def __init__(self, package: str):
        self._package = package
        self._availablePages = {}
        self.reload()

    def reload(self):
        self._availablePages = self.__scan_package(self._package)

    @staticmethod
    def __scan_package(package: str):
        availablePages = {}
        imported_package = __import__(package, fromlist=['blah'])

        for _, pluginName, isPkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not isPkg:
                pluginModule = __import__(pluginName, fromlist=['blah'])
                clsMembers = inspect.getmembers(pluginModule, inspect.isclass)
                for (_, c) in clsMembers:
                    if issubclass(c, Page) and c is not Page:
                        availablePages[c.__name__] = c
        LOGGER.debug(f'Found {len(availablePages)} pages {list(availablePages.keys())}')
        return availablePages

    def get_page_by_type(self, pageType: str) -> Page:
        return self._availablePages[pageType]
