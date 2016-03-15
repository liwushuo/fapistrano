# -*- coding: utf-8 -*-


import click
import yaml
from os import environ
from fabric.api import env, execute
from fapistrano.app import init_cli
from fapistrano.configuration import apply_env
from fapistrano import deploy

@click.group()
@click.option('-d', '--deployfile')
def fap(deployfile):
    if environ.get('DEPLOY_FILE') and not deployfile:
        deployfile = environ.get('DEPLOY_FILE')
    elif not deployfile:
        deployfile = './deploy.yml'
    with open(deployfile, 'rb') as f:
        conf = yaml.load(f.read())
        init_cli(conf)

@fap.command()
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-s', '--stage', required=True, help='deploy stage, for example: app, worker, cron')
def release(role, stage):
    env.role = role
    env.stage = stage
    apply_env(stage, role)
    execute(deploy.release)

@fap.command()
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-s', '--stage', required=True, help='deploy stage, for example: app, worker, cron')
def rollback(role, stage):
    env.role = role
    env.stage = stage
    apply_env(stage, role)
    execute(deploy.rollback)

@fap.command()
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-s', '--stage', required=True, help='deploy stage, for example: app, worker, cron')
def restart(role, stage):
    env.role = role
    env.stage = stage
    apply_env(stage, role)
    execute(deploy.restart)

if __name__ == '__main__':
    fap()
