"""
Animal table (Wikipedia) scrapper
"""
# todo: Unittests (mocks)
# todo: HTML output
# todo: documentation
# todo: README
# todo: Logger rotating files
# todo: sorted keys

import bs4
import functools
import logger
import multiprocessing as mp
import settings
import img_downloader as img_dwnldr
import utils

MODULE_LOGGER = logger.AppLogger(__name__)
LATERAL_COLLECTIVES = dict()


def create_html_output(lateral_collectives: dict) -> None:
    """
    Actual HTML page with all the relevant data
    """
    html_output = list()
    families = sorted(lateral_collectives)

    for family, in families:
        animals = None
        row = list()
        row.append('<tr>')
        row.append(f'<td>{family}</td>')
        row.append('<td>')
        row.append(
            ',<br/>'.join([animal['animal_name'] for animal in animals])
        )
        row.append('</td>')
        row.append('</tr>')

        html_output.append('\n'.join(row))

    with open(settings.OUTPUT_HTML_FILE_TEMPLATE, 'r') as template_file:
        template = template_file.read()

        with open(settings.OUTPUT_HTML_FILE, 'w') as html_output_file:
            html_output_file.write(
                template.format(
                    data='\n'.join(html_output)
                )
            )


def update_collection(animal_name: str, lateral_collectives: list, img_file_name: str) -> None:
    """
    Updates LATERAL_COLLECTIVES dict.
    If the key were not among the dict keys, set a list with an animal name as value (initiate a list)
    """
    for collective in lateral_collectives:
        if collective in LATERAL_COLLECTIVES:
            LATERAL_COLLECTIVES[collective].append(
                {'animal_name': animal_name, 'image_file_name': img_file_name}
            )
        else:
            LATERAL_COLLECTIVES[collective] = [
                {'animal_name': animal_name, 'image_file_name': img_file_name}
            ]


def analyze_table(tree: bs4.BeautifulSoup) -> None:
    """
    Analyzing tree and extract table with animals' data
    """
    # Number of processes to use in the pool - as a cores' number
    pool = mp.Pool(mp.cpu_count())
    table = tree.find_all(settings.TABLE_XPATH)[settings.RELEVANT_TABLE]
    # Scan table rows for relevant data
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        # Skip a row with too few cells - it's a kind of splitter
        if len(cells) < settings.LATERAL_COLLECTIVES_COL:
            continue

        lateral_collectives = [
            str(cell).strip() for cell in cells[settings.LATERAL_COLLECTIVES_COL]
            if type(cell) is bs4.element.NavigableString
        ]
        animal_name_cell = cells[settings.ANIMAL_NAME_COL]
        animal_name = animal_name_cell.find(text=True)
        animal_page = animal_name_cell.find_all('a', href=True)[0]
        pool.apply_async(
            func=img_dwnldr.retrieve_animal_image,
            args=(f'{settings.BASE_URL}{animal_page["href"]}', str(animal_name),),
            callback=functools.partial(update_collection, animal_name, lateral_collectives)
        )

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
    scrap_page(load_root_page(settings.ANIMAL_TABLE_URL))
    MODULE_LOGGER.info(f'Done. Check your {settings.IMAGES_DIR} directory for the images')
    create_html_output(LATERAL_COLLECTIVES)


if __name__ == '__main__':
    main()
