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

This command is designed to restart you application.

* Restart
    * Default behavious is blank.

Example::

    [server01] Executing task 'deploy.release'
    ===> Restarting
    ===> Restarted
    Done.
    Disconnecting from server:2333... done.
