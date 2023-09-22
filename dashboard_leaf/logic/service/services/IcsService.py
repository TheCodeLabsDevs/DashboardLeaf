from dataclasses import dataclass
from datetime import datetime

from icalendar import Calendar
from typing import Dict

from TheCodeLabs_BaseUtils.MultiCacheKeyService import MultiCacheKeyService


@dataclass
class CalendarEvent:
    summary: str = ''
    uid: str = ''
    description: str = ''
    location: str = ''
    start: datetime = ''
    end: datetime = ''


class IcsService(MultiCacheKeyService):
    """
    Fetches information from a given ics calendar file.
    """

    EXAMPLE_SETTINGS = {
        "path": "path/to/my/calendar.ics"
    }

    def _fetch_data(self, settings: Dict) -> Dict:
        events = []

        with open(settings['path'], 'rb') as f:
            calendar = Calendar.from_ical(f.read())
            for component in calendar.walk():
                event = CalendarEvent('event')

                if component.get('SUMMARY') is None:
                    continue

                event.summary = component.get('SUMMARY')
                event.uid = component.get('UID')

                if component.get('DESCRIPTION') is not None:
                    event.description = component.get('DESCRIPTION')

                event.location = component.get('LOCATION')

                if hasattr(component.get('dtstart'), 'dt'):
                    event.start = component.get('dtstart').dt

                if hasattr(component.get('dtend'), 'dt'):
                    event.end = component.get('dtend').dt

                event.url = component.get('URL')
                events.append(event)

        events = sorted(events, key=lambda event: event.start)
        return {'events': events}


if __name__ == '__main__':
    s = IcsService()

    events = s.get_data('0815', 5, {'path': '../../../../abfallkalender_2021_richard-wagner-str.ics'})['events']
    for x in events:
        # if 'Papier' in x.summary:
        print(x.summary, x.start)
