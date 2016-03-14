# -*- coding: utf-8 -*-

from fabric.api import show, run, env, cd

from .. import signal

def init():
    signal.register('deploy.updated', build_fis_assets)

def build_fis_assets():
    with show('output'):
        run('''
        fis release --file  %(releases_path)s/%(new_release)s/%(fis_conf)s \
        --dest  %(releases_path)s/%(new_release)s/%(fis_dest)s \
        --root %(releases_path)s/%(new_release)s/%(fis_source)s \
        --optimize \
        --pack \
        --md5
        ''' % env)
