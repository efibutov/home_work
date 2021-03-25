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


def test_retrieve_content_error(monkeypatch):
    def raise_request_exception():
        raise requests.exceptions.RequestException()

    monkeypatch.setattr(requests, 'get', lambda x: raise_request_exception())
    assert utils.retrieve_content('whatever_uri') == b''


def test_retrieve_content_success(monkeypatch):
    uri = 'http://www.google.com'

    class MockResponse(object):
        def __init__(self, ok=True, content=b''):
            self.ok = ok
            self.content = content

    monkeypatch.setattr(requests, 'get', lambda x: MockResponse(content=b'some_string'))
    assert utils.retrieve_content(uri) == b'some_string'
