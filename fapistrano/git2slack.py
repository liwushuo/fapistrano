# -*- coding: utf-8 -*-

import os

import yaml
from blinker import signal
from fabric.api import env
from .slack import send_message

def init():
    signal('git.delta.publishing').connect(_publish_git_delta_to_slack)
    signal('git.head.publishing').connect(_publish_git_head_to_slack)

def _publish_git_delta_to_slack(sender, **kwargs):
    payload = _format_delta_payload(kwargs.get('delta_log'))
    signal('slack.send').send(None, payload=payload)

def _publish_git_head_to_slack(sender, **kwargs):
    target = _format_target()
    head = kwargs.get('head')
    head = _format_git_commit(head)
    text = """[%s] Current head: %s""" % (target, head)
    signal('slack.send').send(None, text=text)

def _format_delta_payload(delta_log):
    notes = '[%s] Please check if the commits are ready to deploy.' % _format_target()
    return _format_common_gitlog_payload(delta_log, notes, '#aaccaa')

def _format_target():
    return '{app_name}-{env}'.format(**env)

def _format_common_gitlog_payload(gitlog, notes, color='#D00000'):
    text = u'```%s```\n%s' % (gitlog if gitlog else 'No commit.', notes)

    richlog = _format_git_richlog(gitlog)
    if not richlog:
        payload = { 'text': text }
    else:
        payload = {
            'attachments': [
                {
                    'fallback': text,
                    'color': color,
                    'fields': [
                        richlog,
                        {
                            'title': 'Notes',
                            'value': notes
                        },
                    ],
                },
            ]
        }

    return payload

def _format_git_richlog(text):
    if not text:
        return

    conf = _get_config()
    git_web = conf.get('git_web')
    if not git_web:
        return
    commits = []

    for line in text.splitlines():
        commit_hash, commit_log = line.split(' ', 1)
        commits.append(u'<{git_web}{commit_hash}|{commit_hash}> {commit_log}'.format(**locals()))
    return {
        'value': u'\n'.join(commits) if commits else 'No commit.'
    }

def _get_config():
    try:
        with open(os.path.expanduser('~/.fapistranorc')) as f:
            configs = yaml.load(f)
            return configs.get(os.getcwd(), {})
    except IOError:
        return {}

def _format_git_commit(commit):
    conf = _get_config()
    git_web = conf.get('git_web')
    if not git_web:
        return commit
    return u'<%s%s|%s>' % (git_web, commit, commit)
