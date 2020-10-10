import logging

from TheCodeLabs_BaseUtils import CachedService

from logic import Constants
from logic.Registry import Registry

LOGGER = logging.getLogger(Constants.APP_NAME)


class ServiceRegistry(Registry):
    """
    Scans for available service implementations and provides access to them via class name
    """

    def __init__(self, package: str):
        super().__init__(package, CachedService)
