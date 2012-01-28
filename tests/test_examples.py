from support import TestCase
import typecheck

def check_type(typ, to_check):
    typecheck.check_type(typ, None, to_check)

class TypeCheckedTree(TestCase):
    def setUp(self):
        from typecheck import typecheck_args, register_type
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

        @typecheck_args(Tree(int))
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
