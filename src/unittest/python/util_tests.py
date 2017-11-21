from botocore.exceptions import ClientError
from unittest2 import TestCase
from mock import patch, Mock

from simple_container_runtime import util


class Util(TestCase):
    def test_with_boto_retry_retries_method_call_for_throttling_exception(self):
        count_func = Mock()

        @util.with_boto_retry(max_retries=1, pause_time_multiplier=1)
        def my_retried_method(count_func):
            count_func()
            exception = ClientError(error_response={"Error": {"Code": "Throttling", "Message": "Rate exceeded"}},
                                    operation_name="DescribeStacks")
            raise exception

        with self.assertRaises(ClientError):
            my_retried_method(count_func)

        self.assertEqual(2, count_func.call_count)

    def test_with_boto_retry_does_not_retry_for_simple_exception(self):
        count_func = Mock()

        @util.with_boto_retry(max_retries=1, pause_time_multiplier=1)
        def my_retried_method(count_func):
            count_func()
            raise Exception

        with self.assertRaises(Exception):
            my_retried_method(count_func)

        self.assertEqual(1, count_func.call_count)

    def test_with_boto_retry_does_not_retry_for_another_boto_client_error(self):
        count_func = Mock()

        @util.with_boto_retry(max_retries=1, pause_time_multiplier=1)
        def my_retried_method(count_func):
            count_func()
            exception = ClientError(error_response={"Error": {"Code": "Another Error", "Message": "Foo"}},
                                    operation_name="DescribeStacks")
            raise exception

        with self.assertRaises(ClientError):
            my_retried_method(count_func)

        self.assertEqual(1, count_func.call_count)

    def test_with_boto_retry_does_not_retry_without_exception(self):
        count_func = Mock()

        @util.with_boto_retry(max_retries=1, pause_time_multiplier=1)
        def my_retried_method(count_func):
            count_func()
            return "foo"

        self.assertEqual("foo", my_retried_method(count_func))
        self.assertEqual(1, count_func.call_count)
