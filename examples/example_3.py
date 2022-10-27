# -*- coding: utf-8 -*-
"""Run restart numerical Freq Calculation using AiiDA-Orca"""
import sys
import click
import pytest

from aiida.engine import run_get_pk
from aiida.orm import load_node, Code, Dict, SinglefileData
from aiida.common import NotExistent
from aiida.plugins import CalculationFactory

OrcaCalculation = CalculationFactory('orca.orca')


def example_restart_anfreq(orca_code, nproc, submit=True, freq_calc_pk=None):
    """Run restart analytical frequency calculation using AiiDA-Orca"""

    # This line is needed for tests only
    if freq_calc_pk is None:
        freq_calc_pk = pytest.freq_calc_pk  # pylint: disable=no-member

    # old hess file
    retr_fldr = load_node(freq_calc_pk).outputs.retrieved
    with retr_fldr.open('aiida.hess') as handler:
        hess_file = SinglefileData(handler.name)

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
                'freq': {
                    'restart': 'True',
                    'temp': 273,
                }
            },
            'input_keywords': ['RKS', 'BP', 'STO-3G'],
            'extra_input_keywords': ['AnFreq'],
        }
    )

    # Construct process builder
    builder = OrcaCalculation.get_builder()

    builder.structure = load_node(freq_calc_pk).outputs.relaxed_structure
    builder.parameters = parameters
    builder.code = orca_code
    builder.file = {
        'hess': hess_file,
    }

    builder.metadata.options.resources = {
        'num_machines': 1,
        'num_mpiprocs_per_machine': nproc,
    }
    builder.metadata.options.max_wallclock_seconds = 1 * 10 * 60
    if submit:
        print('Testing ORCA restart analytical frequency calculation...')
        res, pk = run_get_pk(builder)
        print('calculation pk: ', pk)
        print('Enthalpy is :', res['output_parameters'].dict['enthalpy'])
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
    example_restart_anfreq(code, nproc, submit, previous_calc)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
