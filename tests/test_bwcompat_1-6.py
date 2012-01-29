from support import TestCase
import typecheck.doctest_support

class TestSuite(TestCase):

    def testTypeCheckedDocstringGetsFoundByDoctest(self):
        import doctest
        import doctests

        finder = doctest.DocTestFinder(verbose=True)
        tests = finder.find(doctests)

        self.assertEquals(3, len(tests))

        runner = doctest.DocTestRunner(doctest.OutputChecker())

        for test in tests:
            runner.run(test)

        self.assertEquals(7, runner.summarize()[1])
        self.assertEquals(0, runner.summarize()[0])
