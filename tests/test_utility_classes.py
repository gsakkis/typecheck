from support import TestCase
import typecheck

def check_type(typ, obj):
    typecheck.check_type(typ, None, obj)

class Test_Or(TestCase):
    def setUp(self):
        from typecheck import Or

        def or_type(obj):
            check_type(Or(int, float), obj)

        self.or_type = or_type

    def test_IsOneOf_alias(self):
        from typecheck import Or, IsOneOf

        assert Or is IsOneOf

    def test_constructor(self):
        from typecheck import Or

        try:
            Or()
        except TypeError, e:
            assert str(e) == "__init__() takes at least 3 arguments (1 given)"
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_success(self):
        from typecheck import Or, And

        # Built-in types
        self.or_type(5)
        self.or_type(7.0)

        class A(object): pass # New-style classes
        class B: pass # Old-style classes
        class C(A, B): pass

        check_type(Or(A, B), C())
        check_type(Or(A, B), A())
        check_type(Or(A, B), B())

        # Nested extension classes
        check_type(Or(A, And(A, B)), C())

        # Complex-er types
        check_type(Or((int, int), [int, float]), (5, 6))

    def test_failure(self):
        from typecheck import _TC_TypeError, Or

        try:
            self.or_type("foo")
        except _TC_TypeError, e:
            assert repr(e.right) == repr(Or(int, float))
            assert e.wrong == str
        else:
            self.fail("Passed incorrectly")

class Test_And(TestCase):
    def test_IsAllOf_alias(self):
        from typecheck import And, IsAllOf

        assert And is IsAllOf

    def test_success(self):
        from typecheck import And

        class A: pass
        class B: pass
        class C(A, B): pass

        check_type(And(A, B), C())

    def test_failure(self):
        from typecheck import _TC_TypeError, And

        try:
            check_type(And(int, float), "foo")
        except _TC_TypeError, e:
            assert repr(e.right) == repr(And(int, float))
            assert e.wrong == str
        else:
            self.fail("Passed incorrectly")


class Test_Not(TestCase):
    def test_IsNoneOf_alias(self):
        from typecheck import Not, IsNoneOf

        assert Not is IsNoneOf

    def test_constructor(self):
        from typecheck import Not

        try:
            Not()
        except TypeError, e:
            assert str(e) == "__init__() takes at least 2 arguments (1 given)"
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_success(self):
        from typecheck import Not

        check_type(Not(int), 4.0)
        check_type(Not(int, float), 'four')

        class A: pass
        class B: pass
        class C: pass

        check_type(Not(A, B, int), C())

    def test_failure_1(self):
        from typecheck import _TC_TypeError, Not

        try:
            check_type(Not(int), 4)
        except _TC_TypeError, e:
            assert repr(e.right) == repr(Not(int))
            assert e.wrong == int
        else:
            self.fail("Passed incorrectly")

    def test_failure_2(self):
        from typecheck import _TC_TypeError, Not

        try:
            check_type(Not(int, float), 4.0)
        except _TC_TypeError, e:
            assert repr(e.right) == repr(Not(int, float))
            assert e.wrong == float
        else:
            self.fail("Passed incorrectly")

    def test_failure_3(self):
        from typecheck import _TC_TypeError, Not

        class A: pass
        class B: pass
        class C(A, B): pass

        try:
            check_type(Not(A, B, int), C())
        except _TC_TypeError, e:
            assert repr(e.right) == repr(Not(A, B, int))
            assert e.wrong == C
        else:
            self.fail("Passed incorrectly")

class Test_Any(TestCase):
    def test_args_and_return_pass(self):
        from typecheck import accepts, returns, Any

        def run_test(dec):
            @dec(Any())
            def foo(a):
                return a

            assert foo(foo) == foo
            assert foo(5) == 5
            assert foo(([], [], 5)) == ([], [], 5)

        run_test(accepts)
        run_test(returns)

    def test_yield_pass(self):
        from typecheck import yields, Any

        @yields(Any())
        def foo(a):
            yield a

        assert foo(5).next() == 5
        assert foo({}).next() == {}
        assert foo(foo).next() == foo

