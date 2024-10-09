import html
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Tuple, List

from TheCodeLabs_BaseUtils.NtfyHelper import NtfyHelper
from timeago import format
from TheCodeLabs_BaseUtils.MultiCacheKeyService import MultiCacheKeyService
from flask import Blueprint

from dashboard_leaf.logic import Constants, Helpers
from dashboard_leaf.logic.service.ServiceManager import ServiceManager
from dashboard_leaf.logic.tile.Tile import Tile

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
        "outdatedValueWarning": {
            "enable": False,
            "limitInSeconds": 300,
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

    MAX_Y_AXIS_SPACING = 2

    def __init__(self, uniqueName: str, settings: Dict, intervalInSeconds: int):
        super().__init__(uniqueName, settings, intervalInSeconds)
        self._notificationSent = False

    def fetch(self, pageName: str) -> Dict:
        storageLeafService = ServiceManager.get_instance().get_service_by_type_name('StorageLeafService')

        startDateTimeObj = datetime.now() - timedelta(hours=self._settings['numberOfHoursToShow'])
        startDateTime = datetime.strftime(startDateTimeObj,self.DATE_FORMAT)
        endDateTime = datetime.strftime(datetime.now(), self.DATE_FORMAT)

        sensorData = self.__get_sensor_data_from_service(endDateTime, pageName, startDateTime, storageLeafService)

        x, y = self._prepare_measurement_data(sensorData['sensorValue'])
        latestTime = datetime.strptime(x[-1], self.DATE_FORMAT) if x else startDateTimeObj
        latestValue = y[-1] if y else ''

        minValue, maxValue = self._get_min_and_max(pageName,
                                                   sensorData['sensorInfo']['type'],
                                                   startDateTime,
                                                   endDateTime,
                                                   storageLeafService,
                                                   y)

        # Check if all values are above zero and the min value for the sensor group is below zero.
        # Therefore a ghost trace must be generated that fills the area underneath the x-axis.
        ghostTraceX, ghostTraceY = self._prepare_ghost_trace(minValue, x, y)

        return {
            'latest': latestValue,
            'x': x,
            'y': y,
            'sensorInfo': sensorData['sensorInfo'],
            'deviceInfo': sensorData['deviceInfo'],
            'min': minValue,
            'max': maxValue,
            'ghostTraceX': ghostTraceX,
            'ghostTraceY': ghostTraceY,
            'latestTime': latestTime
        }

    def __get_sensor_data_from_service(self, endDateTime, pageName, startDateTime, storageLeafService):
        serviceSettings = {
            'url': self._settings['url'],
            'sensorID': self._settings['sensorID'],
            'fetchType': 'all',
            'startDateTime': startDateTime,
            'endDateTime': endDateTime
        }
        cacheKey = f'{pageName}_{self._uniqueName}_all'
        sensorData = storageLeafService.get_data(cacheKey, self._intervalInSeconds, serviceSettings)
        return sensorData

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
        return min(0, minValue) - self.MAX_Y_AXIS_SPACING, maxValue + self.MAX_Y_AXIS_SPACING

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

    def _prepare_measurement_data(self, measurements: List[Dict]) -> Tuple[List[str], List[str]]:
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

    def _prepare_ghost_trace(self, minValue, x, y):
        ghostTraceX = []
        ghostTraceY = []

        if not x or not y:
            return ghostTraceX, ghostTraceY

        if all(float(i) >= 0 for i in y):
            if minValue < 0:
                ghostTraceX = [x[0], x[-1]]
                ghostTraceY = [minValue, minValue]

        return ghostTraceX, ghostTraceY

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

        warningSettings = self._settings['outdatedValueWarning']
        timeSinceLastValue = self._get_time_since_last_value(warningSettings, data)
        self._send_notification(warningSettings, data['sensorInfo'], data['deviceInfo'], timeSinceLastValue)

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
                                    timeSinceLastValue=timeSinceLastValue)

    def _get_time_since_last_value(self, warningSettings: Dict, data):
        timeAgo = ''

        if not warningSettings['enable']:
            return timeAgo

        now = datetime.now()

        limitInSeconds = warningSettings['limitInSeconds']

        if limitInSeconds > 0:
            timeDifference = now - data['latestTime']
            if timeDifference.total_seconds() > limitInSeconds:
                timeAgo = format(timeDifference)

        return timeAgo

    def _send_notification(self, warningSettings: Dict, sensorInfo: Dict, deviceInfo: Dict, timeSinceLastValue: str):
        if not warningSettings['enableNotificationViaPushbullet'] and not warningSettings['enableNotificationViaNtfy']:
            return

        if not timeSinceLastValue:
            self._notificationSent = False
            return

        if self._notificationSent:
            return


        sensorName = sensorInfo['name']
        sensorType = sensorInfo['type']
        deviceName = deviceInfo['name']

        title = 'DashboardLeaf - Outdated Value Warning'
        description = f'Last value for sensor "{sensorName}" received {timeSinceLastValue} ' \
                      f'(type: {sensorType}, device: {deviceName})'

        if warningSettings['enableNotificationViaPushbullet']:
            token = warningSettings['pushbulletToken']
            Helpers.send_notification_via_pushbullet(token, title, description)

        if warningSettings['enableNotificationViaNtfy']:
            NtfyHelper.send_message(userName=warningSettings['ntfySettings']['username'],
                                    password=warningSettings['ntfySettings']['password'],
                                    baseUrl=warningSettings['ntfySettings']['baseUrl'],
                                    topicName=warningSettings['ntfySettings']['topicName'],
                                    message=f'{title}\n\n{description}',
                                    tags=['warning'])


        self._notificationSent = True

    def __format_date(self, dateTime: str):
        parsedDateTime = datetime.strptime(dateTime, self.DATE_FORMAT)
        return datetime.strftime(parsedDateTime, self.DATE_FORMAT_CHART)

    def construct_blueprint(self, pageName: str, *args, **kwargs):
        return Blueprint(f'{pageName}_{__class__.__name__}_{self.get_uniqueName()}', __name__)
