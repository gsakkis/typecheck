from typecheck import AtomicType, TypeAnnotation, _TC_TypeError, _TC_LengthError

class Length(TypeAnnotation):
    def __init__(self, length):
        self.type = self
        self._length = int(length)

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
