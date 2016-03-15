# -*- coding: utf-8 -*-

from fabric.api import cd, env, run, local, task
from fabric.contrib.files import exists
from ..utils import green_alert, red_alert, yellow_alert
from .. import signal

def init():
    if not hasattr(env, 'git_use_reset'):
        env.git_use_reset = False

    if not hasattr(env, 'sed_bsd'):
        env.sed_bsd = True

    if not hasattr(env, 'git_show_delta'):
        env.git_show_delta = False

    if not hasattr(env, 'branch'):
        env.branch = 'master'

    signal.register('deploy.delta.publishing', publish_git_delta)
    signal.register('deploy.head.publishing', publish_git_head)

    signal.register('deploy.reverted', log_reverted_revision)
    signal.register('deploy.updating', update_git_repo)
    signal.register('deploy.updated', publish_git_repo_as_current_release)

def publish_git_delta(**kwargs):
    head = _get_remote_head()
    delta_log = _get_delta(head)
    if not delta_log:
        green_alert('No delta.')
        return
    green_alert('Get delta:\n%s' % delta_log)
    signal.emit('git.delta.publishing', head=head, delta_log=delta_log)

def publish_git_head(**kwargs):
    head = _get_remote_head()
    green_alert('Get head: \n%s' % head)
    signal.emit('git.head.publishing', head=head)

def log_reverted_revision(**kwargs):
    head = _get_remote_head()
    green_alert('Rollback to %s' % head)
    signal.emit('git.reverted', head=head)

def update_git_repo(**kwargs):
    if not exists('%(path)s/repo' % env):

    with cd('%(path)s/repo' % env):
        head = _get_remote_head()
        if head:
            green_alert('Current version: %s' % head)
            delta_log = _get_delta(head, bsd=env.sed_bsd)
        else:
            yellow_alert('No current version detected.')
            delta_log = None

        green_alert('Git Updating')
        signal.emit('git.updating')
        _clone()

        if env.git_use_reset:
            run('git fetch -q')
            run('git reset --hard origin/%(branch)s' % env)
        else:
            run('git pull -q')
            run('git checkout %(branch)s' % env)

        updated_head = _get_remote_head()
        green_alert('Git updated')
        signal.emit('git.updated', delta_log=delta_log, head=updated_head)

        green_alert('Release to %s' % updated_head)

        if delta_log:
            green_alert('Release log:\n%s' % delta_log)

def publish_git_repo_as_current_release(**kwargs):
    _update()


def _get_remote_head():
    if exists('.git'):
        return run("git rev-parse --short HEAD", quiet=True)


def _get_delta(current_version, upstream='origin', bsd=True):
    if not env.git_show_delta:
        return

    local('/usr/bin/env git fetch -q %s' % upstream)
    #FIXME
    return local(
        '/usr/bin/env git log --reverse --pretty="%%h %%s: %%b" --merges %s..%s/master | '
        '/usr/bin/env sed -%s "s/Merge pull request #([0-9]+) from ([^/]+)\\/[^:]+/#\\1\\/\\2/"' % (
            current_version, upstream, 'E' if bsd else 'r'), capture=True).decode('utf8')
def _clone():
    if exists('%(path)s/repo/HEAD'):
        abort('Repo has cloned already!')

    if hasattr(env, 'git_shallow_clone') and env.git_shallow_clone:
        run('git clone --mirror --depth %(git_shallow_clone)s '
            '--no-single-branch %(repo)s %(path)s/repo' % env)
    else:
        run('git clone --mirror %(repo)s %(path)s/repo' % env)


def _update():
    with cd('%(path)s/repo' % env):
        if hasattr(env, 'git_shallow_clone') and env.git_shallow_clone:
            run(
                'git fetch '
                '--depth %(git_shallow_clone)s '
                'origin %(branch)s' % env
            )
        else:
            run('git remote update --prune')
