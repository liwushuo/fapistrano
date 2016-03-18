# -*- coding: utf-8 -*-

from fabric.api import env, run, cd, show
from .. import signal, configuration

def init():
    configuration.setdefault('virtualenvtools_strategy', 'update-path')
    configuration.setdefault('virtualenvtools_executable', 'virtualenv-tools')
    configuration.setdefault('virtualenvtools_venv_path', '%(release_path)s/venv')
    signal.register('deploy.updated', relocate_env)

def relocate_env():
    with cd(env.release_path):
        with show('output'):
            if env.virtualenvtools_strategy == 'update-path':
                run('%(virtualenvtools_executable)s --update-path %(virtualenvtools_venv_path)s' % env)
            elif env.virtualenvtools_strategy == 'reinitialize':
                run('rm %(virtualenvtools_venv_path)s/bin/python*' % env)
                run('%(virtualenvtools_executable)s --reinitialize %(virtualenvtools_venv_path)s' % env)
