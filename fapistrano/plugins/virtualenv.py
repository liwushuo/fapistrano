# -*- coding: utf-8 -*-
"""
virtualenv plugin provide

2 virtualenv environment:

1. virtualenvwrapper in /home/depploy/.virtulaenvs/%(project_name)s
2. virtualenv in each release directory

2 pip install:

1. pip
2. pip wheel

"""
from fabric.api import run, env, prefix, cd
from fabric.contrib.files import exists
from .. import signal

def init():
    if not hasattr(env, 'virtualenv_type'):
        env.virtualenv_type = 'virtualenvwrapper'

    if not hasattr(env, 'virtualenv_upgrade_pip'):
        env.virtualenv_upgrade_pip = True

    signal.register('deploy.updated', build_python_env)

def build_python_env():
    if env.virtualenv_type == 'virtualenvwrapper':
        _check_virtualenvwrapper_env()
        _check_virtualenvwrapper_activate()
    elif env.virtualenv_type == 'virtualenv':
        _check_virtualenv_env()
        _check_virtualenv_activate()

    if env.virtualenv_upgrade_pip:
        _upgrade_pip()

    _install_requirements()

def _check_virtualenvwrapper_env():
    if not exists('~/.virtualenvs/%(project_name)s' % env):
        run('source %(virtualenvwrapper_source)s && mkvirtualenv %(project_name)s' % env)

def _check_virtualenv_env():
    if not exists('%(releases_path)s/%(new_release)s/venv' % env):
        run('virtualenv %(releases_path)s/%(new_release)s/venv' % env)

def _check_virtualenvwrapper_activate():
    env.activate = 'source ~/.virtualenvs/%(project_name)s/bin/activate' % env

def _check_virtualenv_activate():
    env.activate = 'source %(releases_path)s/%(new_release)s/venv/bin/activate' % env

def _upgrade_pip():
    with prefix(env.activate):
        run('pip install -q -U pip setuptools wheel || pip install -U pip setuptools wheel')

def _install_requirements():
    with prefix(env.activate):
        with cd('%(releases_path)s/%(new_release)s' % env):
            run('pip install -r requirements.txt' % env)
