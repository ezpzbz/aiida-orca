# -*- coding: utf-8 -*-
"""Tests for the :class:`aiida_orca.parsers.OrcaBaseParser` parser."""

from aiida_orca.calculations import OrcaCalculation


def test_orca_default(aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_orca, data_regression):
    """Test the ``default`` output example."""
    name = 'default'
    entry_point_calc_job = 'orca.orca'
    entry_point_parser = 'orca_base_parser'

    node = generate_calc_job_node(entry_point_calc_job, aiida_localhost, name, generate_inputs_orca())
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'relaxed_structure' in results
    assert 'output_parameters' in results

    structure_attributes = results['relaxed_structure'].attributes

    # Pop the cell if it is there since float precision error can cause the ``data_regression`` comparison to fail
    structure_attributes.pop('cell', None)

    data_regression.check({
        'relaxed_structure': structure_attributes,
        'output_parameters': results['output_parameters'].attributes,
    })


def test_orca_tddft(aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_orca, data_regression):
    """Test the ``default`` output example."""
    name = 'tddft'
    entry_point_calc_job = 'orca.orca'
    entry_point_parser = 'orca_base_parser'

    node = generate_calc_job_node(entry_point_calc_job, aiida_localhost, name, generate_inputs_orca())
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'output_parameters' in results

    data_regression.check({
        'output_parameters': results['output_parameters'].attributes,
    })


def test_orca_unrestricted(
    aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_orca, data_regression
):
    """Test the ``default`` output example."""
    name = 'unrestricted'
    entry_point_calc_job = 'orca.orca'
    entry_point_parser = 'orca_base_parser'

    node = generate_calc_job_node(entry_point_calc_job, aiida_localhost, name, generate_inputs_orca())
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'output_parameters' in results

    data_regression.check({
        'output_parameters': results['output_parameters'].attributes,
    })


def test_orca_unsuccessful(
    aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_orca, data_regression
):
    """Test that the parser returns non-zero exit code in case of unsuccessfull ORCA job."""
    name = 'unsuccessful'
    entry_point_calc_job = 'orca.orca'
    entry_point_parser = 'orca_base_parser'

    node = generate_calc_job_node(entry_point_calc_job, aiida_localhost, name, generate_inputs_orca())
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.exit_status == OrcaCalculation.exit_codes.ERROR_CALCULATION_UNSUCCESSFUL.status  # pylint: disable=no-member
    assert 'relaxed_structure' in results
    assert 'output_parameters' in results

    structure_attributes = results['relaxed_structure'].attributes

    # Pop the cell if it is there, ORCA does not support periodic cell calculations
    structure_attributes.pop('cell', None)

    data_regression.check({
        'relaxed_structure': structure_attributes,
        'output_parameters': results['output_parameters'].attributes,
    })


def test_orca_missing_stdout(aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_orca):
    """Test that the parser returns non-zero exit code when ORCA output file is missing."""
    name = 'missing_stdout'
    entry_point_calc_job = 'orca.orca'
    entry_point_parser = 'orca_base_parser'

    node = generate_calc_job_node(entry_point_calc_job, aiida_localhost, name, generate_inputs_orca())
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.exit_status == OrcaCalculation.exit_codes.ERROR_OUTPUT_STDOUT_MISSING.status  # pylint: disable=no-member
    assert 'relaxed_structure' not in results
    assert 'output_parameters' not in results
