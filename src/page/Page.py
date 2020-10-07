from abc import ABC, abstractmethod
from typing import List, Dict

from TheCodeLabs_BaseUtils import CachedService


class Page(ABC):
    """
    Abstract page class. Custom implementations must inherit from this class in order to work.
    Page implementations are dynamically scanned via the PageRegistry.
    """
    def __init__(self, name: str, settings: Dict):
        self._name = name
        self._settings = settings

    # user can choose from dropdown, list, whatever in editor
    @abstractmethod
    def register_services(self) -> List[CachedService]:
        pass

    # user must implement this methods in website textarea in editor
    @abstractmethod
    def fetch(self, services: Dict) -> Dict:
        pass

    @abstractmethod
    def render(self, data: Dict) -> str:
        pass

    def update(self) -> str:
        data = self.fetch({})
        return self.render(data)
