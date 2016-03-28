Installation
============

Fapistrano is best installed via pip (highly recommended) or easy_install.

e.g.::

    $ pip install fapistrano

Or, to install a developing version for debugging or hacking, you may want to use pip editable instalation::

    $ pip install -e git+git@github.com:liwushuo/fapistrano.git#egg=fapistrano


If you don't want to pollute your global Python environment, you can use virtualenvwrapper
to create a virtualenv envrionment and install fapistrano inside it::

    $ mkvirtualenv ops
    (ops) $ pip install fapistrano


Config File
-----------

You have to tell fapistrano where to deploy and what to deploy. Thus, you must put
a YAML config `deploy.yml` in your working directory to let fapistrano know basic
information. You can also specify YAML config as command line option. We will explain
it later.

NOTICE: All configuration items available for `fabric.api.env` are Fapistrano configuration
items as well.

SSH
----

Fapistrano deploys using SSH. Thus, you must be able to SSH (ideally with keys and
ssh-agent) from the deployment system to the destination system for Fapistrano to work.

Basically, you can add `user`, `use_ssh_config` and `hosts` configuration items to
your YAML config.

If you are still struggling to get login working, try the Fabric docs.
