# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import zip
from future import standard_library
standard_library.install_aliases()
from nose.tools import assert_equals, nottest

import nic_crawler_analysis.analysis.lang_detect as nca_lang

from . import util as nca_util


TEXT_STRING_LIST = [
    "Ein Beispieltext mit dem wir uns anschauen, ob beim ausführne von unseren Funktionen das richtige herauskommt.",
    # 1
    "An example text to test for english language detection. If everything goes well we should get the result english " \
    "when we're done.",  # 2
    "An example text to test for mixed language detection. If the two parts are roughly equally long, dann ist die " \
    "Chance groß, dass beide Sprachen im Ergebnis auftauchen. Das muss aber nicht sein, weil die Detektion ein " \
    "zufälliges Sample des Textes verwendet.",  # 3
]

LANG_FROM_TEXT_RESULTS = [
    {'de': 0.999},  # 1
    {'en': 0.999},  # 2
    {'de': 0.0, 'en': 0.0},  # 3
]

LANG_BLOCKS_FROM_TEXT_RESULTS = [
    {'de': (0.80, 1.0)},  # 1
    {'en': (0.80, 1.0)},  # 2
    {'de': (0.1, 0.5), 'en': (0.1, 0.5), 'unk': (0.2, 0.8)},  # 3
]

TEST_SET_LANG_FROM_TEXT = zip(TEXT_STRING_LIST, LANG_FROM_TEXT_RESULTS)
TEST_SET_LANG_BLOCKS_FROM_TEXT = zip(TEXT_STRING_LIST, LANG_BLOCKS_FROM_TEXT_RESULTS)

TEST_GENERATORS = []

## Test generators
def test_gen_lang_from_text():
    for parameters in TEST_SET_LANG_FROM_TEXT:
        yield lang_from_text_test, parameters[0], parameters[1]
TEST_GENERATORS.append(test_gen_lang_from_text)


def test_gen_lang_blocks_from_text():
    for parameters in TEST_SET_LANG_BLOCKS_FROM_TEXT:
        yield lang_blocks_from_text_test, parameters[0], parameters[1]
TEST_GENERATORS.append(test_gen_lang_blocks_from_text)


## Test functions
@nottest
def lang_from_text_test(text, expected_langs):
    results = nca_lang.detect_languages(text)

    assert_equals(len(results), len(expected_langs))
    for _lang, _val in expected_langs.items():
        assert_equals(_lang in results.keys(), True)
        assert_equals(results[_lang] >= _val, True)


@nottest
def lang_blocks_from_text_test(text,expected_langs):
    results = nca_lang.detect_language_blocks(text)

    assert_equals(len(results), len(expected_langs))
    for _lang, (_val_lower, _val_upper) in expected_langs.items():
        assert_equals(_lang in results.keys(), True)
        assert_equals(results[_lang] >= _val_lower, True)
        assert_equals(results[_lang] <= _val_upper, True)


@nottest
def test_all():
    nca_util.test_all(TEST_GENERATORS)
