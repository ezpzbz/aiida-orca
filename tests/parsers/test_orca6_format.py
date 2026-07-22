"""Targeted unit tests for ORCA-6-specific output format changes in the vendored cclib parser.

ORCA is proprietary software and no real ORCA 6 log fixtures are available yet for
full regression testing (see ``tests/parsers/fixtures/orca/``, which only contains
logs up to ORCA 5). These tests exercise the ORCA-6-specific parsing branches with
small hand-crafted snippets instead, based on the documented ORCA 6 output format
change reported in https://github.com/ezpzbz/aiida-orca/issues/74.

Replace/extend these with real fixture-based regression tests once ORCA 6 logs
become available.
"""

import io

from aiida_orca.parsers.cclib import orcaparser


def test_orca6_absorption_spectrum_format():
    """ORCA 6 restructured the TDDFT absorption spectrum table: an alphanumeric
    "Transition" column (e.g. "0-1Ag -> 1-3Bu") replaces the plain integer "State"
    column used up to ORCA 5, a separate eV energy column was added, and the
    transition-moment columns are now labelled D2/DX/DY/DZ instead of T2/TX/TY/TZ.
    """
    trigger_line = 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS'
    body = iter(
        [
            '-' * 100,
            '     Transition      Energy     Energy  Wavelength fosc(D2)      D2        DX        DY        DZ',
            '                      (eV)      (cm-1)    (nm)                 (au**2)    (au)      (au)      (au)',
            '-' * 100,
            '  0-1Ag ->  1-3Bu   3.129277   25239.3   396.2   0.000000000   0.00000   0.00000   0.00000   0.00000',
            '-' * 100,
        ]
    )

    parser = orcaparser.ORCA(io.StringIO(''))
    parser.version = (6, 0)
    parser.extract(body, trigger_line)

    assert parser.etenergies == [25239.3]
    assert parser.etoscs == [0.0]


def test_orca5_absorption_spectrum_format_still_works():
    """The pre-ORCA-6 table format (integer "State" column, T2/TX/TY/TZ columns)
    must keep parsing unchanged for ORCA <= 5 logs.
    """
    trigger_line = 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS'
    body = iter(
        [
            '-' * 79,
            'State   Energy  Wavelength   fosc         T2         TX        TY        TZ',
            '        (cm-1)    (nm)                  (au**2)     (au)      (au)      (au)',
            '-' * 79,
            '   1 5184116.7      1.9   0.040578220   0.00258  -0.05076  -0.00000  -0.00000',
            '-' * 79,
        ]
    )

    parser = orcaparser.ORCA(io.StringIO(''))
    parser.version = (5, 0)
    parser.extract(body, trigger_line)

    assert parser.etenergies == [5184116.7]
    assert parser.etoscs == [0.040578220]
