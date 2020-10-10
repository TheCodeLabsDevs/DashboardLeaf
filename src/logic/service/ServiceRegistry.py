import logging
from typing import Type

from TheCodeLabs_BaseUtils.MultiCacheKeyService import MultiCacheKeyService

from logic import Constants
from logic.Registry import Registry

LOGGER = logging.getLogger(Constants.APP_NAME)


class ServiceRegistry(Registry):
    """
    Scans for available service implementations and provides access to them via class name
    """

    __instance = None

    @staticmethod
    def get_instance():
        if ServiceRegistry.__instance is None:
            ServiceRegistry()
        return ServiceRegistry.__instance

    def __init__(self):
        if ServiceRegistry.__instance is None:
            super().__init__()
            ServiceRegistry.__instance = self
        else:
            raise Exception("This class is a singleton!")

    def _get_package(self) -> str:
        return 'logic.service.services'

    def _get_implementation_type(self) -> Type:
        return MultiCacheKeyService
