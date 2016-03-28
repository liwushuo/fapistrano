# -*- coding: utf-8 -*-

from collections import defaultdict

import click
from click.parser import OptionParser
from fabric.api import env, execute

from fapistrano.configuration import apply_env, apply_yaml_to_env
from fapistrano import deploy


@click.group()
@click.option('-d', '--deployfile', default='./deploy.yml')
def fap(deployfile):
    try:
        with open(deployfile, 'rb') as f:
            apply_yaml_to_env(f.read())
    except IOError:
        if deployfile == './deploy.yml':
            _abort("cannot find deployfile. Did you put a deploy.yml file on current directory?")
        else:
            _abort('cannot find deployfile. Does this file really exist?')


@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', help='deploy role, for example: production, staging')
@click.option('-s', '--stage', help='deploy stage, for example: app, worker, cron')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
def release(role, stage, plugin_args):
    _execute(deploy.release, stage, role, plugin_args)


@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', help='deploy role, for example: production, staging')
@click.option('-s', '--stage', help='deploy stage, for example: app, worker, cron')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
def rollback(role, stage, plugin_args):
    _execute(deploy.rollback, stage, role, plugin_args)


@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', help='deploy role, for example: production, staging')
@click.option('-s', '--stage', help='deploy stage, for example: app, worker, cron')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
def restart(role, stage, plugin_args):
    _execute(deploy.restart, stage, role, plugin_args)


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

def _abort(message):
    click.secho(message, blink=True, fg='red')
    exit(1)

def _get_execute_stage_and_roles(stage, role):
    if not stage and not role:
        _abort('Stage or role not found.')
    elif not role and stage not in env.stage_role_configs:
        _abort('Stage not found.')
    elif not role and not env.stage_role_configs[stage]:
        _abort('No role defined in this stage.')
    elif not role:
        _stage = env.stage_role_configs[stage]
        for _role in _stage.keys():
            yield (stage, _role)
        return

    roles = defaultdict(set)
    for _stage in env.stage_role_configs:
        for _role in env.stage_role_configs[_stage]:
            roles[_role].add(_stage)

    if role not in roles:
        _abort('Role not found.')
    elif not roles[role]:
        _abort('No stage defined for this role.')
    else:
        for stage in roles[role]:
            yield (stage, role)

def _execute(method, stage=None, role=None, plugin_args=None):
    combinations = _get_execute_stage_and_roles(stage, role)
    for stage, role in combinations:
        print stage, role
        _setup_execution(role, stage, plugin_args)
        execute(method)


if __name__ == '__main__':
    import os
    auto_envvar_prefix = os.environ.get('FAP_APP') or ''
    fap(auto_envvar_prefix=auto_envvar_prefix)
