from typecheck import Type, TypeAnnotation, check_type, register_type, \
    AtomicType, List, _TC_Exception, _TC_TypeError, _TC_IndexError

class _TC_LengthError(_TC_Exception):
    def __init__(self, wrong, right=None):
        _TC_Exception.__init__(self)
        self.wrong = wrong
        self.right = right

    def error_message(self):
        m = None
        if self.right is not None:
            m = ", expected %d" % self.right
        return "length was %d%s" % (self.wrong, m or "")


class PatternList(List):
    name = "PatternList"

    def __init__(self, *types):
        #import ipdb; ipdb.set_trace()
        if not types:
            raise TypeError("Must supply at least one type to __init__()")
        self._types = [Type(t) for t in types]
        self.type = [t.type for t in self._types]

    def __typecheck__(self, func, to_check):
        if not isinstance(to_check, list):
            raise _TC_TypeError(to_check, self.type)

        # lists are patterned, meaning that [int, float] requires that the
        # to-be-checked list contain an alternating sequence of integers and
        # floats. The pattern must be completed (e.g, [5, 5.0, 6, 6.0] but not
        # [5, 5.0, 6]) for the list to typecheck successfully.

        if len(to_check) % len(self._types):
            raise _TC_LengthError(len(to_check))

        pat_len = len(self._types)
        for i, val in enumerate(to_check):
            type = self._types[i % pat_len]
            try:
                check_type(type, func, val)
            except _TC_Exception, e:
                raise _TC_IndexError(i, e)

    @classmethod
    def __typesig__(cls, obj):
        if isinstance(obj, list) and len(obj) > 1:
            return cls(*obj)

register_type(PatternList)

class Length(TypeAnnotation):
    def __init__(self, length):
        self.type = self
        self._length = int(length)

    def __hash__(self):
        return hash(str(self.__class__) + str(self._length))

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return self._length == other._length

    def __typecheck__(self, func, to_check):
        try:
            length = len(to_check)
        except TypeError:
            raise _TC_TypeError(to_check, "something with a __len__ method")

        if length != self._length:
            raise _TC_LengthError(length, self._length)


class Empty(AtomicType):
    name = "Empty"

    def __init__(self, type):
        if not hasattr(type, '__len__'):
            raise TypeError("Can only assert emptyness for types with __len__ methods")

        AtomicType.__init__(self, type)

    def __typecheck__(self, func, to_check):
        AtomicType.__typecheck__(self, func, to_check)

        if len(to_check) > 0:
            raise _TC_LengthError(len(to_check), 0)
