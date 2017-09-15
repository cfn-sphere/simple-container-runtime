from unittest2 import TestCase
from mock import patch, Mock

from simple_container_runtime.runnable import Runnable


class RunnableTests(TestCase):
    def test_execute_pre_start_modules_does_not_fail_with_missing_config_key(self):
        r = Runnable(None, {"a": "b"})
        r._execute_pre_start_modules()

    def test_execute_pre_start_modules_does_not_fail_with_empty_config_key(self):
        r = Runnable(None, {"pre_start": None})
        r._execute_pre_start_modules()

    def test_send_signals_does_not_fail_with_missing_config_key(self):
        r = Runnable(None, {"a": "b"})
        r._send_signals(False)

    def test_send_signals_does_not_fail_with_empty_config_key(self):
        r = Runnable(None, {"signals": None})
        r._send_signals(False)

    def test_execute_health_checks_does_not_fail_with_missing_config_key(self):
        r = Runnable(None, {"a": "b"})
        r._execute_health_checks()

    def test_execute_health_checks_does_not_fail_with_empty_config_key(self):
        r = Runnable(None, {"healthchecks": None})
        r._execute_health_checks()
