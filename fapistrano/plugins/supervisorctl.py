# -*- coding: utf-8 -*-

from fabric.api import env, run, show, hide
from .. import signal, configuration

def init():
    configuration.setdefault('supervisor_refresh', False)
    configuration.setdefault('supervisor_output', False)
    configuration.setdefault('supervisor_check_status', False)
    configuration.setdefault('supervisor_target', '%(project_name)s')
    configuration.setdefault(
        'supervisor_conf',
        '%(shared_path)s/configs/supervisor_%(stage)s_%(role)s.conf'
    )
    signal.register('deploy.started', _check_supervisor_config)
    signal.register('deploy.published', _restart_service_via_supervisor)
    signal.register('deploy.restarting', _restart_service_via_supervisor)

def _check_supervisor_config(**kwargs):
    run('test -e %(supervisor_conf)s' % env)
    run('ln -nfs %(supervisor_conf)s /etc/supervisor/conf.d/%(project_name)s.conf' % env)
    run('supervisorctl reread')

def _restart_service_via_supervisor(**kwargs):
    output = show if env.supervisor_output else hide
    with output('output'):
        if env.supervisor_refresh:
            run('supervisorctl stop %(supervisor_target)s' % env)
            run('supervisorctl reread')
            if not run('supervisorctl update'):
                run('supervisorctl start %(supervisor_target)s' % env)
        else:
            run('supervisorctl restart %(supervisor_target)s' % env)

        # refresh group need supervisor>=3.20
    if env.supervisor_check_status:
        with show('output'):
            run('supervisorctl status %(supervisor_target)s' % env)
