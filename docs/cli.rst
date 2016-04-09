Command-Line Tool
=================

Fapistrano offers a default command-line tool: `fap`::

    $ fap --help
    Usage: fap [OPTIONS] COMMAND [ARGS]...

    Options:
      -d, --deployfile TEXT
      --help                 Show this message and exit.

    Commands:
      release
      restart
      rollback
      once
      shell

global options
---------------

* set `--dry-run=true` to debug the workflow but no task's really ran.

`fap release`
-------------

This command is designed to ship new deployments to you server.

It do pretter little things:

* Start
    * Create a new release directory under `releases_path`;
    * Create link files/directories in release directory, symlinking them to files/directories to `shared_path`;
* Update
    * Default behaviour is blank;
* Publish
    * Switch current release defined by `current_path` to newly created release directory;
* Finish
    * Remove stale releases, according the number defined by `keep_releases`.

Example::

    [server01] Executing task 'deploy.release'
    ===> Starting
    [server01] run: mkdir -p /home/deploy/www/example/{releases,shared/log}
    [server01] run: chmod -R g+w /home/deploy/www/example/shared
    [server01] run: mkdir -p /home/deploy/www/example/releases/160314-085322
    ===> Started
    ===> Updating
    ===> Updated
    ===> Publishing
    [server01] run: ln -nfs /home/deploy/www/example/releases/160314-085322 current
    ===> Published
    ===> Finishing
    ===> Cleanning up old release(s)
    [server01] run: ls -x /home/deploy/www/example/releases
    [server01] run: rm -rf 160313-230707
    ===> Finished
    Done.
    Disconnecting from server:2333... done.

`fap rollback`
--------------

This command is designed to rollback to previously deployed release.

* Start
    * Check if there is a rollback release, which is deployed before current release;
    * Define:
        * `rollback_from`: current_release;
        * `rollback_to`: release that is deployed previous than current release;
* Update
    * Default behaviour is blank;
* Publish
    * Switch current release defined by `current_path` to `rollback_to`;
* Finish
    * Remove `rollback_from` release.


Example::

    [server01] Executing task 'deploy.release'
    ===> Starting
    [server01] run: mkdir -p /home/deploy/www/example/{releases,shared/log}
    [server01] run: chmod -R g+w /home/deploy/www/example/shared
    ===> Started
    ===> Updating
    ===> Updated
    ===> Publishing
    [server01] run: ln -nfs /home/deploy/www/example/releases/160314-083000 current
    ===> Published
    ===> Finishing
    ===> Cleanning up old release(s)
    [server01] run: rm -rf 160314-085322
    ===> Finished
    Done.
    Disconnecting from server:2333... done.

`fap restart`
-------------

This command is designed to restart your application.

* Restart
    * Default behavious is blank.

Example::

    [server01] Executing task 'deploy.release'
    ===> Restarting
    ===> Restarted
    Done.
    Disconnecting from server:2333... done.

`fap shell`
-----------

This command is designed to start a REPL for your application.

Both `--stage` and `--role` are required.

NOTICE: currently only Python support::

    $ fap shell --stage staging --role app
    Executing app at staging
    [server01] Executing task 'shell'
    [server01] run: venv/bin/ipython
    [server01] out: Python 2.7.10 (default, Jun 30 2015, 15:30:23)
    [server01] out: Type "copyright", "credits" or "license" for more information.
    [server01] out:
    [server01] out: IPython 4.1.2 -- An enhanced Interactive Python.
    [server01] out: ?         -> Introduction and overview of IPython's features.
    [server01] out: %quickref -> Quick reference.
    [server01] out: help      -> Python's own help system.
    [server01] out: object?   -> Details about 'object', use 'object??' for extra details.
    [server01] out:
    [server01] out: In [1]: import os; print os.environ.get('ENV')
    [server01] out: stag
    [server01] out:
    [server01] out: In [2]: exit
    [server01] out:

`fap once`
----------

This command is designed to run script for your application.

Both `--stage` and `--role` are required.

`fap once` needs additionaly option `--command`::

    $ fap once --stage staging --role app --command='which scrapy'
    Executing app at staging
    [app-stag01] Executing task 'once'
    ===> Running
    [app-stag01] run: which scrapy
    [app-stag01] out: venv/bin/scrapy
    [app-stag01] out:

    ===> Ran
