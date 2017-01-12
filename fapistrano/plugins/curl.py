# -*- coding: utf-8 -*-

import sys
from contextlib import contextmanager

from fabric.api import cd, env, show, hide
from .. import signal, configuration
from ..utils import run

def init():
    configuration.setdefault('curl_url', '')
    configuration.setdefault('curl_output', '')
    configuration.setdefault('curl_options', '')
    configuration.setdefault('curl_extract_tar', '')
    configuration.setdefault('curl_extract_tgz', '')
    configuration.setdefault('curl_user', '')
    configuration.setdefault('curl_postinstall_script', '')
    configuration.setdefault('curl_postinstall_output', True)
    signal.register('deploy.updating', download_artifact)

class StreamFilter(object):

    def __init__(self, filter, stream):
        self.stream = stream
        self.filter = filter

    def write(self,data):
        if not self.filter:
            self.stream.write(data)
            self.stream.flush()
        else:
            user = self.filter[:self.filter.index(':')]
            data = data.replace(self.filter, '%s:**************' % user)
            self.stream.write(data)
            self.stream.flush()

    def flush(self):
        self.stream.flush()

@contextmanager
def credential_output():
    sys_stdout = sys.stdout
    credential_stdout = StreamFilter(env.curl_user, sys_stdout)

    sys.stdout = credential_stdout
    yield
    sys.stdout = sys_stdout

def download_artifact(**kwargs):
    with cd(env.release_path), credential_output():
        cmd = 'curl --max-time 30 --retry 3 %(curl_url)s' % env
        if env.curl_user:
            cmd += ' --user %(curl_user)s' % env
        if env.curl_output:
            cmd += ' -o %(curl_output)s' % env
        if env.curl_options:
            cmd += ' %(curl_options)s' % env
        if env.curl_extract_tar:
            cmd += ' | tar -x'
        elif env.curl_extract_tgz:
            cmd += ' | tar -xz'
        run(cmd)
        if env.curl_postinstall_script:
            output = show if env.curl_postinstall_output else hide
            with output('output'):
                run(env.curl_postinstall_script)
