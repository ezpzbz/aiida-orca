# -*- coding: utf-8 -*-
# Copyright (c) 2020, the cclib development team
#
# This file is part of cclib (http://cclib.github.io) and is distributed under
# the terms of the BSD 3-Clause License.
# It is modified to be used as part of aiida-orca package.
"""Tools for identifying, reading and writing files and streams."""

from . import orcaparser
from . import logfileparser


def ccread(source):
    """Attempt to open and read computational chemistry data from a file.

    If the file is not appropriate for cclib parsers, a fallback mechanism
    will try to recognize some common chemistry formats and read those using
    the appropriate bridge such as Open Babel.

    Inputs:
        source - a single logfile, a list of logfiles (for a single job),
                 an input stream, or an URL pointing to a log file.
        *args, **kwargs - arguments and keyword arguments passed to ccopen
    Returns:
        a ccData object containing cclib data attributes
    """

    log = ccopen(source)

    return log.parse()


def ccopen(source):
    """Guess the identity of a particular log file and return an instance of it.

    Inputs:
        source - a single logfile, a list of logfiles (for a single job),
                 an input stream, or an URL pointing to a log file.
        *args, **kwargs - arguments and keyword arguments passed to filetype

    Returns:
      one of ADF, DALTON, GAMESS, GAMESS UK, Gaussian, Jaguar,
      Molpro, MOPAC, NWChem, ORCA, Psi3, Psi/Psi4, QChem, CJSON or None
      (if it cannot figure it out or the file does not exist).
    """
    inputfile = None

    inputfile = logfileparser.openlogfile(source)

    filetype = orcaparser.ORCA

    inputfile.seek(0, 0)
    inputfile.close()
    return filetype(source)
