"""
Animal table (Wikipedia) scrapper
"""
# todo: Unittests (mocks)
# todo: HTML output
# todo: documentation
# todo: README
# todo: Logger rotating files

import bs4
import logger
import multiprocessing as mp
import settings
import image_downloader.img_downloader as img_dwnldr
import utils

MODULE_LOGGER = logger.AppLogger(__name__)
LATERAL_COLLECTIVES = dict()


def create_html_output(lateral_collectives: dict) -> None:
    """
    Actual HTML page with all the relevant data
    """
    pass


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
            func=img_dwnldr.retrieve_animal_image,
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
    """
    Actual parsing of the WIKI page's content
    """
    MODULE_LOGGER.debug('Scanning the HTML tree')

    try:
        tree = bs4.BeautifulSoup(content, 'html.parser')
    except Exception as e:
        MODULE_LOGGER.exception(f'Failed to parse the html page: {e}')
    else:
        analyze_table(tree)


# todo: remove caching shit
def load_root_page(uri: str) -> bytes:
    """
    Load the HTML page either from cache or from Internet
    """
    content = utils.retrieve_content(uri)

    if not content:
        MODULE_LOGGER.warning(f'Failed to load root HTML page (uri={uri}) with the animal table')
    else:
        return content


def main() -> None:
    """
    Read cached file, if it's better.
    Save a cache, if you want to run it many times and it's ok
    to assume that the page did not change
    """
    MODULE_LOGGER.info('Start script')
    scrap_page(
        load_root_page(settings.ANIMAL_TABLE_URL)
    )
    MODULE_LOGGER.info(f'Done. Check your {settings.IMAGES_DIR} directory for the images')


if __name__ == '__main__':
    main()
