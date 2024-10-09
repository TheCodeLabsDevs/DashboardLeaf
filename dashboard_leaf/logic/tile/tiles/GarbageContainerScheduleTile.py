import os
from datetime import datetime
from typing import Dict, List

from TheCodeLabs_BaseUtils.NtfyHelper import NtfyHelper
from flask import Blueprint
from babel.dates import format_date

from dashboard_leaf.logic import Helpers
from dashboard_leaf.logic.service.ServiceManager import ServiceManager
from dashboard_leaf.logic.service.services.IcsService import CalendarEvent
from dashboard_leaf.logic.tile.Tile import Tile


class GarbageContainerScheduleTile(Tile):
    DATE_FORMAT = 'E dd.MM'

    ICON_BY_GARBAGE_TYPE = {
        'Papier': 'garbage_paper',
        'Papiertonnen': 'garbage_paper',
        'Gelbe Tonne': 'garbage_plastic',
        'Gelbe Säcke': 'garbage_plastic',
        'Bioabfall': 'garbage_bio',
        'Restabfall': 'garbage_waste',
        'Restmülltonnen': 'garbage_waste'
    }

    EXAMPLE_SETTINGS = {
        "path": "path/to/my/calendar.ics",
        "garbageType": "Papier" or "Gelbe Tonne" or "Bioabfall" or "Restabfall",
        "notification": {
            "daysBeforeEvent": 1,
            "hour": 10,
            "enableNotificationViaPushbullet": False,
            "pushbulletToken": None,
            "enableNotificationViaNtfy": False,
            "ntfySettings": {
                "username": "",
                "password": "",
                "baseUrl": "",
                "topicName": ""
            }
        }
    }

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)
        self._lastNotificationDate = None

    def fetch(self, pageName: str) -> Dict:
        icsService = ServiceManager.get_instance().get_service_by_type_name('IcsService')

        cacheKey = f'{pageName}_{self._uniqueName}'
        events = icsService.get_data(cacheKey, self._intervalInSeconds, self._settings)['events']

        eventsForGarbageType = [x for x in events if self._settings['garbageType'] in x.summary]
        eventsForGarbageType.sort(key=lambda event: event.start)

        nextEvent = self.__find_next_date(eventsForGarbageType)

        nextEventDate = '--.--.'
        remainingDays = ''
        if nextEvent:
            nextEventDate = nextEvent.start
            if isinstance(nextEventDate, datetime):
                remainingDays = nextEventDate - self._get_current_date_time()
            else:
                remainingDays = nextEventDate - self._get_current_date_time().date()
            remainingDays = remainingDays.days
            nextEventDate = format_date(nextEventDate, self.DATE_FORMAT, 'de')

        iconName = self.ICON_BY_GARBAGE_TYPE[self._settings['garbageType']]

        self._send_notification(remainingDays, nextEventDate)

        return {
            'nextEventDate': nextEventDate,
            'iconFileName': f'{iconName}.png',
            'remainingDays': remainingDays
        }

    def _get_current_date_time(self) -> datetime:
        return datetime.now()

    def __find_next_date(self, events: List[CalendarEvent]) -> CalendarEvent or None:
        now = self._get_current_date_time().date()
        for event in events:
            if event.start < now:
                continue
            return event
        return None

    def _send_notification(self, remainingDays: int, nextEventDate: str):
        notificationSettings = self._settings['notification']
        if not notificationSettings['enableNotificationViaPushbullet'] and not notificationSettings['enableNotificationViaNtfy']:
            self._lastNotificationDate = None
            return

        if remainingDays != notificationSettings['daysBeforeEvent']:
            self._lastNotificationDate = None
            return

        now = self._get_current_date_time()
        if now.hour < notificationSettings['hour']:
            self._lastNotificationDate = None
            return

        if self._is_already_notified(now):
            return

        self._lastNotificationDate = now.date()
        title = 'DashboardLeaf - Garbage Schedule Notification'
        description = f'"{self._settings["garbageType"]}" will be collected in {remainingDays} days ({nextEventDate})'

        if notificationSettings['enableNotificationViaPushbullet']:
            Helpers.send_notification_via_pushbullet(notificationSettings['pushbulletToken'], title, description)

        if notificationSettings['enableNotificationViaNtfy']:
            NtfyHelper.send_message(userName=notificationSettings['ntfySettings']['username'],
                                    password=notificationSettings['ntfySettings']['password'],
                                    baseUrl=notificationSettings['ntfySettings']['baseUrl'],
                                    topicName=notificationSettings['ntfySettings']['topicName'],
                                    message=f'{title}\n\n{description}',
                                    tags=['wastebasket'])

    def _is_already_notified(self, now: datetime) -> bool:
        if self._lastNotificationDate is None:
            return False

        return self._lastNotificationDate == now.date()

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__, data=data)

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
