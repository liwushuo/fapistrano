# -*- coding: utf-8 -*-

from fabric.api import env, task, run, prefix
from fapistrano import deploy
from fapistrano.utils import register_env, register_role

env.project_name = 'test'
env.app_name = 'test'
env.repo = 'git@git.test.com:test/test-repo.git'
env.user = 'deploy'
env.use_ssh_config = True
env.keep_releases = 5
env.branch = 'master'
env.configs_path = '/home/%(user)s/www/configs' % env
env.env_role_configs = {
    'production': {
        'app': {
            'project_name': 'test',
            'hosts': ['test-host']
        }
    },
    'staging': {
        'app': {
        }
    }
}


@task
@register_env('production')
def production():
    pass


@task
@register_role('app')
def app():
    pass


@deploy.first_setup_repo
def deploy_first_setup_repo():
    run('source /usr/local/bin/virtualenvwrapper.sh && mkvirtualenv %(project_name)s' % env)
    _setup_repo()


@deploy.setup_repo
def deploy_setup_repo():
    _setup_repo()


def _setup_repo():
    run('test -d %(configs_path)s/%(app_name)s && '
        'cp %(configs_path)s/%(app_name)s/* %(app_name)s/settings || '
        'echo "no shared config"' % env)
    with prefix(env.activate):
        run('pip install -q -r requirements.txt || pip install -r requirements.txt')
