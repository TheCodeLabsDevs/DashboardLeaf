import json
import os
from dataclasses import dataclass
from typing import List

from TheCodeLabs_BaseUtils import CachedService


@dataclass
class VisualPage:
    code: str


@dataclass
class Page:
    visualPage: VisualPage
    services: List[CachedService]


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
