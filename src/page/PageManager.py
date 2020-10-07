import json
import os
from typing import List

from page.Page import Page


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
            json.dump(self._pages, f)

    def save_and_load(self):
        self.__save()
        self._pages = self.__load()

    def add_page(self, index: int, page: Page):
        self._pages.insert(index, page)

    def remove_page(self, index: int):
        del self._pages[index]

    def get_all_pages(self):
        return self._pages
