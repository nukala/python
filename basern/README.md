From the [datacamp](https://www.datacamp.com/community/tutorials/python-oop-tutorial) series about OOP in Python


modules [tutorial](https://realpython.com/python-modules-packages)

TODO [finance-trading](https://www.datacamp.com/community/tutorials/finance-python-trading) not yet as of 04/17/20

TODO learn about how to pytest


TODO wrapper for these commands with counting logger:
bazel build --worker_verbose --explain --verbose_explanations --verbose_failures ... 2>&1 | tee bld.log

bazel test --worker_verbose --explain --verbose_explanations --verbose_failures --test_verbose_timeout_warnings --test_summary=detailed --test_output=summary --nocache_test_results ... 2>&1 | tee test.log

ITEA_RETRIES=1 ITEA_RETRY_PAUSE=300 bazel test --worker_verbose --explain --verbose_explanations --verbose_failures :integration --test_env=UBER_LDAP_UID --test_env=SSH_AUTH_SOCK --test_output=streamed --test_arg=--verbose --sandbox_debug --subcommands --verbose_failures  2>&1 | tee itea.log


to uninstall (did not try): https://osxuninstaller.com/uninstall-guides/properly-uninstall-python-mac/
