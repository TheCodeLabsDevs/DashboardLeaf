import datetime
from typing import Dict
from unittest import mock
from unittest.mock import MagicMock

from dashboard_leaf.logic import Helpers
from dashboard_leaf.logic.tile.tiles.SensorLineChartTile import SensorLineChartTile, SensorType


def example_settings(showAxes: bool):
    return {
        "title": "My Room",
        "url": "http://127.0.0.1:10003",
        "sensorID": 1,
        "sensorIDsForMinMax": [2, 3, 4],
        "numberOfHoursToShow": 4,
        "decimals": 1,
        "lineColor": "rgba(254, 151, 0, 1)",
        "fillColor": "rgba(254, 151, 0, 0.2)",
        "showAxes": showAxes,
        "outdatedValueWarningLimitInSeconds": 300  # use -1 to disable warning
    }


def storage_leaf_service_mock(minValue, maxValue):
    storageLeafServiceMock = MagicMock()
    storageLeafServiceMock.get_data = MagicMock(return_value={
        'min': minValue,
        'max': maxValue
    })
    return storageLeafServiceMock


class TestGetMinMax:
    START_DATE = datetime.date(year=2021, month=2, day=8)
    END_DATE = datetime.date(year=2021, month=2, day=9)

    def test_humidity_returns_0_and_100(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)
        yValues = ['12.5', '10.5']

        result = tile._get_min_and_max('myPage',
                                       SensorType.HUMIDITY,
                                       self.START_DATE, self.END_DATE,
                                       storage_leaf_service_mock(15.0, 20.0),
                                       yValues)
        assert result == (0, 100)

    def test_temperature_no_values_returns_min_and_max_of_api(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        result = tile._get_min_and_max('myPage',
                                       SensorType.TEMPERATURE,
                                       self.START_DATE, self.END_DATE,
                                       storage_leaf_service_mock(15.0, 20.0),
                                       [])
        assert result == (-SensorLineChartTile.MAX_Y_AXIS_SPACING, 20 + SensorLineChartTile.MAX_Y_AXIS_SPACING)

    def test_temperature_min_max_data_is_none_returns_zero(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        result = tile._get_min_and_max('myPage',
                                       SensorType.TEMPERATURE,
                                       self.START_DATE, self.END_DATE,
                                       storage_leaf_service_mock(None, None),
                                       [])
        assert result == (-SensorLineChartTile.MAX_Y_AXIS_SPACING, SensorLineChartTile.MAX_Y_AXIS_SPACING)

    def test_temperature_min_is_above_zero_returns_zero_min(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        result = tile._get_min_and_max('myPage',
                                       SensorType.TEMPERATURE,
                                       self.START_DATE, self.END_DATE,
                                       storage_leaf_service_mock(5, 6),
                                       [])
        assert result == (-SensorLineChartTile.MAX_Y_AXIS_SPACING, 6 + SensorLineChartTile.MAX_Y_AXIS_SPACING)

    def test_temperature_min_is_below_zero_returns_min(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        result = tile._get_min_and_max('myPage',
                                       SensorType.TEMPERATURE,
                                       self.START_DATE, self.END_DATE,
                                       storage_leaf_service_mock(-3, 6),
                                       [])
        assert result == (-3 - SensorLineChartTile.MAX_Y_AXIS_SPACING, 6 + SensorLineChartTile.MAX_Y_AXIS_SPACING)

    def test_temperature_show_axes_no_values(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(True), 10)

        result = tile._get_min_and_max('myPage',
                                       SensorType.TEMPERATURE,
                                       self.START_DATE, self.END_DATE,
                                       storage_leaf_service_mock(None, None),
                                       [])
        assert result == (-SensorLineChartTile.MAX_Y_AXIS_SPACING, SensorLineChartTile.MAX_Y_AXIS_SPACING)

    def test_temperature_show_axes_values_above_zero_return_zero_min(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(True), 10)

        result = tile._get_min_and_max('myPage',
                                       SensorType.TEMPERATURE,
                                       self.START_DATE, self.END_DATE,
                                       storage_leaf_service_mock(None, None),
                                       [6.0, 12])
        assert result == (-SensorLineChartTile.MAX_Y_AXIS_SPACING, 12 + SensorLineChartTile.MAX_Y_AXIS_SPACING)

    def test_temperature_show_axes_values_below_zero_return_min(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(True), 10)

        result = tile._get_min_and_max('myPage',
                                       SensorType.TEMPERATURE,
                                       self.START_DATE, self.END_DATE,
                                       storage_leaf_service_mock(None, None),
                                       [-6.0, 12])
        assert result == (-6 - SensorLineChartTile.MAX_Y_AXIS_SPACING, 12 + SensorLineChartTile.MAX_Y_AXIS_SPACING)


class TestPrepareMeasurementData:
    def test_no_measurements(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)
        measurements = []

        assert tile._prepare_measurement_data(measurements) == ([], [])

    def test_should_return_rounded_values(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)
        measurements = [
            {'id': 409281, 'value': '-5.37', 'timestamp': '2021-02-09 17:47:55', 'sensor_id': 5}
        ]

        assert tile._prepare_measurement_data(measurements) == (['2021-02-09 17:47:55'], ['-5.4'])

    def test_multiple_measurements_should_return_timestamps_from_latest_to_oldest(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        timestamp1 = '2021-02-09 17:47:55'
        timestamp2 = '2021-02-09 17:48:55'
        measurements = [
            {'id': 409281, 'value': '-5.37', 'timestamp': timestamp1, 'sensor_id': 5},
            {'id': 409282, 'value': '-6.2', 'timestamp': timestamp2, 'sensor_id': 5}
        ]

        assert tile._prepare_measurement_data(measurements) == ([timestamp2, timestamp1], ['-6.2', '-5.4'])


class TestPrepareGhostTrace:
    def test_all_values_below_zero_returns_empty_lists(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)
        x = ['2021-02-09 17:47:55']
        y = [-12]
        assert tile._prepare_ghost_trace(-10, x, y) == ([], [])

    def test_all_values_above_zero_and_min_from_api_above_zero_returns_empty_lists(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)
        x = ['2021-02-09 17:47:55', '2021-02-09 17:48:55']
        y = [6, 8]
        assert tile._prepare_ghost_trace(10, x, y) == ([], [])

    def test_all_values_above_zero_and_min_from_api_below_zero_returns_ghost_trace(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)
        x = ['2021-02-09 17:47:55', '2021-02-09 17:48:55']
        y = [6, 8]
        assert tile._prepare_ghost_trace(-10, x, y) == (x, [-10, -10])

    def test_no_values_returns_empty_lists(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)
        x = []
        y = []
        assert tile._prepare_ghost_trace(-10, x, y) == ([], [])


class TestGetTimeSinceLastValue:
    def __get_warning_settings(self, enable: bool):
        return {
            'enable': enable,
            'limitInSeconds': 10,
            'enableNotificationViaPushbullet': False,
            'pushbulletToken': None,
            'enableNotificationViaNtfy': False,
            'ntfySettings': {
                'username': '',
                'password': '',
                'baseUrl': '',
                'topicName': ''
            }
        }

    def test_warnings_disabled_returns_empty_string(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        warningSettings = self.__get_warning_settings(False)
        data = {'latestTime': datetime.datetime(year=2021, month=1, day=1, hour=12, minute=0, second=0)}

        assert tile._get_time_since_last_value(warningSettings, data) == ''

    def test_warnings_enabled_no_outdated_value_returns_empty_string(self):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        warningSettings = self.__get_warning_settings(True)
        data = {'latestTime': datetime.datetime.now()}

        assert tile._get_time_since_last_value(warningSettings, data) == ''

    @mock.patch('dashboard_leaf.logic.tile.tiles.SensorLineChartTile.datetime')
    def test_warnings_enabled_outdated_value_returns_human_readable_string(self, datetimeMock):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        datetimeMock.now.return_value = datetime.datetime(year=2021, month=1, day=1, hour=12, minute=0, second=0)

        warningSettings = self.__get_warning_settings(True)
        data = {'latestTime': datetime.datetime(year=2021, month=1, day=1, hour=11, minute=00, second=00)}

        assert tile._get_time_since_last_value(warningSettings, data) == '1 hour ago'


class TestSendNotification:
    def __get_warning_settings(self, enable: bool, enableNotification: bool) -> Dict:
        return {
            'enable': enable,
            'limitInSeconds': 10,
            'enableNotificationViaPushbullet': enableNotification,
            'pushbulletToken': 'myToken',
            'enableNotificationViaNtfy': False,
            'ntfySettings': {
                'username': '',
                'password': '',
                'baseUrl': '',
                'topicName': ''
            }
        }

    def __get_sensor_info(self) -> Dict[str, str]:
        return {
            'name': 'mySensor',
            'type': 'temperature'
        }

    def __get_device_info(self) -> Dict[str, str]:
        return {
            'name': 'myDevice'
        }

    @mock.patch('dashboard_leaf.logic.tile.tiles.SensorLineChartTile.Helpers')
    def test_notification_disabled_should_do_nothing(self, helpersMock):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        warningSettings = self.__get_warning_settings(True, False)

        tile._send_notification(warningSettings, {}, {}, '1 hour ago')
        helpersMock.send_notification_via_pushbullet.assert_not_called()

    @mock.patch('dashboard_leaf.logic.tile.tiles.SensorLineChartTile.Helpers')
    def test_notification_enabled_no_outdated_value_should_do_nothing(self, helpersMock):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        warningSettings = self.__get_warning_settings(True, True)

        tile._send_notification(warningSettings, {}, {}, '')
        helpersMock.send_notification_via_pushbullet.assert_not_called()

    @mock.patch('dashboard_leaf.logic.Helpers.requests')
    def test_send_notification_should_call_pushbullet_api(self, requestsMock):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        warningSettings = self.__get_warning_settings(True, True)

        requestsMock.post.return_value.status_code = 200

        tile._send_notification(warningSettings, self.__get_sensor_info(), self.__get_device_info(), '1 hour ago')
        requestsMock.post.assert_called_once_with(Helpers.PUSHBULLET_PUSH_URL, data=mock.ANY, headers=mock.ANY)

    @mock.patch('dashboard_leaf.logic.Helpers.requests')
    def test_already_sent_should_skip_sending(self, requestsMock):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        warningSettings = self.__get_warning_settings(True, True)

        requestsMock.post.return_value.status_code = 200

        tile._send_notification(warningSettings, self.__get_sensor_info(), self.__get_device_info(), '1 hour ago')
        tile._send_notification(warningSettings, self.__get_sensor_info(), self.__get_device_info(), '1 hour ago')
        requestsMock.post.assert_called_once()

    @mock.patch('dashboard_leaf.logic.Helpers.requests')
    def test_already_sent_new_value_arrives_and_gets_outdated_should_call_pushbullet_api(self, requestsMock):
        tile = SensorLineChartTile('mySensorTile', example_settings(False), 10)

        warningSettings = self.__get_warning_settings(True, True)
        requestsMock.post.return_value.status_code = 200

        tile._send_notification(warningSettings, self.__get_sensor_info(), self.__get_device_info(), '1 hour ago')

        # a new valid value arrives
        tile._send_notification(warningSettings, self.__get_sensor_info(), self.__get_device_info(), '')

        # value is outdated again
        tile._send_notification(warningSettings, self.__get_sensor_info(), self.__get_device_info(), '1 hour ago')

        assert requestsMock.post.call_count == 2
