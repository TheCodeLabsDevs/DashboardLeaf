import json
from typing import Dict

from TheCodeLabs_BaseUtils.MultiCacheKeyService import MultiCacheKeyService


class JsonService(MultiCacheKeyService):
    """
    Fetches information from a given json file.
    """

    EXAMPLE_SETTINGS = {
        "path": "path/to/my/file.json"
    }

    def _fetch_data(self, settings: Dict) -> Dict:
        with open(settings['path'], encoding='utf-8') as f:
            data = json.load(f)
        return {'data': data}
