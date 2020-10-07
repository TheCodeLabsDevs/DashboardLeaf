import json
import os
from typing import List, Dict

from TheCodeLabs_BaseUtils import CachedService


class Page:
    # user can choose from dropdown, list, whatever in website
    def register_services(self) -> List[CachedService]:
        pass

    def is_showing(self) -> bool:
        pass

    def update(self):
        data = self.fetch({})
        self.render(data)

    # user must implement this methods in website textarea
    def fetch(self, services: Dict) -> Dict:
        pass

    def render(self, params: Dict):
        pass


class PageManager:
    def __init__(self, saveFolder: str):
        self._saveFolder = saveFolder
        self._pageSettingsPath = os.path.join(self._saveFolder, 'pageSettings.json')
        self._pages = self.__load()

    def __load(self) -> List[Page]:
        if not os.path.exists(self._pageSettingsPath):
            self.__save()

        with open(self._pageSettingsPath, encoding='UTF-8') as f:
            return json.load(f)

    def __save(self):
        with open(self._pageSettingsPath, 'w', encoding='UTF-8') as f:
            return json.dump([], f)

    def addPage(self, index: int, page: Page):
        self._pages.insert(index, page)

    def removePage(self, index: int):
        del self._pages[index]