class Test_IsCallable(TestCase):
    def test_accepts_no_args(self):
        from typecheck import IsCallable

        try:
            IsCallable(5, 6, 7)
        except TypeError, e:
            assert str(e) == "__init__() takes exactly 1 argument (4 given)"
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_builtins(self):
        from typecheck import IsCallable

        check_type(IsCallable(), pow)

    def test_newstyle_classes(self):
        from typecheck import IsCallable

        class A(object):
            pass

        check_type(IsCallable(), A)

    def test_oldstyle_classes(self):
        from typecheck import IsCallable

        class A:
            pass

        check_type(IsCallable(), A)

    def test_userdefined_functions(self):
        from typecheck import IsCallable

        def foo(a):
            return a

        check_type(IsCallable(), foo)

    def test_callable_instances_newstyle(self):
        from typecheck import IsCallable

        class A(object):
            def __call__(self):
                pass

        check_type(IsCallable(), A())

    def test_callable_instances_oldstyle(self):
        from typecheck import IsCallable

        class A:
            def __call__(self):
                pass

        check_type(IsCallable(), A())

    def test_args_fail(self):
        from typecheck import accepts, IsCallable
        from typecheck import TypeCheckError, _TC_TypeError

        @accepts(IsCallable())
        def foo(a):
            return a

        try:
            foo(5)
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == 'a callable'
            assert e.internal.wrong == int

            self.assertEquals(str(e), "Argument a: for 5, expected a callable, got <type 'int'>")
        else:
            raise AssertionError("Failed to raise TypeCheckError")


class Test_HasAttr(TestCase):
    def test_empty(self):
        from typecheck import HasAttr

        try:
            HasAttr()
        except TypeError, e:
            self.assertEqual(str(e), "__init__() takes at least 2 arguments (1 given)")
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_success_named_only(self):
        from typecheck import HasAttr

        class A(object):
            def __init__(self):
                self.foo = 5
                self.bar = 6

        check_type(HasAttr(['foo', 'bar']), A())

    def test_success_typed_only(self):
        from typecheck import HasAttr

        class A(object):
            def __init__(self):
                self.foo = 5
                self.bar = 6

        check_type(HasAttr({'foo':int, 'bar':int}), A())

    def test_success_named_and_typed(self):
        from typecheck import HasAttr

        class A(object):
            def __init__(self):
                self.foo = 5
                self.bar = 6

        check_type(HasAttr(['foo'], {'bar': int}), A())
        check_type(HasAttr({'bar': int}, ['foo']), A())

    def test_failure_missing_attr(self):
        from typecheck import HasAttr, _TC_MissingAttrError

        class A(object):
            def __init__(self):
                self.foo = 5

            def __str__(self):
                return "A()"

        try:
            check_type(HasAttr(['foo', 'bar']), A())
        except _TC_MissingAttrError, e:
            assert e.attr == 'bar'
            self.assertEqual(e.error_message(), "missing attribute bar")
        else:
            raise AssertionError("Did not raise _TC_MissingAttrError")

    def test_failure_badly_typed_attr(self):
        from typecheck import HasAttr, _TC_AttrError, _TC_TypeError

        class A(object):
            def __init__(self):
                self.foo = 5
                self.bar = 7.0

            def __str__(self):
                return "A()"

        for args in ((['foo'], {'bar': int}), ({'bar': int}, ['foo'])):
            try:
                check_type(HasAttr(*args), A())
            except _TC_AttrError, e:
                assert e.attr == 'bar'
                assert isinstance(e.inner, _TC_TypeError)
                assert e.inner.right == int
                assert e.inner.wrong == float
                self.assertEqual(e.error_message(), "as for attribute bar, expected <type 'int'>, got <type 'float'>")
            else:
                raise AssertionError("Did not raise _TC_AttrError")

class Test_IsIterable(TestCase):
    def test_accepts_no_args(self):
        from typecheck import IsIterable

        try:
            IsIterable(5, 6, 7)
        except TypeError, e:
            assert str(e) == "__init__() takes exactly 1 argument (4 given)"
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_success_builtins(self):
        from typecheck import IsIterable

        for t in (list, tuple, set, dict):
            check_type(IsIterable(), t())

    def test_success_generator(self):
        from typecheck import IsIterable

        def foo():
            yield 5
            yield 6

        check_type(IsIterable(), foo())

    def test_success_user_newstyle(self):
        from typecheck import IsIterable

        class A(object):
            def __iter__(self):
                yield 5
                yield 6

        class B(object):
            def __iter__(self):
                return self

            def next(self):
                return 5

        for c in (A, B):
            check_type(IsIterable(), c())

    def test_success_user_oldstyle(self):
        from typecheck import IsIterable

        class A:
            def __iter__(self):
                yield 5
                yield 6

        class B:
            def __iter__(self):
                return self

            def next(self):
                return 5

        for c in (A, B):
            check_type(IsIterable(), c())

    def test_failure(self):
        from typecheck import IsIterable, _TC_TypeError

        class A(object):
            def __str__(self):
                return "A()"

        try:
            check_type(IsIterable(), A())
        except _TC_TypeError, e:
            assert e.right == "an iterable"
            assert e.wrong == A
        else:
            raise AssertionError("Failed to raise _TC_TypeError")


