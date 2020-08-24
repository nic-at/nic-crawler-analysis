# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from builtins import dict, range, str as unicode_str
from past.builtins import basestring
from future import standard_library

import math
import bs4
from collections import defaultdict

import langdetect

from ..parse.html import (
    parse_html,
    extract_html_lang_tag,
    extract_http_equiv_lang_tag
)
from ..parse.http import extract_http_header_lang_tag
from ..util.misc import KNOWN_LANG_TAGS

standard_library.install_aliases()

# Fix seed for reproducible results
langdetect.DetectorFactory.seed = 0
# Init factory and fetch language list
langdetect.detector_factory.init_factory()
lang_list = langdetect.detector_factory._factory.get_lang_list()

TEXT_SAMPLES_N = 20
TEXT_SAMPLES_LENGTH = 20  # words
PROB_THRESHOLD = 0.95
N_TRIALS = 20


def _test_is_bool(var, name):
    return bool(var)


def detect_languages(text, randomize_seed=False):
    """
    Detect the language of text

    Detects the language of text using the langdetect library. By default
    the results of this function are reproducible between subsequent runs.
    When randomize_seed is set to True results between subsequent runs are
    different.

    The underlying implementation in the langdetect library uses random
    samples of the text which are chosen based on an random-number-generator
    seed. This seed is fixed by default.

    Parameters
    ----------
    text : str
        The text to be analyzed
    randomize_seed : bool, optional
        True if random seed used in language detection shall be chosen at
        random (default False)

    Returns
    -------
    languages : dict
        dict of language -> probability pairs
    """
    if not (isinstance(text, str) or isinstance(text, unicode_str)):
        raise ValueError("text is of type '%s' - expected str" % type(text))

    _test_is_bool(randomize_seed, "randomize_seed")

    if randomize_seed:
        preset_seed = langdetect.DetectorFactory.seed
        langdetect.DetectorFactory.seed = None

    detector = langdetect.detector_factory._factory.create()
    detector.n_trial = N_TRIALS
    detector.append(text)

    if randomize_seed:
        langdetect.DetectorFactory.seed = preset_seed

    try:
        langs = detector.get_probabilities()
    except langdetect.lang_detect_exception.LangDetectException:
        return None

    return {_lang.lang: _lang.prob for _lang in langs}


