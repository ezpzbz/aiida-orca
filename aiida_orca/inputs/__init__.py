"""Typed input builders for common ORCA calculation types.

Each builder returns the ``parameters`` dict consumed by
:class:`~aiida_orca.calculations.orca_orca.OrcaCalculation`; no new
``CalcJob`` subclasses or entry points are introduced.
"""

from .freq import build_freq_inputs
from .geoopt import build_geoopt_inputs
from .nmr import build_nmr_inputs
from .single_point import build_single_point_inputs

__all__ = (
    'build_single_point_inputs',
    'build_geoopt_inputs',
    'build_freq_inputs',
    'build_nmr_inputs',
)
