from abc import ABC, abstractmethod
from typing import List, Dict

from TheCodeLabs_BaseUtils import CachedService


class Page(ABC):
    def __init__(self, name: str, settings: Dict):
        self._name = name
        self._settings = settings

    # user can choose from dropdown, list, whatever in website
    @abstractmethod
    def register_services(self) -> List[CachedService]:
        pass

    @abstractmethod
    def is_showing(self) -> bool:
        pass

    # user must implement this methods in website textarea
    @abstractmethod
    def fetch(self, services: Dict) -> Dict:
        pass

    @abstractmethod
    def render(self, params: Dict):
        pass

    def update(self):
        data = self.fetch({})
        self.render(data)
