import contextlib

import boto3
from freezegun import freeze_time
from moto import mock_events
import pytz

from events_dst import utils


@contextlib.contextmanager
def events_rules(suffixes=[]):
    """
    Create some event rules, some scheduled and some not.

    Args
        suffixes (List[str]): list of suffixes to use for some events.
    Yields:
        obj: events client.
    """
    conn = boto3.client('events', region_name='us-east-1')
    for suffix in ['', *suffixes]:
        conn.put_rule(Name=f'pattern-foo{suffix}', EventPattern='{ "foo": [ 1 ] }')
        conn.put_rule(Name=f'pattern-bar{suffix}', EventPattern='{ "bar": [ 1, 2 ] }')
        conn.put_rule(Name=f'schedule-foo{suffix}', ScheduleExpression="cron(0 1 * * ? *)")
        conn.put_rule(Name=f'schedule-bar{suffix}', ScheduleExpression="cron(0 2 * * ? *)")

    yield conn

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

class TestEventsScheduledRules:
    @mock_events
    def test_list(self):
        with events_rules() as evt:
            rules = [r['Name'] for r in utils.events_scheduled_rules(_evt_clnt=evt)]
            assert rules == ["schedule-foo", "schedule-bar"]

    @mock_events
    def test_list_suffixes(self):
        with events_rules(suffixes=['-CST', '-CDT']) as evt:
            rules = [r['Name'] for r in utils.events_scheduled_rules(_evt_clnt=evt)]
            assert sorted(rules) == sorted(["schedule-foo", "schedule-bar", "schedule-foo-CST", "schedule-bar-CST", "schedule-foo-CDT", "schedule-bar-CDT"])
