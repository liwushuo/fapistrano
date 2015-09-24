# Fapistrano

## Install

``` bash
sudo pip install git+ssh://git@ghe.liwushuo.com/ops/fapistrano.git@v0.1.0#egg=fapistrano-0.1.0
```

## How to Use

Available tasks

```
fab deploy.setup
fab deploy.delta
fab deploy.release
fab deploy.rollback
fab deploy.debug_env
```

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


## Implemetion Details

- the build folder is `releases/_build` during deployment
- role/env info is stored in `env.role`/`env.env`
