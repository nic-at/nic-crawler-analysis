# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import zip
from future import standard_library

standard_library.install_aliases()
import nose
from nose.tools import assert_equals, assert_dict_equal, nottest

from nic_crawler_analysis.analysis import js as nca_js
from . import util as nca_util

JS_SECTIONS = [
    ("example.com", [
        ({'type': 'text/javascript'}, '\n            document.write("Hello World!")\n        '),
        ({'src': './include.js'}, None),
        ({'src': 'https://subdomain.example.com/include_local.js'}, None),
        ({'src': 'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js'}, None),
        ({'type': 'text/whatever'}, '\n            some other code\n        '),
    ])
]

ANALYZE_JS_FROM_SECTIONS_RESULT = [
    [
        {"type": 'inline-js', "content": '\n            document.write("Hello World!")\n        '},
        {"type": 'include-local', "src_path": '/include.js', "src":"./include.js"},
        {"type": 'include-local', "src_path": '/include_local.js', "src":'https://subdomain.example.com/include_local.js'},
        {"type": 'include-external', "src_domain": "googleapis.com", "src_path": "/ajax/libs/jquery/3.5.1/jquery.min.js", "src":"https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"},
        {"type": 'inline-unknown', "content":"\n            some other code\n        "},
    ]
]

TEST_SET_ANALYZE_JS_FROM_SECTIONS = zip(JS_SECTIONS, ANALYZE_JS_FROM_SECTIONS_RESULT)

TEST_GENERATORS = []


## Test generators
def test_gen_analyze_js_source_from_blocks():
    for parameters in TEST_SET_ANALYZE_JS_FROM_SECTIONS:
        yield analyze_js_source_from_blocks_test, parameters[0], parameters[1]


TEST_GENERATORS.append(test_gen_analyze_js_source_from_blocks())


## Test functions
@nottest
def analyze_js_source_from_blocks_test(domain_and_blocks, expected_types):
    domain, list_of_blocks = domain_and_blocks
    result = nca_js.analyze_js_source(domain, list_of_blocks)
    for _res, _res_expected, _block in zip(result, expected_types, list_of_blocks):
        assert_dict_equal(_res,_res_expected)

@nottest
def test_all():
    nca_util.test_all(TEST_GENERATORS)
