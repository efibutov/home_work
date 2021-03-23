"""
Animal table (Wikipedia) scrapper
"""
# todo: download proper image
# todo: ARGPARSE - use cached file or read from the Internet
# todo: Unittests (mocks)
# todo: HTML output
# todo: documentation
# todo: README
# todo: verify image
# todo: file already exists exception

import bs4
import io
import json
import logger
import multiprocessing as mp
import os
import requests
import settings
from PIL import Image, UnidentifiedImageError


MODULE_LOGGER = logger.AppLogger(__name__)
LATERAL_COLLECTIVES = dict()

if settings.USE_CACHE and not os.path.exists(settings.IMAGES_DIR):
    os.mkdir(settings.IMAGES_DIR)


def create_html_output(lateral_collectives: dict) -> None:
    """
    Actual HTML page with all the relevant data
    """
    pass


def save_data_in_file(content: bytes, file_name: str) -> None:
    """
    Save the file on provided path
    """
    try:
        with open(file_name, 'wb') as image_file:
            image_file.write(content)
    except PermissionError as e:
        MODULE_LOGGER.exception(f'Failed to save the image due to permission error: {e}')
    except FileExistsError as e:
        MODULE_LOGGER.exception(f'File already exists: {e}')
    except OSError as e:
        MODULE_LOGGER.critical(f'Could not save the image (no space on disk? the disk is unavailable?): {e}')


def retrieve_image(image_uri: str, file_name: str) -> None:
    """
    Download an image and verify it is a proper image content,
    provided by its uri and save under provided file_name
    """
    try:
        response = requests.get(image_uri)
        if not response.ok:
            MODULE_LOGGER.warning(f'Server returned error: {response.status_code}, ({image_uri})')
            return

        image = Image.open(io.BytesIO(response.content))

        if image.size != (0, 0):
            save_data_in_file(response.content, file_name)
        else:
            MODULE_LOGGER.warning(f'Bad image dimensions: {image.size}, ({image_uri})')
    except UnidentifiedImageError:
        MODULE_LOGGER.debug(f'Can not identify an image ({image_uri}) in the data')


def retrieve_animal_image(uri: str, animal_name: str) -> None:
    """
    Download the animal's image
    """
    tree = bs4.BeautifulSoup(requests.get(uri).content, 'html.parser')
    script_text = tree.select('script[type="application/ld+json"]')[0]
    script_dict = json.loads(script_text.find_all(text=True)[0])
    image_uri = script_dict['image']
    file_extension = image_uri.split('/')[-1].split('.')[-1]
    full_file_name = os.path.join(settings.IMAGES_DIR, f'{animal_name}.{file_extension}')
    retrieve_image(image_uri, full_file_name)


def update_collection(animal_name: str, lateral_collectives: list) -> None:
    """
    Updates LATERAL_COLLECTIVES dict.
    If the key were not among the dict keys, set a list with an animal name as value (initiate a list)
    """
    for key in lateral_collectives:
        if key in LATERAL_COLLECTIVES:
            LATERAL_COLLECTIVES[key].append(animal_name)
        else:
            LATERAL_COLLECTIVES[key] = [animal_name]


def analyze_table(tree: bs4.BeautifulSoup) -> None:
    """
    Analyzing tree and extract table with animals' data
    """
    # Number of processes to use in the pool - as a cores' number
    pool = mp.Pool(mp.cpu_count())
    table = tree.find_all(settings.TABLE_XPATH)[settings.RELEVANT_TABLE]

    for row in table.find_all('tr'):
        cells = row.find_all('td')
        # Skip a row with too few cells - it's a kind of splitter
        if len(cells) < settings.LATERAL_COLLECTIVES_COL:
            continue

        animal_name_cell = cells[settings.ANIMAL_NAME_COL]
        animal_name = animal_name_cell.find(text=True)
        animal_page = animal_name_cell.find_all('a', href=True)[0]
        pool.apply_async(
            func=retrieve_animal_image,
            args=(f'{settings.BASE_URL}{animal_page["href"]}', str(animal_name),)
        )

        lateral_collectives = [
            str(cell).strip() for cell in cells[settings.LATERAL_COLLECTIVES_COL]
            if type(cell) is bs4.element.NavigableString
        ]
        update_collection(animal_name, lateral_collectives)

    pool.close()
    pool.join()


def scrap_page(content: bytes) -> None:
    """Actual parsing of the WIKI page's content"""
    MODULE_LOGGER.debug('SEARCHING THE TREE')

    try:
        tree = bs4.BeautifulSoup(content, 'html.parser')
    except Exception as e:
        MODULE_LOGGER.exception(f'Failed to parse the html page: {e}')
    else:
        analyze_table(tree)


def load_page() -> bytes:
    """
    Load the HTML page either from cache or from Internet
    """
    if settings.USE_CACHE and os.path.isfile(settings.CACHE_FILE) and os.path.getsize(settings.CACHE_FILE):
        with open(settings.CACHE_FILE, 'rb') as cache_file:
            html = cache_file.read()
    else:
        html = requests.get(settings.ANIMAL_TABLE_URL).content

        if settings.USE_CACHE:
            with open(settings.CACHE_FILE, 'wb') as cache_file:
                cache_file.write(html)

    return html


def main() -> None:
    """
    Read cached file, if it's better.
    Save a cache, if you want to run it many times and it's ok
    to assume that the page did not change
    """
    MODULE_LOGGER.info('Execution has begin')
    scrap_page(load_page())


def test():
    img_uri = 'https://www.ynet.co.il'
    img_uri = 'https://iv1.lisimg.com/image/2960142/539full-rain-phoenix.jpg'
    response = requests.get(img_uri)

    try:
        image = Image.open(io.BytesIO(response.content))
        # print(dir(image))
        print(image.size)
    except UnidentifiedImageError as e:
        MODULE_LOGGER.debug(f'CAnnot identify an image ({img_uri})')


if __name__ == '__main__':
    test()
    # main()
