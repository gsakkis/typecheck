from support import TestCase

class UnorderedIteratorMixinTests(TestCase):
    def setUp(self):
        from typecheck.mixins import UnorderedIteratorMixin
        from typecheck import accepts

        self.UIM = UnorderedIteratorMixin("MyIterator")
        class MyIterator(self.UIM):
            def __init__(self, *values):
                self.__values = values

            def __iter__(self):
                index = 0
                while index < len(self.__values):
                    yield self.__values[index]
                    index += 1
                raise StopIteration

            def __str__(self):
                return "MyIterator" + str(tuple(self.__values))

        @accepts(MyIterator(int, float))
        def foo(itr):
            pass

        self.Iter = MyIterator
        self.foo = foo

    def tearDown(self):
        from typecheck import unregister_type

        unregister_type(self.UIM)

    def test_used_by_Type(self):
        from typecheck import Type
        from typecheck.mixins import _UnorderedIteratorMixin

        uim = Type(self.Iter(float, int))
        assert isinstance(uim, _UnorderedIteratorMixin)

    def test_success(self):
        MyIter = self.Iter
        foo = self.foo

        foo(MyIter(5, 6, 6.0, 7, 8.0, 9.0))

    def test_failure(self):
        from typecheck import TypeCheckError, Or
        from typecheck import _TC_TypeError
        from typecheck.mixins import _TC_IterationError

        MyIter = self.Iter
        foo = self.foo

        try:
            foo(MyIter(5, 6, 9.0, 4, 'four'))
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_IterationError)
            assert e.internal.iteration == 4
            assert isinstance(e.internal.inner, _TC_TypeError)
            assert e.internal.inner.right == Or(int, float)
            assert e.internal.inner.wrong == str
            self.assertEqual(str(e), "Argument itr: for MyIterator(5, 6, 9.0, 4, 'four'), at iteration 4 (value: 'four'), expected Or(<type 'float'>, <type 'int'>), got <type 'str'>")
        else:
            raise AssertionError("Succeeded incorrectly")
