"""
For pytest initialise a test database and profile
"""
import pytest
pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name


@pytest.fixture(scope='function')
def orca_code(aiida_local_code_factory):  # pylint: disable=unused-argument
    return aiida_local_code_factory(
        'orca',
        'orca',
        prepend=
        'export LD_LIBRARY_PATH=/home/runner/work/aiida-orca/aiida-orca//orca_4_2_1_linux_x86-64_shared_openmpi216'
    )
