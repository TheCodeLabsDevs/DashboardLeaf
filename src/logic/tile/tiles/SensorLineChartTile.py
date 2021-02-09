import html
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Tuple, List

from timeago import format
from TheCodeLabs_BaseUtils.MultiCacheKeyService import MultiCacheKeyService
from flask import Blueprint

from logic import Constants, Helpers
from logic.service.ServiceManager import ServiceManager
from logic.tile.Tile import Tile

LOGGER = logging.getLogger(Constants.APP_NAME)


class SensorType:
    TEMPERATURE = 'temperature'
    HUMIDITY = 'humidity'


class SensorLineChartTile(Tile):
    EXAMPLE_SETTINGS = {
        "title": "My Room",
        "url": "http://127.0.0.1:10003",
        "sensorID": 1,
        "sensorIDsForMinMax": [2, 3, 4],
        "numberOfHoursToShow": 4,
        "decimals": 1,
        "lineColor": "rgba(254, 151, 0, 1)",
        "fillColor": "rgba(254, 151, 0, 0.2)",
        "showAxes": True,
        "outdatedValueWarningLimitInSeconds": 300  # use -1 to disable warning
    }

    UNIT_BY_SENSOR_TYPE = {
        SensorType.TEMPERATURE: '&degC',
        SensorType.HUMIDITY: '%'
    }

    ICON_BY_SENSOR_TYPE = {
        SensorType.TEMPERATURE: 'wi-thermometer',
        SensorType.HUMIDITY: 'wi-humidity'
    }

    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    DATE_FORMAT_CHART = '%H:%M:%S'
    DATETIME_UNIX_TIMESTAMP_START = datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)

    MAX_Y_AXIS_SPACING = 2

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)

    def fetch(self, pageName: str) -> Dict:
        storageLeafService = ServiceManager.get_instance().get_service_by_type_name('StorageLeafService')

        startDateTime = datetime.strftime(datetime.now() - timedelta(hours=self._settings['numberOfHoursToShow']),
                                          self.DATE_FORMAT)
        endDateTime = datetime.strftime(datetime.now(), self.DATE_FORMAT)

        serviceSettings = {
            'url': self._settings['url'],
            'sensorID': self._settings['sensorID'],
            'fetchType': 'all',
            'startDateTime': startDateTime,
            'endDateTime': endDateTime
        }
        cacheKey = f'{pageName}_{self._uniqueName}_all'
        sensorData = storageLeafService.get_data(cacheKey, self._intervalInSeconds, serviceSettings)

        x, y = self.__prepare_measurement_data(sensorData['sensorValue'])
        latestTime = datetime.strptime(x[-1], self.DATE_FORMAT) if x else self.DATETIME_UNIX_TIMESTAMP_START
        latestValue = y[-1] if y else ''

        minValue, maxValue = self._get_min_and_max(pageName,
                                                   sensorData['sensorInfo']['type'],
                                                   startDateTime,
                                                   endDateTime,
                                                   storageLeafService,
                                                   y)

        # Check if all values are above zero and the min value for the sensor group is below zero.
        # Therefore a ghost trace must be generated that fills the area underneath the x-axis.
        ghostTraceX = []
        ghostTraceY = []
        if all(float(i) >= 0 for i in y):
            if minValue < 0:
                ghostTraceX = [x[0], x[-1]]
                ghostTraceY = [minValue, minValue]

        return {
            'latest': latestValue,
            'x': x,
            'y': y,
            'sensorInfo': sensorData['sensorInfo'],
            'min': minValue,
            'max': maxValue,
            'ghostTraceX': ghostTraceX,
            'ghostTraceY': ghostTraceY,
            'latestTime': latestTime
        }

    def _get_min_and_max(self, pageName: str, sensorType: Dict,
                         startDateTime: str, endDateTime: str,
                         storageLeafService: MultiCacheKeyService, y: List) -> Tuple[float, float]:
        if sensorType == SensorType.HUMIDITY:
            return 0, 100

        # prevent fetching min/max from StorageLeaf as this would consume a lot of time due to huge timespans
        if self._settings['showAxes']:
            yValues = [float(item) for item in y]
            minValue = min(yValues, default=0)
            maxValue = max(yValues, default=0)
        else:
            minValue, maxValue = self.__get_min_max_from_service(pageName, startDateTime, endDateTime,
                                                                 storageLeafService)
        return min(0, minValue), maxValue + self.MAX_Y_AXIS_SPACING

    def __get_min_max_from_service(self, pageName: str, startDateTime: str, endDateTime: str,
                                   storageLeafService: MultiCacheKeyService):
        minMaxSettings = {
            'url': self._settings['url'],
            'sensorIDsForMinMax': self._settings['sensorIDsForMinMax'],
            'fetchType': 'minMax',
            'startDateTime': startDateTime,
            'endDateTime': endDateTime
        }

        cacheKey = f'{pageName}_{self._uniqueName}_minMax'
        minMaxData = storageLeafService.get_data(cacheKey, self._intervalInSeconds, minMaxSettings)
        LOGGER.debug(f'Received min/max: {minMaxData} for sensorIDs: {self._settings["sensorIDsForMinMax"]}')
        return minMaxData.get('min', 0) or 0, minMaxData.get('max', 0) or 0

    def __prepare_measurement_data(self, measurements: List[Dict]) -> Tuple[List[str], List[str]]:
        x = []
        y = []

        for measurement in measurements:
            timestamp = measurement['timestamp']
            x.append(timestamp)

            value = float(measurement['value'])
            y.append(Helpers.round_to_decimals(value, self._settings['decimals']))

        x.reverse()
        y.reverse()
        return x, y

    def render(self, data: Dict) -> str:
        sensorType = data['sensorInfo']['type']
        unit = self.UNIT_BY_SENSOR_TYPE.get(sensorType, '')
        unescapedUnit = html.unescape(unit)
        icon = self.ICON_BY_SENSOR_TYPE.get(sensorType, '')

        textLabels = [f'{self.__format_date(xItem)} - {yItem}{unescapedUnit}' for xItem, yItem in zip(data['x'],
                                                                                                      data['y'])]

        title = self._settings['title']
        if self._settings['showAxes']:
            days = int(self._settings['numberOfHoursToShow'] / 24)
            title = f'{title} - {days} days'

        now = datetime.now()
        timeAgo = ''
        outdatedValueWarningLimitInSeconds = self._settings['outdatedValueWarningLimitInSeconds']
        if outdatedValueWarningLimitInSeconds > 0:
            timeDifference = now - data['latestTime']
            if timeDifference.total_seconds() > outdatedValueWarningLimitInSeconds:
                timeAgo = format(timeDifference)

        return Tile.render_template(os.path.dirname(__file__), __class__.__name__,
                                    x=data['x'],
                                    y=data['y'],
                                    textLabels=textLabels,
                                    min=data['min'],
                                    max=data['max'],
                                    latest=data['latest'],
                                    unit=unit,
                                    icon=icon,
                                    title=title,
                                    lineColor=self._settings['lineColor'],
                                    fillColor=self._settings['fillColor'],
                                    chartId=str(uuid.uuid4()),
                                    ghostTraceX=data['ghostTraceX'],
                                    ghostTraceY=data['ghostTraceY'],
                                    showAxes=self._settings['showAxes'],
                                    timeAgo=timeAgo)

    def __format_date(self, dateTime: str):
        parsedDateTime = datetime.strptime(dateTime, self.DATE_FORMAT)
        return datetime.strftime(parsedDateTime, self.DATE_FORMAT_CHART)

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
