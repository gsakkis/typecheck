from support import TestCase
from examples import Empty, Length, PatternList, _TC_LengthError
import typecheck

def check_type(typ, to_check):
    typecheck.check_type(typ, None, to_check)

class TypeCheckedTree(TestCase):
    def setUp(self):
        from typecheck import accepts, register_type
        from typecheck import _TC_Exception, Type
        from typecheck import _TC_NestedError, _TC_TypeError

        class _TC_TreeChildTypeError(_TC_NestedError):
            def __init__(self, child, inner_exception):
                _TC_NestedError.__init__(self, inner_exception)

                self.child = child

            def error_message(self):
                return ("in the %s child" % self.child) + _TC_NestedError.error_message(self)

        class TreeType(object):
            def __init__(self, val):
                self._type = Type(val)
                self.type = self

            def __typecheck__(self, func, to_check):
                if not isinstance(to_check, Tree):
                    raise _TC_TypeError(to_check, self._type)

                try:
                    typecheck.check_type(self._type, func, to_check.val)
                except _TC_Exception:
                    raise _TC_TypeError(to_check.val, self._type.type)

                for side in ('right', 'left'):
                    child = getattr(to_check, side)
                    if child is not None:
                        try:
                            typecheck.check_type(self, func, child)
                        except _TC_Exception, e:
                            raise _TC_TreeChildTypeError(side, e)

            @classmethod
            def __typesig__(cls, obj):
                if isinstance(obj, cls):
                    return obj

            def __str__(self):
                return "Tree(%s)" % str(self._type)

            __repr__ = __str__

        class Tree(object):
            def __init__(self, val, left=None, right=None):
                self.val = val
                self.left = left
                self.right = right

            def __str__(self):
                if self.left is None and self.right is None:
                    return "Tree(%s)" % str(self.val)
                return "Tree(%s, %s, %s)" % (str(self.val), str(self.left), str(self.right))

            __repr__ = __str__

            @classmethod
            def __typesig__(cls, obj):
                if isinstance(obj, cls):
                    if obj.left is None and obj.right is None:
                        return TreeType(obj.val)

        register_type(Tree)
        register_type(TreeType)

        @accepts(Tree(int))
        def preorder(tree):
            l = [tree.val]
            if tree.left is not None:
                l.extend(preorder(tree.left))
            if tree.right is not None:
                l.extend(preorder(tree.right))

            return l

        self.Tree = Tree
        self.preorder = preorder
        self._TC_TreeChildTypeError = _TC_TreeChildTypeError

    def test_success(self):
        Tree = self.Tree
        preorder = self.preorder

        preorder(Tree(5, Tree(6), Tree(7)))

    def test_failure(self):
        from typecheck import TypeCheckError, _TC_TypeError

        Tree = self.Tree
        preorder = self.preorder
        _TC_TreeChildTypeError = self._TC_TreeChildTypeError

        try:
            preorder(Tree(5, Tree(6), Tree(7.0)))
        except TypeCheckError, e:
            assert isinstance(e.internal, _TC_TreeChildTypeError)
            assert e.internal.child == 'right'
            assert isinstance(e.internal.inner, _TC_TypeError)
            assert e.internal.inner.right == int
            assert e.internal.inner.wrong == float
            self.assertEqual(str(e), "Argument tree: for Tree(5, Tree(6), Tree(7.0)), in the right child, expected <type 'int'>, got <type 'float'>")
        else:
            raise AssertionError("Succeeded incorrectly")

# An example of Xor being implemented in terms of the included And, Not
# and Or utility classes
class XorCase(TestCase):
    def setUp(self):
        from typecheck import Or, And, Not

        def Xor(cond_1, cond_2):
            return Or(And(cond_1, Not(cond_2)), And(cond_2, Not(cond_1)))

        self.Xor = Xor

    def test_success(self):
        from typecheck import IsCallable

        check_type(self.Xor(dict, IsCallable()), pow)
        check_type(self.Xor(dict, IsCallable()), {'a': 5})

    def test_failure(self):
        from typecheck import IsIterable, _TC_TypeError

        for obj in (pow, {'a': 5}):
            try:
                check_type(self.Xor(dict, IsIterable()), obj)
            except _TC_TypeError:
                pass
            else:
                raise AssertionError("Failed to raise _TC_TypeError")

# An example of IsIterable being implemented in terms of HasAttr() and
# IsCallable()
class IsIterableCase(TestCase):
    def setUp(self):
        from typecheck import HasAttr, IsCallable

        def IsIterable():
            return HasAttr({'__iter__': IsCallable()})

        self.IsIterable = IsIterable

    def test_success_builtins(self):
        for t in (list, tuple, set, dict):
            check_type(self.IsIterable(), t())

    def test_success_generator(self):
        def foo():
            yield 5
            yield 6

        check_type(self.IsIterable(), foo())

    def test_success_user_newstyle(self):
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
            check_type(self.IsIterable(), c())

    def test_success_user_oldstyle(self):
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
            check_type(self.IsIterable(), c())

    def test_failure(self):
        from typecheck import _TC_MissingAttrError

        class A(object):
            def __str__(self):
                return "A()"

        try:
            check_type(self.IsIterable(), A())
        except _TC_MissingAttrError:
            pass
        else:
            raise AssertionError("Failed to raise _TC_MissingAttrError")

