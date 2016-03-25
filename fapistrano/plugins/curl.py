# -*- coding: utf-8 -*-

from fabric.api import cd, env, run, show, hide
from .. import signal, configuration

def init():
    configuration.setdefault('curl_url', '')
    configuration.setdefault('curl_output', '')
    configuration.setdefault('curl_options', '')
    configuration.setdefault('curl_extract_tar', '')
    configuration.setdefault('curl_postinstall_script', '')
    configuration.setdefault('curl_postinstall_output', True)
    signal.register('deploy.updating', download_artifact)

def download_artifact(**kwargs):
    with cd(env.release_path):
        cmd = 'curl %(curl_url)s %(curl_options)s' % env
        if env.curl_output:
            cmd += ' -o %(curl_output)s' % env
        if env.curl_extract_tar:
            cmd += ' | tar -x'
        run(cmd)
        if env.curl_postinstall_script:
            output = show if env.curl_postinstall_output else hide
            with output('output'):
                run(env.curl_postinstall_script)
