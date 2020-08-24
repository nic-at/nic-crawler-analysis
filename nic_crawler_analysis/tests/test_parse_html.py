# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import zip
from future import standard_library

standard_library.install_aliases()
import nose
from nose.tools import assert_equals, nottest, assert_dict_equal

from nic_crawler_analysis.parse import html as nca_html
from . import util as nca_util

HTML_STRING_LIST = [
    """
<!DOCTYPE html>
<html lang="de_DE">
    <head>
        <title>Page Title</title>
        <meta http-equiv="Content-Language" content="it">
        <script type="text/javascript">
            document.write("Hello World!")
        </script>
        <script src="./include.js"></script>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    </head>
    <body>
        <h1>My First Heading</h1>
        <p>My first paragraph. <strong>A strong statement</strong></p>
        <h2>Ein Satz in einer anderen Sprache.</h2>
        <h3>Hallo & So</h3>
        <noscript>Eine freundliche Erinnerung, dass es javascript braucht</noscript>
    </body>
</html>
""",  # 1
]

EXTRACT_TEXT_FROM_HTML_RESULTS = [
    "My First Heading My first paragraph A strong statement Ein Satz in einer anderen Sprache Hallo So Eine "
    "freundliche Erinnerung dass es javascript braucht",
]

EXTRACT_JS_FROM_HTML_RESULTS = [
    [
        ({'type': 'text/javascript'}, '\n            document.write("Hello World!")\n        '),
        ({'src': './include.js'}, None),
        ({'src': 'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js'}, None)
    ]
]

EXTRACT_NOSCRIPT_FROM_HTML_RESULTS = [
    [
        'Eine freundliche Erinnerung, dass es javascript braucht',
    ]
]

TEST_SET_EXTRACT_TEXT_FROM_HTML = zip(HTML_STRING_LIST, EXTRACT_TEXT_FROM_HTML_RESULTS)
TEST_SET_EXTRACT_JS_FROM_HTML = zip(HTML_STRING_LIST, EXTRACT_JS_FROM_HTML_RESULTS)
TEST_SET_EXTRACT_NOSCRIPT_FROM_HTML = zip(HTML_STRING_LIST, EXTRACT_NOSCRIPT_FROM_HTML_RESULTS)

TEST_GENERATORS = []


## Test generators
def test_gen_extract_text_from_html():
    for parameters in TEST_SET_EXTRACT_TEXT_FROM_HTML:
        yield extract_text_from_html_test, parameters[0], parameters[1]


TEST_GENERATORS.append(test_gen_extract_text_from_html)


def test_gen_extract_js_from_html():
    for parameters in TEST_SET_EXTRACT_JS_FROM_HTML:
        yield extract_js_from_html_test, parameters[0], parameters[1]


TEST_GENERATORS.append(test_gen_extract_js_from_html())


def test_gen_extract_noscript_from_html():
    for parameters in TEST_SET_EXTRACT_NOSCRIPT_FROM_HTML:
        yield extract_noscript_from_html_test, parameters[0], parameters[1]


TEST_GENERATORS.append(test_gen_extract_js_from_html())

## Test functions
@nottest
def extract_text_from_html_test(html, expected_text):
    text = nca_html.extract_text_from_html(html)
    assert_equals(text, expected_text)


@nottest
def extract_noscript_from_html_test(html, expected_texts):
    texts = nca_html.extract_noscript_from_html(html)
    assert_equals(len(texts),len(expected_texts))
    for _text,_exp_text in zip(texts,expected_texts):
        assert_equals(_text, _exp_text, "expected: "+_exp_text)


@nottest
def extract_js_from_html_test(html, expected_js):
    js = sorted(nca_html.extract_js_from_html(html), key=dict_string_pair_to_key)
    assert_equals(len(js), len(expected_js))
    expected_js = sorted(expected_js, key=dict_string_pair_to_key)
    for (attrs_, text), (ref_attrs, ref_text) in zip(js, expected_js):
        assert_dict_equal(attrs_, ref_attrs)
        assert_equals(text, ref_text)

@nottest
def dict_string_pair_to_key(dict_string):
    _d, _s = dict_string
    _d_sorted = sorted(_d.items(), key=lambda x: x[0]+x[1])
    return str(_s) + '_'.join(map(lambda x: ':'.join(x), _d_sorted))

@nottest
def test_all():
    nca_util.test_all(TEST_GENERATORS)