# -*- coding: utf-8 -*-

import json
import requests
import atexit

from fabric.api import env
from fabric.api import task

from ..utils import red_alert
from .. import signal

slack_sendbox = []

def init():
    signal.register('slack.send', _send_data_to_sendbox)

@task
def send_message(text, icon_emoji=':trollface:', timeout=10):
    assert env.slack_webhook
    signal.emit('slack.send', text=text, icon_emoji=icon_emoji, timeout=timeout)

def _check_slack_sendbox(data):
    if data in slack_sendbox:
        return False
    slack_sendbox.append(data)
    return True

def _send_data_to_sendbox(**kwargs):
    if 'text' in kwargs:
        payload = {
            'text': kwargs.get('text'),
            'icon_emoji': kwargs.get('icon_emoji', ':trollface:'),
        }
    elif 'payload' in kwargs:
        payload = kwargs['payload']
    else:
        red_alert('Nothing to be sent to slack.')
        return

    if hasattr(env, 'slack_channel'):
        payload['channel'] = env.slack_channel

    data = json.dumps(payload)

    if not _check_slack_sendbox(data):
        return

def _call_slack_webhook(data):
    requests.post(env.slack_webhook, data=data, timeout=10)

@atexit.register
def send():
    for data in slack_sendbox:
        _call_slack_webhook(data)
