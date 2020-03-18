"""
For pytest initialise a test database and profile
"""
import pytest
pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name

# # Clearing database between tests
# @pytest.fixture(scope='function', autouse=True)
# def clear_database_auto(clear_database):
#     """Automatically clear database in between tests."""
#     pass

# Setting up computer and code.
# @pytest.fixture(scope='function')
# def orca_code(aiida_local_code_factory):  # pylint: disable=unused-argument
#     return aiida_local_code_factory(
#         'orca',
#         'orca',
#         prepend_text=
#         'export LD_LIBRARY_PATH=/home/runner/work/aiida-orca/aiida-orca/orca_4_2_1_linux_x86-64_shared_openmpi216'
#     )

ompi_bin = 'export PATH=/home/runner/work/aiida-orca/aiida-orca/ompi216/bin:$PATH'  # pylint: disable=invalid-name
ompi_lib = 'export LD_LIBRARY_PATH=/home/runner/work/aiida-orca/aiida-orca/ompi216/lib:$LD_LIBRARY_PATH'  # pylint: disable=invalid-name
orca_bin = 'export LD_LIBRARY_PATH=/home/runner/work/aiida-orca/aiida-orca/orca421:$LD_LIBRARY_PATH'  # pylint: disable=invalid-name


@pytest.fixture(scope='function')
def orca_code(aiida_local_code_factory):  # pylint: disable=unused-argument
    return aiida_local_code_factory('orca', 'orca', prepend_text=ompi_lib + '\n' + ompi_lib + '\n' + orca_bin + '\n')
