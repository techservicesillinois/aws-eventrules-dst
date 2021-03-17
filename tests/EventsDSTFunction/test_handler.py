from freezegun import freeze_time
from moto import mock_events
import pytz

from events_dst import handler
from .utils import events_rules

class TestHandleTransition:
    @mock_events
    def test_cdt2cst(self):
        with events_rules(suffixes=['-CST', '-CDT']) as evt:
            handler._handle_transition(enable='CST', disable='CDT', _evt_clnt=evt)

            paginator = evt.get_paginator('list_rules')
            rules = {r['Name']: r for r in paginator.paginate().search('Rules[]')}

            assert rules['pattern-foo']['State'] == 'ENABLED'
            assert rules['pattern-bar']['State'] == 'DISABLED'
            assert rules['schedule-foo']['State'] == 'ENABLED'
            assert rules['schedule-bar']['State'] == 'DISABLED'

            assert rules['pattern-foo-CST']['State'] == 'ENABLED'
            assert rules['pattern-bar-CST']['State'] == 'DISABLED'
            assert rules['schedule-foo-CST']['State'] == 'ENABLED'
            assert rules['schedule-bar-CST']['State'] == 'ENABLED'

            assert rules['pattern-foo-CDT']['State'] == 'ENABLED'
            assert rules['pattern-bar-CDT']['State'] == 'DISABLED'
            assert rules['schedule-foo-CDT']['State'] == 'DISABLED'
            assert rules['schedule-bar-CDT']['State'] == 'DISABLED'

    @mock_events
    def test_cst2cdt(self):
        with events_rules(suffixes=['-CST', '-CDT']) as evt:
            handler._handle_transition(enable='CDT', disable='CST', _evt_clnt=evt)

            paginator = evt.get_paginator('list_rules')
            rules = {r['Name']: r for r in paginator.paginate().search('Rules[]')}

            assert rules['pattern-foo']['State'] == 'ENABLED'
            assert rules['pattern-bar']['State'] == 'DISABLED'
            assert rules['schedule-foo']['State'] == 'ENABLED'
            assert rules['schedule-bar']['State'] == 'DISABLED'

            assert rules['pattern-foo-CST']['State'] == 'ENABLED'
            assert rules['pattern-bar-CST']['State'] == 'DISABLED'
            assert rules['schedule-foo-CST']['State'] == 'DISABLED'
            assert rules['schedule-bar-CST']['State'] == 'DISABLED'

            assert rules['pattern-foo-CDT']['State'] == 'ENABLED'
            assert rules['pattern-bar-CDT']['State'] == 'DISABLED'
            assert rules['schedule-foo-CDT']['State'] == 'ENABLED'
            assert rules['schedule-bar-CDT']['State'] == 'ENABLED'

    @mock_events
    def test_new_patternRules(self):
        # Should not change the state of any pattern rule
        with events_rules(suffixes=['-CST', '-CDT']) as evt:
            for name in ['pattern-foo', 'pattern-foo-CST', 'pattern-foo-CDT']:
                handler._handle_create(
                    dict(name=name, eventPattern='{ "foo": [ 1 ] }'),
                    _evt_clnt=evt,
                )

                rule = evt.describe_rule(Name=name)
                assert rule['State'] == 'ENABLED'

            for name in ['pattern-bar', 'pattern-bar-CST', 'pattern-bar-CDT']:
                handler._handle_create(
                    dict(name=name, eventPattern='{ "bar": [ 1, 2 ] }', state='DISABLED'),
                    _evt_clnt=evt,
                )

                rule = evt.describe_rule(Name=name)
                assert rule['State'] == 'DISABLED'

    @mock_events
    @freeze_time('2021-01-01 18:00:00')
    def test_new_cstRules(self):
        with events_rules(suffixes=['-CST', '-CDT']) as evt:
            # === Rules that shouldn't change
            handler._handle_create(
                dict(name='schedule-foo', scheduleExpression='cron(0 1 * * ? *)'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-foo')
            assert rule['State'] == 'ENABLED'

            handler._handle_create(
                dict(name='schedule-bar', scheduleExpression='cron(0 2 * * ? *)', state='DISABLED'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-bar')
            assert rule['State'] == 'DISABLED'

            # === Rules that should be enabled
            handler._handle_create(
                dict(name='schedule-foo-CST', scheduleExpression='cron(0 1 * * ? *)'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-foo-CST')
            assert rule['State'] == 'ENABLED'

            handler._handle_create(
                dict(name='schedule-bar-CST', scheduleExpression='cron(0 2 * * ? *)', state='DISABLED'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-bar-CST')
            assert rule['State'] == 'ENABLED'

            # === Rules that should be disabled
            handler._handle_create(
                dict(name='schedule-foo-CDT', scheduleExpression='cron(0 1 * * ? *)'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-foo-CDT')
            assert rule['State'] == 'DISABLED'

            handler._handle_create(
                dict(name='schedule-bar-CDT', scheduleExpression='cron(0 2 * * ? *)', state='DISABLED'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-bar-CDT')
            assert rule['State'] == 'DISABLED'

    @mock_events
    @freeze_time('2021-04-01 18:00:00')
    def test_new_cdtRules(self):
        with events_rules(suffixes=['-CST', '-CDT']) as evt:
            # === Rules that shouldn't change
            handler._handle_create(
                dict(name='schedule-foo', scheduleExpression='cron(0 1 * * ? *)'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-foo')
            assert rule['State'] == 'ENABLED'

            handler._handle_create(
                dict(name='schedule-bar', scheduleExpression='cron(0 2 * * ? *)', state='DISABLED'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-bar')
            assert rule['State'] == 'DISABLED'

            # === Rules that should be disabled
            handler._handle_create(
                dict(name='schedule-foo-CST', scheduleExpression='cron(0 1 * * ? *)'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-foo-CST')
            assert rule['State'] == 'DISABLED'

            handler._handle_create(
                dict(name='schedule-bar-CST', scheduleExpression='cron(0 2 * * ? *)', state='DISABLED'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-bar-CST')
            assert rule['State'] == 'DISABLED'

            # === Rules that should be enabled
            handler._handle_create(
                dict(name='schedule-foo-CDT', scheduleExpression='cron(0 1 * * ? *)'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-foo-CDT')
            assert rule['State'] == 'ENABLED'

            handler._handle_create(
                dict(name='schedule-bar-CDT', scheduleExpression='cron(0 2 * * ? *)', state='DISABLED'),
                _evt_clnt=evt,
            )
            rule = evt.describe_rule(Name='schedule-bar-CDT')
            assert rule['State'] == 'ENABLED'
