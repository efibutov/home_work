"""
Unit tests
"""

import pytest
import utils
import requests


@pytest.mark.parametrize(
    'test_value,expected',
    [
        ('/hello|world', '_hello_world',),
        ('*hello^world:', '_hello^world_'),
        ('*hello\\world', '_hello_world'),
        ('<hello?world>', '_hello_world_'),
        ('[hello]world"', '[hello]world_'),
    ]
)
def test_get_proper_file_name_part(test_value, expected):
    assert utils.get_proper_file_name_part(test_value) == expected


def test_rq(monkeypatch):
    class RequestsGet(object):
        def __init__(self, ok=True, content=b''):
            self.ok = ok
            self.content = content

        def get(self, uri):
            return self.ok

    monkeypatch.setattr(requests, 'get', lambda x: RequestsGet())
    assert utils.retrieve_content('whatever_string') == b''
