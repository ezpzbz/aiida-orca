# -*- coding: utf-8 -*-
"""Run simple TDDFT Calculation using AiiDA-Orca"""

import sys
import click
import pytest

from aiida.engine import run_get_pk
from aiida.orm import load_node, Code, Dict
from aiida.common import NotExistent
from aiida.plugins import CalculationFactory

OrcaCalculation = CalculationFactory('orca.orca')  #pylint: disable = invalid-name


def example_simple_tddft(orca_code, nproc, submit=True, opt_calc_pk=None):
    """Run simple TDDFT Calculation using AiiDA-Orca"""

    # This line is needed for tests only
    if opt_calc_pk is None:
        opt_calc_pk = pytest.opt_calc_pk  # pylint: disable=no-member

    # parameters
    parameters = Dict(
        dict={
            'charge': 0,
            'multiplicity': 1,
            'input_blocks': {
                'scf': {
                    'convergence': 'tight',
                },
                'pal': {
                    'nproc': nproc,
                },
                'tddft': {
                    'nroots': 3,
                    'tda': 'false',
                }
            },
            'input_keywords': ['RKS', 'PBE', 'SV(P)'],
            'extra_input_keywords': [],
        }
    )

    # Construct process builder
    builder = OrcaCalculation.get_builder()

    builder.structure = load_node(opt_calc_pk).outputs.relaxed_structure
    builder.parameters = parameters
    builder.code = orca_code
    builder.metadata.options.resources = {
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1,
    }
    builder.metadata.options.max_wallclock_seconds = 1 * 10 * 60
    if submit:
        print('Testing ORCA  simple TDDFT Calculation...')
        res, pk = run_get_pk(builder)
        print('calculation pk: ', pk)
        print('1st ET energy is :', res['output_parameters'].dict['etenergies'][0])
        print('1st oscillator strength energy is :', res['output_parameters'].dict['etoscs'][0])
    else:
        builder.metadata.dry_run = True
        builder.metadata.store_provenance = False
        res, pk = run_get_pk(builder)


@click.command('cli')
@click.argument('codelabel')
@click.option('--nproc', default=1, show_default=True, help='Number of processors for ORCA calculation')
@click.option('--previous_calc', '-p', required=True, type=int, help='PK of example_2.py calculation')
@click.option('--submit', is_flag=True, help='Actually submit calculation')
def cli(codelabel, nproc, previous_calc, submit):
    """Click interface"""
    try:
        code = Code.get_from_string(codelabel)
    except NotExistent:
        print(f'The code {codelabel} does not exist.')
        sys.exit(1)
    example_simple_tddft(code, nproc, previous_calc, submit)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
