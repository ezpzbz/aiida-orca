# -*- coding: utf-8 -*-
"""Run simple DFT calculation"""
import os
import sys
import click
import pytest

import ase.io

from aiida.engine import run_get_pk
from aiida.orm import load_node, Code, Dict, SinglefileData, StructureData
from aiida.common import NotExistent
from aiida.plugins import CalculationFactory

OrcaCalculation = CalculationFactory('orca.orca')  #pylint: disable = invalid-name


def example_opt_restart(orca_code, nproc, submit=True, opt_calc_pk=None):
    """Run simple DFT calculation"""

    # This line is needed for tests only
    if opt_calc_pk is None:
        opt_calc_pk = pytest.opt_calc_pk  # pylint: disable=no-member

    # structure
    thisdir = os.path.dirname(os.path.realpath(__file__))
    xyz_path = os.path.join(thisdir, 'h2co.xyz')
    ase_struct = ase.io.read(xyz_path, format='xyz', index=0)
    ase_struct.set_cell([1.0, 1.0, 1.0])
    structure = StructureData(ase=ase_struct)

    # old gbw file
    retr_fldr = load_node(opt_calc_pk).outputs.retrieved
    with retr_fldr.open('aiida.gbw') as handler:
        gbw_file = SinglefileData(handler.name)

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
                    'nproc': nproc,
                },
            },
            'input_keywords': ['PBE', 'def2-SVP', 'Opt'],
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
        'num_mpiprocs_per_machine': nproc,
    }
    builder.metadata.options.max_wallclock_seconds = 1 * 10 * 60
    if submit:
        print('Testing Orca single point calculation...')
        res, pk = run_get_pk(builder)
        print(f'Calculation PK: {pk}')
        print(f'Optimized structure PK: {res["relaxed_structure"].pk}')
        print(f'SCF Energy: {res["output_parameters"]["scfenergies"]}')
    else:
        builder.metadata.dry_run = True
        builder.metadata.store_provenance = False
        res, pk = run_get_pk(builder)


@click.command('cli')
@click.argument('codelabel')
@click.option('--nproc', default=1, show_default=True, help='Number of processors for ORCA calculation')
@click.option('--previous_calc', '-p', required=True, type=int, help='PK of example_0.py calculation')
@click.option('--submit', is_flag=True, help='Actually submit calculation')
def cli(codelabel, nproc, previous_calc, submit):
    """Click interface"""
    try:
        code = Code.get_from_string(codelabel)
    except NotExistent:
        print(f'The code {codelabel} does not exist.')
        sys.exit(1)
    example_opt_restart(code, nproc, submit, previous_calc)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
