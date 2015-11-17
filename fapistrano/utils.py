# -*- coding: utf-8 -*-

from functools import wraps

from fabric.api import env, show, hide, abort
from fabric.colors import green, red, white


def red_alert(msg, bold=True):
    print red('===>', bold=bold), white(msg, bold=bold)


def green_alert(msg, bold=True):
    print green('===>', bold=bold), white(msg, bold=bold)


def _apply_config():
    stage = env.get('env')
    role = env.get('role')

    # raise error when env/role not set both
    if not stage or not role:
        abort('env or role not set!')

    env.path = '/home/%(user)s/www/%(project_name)s' % env
    env.current_path = '%(path)s/current' % env
    env.releases_path = '%(path)s/releases' % env
    env.shared_path = '%(path)s/shared' % env
    env.activate = 'source ~/.virtualenvs/%(project_name)s/bin/activate' % env


# hosts config must be set before task running
def _apply_env_role_config():
    stage = env.get('env')
    role = env.get('role')

    # ensure stage and role are set
    if not stage or not role:
        return

    if stage in env.env_role_configs:
        if role in env.env_role_configs[stage]:
            env.update(env.env_role_configs[stage][role])


def with_configs(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        _apply_config()
        output_func = show if env.show_output else hide
        with output_func('output'):
            ret = func(*args, **kwargs)
        return ret
    return wrapped


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
