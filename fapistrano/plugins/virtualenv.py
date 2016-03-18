# -*- coding: utf-8 -*-
"""
"""
from fabric.api import run, env, prefix, cd
from fabric.contrib.files import exists
from .. import signal, configuration

def init():
    configuration.setdefault('virtualenv_executive', '/usr/bin/env virtualenv')
    configuration.setdefault('virtualenv_requirements', '%(release_path)s/requirements.txt')
    configuration.setdefault('virtualenv_pip_upgrade', True)
    configuration.setdefault('virtualenv_venv_path', '%(release_path)s/venv')
    configuration.setdefault(
        'virtualenv_activate', 'source %(virtualenv_venv_path)s/bin/activate'
    )
    signal.register('deploy.updated', build_python_env)

def build_python_env():
    _check_virtualenv_env()

    if env.virtualenv_pip_upgrade:
        _upgrade_pip()

    _install_requirements()

def _check_virtualenv_env():
    if not exists(env.virtualenv_venv_path):
        run('%(virtualenv_executive) %(virtualenv_venv_path)s' % env)

def _upgrade_pip():
    with prefix(env.virtualenv_activate):
        run('pip install -U pip setuptools wheel')

def _install_requirements():
    with prefix(env.virtualenv_activate):
        run('pip install -r %(virtualenv_requirements)s' % env)
