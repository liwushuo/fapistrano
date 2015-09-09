# -*- coding: utf-8 -*-

import os
import new
from datetime import datetime

from fabric.api import runs_once
from fabric.api import local
from fabric.api import run
from fabric.api import env
from fabric.api import cd
from fabric.api import prefix
from fabric.api import task
from fabric.api import abort
from fabric.api import parallel
from fabric.colors import green
from fabric.colors import red

RELEASE_PATH_FORMAT = '%y%m%d-%H%M%S'


first_setup_repo_func = None
setup_repo_func = None

def first_setup_repo(f):
    global first_setup_repo_func
    first_setup_repo_func = f
    return f


def setup_repo(f):
    global setup_repo_func
    setup_repo_func = f
    return f


@task
@runs_once
def debug_env():
    from pprint import pprint
    pprint(env)


@task
@runs_once
def delta(upstream='upstream', bsd=True):
    with cd(env.current_path):
        version = run("git rev-parse --short HEAD", quiet=True)

    local('git fetch -q %s' % upstream)
    local('git log --pretty="%%h %%s: %%b" --merges %s..%s/master | '
          'sed -%s "s/Merge pull request #([0-9]+) from ([^/]+)\\/[^:]+/#\\1\\/\\2/"' % (
              version, upstream, 'E' if bsd else 'r'))


@task
def _restart(refresh_supervisor=False, wait_before_refreshing=False):
    if not refresh_supervisor:
        run('supervisorctl restart %(project_name)s' % env)
    else:
        run('supervisorctl stop %(project_name)s' % env)
        if wait_before_refreshing:
            raw_input('type any key to refresh supervisor')
        run('supervisorctl reread')
        if not run('supervisorctl update'):
            run('supervisorctl start %(project_name)s' % env)

    run('supervisorctl status %(project_name)s' % env)


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
def cleanup_failed():
    print green('-----> '), 'Cleanning up failed release'
    if not env.has_key('releases'):
        _releases()

    if env.has_key('dirty_releases'):
        with cd(env.releases_path):
            run('rm -rf %s' % ' '.join(env.dirty_releases))
    else:
        print red('-----> '), 'No dirty releases to clean!'


@task
def cleanup():
    print green('-----> '), 'Cleanning up old release(s)'
    if not env.has_key('releases'):
        _releases()

    if len(env.releases) > env.keep_releases:
        directories = env.releases
        directories.reverse()
        del directories[:env.keep_releases]
        with cd(env.releases_path):
            run('rm -rf %s' % ' '.join(directories))


@task
def setup(branch=None):
    if branch:
        env.branch = branch

    run('mkdir -p %(path)s/{releases,shared/log}' % env)

    # change permission
    run('find %(path)s -type d -exec chmod 755 {} \;' % env)
    run('find %(path)s -type f -exec chmod 644 {} \;' % env)
    run('chmod -R g+w %(shared_path)s' % env)

    # clone code
    with cd(env.releases_path):
        print green('-----> '), 'Cloning the latest code'
        env.new_release = datetime.now().strftime(RELEASE_PATH_FORMAT)
        run('git clone -q --depth 1 %(repo)s %(new_release)s' % env)

    with cd('%(releases_path)s/%(new_release)s' % env):
        print green('-----> '), 'Checking out %(branch)s branch' % env
        run('git checkout %(branch)s' % env)

        if callable(first_setup_repo_func):
            print green('-----> '), 'Setting up repo'
            first_setup_repo_func()

    # symlink
    with cd(env.path):
        run('ln -nfs %(releases_path)s/%(new_release)s current' % env)

        # link supervisorctl and run
        run('ln -nfs %(current_path)s/configs/supervisor_%(env)s_%(role)s.conf '
            '/etc/supervisor/conf.d/%(project_name)s.conf' % env)
        run('supervisorctl reread')
        run('supervisorctl update')
        run('supervisorctl status')


@task
@parallel
def prepare_release(branch=None):
    if branch:
        env.branch = branch

    print green('-----> '), 'Deploying new release on %(branch)s branch' % env

    # get releases
    _releases()

    # make a copy of current release
    with cd(env.releases_path):
        run('cp -R %(current_release)s %(new_release)s' % env)

    try:
        # update code and environments
        with cd('%(releases_path)s/%(new_release)s' % env):
            print green('-----> '), 'Checking out latest code'
            run('git fetch -q')
            run('git reset --hard origin/%(branch)s' % env)

            if callable(setup_repo_func):
                # setup repo
                print green('-----> '), 'Setting up repo'
                setup_repo_func()

    except SystemExit:
        print red('-----> '), 'New release failed to deploy'
        cleanup_failed()
        exit()

    print green('-----> '), 'New release successfully build'


@task
def link_release():
    _releases()

    if not env.releases:
        print red('==>'), 'No release is available.'
        exit()

    env.new_release = env.releases[-1]

    with cd(env.path):
        run('ln -nfs %(releases_path)s/%(new_release)s current' % env)
    _restart()
    cleanup()


@task
def rollback():
    print green('-----> '), 'Rolling back to last release'
    _releases()

    if not env.has_key('previous_release'):
        abort('-----> No release to rollback!')

    env.rollback_from = env.current_release
    env.rollback_to = env.previous_release

    with cd(env.path):
        run('ln -nfs %(releases_path)s/%(rollback_to)s current' % env)
        _restart()
        run('rm -rf %(releases_path)s/%(rollback_from)s' % env)
