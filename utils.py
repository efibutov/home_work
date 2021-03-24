"""
Useful functions for the project
"""

from multiprocessing import Pool, cpu_count
import contextlib
import re
import requests
import settings
from logger import Logger

MODULE_LOGGER = Logger(__name__)


def retrieve_content(uri: str) -> bytes:
    """General method for retrieving content from a provided URI"""
    try:
        response = requests.get(uri)
    except requests.exceptions.RequestException as e:
        MODULE_LOGGER.exception(f'Failed to get animal image data: {e}')
    else:
        if not response.ok:
            MODULE_LOGGER.warning(f'Got bad response from the server: {response.status_code}')
        else:
            content = response.content
            MODULE_LOGGER.debug(f'Got proper content')
            return content


def get_proper_file_name_part(original_filename: str) -> str:
    """
    Replace forbidden UNIX filenames characters with harmless PATHNAME_STUB_SYMBOL
    and return resulting string
    """
    return re.sub(r'[\\/*?:"<>|]', settings.PATHNAME_STUB_SYMBOL, original_filename)


@contextlib.contextmanager
def get_mp_pool(num_of_workers=cpu_count()):
    pool = None

    try:
        pool = Pool(num_of_workers)
        yield pool
    except Exception as e:
        MODULE_LOGGER.exception(f'Failed to create an MP pool: {e}')
    finally:
        if pool:
            pool.close()
            pool.join()
