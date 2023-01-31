# -*- coding: utf-8 -*-
"""Run simple DFT calculation"""
import os
import sys
import click

import ase.io

from aiida.engine import run_get_pk
from aiida.orm import load_node, Code, Dict, StructureData
from aiida.common import NotExistent
from aiida.plugins import WorkflowFactory

OrcaBaseWorkChain = WorkflowFactory('orca.base')


def example_opt(orca_code, nproc, submit=True):
    """Run basic workflow"""

    # structure
    thisdir = os.path.dirname(os.path.realpath(__file__))
    xyz_path = os.path.join(thisdir, 'h2co.xyz')
    ase_struct = ase.io.read(xyz_path, format='xyz', index=0)
    ase_struct.set_cell([1.0, 1.0, 1.0])
    structure = StructureData(ase=ase_struct)

    # parameters
    parameters = Dict(
        dict={
            'charge': 0,
            'multiplicity': 1,
            'input_blocks': {
                'pal': {
                    'nproc': nproc,
                }
            },
            'input_keywords': ['PBE', 'STO-3G'],
            'extra_input_keywords': [],
        }
    )

    # Construct process builder
    builder = OrcaBaseWorkChain.get_builder()

    builder.orca.structure = structure
    builder.orca.parameters = parameters
    builder.orca.code = orca_code

    builder.orca.metadata.options.resources = {
        'num_machines': 1,
        'num_mpiprocs_per_machine': nproc,
    }
    builder.orca.metadata.options.max_wallclock_seconds = 1 * 10 * 60
    if submit:
        print('Testing OrcaBaseWorkChain...')
        res, pk = run_get_pk(builder)
        calc = load_node(pk)
        if not calc.is_finished_ok:
            print(f'{calc.exit_message}')
            sys.exit(1)
        print(f'calculation pk: {pk}')
        print(f'SCF Energy: {res["output_parameters"]["scfenergies"]}')
    else:
        builder.metadata.dry_run = True
        builder.metadata.store_provenance = False
        res, pk = run_get_pk(builder)


@click.command('cli')
@click.argument('codelabel')
@click.option('--nproc', default=1, show_default=True, help='Number of processors for ORCA calculation')
@click.option('--submit', is_flag=True, help='Actually submit calculation')
def cli(codelabel, nproc, submit):
    """Click interface"""
    try:
        code = Code.get_from_string(codelabel)
    except NotExistent:
        print(f'The code {codelabel} does not exist.')
        sys.exit(1)
    example_opt(code, nproc, submit)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
