# -*- coding: utf-8 -*-

from importlib import import_module

from fabric.api import env

def init():
    if not hasattr(env, 'plugins'):
        return
    for plugin in env.plugins:
        mod = import_module(plugin)
        mod.init()

def init_cli(conf):
    for key, value in conf.items():
        setattr(env, key, value)
    init()
