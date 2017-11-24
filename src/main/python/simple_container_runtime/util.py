import logging
import time
import requests
from functools import wraps

from botocore.exceptions import ClientError, BotoCoreError

from simple_container_runtime.exceptions import ScrBotoError


def timed(function):
    logger = logging.getLogger(__name__)

    @wraps(function)
    def wrapper(*args, **kwds):
        start = time.time()
        result = function(*args, **kwds)
        elapsed = time.time() - start
        logger.debug("Execution of {0} required {1}s".format(function.__name__, round(elapsed, 2)))
        return result

    return wrapper


def get_logger(name: str = None, root: bool = False):
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S')

    if not root and name:
        logger = logging.getLogger('scr.{0}'.format(name))

    else:
        logger = logging.getLogger('scr')

    logger.setLevel(logging.INFO)
    return logger


def get_instance_id():
    return requests.get('http://169.254.169.254/latest/meta-data/instance-id', timeout=5).text


def with_boto_retry(max_retries=3, pause_time_multiplier=5):
    """
    Annotation retrying a wrapped function call if it raises a CfnSphereBotoError
    with is_throttling_exception=True
    :param max_retries:
    :param pause_time_multiplier:
    :return: :raise e:
    """
    logger = get_logger()

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwds):
            retries = 0

            while True:
                try:
                    return function(*args, **kwds)
                except (BotoCoreError, ClientError) as e:
                    wrapped_exception = ScrBotoError(e)
                    if not wrapped_exception.is_throttling_exception or retries >= max_retries:
                        raise e

                    sleep_time = pause_time_multiplier * (2 ** retries)
                    logger.warning(
                        "{0} call failed with: '{1}' (Will retry in {2}s)".format(function.__name__, wrapped_exception,
                                                                                  sleep_time))
                    time.sleep(sleep_time)
                    retries += 1

        return wrapper

    return decorator
