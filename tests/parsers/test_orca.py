# -*- coding: utf-8 -*-
"""Tests for the :class:`aiida_orca.parsers.OrcaBaseParser` parser."""


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
