# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import dict
from builtins import str as unicode_str
from past.builtins import basestring
from future import standard_library

import re
import copy
import bs4

from ..util.misc import KNOWN_LANG_TAGS, parse_lang_tag

standard_library.install_aliases()

# Test whether ModuleNotFoundError is available and replace it if not
# This is a python 2.7 compatibility fix
try:
    ModuleNotFoundError
except NameError:
    ModuleNotFoundError = ImportError


try:
    from html.parser import HTMLParseError as ParseError
except ImportError:
    class ParseError(Exception):
        """Dummy exception that replaces HTMLParseError for compatibility
           with older versions of python"""
        pass

try:
    import rfc3987
    RFC_REGEX_AVAILABLE = True
except ModuleNotFoundError:
    RFC_REGEX_AVAILABLE = False


SITE_DESCRIPTION_TAGS = [
    "description",
    "topic",
    "keywords",
    "Description",
    "Topic",
    "Keywords"
]


def filter_text(text):
    """
    Filter out a list of characters from _text_.

    Parameters
    ----------
    text : str
        The string to be filtered

    Returns
    -------
    text :  str
        The filtered string
    """
    return re.sub(
        '[\n \[\]"\'.,:!?/+\-–\\\\*#()%&=_§€$@<>;|'
        '©0123456789»«®…”“•�°←→„▶\x96\xa0\t]+',
        ' ',
        text
    ).strip()


def parse_html(html_):
    """
    Take a html string, parse it and return the structure as a BeautifulSoup
    object.

    Parameters
    ----------
    html_ : str
        string that contains HTML

    Returns
    -------
    bs : bs4.BeautifulSoup
        Parsed HTML
    """
    return bs4.BeautifulSoup(html_, 'html.parser')


def extract_text_from_html(
        input_,
        pre_strip_urls=False
):
    """
    Take a HTML document and return the raw text

    The raw text is returned without any structure (including without
    punctuation) and without non alphabetic characters.

    bs4.BeautifulSoup.get_text is used for parsing. It removes HTML comments,
    scripts and styles prior to extracting the text. Only text in the body is
    returned.

    Parameters
    ----------
    input_ : str or bs4.BeautifulSoup
        HTML document from which the text will be extracted

    pre_strip_urls : bool
        If True, Links that are found in the text part of the HTML are removed
        prior to filtering

    Returns
    -------
    text : str
        The text found in the HTML document
    """
    if isinstance(input_, bs4.BeautifulSoup):
        bs = input_
    elif isinstance(input_, basestring):
        bs = parse_html(input_)
    else:
        raise ValueError("unknown input_ - expected str or "
                         "bs4.BeautifulSoup got '%s'" % (type(input_)))

    try:
        text = bs.body.get_text().strip()
    except (TypeError,AttributeError):
        return None

    if pre_strip_urls:
        if RFC_REGEX_AVAILABLE:
            text = rfc3987.get_compiled_pattern(rule='URI').sub(" ", text)
        else:
            raise ValueError("pre_strip_urls requires regex and rfc3987 "
                             "libraries. One or both could not be found")

    return filter_text(text)


def get_site_description(input_):
    """
    Return the description given in an HTML document

    The function looks for meta tags that have one of the names in the
    `SITE_DESCRIPTION_TAGS` list and concatenates their content into a single
    string. The string is then filtered with :func:`filter_text`.

    Parameters
    ----------
    input_ : str or bs4.BeautifulSoup
        HTML document from which the description will be extracted

    Returns
    -------
    topics : str
        Topics found concatenated into a single string

    """
    if isinstance(input_, bs4.BeautifulSoup):
        bs = input_
    elif isinstance(input_, basestring):
        bs = parse_html(input_)
    else:
        raise ValueError("unknown input_ - expected str or bs4.BeautifulSoup "
                         "got '%s'" % (type(input_)))

    try:
        desc_tags = bs.head.find_all(
            "meta", attrs=dict(name=SITE_DESCRIPTION_TAGS)
        )
    except(TypeError, ParseError):
        return None

    return (' '.join([
        filter_text(_tag["content"])
        for _tag in desc_tags
        if "content" in _tag.attrs
    ])).strip()


