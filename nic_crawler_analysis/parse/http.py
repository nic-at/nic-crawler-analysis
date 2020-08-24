# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str
from future import standard_library

import io
import json
from ..util.misc import parse_lang_tag, KNOWN_LANG_TAGS

standard_library.install_aliases()


def parse_header_json(
        header,
        key_mod=lambda x: x,
        value_mod=lambda x: x
):
    """
    Parse an HTTP header returning a dict where the headers are the keys and
    the values are the values

    Parameters
    ----------
    header : str or list
        HTTP header to parse, either as a string containing json or as a list
        of dicts with 'h' and 'v' keys
    key_mod : callable, optional
        Function mapping str to str that modifies the header names
    value_mod : callable, optional
        Function mapping str to str that modifies the header values

    Returns
    -------
    data : dict
        dict with header names as keys and header values as values
    """
    if not isinstance(header, str):
        raise ValueError("header has type '%s'- expected str" % type(header))
    try:
        header_json_parsed = json.load(io.StringIO(header))
    except ValueError:
        return None
    return {
        key_mod(_header['h']): value_mod(_header['v'])
        for _header in header_json_parsed
    }


def extract_http_header_lang_tag(header, accepted_langs=KNOWN_LANG_TAGS):
    """
    Parse an http header and return the language if found

    Parameters
    ----------
    header : str or dict
        HTTP header to parse, either as a string containing json or as a list
        of dicts with 'h' and 'v' keys
    accepted_langs : list
        List of languages that are accepted by the function. Default:
        'nic_crawler_analysis.util.misc.KNOWN_LANG_TAGS`

    Returns
    -------
    lang : str
        first language found or None
    """
    if isinstance(header, str):
        try:
            d = parse_header_json(header)
            if d is None:
                return None
        except Exception as e:
            raise ValueError("could not parse header - %s" % str(e))
    elif isinstance(header, dict):
        d = header
    else:
        raise ValueError(
            "header is of type '%s' - expected str or dict" % type(header)
        )

    if "Content-Language" in d:
        values = d["Content-Language"]
    elif "content-language" in d:
        values = d["content-language"]
    else:
        return None

    if isinstance(values, str):
        langs = parse_lang_tag(values, accepted_langs=accepted_langs)
    else:
        langs = []
        try:
            for _value in values:
                langs += parse_lang_tag(_value, accepted_langs=accepted_langs)
        except TypeError:
            return None

    if len(langs) == 1:
        return langs[0]
    else:
        return None
