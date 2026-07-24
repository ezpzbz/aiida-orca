"""Parser regression tests against real ORCA 6.1.1 outputs, captured via
``scripts/run_pilot_calcs.py`` from the Phase-1 typed input builders.

These close the "no ORCA 6 fixtures" gap noted in issue #85: the parser
fixes applied alongside them address genuine ORCA 6.1.1 output-format
changes found by actually running the pilot calculations (see the git log
for details), not hypothetical ones.
"""

from aiida.orm import Dict

from aiida_orca.inputs import build_freq_inputs, build_geoopt_inputs, build_nmr_inputs, build_single_point_inputs


def test_orca_single_point(
    aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_orca, data_regression
):
    """Test parsing a real ORCA 6.1.1 single-point (HF/DEF2-SVP) output."""
    parameters = build_single_point_inputs(functional='HF', basis='DEF2-SVP', charge=0, multiplicity=1)
    inputs = generate_inputs_orca({'parameters': Dict(parameters)})

    node = generate_calc_job_node('orca.orca', aiida_localhost, 'single_point', inputs)
    parser = generate_parser('orca_base_parser')
    results, calcfunction = parser.parse_from_node(node)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'output_parameters' in results

    data_regression.check({'output_parameters': results['output_parameters'].attributes})


def test_orca_geoopt(aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_orca, data_regression):
    """Test parsing a real ORCA 6.1.1 geometry-optimization (PBE-D4/DEF2-SVP) output."""
    parameters = build_geoopt_inputs(functional='PBE', basis='DEF2-SVP', dispersion='D4', charge=0, multiplicity=1)
    inputs = generate_inputs_orca({'parameters': Dict(parameters)})

    node = generate_calc_job_node('orca.orca', aiida_localhost, 'geoopt', inputs)
    parser = generate_parser('orca_base_parser')
    results, calcfunction = parser.parse_from_node(node)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'relaxed_structure' in results
    assert 'output_parameters' in results

    structure_attributes = results['relaxed_structure'].attributes
    # Pop the cell if it is there since float precision error can cause the ``data_regression`` comparison to fail
    structure_attributes.pop('cell', None)

    data_regression.check(
        {
            'relaxed_structure': structure_attributes,
            'output_parameters': results['output_parameters'].attributes,
        }
    )


def test_orca_freq(aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_orca, data_regression):
    """Test parsing a real ORCA 6.1.1 frequency (B3LYP-D4/DEF2-SVP) output.

    Covers the ORCA-6-specific parser fixes for the LEAN-SCF solver banner,
    the orbital-truncation notice, and the renamed enthalpy-section line.
    """
    parameters = build_freq_inputs(functional='B3LYP', basis='DEF2-SVP', dispersion='D4', charge=0, multiplicity=1)
    inputs = generate_inputs_orca({'parameters': Dict(parameters)})

    node = generate_calc_job_node('orca.orca', aiida_localhost, 'freq', inputs)
    parser = generate_parser('orca_base_parser')
    results, calcfunction = parser.parse_from_node(node)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'output_parameters' in results

    output_parameters = results['output_parameters'].get_dict()
    assert output_parameters['metadata']['success'] is True
    # Water: 3N-6 = 3 vibrational modes, all real (no imaginary frequencies).
    assert len(output_parameters['vibfreqs']) == 3
    assert all(freq > 0 for freq in output_parameters['vibfreqs'])

    data_regression.check({'output_parameters': results['output_parameters'].attributes})


def test_orca_nmr(aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_orca, data_regression):
    """Test parsing a real ORCA 6.1.1 NMR (BP86/DEF2-TZVP, proton shifts) output."""
    parameters = build_nmr_inputs(
        functional='BP86', basis='DEF2-TZVP', nuclei='ALL H {SHIFT, SSALL}', charge=0, multiplicity=1
    )
    inputs = generate_inputs_orca({'parameters': Dict(parameters)})

    node = generate_calc_job_node('orca.orca', aiida_localhost, 'nmr', inputs)
    parser = generate_parser('orca_base_parser')
    results, calcfunction = parser.parse_from_node(node)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'output_parameters' in results

    data_regression.check({'output_parameters': results['output_parameters'].attributes})
