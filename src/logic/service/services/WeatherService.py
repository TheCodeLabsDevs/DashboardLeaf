import locale
from typing import Dict

import requests
from TheCodeLabs_BaseUtils.MultiCacheKeyService import MultiCacheKeyService


class WeatherService(MultiCacheKeyService):
    URL = 'https://api.openweathermap.org/data/2.5/onecall'

    def _fetch_data(self, settings: Dict) -> Dict:
        response = requests.get(self.URL, params={
            'lat': settings['lat'],
            'lon': settings['lon'],
            'appid': settings['apiKey'],
            'lang': 'de',
            'units': 'metric'
        })

        if response.status_code != 200:
            raise Exception(f'Invalid status code: {response.status_code}')

        # TODO less invasive modification
        locale.setlocale(locale.LC_ALL, 'de_DE')

        return response.json()
