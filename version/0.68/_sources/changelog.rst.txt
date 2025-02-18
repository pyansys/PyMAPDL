.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`0.68.6 <https://github.com/ansys/pymapdl/releases/tag/v0.68.6>`_ - 2024-10-11
==============================================================================

Added
^^^^^

- chore: update CHANGELOG for v0.68.5 `#3455 <https://github.com/ansys/pymapdl/pull/3455>`_
- refactor: removing deprecated arguments `#3473 <https://github.com/ansys/pymapdl/pull/3473>`_


Fixed
^^^^^

- fix: contributors file `#3457 <https://github.com/ansys/pymapdl/pull/3457>`_
- fix: environment variables not being passed to MAPDL process `#3461 <https://github.com/ansys/pymapdl/pull/3461>`_
- fix: exiting earlier to avoid exceptions from gRPC calls `#3463 <https://github.com/ansys/pymapdl/pull/3463>`_
- fix: add ``build cheatsheet`` as env variable within doc-build `#3468 <https://github.com/ansys/pymapdl/pull/3468>`_


Dependencies
^^^^^^^^^^^^

- build: bump grpcio from 1.66.1 to 1.66.2 in the grpc-deps group `#3453 <https://github.com/ansys/pymapdl/pull/3453>`_
- build: bump sphinx-autobuild from 2024.9.19 to 2024.10.3 in the documentation group `#3454 <https://github.com/ansys/pymapdl/pull/3454>`_
- build: bump ansys-tools-visualization-interface from 0.4.4 to 0.4.5 in the core group `#3477 <https://github.com/ansys/pymapdl/pull/3477>`_
- build: bump the documentation group with 3 updates `#3478 <https://github.com/ansys/pymapdl/pull/3478>`_


Miscellaneous
^^^^^^^^^^^^^

- feat: having two global flags. One for visualizer and one for pyvista `#3460 <https://github.com/ansys/pymapdl/pull/3460>`_


Documentation
^^^^^^^^^^^^^

- docs: another hpc docs reorg `#3465 <https://github.com/ansys/pymapdl/pull/3465>`_
- docs: fix cheat sheet rendering `#3469 <https://github.com/ansys/pymapdl/pull/3469>`_


Maintenance
^^^^^^^^^^^

- ci: bump the actions group with 2 updates `#3470 <https://github.com/ansys/pymapdl/pull/3470>`_
- ci: pre-commit autoupdate `#3471 <https://github.com/ansys/pymapdl/pull/3471>`_
- ci: bypass team check if it is dependabot `#3472 <https://github.com/ansys/pymapdl/pull/3472>`_
- build: bump numpy from 2.1.1 to 2.1.2 in the minimal group `#3476 <https://github.com/ansys/pymapdl/pull/3476>`_

`0.68.5 <https://github.com/ansys/pymapdl/releases/tag/v0.68.5>`_ - 2024-10-04
==============================================================================

Added
^^^^^

- feat: Adapt PyMAPDL to common plotter `#2799 <https://github.com/ansys/pymapdl/pull/2799>`_
- refactor: clean mapdl inprocess and move mute to MapdlCore `#3220 <https://github.com/ansys/pymapdl/pull/3220>`_
- refactor: moving tests to a class and adding delete method. `#3258 <https://github.com/ansys/pymapdl/pull/3258>`_
- maint: update CHANGELOG for v0.68.4 `#3276 <https://github.com/ansys/pymapdl/pull/3276>`_
- chore: drop python3.9 support `#3326 <https://github.com/ansys/pymapdl/pull/3326>`_
- chore: update image cache `#3371 <https://github.com/ansys/pymapdl/pull/3371>`_
- chore: pre-commit autoupdate `#3373 <https://github.com/ansys/pymapdl/pull/3373>`_
- chore: skip database testing on v23.X `#3384 <https://github.com/ansys/pymapdl/pull/3384>`_
- chore: remove mapdl_inprocess.py from codecov analysis `#3404 <https://github.com/ansys/pymapdl/pull/3404>`_
- perf: reduce-testing-time `#3427 <https://github.com/ansys/pymapdl/pull/3427>`_


Changed
^^^^^^^

