# -*- coding: utf-8 -*-

import re
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

def set_default_configurations():
    setdefault('show_output', False)
    setdefault('user', 'deploy')
    setdefault('use_ssh_config', True)
    setdefault('path', '/home/%(user)s/www/%(project_name)s')
    setdefault('linked_files', [])
    setdefault('linked_dirs', [])
    setdefault('env_role_configs', {})
    setdefault('keey_releases', 5)
