# -*- coding: utf-8 -*-

from blinker import signal
from fabric.api import cd, env, run, local, task
from fabric.contrib.files import exists
from ..utils import green_alert, red_alert

def init():
    if not hasattr(env, 'git_use_reset'):
        env.git_use_reset = False

    if not hasattr(env, 'sed_bsd'):
        env.sed_bsd = True

    signal('deploy.delta.publishing').connect(publish_git_delta)
    signal('deploy.head.publishing').connect(publish_git_head)
    signal('deploy.reverted').connect(log_reverted_revision)
    signal('deploy.updating').connect(update_git_repo)
    signal('deploy.publishing').connect(publish_git_repo_as_current_release)

def publish_git_delta(sender=None, **kwargs):
    delta_log = _get_delta()
    if not delta_log:
        green_alert('No delta.')
        return
    green_alert('Get delta:\n%s' % delta_log)
    signal('git.delta.publishing').send(None, head=_get_remote_head(), delta_log=delta_log)

def publish_git_head(sender=None, **kwargs):
    head = _get_remote_head()
    green_alert('Get head: \n%s' % head)
    signal('git.head.publishing').send(None, head=head)

def log_reverted_revision(sender=None, **kwargs):
    head = _get_remote_head()
    green_alert('Rollback to %s' % head)
    signal('git.reverted').send(None, head=head)

def update_git_repo(sender=None, **kwargs):
    if not exists('%(path)s/repo' % env):
        _clone_git_repo(env.repo, env.branch)

    with cd('%(path)s/repo' % env):
        delta_log = _get_delta(bsd=env.sed_bsd)

        signal('git.updating').send(None)

        if env.git_use_reset:
            run('git fetch -q')
            run('git reset --hard origin/%(branch)s' % env)
        else:
            run('git pull -q')
            run('git checkout %(branch)s' % env)

        head = _get_remote_head()
        signal('git.updated').send(None, delta_log=delta_log, head=head)

        green_alert('Release to %s' % head)

        if delta_log:
            green_alert('Release log:\n%s' % delta_log)

def publish_git_repo_as_current_release(sender=None, **kwargs):
    with cd(env.path):
        run('cp -r %(path)s/repo %(releases_path)s/_build' % env)
        with cd('%(releases_path)s/_build' % env):
            try:
                signal('git.building').send(None)
                signal('git.built').send(None)
            except SystemExit:
                red_alert('New release failed to build, Cleaning up failed build')
                run('rm -rf %(release_path)s/_build' % env)
                exit()
        with cd('%(releases_path)s' % env):
            run('mv _build %(new_release)s' % env)

def _clone_git_repo(repo, branch='master'):
    green_alert('Cloning the latest code')
    run('git clone -q --depth 1 %(repo)s %(path)s/repo' % env)

    with cd('%(path)s/repo' % env):
        green_alert('Checking out %(branch)s branch' % env)
        run('git checkout %s' % branch)

def _get_remote_head():
    with cd(env.current_path):
        return run("git rev-parse --short HEAD", quiet=True)


def _get_delta(upstream='upstream', bsd=True):
    version = _get_remote_head()
    green_alert('Current version: %s' % version)

    local('/usr/bin/env git fetch -q %s' % upstream)
    #FIXME
    return local(
        'cd /Users/soasme/space/liwushuo/nasdaq ; '
        '/usr/bin/env git log --reverse --pretty="%%h %%s: %%b" --merges %s..%s/master | '
        '/usr/bin/env sed -%s "s/Merge pull request #([0-9]+) from ([^/]+)\\/[^:]+/#\\1\\/\\2/"' % (
            version, upstream, 'E' if bsd else 'r'), capture=True).decode('utf8')
