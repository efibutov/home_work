import logging

BASE_URL = 'https://en.wikipedia.org'
ANIMAL_TABLE_URL = f'{BASE_URL}/wiki/List_of_animal_names'
LOG_FILE_PATH = './logs.txt'
OUTPUT_HTML_FILE = './output.html'
OUTPUT_HTML_FILE_TEMPLATE = './output_template.html'
TABLE_XPATH = 'table'
ANIMAL_NAME_COL = 0
LATERAL_COLLECTIVES_COL = 5
RELEVANT_TABLE = -1  # There are two tables on the page; we need the 2nd one
IMAGES_DIR = '/tmp'
SOFT_LINK_NAME = 'tmp'
IMAGE_HTML_WIDTH = 400
# When developing and debugging it could be easier to cache the HTML page on a local file
USE_CACHE = True
DEFAULT_LOG_LEVEL = logging.DEBUG
STUB_SYMBOL = '_'
REWRITE_EXISTING_IMAGE_FILES = True
WRONG_IMAGE_DIMENSIONS = (0, 0)
