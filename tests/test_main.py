"""
Unit tests
"""

import pytest
from main import main
from PIL import Image
import requests


def test_main():
    """
    Testing main function
    """
    assert not main()
