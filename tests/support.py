import unittest
import sys
import os.path
import time

def _strclass(cls):
    return "%s.%s" % (cls.__module__, cls.__name__)

def run_all_tests(test_mod=None, tests=None):
    if tests is None:
        tests = unittest.TestLoader().loadTestsFromModule(test_mod)
    unittest.TextTestRunner(verbosity=2).run(tests)

def adjust_path():
    parent_dir = os.path.split(sys.path[0])[0]
    sys.path = [parent_dir] + sys.path

TestCase = unittest.TestCase

### The following are some convenience functions used throughout the test
### suite

def test_equality(eq_tests, ne_tests, repeats=10):
    eq_error = "Problem with __eq__ with %s and %s"
    ne_error = "Problem with __ne__ with %s and %s"

    # We run this multiple times to try and shake out any errors
    # related to differences in set/dict/etc ordering
    for _ in xrange(0, repeats):
        for (left, right) in eq_tests:
            try:
                assert left == right
            except AssertionError:
                raise AssertionError(eq_error % (left, right))

            try:
                assert not left != right
            except AssertionError:
                raise AssertionError(ne_error % (left, right))

        for (left, right) in ne_tests:
            try:
                assert left != right
            except AssertionError:
                raise AssertionError(ne_error % (left, right))

            try:
                assert not left == right
            except AssertionError:
                raise AssertionError(eq_error % (left, right))

def test_hash(eq_tests, ne_tests, repeats=10):
    hash_error = "Problem with hash() with %s and %s"

    # We run this multiple times to try and shake out any errors
    # related to differences in set/dict/etc ordering
    for _ in xrange(0, repeats):
        for (left, right) in eq_tests:
            try:
                assert hash(left) == hash(right)
            except AssertionError:
                raise AssertionError(hash_error % (left, right))

        for (left, right) in ne_tests:
            try:
                assert hash(left) != hash(right)
            except AssertionError:
                raise AssertionError(hash_error % (left, right))
