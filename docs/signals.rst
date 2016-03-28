Signals
=======

Basically, Fapistrano provides 3 type of deploy flow:

1. release flow
2. rollback flow
3. restart flow

Release Flow
------------

When you trigger a release task, it emits at least 8 signals:

* `deploy.starting`
* `deploy.started`
* `deploy.updating`
* `deploy.updated`
* `deploy.publishing`
* `deploy.published`
* `deploy.finishing`
* `deploy.finished`

Rollback Flow
-------------

When you trigger a rollback task, it emits at least 8 signals:

* `deploy.starting`
* `deploy.started`
* `deploy.reverting`
* `deploy.reverted`
* `deploy.publishing`
* `deploy.published`
* `deploy.finishing_rollback`
* `deploy.finished`

Restart Flow
------------

When you tirgger a restart flow, it emits at least 2 signals:

* `deploy.restarting`
* `deploy.restarted`

You can hook this signals and write you own deploy logic.
