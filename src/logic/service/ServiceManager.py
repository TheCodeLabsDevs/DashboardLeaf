from __future__ import annotations

import logging
from typing import List, Dict

from TheCodeLabs_BaseUtils.MultiCacheKeyService import MultiCacheKeyService

from logic import Constants
from logic.service.ServiceRegistry import ServiceRegistry

LOGGER = logging.getLogger(Constants.APP_NAME)


class ServiceManager:
    """
    Provides access to service instances
    """

    __instance = None

    @staticmethod
    def get_instance() -> ServiceManager:
        if ServiceManager.__instance is None:
            ServiceManager()
        return ServiceManager.__instance

    def __init__(self):
        if ServiceManager.__instance is None:
            self._services = ServiceManager.__instantiate_services()
            ServiceManager.__instance = self
        else:
            raise Exception('This class is a singleton!')

    @staticmethod
    def __instantiate_services() -> Dict[str, MultiCacheKeyService]:
        services = {}
        availableImplementationTypeNames = ServiceRegistry.get_instance().get_all_available_implementation_types()
        for implementationTypeName in availableImplementationTypeNames:
            implementation = ServiceRegistry.get_instance().get_implementation_by_type_name(implementationTypeName)
            services[implementationTypeName] = implementation()
        return services

    def get_service_by_type_name(self, implementationTypeName: str) -> MultiCacheKeyService:
        return self._services[implementationTypeName]

    def get_all_available_service_types(self) -> List[str]:
        return list(self._services.keys())
