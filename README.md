# DashboardLeaf

Flask server for displaying multiple dashboards with custom tiles that refresh periodically.

## Page

Holds multiple tiles and displays them in a grid. On mobile devices in portrait orientation the grid will be displayed as a single column.  

### Page settings
All settings regarding pages and their tiles are located inside the `pageSettings.json` in the project's root directory. An example settings file is available for reference.  
The following snippet shows an example of a tile in the settings files.
```json
 {
        "tileType": "SensorLineChartTile",
        "uniqueName": "SensorLineChart_Temperature_Wohnzimmer",
        "intervalInSeconds": 60,
        "settings": {
            "title": "Wohnzimmer",
            "url": "http://192.168.178.39:10003",
            "sensorID": 1,
            "sensorIDsForMinMax": [
                1,
                3,
                5
            ],
            "numberOfHoursToShow": 4,
            "decimals": 1,
            "lineColor": "rgba(254, 151, 0, 1)",
            "fillColor": "rgba(254, 151, 0, 0.2)"
        },
        "x": 0,
        "y": 0,
        "width": 3,
        "height": 3
    }
```

- `tileType` - References the name of a tile class. This class must exist on start of the server.
- `uniqueName` - This name must be unique across the complete page.
- `intervalInSeconds` - Specifies the automatic refresh rate in seconds.
- `x` - Horizontal position in the grid, starting by 0 (**Note:** Positions should not be assigned more than once!)
- `y` - Vertical position in the grid, starting by 0 (**Note:** Positions should not be assigned more than once!)
- `width` - The tile's width (minimum is 1 maximum is 12 on desktop horizontal screens)
- `height` - The tile's height (minimum is 1 maximum is 12 on desktop horizontal screens)
- `settings` - Optional additional settings for the tile. See the corresponding tile implementation for further details and explanation.

## Tile

A tile is displayed on a page and shows arbitrary information. It is possible to create custom tiles.

## Create a custom tile

### 1. Create a new tile inside `src/tile/tiles` using the following clock tile example:
```python
import os
from datetime import datetime
from typing import Dict

from flask import Blueprint

from logic.tile.Tile import Tile

class MyCustomClockTile(Tile):
    EXAMPLE_SETTINGS = {}

    DATE_FORMAT = '%H:%M:%S'

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, pageName: str) -> Dict:
        return {'time': datetime.strftime(datetime.now(), self.DATE_FORMAT)}

    def render(self, data: Dict) -> str:
        return Tile.render_template(os.path.dirname(__file__), __class__.__name__, time=data['time'])

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
```

- `EXAMPLE_SETTINGS` is used to document a dict like settings structure that this tile offers. Those settings are usable in the `pageSettings.json`. Our clock example doesn't have any settings.
- The constructor just passes the parameters to the parent abstract class and is not required if you are not doing anything else inside.
- On page load the `construct_blueprint` method is called and provides a unique route for the current tile instance on the specific page.
- Once the tile refresh interval is expired, an automatic refresh is triggered by the system. Therefore `fetch` and `render` are called.
- The `fetch` method is meant to retrieve information from an arbitrary source and perform all necessary data operations and modifications. It provides a dictionary with the processed data. 
- This data dictionary is passed to the `render` method which performs all necessary tasks to create the view. A jinja template is rendered at the end of the method.
- The rendered template results in a html fragment which is sent to all connected clients. Each client will then replace the tile content on the page accordingly.


### 2. Create a new jinja template
A jinja template for our clock example can look like this:
```jinja2
<style>
    .clockTile {
        font-size: 7vh;
        font-weight: bold;
    }
    
    .clockTile .myClass {
        color: #FFFFFF;
    }
</style>

<div class="clockTile">
    <span class="myClass">{{ time }}</span>
</div>
```

The `time` variable is passed in the `render` method.  
**Note:** Make sure to use unique css class names to avoid collisions with other tiles. It is best practice addressing all style classes inside the template by the root class too (See the line `.clockTile .myClass {` for an example)

### 3. Use your tile
The tiles inside the `tiles` folder will be automatically scanned and recognized upon server start. There is no need to perform a special registration.  
To use your custom tile simply add it to your `pageSettings.json`.
```json
[
    {
        "uniqueName": "MyPage",
        "tiles": [
            {
                "tileType": "MyCustomClockTile",
                "uniqueName": "ClockForMe",
                "intervalInSeconds": 60,
                "settings": {
                },
                "x": 1,
                "y": 1,
                "width": 3,
                "height": 2
            }
        ]
    }
]
```


## Service
A service is used to provide access to a data source for multiple tiles. Imagine a tile that fetches weather data from a given api to show the current outside temperature and a second tile showing the forecast for the next three days. Creating both tiles independently will result in code duplication especially for the api fetch logic. To avoid this problem a service could be used. A service should be es generic and configurable as possible. In the given example a service that takes an url, credentials and a city name as input and provides a complete forecast data dictionary would be the best choice. Both tiles could then use this service and extract the data the need form the dictionary.  

## Create a custom service

### 1. Create a new service inside `src/service/services` using the following example:
```python
from typing import Dict

import requests
from TheCodeLabs_BaseUtils.MultiCacheKeyService import MultiCacheKeyService

class MyWeatherService(MultiCacheKeyService):
    URL = 'https://api.openweathermap.org/data/2.5/onecall'

    """
    Fetches weather forecast information from OpenWeatherMap.
    """

    EXAMPLE_SETTINGS = {
        "lat": "51.012825",
        "lon": "13.666365",
        "apiKey": "myApiKey"
    }

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
```

- `EXAMPLE_SETTINGS` is used to document a dict like settings structure that this tile offers. Those settings are usable in the `pageSettings.json`. Our clock example doesn't have any settings.
- A service provides a `get_data` method that is used to request the latest data from an external class. This method will return the latest cached data or if the fetch interval is reached call `_fetch_data`, update the cache and return the new data.
- The `_fetch_data` is the only method we must implement. A dictionary holds all settings for this fetch. The method returns a dictionary with the fetched data.

**Note:** Services are only instantiated once therefore you have to make sure to use unique cache keys and implement the services stateless (one call to `get_data` with a set of settings should not interfere with another different call afterwards)!

### 2. Use your service
The services inside the `services` folder will be automatically scanned and recognized upon server start. There is no need to perform a special registration.  
To use your service inside a tile use the following lines:
```python
from logic.service.ServiceManager import ServiceManager

weatherService = ServiceManager.get_instance().get_service_by_type_name('MyWeatherService')
cacheKey = f'{pageName}_{self._uniqueName}'
return weatherService.get_data(cacheKey, self._intervalInSeconds, self._settings)
```

`MyWeatherService` must reference the name of an existing service class inside `src/service/services`.  
