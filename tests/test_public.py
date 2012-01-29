import sys
import types
from support import TestCase
import typecheck
from typecheck import Set


def check_type(typ, obj):
    typecheck.check_type(typ, None, obj)

class Test_returns(TestCase):
    def test_success_1(self):
        from typecheck import returns

        @returns(int, int, int)
        def foo():
            return 5, 6, 7

        assert foo() == (5, 6, 7)
        assert foo.type_return == (int, int, int)

    def test_success_2(self):
        from typecheck import returns

        @returns([int])
        def foo():
            return [4, 5, 6]

        assert foo() == [4, 5, 6]
        assert foo.type_return == [int]

    def test_success_3(self):
        from typecheck import returns

        @returns([int], int, str)
        def foo():
            return [4, 5, 6], 5, "foo"

        assert foo() == ([4, 5, 6], 5, "foo")
        assert foo.type_return == ([int], int, str)

    def test_success_4(self):
        from typecheck import returns

        @returns(int)
        def foo():
            return 7

        assert foo() == 7
        assert foo.type_return == int

    def test_success_5(self):
        from typecheck import returns

        @returns((int,))
        def foo():
            return (7,)

        assert foo() == (7,)
        assert foo.type_return == (int,)

    def test_failure_1(self):
        from typecheck import returns, TypeCheckError, _TC_TypeError

        @returns(int, int, int)
        def foo():
            return 5, 6

        assert foo.type_return == (int, int, int)

        try:
            foo()
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == (int, int, int)
            assert e.internal.wrong == (int, int)
            self.assertEqual(str(e), "Return value: for (5, 6), expected (<type 'int'>, <type 'int'>, <type 'int'>), got (<type 'int'>, <type 'int'>)")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_2(self):
        from typecheck import returns, TypeCheckError
        from typecheck import _TC_TypeError, _TC_IndexError

        @returns([int])
        def foo():
            return [4, 5, 6.0]

        assert foo.type_return == [int]

        try:
            foo()
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_IndexError)
            assert e.internal.index == 2
            assert isinstance(e.internal.inner, _TC_TypeError)
            assert e.internal.inner.wrong == float
            assert e.internal.inner.right == int
            self.assertEqual(str(e), "Return value: for [4, 5, 6.0], at index 2, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_3(self):
        from typecheck import returns, TypeCheckError
        from typecheck import _TC_TypeError, _TC_IndexError

        @returns([int], int, str)
        def foo():
            return [4, 5, 6], 5, ["foo"]

        assert foo.type_return == ([int], int, str)

        try:
            foo()
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_IndexError)
            assert e.internal.index == 2
            assert isinstance(e.internal.inner, _TC_TypeError)
            assert e.internal.inner.wrong == [str]
            assert e.internal.inner.right == str
            self.assertEqual(str(e), "Return value: for ([4, 5, 6], 5, ['foo']), at index 2, expected <type 'str'>, got [<type 'str'>]")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_4(self):
        from typecheck import returns, TypeCheckError, _TC_TypeError

        @returns((int,))
        def foo():
            return 7

        assert foo.type_return == (int,)

        try:
            foo()
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == (int,)
            assert e.internal.wrong == int
            self.assertEqual(str(e), "Return value: for 7, expected (<type 'int'>,), got <type 'int'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_decorator_returns_function(self):
        from typecheck import returns

        @returns((int,))
        def foo():
            return 7

        assert isinstance(foo, types.FunctionType)

class Test_yields(TestCase):
    def test_pass(self):
        from typecheck import yields

        @yields(int)
        def foo(a):
            yield a
            yield a + 1
            yield a + 2

        gen = foo(5)

        assert gen.next() == 5
        assert gen.next() == 6
        assert gen.next() == 7

        assert foo.type_yield == int
        assert gen.type_yield == foo.type_yield

        try:
            gen.next()
        except StopIteration:
            pass
        else:
            raise AssertionError("Failed to raise the proper exception")

    def test_fail(self):
        from typecheck import yields, TypeCheckError
        from typecheck import _TC_GeneratorError, _TC_TypeError

        @yields(int)
        def foo(a):
            yield a

        gen = foo(5.0)

        assert foo.type_yield == int
        assert gen.type_yield == foo.type_yield

        try:
            gen.next()
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_GeneratorError)
            assert e.internal.yield_no == 1
            assert isinstance(e.internal.inner, _TC_TypeError)
            assert e.internal.inner.right == int
            assert e.internal.inner.wrong == float
            self.assertEqual(str(e), "At yield #1: for 5.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            raise AssertionError("Failed to raise the proper exception")

    def test_restartable(self):
        from typecheck import yields

        @yields(int)
        def foo(a):
            yield a
            yield a + 1
            yield a + 2

        assert foo.type_yield == int
        assert foo(5).type_yield == foo.type_yield

        for _ in (1, 2):
            gen = foo(5)

            assert gen.type_yield == foo.type_yield

            assert gen.next() == 5
            assert gen.next() == 6
            assert gen.next() == 7

            try:
                gen.next()
            except StopIteration:
                pass
            else:
                raise AssertionError("Failed to raise the proper exception")

    def test_fails_on_non_generators(self):
        from typecheck import yields

        @yields(int)
        def foo(a):
            return a + 1

        try:
            assert foo(5) == 6
        except TypeError, e:
            self.assertEqual(str(e), "yields only works for generators")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_decorator_returns_function(self):
        from typecheck import yields

        @yields(int)
        def foo():
            yield 7

        assert isinstance(foo, types.FunctionType)

class Test_accepts(TestCase):
    def test_success_single_positional(self):
        from typecheck import accepts

        @accepts(int)
        def foo(int_1):
            return int_1

        assert foo(6) == 6

        assert foo.type_args == {'int_1': int}

    def test_success_multiple_positional(self):
        from typecheck import accepts

        @accepts(int, int, int)
        def foo(int_1, int_2, int_3):
            return int_1, int_2, int_3

        assert foo(1, 2, 3) == (1, 2, 3)
        assert foo.type_args == {'int_1': int, 'int_2': int, 'int_3': int}

    def test_success_multiple_positional_type_by_kw(self):
        from typecheck import accepts

        @accepts(int_2=int, int_1=int, int_3=int)
        def foo(int_1, int_2, int_3):
            return int_1, int_2, int_3

        assert foo(1, 2, 3) == (1, 2, 3)

        assert foo.type_args == {'int_1': int, 'int_2': int, 'int_3': int}

    def test_success_multiple_keyword(self):
        from typecheck import accepts

        @accepts(kw_1=int, kw_2=int, kw_3=int)
        def foo(kw_1=5, kw_2=6, kw_3=7):
            return (kw_1, kw_2, kw_3)

        assert foo() == (5, 6, 7)
        assert foo(9, 9, 9) == (9, 9, 9)
        assert foo(kw_1=33, kw_3=88) == (33, 6, 88)
        assert foo(kw_3=55, kw_2=2) == (5, 2, 55)

        assert foo.type_args == {'kw_1': int, 'kw_2': int, 'kw_3': int}

    def test_success_multiple_keyword_type_by_pos(self):
        from typecheck import accepts

        # Checking type-specification, not arg-passing
        @accepts(int, int, int)
        def foo(kw_1=5, kw_2=6, kw_3=7):
            return (kw_1, kw_2, kw_3)

        assert foo() == (5, 6, 7)
        assert foo(9, 9, 9) == (9, 9, 9)
        assert foo(kw_1=33, kw_3=88) == (33, 6, 88)
        assert foo(kw_3=55, kw_2=2) == (5, 2, 55)

        assert foo.type_args == {'kw_1': int, 'kw_2': int, 'kw_3': int}

    def test_success_kwargs_form_1(self):
        from typecheck import accepts

        # Type can be passed as a single type...
        # (in this case, the values of the dict
        # will be checked against the given type)
        @accepts(kwargs=int)
        def foo(**kwargs):
            return kwargs

        assert foo() == {}
        assert foo(int_1=5, int_2=8) == {'int_1': 5, 'int_2': 8}

        assert foo.type_args == {'kwargs': {str: int}}

    def test_success_kwargs_form_2(self):
        from typecheck import accepts

        # ...or in normal dict form
        # (in this case, full checking is done)
        @accepts(kwargs={str: int})
        def foo(**kwargs):
            return kwargs

        assert foo() == {}
        assert foo(int_1=5, int_2=8) == {'int_1': 5, 'int_2': 8}

        assert foo.type_args == {'kwargs': {str: int}}

    def test_success_vargs_form_1(self):
        from typecheck import accepts

        # Type can be passed as a single type...
        @accepts(vargs=int)
        def foo(*vargs):
            return vargs

        assert foo() == ()
        assert foo(5, 8) == (5, 8)

        assert foo.type_args == {'vargs': [int]}

    def test_success_vargs_form_2(self):
        from typecheck import accepts

        # ...or as an actual tuple. Note that
        # this form is useful if you want to
        # specify patterned tuples
        @accepts(vargs=[int])
        def foo(*vargs):
            return vargs

        assert foo() == ()
        assert foo(5, 8) == (5, 8)

        assert foo.type_args == {'vargs': [int]}

    def test_success_pos_and_kw(self):
        from typecheck import accepts

        @accepts(int, int, foo=int)
        def foo(req_1, req_2, foo=7):
            return (req_1, req_2, foo)

        assert foo(5, 6, foo=88) == (5, 6, 88)
        assert foo(5, 6) == (5, 6, 7)
        assert foo(foo=5, req_2=44, req_1=99) == (99, 44, 5)

        assert foo.type_args == {'req_1': int, 'req_2': int, 'foo': int}

    def test_success_unpacked_tuples(self):
        from typecheck import accepts

        @accepts(int, (int, (int, int)), int)
        def foo(req_1, (req_2, (req_3, req_4)), req_5):
            return (req_1, req_2, req_3, req_4, req_5)

        assert foo(4, (5, (6, 7)), 8) == (4, 5, 6, 7, 8)

        assert foo.type_args == {'req_1': int, ('req_2', ('req_3', 'req_4')): (int, (int, int)), 'req_5': int}

    def test_failure_single_positional(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(int)
        def foo(int_1):
            return 7

        assert foo.type_args == {'int_1': int}

        try:
            foo(6.0)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument int_1: for 6.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_multiple_positional_1(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(int, int, int)
        def foo(int_1, int_2, int_3):
            return 7

        assert foo.type_args == {'int_1': int, 'int_2': int, 'int_3': int}

        try:
            foo(1, 2, 3.0)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument int_3: for 3.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_multiple_positional_2(self):
        from typecheck import accepts

        @accepts(int, int)
        def foo(a, b):
            return a, b

        try:
            foo(3)
        except TypeError, e:
            assert str(e) == "foo() takes exactly 2 arguments (1 given)"
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_failure_multiple_positional_type_by_kw(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(int_2=int, int_1=int, int_3=int)
        def foo(int_1, int_2, int_3):
            return 7

        assert foo.type_args == {'int_1': int, 'int_2': int, 'int_3': int}

        try:
            foo(1, 2, 3.0)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument int_3: for 3.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_multiple_keyword_1(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(kw_1=int, kw_2=int, kw_3=int)
        def foo(kw_1=5, kw_2=6, kw_3=7):
            return (kw_1, kw_2, kw_3)

        assert foo.type_args == {'kw_1': int, 'kw_2': int, 'kw_3': int}

        try:
            foo(9.0, 9, 9)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument kw_1: for 9.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_multiple_keyword_2(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(kw_1=int, kw_2=int, kw_3=int)
        def foo(kw_1=5, kw_2=6, kw_3=7):
            return (kw_1, kw_2, kw_3)

        assert foo.type_args == {'kw_1': int, 'kw_2': int, 'kw_3': int}

        try:
            foo(kw_1=9.0, kw_3=88)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument kw_1: for 9.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Failed to raise TypeCheckError")

    def test_failure_multiple_keyword_3(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(kw_1=int, kw_2=int, kw_3=int)
        def foo(kw_1=5, kw_2=6, kw_3=7):
            return (kw_1, kw_2, kw_3)

        assert foo.type_args == {'kw_1': int, 'kw_2': int, 'kw_3': int}

        try:
            foo(kw_3=9.0, kw_1=88)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument kw_3: for 9.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Failed to raise TypeCheckError")

    def test_failure_multiple_keyword_type_by_pos_1(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(int, int, int)
        def foo(kw_1=5, kw_2=6, kw_3=7):
            return (kw_1, kw_2, kw_3)

        assert foo.type_args == {'kw_1':int, 'kw_2': int, 'kw_3': int}

        try:
            foo(9.0, 9, 9)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument kw_1: for 9.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_multiple_keyword_type_by_pos_2(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(int, int, int)
        def foo(kw_1=5, kw_2=6, kw_3=7):
            return (kw_1, kw_2, kw_3)

        assert foo.type_args == {'kw_1':int, 'kw_2': int, 'kw_3': int}

        try:
            foo(kw_1=9.0, kw_3=88)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument kw_1: for 9.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_multiple_keyword_type_by_pos_3(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(int, int, kw_3=int)
        def foo(kw_1=5, kw_2=6, kw_3=7):
            return (kw_1, kw_2, kw_3)

        assert foo.type_args == {'kw_1':int, 'kw_2': int, 'kw_3': int}

        try:
            foo(kw_3=9.0, kw_1=88)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument kw_3: for 9.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_kwargs_form_1(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError, _TC_KeyValError

        # Type can be passed as a single type...
        # (in this case, the values of the dict
        # will be checked against the given type)
        @accepts(kwargs=int)
        def foo(**kwargs):
            return kwargs

        assert foo.type_args == {'kwargs': {str: int}}

        try:
            foo(int_1=5.0, int_2=8)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_KeyValError)
            assert e.internal.key == 'int_1'
            assert e.internal.val == 5.0
            assert isinstance(e.internal.inner, _TC_TypeError)
            assert e.internal.inner.right == int
            assert e.internal.inner.wrong == float
            self.assertEqual(str(e), "Argument kwargs: for {'int_1': 5.0, 'int_2': 8}, at key 'int_1', value 5.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_kwargs_form_2(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError, _TC_KeyValError

        # ...or in normal dict form
        # (in this case, full checking is done)
        @accepts(kwargs={str: int})
        def foo(**kwargs):
            return kwargs

        assert foo.type_args == {'kwargs': {str: int}}

        try:
            foo(int_1=5.0, int_2=8)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_KeyValError)
            assert e.internal.key == 'int_1'
            assert e.internal.val == 5.0
            assert isinstance(e.internal.inner, _TC_TypeError)
            assert e.internal.inner.right == int
            assert e.internal.inner.wrong == float
            self.assertEqual(str(e), "Argument kwargs: for {'int_1': 5.0, 'int_2': 8}, at key 'int_1', value 5.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_vargs_form_1(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError, _TC_IndexError

        # Type can be passed as a single type...
        @accepts(vargs=int)
        def foo(*vargs):
            return vargs

        assert foo.type_args == {'vargs': [int]}

        try:
            foo(5, 8.0)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_IndexError)
            assert e.internal.index == 1
            assert isinstance(e.internal.inner, _TC_TypeError)
            assert e.internal.inner.right == int
            assert e.internal.inner.wrong == float
            self.assertEqual(str(e), "Argument vargs: for [5, 8.0], at index 1, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_vargs_form_2(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError, _TC_IndexError

        # ...or as an actual list. Note that
        # this form is useful if you want to
        # specify patterned lists
        @accepts(vargs=[int])
        def foo(*vargs):
            return vargs

        assert foo.type_args == {'vargs': [int]}

        try:
            foo(5, 8.0)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_IndexError)
            assert e.internal.index == 1
            assert isinstance(e.internal.inner, _TC_TypeError)
            assert e.internal.inner.right == int
            assert e.internal.inner.wrong == float
            self.assertEqual(str(e), "Argument vargs: for [5, 8.0], at index 1, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_pos_and_kw_1(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(int, int, foo=int)
        def foo(req_1, req_2, foo=7):
            return (req_1, req_2, foo)

        assert foo.type_args == {'foo': int, 'req_1':int, 'req_2': int}

        try:
            foo(5, 6.0, foo=88)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument req_2: for 6.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_pos_and_kw_2(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(int, int, foo=int)
        def foo(req_1, req_2, foo=7):
            return (req_1, req_2, foo)

        assert foo.type_args == {'foo': int, 'req_1':int, 'req_2': int}

        try:
            foo(5, 6, foo=88.0)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument foo: for 88.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_pos_and_kw_3(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(int, int, foo=int)
        def foo(req_1, req_2, foo=7):
            return (req_1, req_2, foo)

        assert foo.type_args == {'foo': int, 'req_1':int, 'req_2': int}

        try:
            foo(foo=5, req_2=44, req_1=99.0)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument req_1: for 99.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_unpacked_tuples_1(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_IndexError, _TC_TypeError

        @accepts(int, (int, (int, int)), int)
        def foo(a, (b, (c, d)), e):
            return a, b, c, d, e

        assert foo.type_args == {'a': int, ('b', ('c', 'd')): (int, (int, int)), 'e': int}

        try:
            foo(5, (6, (7, 8.0)), 9)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_IndexError)
            assert e.internal.index == 1
            assert isinstance(e.internal.inner, _TC_IndexError)
            assert e.internal.inner.index == 1
            assert isinstance(e.internal.inner.inner, _TC_TypeError)
            assert e.internal.inner.inner.right == int
            assert e.internal.inner.inner.wrong == float
            self.assertEqual(str(e), "Argument (b, (c, d)): for (6, (7, 8.0)), at index 1, at index 1, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_unpacked_tuples_2(self):
        from typecheck import accepts

        @accepts(int, (int, (int, int)), int)
        def foo(a, (b, (c, d)), e):
            return a, b, c, d, e

        assert foo.type_args == {'a': int, ('b', ('c', 'd')): (int, (int, int)), 'e': int}

        try:
            foo(5, (6, 4), 9)
        except TypeError, e:
            if sys.version_info[:2] >= (2, 5):
                self.assertEqual(str(e), "'int' object is not iterable")
            else:
                self.assertEqual(str(e), "unpack non-sequence")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_failure_unpacked_tuples_3(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(int, (int, (int, int)), int)
        def foo(a, (b, (c, d)), e):
            return a, b, c, d, e

        assert foo.type_args == {'a': int, ('b', ('c', 'd')): (int, (int, int)), 'e': int}

        try:
            foo(5, (6, (7, 8)), (9, 10))
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == (int, int)
            self.assertEqual(str(e), "Argument e: for (9, 10), expected <type 'int'>, got (<type 'int'>, <type 'int'>)")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_generators_pass(self):
        from typecheck import accepts

        @accepts(int)
        def foo(a):
            yield a
            yield a + 1
            yield a + 2

        gen = foo(5)

        assert gen.next() == 5
        assert gen.next() == 6
        assert gen.next() == 7

        assert foo.type_args == {'a': int}

    def test_generators_fail(self):
        from typecheck import accepts, TypeCheckError
        from typecheck import _TC_TypeError

        @accepts(int)
        def foo(a):
            yield a
            yield a + 1
            yield a + 2

        assert foo.type_args == {'a': int}

        try:
            foo(5.0)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == int
            assert e.internal.wrong == float
            self.assertEqual(str(e), "Argument a: for 5.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_bad_signature_missing_pos(self):
        from typecheck import accepts, TypeSignatureError
        from typecheck import _TS_MissingTypeError

        try:
            @accepts(int, int, int)
            def foo(a, b, c, e):
                return a, b, c, e
        except TypeSignatureError, e:
            assert isinstance(e.internal, _TS_MissingTypeError)
            assert e.internal.parameter == 'e'
            self.assertEqual(str(e), "parameter 'e' lacks a type")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_bad_signature_missing_kw(self):
        from typecheck import accepts, TypeSignatureError
        from typecheck import _TS_MissingTypeError

        try:
            @accepts(a=int, b=int, c=int)
            def foo(a=5, b=6, c=7, d=8):
                return a, b, c, d
        except TypeSignatureError, e:
            assert isinstance(e.internal, _TS_MissingTypeError)
            assert e.internal.parameter == 'd'
            self.assertEqual(str(e), "parameter 'd' lacks a type")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_bad_signature_duplicate_kw(self):
        from typecheck import accepts, TypeSignatureError
        from typecheck import _TS_TwiceTypedError

        try:
            @accepts(int, a=int, b=int, c=int)
            def foo(a=5, b=6, c=7):
                return a, b, c
        except TypeSignatureError, e:
            assert isinstance(e.internal, _TS_TwiceTypedError)
            assert e.internal.parameter == 'a'
            assert e.internal.kw_type == int
            assert e.internal.pos_type == int
            self.assertEqual(str(e), "parameter 'a' is provided two types (<type 'int'> and <type 'int'>)")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_bad_signature_extra_pos(self):
        from typecheck import accepts, TypeSignatureError
        from typecheck import _TS_ExtraPositionalError

        try:
            @accepts(int, int, int, int)
            def foo(a, b, c):
                return a, b, c
        except TypeSignatureError, e:
            assert isinstance(e.internal, _TS_ExtraPositionalError)
            assert e.internal.type == int
            self.assertEqual(str(e), "an extra positional type has been supplied")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_bad_signature_extra_kw(self):
        from typecheck import accepts, TypeSignatureError
        from typecheck import _TS_ExtraKeywordError

        try:
            @accepts(a=int, b=int, c=int)
            def foo(a=5, b=6):
                return a, b
        except TypeSignatureError, e:
            assert isinstance(e.internal, _TS_ExtraKeywordError)
            assert e.internal.keyword == 'c'
            self.assertEqual(str(e), "the keyword 'c' in the signature is not in the function")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_bad_signature_unpack_nonsequence(self):
        from typecheck import accepts, TypeSignatureError
        from typecheck import _TS_TupleError

        try:
            @accepts(int, int)
            def foo(a, (b, c)):
                return a, b, c
        except TypeSignatureError, e:
            assert isinstance(e.internal, _TS_TupleError)
            assert e.internal.parameters == ('b', 'c')
            assert e.internal.types == int
            self.assertEqual(str(e), "the signature type <type 'int'> does not match ('b', 'c')")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_bad_signature_unpack_bad_sequence_1(self):
        from typecheck import accepts, TypeSignatureError
        from typecheck import _TS_TupleError

        try:
            @accepts(int, (int, int, int))
            def foo(a, (b, c)):
                return a, b, c
        except TypeSignatureError, e:
            assert isinstance(e.internal, _TS_TupleError)
            assert e.internal.parameters == ('b', 'c')
            assert e.internal.types == (int, int, int)
            self.assertEqual(str(e), "the signature type (<type 'int'>, <type 'int'>, <type 'int'>) does not match ('b', 'c')")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_bad_signature_unpack_bad_sequence_2(self):
        from typecheck import accepts, TypeSignatureError
        from typecheck import _TS_TupleError

        try:
            @accepts(int, (int, int))
            def foo(a, (b, c, d)):
                return a, b, c, d
        except TypeSignatureError, e:
            assert isinstance(e.internal, _TS_TupleError)
            assert e.internal.parameters == ('b', 'c', 'd')
            assert e.internal.types == (int, int)
            self.assertEqual(str(e), "the signature type (<type 'int'>, <type 'int'>) does not match ('b', 'c', 'd')")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_bad_signature_unpack_bad_sequence_3(self):
        from typecheck import accepts, TypeSignatureError
        from typecheck import _TS_TupleError

        try:
            @accepts(int, (int, (int, int), (int, int)))
            def foo(a, (b, (c, d, e), (f, g))):
                return a, b, c, d, e, f, g
        except TypeSignatureError, e:
            assert isinstance(e.internal, _TS_TupleError)
            assert e.internal.parameters == ('b', ('c', 'd', 'e'), ('f', 'g'))
            assert e.internal.types == (int, (int, int), (int, int))
            self.assertEqual(str(e), "the signature type (<type 'int'>, (<type 'int'>, <type 'int'>), (<type 'int'>, <type 'int'>)) does not match ('b', ('c', 'd', 'e'), ('f', 'g'))")
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_decorator_returns_function(self):
        from typecheck import accepts

        @accepts(int)
        def foo(a):
            return 7

        assert isinstance(foo, types.FunctionType)

class SetTests(TestCase):
    def test_empty_list(self):
        Set([])

    def test_success_basic(self):
        check_type(Set([int]), set([4, 5, 6, 4, 5, 6]))

    def test_success_mutlitypes(self):
        check_type(Set([int, float]), set([4, 5.0, 6, 4, 5, 6.0]))

    def test_success_nested(self):
        from typecheck import Or

        check_type(Set([(int, int)]), set([(4, 5), (6, 7)]))

        check_type(Set([Or(int, float)]), set([4, 4.0, 5, 5.0]))

    def test_success_empty(self):
        check_type(Set([]), set())

    def test_failure_empty(self):
        from typecheck import _TC_LengthError

        try:
            check_type(Set([]), set([4, 5, 6]))
        except _TC_LengthError, e:
            assert e.right == 0
            assert e.wrong == 3
        else:
            raise AssertionError("Failed to raise _TC_LengthError")

    def test_failure(self):
        from typecheck import _TC_KeyError, _TC_TypeError

        try:
            check_type(Set([int]), set([4, 5, 6.0]))
        except _TC_KeyError, e:
            assert e.key == 6.0
            assert isinstance(e.inner, _TC_TypeError)
            assert e.inner.right == int
            assert e.inner.wrong == float
        else:
            raise AssertionError("Did not raise the proper exception")

    def test_failure_multitypes(self):
        from typecheck import Or, _TC_KeyError, _TC_TypeError

        try:
            check_type(Set([int, float]), set([4, 5, 6.0, 's']))
        except _TC_KeyError, e:
            assert e.key == 's'
            assert isinstance(e.inner, _TC_TypeError)
            assert e.inner.right == Or(int, float)
            assert e.inner.wrong == str
        else:
            raise AssertionError("Did not raise the proper exception")

    def test_failure_nested(self):
        from typecheck import _TC_KeyError, _TC_TypeError

        try:
            check_type(Set([(int, int)]), set([(4, 5), (4, 6.0)]))
        except _TC_KeyError, e:
            assert e.key == (4, 6.0)
            assert isinstance(e.inner, _TC_TypeError)
            assert e.inner.right == (int, int)
            assert e.inner.wrong == (int, float)
        else:
            raise AssertionError("Did not raise the proper exception")

    def test_equality(self):
        class A(object): pass
        class B(A): pass

        eq_tests = [
            (Set([str]), Set([str])),
            (Set([A, B]), Set([A, B])),
            (Set([]), Set([])),
            (Set([int, int, str]), Set([int, str])),
            (Set([int, str]), Set([str, int])),
            (Set([Set([int, float]), int]), Set([Set([float, int]), int])),
            (Set([Set([int, str]), Set([int, str])]), Set([Set([int, str])])) ]

        ne_tests = [
            (Set([A, B]), Set([B, B])),
            (Set([A, B]), Set([A, A])),
            (Set([]), Set([int, int])),
            (Set([Set([int, str])]), Set([Set([Set([int, str])])])),
            (Set([int, int]), set([int, int])) ]

        self.multipleAssertEqual(eq_tests, ne_tests)

    def test_hash(self):
        class A(object): pass
        class B(A): pass

        eq_tests = [
            (Set([str]), Set([str])),
            (Set([A, B]), Set([A, B])),
            (Set([]), Set([])),
            (Set([int, int, str]), Set([int, str])),
            (Set([int, str]), Set([str, int])),
            (Set([Set([int, float]), int]), Set([Set([float, int]), int])),
            (Set([Set([int, str]), Set([int, str])]), Set([Set([int, str])])) ]

        ne_tests = [
            (Set([A, B]), Set([B, B])),
            (Set([A, B]), Set([A, A])),
            (Set([]), Set([int, int])),
            (Set([Set([int, str])]), Set([Set([Set([int, str])])])) ]

        self.multipleAssertEqualHashes(eq_tests, ne_tests)

    def test_Type_uses_it(self):
        from typecheck import Type

        t = Type(set([int, float]))
        assert isinstance(t, Set)

class Test_cooperation(TestCase):
    def test_args_pass_return_pass(self):
        from typecheck import accepts, returns

        def run_test(dec_1, dec_2):
            @dec_1(int, int)
            @dec_2(int, int)
            def foo(a, b):
                return a, b

            assert foo(5, 6) == (5, 6)

            assert foo.type_return == (int, int)
            assert foo.type_args == {'a': int, 'b': int}

        run_test(accepts, returns)
        run_test(returns, accepts)

    def test_args_pass_return_fail(self):
        from typecheck import accepts, returns
        from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError

        def run_test(dec_1, dec_2):
            @dec_1(int, int)
            @dec_2(int, int)
            def foo(a, b):
                return a, float(b)

            assert foo.type_return == (int, int)
            assert foo.type_args == {'a': int, 'b': int}

            try:
                foo(5, 6)
            except TypeCheckError, e:
                assert isinstance(e.internal, _TC_IndexError)
                assert e.internal.index == 1
                assert isinstance(e.internal.inner, _TC_TypeError)
                assert e.internal.inner.right == int
                assert e.internal.inner.wrong == float
                self.assertEqual(str(e), "Return value: for (5, 6.0), at index 1, expected <type 'int'>, got <type 'float'>")
            else:
                raise AssertionError("Succeeded incorrectly")

        run_test(accepts, returns)
        run_test(returns, accepts)

    def test_args_return_builds_function(self):
        from typecheck import accepts, returns

        def run_test(dec_1, dec_2):
            @dec_1(int, int)
            @dec_2(int, int)
            def foo(a, b):
                return a, float(b)

            assert isinstance(foo, types.FunctionType)

        run_test(accepts, returns)
        run_test(returns, accepts)

    def test_args_pass_yield_pass(self):
        from typecheck import accepts, yields

        def run_test(dec_1, dec_2):
            @dec_1(int, int)
            @dec_2(int, int)
            def foo(a, b):
                yield a, b
                yield a + 1, b
                yield a, b + 1

            assert foo.type_yield == (int, int)
            assert foo.type_args == {'a': int, 'b': int}

            gen = foo(5, 6)
            assert gen.next() == (5, 6)
            assert gen.next() == (6, 6)
            assert gen.next() == (5, 7)

            assert gen.type_yield == foo.type_yield

            try:
                gen.next()
            except StopIteration:
                pass
            else:
                raise AssertionError("Failed to raise the proper exception")

        run_test(accepts, yields)
        run_test(yields, accepts)

    def test_args_pass_yield_fail(self):
        from typecheck import accepts, yields
        from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError
        from typecheck import _TC_GeneratorError

        def run_test(dec_1, dec_2):
            @dec_1(int, int)
            @dec_2(int, int)
            def foo(a, b):
                yield a, b
                yield a, float(b)

            assert foo.type_yield == (int, int)
            assert foo.type_args == {'a': int, 'b': int}

            gen = foo(5, 6)
            assert gen.type_yield == foo.type_yield
            assert gen.next() == (5, 6)

            try:
                gen.next()
            except TypeCheckError, e:
                assert isinstance(e.internal, _TC_GeneratorError)
                assert e.internal.yield_no == 2
                assert isinstance(e.internal.inner, _TC_IndexError)
                assert e.internal.inner.index == 1
                assert isinstance(e.internal.inner.inner, _TC_TypeError)
                assert e.internal.inner.inner.right == int
                assert e.internal.inner.inner.wrong == float
                self.assertEqual(str(e), "At yield #2: for (5, 6.0), at index 1, expected <type 'int'>, got <type 'float'>")
            else:
                raise AssertionError("Succeeded incorrectly")

            try:
                gen.next()
            except StopIteration:
                pass
            else:
                raise AssertionError("Failed to raise the proper exception")

        run_test(accepts, yields)
        run_test(yields, accepts)

    def test_args_yield_builds_function(self):
        from typecheck import accepts, yields

        def run_test(dec_1, dec_2):
            @dec_1(int, int)
            @dec_2(int, int)
            def foo(a, b):
                yield a, float(b)

            assert isinstance(foo, types.FunctionType)

        run_test(accepts, yields)
        run_test(yields, accepts)

    def __test_doubler(self, decorator):
        try:
            @decorator(int, int)
            @decorator(int, int)
            def foo(a, b):
                return a, b
        except RuntimeError, e:
            self.assertEqual(str(e), 'Cannot use the same typecheck_* function more than once on the same function')
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_double_accepts(self):
        from typecheck import accepts

        self.__test_doubler(accepts)

    def test_double_returns(self):
        from typecheck import returns

        self.__test_doubler(returns)

    def test_double_yields(self):
        from typecheck import yields

        self.__test_doubler(yields)

    def test_return_and_yield(self):
        from typecheck import yields, returns

        try:
            @yields(int, int)
            @returns(int, int)
            def foo(a, b):
                return a, b
        except RuntimeError, e:
            self.assertEqual(str(e), 'Cannot use returns and yields on the same function')
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_no_double_execution_return(self):
        from typecheck import accepts, returns

        def double_execution(dec_1, dec_2):
            # We need to make sure that the function only gets executed once,
            # even if it's wrapped by two decorators
            usage_counter = [0]

            @dec_1(int)
            @dec_2(int)
            def foo(a):
                usage_counter[0] += 1

                return a

            assert foo(5) == 5
            assert usage_counter[0] == 1

        double_execution(accepts, returns)
        double_execution(returns, accepts)

    def test_no_double_execution_yield(self):
        from typecheck import accepts, yields

        def double_execution(dec_1, dec_2):
            # We need to make sure that the function only gets executed once,
            # even if it's wrapped by two decorators
            usage_counter = [0]

            @dec_1(int)
            @dec_2(int)
            def foo(a):
                usage_counter[0] += 1

                yield a

            gen = foo(5)
            assert gen.next() == 5
            assert usage_counter[0] == 1

            try:
                gen.next()
            except StopIteration:
                pass
            else:
                raise AssertionError("Failed to raise the proper exception")

        double_execution(accepts, yields)
        double_execution(yields, accepts)

    def test_verify_args_checked_first__return(self):
        from typecheck import accepts, returns
        from typecheck import TypeCheckError, _TC_TypeError

        def run_test(dec_1, dec_2):
            @dec_1
            @dec_2
            def foo(a, b):
                return 'a'

            try:
                assert foo(5.0, 6.0) == 5.0
            except TypeCheckError, e:
                assert isinstance(e.internal, _TC_TypeError)
                assert e.internal.right == int
                assert e.internal.wrong == float
                self.assertEqual(str(e), "Argument a: for 5.0, expected <type 'int'>, got <type 'float'>")
            else:
                raise AssertionError("Failed to raise the proper exception")

        run_test(accepts(int, int), returns(float))
        run_test(returns(float), accepts(int, int))

    def test_verify_args_checked_first__yield(self):
        from typecheck import accepts, yields
        from typecheck import TypeCheckError, _TC_TypeError

        def run_test(dec_1, dec_2):
            @dec_1
            @dec_2
            def foo(a, b):
                yield 'a'

            try:
                assert foo(5.0, 6.0).next() == 5.0
            except TypeCheckError, e:
                assert isinstance(e.internal, _TC_TypeError)
                assert e.internal.right == int
                assert e.internal.wrong == float
                self.assertEqual(str(e), "Argument a: for 5.0, expected <type 'int'>, got <type 'float'>")
            else:
                raise AssertionError("Failed to raise the proper exception")

        run_test(accepts(int, int), yields(float))
        run_test(yields(float), accepts(int, int))

class Test_Self_class(TestCase):
    def test_self_in_args_pass(self):
        from typecheck import accepts, Self

        class Test(object):
            @accepts(Self(), int, Self())
            def foo(self, a, b):
                return a, b

        t = Test()
        assert Test().foo(4, t) == (4, t)

        assert Test.foo.type_args == {'self': Self(), 'a': int, 'b': Self()}

    def test_self_in_args_fail(self):
        from typecheck import accepts, Self, TypeCheckError
        from typecheck import _TC_TypeError

        class Test(object):
            @accepts(Self(), int, Self())
            def foo(self, a, b):
                return a, b

        assert Test.foo.type_args == {'self': Self(), 'a': int, 'b': Self()}

        try:
            assert Test().foo(4, 6) == (4, 6)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.wrong == int
            assert e.internal.right == Test
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_self_in_return_pass(self):
        from typecheck import returns, Self

        class Test(object):
            @returns(Self(), int, Self())
            def foo(self, a, b):
                return self, a, b

        t = Test()
        t_1 = Test()
        assert t_1.foo(4, t) == (t_1, 4, t)

        assert Test.foo.type_return == (Self(), int, Self())

    def test_self_in_return_fail(self):
        from typecheck import returns, Self, TypeCheckError
        from typecheck import _TC_IndexError, _TC_TypeError

        class Test(object):
            @returns(Self(), int, Self())
            def foo(self, a, b):
                return self, a, b

        try:
            t = Test()
            assert t.foo(4, 6) == (t, 4, 6)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_IndexError)
            assert e.internal.index == 2
            assert isinstance(e.internal.inner, _TC_TypeError)
            assert e.internal.inner.wrong == int
            assert e.internal.inner.right == Test
        else:
            raise AssertionError("Succeeded incorrectly")

        assert Test.foo.type_return == (Self(), int, Self())

    def test_self_in_yield_pass(self):
        from typecheck import yields, Self

        class Test(object):
            @yields(Self(), int, Self())
            def foo(self, a, b):
                yield self, a, self

        t = Test()
        assert t.foo(4, 6).next() == (t, 4, t)
        assert Test.foo.type_yield == (Self(), int, Self())

    def test_self_in_args_yield_pass(self):
        from typecheck import yields, Self
        from typecheck import accepts

        class Test(object):
            @accepts(Self(), int, int)
            @yields(Self(), int, Self())
            def foo(self, a, b):
                yield self, a, self

        t = Test()
        assert t.foo(4, 6).next() == (t, 4, t)

        assert Test.foo.type_yield == (Self(), int, Self())
        assert Test.foo.type_args == {'self': Self(), 'a': int, 'b': int}

    def test_self_in_args_yield_fail(self):
        from typecheck import yields, Self, TypeCheckError
        from typecheck import _TC_IndexError, _TC_TypeError
        from typecheck import _TC_GeneratorError, accepts

        class Test(object):
            @accepts(Self(), int, int)
            @yields(Self(), int, Self())
            def foo(self, a, b):
                yield b, a, b

        assert Test.foo.type_yield == (Self(), int, Self())
        assert Test.foo.type_args == {'self': Self(), 'a': int, 'b': int}

        try:
            assert Test().foo(4, 6).next() == (6, 4, 6)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_GeneratorError)
            assert e.internal.yield_no == 1
            assert isinstance(e.internal.inner, _TC_IndexError)
            assert e.internal.inner.index == 0
            assert isinstance(e.internal.inner.inner, _TC_TypeError)
            assert e.internal.inner.inner.wrong == int
            assert e.internal.inner.inner.right == Test
        else:
            raise AssertionError("Succeeded incorrectly")

class Test_enable_checking_global(TestCase):
    def tearDown(self):
        typecheck.enable_checking = True

    def test_accepts(self):
        from typecheck import accepts, TypeCheckError

        @accepts(int)
        def foo(a):
            return a

        typecheck.enable_checking = True
        assert foo(5) == 5

        typecheck.enable_checking = False
        assert foo(5.0) == 5.0

        typecheck.enable_checking = True
        try:
            assert foo(5.0) == 5.0
        except TypeCheckError:
            pass # We don't need to look at this
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_returns(self):
        from typecheck import returns, TypeCheckError

        @returns(int)
        def foo(a):
            return a

        typecheck.enable_checking = True
        assert foo(5) == 5

        typecheck.enable_checking = False
        assert foo(5.0) == 5.0

        typecheck.enable_checking = True
        try:
            assert foo(5.0) == 5.0
        except TypeCheckError:
            pass # We don't need to look at this
        else:
            raise AssertionError("Succeeded incorrectly")

    def test_yields(self):
        from typecheck import yields, TypeCheckError

        @yields(int)
        def foo(a):
            yield a

        typecheck.enable_checking = True
        gen = foo(5)
        assert gen.next() == 5
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            raise AssertionError("Failed to raise the proper exception")

        typecheck.enable_checking = False
        gen = foo(5.0)
        assert gen.next() == 5.0
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            raise AssertionError("Failed to raise the proper exception")

        typecheck.enable_checking = True
        gen = foo(5.0)
        try:
            assert gen.next() == 5.0
        except TypeCheckError:
            pass # We don't need to look at this
        else:
            raise AssertionError("Succeeded incorrectly")
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            raise AssertionError("Failed to raise the proper exception")

class Test_signature_checking_hooks(TestCase):
    def setUp(self):
        from typecheck import register_type

        flags = {'start': [], 'stop': []}

        appender_reg = {}

        def appender(flag, function):
            if isinstance(function, types.GeneratorType):
                if function.gi_frame is not None:
                    appender_reg[function] = function.gi_frame.f_code.co_name

                flags[flag].append("gen_%s" % appender_reg[function])
            else:
                flags[flag].append(function.__name__)

        class Test(object):
            @classmethod
            def __typesig__(cls, obj):
                pass

            # This is invoked when we start checking the function
            @classmethod
            def __startchecking__(cls, function):
                appender('start', function)

            @classmethod
            def __switchchecking__(cls, from_func, to_func):
                appender('stop', from_func)
                appender('start', to_func)

            # This is invoked when we stop checking the function
            @classmethod
            def __stopchecking__(cls, function):
                appender('stop', function)

        register_type(Test)
        self.Test = Test
        self.flags = flags

    def tearDown(self):
        from typecheck import is_registered_type, unregister_type

        if is_registered_type(self.Test):
            unregister_type(self.Test)

    def __test_single(self, decorator):
        @decorator(int)
        def foo(a):
            return a

        assert foo(5) == 5

        assert self.flags['start'] == ['foo']
        assert self.flags['stop'] == ['foo']

    def test_args(self):
        from typecheck import accepts

        self.__test_single(accepts)

    def test_return(self):
        from typecheck import returns

        self.__test_single(returns)

    def test_yield(self):
        from typecheck import yields

        @yields(int)
        def foo(a):
            yield a

        gen = foo(5)
        assert self.flags['start'] == ['foo', 'gen_foo']
        assert self.flags['stop'] == ['foo']

        assert gen.next() == 5
        assert self.flags['start'] == ['foo' , 'gen_foo']
        assert self.flags['stop'] == ['foo']
        try:
            gen.next()
        except StopIteration:
            assert self.flags['start'] == ['foo' , 'gen_foo']
            assert self.flags['stop'] == ['foo', 'gen_foo']
        else:
            raise AssertionError("Failed to raise StopIteration at the right point")

    def test_args_return(self):
        from typecheck import returns, accepts

        def test_double(dec_1, dec_2):
            self.flags['start'] = []
            self.flags['stop'] = []

            @dec_1(int)
            @dec_2(int)
            def foo(a):
                return a

            assert foo(5) == 5

            assert self.flags['start'] == ['foo']
            assert self.flags['stop'] == ['foo']

        test_double(returns, accepts)
        test_double(accepts, returns)

    def test_args_yield(self):
        from typecheck import yields, accepts

        def test_double(dec_1, dec_2):
            self.flags['start'] = []
            self.flags['stop'] = []

            @dec_1(int)
            @dec_2(int)
            def foo(a):
                yield a

            gen = foo(5)
            assert self.flags['start'] == ['foo', 'gen_foo']
            assert self.flags['stop'] == ['foo']

            assert gen.next() == 5
            assert self.flags['start'] == ['foo', 'gen_foo']
            assert self.flags['stop'] == ['foo']
            try:
                gen.next()
            except StopIteration:
                assert self.flags['start'] == ['foo', 'gen_foo']
                assert self.flags['stop'] == ['foo', 'gen_foo']
            else:
                raise AssertionError("Failed to raise StopIteration at the right point")

        test_double(yields, accepts)
        test_double(accepts, yields)

    def test_handles_exceptions_return(self):
        from typecheck import returns, accepts

        def test_double(dec_1, dec_2):
            self.flags['start'] = []
            self.flags['stop'] = []

            @dec_1(int)
            @dec_2(int)
            def foo(a):
                raise RuntimeError()

            try:
                assert foo(5) == 5
            except RuntimeError:
                pass
            else:
                raise AssertionError("Failed to allow RuntimeError through")

            assert self.flags['start'] == ['foo']
            assert self.flags['stop'] == ['foo']

        test_double(returns, accepts)
        test_double(accepts, returns)

    def test_handles_exceptions_yield(self):
        from typecheck import yields, accepts

        def test_double(dec_1, dec_2):
            self.flags['start'] = []
            self.flags['stop'] = []

            @dec_1(int)
            @dec_2(int)
            def foo(a):
                yield a
                raise RuntimeError()

            gen = foo(5)
            assert self.flags['start'] == ['foo', 'gen_foo']
            assert self.flags['stop'] == ['foo']

            assert gen.next() == 5
            assert self.flags['start'] == ['foo', 'gen_foo']
            assert self.flags['stop'] == ['foo']
            try:
                gen.next()
            except RuntimeError:
                # Note that gen_foo hasn't stopped checking yet
                assert self.flags['start'] == ['foo', 'gen_foo']
                assert self.flags['stop'] == ['foo']
            else:
                raise AssertionError("Failed to raise RuntimeError at the right point")

            try:
                gen.next()
            except StopIteration:
                assert self.flags['start'] == ['foo', 'gen_foo']
                assert self.flags['stop'] == ['foo', 'gen_foo']
            else:
                raise AssertionError("Failed to raise StopIteration at the right point")

        test_double(yields, accepts)
        test_double(accepts, yields)

    def test_nested_functions(self):
        from typecheck import returns, accepts

        def test_double(dec_1, dec_2):
            self.flags['start'] = []
            self.flags['stop'] = []

            @dec_1(int)
            @dec_2(int)
            def bar(a):
                return a

            @dec_1(int)
            @dec_2(int)
            def foo(a):
                return bar(a)

            assert foo(5) == 5

            assert self.flags['start'] == ['foo', 'bar']
            assert self.flags['stop'] == ['bar', 'foo']

        test_double(returns, accepts)
        test_double(accepts, returns)

    def test_nested_functions_with_exceptions(self):
        from typecheck import returns, accepts

        def test_double(dec_1, dec_2):
            self.flags['start'] = []
            self.flags['stop'] = []

            @dec_1(int)
            @dec_2(int)
            def bar(a):
                raise RuntimeError()

            @dec_1(int)
            @dec_2(int)
            def foo(a):
                return bar(a)

            assert foo(5) == 5

        for dec_1, dec_2 in ((returns, accepts),
                             (accepts, returns)):
            try:
                test_double(dec_1, dec_2)
            except RuntimeError:
                assert self.flags['start'] == ['foo', 'bar']
                assert self.flags['stop'] == ['bar', 'foo']
            else:
                raise AssertionError("Failed to raise the proper exception")

    def test_incorrect_generator_usage(self):
        from typecheck import yields

        @yields(int)
        def foo():
            yield 5

        def contain_scope():
            assert foo().next() == 5

        for i in range(1, 3):
            contain_scope()
            assert self.flags['start'] == ['foo', 'gen_foo'] * i
            assert self.flags['stop'] == ['foo', 'gen_foo'] * i

# We inherit everything else from Test_signature_checking_hooks
class Test_hooks_ignore_enable_checking(Test_signature_checking_hooks):
    def setUp(self):
        Test_signature_checking_hooks.setUp(self)
        typecheck.enable_checking = False

    def tearDown(self):
        Test_signature_checking_hooks.tearDown(self)
        typecheck.enable_checking = True
