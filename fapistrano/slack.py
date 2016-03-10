# -*- coding: utf-8 -*-

import json
import requests

from blinker import signal
from fabric.api import env
from fabric.api import task

from .utils import red_alert

def init():
    signal('slack.send').connect(_send_text)

@task
def send_message(text, icon_emoji=':trollface:', timeout=10):
    assert env.slack_webhook
    signal('slack.send').send(None, text=text, icon_emoji=icon_emoji, timeout=timeout)

def _send_text(sender, **kwargs):
    signal('slack.sending').send(None, **kwargs)

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
    resp = requests.post(env.slack_webhook, data=data, timeout=kwargs.get('timeout', 10))
    signal('slack.sent').send(None, is_success=resp.status_code == 200)
