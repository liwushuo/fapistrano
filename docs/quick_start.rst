Quick Start
============

Once installed, Fapistrano bootstraps a `fap` command to complete release/rollback/restart task.

First Run
---------

Add a file named `deploy.yml`::

    project_name: smallest-example
    app_name: smallest-example
    user: deploy
    use_ssh_config: true

    stage_role_configs:
      staging:
        app:
          hosts:
            - app-stag01

After Runing command below, Fapistrano will create a smallest example on your host::

    $ fap release --stage staging --role app
    [app-stag01] Executing task 'release'
    ===> Starting
    [app-stag01] run: mkdir -p /home/deploy/www/smallest-example/{releases,shared/log}
    [app-stag01] run: chmod -R g+w /home/deploy/www/smallest-example/shared
    [app-stag01] run: mkdir -p /home/deploy/www/smallest-example/releases/160328-162832
    ===> Started
    ===> Updating
    ===> Updated
    ===> Publishing
    [app-stag01] run: ln -nfs /home/deploy/www/smallest-example/releases/160328-162832 /home/deploy/www/smallest-example/current
    ===> Published
    ===> Finishing
    [app-stag01] run: ls -x /home/deploy/www/smallest-example/releases
    ===> Finished

For now, it does nothing but leaving a blank directory hierachy to you::

    $ ssh deploy@app-stag01 tree /home/deploy/www/smallest-example/
    /home/deploy/www/smallest-example/
    ├── current -> /home/deploy/www/smallest-example/releases/160328-162832
    ├── releases
    │   └── 160328-162832
    └── shared
        └── log

    5 directories, 0 files

Using Git
---------

Git is a popular scm tool. Fapistrano integrated git as a plugin.
You need to declare loading `fapistrano.git` and specify repository in `deploy.yml`::

     project_name: git-example
     app_name: git-example
     user: deploy
     use_ssh_config: true

     stage_role_configs:
       staging:
         app:
           hosts:
             - app-stag01

     plugins:
       - fapistrano.plugins.git

     repo: git@github.com:octocat/Hello-World.git
     branch: master

By Executing release flow, Fapistrano clones remote git repo and export code in
`master` branch to release directory::

    $ fap release --stage staging --role app
    [app-stag01] Executing task 'release'
    ===> Starting
    [app-stag01] run: mkdir -p /home/deploy/www/git-example/{releases,shared/log}
    [app-stag01] run: chmod -R g+w /home/deploy/www/git-example/shared
    [app-stag01] run: mkdir -p /home/deploy/www/git-example/releases/160328-163937
    ===> Started
    [app-stag01] run: git clone --mirror --depth 1 --no-single-branch git@github.com:octocat/Hello-World.git /home/deploy/www/git-example/repo
    [app-stag01] run: git ls-remote --heads git@github.com:octocat/Hello-World.git
    ===> Updating
    [app-stag01] run: git fetch --depth 1 origin master
    [app-stag01] run: git rev-list --max-count=1 --abbrev-commit --abbrev=12 master
    [app-stag01] run: git archive master | tar -x -f - -C /home/deploy/www/git-example/releases/160328-163937/
    [app-stag01] run: echo 7fd1a60b01f9 >> REVISION
    ===> Updated
    ===> Publishing
    [app-stag01] run: ln -nfs /home/deploy/www/git-example/releases/160328-163937 /home/deploy/www/git-example/current
    ===> Published
    ===> Finishing
    [app-stag01] run: ls -x /home/deploy/www/git-example/releases
    ===> Finished

