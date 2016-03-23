# -*- coding: utf-8 -*-


import click
import yaml
from os import environ
from click.parser import OptionParser
from fabric.api import env, execute
from fapistrano.configuration import apply_env, apply_yaml_to_env
from fapistrano import app
from fapistrano import deploy


@click.group()
@click.option('-d', '--deployfile', default='./deploy.yml')
def fap(deployfile):
    try:
        with open(deployfile, 'rb') as f:
            apply_yaml_to_env(f.read())
    except IOError:
        if deploy_file == './deploy.yml':
            print("cannot find deployfile. Did you put a deploy.yml file on current directory?")
            exit(1)
        else:
            print('cannot find deployfile. Does this file really exist?')
            exit(1)


@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-s', '--stage', required=True, help='deploy stage, for example: app, worker, cron')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
def release(role, stage, plugin_args):
    _setup_execution(role, stage, plugin_args)
    execute(deploy.release)

@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-s', '--stage', required=True, help='deploy stage, for example: app, worker, cron')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
def rollback(role, stage, plugin_args):
    _setup_execution(role, stage, plugin_args)
    execute(deploy.rollback)

@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-s', '--stage', required=True, help='deploy stage, for example: app, worker, cron')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
def restart(role, stage, plugin_args):
    _setup_execution(role, stage, plugin_args)
    execute(deploy.restart)


def _apply_plugin_options(plugin_args):
    parser = OptionParser()
    for key in env:
        option_key = '--%s' % key.replace('_', '-')
        parser.add_option([option_key], key)

    opts, largs, order = parser.parse_args(list(plugin_args))
    for arg_key in order:
        setattr(env, arg_key, opts[arg_key])

def _setup_execution(role, stage, plugin_args):
    env.role = role
    env.stage = stage
    apply_env(stage, role)
    _apply_plugin_options(plugin_args)

if __name__ == '__main__':
    import os
    auto_envvar_prefix = os.environ.get('FAP_APP') or ''
    fap(auto_envvar_prefix=auto_envvar_prefix)
