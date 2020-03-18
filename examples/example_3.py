"""Run restart numerical Freq Calculation using AiiDA-Orca"""
import os
import sys
import click
import pytest

from aiida.engine import run_get_pk
from aiida.orm import load_node, Code, Dict, SinglefileData
from aiida.common import NotExistent
from aiida.plugins import CalculationFactory

OrcaCalculation = CalculationFactory('orca')  #pylint: disable = invalid-name


def example_restart_numfreq(orca_code, freq_calc_pk=None, submit=True):
    """Run restart numerical Freq Calculation using AiiDA-Orca"""

    # This line is needed for tests only
    if freq_calc_pk is None:
        freq_calc_pk = pytest.freq_calc_pk  # pylint: disable=no-member

    # old hess file
    retr_fldr = load_node(freq_calc_pk).outputs.retrieved
    hess_file = SinglefileData(os.path.join(retr_fldr._repository._get_base_folder().abspath, 'aiida.hess'))  #pylint: disable=protected-access

    # parameters
    parameters = Dict(
        dict={
            'charge': 0,
            'multiplicity': 1,
            'input_blocks': {
                'scf': {
                    'convergence': 'tight',
                },
                # 'pal': {
                #     'nproc': 2,
                # },
                'freq': {
                    'restart': 'True',
                    'temp': 273,
                }
            },
            'input_kewords': ['RKS', 'BP', 'def2-TZVP', 'RI', 'def2/J'],
            'extra_input_keywords': ['Grid5', 'NoFinalGrid', 'NumFreq'],
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
        'num_mpiprocs_per_machine': 1,
    }
    builder.metadata.options.max_wallclock_seconds = 1 * 10 * 60
    if submit:
        print('Testing ORCA  restart numerical Frequency Calculation...')
        res, pk = run_get_pk(builder)
        print('calculation pk: ', pk)
        print('Enthalpy is :', res['output_parameters'].dict['enthalpy'])
    else:
        builder.metadata.dry_run = True
        builder.metadata.store_provenance = False


@click.command('cli')
@click.argument('codelabel')
@click.option('--previous_calc', '-p', required=True, type=int, help='PK of example_2.py calculation')
@click.option('--submit', is_flag=True, help='Actually submit calculation')
def cli(codelabel, previous_calc, submit):
    """Click interface"""
    try:
        code = Code.get_from_string(codelabel)
    except NotExistent:
        print("The code '{}' does not exist".format(codelabel))
        sys.exit(1)
    example_restart_numfreq(code, previous_calc, submit)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
