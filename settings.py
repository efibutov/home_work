"""
App settings
"""
# Logger related settings
import logging
LOG_FILE_PATH = './logs.txt'
DEFAULT_LOG_LEVEL = logging.DEBUG
LOG_FILE_SIZE = 500 * 1000
LOG_BACKUP_COUNT = 5
LOGGING_FORMAT_STRING = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# HTML, pages, and tables structure settings
BASE_URL = 'https://en.wikipedia.org'
ANIMAL_TABLE_URL = f'{BASE_URL}/wiki/List_of_animal_names'
OUTPUT_HTML_FILE = './output.html'
OUTPUT_HTML_FILE_TEMPLATE = './output_template.html'
TABLE_XPATH = 'table'
ANIMAL_NAME_COL = 0
LATERAL_COLLECTIVES_COL = 5
RELEVANT_TABLE = -1  # There are two tables on the page; we need the 2nd one

# Imaging related settings
IMAGES_DIR = '/tmp'
SOFT_LINK_NAME = 'tmp'
IMAGE_HTML_WIDTH = 400
WRONG_IMAGE_DIMENSIONS = (0, 0)

# Images files, OS restrictions
PATHNAME_STUB_SYMBOL = '_'
REWRITE_EXISTING_IMAGE_FILES = True
