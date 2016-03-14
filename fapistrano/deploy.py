# -*- coding: utf-8 -*-

from datetime import datetime

from fabric.api import runs_once
from fabric.api import run
from fabric.api import env
from fabric.api import cd
from fabric.api import task
from fabric.api import abort
from fabric.contrib.files import exists
from .utils import green_alert, with_configs
from .directory import (
    get_outdated_releases, get_releases_path,
    get_current_release, get_previous_release,
    get_linked_files, get_linked_file_dirs,
    get_linked_dirs, get_linked_dir_parents,
)
from . import signal

# do not print output by default
env.show_output = False


def first_setup_repo(f):
    # deprecated
    return f

setup_repo = signal.listen('deploy.updated')



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
        outdated_releases = get_outdated_releases()
        if outdated_releases:
            run('rm -rf %s' % ' '.join(outdated_releases))


@task
@with_configs
def release():
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
    green_alert('Starting')
    signal.emit('deploy.starting')
    env.rollback_from = get_current_release()
    env.rollback_to = get_previous_release()
    _check_rollback_to()

    green_alert('Started')
    signal.emit('deploy.started')

    green_alert('Reverting')
    signal.emit('deploy.reverting')

    green_alert('Reverted')
    signal.emit('deploy.reverted')

    green_alert('Publishing')
    signal.emit('deploy.publishing')
    _symlink_rollback()

    green_alert('Published')
    signal.emit('deploy.published')

    green_alert('Finishing rollback')
    signal.emit('deploy.finishing_rollback')
    cleanup_rollback()

    green_alert('Finished')
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
    _symlink_shared_files()

def _check():
    run('mkdir -p %(path)s/{releases,shared/log}' % env)
    run('chmod -R g+w %(shared_path)s' % env)
    run('mkdir -p %(releases_path)s/%(new_release)s' % env)
    for linked_file_dir in get_linked_file_dirs():
        dir = '%(releases_path)s/%(new_release)s/' % env
        dir += linked_file_dir
        run('mkdir -p %s' % dir)
    for linked_dir_parent in get_linked_dir_parents():
        dir = '%(releases_path)s/%(new_release)s/' % env
        dir += linked_dir_parent
        run('mkdir -p %s' % dir)

def _symlink_shared_files():
    for linked_file in get_linked_files():
        env.linked_file = linked_file
        if exists('%(releases_path)s/%(new_release)s/%(linked_file)s' % env):
            run('rm %(releases_path)s/%(new_release)s/%(linked_file)s' % env)
        run('ln -nfs %(shared_path)s/%(linked_file)s %(releases_path)s/%(new_release)s/%(linked_file)s' % env)
    for linked_dir in get_linked_dirs():
        env.linked_dir = linked_dir
        if exists('%(releases_path)s/%(new_release)s/%(linked_dir)s' % env):
            run('rm -rf %(releases_path)s/%(new_release)s/%(linked_dir)s' % env)
        run('ln -nfs  %(shared_path)s/%(linked_dir)s %(releases_path)s/%(new_release)s/%(linked_dir)s' % env)

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
