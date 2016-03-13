# -*- coding: utf-8 -*-

import os
import new
from datetime import datetime
import atexit

from blinker import signal
from fabric.api import runs_once
from fabric.api import local
from fabric.api import run
from fabric.api import env
from fabric.api import cd
from fabric.api import prefix
from fabric.api import task
from fabric.api import abort
from fabric.api import parallel
from fabric.api import show, hide
from fabric.api import with_settings
from fabric.colors import green, red, white

import yaml
import requests
import json

from .utils import red_alert, green_alert, with_configs

RELEASE_PATH_FORMAT = '%y%m%d-%H%M%S'

# do not print output by default
env.show_output = False
first_setup_repo_func = None

def first_setup_repo(f):
    global first_setup_repo_func
    first_setup_repo_func = f
    return f


def setup_repo(f):
    # legacy interface, this should not be used anymore.
    def setup_repo_func(sender, **kwargs):
        f()
    signal('git.building').connect(setup_repo_func)
    return f


@task
@runs_once
@with_configs
def head():
    # deprecated
    signal('deploy.head.publishing').send(None)
    signal('deploy.head.published').send(None)

@task
@runs_once
@with_configs
def delta():
    # deprecated
    signal('deploy.delta.publishing').send(None)
    signal('deploy.delta.published').send(None)


@task
@with_configs
def restart():
    signal('deploy.restarting').send(None)
    signal('deploy.restarted').send(None)
    # FIXME: get the status of the service

@task
def _releases():
    env.releases = sorted(run('ls -x %(releases_path)s' % env).split())
    env.current_release = run('readlink %(current_path)s' % env).rsplit('/', 1)[1]

    current_index = env.releases.index(env.current_release)
    if current_index > 1:
        env.previous_release = env.releases[current_index-1]
    if len(env.releases) != current_index + 1:
        env.dirty_releases = env.releases[current_index+1:]
    env.new_release = datetime.now().strftime(RELEASE_PATH_FORMAT)


@task
@with_configs
def cleanup_failed():
    green_alert('Cleanning up failed build')

    with cd(env.releases_path):
        run('rm -rf _build')


@task
@with_configs
def cleanup():
    green_alert('Cleanning up old release(s)')
    if not env.has_key('releases'):
        _releases()

    if len(env.releases) > env.keep_releases:
        directories = env.releases
        directories.reverse()
        del directories[:env.keep_releases]
        with cd(env.releases_path):
            run('rm -rf %s' % ' '.join(directories))


@task
@with_configs
def setup(branch=None):
    if branch:
        env.branch = branch

    green_alert('Creating project path')
    run('mkdir -p %(path)s/{releases,shared/log}' % env)

    # change permission
    run('find %(path)s -type d -exec chmod 755 {} \;' % env)
    run('find %(path)s -type f -exec chmod 644 {} \;' % env)
    run('chmod -R g+w %(shared_path)s' % env)

    # clone code
    with cd(env.releases_path):
        green_alert('Cloning the latest code')
        env.new_release = datetime.now().strftime(RELEASE_PATH_FORMAT)
        run('git clone -q --depth 1 %(repo)s _build' % env)

    with cd('%(releases_path)s/_build' % env):
        green_alert('Checking out %(branch)s branch' % env)
        run('git checkout %(branch)s' % env)

        if callable(first_setup_repo_func):
            green_alert('Setting up repo')
            first_setup_repo_func()

    # symlink
    with cd(env.releases_path):
        run('mv _build %(new_release)s' % env)
    with cd(env.path):
        run('ln -nfs %(releases_path)s/%(new_release)s current' % env)

        # link supervisorctl and run
        run('ln -nfs %(current_path)s/configs/supervisor_%(env)s_%(role)s.conf '
            '/etc/supervisor/conf.d/%(project_name)s.conf' % env)
        run('supervisorctl reread')
        run('supervisorctl update')
        run('supervisorctl status')


@task
@with_configs
def release(branch=None, refresh_supervisor=False, use_reset=False, bsd=True):
    if branch:
        env.branch = branch

    green_alert('Deploying new release on %(branch)s branch' % env)

    # get releases
    _releases()

    green_alert('Creating the build path')
    with cd(env.releases_path):
        run('cp -rp %(current_release)s _build' % env)

    try:
        # update code and environments
        with cd('%(releases_path)s/_build' % env):
            signal('deploy.updating').send(
                None,
                git_user_reset=use_reset,
                git_bsd=bsd,
            )

            signal('deploy.updated').send(None)

            if callable(setup_repo_func):
                # setup repo
                green_alert('Setting up repo')
                setup_repo_func()

    except SystemExit:
        red_alert('New release failed to build')
        cleanup_failed()
        exit()

    green_alert('Symlinking to current')
    with cd(env.releases_path):
        run('mv _build %(new_release)s' % env)
    with cd(env.path):
        run('ln -nfs %(releases_path)s/%(new_release)s current' % env)
    green_alert('Done. Deployed %(new_release)s on %(branch)s' % env)

    green_alert('Launching')
    restart(refresh_supervisor)

    cleanup()

    # TODO: do rollback when restart failed

@task
@with_configs
def resetup_repo():
    with cd('%(current_path)s' % env):
        green_alert('Setting up repo')
        setup_repo_func()

@task
@with_configs
def rollback():
    green_alert('Rolling back to last release')
    _releases()

    if not env.has_key('previous_release'):
        abort('No release to rollback')

    env.rollback_from = env.current_release
    env.rollback_to = env.previous_release

    with cd(env.path):
        run('ln -nfs %(releases_path)s/%(rollback_to)s current' % env)
        restart()
        run('rm -rf %(releases_path)s/%(rollback_from)s' % env)

    signal('git.reverted').send(None)


@task
def debug_output():
    env.show_output = True

@task
@with_configs
@runs_once
def debug_env():
    from pprint import pprint
    pprint(env)
