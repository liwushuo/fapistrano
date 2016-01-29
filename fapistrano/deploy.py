# -*- coding: utf-8 -*-

import os
import new
from datetime import datetime
import atexit

from fabric.api import runs_once
from fabric.api import local
from fabric.api import run
from fabric.api import env
from fabric.api import cd
from fabric.api import prefix
from fabric.api import task
from fabric.api import abort
from fabric.api import parallel
from fabric.api import show, hide
from fabric.api import with_settings
from fabric.colors import green, red, white

import yaml
import requests
import json

from .utils import red_alert, green_alert, with_configs

RELEASE_PATH_FORMAT = '%y%m%d-%H%M%S'

# do not print output by default
env.show_output = False
first_setup_repo_func = None
setup_repo_func = None
slack_sendbox = []
slack_atexit = False

def first_setup_repo(f):
    global first_setup_repo_func
    first_setup_repo_func = f
    return f


def setup_repo(f):
    global setup_repo_func
    setup_repo_func = f
    return f


def _get_config():
    try:
        with open(os.path.expanduser('~/.fapistranorc')) as f:
            configs = yaml.load(f)
            return configs.get(os.getcwd(), {})
    except IOError:
        return {}


def _check_slack_sendbox(data):
    if data in slack_sendbox:
        return False
    slack_sendbox.append(data)
    return True


def _send_to_slack(payload, **kw):
    conf = _get_config()
    if 'slack_webhook' not in conf:
        return
    if isinstance(payload, basestring):
        payload = {'text': payload}
    payload.setdefault('icon_emoji', ':trollface:')
    payload.update(kw)
    data = json.dumps(payload)
    if not _check_slack_sendbox(data):
        return

    global slack_atexit
    if not slack_atexit:
        slack_atexit = True
        @atexit.register
        def send():
            for data in slack_sendbox:
                return requests.post(conf['slack_webhook'], data=data, timeout=10)


def _format_target():
    return '{app_name}-{env}'.format(**env)


def _format_link(title, href):
    return u'<%s|%s>' % (title, href)


def _format_git_commit(commit):
    conf = _get_config()
    git_web = conf.get('git_web')
    if not git_web:
        return commit
    return u'<%s%s|%s>' % (git_web, commit, commit)


def _format_git_richlog(text):
    if not text:
        return

    conf = _get_config()
    git_web = conf.get('git_web')
    if not git_web:
        return
    commits = []

    for line in text.splitlines():
        commit_hash, commit_log = line.split(' ', 1)
        commits.append(u'<{git_web}{commit_hash}|{commit_hash}> {commit_log}'.format(**locals()))
    return {
        'value': u'\n'.join(commits) if commits else 'No commit.'
    }


def _format_delta_payload(delta_log):
    notes = '[%s] Please check if the commits are ready to deploy.' % _format_target()
    return _format_common_gitlog_payload(delta_log, notes, '#aaccaa')


def _format_release_payload(delta_log):
    notes = '[%s] Deploy to %s. Please check if it works properly.' % (
        _format_target(), _format_git_commit(_get_remote_head())
    )
    return _format_common_gitlog_payload(delta_log, notes)


def _format_common_gitlog_payload(gitlog, notes, color='#D00000'):
    text = u'```%s```\n%s' % (gitlog if gitlog else 'No commit.', notes)

    richlog = _format_git_richlog(gitlog)
    if not richlog:
        payload = { 'text': text }
    else:
        payload = {
            'attachments': [
                {
                    'fallback': text,
                    'color': color,
                    'fields': [
                        richlog,
                        {
                            'title': 'Notes',
                            'value': notes
                        },
                    ],
                },
            ]
        }

    return payload


def _get_remote_head():
    with cd(env.current_path):
        return run("git rev-parse --short HEAD", quiet=True)


def _get_delta(upstream='upstream', bsd=True):
    version = _get_remote_head()

    local('git fetch -q %s' % upstream)
    return local('git log --reverse --pretty="%%h %%s: %%b" --merges %s..%s/master | '
                 'sed -%s "s/Merge pull request #([0-9]+) from ([^/]+)\\/[^:]+/#\\1\\/\\2/"' % (
                     version, upstream, 'E' if bsd else 'r'), capture=True).decode('utf8')


@task
@runs_once
@with_configs
def head(slack_channel=None):
    green_alert('[%s] Current head: %s' % (_format_target(), _get_remote_head()))
    if slack_channel:
        _send_to_slack(
            '[%s] Current head: %s' % (_format_target(), _format_git_commit(_get_remote_head())),
            channel=slack_channel
        )


@task
@runs_once
@with_configs
def delta(upstream='upstream', bsd=True, slack_channel=None):
    delta_log = _get_delta(upstream, bsd)

    if not delta_log:
        green_alert('No delta.')
        return

    green_alert('Get delta:\n%s' % delta_log)

    if slack_channel:
        _send_to_slack(_format_delta_payload(delta_log), channel=slack_channel)


@task
@with_configs
def restart(refresh_supervisor=False, wait_before_refreshing=False, slack_channel=None):
    with show('output'):
        if not refresh_supervisor:
            run('supervisorctl restart %(supervisor_target)s' % env)
        else:
            run('supervisorctl stop %(supervisor_target)s' % env)
            if wait_before_refreshing:
                raw_input('type any key to refresh supervisor')
            run('supervisorctl reread')
            if not run('supervisorctl update'):
                run('supervisorctl start %(supervisor_target)s' % env)

        run('supervisorctl status %(supervisor_target)s' % env)

    # FIXME: get the status of the service

    green_alert('Service restarted at %s' % _get_remote_head())
    if slack_channel:
        _send_to_slack(
            '[%s] Restart at %s' % (_format_target(), _format_git_commit(_get_remote_head())),
            channel=slack_channel
        )


