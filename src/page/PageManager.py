import json
import os
from typing import List, Dict

from page.Page import Page
from page.PageRegistry import PageRegistry


class PageManager:
    def __init__(self, saveFolder: str, pageRegistry: PageRegistry):
        self._saveFolder = saveFolder
        self._pageRegistry = pageRegistry
        self._pageSettingsPath = os.path.join(self._saveFolder, 'pageSettings.json')
        self._pageSettings = self.__load_settings()
        self._pageInstances = self.__create_page_instances()

    def __load_settings(self) -> List[Dict]:
        if not os.path.exists(self._pageSettingsPath):
            self.__save_settings()

        with open(self._pageSettingsPath, encoding='UTF-8') as f:
            return json.load(f)

    def __save_settings(self):
        with open(self._pageSettingsPath, 'w', encoding='UTF-8') as f:
            json.dump(self._pageSettings, f)

    def __create_page_instances(self) -> Dict[str, Page]:
        pageInstances = {}
        for pageSetting in self._pageSettings:
            pageType = pageSetting['pageType']
            uniqueName = pageSetting['uniqueName']
            settings = pageSetting['settings']
            pageInstance = self._pageRegistry.get_page_by_type(pageType)
            pageInstances[uniqueName] = pageInstance(uniqueName, settings)
        return pageInstances

    def save_and_load(self):
        self.__save_settings()
        self._pageSettings = self.__load_settings()
        self._pageInstances = self.__create_page_instances()

    def add_page(self, index: int, pageName: str, uniqueName: str, settings: Dict):
        self._pageSettings.insert(index, {'pageName': pageName, 'uniqueName': uniqueName, 'settings': settings})

    def remove_page(self, index: int):
        del self._pageSettings[index]

    def get_all_available_page_names(self):
        return list(self._pageInstances.keys())

    def get_page_instance_by_name(self, name: str):
        return self._pageInstances[name]