from datetime import datetime
from unittest import mock

from logic import Helpers
from logic.tile.tiles.GarbageContainerScheduleTile import GarbageContainerScheduleTile


def example_settings(enableNotifications):
    return {
        "path": None,
        "garbageType": "Papier" or "Gelbe Säcke" or "Bioabfall" or "Restabfall",
        "notificationViaPushbullet": {
            "enable": enableNotifications,
            "daysBeforeEvent": 1,
            "hour": 10,
            "pushbulletToken": "myToken"
        }
    }


class TestIsAlreadyNotified:
    def test_not_notified_should_return_false(self):
        tile = GarbageContainerScheduleTile('myGarbageScheduleTile', example_settings(False), 10)
        assert tile._is_already_notified(datetime.now()) is False

    def test_already_notified_but_not_today_should_return_false(self):
        tile = GarbageContainerScheduleTile('myGarbageScheduleTile', example_settings(False), 10)

        tile.__lastNotificationDate = datetime(year=2021, month=3, day=18).date()
        currentDateTime = datetime(year=2021, month=3, day=21, hour=11, minute=35, second=0)

        assert tile._is_already_notified(currentDateTime) is False

    def test_already_notified_should_return_true(self):
        tile = GarbageContainerScheduleTile('myGarbageScheduleTile', example_settings(False), 10)

        tile._lastNotificationDate = datetime(year=2021, month=3, day=21).date()
        currentDateTime = datetime(year=2021, month=3, day=21, hour=11, minute=35, second=0)

        assert tile._is_already_notified(currentDateTime) is True


class TestSendNotification:
    @mock.patch('logic.tile.tiles.GarbageContainerScheduleTile.Helpers')
    def test_notification_disabled_should_do_nothing(self, helpersMock):
        tile = GarbageContainerScheduleTile('myGarbageScheduleTile', example_settings(False), 10)

        tile._send_notification(1, '')
        helpersMock.send_notification_via_pushbullet.assert_not_called()

    @mock.patch('logic.tile.tiles.GarbageContainerScheduleTile.Helpers')
    def test_notification_enabled_reaming_days_greater_than_settings_should_do_nothing(self, helpersMock):
        tile = GarbageContainerScheduleTile('myGarbageScheduleTile', example_settings(True), 10)

        tile._send_notification(3, '')
        helpersMock.send_notification_via_pushbullet.assert_not_called()

    @mock.patch('logic.Helpers.requests')
    def test_send_notification_after_settings_hour_should_call_pushbullet_api(self, requestsMock):
        tile = GarbageContainerScheduleTile('myGarbageScheduleTile', example_settings(True), 10)

        requestsMock.post.return_value.status_code = 200
        with mock.patch.object(tile, '_get_current_date_time', wraps=tile._get_current_date_time) as currentDateTimeMock:
            currentDateTimeMock.return_value = datetime(year=2021, month=3, day=21, hour=11, minute=35, second=0)
            tile._send_notification(1, '')

        requestsMock.post.assert_called_once_with(Helpers.PUSHBULLET_PUSH_URL, data=mock.ANY, headers=mock.ANY)

    @mock.patch('logic.tile.tiles.GarbageContainerScheduleTile.Helpers')
    def test_send_notification_before_settings_hour_should_do_nothing(self, helpersMock):
        tile = GarbageContainerScheduleTile('myGarbageScheduleTile', example_settings(True), 10)

        with mock.patch.object(tile, '_get_current_date_time', wraps=tile._get_current_date_time) as currentDateTimeMock:
            currentDateTimeMock.return_value = datetime(year=2021, month=3, day=21, hour=9, minute=35, second=0)
            tile._send_notification(1, '')

        helpersMock.send_notification_via_pushbullet.assert_not_called()

    @mock.patch('logic.Helpers.requests')
    def test_already_notified_should_skip_sending(self, requestsMock):
        tile = GarbageContainerScheduleTile('myGarbageScheduleTile', example_settings(True), 10)

        with mock.patch.object(tile, '_get_current_date_time',
                               wraps=tile._get_current_date_time) as currentDateTimeMock:
            currentDateTimeMock.return_value = datetime(year=2021, month=3, day=21, hour=11, minute=00, second=0)
            requestsMock.post.return_value.status_code = 200
            tile._send_notification(1, '')
            tile._send_notification(1, '')

        requestsMock.post.assert_called_once()

    @mock.patch('logic.Helpers.requests')
    def test_already_notified_should_skip_sending_even_if_already_skipped_before(self, requestsMock):
        tile = GarbageContainerScheduleTile('myGarbageScheduleTile', example_settings(True), 10)

        with mock.patch.object(tile, '_get_current_date_time',
                               wraps=tile._get_current_date_time) as currentDateTimeMock:
            currentDateTimeMock.return_value = datetime(year=2021, month=3, day=21, hour=11, minute=00, second=0)
            requestsMock.post.return_value.status_code = 200
            tile._send_notification(1, '')
            tile._send_notification(1, '')
            tile._send_notification(1, '')

        requestsMock.post.assert_called_once()
