# -*- coding: utf-8 -*-

from functools import wraps

from fabric.api import env, show, hide
from fabric.colors import green, red, white


def red_alert(msg, bold=True):
    print red('===>', bold=bold), white(msg, bold=bold)


def green_alert(msg, bold=True):
    print green('===>', bold=bold), white(msg, bold=bold)


def _apply_env_role_config():
    stage = env.get('env')
    role = env.get('role')

    # TODO: raise error when env/role not set both

    # ensure stage and role are set
    if not stage or not role:
        return

    if stage in env.env_role_configs:
        if role in env.env_role_configs[stage]:
            env.update(env.env_role_configs[stage][role])

    env.path = '/home/%(user)s/www/%(project_name)s' % env
    env.current_path = '%(path)s/current' % env
    env.releases_path = '%(path)s/releases' % env
    env.shared_path = '%(path)s/shared' % env
    env.activate = 'source ~/.virtualenvs/%(project_name)s/bin/activate' % env


def register_role(role):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            env.role = role
            _apply_env_role_config()
            return func(*args, **kwargs)
        return wrapped
    return wrapper


def register_env(stage):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            env.env = stage
            _apply_env_role_config()
            return func(*args, **kwargs)
        return wrapped
    return wrapper
