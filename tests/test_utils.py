"""
Unit tests
"""

import pytest
import utils


@pytest.mark.parametrize(
    'test_value,expected',
    [
        ('/hello/world', '_hello_world',),
        ('*hello^world', '_hello^world'),
        ('*hello\\world', '_hello_world'),
        ('<hello?world>', '_hello_world_'),
    ]
)
def test_get_proper_file_name_part(test_value, expected):
    assert utils.get_proper_file_name_part(test_value) == expected
