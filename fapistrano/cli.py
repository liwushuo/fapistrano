# -*- coding: utf-8 -*-

from collections import defaultdict

import yaml
import click
from click.parser import OptionParser
from fabric.api import env, execute

from fapistrano.configuration import apply_env, apply_yaml_to_env, set_default_configurations
from fapistrano import deploy


@click.group()
@click.option('-d', '--deployfile', default='./deploy.yml')
@click.pass_context
def fap(ctx, deployfile):
    try:
        with open(deployfile, 'rb') as f:
            ctx.obj = {'yaml': yaml.load(f.read())}

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
@click.pass_context
def release(ctx, role, stage, plugin_args):
    _execute(ctx, deploy.release, stage, role, None, plugin_args)


@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', help='deploy role, for example: production, staging')
@click.option('-s', '--stage', help='deploy stage, for example: app, worker, cron')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def rollback(ctx, role, stage, plugin_args):
    _execute(ctx, deploy.rollback, stage, role, None, plugin_args)


@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', help='deploy role, for example: production, staging')
@click.option('-s', '--stage', help='deploy stage, for example: app, worker, cron')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def restart(ctx, role, stage, plugin_args):
    _execute(ctx, deploy.restart, stage, role, None, plugin_args)

@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-s', '--stage', required=True, help='deploy stage, for example: app, worker, cron')
@click.option('-c', '--command', help='run command')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def once(ctx, role, stage, command, plugin_args):
    _execute(ctx, deploy.once, stage, role, command, plugin_args)


@fap.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('-r', '--role', required=True, help='deploy role, for example: production, staging')
@click.option('-s', '--stage', required=True, help='deploy stage, for example: app, worker, cron')
@click.argument('plugin_args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def shell(ctx, role, stage, plugin_args):
    _execute(ctx, deploy.shell, stage, role, None, plugin_args)


def _apply_plugin_options(plugin_args):
    parser = OptionParser()
    for key in env:
        option_key = '--%s' % key.replace('_', '-')
        parser.add_option([option_key], key)

    opts, largs, order = parser.parse_args(list(plugin_args))
    for arg_key in order:
        setattr(env, arg_key, opts[arg_key])

def get_method_name(method):
    return method.__name__.split('.')[-1]

def _setup_execution(ctx, method, role, stage, command, plugin_args):
    env.run_command = command or ''
    set_default_configurations(force=True)
    apply_yaml_to_env(ctx.obj.get('yaml'), get_method_name(method))
    apply_env(stage, role)
    _apply_plugin_options(plugin_args)

def _abort(message):
    click.secho('Error: %s' % message, blink=True, fg='red')
    exit(1)

def _log(message):
    click.secho(message, blink=True, fg='green')

def _get_execute_stage_and_roles(ctx, stage, role):
    stage_role_configs = ctx.obj.get('yaml').get('stage_role_configs')

    if not stage_role_configs:
        _abort('Stage role config not found.')

    if not role and not stage:
        _abort('Stage or role not found.')

    if not role and stage not in stage_role_configs:
        _abort('Stage not found.')

    if not role and not stage_role_configs.get(stage):
        _abort('No role defined in this stage.')

    if stage and role and stage:
        return [(stage, role)]

    if not role:
        comb = []
        for _role in stage_role_configs[stage].keys():
            comb.append((stage, _role))
        return comb

    roles = defaultdict(set)
    for _stage in stage_role_configs:
        for _role in stage_role_configs[_stage]:
            roles[_role].add(_stage)

    if role not in roles:
        _abort('Role not found.')

    if not roles[role]:
        _abort('No stage defined for this role.')

    comb = []
    for _stage in roles[role]:
        comb.append((_stage, role))
    return comb

def _execute(ctx, method, stage=None, role=None, command=None, plugin_args=None):
    combinations = _get_execute_stage_and_roles(ctx, stage, role)
    for stage, role in combinations:
        _log('Executing %s at %s' % (role, stage))
        _setup_execution(ctx, method, role, stage, command, plugin_args)
        execute(method)


if __name__ == '__main__':
    import os
    auto_envvar_prefix = os.environ.get('FAP_APP') or ''
    fap(obj={}, auto_envvar_prefix=auto_envvar_prefix)
