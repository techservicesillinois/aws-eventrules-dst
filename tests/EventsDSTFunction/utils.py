import contextlib

import boto3

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
        conn.put_rule(Name=f'pattern-foo{suffix}', State='ENABLED', EventPattern='{ "foo": [ 1 ] }')
        conn.put_rule(Name=f'pattern-bar{suffix}', State='DISABLED', EventPattern='{ "bar": [ 1, 2 ] }')
        conn.put_rule(Name=f'schedule-foo{suffix}', State='ENABLED', ScheduleExpression="cron(0 1 * * ? *)")
        conn.put_rule(Name=f'schedule-bar{suffix}', State='DISABLED', ScheduleExpression="cron(0 2 * * ? *)")

    yield conn
