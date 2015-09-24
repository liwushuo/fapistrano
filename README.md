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

## Implemetion Details

- the build folder is `releases/_build` during deployment
- role/env info is stored in `env.role`/`env.env`
