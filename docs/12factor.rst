12 Factor
=========

Fapistrano is not a silver-bullet, you can possibly mess up deployment process on wrongly
configuring you application.

Following the guideline of `The Twelve-Factor App` may reduce potential traps.

Codebase
---------

One codebase tracked in revision control, many deploys.

Fapistrano archive that goal by configurating item `stage_role_configs`.
Each stage can connected with several roles.

For instance, an application is deployed to production but with several instance below.
Codebase is `git@git.your-corp.com:owner/repo.git`. Deployment instances are `production + web`,
`production + worker`, `production + cron`. These instances are running on different path
on different servers, sharing different config.::

    plugins:
      - fapistrano.git
      - fapistrano.supervisorctl
    repo: git@git.your-corp.com:owner/repo.git
    stage_role_configs:
      production:
        web:
          hosts:
            - app-web01
            - app-web02
          linked_files:
            - configs/supervisor_production_web.conf
        worker:
          hosts:
            - app-job01
          linked_files:
            - configs/supervisor_production_worker.conf
        cron:
          hosts:
            - app-job01
          linked_files:
            - configs/supervisor_production_cron.conf


Dependencies
------------------

Explicity declare and isolate dependencies.

Fapistrano archives that goal by loading property plugin.

For example, if you loading a `fapistrnao.virtualenv` plugin, Fapistrano will create a `venv`
directory as python execution environment::

    plugins:
      - fapistrano.git
      - fapistrano.virtualenv
    stage_role_configs:
      production:
        web:
          virtualenv_requirements: '%(release_path)s/production-requirements.txt

It assumes that you have a `production-requirements.txt` in your git repository.
Once updating git repository, Fapistrano will run these commands::

    $ virtualenv venv
    $ venv/bin/pip install -r production-requirements.txt

WARNING: This is still not the recommend way to install dependencies for Python.
Fetching dependencies and compiling binaries at build stage, bundling your codebase and
wheel packages as deployment artifact may be a better practice.


Config
------------------


Store config in the environment.

DO NOT EVER COMMIT SECRETS INTO YOUR REPOSITORY.

It is recommended to save your secrets at your shared folder and then link them on deploying::

    plugins:
      - fapistrano.git
    stage_role_configs:
      production:
        web:
          linked_files:
            app/settings/production.py

Load these linked files as configurations. They won't hurt you!

Build, Release, Run
-------------------

Strictly separate build and run stages.

It's not recommended to write configs below::

    # deploy.yml
    plugins:
      - fapistrano.git
      - fapistrano_webpack

    # fapistrano_webpack.py
    def init():
        signal.register('deploy.updating', compile_static_resource)

The reason is simple: build stage is totally different from release stage and run stage.
It's not worth installing entire build infrastructure on your production servers.

We prefer converting a code repo into an executable bundle first. It turned out simpler
and faster to release your codebase to production.::

    # deploy.yml
    plugins:
      - fapistrano.curl

    curl_extract_tgz: true
    curl_postinstall_script: "./install.sh"

In the above, all you need to do is to pass a `--curl-url` option into `fap` command.
Once artifact downloaded, Fapistrano will

* Extract your final codes: python code, static resource compiled by webpack.
* Run `./install.sh` which possibly create virtualenv and install python dependencies. (virtualenv and dependencies have been put into tgz)

Processes
-------------------

Execute the app as one or more stateless processes.

Make sure your application is stateless and share-nothing.

Your application is running in a easy-to-lost directory, since release directory can
only be kept to at max number of `keep_releases`.

If your have any persist data, commit them into database or write them into shared files::

    # deploy.yml
    stage_role_configs:
      production:
        web:
          linked_files:
            - log/audio-transcoding.log
            - log/image-compress.log

NOTICE: do not write supervisor log in shared, since they are written by `root` user.

Concurrency
-------------------

Scale out via the process model

If you want to scale out your application, you can add a new host to `deploy.yml` definition::

    stage_role_configs:
      production:
        web:
          hosts:
            - app-web01

     stage_role_configs:
      production:
        web:
          hosts:
            - app-web01
            - app-web02
            - app-web03

Use your load balance infrastructure to route traffic to these applciation instance::

    upstream app_servers {
        server    app-web01:8080;
        server    app-web02:8080;
        server    app-web03:8080;
    }

    server {
        listen 80;
        server_name example.org;

        location / {
            proxy_redirect     off;
            proxy_set_header   Host             $host;
            proxy_set_header   X-Real-IP        $remote_addr;
            proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
            proxy_pass http://app_servers;
        }
    }

Disposability
-------------------

Maximize robustness with fast startup and graceful shutdown.

Starting or stoping your application should not take a long time for waiting.
Few seconds are durable.

It is recommended to rely on process manager, such as supervisor, to manage output stream,
respond to crashed processes, and handle restarts and shutdowns::

    plugins:
      - fapistrano.supervisorctl
      - fapistrano.git

    supervisor_check_status: true
    supervisor_output: true
    supervisor_refresh: false
    supervisor_conf: configs/supervisor_%(role)s.conf

Dev/Prod parity
---------------

Keep development, staging, and production as similar as possible.

A typically Fapistrano way of Dev/Prod parity is to deploy same code but
to symlink different config files.::

    stage_role_configs:
      production:
        web:
          linked_files:
            - app/settings/production.py
      staging:
        web:
          linked_files:
            - app/settings/staging.py

Admin Processes
----------------

Run admin/management tasks as one-off processes.

It is recommended to commit your one-off scripts into your repository and treat it as
a brand new release. A one-off goal may be archived by disabling supervisor pluging and
customizing running endpoint.
