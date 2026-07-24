"""Tests for the NMR typed input builder."""

from aiida.orm import Dict

from aiida_orca.calculations.orca_orca import OrcaCalculation
from aiida_orca.inputs import build_nmr_inputs


def test_nmr_default(generate_calc_job, generate_inputs_orca, file_regression):
    """Rendered input matches the ORCA 6.1 NMR tutorial baseline (BP86/DEF2-TZVP, proton shifts)."""
    parameters = build_nmr_inputs(
        functional='BP86',
        basis='DEF2-TZVP',
        nuclei='ALL H {SHIFT, SSALL}',
        charge=0,
        multiplicity=1,
    )
    inputs = generate_inputs_orca({'parameters': Dict(parameters)})
    _, dirpath = generate_calc_job('orca.orca', inputs)

    with dirpath.open(OrcaCalculation._INPUT_FILE) as handle:  # pylint: disable=protected-access
        input_written = handle.read()

    file_regression.check(input_written, encoding='utf-8', extension='.in')
