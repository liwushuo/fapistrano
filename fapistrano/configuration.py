# -*- coding: utf-8 -*-

import re
from importlib import import_module
from functools import wraps
from datetime import datetime
from fabric.api import env, abort, show, hide


def format_definition():

    def _format(key, defs, cals):
        if key in cals:
            return cals[key]
        elif not isinstance(defs[key], str):
            cals[key] = defs[key]
            return defs[key]
        else:
            keys = re.findall(r'%\(([^)]*)\)', defs[key])
            ctx = {
                k: _format(k, defs, cals)
                for k in keys
            }
            cals[key] = defs[key] % ctx
            return cals[key]

    defs = dict(env.items())
    cals = {}

    for key in defs:
         _format(key, defs, cals)

    return cals


def setdefault(key, value, force=True):
    if force:
        setattr(env, key, value)
    elif not hasattr(env, key):
        setattr(env, key, value)

RELEASE_PATH_FORMAT = '%y%m%d-%H%M%S'

def set_default_configurations(force=True):
    setdefault('show_output', False, force)
    setdefault('user', 'deploy', force)
    setdefault('use_ssh_config', True, force)
    setdefault('shared_writable', True, force)
    setdefault('path', '/home/%(user)s/www/%(app_name)s', force)
    setdefault('current_path', '%(path)s/current', force)
    setdefault('releases_path', '%(path)s/releases', force)
    setdefault('shared_path', '%(path)s/shared', force)
    setdefault('new_release', datetime.now().strftime(RELEASE_PATH_FORMAT), force)
    setdefault('release_path', '%(releases_path)s/%(new_release)s', force)
    setdefault('environment_file', '%(release_path)s/.env', force)
    setdefault('environment', {}, force)
    setdefault('linked_files', [], force)
    setdefault('linked_dirs', [], force)
    setdefault('env_role_configs', {}, force)
    setdefault('keep_releases', 5, force)
    setdefault('stage_role_configs', {}, force)

def check_stage_and_role():
    stage = env.get('stage')
    role = env.get('role')

    # raise error when env/role not set both
    if not stage or not role:
        abort('stage or role not set!')

def apply_configurations_to_env(conf):
    for env_item in conf:
        env_value = conf.get(env_item)
        setattr(env, env_item, env_value)

def apply_role_configurations_to_env(stage, role):
    if stage in env.stage_role_configs:
        if role in env.stage_role_configs[stage]:
            config = env.stage_role_configs[stage][role]
            apply_configurations_to_env(config)

def apply_yaml_to_env(confs, operation):

    from .signal import clear
    clear()

    plugins = confs.get(operation + '_plugins') or confs.get('plugins') or []

    for plugin in plugins:
        mod = import_module(plugin)
        mod.init()

    for key, value in confs.items():
        setattr(env, key, value)

def apply_env(stage, role):
    env.stage = stage
    env.role = role
    check_stage_and_role()
    set_default_configurations(force=False)
    apply_role_configurations_to_env(stage, role)
    apply_configurations_to_env(format_definition())


def with_configs(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        output_func = show if env.show_output else hide
        with output_func('output'):
            ret = func(*args, **kwargs)
        return ret
    return wrapped
