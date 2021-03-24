"""
Animal table (Wikipedia) scrapper
Analyzes the root table, and creates an output in user-friendly format (html page with images)
"""
# todo: Unittests (mocks)
# todo: documentation
# todo: typehints
import bs4
import functools
import logger
import multiprocessing as mp
import os
import settings
import img_downloader as img_dwnldr
import utils

MODULE_LOGGER = logger.Logger(__name__)
LATERAL_COLLECTIVES = dict()


def create_html_output(lateral_collectives: dict) -> None:
    """Actual HTML page with all the relevant data"""
    html_output = list()

    for family in sorted(lateral_collectives):
        row = list()
        row.append(f'<tr><td style="text-align:center">{family}</td><td style="text-align:center">')
        animals_field = list()

        for animal_name in sorted(lateral_collectives[family]):
            animals_field.append(animal_name)
            img_src = os.path.join(settings.IMAGES_DIR, lateral_collectives[family][animal_name])

            if os.path.isfile(img_src):
                animals_field.append(
                    f'<img src=".{lateral_collectives[family][animal_name]}" width="{settings.IMAGE_HTML_WIDTH}">'
                )

        row.append('<br />'.join(animals_field))
        row.append('</td></tr>')
        html_output.append('\n'.join(row))

    with open(settings.OUTPUT_HTML_FILE_TEMPLATE, 'r') as template_file:
        template = template_file.read()

    with open(settings.OUTPUT_HTML_FILE, 'w') as html_output_file:
        html_output_file.write(template.format(data='\n'.join(html_output)))


def update_collection(animal_name: str, lateral_collectives: list, img_file_name: str) -> None:
    """
    Updates LATERAL_COLLECTIVES dict.
    If the key were not among the dict keys, set a list with an animal name as value (initiate a list)
    """
    for collective in lateral_collectives:
        if collective not in LATERAL_COLLECTIVES:
            LATERAL_COLLECTIVES[collective] = {animal_name: img_file_name}
        else:
            LATERAL_COLLECTIVES[collective][animal_name] = img_file_name


def analyze_table(tree: bs4.BeautifulSoup) -> None:
    """Analyzing tree and extract table with animals' data"""
    # Number of processes to use in the pool - as a cores' number
    table = tree.find_all(settings.TABLE_XPATH)[settings.RELEVANT_TABLE]

    with utils.get_mp_pool() as pool:
        # Scan table rows for relevant data
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            # Skip a row with too few cells - it's a kind of splitter
            if len(cells) < settings.LATERAL_COLLECTIVES_COL:
                continue
            # Add strings only, skip tags
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


def make_soft_link() -> None:
    """
    Add soft link in the current directory to the provided image source dir
    """
    try:
        os.symlink(
            src=settings.IMAGES_DIR,
            dst=settings.SOFT_LINK_NAME,
            target_is_directory=True
        )
    except FileExistsError as e:
        MODULE_LOGGER.debug(f'The soft link already exists: {e}')
    else:
        MODULE_LOGGER.debug(f'The soft link successfully created')


def main() -> None:
    """
    Entry point
    """
    MODULE_LOGGER.info('Start script')
    make_soft_link()
    scrap_page(load_root_page(settings.ANIMAL_TABLE_URL))
    MODULE_LOGGER.info(f'Done. Check your {settings.IMAGES_DIR} directory for the images')
    create_html_output(LATERAL_COLLECTIVES)


if __name__ == '__main__':
    main()
