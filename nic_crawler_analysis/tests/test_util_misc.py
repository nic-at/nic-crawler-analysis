# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import zip
from future import standard_library

standard_library.install_aliases()
import nose
from nose.tools import assert_equals, assert_dict_equal, nottest, raises

from nic_crawler_analysis.util import misc as nca_misc
from . import util as nca_util

TEST_SET_ANALYZE_PATH_FROM_STR_INPUT = [
    "/some/path/to/a/file/v5.1.8/include.js",   # 1
    "/some/path/to/",                           # 2
    "/some//path/to/",                          # 3
    "/some/path/to/a/file/v5/include.js",       # 4
    "/some/path/to/a/file/include-5.1.9.js",    # 5
    "some/path/to/a/file/v5.1.8/include.xml",   # 6
    "some/path/to/a/file5/include.xml",         # 7
]

TEST_SET_ANALYZE_PATH_FROM_STR_RESULTS = [
    {'components': ['some', 'path', 'to', 'a', 'file', 'v5.1.8', 'include.js'], 'file': 'include.js', 'file_extension': 'js', 'version_number': '5.1.8'},  #1
    {'components': ['some', 'path', 'to'], 'version_number': None},  #2
    {'components': ['some', 'path', 'to'], 'version_number': None},  #3
    {'components': ['some', 'path', 'to', 'a', 'file', 'v5', 'include.js'], 'file': 'include.js','file_extension': 'js', 'version_number': '5'},  # 4
    {'components': ['some', 'path', 'to', 'a', 'file', 'include-5.1.9.js'], 'file': 'include-5.1.9.js','file_extension': 'js', 'version_number': '5.1.9'},  # 5
    {'components': ['some', 'path', 'to', 'a', 'file', 'v5.1.8', 'include.xml'], 'file': 'include.xml','file_extension': 'xml', 'version_number': '5.1.8'},  # 6
    {'components': ['some', 'path', 'to', 'a', 'file5', 'include.xml'], 'file': 'include.xml','file_extension': 'xml', 'version_number': None},  # 6
]

TEST_SET_RAISE_ANALYZE_PATH_FROM_STR_INPUT = [
    "/some/path/to/a/file/v5.1.8/include.js/x/y/z/a/b/c/d/e/f/g/h/j/i/k/l/m/n/b/d/f/g/r/e/x"*10,
]

TEST_SET_ANALYZE_PATH_FROM_STR = zip(TEST_SET_ANALYZE_PATH_FROM_STR_INPUT, TEST_SET_ANALYZE_PATH_FROM_STR_RESULTS)
TEST_SET_RAISE_ANALYZE_PATH_FROM_STR = TEST_SET_RAISE_ANALYZE_PATH_FROM_STR_INPUT

TEST_GENERATORS = []

## Test generators
def test_gen_analyze_path():
    for parameters in TEST_SET_ANALYZE_PATH_FROM_STR:
        yield analyze_path_test, parameters[0], parameters[1]


TEST_GENERATORS.append(test_gen_analyze_path())

def test_gen_raise_analyze_path():
    for parameter in TEST_SET_RAISE_ANALYZE_PATH_FROM_STR:
        yield analyze_path_test_raise, parameter


TEST_GENERATORS.append(test_gen_raise_analyze_path())


## Test functions
@nottest
def analyze_path_test(input_, expected_result):
    result = nca_misc.analyze_path(input_)
    assert_dict_equal(result,expected_result)


@nottest
@raises(ValueError)
def analyze_path_test_raise(input_):
    print(input_)
    result = nca_misc.analyze_path(input_)


@nottest
def test_all():
    nca_util.test_all(TEST_GENERATORS)