class Test_Length(TestCase):
    def test_constructor(self):
        try:
            Length()
        except TypeError, e:
            assert str(e) == "__init__() takes exactly 2 arguments (1 given)"
        else:
            raise AssertionError("Failed to raise TypeError")

        try:
            Length(4, 5)
        except TypeError, e:
            assert str(e) == "__init__() takes exactly 2 arguments (3 given)"
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_bad_argument(self):
        try:
            Length('abc')
        except ValueError:
            pass
        else:
            raise AssertionError("Failed to raise an exception")

    def test_equality(self):
        eq_tests = [(Length(4), Length(4)), (Length(4.0), Length(4))]
        ne_tests = [(Length(5), Length(4))]

        self.multipleAssertEqual(eq_tests, ne_tests)

    def test_hash(self):
        eq_tests = [(Length(4), Length(4)), (Length(4.0), Length(4))]
        ne_tests = [(Length(5), Length(4))]

        self.multipleAssertEqualHashes(eq_tests, ne_tests)

    def test_pass_builtins(self):
        for obj in ([4, 5], (6, 7), {5: 6, 7: 8}):
            check_type(Length(2), obj)

    def test_pass_userdef(self):
        class A(object):
            def __len__(self):
                return 5

        check_type(Length(5), A())

    def test_fail_1(self):
        try:
            check_type(Length(5), [6])
        except _TC_LengthError, e:
            assert e.wrong == 1
            assert e.right == 5
        else:
            raise AssertionError("Failed to raise _TC_LengthError")

    def test_fail_2(self):
        from typecheck import _TC_TypeError

        try:
            check_type(Length(5), 5)
        except _TC_TypeError, e:
            assert e.right == "something with a __len__ method"
            assert e.wrong == int
        else:
            raise AssertionError("Failed to raise _TC_TypeError")

    def test_combined(self):
        from typecheck import And

        and_type = And(Length(3), tuple)
        check_type(and_type, (5, 6, 7))

class Test_Empty(TestCase):
    def test_bad_constructor_1(self):
        try:
            Empty()
        except TypeError, e:
            self.assertEqual(str(e), "__init__() takes exactly 2 arguments (1 given)")
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_bad_constructor_2(self):
        try:
            Empty(dict, list)
        except TypeError, e:
            self.assertEqual(str(e), "__init__() takes exactly 2 arguments (3 given)")
        else:
            raise AssertionError("Failed to raise TypeError")

    def test_bad_empty_type(self):
        for t in (int, float):
            try:
                Empty(t)
            except TypeError:
                pass
            else:
                raise AssertionError("Failed to raise TypeError for %s" % t)

    def test_list_success(self):
        check_type(Empty(list), [])

    def test_list_failure(self):
        try:
            check_type(Empty(list), [5, 6])
        except _TC_LengthError, e:
            assert e.wrong == 2
            assert e.right == 0
        else:
            self.fail("Passed incorrectly")

    def test_dict_success(self):
        check_type(Empty(dict), {})

    def test_dict_failure(self):
        try:
            check_type(Empty(dict), {'f': 5})
        except _TC_LengthError, e:
            assert e.wrong == 1
            assert e.right == 0
        else:
            self.fail("Passed incorrectly")

    def test_set_success(self):
        check_type(Empty(set), set())

    def test_set_failure(self):
        try:
            check_type(Empty(set), set([5, 6]))
        except _TC_LengthError, e:
            assert e.wrong == 2
            assert e.right == 0
        else:
            self.fail("Passed incorrectly")

    def test_userdef_success(self):
        class A(object):
            def __len__(self):
                return 0

        check_type(Empty(A), A())

    def test_userdef_failure(self):
        class A(object):
            def __len__(self):
                return 2

        try:
            check_type(Empty(A), A())
        except _TC_LengthError, e:
            assert e.wrong == 2
            assert e.right == 0
        else:
            self.fail("Passed incorrectly")

    def test_inappropriate_type(self):
        from typecheck import _TC_TypeError

        for t in (dict, list, set):
            try:
                check_type(Empty(t), 5)
            except _TC_TypeError, e:
                assert e.right == t
                assert e.wrong == int
            else:
                raise AssertionError("Failed to raise _TC_TypeError")

    def test_equality(self):
        eq_tests = [
            (Empty(list), Empty(list)),
            (Empty(dict), Empty(dict)),
            (Empty(set), Empty(set)) ]

        ne_tests = [
            (Empty(list), Empty(dict)),
            (Empty(list), Empty(set)),
            (Empty(dict), Empty(list)),
            (Empty(dict), Empty(set)),
            (Empty(set), Empty(list)),
            (Empty(set), Empty(dict)), ]

        self.multipleAssertEqual(eq_tests, ne_tests)

    def test_hash(self):
        eq_tests = [
            (Empty(list), Empty(list)),
            (Empty(dict), Empty(dict)),
            (Empty(set), Empty(set)) ]

        ne_tests = [
            (Empty(list), Empty(dict)),
            (Empty(list), Empty(set)),
            (Empty(dict), Empty(set)) ]

        self.multipleAssertEqualHashes(eq_tests, ne_tests)