- ci: bump docker/login-action from 3.2.0 to 3.3.0 in the actions group `#3306 <https://github.com/ansys/pymapdl/pull/3306>`_
- build: bump importlib-metadata from 8.0.0 to 8.2.0 in the minimal group `#3309 <https://github.com/ansys/pymapdl/pull/3309>`_
- build: update pre-commit-hook `#3339 <https://github.com/ansys/pymapdl/pull/3339>`_


Fixed
^^^^^

- fix: removing io error when logging to closed streams `#3273 <https://github.com/ansys/pymapdl/pull/3273>`_
- fix: increasing timeout for local-min `#3282 <https://github.com/ansys/pymapdl/pull/3282>`_
- fix: local-min timeout `#3288 <https://github.com/ansys/pymapdl/pull/3288>`_
- fix: missing arguments in secdata `#3295 <https://github.com/ansys/pymapdl/pull/3295>`_
- Fix/node-numbering `#3297 <https://github.com/ansys/pymapdl/pull/3297>`_
- fix: filename with /OUTPUT command in stored commands `#3304 <https://github.com/ansys/pymapdl/pull/3304>`_
- fix: license headers `#3307 <https://github.com/ansys/pymapdl/pull/3307>`_
- fix: Making sure we skip all the pool unit tests. `#3315 <https://github.com/ansys/pymapdl/pull/3315>`_
- fix: reuploading file on CDREAD `#3355 <https://github.com/ansys/pymapdl/pull/3355>`_
- fix: warning raised in v251 `#3361 <https://github.com/ansys/pymapdl/pull/3361>`_
- fix: avoid changing entities ids after plotting `#3421 <https://github.com/ansys/pymapdl/pull/3421>`_
- fix: disabling logging on `__del__` `#3428 <https://github.com/ansys/pymapdl/pull/3428>`_
- fix: small plotting fix `#3439 <https://github.com/ansys/pymapdl/pull/3439>`_
- fix: changelog `#3452 <https://github.com/ansys/pymapdl/pull/3452>`_


Dependencies
^^^^^^^^^^^^

