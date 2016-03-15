# -*- coding: utf-8 -*-

from fabric.api import cd, env, run, local, task, abort
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

    signal.register('deploy.started', check_repo)
    signal.register('deploy.reverting', log_previous_revision)
    signal.register('deploy.finishing_rollback', log_rollback_revision)
    signal.register('deploy.updating', update_git_repo)

def check_repo(**kwargs):
    _check()

def log_previous_revision(**kwargs):
    head = _read_current_revision()
    green_alert('Rollback from %s' % head)

def log_rollback_revision(**kwargs):
    head = _read_current_revision()
    green_alert('Rollback to %s' % head)

def update_git_repo(**kwargs):
    if not exists('%(path)s/repo' % env):
        _clone()
    _update()
    _set_current_version()
    _release()
    _echo_revision()


def _get_remote_head():
    if exists('.git'):
        return run("git rev-parse --short HEAD", quiet=True)


def _get_delta(current_version, upstream='origin', bsd=True):
    if not env.git_show_delta:
        return

    local('/usr/bin/env git fetch -q %s' % upstream)
    return local(
        '/usr/bin/env git log '
        '--reverse '
        '--pretty="%%h %%s: %%b" '
        '--merges %s..%s/master | '

        '/usr/bin/env sed -%s '
        '"s/Merge pull request #([0-9]+) from ([^/]+)\\/[^:]+/#\\1\\/\\2/"'
        % (
            current_version,
            upstream,
            'E' if bsd else 'r'
        ),
        capture=True
    ).decode('utf8')


def _check():
    with cd('%(path)s/repo' % env):
        run('git ls-remote --heads %(repo)s' % env)


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


def _release():
    with cd('%(path)s/repo' % env):
        run('git archive %(branch)s '
            '| tar -x -f - -C %(releases_path)s/%(new_release)s' % env)


def _get_revision():
    with cd('%(path)s/repo' % env):
        return run(
            'git rev-list '
            '--max-count=1 '
            '--abbrev-commit '
            '--abbrev=12 '
            '%(branch)s' % env
        )


def _echo_revision():
    with cd('%(releases_path)s/%(new_release)s' % env):
        run('echo %(current_version)s >> REVISION' % env)


def _read_current_revision():
    return run('cat %(current_path)s/REVISION' % env)


def _set_current_version():
    env.current_version = _get_revision()
