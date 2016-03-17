# -*- coding: utf-8 -*-


import click
import yaml
from os import environ
from click.parser import OptionParser
from fabric.api import env, execute
from fapistrano.app import init_cli
from fapistrano.configuration import apply_env
from fapistrano import deploy

def _apply_plugin_options(plugin_args):
    parser = OptionParser()
    for key in env:
        option_key = '--%s' % key.replace('_', '-')
        parser.add_option([option_key], key)

    opts, largs, order = parser.parse_args(list(plugin_args))
    for arg_key in order:
        setattr(env, arg_key, opts[arg_key])

@click.group()
@click.option('-d', '--deployfile', default='./deploy.yml')
def fap(deployfile):
    with open(deployfile, 'rb') as f:
        conf = yaml.load(f.read())
        init_cli(conf)

@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging', allow_from_autoenv=True)
@click.option('-s', '--stage', required=True, help='deploy stage, for example: app, worker, cron', allow_from_autoenv=True)
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
def release(role, stage, plugin_args):
    env.role = role
    env.stage = stage
    apply_env(stage, role)
    _apply_plugin_options(plugin_args)
    execute(deploy.release)

@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-s', '--stage', required=True, help='deploy stage, for example: app, worker, cron')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
def rollback(role, stage, plugin_args):
    env.role = role
    env.stage = stage
    apply_env(stage, role)
    _apply_plugin_options(plugin_args)
    execute(deploy.rollback)

@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-s', '--stage', required=True, help='deploy stage, for example: app, worker, cron')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
def restart(role, stage, plugin_args):
    env.role = role
    env.stage = stage
    apply_env(stage, role)
    _apply_plugin_options(plugin_args)
    execute(deploy.restart)

if __name__ == '__main__':
    import os
    auto_envvar_prefix = os.environ.get('FAP_APP') or ''
    fap(auto_envvar_prefix=auto_envvar_prefix)