- build: bump numpy from 1.26.4 to 2.0.0 `#3177 <https://github.com/ansys/pymapdl/pull/3177>`_
- build: bump sphinx from 7.3.7 to 7.4.4 in the documentation group `#3283 <https://github.com/ansys/pymapdl/pull/3283>`_
- build: bump grpcio from 1.65.0 to 1.65.1 in the grpc-deps group `#3299 <https://github.com/ansys/pymapdl/pull/3299>`_
- build: bump sphinx from 7.4.4 to 7.4.6 in the documentation group `#3300 <https://github.com/ansys/pymapdl/pull/3300>`_
- build: bump ansys-tools-visualization-interface from 0.2.6 to 0.3.0 in the core group `#3310 <https://github.com/ansys/pymapdl/pull/3310>`_
- build: bump the documentation group with 3 updates `#3311 <https://github.com/ansys/pymapdl/pull/3311>`_, `#3324 <https://github.com/ansys/pymapdl/pull/3324>`_
- build: bump pytest from 8.2.2 to 8.3.2 in the testing group `#3312 <https://github.com/ansys/pymapdl/pull/3312>`_
- build: bump grpcio from 1.65.1 to 1.65.2 in the grpc-deps group `#3322 <https://github.com/ansys/pymapdl/pull/3322>`_
- build: bump ansys-tools-visualization-interface from 0.3.0 to 0.4.0 in the core group `#3323 <https://github.com/ansys/pymapdl/pull/3323>`_
- feat: adding `PYMAPDL_APDL_LOG` env var for testing `#3328 <https://github.com/ansys/pymapdl/pull/3328>`_
- build: bump grpcio from 1.65.2 to 1.65.4 in the grpc-deps group `#3344 <https://github.com/ansys/pymapdl/pull/3344>`_
- build: bump the core group with 2 updates `#3345 <https://github.com/ansys/pymapdl/pull/3345>`_, `#3358 <https://github.com/ansys/pymapdl/pull/3358>`_, `#3368 <https://github.com/ansys/pymapdl/pull/3368>`_
- build: bump sphinx-gallery from 0.17.0 to 0.17.1 in the documentation group `#3346 <https://github.com/ansys/pymapdl/pull/3346>`_
- ci: bump ansys/actions from 6 to 7 in the actions group `#3352 <https://github.com/ansys/pymapdl/pull/3352>`_
- build: bump pyansys-tools-report from 0.7.3 to 0.8.0 in the testing group `#3360 <https://github.com/ansys/pymapdl/pull/3360>`_
- build: bump the documentation group across 1 directory with 3 updates `#3363 <https://github.com/ansys/pymapdl/pull/3363>`_
- build: bump grpcio from 1.65.4 to 1.66.0 in the grpc-deps group `#3367 <https://github.com/ansys/pymapdl/pull/3367>`_
- build: bump grpcio from 1.66.0 to 1.66.1 in the grpc-deps group `#3381 <https://github.com/ansys/pymapdl/pull/3381>`_
- build: bump plotly from 5.23.0 to 5.24.0 in the documentation group `#3383 <https://github.com/ansys/pymapdl/pull/3383>`_
- build: bump the core group with 3 updates `#3386 <https://github.com/ansys/pymapdl/pull/3386>`_
- build: bump sphinx-autobuild from 2024.4.16 to 2024.9.3 in the documentation group `#3387 <https://github.com/ansys/pymapdl/pull/3387>`_
- build: bump ansys-tools-visualization-interface from 0.4.0 to 0.4.4 in the core group `#3400 <https://github.com/ansys/pymapdl/pull/3400>`_
- build: bump plotly from 5.24.0 to 5.24.1 in the documentation group `#3401 <https://github.com/ansys/pymapdl/pull/3401>`_
- build: bump pytest from 8.3.2 to 8.3.3 in the testing group `#3402 <https://github.com/ansys/pymapdl/pull/3402>`_
- build: bump ansys-sphinx-theme from 1.0.8 to 1.0.11 in the core group `#3418 <https://github.com/ansys/pymapdl/pull/3418>`_
- build: bump sphinx-autobuild from 2024.9.3 to 2024.9.19 in the documentation group `#3419 <https://github.com/ansys/pymapdl/pull/3419>`_
- build: bump pandas from 2.2.2 to 2.2.3 in the documentation group `#3433 <https://github.com/ansys/pymapdl/pull/3433>`_


Miscellaneous
^^^^^^^^^^^^^

- feat/adding missing argument `#3293 <https://github.com/ansys/pymapdl/pull/3293>`_
- feat/adding preppost license to allowed `#3294 <https://github.com/ansys/pymapdl/pull/3294>`_
- docs: adding warning about \*mwrite. Update \*vwrite warning to include \*mwrite `#3296 <https://github.com/ansys/pymapdl/pull/3296>`_
- [pre-commit.ci] pre-commit autoupdate `#3316 <https://github.com/ansys/pymapdl/pull/3316>`_, `#3330 <https://github.com/ansys/pymapdl/pull/3330>`_, `#3351 <https://github.com/ansys/pymapdl/pull/3351>`_
- feat: adding more descriptive errors `#3319 <https://github.com/ansys/pymapdl/pull/3319>`_
- feat: database module improvements `#3320 <https://github.com/ansys/pymapdl/pull/3320>`_
- feat: adding channel subscription method and tests `#3340 <https://github.com/ansys/pymapdl/pull/3340>`_
- feat: Adding 'methodconfig' for all services in channel to allow retry `#3343 <https://github.com/ansys/pymapdl/pull/3343>`_
- feat: adding python side retry mechanism `#3354 <https://github.com/ansys/pymapdl/pull/3354>`_
- Update conftest.py to switch mapdl.tbdat to mapdl.tbdata `#3362 <https://github.com/ansys/pymapdl/pull/3362>`_
- feat: supporting ´´to_dataframe()´´ for some bc list commands `#3412 <https://github.com/ansys/pymapdl/pull/3412>`_
- feat: add exit to inprocess backend `#3435 <https://github.com/ansys/pymapdl/pull/3435>`_
- feat: removing-CDB-files `#3441 <https://github.com/ansys/pymapdl/pull/3441>`_


Documentation
^^^^^^^^^^^^^

