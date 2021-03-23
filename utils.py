import re
import requests
import settings
from logger import AppLogger

MODULE_LOGGER = AppLogger(__name__)


def retrieve_content(uri: str) -> bytes:
    """
    General method for retrieving content from a provided URI
    """
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
    Replace forbidden UNIX filenames characters with harmless STUB_SYMBOL and return resulting string
    """
    return re.sub(r'[\\/*?:"<>|]', settings.STUB_SYMBOL, original_filename)