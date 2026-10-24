repo: celery
docs=204 claims=4553 referents=728 evidence=14516
code_verdicts: {'REFUTED': 34, 'NEI': 375, 'SUPPORTED': 387}  coverage=0.53  resolved=421

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 27 items in 7 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    DEPENDENCY       TRUE_CANDIDATE  neg=0: 1
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 5
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=0: 5
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 34 of 34):
  1. SYMBOL_EXISTS celery.worker.awesome CONTRIBUTING.rst:813-813
     tier: -
     raw: # ``celery.worker.awesome``
     cited by 2 claims
  2. PATH_EXISTS m_module.py CONTRIBUTING.rst:847-847
     tier: bare
     raw: $ isort m_module.py --diff # Do a dry-run to see the proposed changes
  3. PATH_EXISTS docs/configuration.rst CONTRIBUTING.rst:1202-1202
     tier: anchored
     raw: in :file:`docs/configuration.rst`. Also, all settings need to be added to the
     cited by 2 claims
  4. PATH_EXISTS docs/include/introduction.txt CONTRIBUTING.rst:1467-1467
     tier: anchored
     raw: :file:`docs/include/introduction.txt`
  5. PATH_EXISTS proj/proj/celery.py docs/django/first-steps-with-django.rst:37-37
     tier: unanchored
     raw: then the recommended way is to create a new `proj/proj/celery.py` module
     cited by 2 claims
  6. PATH_EXISTS proj/proj/__init__.py docs/django/first-steps-with-django.rst:48-48
     tier: unanchored
     raw: :file:`proj/proj/__init__.py`:
     cited by 2 claims
  7. SYMBOL_EXISTS celery.task.pingtask docs/internals/app-overview.rst:95-95
     tier: -
     raw: ``celery.task.PingTask``
  8. SYMBOL_EXISTS celery.messaging docs/internals/app-overview.rst:115-115
     tier: -
     raw: ``celery.messaging``
     cited by 2 claims
  9. PATH_EXISTS app.conf docs/internals/app-overview.rst:123-123
     tier: bare
     raw: ``celery.conf.*`` -> {``app.conf``}
  10. SYMBOL_EXISTS celery.utils.textindent docs/internals/app-overview.rst:140-140
     tier: -
     raw: ``.textindent`` -> ``celery.utils.textindent``
  11. SYMBOL_EXISTS celery.task.sets.taskset docs/internals/app-overview.rst:180-180
     tier: -
     raw: ``celery.task.sets.TaskSet`` (``app.TaskSet``)
  12. SYMBOL_EXISTS celery.result.tasksetresult docs/internals/app-overview.rst:182-182
     tier: -
     raw: ``celery.result.TaskSetResult`` (``app.TaskSetResult``)
  13. SYMBOL_EXISTS celery.result.baseasyncresult docs/internals/app-overview.rst:185-185
     tier: -
     raw: ``celery.result.BaseAsyncResult`` / ``celery.result.AsyncResult``
  14. SYMBOL_EXISTS celery.bin.worker.workercommand docs/internals/app-overview.rst:187-187
     tier: -
     raw: ``celery.bin.worker.WorkerCommand``
  15. SYMBOL_EXISTS celery.worker.workercontroller docs/internals/app-overview.rst:189-189
     tier: -
     raw: ``celery.worker.WorkerController``
  16. SYMBOL_EXISTS celery.worker.control.controldispatch docs/internals/app-overview.rst:193-193
     tier: -
     raw: ``celery.worker.control.ControlDispatch``
  17. SYMBOL_EXISTS celery.worker.control.registry.panel docs/internals/app-overview.rst:194-194
     tier: -
     raw: ``celery.worker.control.registry.Panel``
  18. SYMBOL_EXISTS celery.pidbox.broadcastpublisher docs/internals/app-overview.rst:195-195
     tier: -
     raw: ``celery.pidbox.BroadcastPublisher``
  19. SYMBOL_EXISTS celery.pidbox.broadcastconsumer docs/internals/app-overview.rst:196-196
     tier: -
     raw: ``celery.pidbox.BroadcastConsumer``
  20. SYMBOL_EXISTS celery.bin.events.evcommand docs/internals/app-overview.rst:199-199
     tier: -
     raw: ``celery.bin.events.EvCommand``
  21. SYMBOL_EXISTS celery.bin.amqp.amqpadmin docs/internals/app-overview.rst:209-209
     tier: -
     raw: ``celery.bin.amqp.AMQPAdmin``
  22. SYMBOL_EXISTS celery.bin.beat.beatcommand docs/internals/app-overview.rst:211-211
     tier: -
     raw: ``celery.bin.beat.BeatCommand``
  23. SYMBOL_EXISTS celery.decorators docs/internals/deprecation.rst:143-143
     tier: -
     raw: ``celery.decorators``
  24. SYMBOL_EXISTS celery.task.control docs/internals/deprecation.rst:159-159
     tier: -
     raw: ``celery.task.control``
  25. SYMBOL_EXISTS celery.task.schedules docs/internals/deprecation.rst:163-163
     tier: -
     raw: ``celery.task.schedules``
  26. SYMBOL_EXISTS celery.task.chords docs/internals/deprecation.rst:167-167
     tier: -
     raw: ``celery.task.chords``
  27. SYMBOL_EXISTS celery.app.trace.build_tracer.trace_task docs/userguide/application.rst:512-512
     tier: -
     raw: this has been unrolled into ``celery.app.trace.build_tracer.trace_task``
  28. SYMBOL_EXISTS celery.backend_cleanup docs/userguide/configuration.rst:1066-1066
     tier: -
     raw: (``celery.backend_cleanup``), assuming that ``celery beat`` is
     cited by 2 claims
  29. SYMBOL_EXISTS celery.commands docs/userguide/extending.rst:829-829
     tier: -
     raw: Celery recognizes ``celery.commands`` entry-points to install additional
     cited by 2 claims
  30. SYMBOL_EXISTS celery.result_backends docs/userguide/extending.rst:878-878
     tier: -
     raw: entry-points (for the ``celery.commands``, ``celery.result_backends``,
  31. SYMBOL_EXISTS celery.beat_schedulers docs/userguide/extending.rst:879-879
     tier: -
     raw: or ``celery.beat_schedulers`` namespaces) only takes effect after the
  32. DEPENDENCY kombu docs/userguide/monitoring.rst:840-840
     tier: -
     raw: .. versionadded:: Kombu 5.6.0
     evidence: kombu:requirements/default.txt:>=5.7.0rc1, kombu:requirements/test-ci-default.txt:>=5.6.2, kombu:requirements/test-integration.txt:>=5.6.2
  33. PATH_EXISTS akismet.py docs/userguide/tasks.rst:2406-2406
     tier: bare
     raw: To make API calls to `Akismet`_ I use the `akismet.py`_ library written by
     cited by 2 claims
  34. PATH_EXISTS requirements/doc.txt requirements/README.rst:35-35
     tier: anchored
     raw: :file:`requirements/doc.txt`

