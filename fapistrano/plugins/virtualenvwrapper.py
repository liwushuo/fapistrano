# -*- coding: utf-8 -*-

from fabric.api import env, prefix, cd
from fabric.contrib.files import exists
from .. import signal, configuration
from ..utils import run

def init():
    configuration.setdefault('virtualenvwrapper_source', '/usr/local/bin/virtualenvwrapper.sh')
    configuration.setdefault('virtualenvwrapper_home', '/home/%(user)s/.virtualenvs')
    configuration.setdefault('virtualenvwrapper_project', '/%(virtualenvwrapper_home)s/%(app_name)s')
    configuration.setdefault('virtualenvwrapper_pip_upgrade', True)
    configuration.setdefault('virtualenvwrapper_requirements', '%(release_path)s/requirements.txt')
    configuration.setdefault(
        'virtualenvwrapper_activate',
        'source %(virtualenvwrapper_project)s/bin/activate'
    )
    signal.register('deploy.updated', check_python_env)


def check_python_env():
    _check_virtualenvwrapper_env()
    if env.virtualenvwrapper_pip_upgrade:
        _upgrade_pip()
    _install_requirements()


def _check_virtualenvwrapper_env():
    if not exists(env.virtualenvwrapper_project):
        run('source %(virtualenvwrapper_source)s && mkvirtualenv %(app_name)s' % env)


def _upgrade_pip():
    with prefix(env.virtualenvwrapper_activate):
        run('pip install -q -U pip setuptools wheel || pip install -U pip setuptools wheel')


def _install_requirements():
    with prefix(env.virtualenvwrapper_activate):
        run('pip install -r %(virtualenvwrapper_requirements)s' % env)
