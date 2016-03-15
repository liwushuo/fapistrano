# -*- coding: utf-8 -*-

from fabric.api import (
    runs_once, run, env, cd,
    task, abort,
)
from fabric.contrib.files import exists

from .utils import green_alert
from .configuration import with_configs
from .directory import (
    get_current_release, get_previous_release,
    get_linked_files, get_linked_file_dirs,
    get_linked_dirs, get_linked_dir_parents,
    get_outdated_releases,
)
from . import signal



@task
@with_configs
def restart():
    signal.emit('deploy.restarting')
    signal.emit('deploy.restarted')


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
    _symlink_current()

    green_alert('Published')
    signal.emit('deploy.published')

    green_alert('Finishing')
    signal.emit('deploy.finishing')
    _cleanup()

    green_alert('Finished')
    signal.emit('deploy.finished')


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
    env.release_path = '%(releases_path)s/%(rollback_to)s' % env
    _check_rollback_to()

    green_alert('Started')
    signal.emit('deploy.started')

    green_alert('Reverting')
    signal.emit('deploy.reverting')

    green_alert('Reverted')
    signal.emit('deploy.reverted')

    green_alert('Publishing')
    signal.emit('deploy.publishing')
    _symlink_current()

    green_alert('Published')
    signal.emit('deploy.published')

    green_alert('Finishing rollback')
    signal.emit('deploy.finishing_rollback')
    _cleanup_rollback()

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
    run('mkdir -p %(release_path)s' % env)
    for linked_file_dir in get_linked_file_dirs():
        dir = '%(release_path)s/' % env
        dir += linked_file_dir
        run('mkdir -p %s' % dir)
    for linked_dir_parent in get_linked_dir_parents():
        dir = '%(release_path)s/' % env
        dir += linked_dir_parent
        run('mkdir -p %s' % dir)

def _symlink_shared_files():
    for linked_file in get_linked_files():
        env.linked_file = linked_file
        if exists('%(release_path)s/%(linked_file)s' % env):
            run('rm %(release_path)s/%(linked_file)s' % env)
        run('ln -nfs %(shared_path)s/%(linked_file)s %(release_path)s/%(linked_file)s' % env)
    for linked_dir in get_linked_dirs():
        env.linked_dir = linked_dir
        if exists('%(release_path)s/%(linked_dir)s' % env):
            run('rm -rf %(release_path)s/%(linked_dir)s' % env)
        run('ln -nfs  %(shared_path)s/%(linked_dir)s %(release_path)s/%(linked_dir)s' % env)


def _symlink_current():
    run('ln -nfs %(release_path)s %(current_path)s' % env)

def _check_rollback_to():
    if not env.release_path:
        abort('No release to rollback')

def _cleanup_rollback():
    run('rm -rf %(releases_path)s/%(rollback_from)s' % env)

def _cleanup():
    with cd(env.releases_path):
        outdated_releases = get_outdated_releases()
        if outdated_releases:
            run('rm -rf %s' % ' '.join(outdated_releases))
