# -*- coding: utf-8 -*-

from fabric.api import show, env, cd, show, hide

from .. import signal, configuration
from ..utils import run

def init():
    configuration.setdefault('fis_output', False)
    configuration.setdefault('fis_domains', False)
    configuration.setdefault('fis_md5', True)
    configuration.setdefault('fis_optimize', True)
    configuration.setdefault('fis_pack', True)
    configuration.setdefault('fis_conf', 'fis-conf.js')
    signal.register('deploy.updated', build_fis_assets)
    # FIXME: asset fis install

def build_fis_assets():
    output = show if env.fis_output else hide
    with output('output'):
        with cd('%(release_path)s/%(fis_source)s' % env):
            cmd = (
                'fis release '
                '--file %(fis_conf)s '
                '--dest %(fis_dest)s '
            ) % env
            if env.fis_md5:
                cmd += '--md5 '
            if env.fis_optimize:
                cmd += '--optimize '
            if env.fis_pack:
                cmd += '--pack '
            if env.fis_domains:
                cmd += '--domains '
            run(cmd)
