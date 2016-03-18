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


def setdefault(key, value, force=False):
    if force:
        setattr(env, key, value)
    elif not hasattr(env, key):
        setattr(env, key, value)

RELEASE_PATH_FORMAT = '%y%m%d-%H%M%S'

def set_default_configurations():
    setdefault('show_output', False)
    setdefault('user', 'deploy')
    setdefault('use_ssh_config', True)
    setdefault('path', '/home/%(user)s/www/%(app_name)s', force=True)
    setdefault('current_path', '%(path)s/current')
    setdefault('releases_path', '%(path)s/releases')
    setdefault('shared_path', '%(path)s/shared')
    setdefault('new_release', datetime.now().strftime(RELEASE_PATH_FORMAT))
    setdefault('release_path', '%(releases_path)s/%(new_release)s')
    setdefault('linked_files', [])
    setdefault('linked_dirs', [])
    setdefault('env_role_configs', {})
    setdefault('keey_releases', 5)
    setdefault('stage_role_configs', {})

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

def apply_yaml_to_env(data):
    import yaml
    confs = yaml.load(data)
    for key, value in confs.items():
        setattr(env, key, value)
    if not hasattr(env, 'plugins'):
        return
    for plugin in env.plugins:
        mod = import_module(plugin)
        mod.init()

def apply_env(stage, role):
    env.stage = stage
    env.role = role
    check_stage_and_role()
    set_default_configurations()
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