- feat: Supporting SLURM env vars for launching MAPDL configuration `#2754 <https://github.com/ansys/pymapdl/pull/2754>`_
- Docs/improving hpc documentation `#3379 <https://github.com/ansys/pymapdl/pull/3379>`_
- build: bump ansys-sphinx-theme from 1.0.5 to 1.0.7 in the core group `#3382 <https://github.com/ansys/pymapdl/pull/3382>`_
- docs: remove ``thispagetitle`` meta tag and add default `#3389 <https://github.com/ansys/pymapdl/pull/3389>`_
- docs: fix keywords metadata `#3396 <https://github.com/ansys/pymapdl/pull/3396>`_
- docs: cards layout for the landing page `#3414 <https://github.com/ansys/pymapdl/pull/3414>`_
- docs: adding cheat sheet on documentation `#3422 <https://github.com/ansys/pymapdl/pull/3422>`_
- docs: revamping example landing page and adding groups `#3434 <https://github.com/ansys/pymapdl/pull/3434>`_
- docs: reorg hpc section `#3436 <https://github.com/ansys/pymapdl/pull/3436>`_
- docs: update image and code block `#3440 <https://github.com/ansys/pymapdl/pull/3440>`_
- docs: adding directive to hide elements `#3449 <https://github.com/ansys/pymapdl/pull/3449>`_


Maintenance
^^^^^^^^^^^

- build: bump pyansys-tools-versioning from 0.5.0 to 0.6.0 in the minimal group `#3357 <https://github.com/ansys/pymapdl/pull/3357>`_
- build: bump importlib-metadata from 8.2.0 to 8.4.0 in the minimal group `#3366 <https://github.com/ansys/pymapdl/pull/3366>`_
- build: bump the minimal group with 2 updates `#3399 <https://github.com/ansys/pymapdl/pull/3399>`_, `#3417 <https://github.com/ansys/pymapdl/pull/3417>`_
- ci: pre-commit autoupdate `#3443 <https://github.com/ansys/pymapdl/pull/3443>`_
- ci: bump actions/checkout from 4.1.7 to 4.2.0 in the actions group `#3444 <https://github.com/ansys/pymapdl/pull/3444>`_
- ci: changing pre-commit commit and pr name `#3445 <https://github.com/ansys/pymapdl/pull/3445>`_

`0.68.4 <https://github.com/ansys/pymapdl/releases/tag/v0.68.4>`_ - 2024-07-15
==============================================================================

Added
^^^^^


Fixed
^^^^^

- fix: missing arguments on ``OCDATA`` command `#3226 <https://github.com/ansys/pymapdl/pull/3226>`_
- fix: Raising `ValueError` when using ips within pool library `#3240 <https://github.com/ansys/pymapdl/pull/3240>`_
- fix: pool issues `#3266 <https://github.com/ansys/pymapdl/pull/3266>`_
- fix: using same labels everywhere `#3188 <https://github.com/ansys/pymapdl/pull/3188>`_
- fix: avoid inspecting suspended processes `#3227 <https://github.com/ansys/pymapdl/pull/3227>`_
- fix: not deleting temporary file when ``remove_temp_dir_on_exit`` =True `#3247 <https://github.com/ansys/pymapdl/pull/3247>`_
- fix: local tests always running as student `#3251 <https://github.com/ansys/pymapdl/pull/3251>`_
- fix: incorrect env vars section `#3252 <https://github.com/ansys/pymapdl/pull/3252>`_


Documentation
^^^^^^^^^^^^^

- docs: adapt static images to dark/light themes `#3249 <https://github.com/ansys/pymapdl/pull/3249>`_
- docs: documenting new naming conventions for commits, branches and PRs. `#3228 <https://github.com/ansys/pymapdl/pull/3228>`_


Dependencies
^^^^^^^^^^^^

