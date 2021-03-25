"""
Useful functions for the project
"""

import contextlib
import re
import requests
import settings
from logger import Logger
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count

MODULE_LOGGER = Logger(__name__)


def retrieve_content(uri: str) -> bytes:
    """
    General method for retrieving content from a provided URI.
    Empty bytes list will be returned on any exception
    """
    result = bytes()

    try:
        response = requests.get(uri)
    except requests.exceptions.RequestException as e:
        MODULE_LOGGER.exception(f'Failed to get animal image data: {e} (uri={uri})')
    else:
        if not response.ok:
            MODULE_LOGGER.warning(f'Bad response {response.status_code} (uri={uri})')
        else:
            MODULE_LOGGER.debug(f'Proper content (uri={uri})')
            result = response.content

    return result


def get_proper_file_name_part(original_filename: str) -> str:
    """
    Replace forbidden UNIX filenames characters with harmless PATHNAME_STUB_SYMBOL
    and return resulting string
    """
    return re.sub(r'[\\/*?:"<>|]', settings.PATHNAME_STUB_SYMBOL, original_filename)


@contextlib.contextmanager
def get_mp_pool(num_of_workers=cpu_count()):
    """Allows to use a MP pool of workers with a context manager"""
    pool = None

    try:
        pool = ThreadPool(num_of_workers)
        yield pool
    except Exception as e:
        MODULE_LOGGER.exception(f'Failed to create an MP pool: {e}')
    finally:
        if pool:
            pool.close()
            pool.join()
