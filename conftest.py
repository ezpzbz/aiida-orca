# -*- coding: utf-8 -*-
"""
For pytest initialise a test database and profile
"""
import pytest

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']


def pytest_addoption(parser):
    """Add cmdline options to pytest"""
    parser.addoption('--nproc', action='store', default=1)


@pytest.fixture(scope='function')
def orca_code(aiida_local_code_factory):  # pylint: disable=unused-argument
    """Fixture for fetching Orca Code node from AiiDA DB"""
    return aiida_local_code_factory('orca', 'orca')


@pytest.fixture(scope='session')
def nproc(request):
    """Fixture for number of CPUs"""
    return request.config.option.nproc if request.config.option.nproc else 2
