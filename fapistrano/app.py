# -*- coding: utf-8 -*-

from importlib import import_module

from fabric.api import env

def init():
    for plugin in env.plugins:
        mod = import_module(plugin)
        mod.init()
