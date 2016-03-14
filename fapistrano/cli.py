# -*- coding: utf-8 -*-

import click
import yaml
from fabric.api import env as fabenv, local, execute
from fapistrano.app import init_cli
from fapistrano.utils import with_configs, register_role, register_env, _apply_env_role_config
from fapistrano import deploy

@click.group()
@click.option('-d', '--deployfile', default='deploy.yml')
def fap(deployfile):
    with open(deployfile, 'rb') as f:
        conf = yaml.load(f.read())
        init_cli(conf)

@fap.command()
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-e', '--env', required=True, help='deploy env, for example: app, worker, cron')
def release(role, env):
    fabenv.role = role
    fabenv.env = env
    _apply_env_role_config()
    execute(deploy.release)

@fap.command()
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-e', '--env', required=True, help='deploy env, for example: app, worker, cron')
def rollback(role, env):
    fabenv.role = role
    fabenv.env = env
    _apply_env_role_config()
    execute(deploy.rollback)

@fap.command()
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-e', '--env', required=True, help='deploy env, for example: app, worker, cron')
def restart(role, env):
    fabenv.role = role
    fabenv.env = env
    _apply_env_role_config()
    execute(deploy.rollback)

if __name__ == '__main__':
    fap()
