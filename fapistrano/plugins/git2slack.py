# -*- coding: utf-8 -*-

import os

import yaml

from fabric.api import env
from .. import signal

def init():
    signal.register('git.delta.publishing', _publish_git_delta_to_slack)
    signal.register('git.head.publishing', _publish_git_head_to_slack)
    signal.register('git.reverted', _publish_rollback_head_to_slack)
    signal.register('git.updated', _publish_updated_delta_to_slack)


def _publish_git_delta_to_slack(**kwargs):
    payload = _format_delta_payload(kwargs.get('delta_log'))
    signal.emit('slack.send', payload=payload)

def _publish_git_head_to_slack(**kwargs):
    target = _format_target()
    head = kwargs.get('head')
    head = _format_git_commit(head)
    text = """[%s] Current head: %s""" % (target, head)
    signal.emit('slack.send', text=text)

def _publish_rollback_head_to_slack(**kwargs):
    target = _format_target()
    head = kwargs.get('head')
    head = _format_git_commit(head)
    text = """[%s] Rollback to %s""" % (target, head)
    signal.emit('slack.send', text=text)

def _publish_updated_delta_to_slack(**kwargs):
    delta_log = kwargs.get('delta_log')
    remote_head = kwargs.get('head')
    payload = _format_release_payload(remote_head, delta_log)
    signal.emit('slack.send', payload=payload)

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

def _format_release_payload(remote_head, delta_log):
    notes = '[%s] Deploy to %s. Please check if it works properly.' % (
        _format_target(), _format_git_commit(remote_head)
    )
    return _format_common_gitlog_payload(delta_log, notes)
