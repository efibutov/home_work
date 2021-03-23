"""
Basic scrapper
"""
import bs4
from multiprocessing import Pool, cpu_count
import os
import requests
import settings
from logger import AppLogger
import json
# todo: ARGPARSE - use cached file or read from the Internet
# todo: Logger
# todo: Unittests (mocks)
# todo: HTML output
# todo: documentation

MODULE_LOGGER = AppLogger(__name__)
LATERAL_COLLECTIVES = dict()


def create_html_output(lateral_collectives: dict) -> None:
    """
    Actual HTML page with all the relevant data
    """
    pass


def download_animal_image(uri: str, animal_name) -> None:
    """
    Download the animal's image
    """
    try:
        # print(animal_name)
        tree = bs4.BeautifulSoup(requests.get(uri).content, 'html.parser')
        script_text = tree.select('script[type="application/ld+json"]')[0]
        script_dict = json.loads(script_text.find_all(text=True)[0])
        image_uri = script_dict['image']
        file_extension = image_uri.split('/')[-1].split('.')[-1]
        full_file_name = os.path.join(settings.IMAGES_DIR, f'{animal_name}.{file_extension}')

        with open(full_file_name, 'wb') as image_file:
            image_file.write(requests.get(image_uri).content)
    except PermissionError as e:
        MODULE_LOGGER.exception(f'Failed to save an image due to permission error: {e}')
    except FileExistsError as e:
        MODULE_LOGGER.exception(f'Failed does not exist: {e}')


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
    # The simplest way to run in multithreading - use all the available cores
    pool = Pool(cpu_count())
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
            func=download_animal_image,
            args=(f'{settings.BASE_URL}{animal_page["href"]}', str(animal_name),)
        )

        lateral_collectives = [
            str(cell).strip() for cell in cells[settings.LATERAL_COLLECTIVES_COL]
            if type(cell) is bs4.element.NavigableString
        ]
        update_collection(animal_name, lateral_collectives)

    pool.close()
    pool.join()


def scrap_page(content: str) -> None:
    """Actual parsing of the WIKI page's content"""
    MODULE_LOGGER.debug('SEARCHING THE TREE')

    try:
        tree = bs4.BeautifulSoup(content, 'html.parser')
    except Exception as e:
        MODULE_LOGGER.exception(f'Failed to parse the html page: {e}')
    else:
        analyze_table(tree)


def load_page_data():
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
    scrap_page(load_page_data())


if __name__ == '__main__':
    # s = str(bs4.element.NavigableString('Vicuña'))
    # print(s)
    main()
