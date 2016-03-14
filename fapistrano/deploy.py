# -*- coding: utf-8 -*-

from datetime import datetime

from fabric.api import runs_once
from fabric.api import run
from fabric.api import env
from fabric.api import cd
from fabric.api import task
from fabric.api import abort

from .utils import green_alert, with_configs
from .directory import (
    get_outdated_releases, get_releases_path,
    get_current_release, get_previous_release,
)
from . import signal

RELEASE_PATH_FORMAT = '%y%m%d-%H%M%S'

# do not print output by default
env.show_output = False


def first_setup_repo(f):
    # deprecated
    return f

setup_repo = signal.listen('git.building')



@task
@runs_once
@with_configs
def head():
    # deprecated
    signal.emit('deploy.head.publishing')
    signal.emit('deploy.head.published')


@task
@runs_once
@with_configs
def delta():
    # deprecated
    signal.emit('deploy.delta.publishing')
    signal.emit('deploy.delta.published')


@task
@with_configs
def restart():
    signal.emit('deploy.restarting')
    signal.emit('deploy.restarted')
    # FIXME: get the status of the service


@task
@with_configs
def cleanup_failed():
    green_alert('Cleanning up failed build')
    with cd(env.releases_path):
        run('rm -rf _build')


@task
@with_configs
def cleanup_rollback():
    green_alert('Cleaning up %(releases_path)s/%(rollback_from)s' % env)
    run('rm -rf %(releases_path)s/%(rollback_from)s' % env)


@task
@with_configs
def cleanup():
    green_alert('Cleanning up old release(s)')
    with cd(get_releases_path()):
        run('rm -rf %s' % ' '.join(get_outdated_releases()))


@task
@with_configs
def release(branch=None):
    env.branch = branch if branch else env.branch
    env.new_release = datetime.now().strftime(RELEASE_PATH_FORMAT)
    green_alert('Starting')
    signal.emit('deploy.starting')
    _start_deploy()

    green_alert('Started')
    signal.emit('deploy.started')

    green_alert('Updating')
    signal.emit('deploy.updating')

    green_alert('Updated')
    signal.emit('deploy.updated')

    green_alert('Publishing')
    signal.emit('deploy.publishing')
    _symlink_new_release()

    green_alert('Published')
    signal.emit('deploy.published')

    green_alert('Finishing')
    signal.emit('deploy.finishing')
    cleanup()

    green_alert('Finished')
    signal.emit('deploy.finished')
    # TODO: do rollback when restart failed


@task
@with_configs
def resetup_repo():
    with cd('%(current_path)s' % env):
        signal.emit('git.building')
        signal.emit('git.built')

@task
@with_configs
def rollback():
    signal.emit('deploy.starting')
    green_alert('Rolling back to last release')
    env.rollback_from = get_current_release()
    env.rollback_to = get_previous_release()
    _check_rollback_to()
    signal.emit('deploy.started')

    signal.emit('deploy.reverting')
    signal.emit('deploy.reverted')

    signal.emit('deploy.publishing')
    _symlink_rollback()
    signal.emit('deploy.published')

    signal.emit('deploy.finishing_rollback')
    cleanup_rollback()
    signal.emit('deploy.finished')


@task
def debug_output():
    env.show_output = True


@task
@with_configs
@runs_once
def debug_env():
    from pprint import pprint
    pprint(env)


def _start_deploy():
    _check()

def _check():
    run('mkdir -p %(path)s/{releases,shared/log}' % env)
    run('chmod -R g+w %(shared_path)s' % env)
    run('mkdir -p %(releases_path)s/%(new_release)s' % env)

def _symlink_current(dest):
    with cd(env.path):
        run('ln -nfs %s current' % dest)

def _symlink_new_release():
    _symlink_current('%(releases_path)s/%(new_release)s' % env)

def _symlink_rollback():
    _symlink_current('%(releases_path)s/%(rollback_to)s' % env)

def _check_rollback_to():
    if not env.rollback_to:
        abort('No release to rollback')
