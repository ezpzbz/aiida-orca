# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name,unused-argument
"""Configuration and fixtures for unit test suite."""
from __future__ import annotations

import typing as t

import pytest

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name


def recursive_merge(left: dict[t.Any, t.Any], right: dict[t.Any, t.Any]) -> None:
    """Recursively merge the ``right`` dictionary into the ``left`` dictionary.

    :param left: Base dictionary.
    :param right: Dictionary to recurisvely merge on top of ``left`` dictionary.
    """
    for key, value in right.items():
        if (key in left and isinstance(left[key], dict) and isinstance(value, dict)):
            recursive_merge(left[key], value)
        else:
            left[key] = value


@pytest.fixture(scope='function')
def fixture_sandbox():
    """Return a `SandboxFolder`."""
    from aiida.common.folders import SandboxFolder
    with SandboxFolder() as folder:
        yield folder


@pytest.fixture
def generate_calc_job(fixture_sandbox):
    """Fixture to construct a new `CalcJob` instance and call `prepare_for_submission` for testing `CalcJob` classes.

    The fixture will return the `CalcInfo` returned by `prepare_for_submission` and the temporary folder that was passed
    to it, into which the raw input files will have been written.
    """

    def _generate_calc_job(entry_point_name, inputs=None):
        """Fixture to generate a mock `CalcInfo` for testing calculation jobs."""
        from aiida.engine.utils import instantiate_process
        from aiida.manage.manager import get_manager
        from aiida.plugins import CalculationFactory

        manager = get_manager()
        runner = manager.get_runner()

        process_class = CalculationFactory(entry_point_name)
        process = instantiate_process(runner, process_class, **inputs)

        calc_info = process.prepare_for_submission(fixture_sandbox)

        return calc_info, fixture_sandbox

    return _generate_calc_job


@pytest.fixture
def generate_structure():
    """Return a ``StructureData`` representing a water molecule."""
    from ase.build import molecule
    from aiida.orm import StructureData
    # NOTE: Adding a default cell, even if PBC=false,
    # is here only temporarily for compatibility with AiiDA 1.x
    return StructureData(ase=molecule('H2O', vacuum=5.0))


@pytest.fixture
def generate_inputs_orca(aiida_local_code_factory, generate_structure):
    """Generate default inputs for an ``OrcaCalculation``."""

    def factory(inputs=None):
        """Generate default inputs for an ``OrcaCalculation``."""
        from aiida.orm import Dict

        parameters = {
            'charge': 0,
            'multiplicity': 1,
            'input_blocks': {
                'scf': {
                    'convergence': 'tight',
                },
                'pal': {
                    'nproc': 1,
                }
            },
            'input_keywords': ['PBE', 'SV(P)', 'Opt'],
            'extra_input_keywords': [],
        }

        base_inputs = {
            'code': aiida_local_code_factory('orca.orca', '/bin/bash'),
            'structure': generate_structure,
            'parameters': Dict(dict=parameters),
            'metadata': {
                'options': {
                    'resources': {
                        'num_machines': 1,
                        'num_mpiprocs_per_machine': 1,
                    },
                    'max_wallclock_seconds': 1800
                }
            }
        }

        recursive_merge(base_inputs, inputs or {})

        return base_inputs

    return factory
