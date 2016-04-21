# -*- coding: utf-8 -*-

from fabric.api import env, run, settings
from fabric.colors import green, red, white, yellow


def red_alert(msg, bold=True):
    print red('===>', bold=bold), white(msg, bold=bold)


def green_alert(msg, bold=True):
    print green('===>', bold=bold), white(msg, bold=bold)


def yellow_alert(msg, bold=True):
    print yellow('===>', bold=bold), white(msg, bold=bold)

def dry_run_function(function, **data):
    green_alert(' '.join(function.__name__.split('_')))

def run_function(function, **data):
    if env.dry_run:
        dry_run_function(function, **data)
    else:
        function(**data)

def run_as(command, sudo='current'):
    if sudo == 'current':
        run(command % env)
    else:
        with settings(sudo_user=sudo):
            sudo(command % env)
