# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import zip
from future import standard_library
standard_library.install_aliases()
import nose
from nose.tools import assert_equals, nottest

import nic_crawler_analysis.parse.html as nca_html
import nic_crawler_analysis.analysis.lang_detect as nca_lang
from . import util as nca_test

HTML_STRING_LIST = [
    """
<!DOCTYPE html>
<html lang="de_DE">
    <head>
        <title>Page Title</title>
        <meta http-equiv="Content-Language" content="it">
    </head>
    <body>
        <h1>Eine Überschrift</h1>
        <p>Was ganz interessantes</strong></p>
        <h2>Ein Satz in einer anderen Sprache.</h2>
    </body>
</html>
""",  # 1
]

LANG_FROM_TEXT_RESULTS = [
    {'de': 0.999},  # 1
]

TEST_SET_LANG_FROM_HTML = zip(HTML_STRING_LIST, LANG_FROM_TEXT_RESULTS)
TEST_GENERATORS = []


## Test generators
def test_gen_lang_from_html():
    for parameters in TEST_SET_LANG_FROM_HTML:
        yield lang_from_html_test, parameters[0], parameters[1]
TEST_GENERATORS.append(test_gen_lang_from_html)


@nottest
def lang_from_html_test(html, expected_langs):
    text = nca_html.extract_text_from_html(html)
    results = nca_lang.detect_languages(text)

    assert_equals(len(results), len(expected_langs))
    for _lang, _val in expected_langs.items():
        assert_equals(_lang in results.keys(), True)
        assert_equals(results[_lang] >= _val, True)


def test_all():
    nca_test.test_all(TEST_GENERATORS)