@task
def _releases():
    env.releases = sorted(run('ls -x %(releases_path)s' % env).split())
    env.current_release = run('readlink %(current_path)s' % env).rsplit('/', 1)[1]

    current_index = env.releases.index(env.current_release)
    if current_index > 1:
        env.previous_release = env.releases[current_index-1]
    if len(env.releases) != current_index + 1:
        env.dirty_releases = env.releases[current_index+1:]
    env.new_release = datetime.now().strftime(RELEASE_PATH_FORMAT)


@task
@with_configs
def cleanup_failed():
    green_alert('Cleanning up failed build')

    with cd(env.releases_path):
        run('rm -rf _build')


@task
@with_configs
def cleanup():
    green_alert('Cleanning up old release(s)')
    if not env.has_key('releases'):
        _releases()

    if len(env.releases) > env.keep_releases:
        directories = env.releases
        directories.reverse()
        del directories[:env.keep_releases]
        with cd(env.releases_path):
            run('rm -rf %s' % ' '.join(directories))


@task
@with_configs
def setup(branch=None):
    if branch:
        env.branch = branch

    green_alert('Creating project path')
    run('mkdir -p %(path)s/{releases,shared/log}' % env)

    # change permission
    run('find %(path)s -type d -exec chmod 755 {} \;' % env)
    run('find %(path)s -type f -exec chmod 644 {} \;' % env)
    run('chmod -R g+w %(shared_path)s' % env)

    # clone code
    with cd(env.releases_path):
        green_alert('Cloning the latest code')
        env.new_release = datetime.now().strftime(RELEASE_PATH_FORMAT)
        run('git clone -q --depth 1 %(repo)s _build' % env)

    with cd('%(releases_path)s/_build' % env):
        green_alert('Checking out %(branch)s branch' % env)
        run('git checkout %(branch)s' % env)

        if callable(first_setup_repo_func):
            green_alert('Setting up repo')
            first_setup_repo_func()

    # symlink
    with cd(env.releases_path):
        run('mv _build %(new_release)s' % env)
    with cd(env.path):
        run('ln -nfs %(releases_path)s/%(new_release)s current' % env)

        # link supervisorctl and run
        run('ln -nfs %(current_path)s/configs/supervisor_%(env)s_%(role)s.conf '
            '/etc/supervisor/conf.d/%(project_name)s.conf' % env)
        run('supervisorctl reread')
        run('supervisorctl update')
        run('supervisorctl status')


@task
@with_configs
def release(branch=None, refresh_supervisor=False, use_reset=False, bsd=True, slack_channel=None):
    if branch:
        env.branch = branch

    delta_log = _get_delta(branch or 'upstream', bsd)

    if delta_log:
        green_alert('Deploying new release on %(branch)s branch' % env)

        # get releases
        _releases()

        green_alert('Creating the build path')
        with cd(env.releases_path):
            run('cp -rp %(current_release)s _build' % env)

        try:
            # update code and environments
            with cd('%(releases_path)s/_build' % env):
                green_alert('Checking out latest code')
                if use_reset:
                    run('git fetch -q')
                    run('git reset --hard origin/%(branch)s' % env)
                else:
                    run('git pull -q')
                    run('git checkout %(branch)s' % env)

                if callable(setup_repo_func):
                    # setup repo
                    green_alert('Setting up repo')
                    setup_repo_func()

        except SystemExit:
            red_alert('New release failed to build')
            cleanup_failed()
            exit()

        green_alert('Symlinking to current')
        with cd(env.releases_path):
            run('mv _build %(new_release)s' % env)
        with cd(env.path):
            run('ln -nfs %(releases_path)s/%(new_release)s current' % env)
        green_alert('Done. Deployed %(new_release)s on %(branch)s' % env)

    green_alert('Launching')
    restart(refresh_supervisor)

    cleanup()

    green_alert('Release to %s' % _get_remote_head())
    if delta_log:
        green_alert('Release log:\n%s' % delta_log)

    if slack_channel:
        _send_to_slack(_format_release_payload(delta_log), channel=slack_channel)

    # TODO: do rollback when restart failed

@task
@with_configs
def resetup_repo():
    with cd('%(current_path)s' % env):
        green_alert('Setting up repo')
        setup_repo_func()

@task
@with_configs
def rollback(slack_channel=None):
    green_alert('Rolling back to last release')
    _releases()

    if not env.has_key('previous_release'):
        abort('No release to rollback')

    env.rollback_from = env.current_release
    env.rollback_to = env.previous_release

    with cd(env.path):
        run('ln -nfs %(releases_path)s/%(rollback_to)s current' % env)
        restart()
        run('rm -rf %(releases_path)s/%(rollback_from)s' % env)

    green_alert('Rollback to %s' % _get_remote_head())
    if slack_channel:
        _send_to_slack(
            '[%s] Rollback to %s' % (_format_target(), _format_git_commit(_get_remote_head())),
            channel=slack_channel
        )


@task
def debug_output():
    env.show_output = True

@task
@with_configs
@runs_once
def debug_env():
    from pprint import pprint
    pprint(env)
