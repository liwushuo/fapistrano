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

`fap restart`
-------------

This command is designed to restart you application.

* Restart
    * Default behavious is blank.
