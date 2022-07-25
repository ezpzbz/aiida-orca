# Copyright (c) 2020, the cclib development team
#
# This file is part of cclib (http://cclib.github.io) and is distributed under
# the terms of the BSD 3-Clause License.
#
# It is modified to be used as part of aiida-orca package.
"""Utilities often used by cclib parsers and scripts"""

import re

import numpy
import periodictable

_BUILTIN_FLOAT = float


def float(number):
    """Convert a string to a float.

    This method should perform certain checks that are specific to cclib,
    including avoiding the problem with Ds instead of Es in scientific notation.
    Another point is converting string signifying numerical problems (*****)
    to something we can manage (Numpy's NaN).
    """
    # print(number)
    if list(set(number)) == ['*']:
        return numpy.nan

    return _BUILTIN_FLOAT(number.replace('D', 'E'))


def convertor(value, fromunits, tounits):
    """Convert from one set of units to another.

    Sources:
        NIST 2010 CODATA (http://physics.nist.gov/cuu/Constants/index.html)
        Documentation of GAMESS-US or other programs as noted
    """

    _convertor = {'hartree_to_eV': lambda x: x * 27.21138505, 'ebohr_to_Debye': lambda x: x * 2.5417462300}

    return _convertor[f'{fromunits}_to_{tounits}'](value)


def skip_until_no_match(inputfile, regex):
    """Skip lines that match a regex. First non-matching line is returned.

    This method allows to skip a variable number of lines, allowing for example,
    to parse sections that might have different whitespace/spurious lines for
    different versions of the software.
    """
    line = next(inputfile)
    while re.match(regex, line):
        line = next(inputfile)
    return line


def str_contains_only(string, chars):
    """Checks if string contains only the specified characters.
    """
    return all([c in chars for c in string])


class PeriodicTable:
    """Allows conversion between element name and atomic no."""

    def __init__(self):
        self.element = [None]
        self.number = {}

        for e in periodictable.elements:
            if e.symbol != 'n':
                self.element.append(e.symbol)
                self.number[e.symbol] = e.number


# EOF
