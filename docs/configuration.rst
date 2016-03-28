Configuration
=============

Deployfile Searching Strategy
-----------------------------

Here is the algorithm which Fapistrano find deployfile:

* Read system environment variable `FAP_APP` and then find deployfile by reading another system environment varialble `%(FAP_APP)s_DEPLOYFILE`, `EXAMPLE_DEPLOYFILE` in the assuming case::

    $ export FAP_APP=EXAMPLE
    $ export EXAMPLE_DEPLOYFILE=/path/to/example/deploy.yml
    $ fap release -s production

* If `FAP_APP` does not exist, Fapistrano will try to load deployfile by `--deployfile` / `-d` option::

    $ fap --deployfile /path/to/example/deploy.yml release -s production

* If both two variables listed above are missing, Fapistrano will try to load default deployfile `deploy.yml` in current workong dir::

    $ ls
    deploy.yml
    $ fap release -s production

Configuration Loading Strategy
------------------------------

Here is the algorithm which Fapistrano load configuration items:

* Read command line options, with key turning `-` into `_`.  NOTICE: key must exists in fabric env, Fapistrano default env or deploy.yml::

    $ fap release -s production --current-release=/var/www/example

* Read Configs defined in `stage_role_configs`. In below case, Fapistrano will use path defined in `stage_role_configs/stage/app/current_release`::

    $ tail -n5 deploy.yml
    stage_role_configs:
      stage:
        app:
          current_release: /var/www/example-staging
    current_release: /var/www/example-production
    $ fap release -s stage

* Read Configs defined in `deploy.yml` not not in `stage_role_configs`.::

    $ tail -n5 deploy.yml
    stage_role_configs:
      stage:
        app:
          current_release: /var/www/example-staging
      production:
        app:
    current_release: /var/www/example-production
    $ fap release -s production


Value Formatting
----------------

All configuration item values can be defined in Python string template format with a
keyword inside.

For instance, you have an `app_name` variable and a `path` variable defined like this::

    app_name: example
    path: /var/www/%(app_name)s

Variable `path` will be formatted to `/var/www/example` before running task.

NOTICE: Currently only string value are supported.

Configuration Items
-------------------

The following variables are used for fabric:

* `user`
* `hosts`

The following variables are used for Fapistrano:

* `project_name`
* `app_name`
* `path`
* `current_path`
* `releases_path`
* `shared_path`
* `new_release`
* `release_path`,
* `linked_files`, list, default [].
* `linked_dirs`, list, default [].
* `stage_role_configs`, dict.
* `keep_releases`, integer, default 5.

Additional configurations are defined by Fapistrano plugins.