- build: bump grpcio from 1.64.1 to 1.65.0 in the grpc-deps group `#3270 <https://github.com/ansys/pymapdl/pull/3270>`_
- build: bump zipp from 3.17.0 to 3.19.1 in /doc/source/examples/extended_examples/hpc `#3261 <https://github.com/ansys/pymapdl/pull/3261>`_
- build: bump the minimal group across 1 directory with 2 updates `#3197 <https://github.com/ansys/pymapdl/pull/3197>`_
- build: bump importlib-metadata from 7.2.0 to 7.2.1 in the minimal group `#3212 <https://github.com/ansys/pymapdl/pull/3212>`_
- build: bump scipy from 1.13.1 to 1.14.0 in the core group `#3213 <https://github.com/ansys/pymapdl/pull/3213>`_
- build: bump the documentation group with 2 updates `#3214 <https://github.com/ansys/pymapdl/pull/3214>`_
- build: bump autopep8 from 2.3.0 to 2.3.1 in the testing group `#3215 <https://github.com/ansys/pymapdl/pull/3215>`_
- build: update requirements in devcontainer directory `#3217 <https://github.com/ansys/pymapdl/pull/3217>`_
- build: removing reredirect sphinx extension `#3224 <https://github.com/ansys/pymapdl/pull/3224>`_
- build: bump importlib-metadata from 7.2.1 to 8.0.0 in the minimal group `#3229 <https://github.com/ansys/pymapdl/pull/3229>`_
- build: bump the core group with 2 updates `#3241 <https://github.com/ansys/pymapdl/pull/3241>`_
- build: update ansys-api-mapdl to 0.5.2 `#3255 <https://github.com/ansys/pymapdl/pull/3255>`_
- build: bump certifi from 2024.2.2 to 2024.7.4 in /doc/source/examples/extended_examples/hpc `#3242 <https://github.com/ansys/pymapdl/pull/3242>`_


Tests
^^^^^

- test: skip test `#3259 <https://github.com/ansys/pymapdl/pull/3259>`_


Maintenance
^^^^^^^^^^^

- [pre-commit.ci] pre-commit autoupdate `#3238 <https://github.com/ansys/pymapdl/pull/3238>`_, `#3253 <https://github.com/ansys/pymapdl/pull/3253>`_
- ci: Fix missing labels format in dependabot file `#3204 <https://github.com/ansys/pymapdl/pull/3204>`_
- ci: wrong tagging on the coverage artifacts `#3225 <https://github.com/ansys/pymapdl/pull/3225>`_
- ci: Adding v251 CentOS based image to testing `#3210 <https://github.com/ansys/pymapdl/pull/3210>`_
- ci: [pre-commit.ci] pre-commit autoupdate `#3206 <https://github.com/ansys/pymapdl/pull/3206>`_
- ci: Use CICD only on ``v*`` tags. `#3186 <https://github.com/ansys/pymapdl/pull/3186>`_
- ci: checking documentation style in ``Examples`` directory too `#3191 <https://github.com/ansys/pymapdl/pull/3191>`_
- chore: update CHANGELOG for v0.68.3 `#3201 <https://github.com/ansys/pymapdl/pull/3201>`_
- ci: Update julia testing `#3211 <https://github.com/ansys/pymapdl/pull/3211>`_
- ci: improving if to match also schedule and workflow_dispatch `#3223 <https://github.com/ansys/pymapdl/pull/3223>`_
- ci: Using a dynamically generated matrix for testing job setup `#3232 <https://github.com/ansys/pymapdl/pull/3232>`_
- ci: increase the files checked for changes before load docs cache `#3237 <https://github.com/ansys/pymapdl/pull/3237>`_
- ci: run extended array based on the person who open the PR `#3256 <https://github.com/ansys/pymapdl/pull/3256>`_


Miscellaneous
^^^^^^^^^^^^^

- chore: update CHANGELOG for v0.68.2 `#3183 <https://github.com/ansys/pymapdl/pull/3183>`_


`0.68.3 <https://github.com/ansys/pymapdl/releases/tag/v0.68.3>`_ - 2024-06-21
==============================================================================

Added
^^^^^

- feat: Add an inprocess backend to pymapdl `#3198 <https://github.com/ansys/pymapdl/pull/3198>`_

`0.68.2 <https://github.com/ansys/pymapdl/releases/tag/v0.68.2>`_ - 2024-06-18
==============================================================================

Added
^^^^^

