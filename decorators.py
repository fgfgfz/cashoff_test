from time import sleep
from functools import wraps
from sys import exit

from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from loguru import logger


def retry_request(retries=5, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except HTTPError as exception:
                    logger.exception(f'{exception.__class__.__name__}: {exception}')
                except RequestException as exception:
                    logger.exception(f'{exception.__class__.__name__}: {exception}')

                logger.info(f'Attempt {attempt + 1} failed. Retrying after {delay} seconds...')
                sleep(delay)

            logger.info(f'All attempts failed')
            exit(1)

        return wrapper

    return decorator
