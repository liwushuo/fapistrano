# -*- coding: utf-8 -*-

from fabric.api import env, run as fabrun, sudo, settings
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

def run(command, sudo_user=None):
    sudo_user = sudo_user or env.sudo_user
    if not sudo_user or sudo_user == env.user:
        fabrun(command % env)
    else:
        with settings(sudo_user=sudo_user):
            sudo(command % env)
