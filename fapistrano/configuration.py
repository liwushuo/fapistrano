# -*- coding: utf-8 -*-

import re
from importlib import import_module
from functools import wraps
from datetime import datetime
from fabric.api import env, abort, show, hide


def format_definition():

    defs = dict(env.items())
    cals = {}

    def _apply_basic(val):
        if not isinstance(val, str):
            return val
        keys = re.findall(r'%\(([^)]*)\)', val)
        ctx = {
            k: _format_basic(k)
            for k in keys
        }
        return val % ctx

    def _format_basic(key):
        if key in cals:
            return cals[key]
        elif not isinstance(key, str):
            cals[key] = defs[key]
            return cals[key]
        else:
            cals[key] = _apply_basic(defs[key])
            return cals[key]

    def _format_structure(structure, key):
        if isinstance(structure, str):
            return _apply_basic(structure)
        elif not isinstance(structure, (list, dict)):
            return structure
        elif isinstance(structure, list):
            cals[key] = [_format_structure(elem, key) for elem in structure]
            return cals[key]
        else:
            cals[key] = {k: _format_structure(structure[k], key) for k in structure}
            return cals[key]

    for key in defs:
        if isinstance(defs[key], (int, str, long, bool, )):
            _format_basic(key)

    for key in defs:
        if isinstance(defs[key], (list, dict, )):
            _format_structure(defs[key], key)

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
    setdefault('sudo_user', 'deploy', force)
    setdefault('sudo_prefix', 'sudo -i ', force)
    setdefault('shared_writable', True, force)
    setdefault('path', '/home/%(sudo_user)s/www/%(app_name)s', force)
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
    setdefault('dry_run', False, force)

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
