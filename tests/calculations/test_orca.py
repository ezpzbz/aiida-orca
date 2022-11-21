# -*- coding: utf-8 -*-
"""Tests for the :class:`aiida_orca.calculations.orca_orca.OrcaCalculation` plugin."""
import io

from aiida.common import datastructures
from aiida.orm import SinglefileData

from aiida_orca.calculations.orca_orca import OrcaCalculation


def test_default(generate_calc_job, generate_inputs_orca, file_regression):
    """Test a default ``OrcaCalculation``."""
    entry_point_name = 'orca.orca'

    inputs = generate_inputs_orca()
    calc_info, dirpath = generate_calc_job(entry_point_name, inputs)

    # pylint: disable=protected-access
    cmdline_params = [OrcaCalculation._INPUT_FILE]
    retrieve_list = [
        OrcaCalculation._OUTPUT_FILE, OrcaCalculation._GBW_FILE, OrcaCalculation._HESSIAN_FILE,
        OrcaCalculation._RELAX_COORDS_FILE
    ]
    filenames_written = [OrcaCalculation._INPUT_FILE, OrcaCalculation._INPUT_COORDS_FILE]

    # Check the attributes of the returned `CalcInfo`
    assert isinstance(calc_info, datastructures.CalcInfo)
    assert isinstance(calc_info.codes_info[0], datastructures.CodeInfo)
    assert sorted(calc_info.codes_info[0].cmdline_params) == cmdline_params
    assert sorted(calc_info.retrieve_list) == sorted(retrieve_list)
    assert calc_info.local_copy_list is None

    with dirpath.open(OrcaCalculation._INPUT_FILE) as handle:
        input_written = handle.read()
    # pylint: enable=protected-access

    # Checks on the files written to the sandbox folder as raw input
    assert sorted(dirpath.get_content_list()) == sorted(filenames_written)
    file_regression.check(input_written, encoding='utf-8', extension='.in')


def test_file_any(generate_calc_job, generate_inputs_orca):
    """Test the ``file`` input namespace."""
    entry_point_name = 'orca.orca'

    single_file = SinglefileData(io.BytesIO(b'content'))
    inputs = generate_inputs_orca({'file': {'some_file': single_file}})
    calc_info, _ = generate_calc_job(entry_point_name, inputs)
    assert calc_info.local_copy_list == [(single_file.uuid, single_file.filename, single_file.filename)]


def test_file_gbw(generate_calc_job, generate_inputs_orca):
    """Test the ``file`` input namespace.

    When the key is ``gbw``, the target filename used is ``aiida_old.gbw``.
    """
    entry_point_name = 'orca.orca'

    single_file = SinglefileData(io.BytesIO(b'content'), filename='file.gbw')
    inputs = generate_inputs_orca({'file': {'gbw': single_file}})
    calc_info, _ = generate_calc_job(entry_point_name, inputs)
    assert calc_info.local_copy_list == [(single_file.uuid, single_file.filename, 'aiida_old.gbw')]
