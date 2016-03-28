Directory
==========

Root
-----

The root path of this structure can be defined with the configuration variable `path`.

Default `path` is `/home/%(user)s/www/%(app_name)s`.

Assuming your `deploy.yml` contains this::

    user: deploy
    app_name: example

Then you project will be deployed to `/home/deploy/www/example`.

If you have special demand, you can rewrite `path` in your `deploy.yml`::

    user: deploy
    app_name: example
    path: /var/www/example

Basic Structure
---------------

The directory hierarchy on each remote host is strictly defined.
Inspecting the tree inside `path` may look like this::

    ├── current -> /home/deploy/www/example/releases/160323-164537
    ├── releases
    │   ├── 160323-164333
    │   ├── 160323-164407
    │   ├── 160323-164537
    │   │   ├── configs
    │   │   │   └── supervisor_staging_app.conf -> /home/deploy/www/example/shared/configs/supervisor_staging_app.conf
    └── shared
        ├── configs
        │   └── supervisor_staging_app.conf

Latest Releases
---------------

`releases` is a directory contains several latest deployments.

A directory naming with `%y%m%d-%H%M%S` will be created after a deployment starting.

Default path is `%(path)s/releases`.

Current Release
---------------

`current` is a symlink to latest deployment listed in `releases` directory.

This symlink is updated at the end of a successful deployment.
If the deployment fails in any step the current symlink still points to the old release.

If you are releasing a new deployment, `current` will be symlink to newly created directory.
If you are rollbacking an old deployment, `current` will be symlink to elderly existed directory.

Default symlink is `%(path)s/current`.

Shared files or directories
---------------------------

`shared` is a directory contains files and directories that will be symlinked in each release.

Default path is `%(path)s/shared`.
