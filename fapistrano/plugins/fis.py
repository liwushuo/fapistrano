# -*- coding: utf-8 -*-

from fabric.api import show, run, env, cd, show, hide

from .. import signal, configuration

def init():
    configuration.setdefault('fis_output', False)
    configuration.setdefault('fis_domain', False)
    configuration.setdefault('fis_optimize', True)
    configuration.setdefault('fis_pack', True)
    signal.register('deploy.updated', build_fis_assets)

def build_fis_assets():
    output = show if env.fis_output else hide
    with output('output'):
        cmd = ('fis release --file %(release_path)s/%(fis_conf)s '
            '--dest %(release_path)s/%(fis_dest)s '
            '--root %(release_path)s/%(fis_source)s ') % env
        if env.fis_optimize:
            cmd += '--optimize '
        if env.fis_pack:
            cmd += '--pack '
        if env.fis_domain:
            cmd += '--domains '
        run(cmd)
