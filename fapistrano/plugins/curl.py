# -*- coding: utf-8 -*-

from fabric.api import cd, env, run
from .. import signal, configuration

def init():
    configuration.setdefault('curl_url', '')
    configuration.setdefault('curl_options', '')
    signal.register('deploy.updating', download_artifact)

def download_artifact(**kwargs):
    with cd(env.release_path):
        run('curl %(curl_url)s %(curl_options)s' % env)
