import urllib.parse
from typing import Dict

import requests
from TheCodeLabs_BaseUtils.MultiCacheKeyService import MultiCacheKeyService

from logic import Helpers


class StorageLeafService(MultiCacheKeyService):
    """
    Fetches data from a StorageLeaf instance.
    """

    EXAMPLE_SETTINGS = {
        "url": "http://127.0.0.1:10003",
        "sensorID": 1,
        "sensorIDsForMinMax": [2, 3, 4],
        "fetchType": "latest" or "all" or "minMax",
        "startDateTime": "2020-01-30 18:03:15",
        "endDateTime": "2020-01-30 20:03:15"
    }

    def _fetch_data(self, settings: Dict) -> Dict:
        fetchType = settings['fetchType']
        if fetchType == 'minMax':
            joinedIDs = ','.join([str(item) for item in settings["sensorIDsForMinMax"]])
            startDateTime = urllib.parse.quote(settings['startDateTime'])
            endDateTime = urllib.parse.quote(settings['endDateTime'])

            urlMinMax = Helpers.join_url_parts(settings['url'],
                                               f'measurements/minMax?sensorIds={joinedIDs}'
                                               f'&startDateTime={startDateTime}'
                                               f'&endDateTime={endDateTime}')
            minMaxResponse = requests.get(urlMinMax)
            if minMaxResponse.status_code != 200:
                raise Exception(f'Invalid status code: {minMaxResponse.status_code}')
            return minMaxResponse.json()

        urlSensorInfo = Helpers.join_url_parts(settings['url'], 'sensor', str(settings['sensorID']))
        if fetchType == 'all':
            if 'startDateTime' in settings and 'endDateTime' in settings:
                startDateTime = urllib.parse.quote(settings['startDateTime'])
                endDateTime = urllib.parse.quote(settings['endDateTime'])
                urlSensorValue = Helpers.join_url_parts(urlSensorInfo,
                                                        f'measurements'
                                                        f'?startDateTime={startDateTime}&endDateTime={endDateTime}')
            else:
                urlSensorValue = Helpers.join_url_parts(urlSensorInfo, 'measurements')
        else:
            urlSensorValue = Helpers.join_url_parts(urlSensorInfo, 'measurements/latest')

        sensorInfoResponse = requests.get(urlSensorInfo)
        if sensorInfoResponse.status_code != 200:
            raise Exception(f'Invalid status code: {sensorInfoResponse.status_code}')

        sensorValueResponse = requests.get(urlSensorValue)
        if sensorValueResponse.status_code != 200:
            raise Exception(f'Invalid status code: {sensorValueResponse.status_code}')

        return {
            'sensorInfo': sensorInfoResponse.json(),
            'sensorValue': sensorValueResponse.json()
        }