- feat: add a MAPDL version section in for bug issues `#2982 <https://github.com/ansys/pymapdl/pull/2982>`_
- feat: adding some env var print to report `#2999 <https://github.com/ansys/pymapdl/pull/2999>`_
- feat: adding ``cycexpand`` command `#3023 <https://github.com/ansys/pymapdl/pull/3023>`_
- feat: update ``vfquery`` `#3037 <https://github.com/ansys/pymapdl/pull/3037>`_
- feat: add argument to disable run_at_connect in `MapdlGrpc` `#3047 <https://github.com/ansys/pymapdl/pull/3047>`_
- feat: allowing passing IP to ``MapdlPool`` `#3048 <https://github.com/ansys/pymapdl/pull/3048>`_
- feat: add argument to disable run_at_connect in MapdlGrpc `#3049 <https://github.com/ansys/pymapdl/pull/3049>`_
- feat: converting chained APDL commands to PyMAPDL context manager `#3154 <https://github.com/ansys/pymapdl/pull/3154>`_
- feat: allowing multiple IPs for remote connection on ``MapdlPool`` `#3166 <https://github.com/ansys/pymapdl/pull/3166>`_
- feat: implementing ``ansys/actions/changelogs`` and adding release note in documentation `#3019 <https://github.com/ansys/pymapdl/pull/3019>`_
- feat: adding option to ``_ctrl`` command `#3002 <https://github.com/ansys/pymapdl/pull/3002>`_
- feat: making old API function discoverable when Click is not installed `#3086 <https://github.com/ansys/pymapdl/pull/3086>`_


Changed
^^^^^^^

- refactor: refactoring CLI `#2960 <https://github.com/ansys/pymapdl/pull/2960>`_


Fixed
^^^^^

- fix: avoiding future sphinx warning `#3035 <https://github.com/ansys/pymapdl/pull/3035>`_
- fix: update the general files to align with PyAnsys standards `#3151 <https://github.com/ansys/pymapdl/pull/3151>`_
- fix: combine the ``docker-compose`` files `#3169 <https://github.com/ansys/pymapdl/pull/3169>`_


Documentation
^^^^^^^^^^^^^

- docs: adding previous changes in ``changelog.d`` repository `#3182 <https://github.com/ansys/pymapdl/pull/3182>`_
- docs: clarifying MAPDL commands API section `#3071 <https://github.com/ansys/pymapdl/pull/3071>`_
- docs: HPC documentation `#2966 <https://github.com/ansys/pymapdl/pull/2966>`_
- docs: adding ML-Genetic Algorithm example `#2981 <https://github.com/ansys/pymapdl/pull/2981>`_
- docs: customize agent for linkchecker `#2998 <https://github.com/ansys/pymapdl/pull/2998>`_
- docs: setting docs version to v241 `#3024 <https://github.com/ansys/pymapdl/pull/3024>`_
- docs: adding documentation about remote mapdl pool `#3046 <https://github.com/ansys/pymapdl/pull/3046>`_
- docs: update a minor typo in `mapdl.rst` `#3140 <https://github.com/ansys/pymapdl/pull/3140>`_


Dependencies
^^^^^^^^^^^^

- build: bump autopep8 from 2.2.0 to 2.3.0 in the testing group `#3179 <https://github.com/ansys/pymapdl/pull/3179>`_
- build: bump pyvista[trame] from 0.43.9 to 0.43.10 `#3180 <https://github.com/ansys/pymapdl/pull/3180>`_
- build: bump ansys-sphinx-theme from 0.16.5 to 0.16.6 in the core group across 1 directory `#3181 <https://github.com/ansys/pymapdl/pull/3181>`_


Miscellaneous
^^^^^^^^^^^^^

- chore: removing cdb files `#3036 <https://github.com/ansys/pymapdl/pull/3036>`_
- ci: having only one set of Dependabot rules `#3107 <https://github.com/ansys/pymapdl/pull/3107>`_
- ci: adding tag for doc review `#3118 <https://github.com/ansys/pymapdl/pull/3118>`_
- ci: remove OS package duplicate `#3147 <https://github.com/ansys/pymapdl/pull/3147>`_
- ci: using trusted publisher release process `#3171 <https://github.com/ansys/pymapdl/pull/3171>`_

.. vale on
