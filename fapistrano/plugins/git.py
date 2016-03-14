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
        _clone_git_repo(env.repo, env.branch)

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
    with cd(env.path):
        if exists('%(releases_path)s/_build' % env):
            run('rm -rf %(releases_path)s/_build' % env)
        run('cp -R %(path)s/repo/ %(releases_path)s/_build' % env)
        with cd('%(releases_path)s/_build' % env):
            try:
                green_alert('Git building')
                signal.emit('git.building')

                green_alert('Git built')
                signal.emit('git.built')
            except SystemExit:
                red_alert('New release failed to build, Cleaning up failed build')
                run('rm -rf %(release_path)s/_build' % env)
                exit()
        with cd('%(releases_path)s' % env):
            run('cp -R _build/*  %(new_release)s' % env)

def _clone_git_repo(repo, branch='master'):
    green_alert('Cloning the latest code')
    run('git clone -q --depth 1 %(repo)s %(path)s/repo' % env)

    with cd('%(path)s/repo' % env):
        green_alert('Checking out %(branch)s branch' % env)
        run('git checkout %s' % branch)

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
