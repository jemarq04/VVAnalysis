"""

Some useful functions

Nate Woods, U. Wisconsin

"""


def makeNumberPretty(n, maxDigits=10):
    """
    Take a number, return a string of it with the right number of digits
    and whatnot.
    Cuts off at maxDigits places after the decimal point.
    No trailing zeros, or decimal points if there are no digits after it.
    """
    if maxDigits < 0:
        raise ValueError(f"Invalid number of digits: {maxDigits}")

    digitsBeforeDecimal = len(f"{n:.0f}")
    digits = digitsBeforeDecimal + maxDigits
    return f"{{:.{digits}g}}".format(n)


def combineWeights(*wts, **kwargs):
    """
    Combine all non-null items in wts into a string that multiplies them all
    together (' * ' between items), unless certain keyword arguments
    are present:
    kwargs['selections'] evaluates to True -> join with ' && ' instead of ' * '
    kwargs['joinwith'] can be used to replace ' * ' with an arbitrary string
    """
    if not all(isinstance(w, str) or isinstance(w, _NumType) for w in wts):
        raise TypeError("You can only combine weights made of numbers or strings")
    goodWeights = [str(w) for w in wts if w]
    if not goodWeights:
        return "1"
    joiner = " * "
    if kwargs.get("selections", False):
        joiner = " && "
    joiner = "){}(".format(kwargs.get("joinwith", joiner))
    return "(" + joiner.join(goodWeights) + ")"


identityFunction = lambda *args, **kwargs: True


Z_MASS = 91.1876


def zMassDist(m):
    return abs(m - Z_MASS)


def zeroNegativeBins(h):
    for b in h:
        b.value = max(0.0, b.value)
