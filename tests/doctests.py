##
# - Originally submitted by Knut Hartmann (2005/09/28)
# - Hacked up by Iain to allow integration with the _unittest module
# - Further hacked up by Collin Winter (2005.11.16) to work with his own testsuite

from typecheck import accepts

@accepts(str)
def checker(aString):
    """
    >>> print sorted([x for x in globals().copy() if not x.startswith('_')])
    ['MyTestClass', 'Rational', 'accepts', 'checker', 'checker2', 'testMyClass']
    >>> print sorted([x for x in locals().copy() if not x.startswith('_')])
    ['MyTestClass', 'Rational', 'accepts', 'checker', 'checker2', 'testMyClass', 'x']
    >>> checker('Nonsense')
    2
    """
    if aString == "":
        return 1
    else:
        return 2

def checker2(aString):
    """
    >>> print sorted([x for x in globals().copy() if not x.startswith('_')])
    ['MyTestClass', 'Rational', 'accepts', 'checker', 'checker2', 'testMyClass']
    >>> print sorted([x for x in locals().copy() if not x.startswith('_')])
    ['MyTestClass', 'Rational', 'accepts', 'checker', 'checker2', 'testMyClass', 'x']
    >>> checker2('Nonsense')
    2
    """
    if aString == "":
        return 1
    else:
        return 2

class Rational(object):
    @accepts(object, int, int)
    def __init__(self, numerator, denumerator):
        self.p = numerator
        self.q = denumerator

class MyTestClass:
    @accepts(object, int, Rational)
    def __init__(self, a, b):
        pass

def testMyClass():
    """
    >>> print MyTestClass(1, Rational(1, 2)) # doctest:+ELLIPSIS
    <...doctests.MyTestClass instance at 0x...>
    """
    pass
