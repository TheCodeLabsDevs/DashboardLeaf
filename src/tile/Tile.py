from abc import ABC, abstractmethod
from typing import Dict, Tuple


class Tile(ABC):
    """
    Abstract tile class. Custom implementations must inherit from this class in order to work.
    Tile implementations are dynamically scanned via the TileRegistry.
    """

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        self._uniqueName = uniqueName
        self._settings = settings
        self._intervalInSeconds = intervalInSeconds

    def get_uniqueName(self) -> str:
        return self._uniqueName

    def get_intervalInSeconds(self) -> int:
        return self._intervalInSeconds

    @abstractmethod
    def fetch(self, services: Dict) -> Dict:
        pass

    @abstractmethod
    def render(self, data: Dict) -> str:
        pass

    def update(self) -> Tuple[str, str]:
        data = self.fetch({})
        return self._uniqueName, self.render(data)

    @abstractmethod
    def ConstructBlueprint(self, *args, **kwargs):
        pass
