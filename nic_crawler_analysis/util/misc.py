# -*- coding: utf-8 -*-
import re
import posixpath

from typing import List

# Default accepted languages - these are the ones recognized by langdetect
KNOWN_LANG_TAGS = ['af', 'ar', 'bg', 'bn', 'ca', 'cs', 'cy', 'da', 'de', 'el',
                   'en', 'es', 'et', 'fa', 'fi', 'fr', 'gu', 'he', 'hi', 'hr',
                   'hu', 'id', 'it', 'ja', 'kn', 'ko', 'lt', 'lv', 'mk', 'ml',
                   'mr', 'ne', 'nl', 'no', 'pa', 'pl', 'pt', 'ro', 'ru', 'sk',
                   'sl', 'so', 'sq', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr',
                   'uk', 'ur', 'vi', 'zh-cn', 'zh-tw']

REGEX_VERSION_NUMBER_V_PREFIX = "(?:v([0-9]+))"
COMP_REGEX_VERSION_NUMBER_V_PREFIX = re.compile(REGEX_VERSION_NUMBER_V_PREFIX)
REGEX_VERSION_NUMBER_EXTENDED = "([0-9]+(?:\.[0-9]+)+)"
COMP_REGEX_VERSION_NUMBER_EXTENDED = re.compile(REGEX_VERSION_NUMBER_EXTENDED)
PATH_LENGTH_LIMIT = 20


def parse_lang_tag(text, accepted_langs=KNOWN_LANG_TAGS):
    """
    Take a string that contains language tags and find the ones that are in
    accepted_langs

    The string is split on spaces and on the following characters: ,.-_*\n\t
    Each token is then lower cased and compared to the accepted_langs list
    Parameters
    ----------
    text : str
        String that contains language tokens
    accepted_langs : list
        List of accepted language tags

    Returns
    -------
    languages : list
        list of languages found
    """
    text_split = re.split("[ ,.-_*\n\t]", text.lower())
    langs = []
    for _item in text_split:
        if _item.lower() in accepted_langs:
            langs.append(_item)
    return langs


parse_lang_tag.__annotations__ = {
    'text': str,
    'accepted_langs': List[str],
    'return': List[str]
}


def _split_path(path):
    components = []
    loop_counter = 0
    _head, _tail = posixpath.split(path)
    while _head.replace("/", "") != '':
        if loop_counter > PATH_LENGTH_LIMIT:
            raise ValueError("invalid path - exceeded length limit")
        if _tail != '':
            components.append(_tail)
        _head, _tail = posixpath.split(_head)
        loop_counter += 1

    if _tail != '':
        components.append(_tail)
    return components[::-1]


def _detect_version_numbers(path_components):
    version_numbers_found = []
    for _comp in path_components:
        m = COMP_REGEX_VERSION_NUMBER_EXTENDED.search(_comp)
        if not m:
            m = COMP_REGEX_VERSION_NUMBER_V_PREFIX.match(_comp)
        if m:
            version_numbers_found.append(m.group(1))
    if len(version_numbers_found) > 1:
        return "multiple"
    elif len(version_numbers_found) == 1:
        return version_numbers_found[0]
    else:
        return None


def _detect_file_extension(filename):
    splits = filename.split(".")
    if len(splits) >= 2:
        return splits[-1]
    else:
        return None


def analyze_path(path):
    """
    Return a dictionary with various useful splits of path

    It is assumed that path is given in POSIX format (internally the posixpath
    module is used).

    The returned dictionary contains the following keys:
    'components' : list
        list of the components that make up the path, e.g.:
        some/path/to/a/file.js -> ['some','path','to','a','file.js']
    'version_number' : str
        version number if one of the components contains something that
        resembles a version number. If multiple components contain a version
        number then 'multiple' is returned. If no version number is found, None
        is returned.
    'file' : str, optional
        filename if the path points to what may be a file (i.e. path does not
        end with '/')
    'file_extension' : str, optional
        extension of the file if there is one. None if no extension found.

    Parameters
    ----------
    path : str
        Path to analyze

    Returns
    -------
    ret : dict
        Dictionary with analysis.
    """
    result = {}

    path_stripped = path.strip()

    if len(path_stripped) <= 0:
        return {}

    if path_stripped[-1] == "/":
        is_file = False
    else:
        is_file = True

    path_components = _split_path(path_stripped)
    result["components"] = path_components

    if is_file:
        result["file"] = path_components[-1]
        result["file_extension"] = _detect_file_extension(path_components[-1])

    result["version_number"] = _detect_version_numbers(path_components)

    return result
