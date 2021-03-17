""" Lambda handler entrypoints. """
from datetime import datetime
import logging

import boto3

from .utils import events_scheduled_rules

logger = logging.getLogger(__name__)

evt_clnt = boto3.client('events')


def _handle_transition(enable, disable, _evt_clnt=evt_clnt):
    """
    Handle when the time transitions from DST -> STD or from STD -> DST. This
    lists the rules and disables ones that match the old timezone abbrev and
    enables one that match the new timezone abbrev.

    Args:
        enable (str): timezone abbrev to enable.
        disable (str): timezone abbrev to disable.
    """
    logger.info('Handling transition from %(enable)s to %(disable)s', {
        'enable': enable,
        'disable': disable,
    })
    enable_suffix = '-' + enable.lower()
    disable_suffix = '-' + disable.lower()

    for rule in events_scheduled_rules(_evt_clnt=_evt_clnt):
        logger.debug('Rule %(name)s: %(state)s', {
            'name': rule['Name'],
            'state': rule['State'],
        })
        rule_name    = rule['Name']
        rule_enabled = rule['State'] == 'ENABLED'

        try:
            if rule_name.lower().endswith(disable_suffix) and rule_enabled:
                logger.info('Disabling rule %(name)s', { 'name': rule_name })
                _evt_clnt.disable_rule(
                    Name=rule_name,
                    EventBusName=rule['EventBusName'],
                )
            elif rule_name.lower().endswith(enable_suffix) and not rule_enabled:
                logger.info('Enabling rule %(name)s', { 'name': rule_name })
                _evt_clnt.enable_rule(
                    Name=rule_name,
                    EventBusName=rule['EventBusName'],
                )
        except Exception: # pylint: disable=broad-except
            logger.exception('Exception transitioning rule %(name)s', { 'name': rule_name })
