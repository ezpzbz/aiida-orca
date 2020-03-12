"""Run simple DFT calculation"""

import sys
import click

import pymatgen as mg

from aiida.engine import run
from aiida.orm import (Code, Dict, StructureData)
from aiida.common import NotExistent
from aiida.plugins import CalculationFactory

OrcaCalculation = CalculationFactory('orca')  #pylint: disable = invalid-name


def example_dft(orca_code, submit=True):
    """Run simple DFT calculation"""

    print("Testing Gaussian Input Creation")

    # structure
    structure = StructureData(pymatgen_molecule=mg.Molecule.from_file('./ch4.xyz'))

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
                }
            },
            'input_keywords': {
                'B3LYP/G': None,
                'SV(P)': None,
                'Opt': None,
            },
            'extra_input_keywords': {},
        }
    )

    # Construct process builder

    builder = OrcaCalculation.get_builder()

    builder.structure = structure
    builder.parameters = parameters
    builder.code = orca_code

    builder.metadata.options.resources = {
        "num_machines": 1,
        "num_mpiprocs_per_machine": 2,
    }
    builder.metadata.options.max_wallclock_seconds = 1 * 3 * 60
    # builder.metadata.options.max_memory_kb = int(parameters['link0_parameters']['%mem'][:-2])
    if submit:

        builder.metadata.dry_run = False
        builder.metadata.store_provenance = True

        print("Submitted calculation...")
        run(builder)
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
    example_dft(code, submit)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