Now we have added a `repo` directory and updated out release directory::

    % ssh deploy@lws-stag01 tree /home/deploy/www/git-example
    /home/deploy/www/git-example
    ├── current -> /home/deploy/www/git-example/releases/160328-163937
    ├── releases
    │   └── 160328-163937
    │       ├── README
    │       └── REVISION
    ├── repo
    │   ├── branches
    │   ├── config
    │   ├── description
    │   ├── FETCH_HEAD
    │   ├── HEAD
    │   ├── hooks
    │   │   ├── applypatch-msg.sample
    │   │   ├── commit-msg.sample
    │   │   ├── post-update.sample
    │   │   ├── pre-applypatch.sample
    │   │   ├── pre-commit.sample
    │   │   ├── prepare-commit-msg.sample
    │   │   ├── pre-push.sample
    │   │   ├── pre-rebase.sample
    │   │   └── update.sample
    │   ├── info
    │   │   └── exclude
    │   ├── objects
    │   │   ├── info
    │   │   └── pack
    │   │       ├── pack-c8b9cbbd14e791b8beddf1033f5b4357d4f179da.idx
    │   │       └── pack-c8b9cbbd14e791b8beddf1033f5b4357d4f179da.pack
    │   ├── packed-refs
    │   ├── refs
    │   │   ├── heads
    │   │   └── tags
    │   └── shallow
    └── shared
        └── log


Using Supervisor
----------------

A static git repository updating is trivial.
Let's get a little bit more complicated now.

We are going to define `deploy.yml` for a flask hello-world application::

    project_name: supervisor-example
    app_name: supervisor-example
    user: deploy
    use_ssh_config: true

    stage_role_configs:
      staging:
        app:
          hosts:
            - app-stag01

    plugins:
      - fapistrano.plugins.git
      - fapistrano.plugins.virtualenv
      - fapistrano.plugins.supervisorctl

    repo: git@github.com:liwushuo/fapistrano.git
    git_archive_tree: examples/supervisor-example

    supervisor_check_status: true
    supervisor_conf: configs/supervisor_%(stage)s_%(role)s.conf

Then we add `configs/supervisor_staging_app.conf` to the repository::

    [program:supervisor-example]
    command=python app.py
    directory=/home/deploy/www/%(program_name)s/current
    environment=PATH="/home/deploy/www/%(program_name)s/current/venv/bin",FLASK_ENV="stag"
    numprocs=1
    user=deploy
    autostart=true
    autorestart=true
    redirect_stderr=true
    stdout_logfile=/var/log/supervisor/%(program_name)s-web.log
    stdout_logfile_maxbytes=100MB
    stdout_logfile_backups=10

Finally, Run with option `--supervisor-refresh=true`, since we first
registered our supervisor config to supervisord. In the next release,
there is no need to add option `--supervisor-refresh=true` unless
supervisor config file modified.::

    [app-stag01] Executing task 'release'
    ===> Starting
    [app-stag01] run: mkdir -p /home/deploy/www/supervisor-example/{releases,shared/log}
    [app-stag01] run: chmod -R g+w /home/deploy/www/supervisor-example/shared
    [app-stag01] run: mkdir -p /home/deploy/www/supervisor-example/releases/160328-173812
    ===> Started
    [app-stag01] run: git clone --mirror --depth 1 --no-single-branch git@github.com:liwushuo/fapistrano.git /home/deploy/www/supervisor-example/repo
    [app-stag01] run: git ls-remote --heads git@github.com:liwushuo/fapistrano.git
    [app-stag01] run: ln -nfs /home/deploy/www/supervisor-example/current/configs/supervisor_staging_app.conf /etc/supervisor/conf.d/supervisor-example.conf
    ===> Updating
    [app-stag01] run: git fetch --depth 1 origin master
    [app-stag01] run: git rev-list --max-count=1 --abbrev-commit --abbrev=12 master
    [app-stag01] run: git archive master examples/supervisor-example | tar -x --strip-components 2 -f - -C /home/deploy/www/supervisor-example/releases/160328-173812/
    [app-stag01] run: echo 86ba572f3d8e >> REVISION
    ===> Updated
    [app-stag01] run: /usr/bin/env virtualenv /home/deploy/www/supervisor-example/releases/160328-173812/venv
    [app-stag01] run: pip install -U pip setuptools wheel
    [app-stag01] run: pip install -r /home/deploy/www/supervisor-example/releases/160328-173812/requirements.txt
    ===> Publishing
    [app-stag01] run: ln -nfs /home/deploy/www/supervisor-example/releases/160328-173812 /home/deploy/www/supervisor-example/current
    ===> Published
    [app-stag01] run: supervisorctl stop supervisor-example
    [app-stag01] run: supervisorctl reread
    [app-stag01] run: supervisorctl update
    [app-stag01] run: supervisorctl start supervisor-example
    [app-stag01] run: supervisorctl status supervisor-example
    [app-stag01] out: supervisor-example               RUNNING    pid 13014, uptime 0:00:02
    [app-stag01] out:

    ===> Finishing
    [app-stag01] run: ls -x /home/deploy/www/supervisor-example/releases
    [app-stag01] run: rm -rf 160328-173248
    ===> Finished

