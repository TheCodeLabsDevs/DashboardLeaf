import os
from abc import ABC, abstractmethod
from typing import Dict, Tuple

from jinja2 import Template


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

    @staticmethod
    def render_template(currentDirectory: str, className: str, *args, **kwargs) -> str:
        templatePath = os.path.join(currentDirectory, '{}.html'.format(className))
        with open(templatePath, encoding='utf-8') as f:
            templateHtml = f.read()

        return Template(templateHtml).render(*args, **kwargs)

    @abstractmethod
    def fetch(self, pageName: str) -> Dict:
        pass

    @abstractmethod
    def render(self, data: Dict) -> str:
        pass

    def update(self, pageName: str) -> Tuple[str, str]:
        from logic.tile.TileScheduler import TileScheduler

        data = self.fetch(pageName)
        return TileScheduler.get_full_name(pageName, self._uniqueName), self.render(data)

    @abstractmethod
    def construct_blueprint(self, pageName: str, *args, **kwargs):
        pass
