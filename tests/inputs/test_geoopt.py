"""Tests for the geometry optimization typed input builder."""

from aiida.orm import Dict

from aiida_orca.calculations.orca_orca import OrcaCalculation
from aiida_orca.inputs import build_geoopt_inputs


def test_geoopt_default(generate_calc_job, generate_inputs_orca, file_regression):
    """Rendered input matches the ORCA 6.1 geometry-optimization tutorial baseline (PBE-D4/DEF2-SVP)."""
    parameters = build_geoopt_inputs(functional='PBE', basis='DEF2-SVP', dispersion='D4', charge=0, multiplicity=1)
    inputs = generate_inputs_orca({'parameters': Dict(parameters)})
    _, dirpath = generate_calc_job('orca.orca', inputs)

    with dirpath.open(OrcaCalculation._INPUT_FILE) as handle:  # pylint: disable=protected-access
        input_written = handle.read()

    file_regression.check(input_written, encoding='utf-8', extension='.in')
