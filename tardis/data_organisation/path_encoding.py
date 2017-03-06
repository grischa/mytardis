import string
from urllib import quote

from django.conf import settings

SAFE_CHARS = getattr(settings, 'SAFE_FILESYSTEM_CHARACTERS', '')


def path_string_escape(input_string):
    return quote(input_string, safe=SAFE_CHARS)


def whitespace_to_underscores(input_string):
    for ws in string.whitespace:
        if ws in input_string:
            input_string = input_string.replace(ws, '_')
    return input_string
