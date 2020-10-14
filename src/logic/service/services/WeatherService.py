from typing import Dict

import requests
from TheCodeLabs_BaseUtils.MultiCacheKeyService import MultiCacheKeyService


class WeatherService(MultiCacheKeyService):
    URL = 'https://api.openweathermap.org/data/2.5/onecall'

    """
    Fetches weather forecast information from OpenWeatherMap.
    """

    EXAMPLE_SETTINGS = {
        "lat": "51.012825",
        "lon": "13.666365",
        "apiKey": "myApiKey"
    }

    def get_data(self, cacheKey: str, fetchIntervalInSeconds: int, settings: Dict) -> Dict:
        if not cacheKey:
            cacheKey = f'weather_{settings["lat"]}_{settings["lon"]}'
        return super().get_data(cacheKey, fetchIntervalInSeconds, settings)

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

        return response.json()
