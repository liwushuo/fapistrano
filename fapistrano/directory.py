# -*- coding: utf-8 -*-

import os
from fabric.api import run, env

# TODO: remove most of it, because we have better default option now.

def set_path():
    env.path = '/home/%(user)s/www/%(project_name)s' % env

def get_path():
    if not hasattr(env, 'path'):
        set_path()
    return env.path

def set_releases_path():
    env.releases_path = '%s/releases' % get_path()

def get_releases_path():
    if not hasattr(env, 'releases_path'):
        set_releases_path()
    return env.releases_path

def set_shared_path():
    env.shared_path = '%s/shared' % get_path()

def get_shared_path():
    if not hasattr(env, 'shared_path'):
        set_shared_path()
    return env.shared_path

def set_current_path():
    env.current_path = '%s/current' % get_path()

def get_current_path():
    if not hasattr(env, 'current_path'):
        set_current_path()
    return env.current_path

def _get_all_releases():
    return sorted(run('ls -x %(releases_path)s' % env).split())

def set_all_releases():
    env.releases = _get_all_releases()

def get_all_releases():
    if not hasattr(env, 'releases'):
        set_all_releases()
    return env.releases

def set_current_release():
    env.current_release = run('readlink %(current_path)s' % env).rsplit('/', 1)[1]

def get_current_release():
    if not hasattr(env, 'current_release'):
        set_current_release()
    return env.current_release

def set_previous_release():
    current_index = get_all_releases().index(env.current_release)
    if current_index > 1:
        env.previous_release = env.releases[current_index-1]
    else:
        env.previous_release = None

def get_previous_release():
    if not hasattr(env, 'previous_release'):
        set_previous_release()
    return env.previous_release

def set_dirty_releases():
    all_releases = get_all_releases()
    current_release = get_current_release()
    current_index = all_releases.index(current_release)
    if len(all_releases) != current_index + 1:
        env.dirty_releases = all_releases[current_index + 1:]
    else:
        env.dirty_releases = []

def get_dirty_releases():
    if not hasattr(env, 'dirty_releases'):
        set_dirty_releases()
    return env.dirty_releases

def get_keep_releases_count():
    if not hasattr(env, 'keep_releases'):
        env.keep_releases = 5
    return env.keep_releases

def get_outdated_releases():
    all_releases = _get_all_releases()
    keep_releases_count = get_keep_releases_count()
    if len(all_releases) > keep_releases_count:
        directories = list(reversed(all_releases))
        del directories[:env.keep_releases]
        return directories
    else:
        return []

def set_linked_files():
    env.linked_files = []

def get_linked_files():
    if not hasattr(env, 'linked_files'):
        set_linked_files()
    return env.linked_files

def set_linked_dirs():
    env.linked_dirs = []

def get_linked_dirs():
    if not hasattr(env, 'linked_dirs'):
        set_linked_dirs()
    return env.linked_dirs

def get_linked_file_dirs():
    linked_files = get_linked_files()
    return set(map(os.path.dirname, linked_files))

def get_linked_dir_parents():
    linked_dirs = get_linked_dirs()
    return set(map(os.path.dirname, linked_dirs))
