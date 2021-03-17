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
