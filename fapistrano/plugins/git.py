# -*- coding: utf-8 -*-

from fabric.api import cd, env, local, task, abort
from fabric.contrib.files import exists

from ..utils import green_alert, red_alert, yellow_alert, run
from .. import signal, configuration

def init():
    configuration.setdefault('git_shallow_clone', 1)
    configuration.setdefault('branch', 'master')
    configuration.setdefault('revision_file', 'REVISION')
    configuration.setdefault('repo_path', '%(path)s/repo')
    configuration.setdefault('repo_head_path', '%(repo_path)s/HEAD')
    configuration.setdefault('git_archive_tree', '')
    signal.register('deploy.started', check_repo)
    signal.register('deploy.reverting', log_previous_revision)
    signal.register('deploy.finishing_rollback', log_rollback_revision)
    signal.register('deploy.updating', update_git_repo)


def check_repo(**kwargs):
    _check()


def log_previous_revision(**kwargs):
    if _does_current_revision_exist():
        head = _read_current_revision()
        green_alert('Rollback from %s' % head)


def log_rollback_revision(**kwargs):
    if _does_current_revision_exist():
        head = _read_current_revision()
        green_alert('Rollback to %s' % head)


def update_git_repo(**kwargs):
    _update()
    _set_current_version()
    _release()
    _echo_revision()


def _check():
    if not exists(env.repo_path):
        _clone()

    with cd(env.repo_path):
        run('git ls-remote --heads %(repo)s' % env)


def _clone():
    if exists(env.repo_head_path):
        abort('Repo has cloned already!')

    if env.git_shallow_clone:
        run('git clone --mirror --depth %(git_shallow_clone)s '
            '--no-single-branch %(repo)s %(repo_path)s' % env)
    else:
        run('git clone --mirror %(repo)s %(repo_path)s' % env)


def _update():
    with cd(env.repo_path):
        if env.git_shallow_clone:
            run('git fetch --depth %(git_shallow_clone)s origin %(branch)s' % env)
        else:
            run('git remote update --prune')


def _release():
    with cd(env.repo_path):
        if env.git_archive_tree:
            env.git_strip_components = len(env.git_archive_tree.split('/'))
            run('git archive %(branch)s %(git_archive_tree)s | tar -x --strip-components %(git_strip_components)d -f - -C %(release_path)s/' % env)
        else:
            run('git archive %(branch)s | tar -x -f - -C %(release_path)s/' % env)


def _get_revision():
    with cd(env.repo_path):
        return run(
            'git rev-list '
            '--max-count=1 '
            '--abbrev-commit '
            '--abbrev=12 '
            '%(branch)s' % env
        )


def _echo_revision():
    with cd(env.release_path):
        run('echo %(current_version)s >> %(revision_file)s' % env)


def _read_current_revision():
    return run('cat %(current_path)s/%(revision_file)s' % env)

def _does_current_revision_exist():
    return exists('%(current_path)s/$(revision_file)s' % env)

def _set_current_version():
    env.current_version = _get_revision()
