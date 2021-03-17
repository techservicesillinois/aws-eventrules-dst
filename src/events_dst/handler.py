""" Lambda handler entrypoints. """
from datetime import datetime
import logging
import os

import boto3

from .utils import events_scheduled_rules, local_now

RULE_SUFFIXES = ['-' + s.lower() for s in os.environ.get('TZ_ABBREVS', '').split(',') if s]

logger = logging.getLogger(__name__)

evt_clnt = boto3.client('events')

def _handle_create(rule, _evt_clnt=evt_clnt):
    """
    Handle when a new rule is created and set its initial state based on if we
    are in DST or STD time right now. This will only handle the rule if it
    ends with something in RULE_SUFFIXES.

    Args:
        rule (dict): Information on the rule being created. Expected to be the
            event requestParameters from CloudTrail.
    """
    rule_name = rule['name']
    rule_enabled = rule.get('state', 'ENABLED') == 'ENABLED'
    if not rule.get('scheduleExpression'):
        logger.debug('Ignoring new rule %(name)s without a schedule expression', {
            'name': rule_name,
        })
        return

    rule_params = dict(Name=rule_name)
    if rule.get('eventBusName'):
        rule_params['EventBusName'] = rule['eventBusName']

    now_suffix = '-' + local_now().strftime('%Z').lower()
    try:
        if rule_name.lower().endswith(now_suffix):
            if not rule_enabled:
                 logger.info('Enabling rule %(name)s', { 'name': rule_name })
                 _evt_clnt.enable_rule(**rule_params)
        elif any(map(lambda s: rule_name.lower().endswith(s), RULE_SUFFIXES)):
            if rule_enabled:
                 logger.info('Disabling rule %(name)s', { 'name': rule_name })
                 _evt_clnt.disable_rule(**rule_params)
        else:
            logger.debug('Ignoring new rule %(name)s that does not match a suffix', {
                'name': rule_name,
            })
    except Exception: # pylint: disable=broad-except
        logger.exception('Exception handling rule %(name)s', { 'name': rule_name })

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
