=======
History
=======

0.9.2 (2017-03-20)
------------------

* fix contaminated outdated releases.

0.9.1 (2016-9-18)
------------------

* fix stale releases left on servers.

0.9.0 (2016-4-21)
------------------

* support different login user and sudo user.

0.8.3 (2016-4-18)
------------------

* fix missing output from curl.
* fix .env format.
* support formatted env for list/dict.

0.8.2 (2016-4-9)
------------------

* add `--dry-run` option.

0.8.1 (2016-4-1)
------------------

* hide curl password.

0.8.0 (2016-3-30)
------------------

* add command `once`.
* add command `shell` (only support python now).
* find plugins for each command if possible, fallback to default plugin.
* add `.env` file at remote.

0.7.3 (2016-3-29)
------------------

* bugfix for cross env pollution.

0.7.2 (2016-3-29)
------------------

* cli support group deploy by role or stage.
* add option `--curl-extract-tgz`.
* add option `--git-archive-tree`.

0.7.1 (2016-3-25)
------------------

* fix fis option.
* add option `--shared_writable`.
* alert on missing localshared files.
* add option `--curl-postinstall-output`.
* add option `--curl-output`.

0.7.0 (2016-3-21)
------------------

* release to pypi.

0.6.0 (2016-3-15)
------------------

* move git, supervisor, slack as plugins.
* put git bare repo on path.
* add fis plugin.
* add `fap` cli.
* use signal to refactor release/rollback flow.
* add curl plugin.
* add supervisor plugin.

0.5.1 (2015-2-1)
------------------

* support supervisor group
* slack notification.

0.1.0 (2015-9-23)
------------------

* First release.
