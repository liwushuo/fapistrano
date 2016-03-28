Plugin
======

This section talks about installing, loading and writing third party plugins.

Installing Plugins
------------------

Installing a third party plugin can be easily done with pip::

    $ pip install fapistrano-PLUGIN

Loading Plugins
---------------

In your `deploy.yml`, append plugin name to configuration item `plugins`::

    plugins:
      - fapistrano.git
      - fapistrano.virtualenv

Normally, plugins have their own configurations.
Don't forget configure these configurations before running `fap` command.

You can set plugin configurations globally, or custmozie for each Stage-Role, or even
on each cli running.

Tracing Plugins(TODO)
----------------------

If you want to find out a complete function call sequence during deploying applicaiton,
you can find out the answer by typing::

    $ fap release -s production --dry-run

Deactivating Plugins(TODO)
--------------------------

TODO

You can prevent plugins from loading them::

    fap release -s staging --no-plugins fapistrano.git

This means that any subsequent try to activate/load the named plugin will not work.


Writing Plugins
---------------

It's easy to implement plugins for your own vanilla project or pip installable plugins that
can be used throughout many projects.

A plugin contains an `init` function.

Normally plugin register default configurations and signal handlers at `init` function.
A plugin is recommended to use it's name as prefix in configuration definition. Here is
a hello-world example::


    # fapistrano_echo.py
    import click
    from fapistrano import signal, configuration, env

    def init():
        configuration.setdefault('echo_message', 'Hello World')
        signal.register('deploy.finished', echo_message)

    def echo_message(**kwargs):
        click.secho(env.echo_message, fg='green')



Default Plugins
---------------

Fapistrano internally bootstrap several plugins:

* `fapistrano.curl`: dowloading a file into release directory on updating release.
* `fapistrano.git`: using git as a scm tool to update files on updateing release.
* `fapistrano.localshared`: copy some files from one place at your server to shared directory before starting release.
* `fapistrano.supervisorctl`: restart your application on release published.
* `fapistrano.virtualenv`: using virtualenv to create python environment on updating release.
* `fapistrano.virtualenvwrapper`: using virtualenvwrapper to create python environment on updating release.