Now, our flask application is running!::

    $ ssh deploy@app-stag01 curl -s http://0.0.0.0:5000
    hello world

Rollback!
---------

Rollback is easily by replacing `release` to `rollback`.

After releasing again, our release are now at 160328-175016.

let's trigger a rollback flow.::

    $ fap rollback --stage staging --role app
    staging app
    [app-stag01] Executing task 'rollback'
    ===> Starting
    [app-stag01] run: readlink /home/deploy/www/supervisor-example/current
    [app-stag01] run: ls -x /home/deploy/www/supervisor-example/releases
    ===> Started
    [app-stag01] run: git ls-remote --heads git@github.com:liwushuo/fapistrano.git
    [app-stag01] run: ln -nfs /home/deploy/www/supervisor-example/current/configs/supervisor_staging_app.conf /etc/supervisor/conf.d/supervisor-example.conf
    ===> Reverting
    ===> Reverted
    ===> Publishing
    [app-stag01] run: ln -nfs /home/deploy/www/supervisor-example/releases/160328-173812 /home/deploy/www/supervisor-example/current
    ===> Published
    [app-stag01] run: supervisorctl restart supervisor-example
    [app-stag01] run: supervisorctl status supervisor-example
    [app-stag01] out: supervisor-example               RUNNING    pid 15272, uptime 0:00:02
    [app-stag01] out:

    ===> Finishing rollback
    [app-stag01] run: rm -rf /home/deploy/www/supervisor-example/releases/160328-175016
    ===> Finished

This command help us rollback our current release back to `160328-173812`, which is deployed
in last example.

Using with Beeper
-----------------

Beeper is a tool bundling virtualenv.py, wheels and our project as a tar file.
With the help of Jenkins, we can build a beeper tgz file before release.

We can use a curl plugin to update our application::


    project_name: curl-example
    app_name: curl-example
    user: deploy
    use_ssh_config: true
    stage_role_configs:
      staging:
        app:
          hosts:
            - app-stag01
    plugins:
      - fapistrano.plugins.curl
      - fapistrano.plugins.supervisorctl

    curl_extract_tar: true
    curl_postinstall_script: "sh ./install.sh"

    supervisor_check_status: true

When running `fap release`, we can attach option `--curl-url`. Assuming you are
using Jenkins to build your application and have authority to fetch artifact::

    $ fap release -s staging -r app --curl-url=http://ci.your-corp.com/view/Server/job/server.builder.curl-example/lastSuccessfulBuild/artifact/dist/curl-example-0f2da63.tar --curl-options="--user $JENKINS_USERNAME:$JENKINS_TOKEN"


Using with Jar
--------------

If there is a Java application to deploy, it's recommend to build it to a Jar file.
You can integrate `fapistrano.plugins.curl` to deploy jar.::

    project_name: jar-example
    app_name: jar-example
    user: deploy
    use_ssh_config: true
    stage_role_configs:
      staging:
        app:
          hosts:
            - app-stag01
    plugins:
      - fapistrano.plugins.localshared
      - fapistrano.plugins.curl
      - fapistrano.plugins.supervisorctl

    # supervisor conf
    supervisor_refresh: false
    supervisor_output: false
    supervisor_check_status: true

    # curl conf
    curl_output: 'bayarea.jar'
