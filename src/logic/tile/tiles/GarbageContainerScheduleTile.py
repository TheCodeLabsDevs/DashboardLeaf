import os
from datetime import datetime
from typing import Dict, List

from flask import Blueprint

from logic.service.ServiceManager import ServiceManager
from logic.service.services.IcsService import CalendarEvent
from logic.tile.Tile import Tile


class GarbageContainerScheduleTile(Tile):
    DATE_FORMAT = '%d.%m. (%a)'

    EXAMPLE_SETTINGS = {
        "path": "path/to/my/calendar.ics",
        "garbageType": "Papier" or "Gelbe Säcke" or "Bioabfall" or "Restabfall"
    }

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, pageName: str) -> Dict:
        icsService = ServiceManager.get_instance().get_service_by_type_name('IcsService')

        cacheKey = f'{pageName}_{self._uniqueName}'
        events = icsService.get_data(cacheKey, self._intervalInSeconds, self._settings)['events']

        eventsForGarbageType = [x for x in events if self._settings['garbageType'] in x.summary]
        nextEvent = self.__find_next_date(eventsForGarbageType)

        nextEventDate = '--.--.'
        if nextEvent:
            nextEventDate = datetime.strftime(nextEvent.start, self.DATE_FORMAT)

        # TODO: set locale for weekday
        # TODO: set icon for garbageType

        return {
            'nextEventDate': nextEventDate
        }

    def __find_next_date(self, events: List[CalendarEvent]) -> CalendarEvent or None:
        now = datetime.now().date()
        for event in events:
            if event.start < now:
                continue
            return event
        return None

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__, nextEventDate=data['nextEventDate'])

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
