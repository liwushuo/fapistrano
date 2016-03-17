# -*- coding: utf-8 -*-

from fabric.api import env, run, show, hide, abort
from fabric.contrib.files import exists
from .. import signal, configuration

def init():
    configuration.setdefault('supervisor_refresh', False)
    configuration.setdefault('supervisor_output', False)
    configuration.setdefault('supervisor_check_status', False)
    configuration.setdefault('supervisor_program', '%(app_name)s')
    configuration.setdefault(
        'supervisor_target',
        '/etc/supervisor/conf.d/%(supervisor_program)s.conf'
    )
    configuration.setdefault(
        'supervisor_conf',
        '%(current_path)s/configs/supervisor_%(stage)s_%(role)s.conf'
    )
    signal.register('deploy.started', _check_supervisor_config)
    signal.register('deploy.published', _restart_service_via_supervisor)
    signal.register('deploy.restarting', _restart_service_via_supervisor)

def _check_supervisor_config(**kwargs):
    if not exists(env.supervisor_conf):
        abort('Error: can\'t find supervisor configuration.')
    run('ln -nfs %(supervisor_conf)s %(supervisor_target)s' % env)

def _restart_service_via_supervisor(**kwargs):
    output = show if env.supervisor_output else hide
    with output('output'):
        if env.supervisor_refresh:
            run('supervisorctl stop %(supervisor_program)s' % env)
            run('supervisorctl reread')
            if not run('supervisorctl update'):
                run('supervisorctl start %(supervisor_program)s' % env)
        else:
            run('supervisorctl restart %(supervisor_program)s' % env)

        # refresh group need supervisor>=3.20
    if env.supervisor_check_status:
        with show('output'):
            run('supervisorctl status %(supervisor_program)s' % env)
