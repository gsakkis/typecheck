import unittest

class TestCase(unittest.TestCase):

    def multipleAssertEqual(self, eq_tests, ne_tests, repeats=10):
        # We run this multiple times to try and shake out any errors
        # related to differences in set/dict/etc ordering
        for _ in xrange(0, repeats):
            for left, right in eq_tests:
                self.assertTrue(left == right)
                self.assertFalse(left != right)
            for left, right in ne_tests:
                self.assertTrue(left != right)
                self.assertFalse(left == right)

    def multipleAssertEqualHashes(self, eq_tests, ne_tests, repeats=10):
        # We run this multiple times to try and shake out any errors
        # related to differences in set/dict/etc ordering
        for _ in xrange(0, repeats):
            for left, right in eq_tests:
                self.assertTrue(hash(left) == hash(right))
            for left, right in ne_tests:
                self.assertTrue(hash(left) != hash(right))