def detect_language_blocks(
        text,
        include_unk=True,
        randomize_seed=False,
        return_shares=True,
        return_blocks=False
):
    """
    Split text into blocks and detect the language of each block

    The text is split into at most 20 blocks of 20 words each of which may
    overlap with each other depending on the length of the string. If the
    string is too short to generate 20 blocks without repeating a block, the
    number of blocks is reduced accordingly.

    The language probabilities of each block are calculated using
    detectLanguage and a block is considered to be in a given language if its
    probability is higher than 0.95. If a block is uncertain it is marked with
    "unk".

    Returned are the either the number of times each language is detected in
    the text (return_shares == False) or the fraction of blocks that is
    detected in each language (return_shares = True). include_unk controls
    whether "unk" is returned as another language. The shares returned always
    sum to 1, regardless of whether "unk" is included or not.

    Additional information on each block is returned if return_blocks == True.

    Parameters
    ----------
    text : str
        text to be analyzed
    include_unk : bool, optional (default: True)
        True if result should include unknown blocks marked with "unk"
    randomize_seed : bool, optional (default: False)
        True if a new seed shall be chosen at each invocation (see
        :func:`detectLanguages`)
    return_shares : bool, optional (default: True)
        True if the share of eachlanguage in the text shall be returned.
        Otherwise the number of blocks in each language is returned.
    return_blocks : bool, optional (default: False)
        True if the blocks used to detect the language shall be returned as a
        list of dict.

    Returns
    -------
    langs : dict
        language => share/count pairs. The sum of shares is always 1.

    blocks : list of dict, optional (return_blocks == True)
        list of dict where each dict contains information on a single block of
        text that was generated.
    """

    if not isinstance(text, basestring):
        raise ValueError("text is of type '%s' - expected str" % type(text))

    include_unk = _test_is_bool(include_unk, "include_unk")
    randomize_seed = _test_is_bool(randomize_seed, "randomize_seed")
    return_shares = _test_is_bool(return_shares, "return_shares")
    return_blocks = _test_is_bool(return_blocks, "return_blocks")

    words = text.split()
    n_words = len(words)

    language_block_counts = defaultdict(int)
    count_blocks_identified = 0

    if n_words <= TEXT_SAMPLES_LENGTH:
        # there is only enough space for a single sample
        begins = [0, ]
    elif n_words < (TEXT_SAMPLES_LENGTH + TEXT_SAMPLES_N):
        # we can slide over (n_words - TEXT_SAMPLES_LENGTH) times
        begins = range(0, n_words - TEXT_SAMPLES_LENGTH, 1)
    else:
        # The text is large enough that we can slide over TEXT_SAMPLES_N times.
        # step is chosen so that the samples are uniformly distributed over the
        # text.
        step = math.floor(
            float(n_words - TEXT_SAMPLES_LENGTH) / TEXT_SAMPLES_N
        )
        assert step > 0, "step should be larger than 0"
        begins = range(0, n_words - TEXT_SAMPLES_LENGTH, step)

    blocks = []

    for _i_begin in begins:
        _text = ' '.join(words[_i_begin:_i_begin + TEXT_SAMPLES_LENGTH])
        _langs = detect_languages(_text, randomize_seed=randomize_seed)

        _lang_detected = "unk"
        if _langs is not None:
            for _lang, _prob in _langs.items():
                if _prob > PROB_THRESHOLD:
                    _lang_detected = _lang
                    language_block_counts[_lang] += 1
                    count_blocks_identified += 1
                    break

        blocks.append({
            'i_begin': _i_begin,
            'text': _text,
            'lang_probs': _langs,
            'lang': _lang_detected

        })

    if return_shares:
        count = len(begins) if include_unk else count_blocks_identified
        result = {
            _lang: _counts / count
            for _lang, _counts in language_block_counts.items()
        }
        if include_unk:
            unk_share = 1.0 - count_blocks_identified / count
            if unk_share > 0:
                result["unk"] = unk_share
    else:
        result = dict(language_block_counts)
        if include_unk:
            unk_n = len(begins) - count_blocks_identified
            if unk_n > 0:
                result["unk"] = unk_n

    if return_blocks:
        return result, blocks
    else:
        return result


def get_site_meta_language(
        header,
        body,
        accepted_langs=KNOWN_LANG_TAGS
):
    """
    Find the language of a site in the meta-information given.

    The function looks at three places in the following order: the top-level
    <html> tag, a http-equiv tag and finally in the HTTP header. The first
    language found that is in accepted_langs is returned.

    Parameters
    ----------
    header : str or list of dict
        Header either as a str that contains json or a list of dictionaries
        each with the keys 'h' and 'v'
    body : str or bs4.BeautifulSoup
        HTML content of the site
    accepted_langs : list
        list of accepted language tags

    Returns
    -------
    language : str or None
        language found or None
    """
    if not isinstance(header, str) and not isinstance(header, dict):
        raise ValueError(
            "unknown header - expected str or dict - got '%s'" % (type(header))
        )

    if isinstance(body, bs4.BeautifulSoup):
        bs = body
    elif isinstance(body, str):
        bs = parse_html(body)
    else:
        raise ValueError("unknown body - expected str or bs4.BeautifulSoup - "
                         "got '%s'" % (type(body)))

    # Prefer language tags in the following order:
    #   HTML Start -> HTTP-EQUIV -> HEADER

    # HTML Start Tag
    html_lang = extract_html_lang_tag(bs, accepted_langs=accepted_langs)
    if html_lang is not None:
        return html_lang

    # HTTP-EQUIV Tag
    http_equiv_lang = extract_http_equiv_lang_tag(
        bs, accepted_langs=accepted_langs
    )
    if http_equiv_lang is not None:
        return http_equiv_lang

    # Header
    http_header_lang = extract_http_header_lang_tag(
        header, accepted_langs=accepted_langs
    )
    if http_header_lang is not None:
        return http_header_lang

    # No language found
    return None
