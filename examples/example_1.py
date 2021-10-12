"""Run simple DFT calculation"""
import os
import sys
import click
import pytest

import pymatgen.core.structure as mg

from aiida.engine import run_get_pk
from aiida.orm import load_node, Code, Dict, SinglefileData, StructureData
from aiida.common import NotExistent
from aiida.plugins import CalculationFactory

OrcaCalculation = CalculationFactory('orca_main')  #pylint: disable = invalid-name


def example_opt_restart(orca_code, opt_calc_pk=None, submit=True):
    """Run simple DFT calculation"""

    # This line is needed for tests only
    if opt_calc_pk is None:
        opt_calc_pk = pytest.opt_calc_pk  # pylint: disable=no-member

    # structure
    thisdir = os.path.dirname(os.path.realpath(__file__))
    xyz_path = os.path.join(thisdir, 'h2co.xyz')
    structure = StructureData(pymatgen_molecule=mg.Molecule.from_file(xyz_path))

    # old gbw file
    retr_fldr = load_node(opt_calc_pk).outputs.retrieved
    gbw_file = SinglefileData(os.path.join(retr_fldr._repository._get_base_folder().abspath, 'aiida.gbw'))  #pylint: disable=protected-access

    # parameters
    parameters = Dict(
        dict={
            'charge': 0,
            'multiplicity': 1,
            'input_blocks': {
                'scf': {
                    'convergence': 'tight',
                    'moinp': '"aiida_old.gbw"',
                },
                'pal': {
                    'nproc': 2,
                },
            },
            'input_keywords': ['B3LYP/G', 'def2-TZVP', 'Opt'],
            'extra_input_keywords': ['MOREAD'],
        }
    )

    # Construct process builder
    builder = OrcaCalculation.get_builder()

    builder.structure = structure
    builder.parameters = parameters
    builder.code = orca_code
    builder.file = {
        'gbw': gbw_file,
    }
    builder.metadata.options.resources = {
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1,
    }
    builder.metadata.options.max_wallclock_seconds = 1 * 10 * 60
    if submit:
        print('Testing Orca Opt Calculations...')
        res, pk = run_get_pk(builder)
        print('calculation pk: ', pk)
        print('SCF Energy is :', res['output_parameters'].dict['scfenergies'])
    else:
        builder.metadata.dry_run = True
        builder.metadata.store_provenance = False


@click.command('cli')
@click.argument('codelabel')
@click.option('--previous_calc', '-p', required=True, type=int, help='PK of example_0.py calculation')
@click.option('--submit', is_flag=True, help='Actually submit calculation')
def cli(codelabel, previous_calc, submit):
    """Click interface"""
    try:
        code = Code.get_from_string(codelabel)
    except NotExistent:
        print("The code '{}' does not exist".format(codelabel))
        sys.exit(1)
    example_opt_restart(code, previous_calc, submit)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
