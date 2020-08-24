# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import map
from builtins import str as text
from future import standard_library
standard_library.install_aliases()
import logging
from nose.tools import assert_true

TEST_ALL_LOGGING = logging.info


def test_all(generator_list):
    for _gen in generator_list:
        for _test in _gen():
            f = _test[0]
            params = _test[1:]
            if not TEST_ALL_LOGGING is None:
                TEST_ALL_LOGGING(u"-- running test %s (%s)\n" % (f.__name__, ', '.join(map(text, params))))
            f(*params)