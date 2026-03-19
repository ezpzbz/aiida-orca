# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name,unused-argument
"""Configuration and fixtures for unit test suite."""
from __future__ import annotations

import typing as t

from aiida import __version__ as aiida_version
from packaging.version import Version
import pytest

if Version(aiida_version) >= Version('2.6.0'):
    pytest_plugins = ['aiida.tools.pytest_fixtures']  # pylint: disable=invalid-name
else:
    pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name

    @pytest.fixture
    def aiida_code_installed(aiida_local_code_factory):
        """Compatibility shim with the new aiida pytest fixtures"""

        def _code(filepath_executable='/bin/bash', default_calc_job_plugin=None, label=None):
            return aiida_local_code_factory(
                executable=filepath_executable,
                entry_point=default_calc_job_plugin,
                label=label,
            )

        return _code


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
def generate_calc_job_node(aiida_localhost):
    """Fixture to generate a mock `CalcJobNode` for testing parsers."""

    def flatten_inputs(inputs, prefix=''):
        """Flatten inputs recursively like :meth:`aiida.engine.processes.process::Process._flatten_inputs`."""
        from collections.abc import Mapping
        flat_inputs = []
        for key, value in inputs.items():
            if isinstance(value, Mapping):
                flat_inputs.extend(flatten_inputs(value, prefix=prefix + key + '__'))
            else:
                flat_inputs.append((prefix + key, value))
        return flat_inputs

    def _generate_calc_job_node(entry_point_name='base', computer=None, test_name=None, inputs=None):
        """Fixture to generate a mock `CalcJobNode` for testing parsers.

        :param entry_point_name: entry point name of the calculation class
        :param computer: a `Computer` instance
        :param test_name: relative path of directory with test output files in the `fixtures/{entry_point_name}` folder.
        :param inputs: any optional nodes to add as input links to the corrent CalcJobNode
        :return: `CalcJobNode` instance with an attached `FolderData` as the `retrieved` node.
        """
        import os

        from aiida import orm
        from aiida.common import LinkType
        from aiida.plugins.entry_point import format_entry_point_string

        entry_point = format_entry_point_string('aiida.calculations', entry_point_name)

        node = orm.CalcJobNode(computer=computer or aiida_localhost, process_type=entry_point)
        node.base.attributes.set('input_filename', 'aiida.in')
        node.base.attributes.set('output_filename', 'aiida.out')
        node.base.attributes.set('error_filename', 'aiida.err')
        node.set_option('resources', {'num_machines': 1, 'num_mpiprocs_per_machine': 1})
        node.set_option('max_wallclock_seconds', 1800)

        if inputs:
            for name, option in inputs.pop('metadata', {}).get('options', {}).items():
                node.set_option(name, option)

            for link_label, input_node in flatten_inputs(inputs):
                input_node.store()
                node.base.links.add_incoming(input_node, link_type=LinkType.INPUT_CALC, link_label=link_label)

        node.store()

        if test_name is not None:
            basepath = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(entry_point_name[len('orca.'):], test_name)
            filepath_folder = os.path.join(basepath, 'parsers', 'fixtures', filename)

            retrieved = orm.FolderData()
            retrieved.base.repository.put_object_from_tree(filepath_folder)

            retrieved.base.links.add_incoming(node, link_type=LinkType.CREATE, link_label='retrieved')
            retrieved.store()

            remote_folder = orm.RemoteData(computer=computer or aiida_localhost, remote_path='/tmp')
            remote_folder.base.links.add_incoming(node, link_type=LinkType.CREATE, link_label='remote_folder')
            remote_folder.store()

        return node

    return _generate_calc_job_node


@pytest.fixture(scope='session')
def generate_parser():
    """Fixture to load a parser class for testing parsers."""

    def _generate_parser(entry_point_name):
        """Fixture to load a parser class for testing parsers.

        :param entry_point_name: entry point name of the parser class
        :return: the `Parser` sub class
        """
        from aiida.plugins import ParserFactory
        return ParserFactory(entry_point_name)

    return _generate_parser


@pytest.fixture
def generate_structure():
    """Return a ``StructureData`` representing a water molecule."""
    from ase.build import molecule
    from aiida.orm import StructureData
    # NOTE: Adding a default cell, even if PBC=false,
    # is here only temporarily for compatibility with AiiDA 1.x
    return StructureData(ase=molecule('H2O', vacuum=5.0))


@pytest.fixture
def generate_inputs_orca(aiida_code_installed, generate_structure):
    """Generate default inputs for an ``OrcaCalculation``."""

    def factory(inputs=None):
        """Generate default inputs for an ``OrcaCalculation``."""
        from aiida.orm import Dict

        parameters = {
            'charge': 0,
            'multiplicity': 1,
            'input_blocks': {
                'pal': {
                    'nproc': 1,
                },
                'scf': {
                    'convergence': 'tight',
                }
            },
            'input_keywords': ['PBE', 'SV(P)', 'Opt'],
            'extra_input_keywords': ['MOREAD'],
        }

        base_inputs = {
            'code': aiida_code_installed(default_calc_job_plugin='orca.orca', filepath_executable='/bin/bash'),
            'structure': generate_structure,
            'parameters': Dict(dict=parameters),
            'metadata': {
                'options': {
                    'resources': {
                        'num_machines': 1,
                        'num_mpiprocs_per_machine': 1,
                    },
                    'max_wallclock_seconds': 1800,
                }
            },
        }

        recursive_merge(base_inputs, inputs or {})

        return base_inputs

    return factory
