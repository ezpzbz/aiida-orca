#!/usr/bin/env python
"""Run the Phase-1 pilot calculation types through a real ORCA install and
capture the resulting output files as parser test fixtures.

Requires a local AiiDA profile + registered ORCA code (see
scripts/setup_local_orca.sh / CONTRIBUTING.md).

Usage:
    verdi run scripts/run_pilot_calcs.py [profile-name] [code-label]
"""

from __future__ import annotations

import sys
from pathlib import Path

from aiida import load_profile
from aiida.engine import run_get_node
from aiida.orm import Dict, StructureData, load_code
from aiida.plugins import CalculationFactory
from ase.build import molecule

from aiida_orca.inputs import (
    build_freq_inputs,
    build_geoopt_inputs,
    build_nmr_inputs,
    build_single_point_inputs,
)

FIXTURES_ROOT = Path(__file__).resolve().parent.parent / 'tests' / 'parsers' / 'fixtures' / 'orca'

PILOTS = {
    'single_point': lambda: build_single_point_inputs(functional='HF', basis='DEF2-SVP', charge=0, multiplicity=1),
    'geoopt': lambda: build_geoopt_inputs(
        functional='PBE', basis='DEF2-SVP', dispersion='D4', charge=0, multiplicity=1
    ),
    'freq': lambda: build_freq_inputs(functional='B3LYP', basis='DEF2-SVP', dispersion='D4', charge=0, multiplicity=1),
    'nmr': lambda: build_nmr_inputs(
        functional='BP86', basis='DEF2-TZVP', nuclei='ALL H {SHIFT, SSALL}', charge=0, multiplicity=1
    ),
}


def run_pilot(name: str, code_label: str) -> None:
    code = load_code(code_label)
    structure = StructureData(ase=molecule('H2O'))
    parameters = Dict(PILOTS[name]())

    inputs = {
        'code': code,
        'structure': structure,
        'parameters': parameters,
        'metadata': {
            'options': {
                'resources': {'num_machines': 1, 'num_mpiprocs_per_machine': 1},
                'max_wallclock_seconds': 600,
                'withmpi': False,
            },
        },
    }

    OrcaCalculation = CalculationFactory('orca.orca')
    result, node = run_get_node(OrcaCalculation, **inputs)

    print(f'\n=== {name}: exit_status={node.exit_status} ===')
    if 'output_parameters' in result:
        params = result['output_parameters'].get_dict()
        print('  success:', params.get('metadata', {}).get('success'))
        print('  scfenergies:', params.get('scfenergies'))
        if 'freeenergy' in params:
            print('  freeenergy:', params.get('freeenergy'))
        if 'vibfreqs' in params:
            print('  vibfreqs:', params.get('vibfreqs'))
        if 'nmrtensors' in params:
            print('  nmrtensors present:', bool(params.get('nmrtensors')))

    if 'retrieved' not in result:
        print('  no retrieved output; skipping fixture capture')
        return

    fixture_dir = FIXTURES_ROOT / name
    fixture_dir.mkdir(parents=True, exist_ok=True)
    retrieved = result['retrieved']
    for filename in ('aiida.out', 'aiida.xyz'):
        if filename in retrieved.list_object_names():
            with retrieved.base.repository.open(filename, mode='rb') as src:
                (fixture_dir / filename).write_bytes(src.read())
    print(f'  fixture saved to {fixture_dir}')


def main() -> None:
    profile = sys.argv[1] if len(sys.argv) > 1 else 'orca-dev-nobroker'
    code_label = sys.argv[2] if len(sys.argv) > 2 else 'orca-6.1.1@localhost'
    load_profile(profile)

    for name in PILOTS:
        run_pilot(name, code_label)


if __name__ == '__main__':
    main()
