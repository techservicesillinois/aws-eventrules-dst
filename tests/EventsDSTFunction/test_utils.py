from freezegun import freeze_time
import pytz

from events_dst import utils

@freeze_time('2021-01-01 01:02:03')
class TestLocalNow:
    def test_utc(self):
        now = utils.local_now(pytz.utc)
        assert now.isoformat() == "2021-01-01T01:02:03+00:00"

    def test_default(self):
        now = utils.local_now()
        assert now.isoformat() == "2020-12-31T19:02:03-06:00"

    def test_eastern(self):
        now = utils.local_now(pytz.timezone('US/Eastern'))
        assert now.isoformat() == "2020-12-31T20:02:03-05:00"