def extract_html_lang_tag(
        input_,
        accepted_langs=KNOWN_LANG_TAGS
):
    """
    Find the language tag in the opening <html> tag and return it

    Only languages that are in the accepted_langs list are returned.

    Parameters
    ----------
    input_ : str or bs4.BeautifulSoup
        HTML document from which the description will be extracted
    accepted_langs : list
        List of languages that are accepted by the function.
        Default: `nic_crawler_analysis.util.misc.KNOWN_LANG_TAGS`

    Returns
    -------
    lang : str or None
        first language found or None
    """
    if isinstance(input_, bs4.BeautifulSoup):
        bs = input_
    elif isinstance(input_, basestring):
        bs = parse_html(input_)
    else:
        raise ValueError("unknown input_ - expected str or bs4.BeautifulSoup "
                         "got '%s'" % (type(input_)))

    try:
        tag_text = bs.html["lang"]
    except (KeyError, TypeError, AttributeError):
        return None

    langs = parse_lang_tag(tag_text, accepted_langs=accepted_langs)
    if len(langs) > 0:
        return langs[0]
    else:
        return None


def extract_http_equiv_lang_tag(
        input_,
        accepted_langs=KNOWN_LANG_TAGS
):
    """
    Find the language tag in an http-equiv tag return it

    Only languages that are in the accepted_langs list are returned.

    Parameters
    ----------
    input_ : str or bs4.BeautifulSoup
        HTML document from which the description will be extracted
    accepted_langs : list
        List of languages that are accepted by the function.
        Default: `nic_crawler_analysis.util.misc.KNOWN_LANG_TAGS`

    Returns
    -------
    lang : str or None
        first language found or None
    """
    if isinstance(input_, bs4.BeautifulSoup):
        bs = input_
    elif isinstance(input_, basestring):
        bs = parse_html(input_)
    else:
        raise ValueError("unknown input_ - expected str or bs4.BeautifulSoup "
                         "got '%s'" % (type(input_)))

    try:
        tags_lang = bs.findAll(
            "meta",
            attrs={
                'http-equiv': [
                    "Content-Language",
                    "content-language"
                ]
            })
        langs = parse_lang_tag(tags_lang[0]["content"])
        if len(langs) == 1:
            return langs[0]
        else:
            return None
    except (ParseError, KeyError, IndexError):
        return None


def extract_js_from_html(input_):
    """
    Find all script tags and return their contents

    Parameters
    ----------
    input_ : str or bs4.Beautifulsoup
        HTML content to extract from

    Returns
    -------
    js_code : List of tuples
        dict, string pairs. The dict contains the tag's attributes (which may
        be empty) and the string containts the text of the tag (which may be
        None).

    """
    if isinstance(input_, bs4.BeautifulSoup):
        bs = input_
    elif isinstance(input_, basestring):
        bs = parse_html(input_)
    else:
        raise ValueError("unknown input_ - expected str or bs4.BeautifulSoup "
                         "got '%s'" % (type(input_)))

    return [
        (
            copy.deepcopy(tag.attrs),
            unicode_str(tag.string)
            if tag.string is not None else None
        )
        for tag in bs.findAll("script")
    ]


def extract_noscript_from_html(input_):
    """
    Find all script tags and return their contents

    Parameters
    ----------
    input_ : str or bs4.Beautifulsoup
        HTML content to extract from

    Returns
    -------
    noscript_tags : List of unicode_str
        List of text included in noscript tags

    """
    if isinstance(input_, bs4.BeautifulSoup):
        bs = input_
    elif isinstance(input_, basestring):
        bs = parse_html(input_)
    else:
        raise ValueError("unknown input_ - expected str or bs4.BeautifulSoup "
                         "got '%s'" % (type(input_)))

    try:
        tag_strings = [
            unicode_str(tag.string) if tag.string is not None else None
            for tag in bs.findAll("noscript")
        ]
    except TypeError:
        return []

    return tag_strings
