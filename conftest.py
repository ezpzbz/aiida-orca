"""
For pytest initialise a test database and profile
"""
import os
import pytest

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name

thisdir = os.path.dirname(os.path.realpath(__file__))  # pylint: disable=invalid-name
prepend_text = 'source ' + str(os.path.join(thisdir, '.github', 'setup.sh'))  # pylint: disable=invalid-name

# Example of how to define your own fixture
# @pytest.fixture(scope='function', autouse=True)
# def clear_database_auto(clear_database):
#     """Automatically clear database in between tests."""
#     pass


@pytest.fixture(scope='function')
def orca_code(aiida_local_code_factory):  # pylint: disable=unused-argument
    return aiida_local_code_factory('orca', 'orca', prepend_text=prepend_text)


#EOF