class PatternListTests(TestCase):
    def setUp(self):
        def lis(obj):
            check_type(PatternList(int, float), obj)

        self.list = lis

    def test_success(self):
        self.list([])
        self.list([ 4, 5.0 ])
        self.list([ 4, 5.0, 8, 9.0 ])
        self.list([ 4, 5.0, 9, 8.0, 4, 5.0 ])

    def test_index_failure(self):
        from typecheck import _TC_IndexError, _TC_TypeError

        try:
            # 5 is not a float
            self.list([4, 5, 6, 7.0])
        except _TC_IndexError, e:
            assert e.index == 1
            assert isinstance(e.inner, _TC_TypeError)
            assert e.inner.wrong == int
            assert e.inner.right == float
        else:
            self.fail("Passed incorrectly")

    def test_type_failure(self):
        from typecheck import _TC_TypeError

        try:
            self.list({ 'f': 4 })
        except _TC_TypeError, e:
            assert e.right == [int, float]
            assert e.wrong == {str: int}
        else:
            self.fail("Passed incorrectly")

    def test_equality(self):
        class A(object): pass
        class B(A): pass

        eq_tests = [
            (PatternList(str, str), PatternList(str, str)),
            (PatternList(A, B), PatternList(A, B)),
            (PatternList(PatternList(int, int), int), PatternList(PatternList(int, int), int)) ]

        ne_tests = [
            (PatternList(str, int), PatternList(int, str)),
            (PatternList(A, B), PatternList(B, B)),
            (PatternList(A, B), PatternList(A, A)),
            (PatternList(PatternList(int, int)), PatternList(PatternList(PatternList(int, int)))),
            (PatternList(int, int), PatternList(int, int, int)),
            (PatternList(int, int), [int, int]) ]

        self.multipleAssertEqual(eq_tests, ne_tests)

    def test_hash(self):
        class A(object): pass
        class B(A): pass

        eq_tests = [
            (PatternList(str, str), PatternList(str, str)),
            (PatternList(A, B), PatternList(A, B)),
            (PatternList(PatternList(int, int), int), PatternList(PatternList(int, int), int)) ]

        ne_tests = [
            (PatternList(str, int), PatternList(int, str)),
            (PatternList(A, B), PatternList(B, B)),
            (PatternList(A, B), PatternList(A, A)),
            (PatternList(PatternList(int, int)), PatternList(PatternList(PatternList(int, int)))),
            (PatternList(int, int), PatternList(int, int, int)) ]

        self.multipleAssertEqualHashes(eq_tests, ne_tests)

    def test_patterned_lists_in_lists(self):
        from typecheck import _TC_IndexError, _TC_TypeError

        def list1(obj):
            check_type(PatternList([int, str]), obj)

        # This should pass (list of lists)
        list1([[4, "foo"], [6, "foo", 7, "bar"]])

        try:
            # 6 is not list of alternating integers and strings
            list1([[4, "foo"], 6])
        except _TC_IndexError, e:
            assert e.index == 1
            assert isinstance(e.inner, _TC_TypeError)
            assert e.inner.right == [int, str]
            assert e.inner.wrong == int
        else:
            self.fail("Passed incorrectly")

    def test_patterned_lists_of_patterned_lists(self):
        from typecheck import _TC_IndexError, _TC_TypeError

        # [[[i, s]]] (list of lists of lists of alternating ints and strs)
        def list2(obj):
            check_type(PatternList([[int, str]]), obj)

        list2([ [[4, "foo"], [5, "bar"]], [[4, "baz", 7, "foo"]] ])

        try:
            # The error is in [4,[6]]; the [6] isn't a string
            list2([[[6, "a"], [7, "r", 8, "q"], [4, [6]], [6, "aaa"]]])
        except _TC_IndexError, e:
            assert e.index == 0
            assert isinstance(e.inner, _TC_IndexError)
            assert e.inner.index == 2
            assert isinstance(e.inner.inner, _TC_IndexError)
            assert e.inner.inner.index == 1
            assert isinstance(e.inner.inner.inner, _TC_TypeError)
            assert e.inner.inner.inner.right == str
            assert e.inner.inner.inner.wrong == [int]
        else:
            self.fail("Passed incorrectly")
