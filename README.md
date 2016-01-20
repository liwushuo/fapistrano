# Fapistrano

## Install

``` bash
pip install fapistrano
```

To upgrade

``` bash
pip install -U fapistrano
```

## How to Use

Available tasks

```
fab deploy.setup:branch=master
fab deploy.delta
fab deploy.release:branch=master,refresh_supervisor=0,use_reset=0
fab deploy.rollback
fab deploy.resetup_repo deploy.restart
fab deploy.debug_env
fab deploy.debug_output deploy.release
```

Refer to [fabfile_example.py](https://ghe.liwushuo.com/ops/fapistrano/blob/master/fabfile_example.py) for more details

## Example Workflow

first time setup

```
fab staging app deploy.setup
```

deployments

```
fab staging app deploy.delta    # view diff
fab staging app deploy.release
fab staging app deploy.rollback # if error
```

## Slack integration

config ~/.fapistranorc in yaml.

```
/Users/someone/workspace/someproject:
  slack_webhook: https://hooks.slack.com/services/somehook
  git_web: https://github.com/someone/someproject/commit/ # for clickable commit hash
```

commands example:
```
fab staging app deploy.delta:slack_channel=#channel
fab staging app deploy.release:slack_channel=@someone
```


## Implemetion Details

- the build folder is `releases/_build` during deployment
- role/env info is stored in `env.role`/`env.env`
