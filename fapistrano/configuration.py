# -*- coding: utf-8 -*-

import re
from fabric.api import env

def get(key):
    definition = getattr(env, key)
    if callable(definition):
        return definition()
    else:
        return definition % env

def format(string):
    keys = re.findall(r'%\(([^)]*)\)', string)
    context = {key: get(key) for key in keys}
    return string % context

def setdefault(key, value):
    if not hasattr(env, key):
        setattr(env, key, value)

def set_default_configurations():
    setdefault('show_output', False)
    setdefault('user', 'deploy')
    setdefault('use_ssh_config', True)
    setdefault('path', '/home/%(user)s/www/%(project_name)s')
    setdefault('linked_files', [])
    setdefault('linked_dirs', [])
    setdefault('env_role_configs', {})
    setdefault('keey_releases', 5)
