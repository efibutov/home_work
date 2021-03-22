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

MODULE_LOGGER = AppLogger(__name__)
LATERAL_COLLECTIVES = dict()


def download_animal_image(uri, animal_name):
    print(animal_name)
    return
    r = requests.get(uri)

    try:
        tree = bs4.BeautifulSoup(requests.get(uri).content, 'html.parser')
        script_text = tree.select('script[type="application/ld+json"]')[0]
        script_dict = json.loads(script_text.find_all(text=True)[0])
        image_uri = script_dict['image']
        file_name = image_uri.split('/')[-1]

        with open(os.path.join(settings.IMAGES_DIR, file_name), 'wb') as image_file:
            image_file.write(requests.get(image_uri).content)
    except Exception as e:
        print(uri, e)


def update_collection(animal_name, lateral_collectives):
    """
    Updates LATERAL_COLLECTIVES dict.
    If the key no present in the dict, add set a list with an animal name as value
    """
    for key in lateral_collectives:
        if key in LATERAL_COLLECTIVES:
            LATERAL_COLLECTIVES[key].append(animal_name)
        else:
            LATERAL_COLLECTIVES[key] = [animal_name]


def scrap_page(content):
    """Actual parsing of the content of the WIKI page"""
    MODULE_LOGGER.debug('SEARCHING THE TREE')
    pool = Pool(cpu_count())

    try:
        tree = bs4.BeautifulSoup(content, 'html.parser')
    except Exception as e:
        MODULE_LOGGER.exception(f'Failed to parse the html page: {e}')
    else:
        table = tree.find_all(settings.TABLE_XPATH)[settings.RELEVANT_TABLE]

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            # Skip a row with too few cells - it's a kind of splitter
            if len(cells) < settings.LATERAL_COLLECTIVES_COL:
                continue

            animal_name_cell = cells[settings.ANIMAL_NAME_COL]
            animal_name = str(animal_name_cell.find(text=True))
            animal_page = animal_name_cell.find_all('a', href=True)[0]
            pool.apply_async(
                func=download_animal_image,
                args=(f'{settings.BASE_URL}{animal_page["href"]}', animal_name,)
            )

            lateral_collectives = [
                str(cell).strip() for cell in cells[settings.LATERAL_COLLECTIVES_COL]
                if type(cell) is bs4.element.NavigableString
            ]
            update_collection(animal_name, lateral_collectives)

    pool.close()
    pool.join()


def main():
    """
    Read cached file, if it's better.
    Save a cache, if you want to run it many times and it's ok
    to assume that the page did not change
    """
    MODULE_LOGGER.info('Execution has begin')

    if os.path.isfile(settings.CACHE_FILE) and os.path.getsize(settings.CACHE_FILE):
        with open(settings.CACHE_FILE, 'r') as cache_file:
            html = cache_file.read()
    else:
        html = str(requests.get(settings.ANIMAL_TABLE_URL).content)

        with open(settings.CACHE_FILE, 'w') as cache_file:
            cache_file.write(html)

    scrap_page(html)


if __name__ == '__main__':
    main()