class Test_YieldSeq(TestCase):
    def test_bad_seq(self):
        from typecheck import YieldSeq

        try:
            YieldSeq()
        except TypeError, e:
            self.assertEqual(str(e), "__init__() takes at least 3 arguments (1 given)")
        else:
            raise AssertionError("Did not raise TypeError")

        try:
            YieldSeq(int)
        except TypeError, e:
            self.assertEqual(str(e), "__init__() takes at least 3 arguments (2 given)")
        else:
            raise AssertionError("Did not raise TypeError")

    def test_success(self):
        from typecheck import YieldSeq, yields

        @yields(int, YieldSeq(int, int, float))
        def foo(const, seq):
            for o in seq:
                yield (const, o)

        const = 5
        seq = [5, 6, 7.0]
        g = foo(const, seq)

        for obj in seq:
            assert g.next() == (const, obj)

    def test_nested_success(self):
        from typecheck import YieldSeq, yields

        @yields(YieldSeq(float, str, str))
        def bar(seq):
            for o in seq:
                yield o

        @yields(YieldSeq(float, str, str), YieldSeq(int, int, float))
        def foo(seq_1, seq_2):
            g = bar(seq_1)

            for o in seq_2:
                yield (g.next(), o)

        seq_1 = [7.0, "i", "i"]
        seq_2 = [5, 6, 7.0]
        g = foo(seq_1, seq_2)

        for tup in zip(seq_1, seq_2):
            assert g.next() == tup

    def test_parallel_success(self):
        from typecheck import YieldSeq, yields

        @yields(int, YieldSeq(int, int, float))
        def foo(const, seq):
            for o in seq:
                yield (const, o)

        const = 5
        seq = [5, 6, 7.0]
        g = foo(const, seq)
        h = foo(const, seq)

        for _ in seq:
            assert g.next() == h.next()

    def test_failure_1(self):
        from typecheck import YieldSeq, yields
        from typecheck import TypeCheckError, _TC_GeneratorError
        from typecheck import _TC_TypeError

        @yields(YieldSeq(int, int, float))
        def foo():
            yield 5
            yield 7.0

        g = foo()
        assert g.next() == 5

        try:
            g.next()
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_GeneratorError)
            assert e.internal.yield_no == 2
            assert isinstance(e.internal.inner, _TC_TypeError)
            assert e.internal.inner.right == int
            assert e.internal.inner.wrong == float
            self.assertEqual(str(e), "At yield #2: for 7.0, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Did not raise TypeCheckError")

    def test_failure_2(self):
        from typecheck import YieldSeq, yields
        from typecheck import TypeCheckError, _TC_GeneratorError
        from typecheck import _TC_YieldCountError

        @yields(YieldSeq(int, float))
        def foo():
            yield 5
            yield 7.0
            yield 8.0

        g = foo()
        assert g.next() == 5
        assert g.next() == 7.0

        try:
            g.next()
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_GeneratorError)
            assert e.internal.yield_no == 3
            assert isinstance(e.internal.inner, _TC_YieldCountError)
            assert e.internal.inner.expected == 2
            self.assertEqual(str(e), "At yield #3: only expected the generator to yield 2 times")
        else:
            raise AssertionError("Did not raise TypeCheckError")

class Test_Xor(TestCase):
    def test_IsOnlyOneOf_alias(self):
        from typecheck import Xor, IsOnlyOneOf

        assert Xor is IsOnlyOneOf

    def test_no_parameters(self):
        from typecheck import Xor

        try:
            Xor()
        except TypeError, e:
            self.assertEqual(str(e), "__init__() takes at least 3 arguments (1 given)")
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_success(self):
        from typecheck import Xor, IsCallable

        check_type(Xor(dict, IsCallable()), pow)
        check_type(Xor(dict, IsCallable()), {'a': 5})

    def test_failure_matched_no_conditions(self):
        from typecheck import Xor, IsIterable
        from typecheck import _TC_XorError, _TC_TypeError

        try:
            check_type(Xor(dict, IsIterable()), 5)
        except _TC_XorError, e:
            assert e.matched_conds == 0
            assert isinstance(e.inner, _TC_TypeError)
            assert repr(e.inner.right) == repr(Xor(dict, IsIterable()))
            assert e.inner.wrong == int
            self.assertEqual(e.error_message(), ", expected Xor(<type 'dict'>, IsIterable()), got <type 'int'> (matched neither assertion)")
        else:
            raise AssertionError("Failed to raise _TC_TypeError")

    def test_failure_matched_both_conditions(self):
        from typecheck import Xor, IsIterable
        from typecheck import _TC_XorError, _TC_TypeError

        try:
            check_type(Xor(dict, IsIterable()), {'a': 5})
        except _TC_XorError, e:
            assert e.matched_conds == 2
            assert isinstance(e.inner, _TC_TypeError)
            assert repr(e.inner.right) == repr(Xor(dict, IsIterable()))
            assert e.inner.wrong == {str: int}
            self.assertEqual(e.error_message(), ", expected Xor(<type 'dict'>, IsIterable()), got {<type 'str'>: <type 'int'>} (matched both assertions)")
        else:
            raise AssertionError("Failed to raise _TC_TypeError")

