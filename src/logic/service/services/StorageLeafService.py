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
        "fetchType": "latest" or "all",
        "fetchLimit": 100
    }

    URL_BY_FETCH_TYPE = {
        'latest': 'measurements/latest',
        'all': 'measurements/'
    }

    def _fetch_data(self, settings: Dict) -> Dict:
        urlSensorInfo = Helpers.join_url_parts(settings['url'], 'sensor', str(settings['sensorID']))

        fetchType = settings['fetchType']
        if fetchType == 'all':
            urlSensorValue = Helpers.join_url_parts(urlSensorInfo, 'measurements', str(settings['fetchLimit']))
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