"""Run Opt and Numerical Freq Calculation using AiiDA-Orca"""
import os
import sys
import click
import pytest

from pymatgen.core import Molecule

from aiida.engine import run_get_pk
from aiida.orm import (Code, Dict, StructureData)
from aiida.common import NotExistent
from aiida.plugins import CalculationFactory

OrcaCalculation = CalculationFactory('orca_main')  #pylint: disable = invalid-name


def example_opt_numfreq(orca_code, submit=True):
    """Run Opt and Numerical Calculation using AiiDA-Orca"""

    # structure
    thisdir = os.path.dirname(os.path.realpath(__file__))
    xyz_path = os.path.join(thisdir, 'h2co.xyz')
    structure = StructureData(pymatgen_molecule=Molecule.from_file(xyz_path))

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
                    'nproc': 2,
                },
            },
            'input_kewords': ['RKS', 'BP', 'def2-SVP', 'RI', 'def2/J'],
            'extra_input_keywords': ['DEFGRID1', 'NumFreq', 'OPT'],
        }
    )

    # Construct process builder

    builder = OrcaCalculation.get_builder()

    builder.structure = structure
    builder.parameters = parameters
    builder.code = orca_code

    builder.metadata.options.resources = {
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1,
    }
    builder.metadata.options.max_wallclock_seconds = 1 * 10 * 60
    if submit:
        print('Testing ORCA and Numerical Frequency Calculation...')
        res, pk = run_get_pk(builder)
        print('calculation pk: ', pk)
        print('Enthalpy is :', res['output_parameters'].dict['enthalpy'])
        pytest.freq_calc_pk = pk
    else:
        builder.metadata.dry_run = True
        builder.metadata.store_provenance = False


@click.command('cli')
@click.argument('codelabel')
@click.option('--submit', is_flag=True, help='Actually submit calculation')
def cli(codelabel, submit):
    """Click interface"""
    try:
        code = Code.get_from_string(codelabel)
    except NotExistent:
        print("The code '{}' does not exist".format(codelabel))
        sys.exit(1)
    example_opt_numfreq(code, submit)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