class Test_Exact(TestCase):
    def test_constructor(self):
        from typecheck import Exact

        try:
            Exact()
        except TypeError, e:
            assert str(e) == "__init__() takes exactly 2 arguments (1 given)"
        else:
            raise AssertionError("Failed to raise TypeError")

        try:
            Exact(4, 5)
        except TypeError, e:
            assert str(e) == "__init__() takes exactly 2 arguments (3 given)"
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_pass(self):
        from typecheck import Exact, Or

        for obj in (5, [5, 6], Exact, Or(int, float)):
            check_type(Exact(obj), obj)

    def test_fail_1(self):
        from typecheck import Exact, _TC_ExactError

        try:
            check_type(Exact(5), 6)
        except _TC_ExactError, e:
            assert e.wrong == 6
            assert e.right == 5
        else:
            raise AssertionError("Failed to raise _TC_ExactError")

    def test_fail_2(self):
        from typecheck import Exact, _TC_ExactError

        try:
            check_type(Exact(Exact), Exact(5))
        except _TC_ExactError, e:
            assert repr(e.right) == repr(Exact)
            assert repr(e.wrong) == repr(Exact(5))
        else:
            raise AssertionError("Failed to raise _TC_ExactError")

    def test_fail_3(self):
        from typecheck import Exact, TypeAnnotation, _TC_ExactError

        try:
            check_type(Exact(TypeAnnotation), Exact)
        except _TC_ExactError, e:
            assert repr(e.right) == repr(TypeAnnotation)
            assert repr(e.wrong) == repr(Exact)
        else:
            raise AssertionError("Failed to raise _TC_ExactError")

    def test_combined(self):
        from typecheck import Exact, Or

        or_type = Or(Exact(5), Exact(6), Exact(7))

        for num in (5, 6, 7):
            check_type(or_type, num)

class Test_Class(TestCase):

    def test_no_class(self):
        from typecheck import Class, accepts

        ClassB = Class("ClassB")

        @accepts(ClassB)
        def foo(a):
            return a

        try:
            foo(5)
        except NameError, e:
            self.assertEqual(str(e), "name 'ClassB' is not defined")
        else:
            raise AssertionError("Failed to raise NameError")

    def test_success(self):
        from typecheck import Class, accepts, Self

        ClassB = Class("ClassB")

        class ClassA(object):
            @accepts(Self(), ClassB)
            def foo(self, a):
                return a

        class ClassB(object):
            @accepts(Self(), ClassA)
            def foo(self, a):
                return a

        ClassA().foo(ClassB())
        ClassB().foo(ClassA())

    def test_failure(self):
        from typecheck import Class, accepts, Self
        from typecheck import TypeCheckError, _TC_TypeError

        ClassB = Class("ClassB")

        class ClassA(object):
            @accepts(Self(), ClassB)
            def foo(self, a):
                return a

        class ClassB(object):
            @accepts(Self(), ClassA)
            def foo(self, a):
                return a

        try:
            ClassA().foo(ClassA())
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TypeError)
            assert e.internal.right == ClassB
            assert e.internal.wrong == ClassA
        else:
            raise AssertionError("Failed to raise TypeCheckError")

