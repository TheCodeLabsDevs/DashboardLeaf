from datetime import datetime
from typing import Dict, List

from TheCodeLabs_BaseUtils import CachedService

from page.Page import Page


class ClockPage(Page):
    def __init__(self, uniqueName: str, settings: Dict):
        super().__init__(uniqueName, settings)

    def register_services(self) -> List[CachedService]:
        pass

    def fetch(self, services: Dict) -> Dict:
        return {'time': datetime.now()}

    def render(self, data: Dict) -> str:
        return f'Current time: {data["time"]}'
