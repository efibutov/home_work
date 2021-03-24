"""
Image download utils
"""

import bs4
import io
import json
import logger
import os
import settings
import utils
from PIL import Image, UnidentifiedImageError

MODULE_LOGGER = logger.Logger(__name__)


def save_data_in_file(content: bytes, file_name: str) -> None:
    """
    Save the file on provided path
    """
    try:
        if os.path.isfile(file_name):
            MODULE_LOGGER.warning(f'The file {file_name} already exists')

            if not settings.REWRITE_EXISTING_IMAGE_FILES:
                return

        with open(file_name, 'wb') as image_file:
            image_file.write(content)
    except PermissionError as e:
        MODULE_LOGGER.exception(f'Failed to save the image due to permission error: {e}')
    except OSError as e:
        MODULE_LOGGER.critical(f'Could not save the image (no space on disk? the disk is unavailable?): {e}')
    except Exception as e:
        MODULE_LOGGER.exception(f'General exception: {e}')


def validate_image_and_save_to_file(content, file_name, image_uri):
    """
    Validate content and, if it represents a proper image, save it on destination (settings)
    """
    try:
        # Before storing to a disk, validate the data
        image = Image.open(io.BytesIO(content))

        if image.size != settings.WRONG_IMAGE_DIMENSIONS:
            save_data_in_file(content, file_name)
        else:
            MODULE_LOGGER.warning(f'Bad image dimensions: {image.size}, ({image_uri})')
    except UnidentifiedImageError:
        MODULE_LOGGER.debug(f'Can not identify an image ({image_uri}) in the data')


def retrieve_image(image_uri: str, file_name: str) -> None:
    """
    Download an image and verify it is a proper image content,
    provided by its uri and save under provided file_name
    """
    content = utils.retrieve_content(image_uri)

    if not content:
        MODULE_LOGGER.warning(f'Failed to retrieve image: {image_uri}')
    else:
        validate_image_and_save_to_file(content, file_name, image_uri)


def retrieve_animal_image(uri: str, animal_name: str) -> str:
    """
    Download the animal's image

    :param uri:
    :param animal_name:
    :return:
    """
    content = utils.retrieve_content(uri)

    if not content:
        MODULE_LOGGER.warning(f'Failed to retrieve animal page')
    else:
        tree = bs4.BeautifulSoup(content, 'html.parser')
        script_text = tree.select('script[type="application/ld+json"]')[0]
        script_dict = json.loads(script_text.find_all(text=True)[0])
        image_uri = script_dict['image']
        file_extension = image_uri.split('/')[-1].split('.')[-1]
        full_file_name = os.path.join(
            settings.IMAGES_DIR,
            f'{utils.get_proper_file_name_part(animal_name)}.{utils.get_proper_file_name_part(file_extension)}'
        )
        retrieve_image(image_uri, full_file_name)
        return full_file_name