class Test_Typeclass(TestCase):
    def test_no_args(self):
        from typecheck import Typeclass

        try:
            Typeclass()
        except TypeError:
            pass
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_instances_1(self):
        from typecheck import Typeclass

        tc = Typeclass(list, tuple, set)
        instances = tc.instances()

        assert isinstance(instances, list)
        assert len(instances) == 3
        assert list in instances
        assert tuple in instances
        assert set in instances

    def test_instances_2(self):
        from typecheck import Typeclass

        tc = Typeclass(list, tuple, Typeclass(str, unicode))
        instances = tc.instances()

        assert isinstance(instances, list)
        assert len(instances) == 4
        assert list in instances
        assert tuple in instances
        assert str in instances
        assert unicode in instances

    def test_has_instance(self):
        from typecheck import Typeclass

        tc = Typeclass(list, tuple)

        assert tc.has_instance(list)
        assert tc.has_instance(tuple)
        assert not tc.has_instance(set)

        tc.add_instance(set)

        assert tc.has_instance(set)

    def test_interface(self):
        from typecheck import Typeclass

        tc = Typeclass(list, tuple, set)
        interface = tc.interface()

        for method in interface:
            for t in (list, tuple, set):
                assert callable(getattr(t, method))

        for method in ('__class__', '__init__', '__new__', '__doc__'):
            assert method not in interface

    def test_pass(self):
        from typecheck import Typeclass

        tc = Typeclass(list, set)

        # These are a no-brainer
        check_type(tc, list)
        check_type(tc, set)

        check_type(tc, tuple)

        # XXX Does tuple get added to the instances list?
        # assert tuple in tc.instances()

    def test_fail_1(self):
        from typecheck import Typeclass, _TC_AttrError, _TC_TypeError
        from typecheck import IsCallable

        class A(object):
            def foo(self):
                pass

        class B(object):
            def foo(self):
                pass

            def bar(self):
                pass

        class C(object):
            def __init__(self):
                self.foo = 5

        tc = Typeclass(A, B)

        try:
            check_type(tc, C())
        except _TC_AttrError, e:
            assert e.attr == 'foo'
            assert isinstance(e.inner, _TC_TypeError)
            assert repr(e.inner.right) == repr(IsCallable())
            assert e.inner.wrong == int
        else:
            raise AssertionError("Failed to raise _TC_AttrError")

    def test_fail_2(self):
        from typecheck import Typeclass, _TC_MissingAttrError

        class A(object):
            def foo(self):
                pass

        class B(object):
            def foo(self):
                pass

            def bar(self):
                pass

        class C(object):
            pass

        tc = Typeclass(A, B)

        try:
            check_type(tc, C())
        except _TC_MissingAttrError, e:
            assert e.attr == 'foo'
        else:
            raise AssertionError("Failed to raise _TC_MissingAttrError")

    def test_add_instance(self):
        from typecheck import Typeclass

        tc = Typeclass(list, set, tuple)
        interface_before = tc.interface()

        tc.add_instance(dict)

        # Adding an instance shouldn't chance the interface...
        assert interface_before == tc.interface()

        # but it should change the instances list
        assert dict in tc.instances()

    def test_intersect_1(self):
        # Make sure .intersect works on other Typeclass instances
        from typecheck import Typeclass

        tc_int = Typeclass(int)
        tc_flt = Typeclass(float)

        interface_int = set(tc_int.interface())
        interface_flt = set(tc_flt.interface())
        merged_intfc = interface_int.intersection(interface_flt)

        tc_int.intersect(tc_flt)

        for t in (int, float):
            assert tc_int.has_instance(t)

        for method in merged_intfc:
            assert method in tc_int.interface()

    def test_intersect_2(self):
        # Make sure .intersect works on all iterables
        from typecheck import Typeclass

        tc_int = Typeclass(int)
        tc_flt = Typeclass(float)

        interface_int = set(tc_int.interface())
        interface_flt = set(tc_flt.interface())
        merged_intfc = interface_int.intersection(interface_flt)

        def run_test(itr_type):
            tc_int.intersect(itr_type([float]))

            for t in (int, float):
                assert tc_int.has_instance(t)

            for method in merged_intfc:
                assert method in tc_int.interface()

        def gen(seq):
            for o in seq:
                yield o

        for itr_type in (tuple, list, set, gen):
            run_test(itr_type)

    def test_cope_with_class_changes(self):
        from typecheck import Typeclass, _TC_AttrError, _TC_TypeError
        from typecheck import IsCallable

        class A(object):
            def foo(self): pass

        class B(object):
            def foo(self): pass

        tc = Typeclass(A)
        b = B()

        # Should pass
        check_type(tc, b)

        B.foo = 5

        # B is still cached as known-good
        check_type(tc, b)

        tc.recalculate_interface()

        try:
            check_type(tc, b)
        except _TC_AttrError, e:
            assert e.attr == 'foo'
            assert isinstance(e.inner, _TC_TypeError)
            assert repr(e.inner.right) == repr(IsCallable())
            assert e.inner.wrong == int
        else:
            raise AssertionError("Failed to raise _TC_AttrError")
