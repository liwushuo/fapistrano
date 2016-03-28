# Fapistrano

A remote server automation and deployment tool.

* Document: [http://pythonhosted.org/fapistrano/](http://pythonhosted.org/fapistrano/)

## Install

``` bash
pip install fapistrano
```

To upgrade

``` bash
pip install -U fapistrano
```

## How to Use

```
$ fap release --stage production --role web
$ fap rollback --stage production --role web
$ fap restart --stage production --role web
```
