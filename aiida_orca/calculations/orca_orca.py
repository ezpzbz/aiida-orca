# -*- coding: utf-8 -*-
"""AiiDA-ORCA plugin -- Main Calculations"""

from aiida.engine import CalcJob
from aiida.orm import Dict, SinglefileData, StructureData, to_aiida_type
from aiida.common import CalcInfo, CodeInfo
from aiida.common.folders import Folder

from aiida_orca.utils import render_orca_input


class OrcaCalculation(CalcJob):
    """
    This is a OrcaCalculation, subclass of JobCalculation,
    to prepare input for an ab-initio ORCA calculation.
    For information on ORCA, refer to: https://orcaforum.kofo.mpg.de/app.php/portal
    This class is responsible for doing main calculations in ORCA.
    """

    # Defaults
    _INPUT_FILE = 'aiida.inp'
    _OUTPUT_FILE = 'aiida.out'
    _HESSIAN_FILE = 'aiida.hess'
    _INPUT_COORDS_FILE = 'aiida.coords.xyz'
    _RELAX_COORDS_FILE = 'aiida.xyz'
    _TRAJECTORY_FILE = 'aiida_trj.xyz'
    _PARSER = 'orca_base_parser'
    _GBW_FILE = 'aiida.gbw'
    _PARENT_CALC_FOLDER = 'parent_calc'

    @classmethod
    def define(cls, spec):
        super(OrcaCalculation, cls).define(spec)

        # Input parameters
        spec.input('structure', valid_type=StructureData, required=True, help='Input structure')
        spec.input(
            'parameters',
            valid_type=Dict,
            serializer=to_aiida_type,
            required=True,
            help='Input parameters to generate the input file.'
        )
        spec.input(
            'settings', valid_type=Dict, serializer=to_aiida_type, required=False, help='Additional input parameters'
        )
        spec.input_namespace(
            'file',
            valid_type=SinglefileData,
            required=False,
            help='Additional input files like gbw or hessian',
            dynamic=True
        )

        # Specify default parser
        spec.input('metadata.options.parser_name', valid_type=str, default=cls._PARSER, non_db=True)

        # Specify default input file
        spec.input('metadata.options.input_filename', valid_type=str, default=cls._INPUT_FILE)

        # Specify default output file
        spec.input('metadata.options.output_filename', valid_type=str, default=cls._OUTPUT_FILE)

        spec.input('metadata.options.withmpi', valid_type=bool, default=False)

        # Exit codes
        spec.exit_code(
            100, 'ERROR_NO_RETRIEVED_FOLDER', message='The retrieved folder data node could not be accessed.'
        )
        spec.exit_code(
            302,
            'ERROR_OUTPUT_STDOUT_MISSING',
            message='The retrieved folder did not contain the required stdout output file.'
        )
        spec.exit_code(
            303, 'ERROR_CALCULATION_UNSUCCESSFUL', message='The ORCA calculation did not finish succesfully.'
        )
        spec.exit_code(311, 'ERROR_OUTPUT_STDOUT_PARSE', message='The stdout output file could not be parsed.')

        # Output parameters
        spec.output('output_parameters', valid_type=Dict, required=True, help='the results of the calculation')
        spec.output('relaxed_structure', valid_type=StructureData, required=False, help='relaxed structure')
        spec.default_output_node = 'output_parameters'

    def prepare_for_submission(self, folder: Folder) -> CalcInfo:
        """Create the input files from the input nodes passed to this instance of the `CalcJob`.

        Args:
            folder (Folder): ``AiiDA`` folder to temporarily write files on disk

        Returns:
            CalcInfo: ``AiiDA`` CalcInfo Instance
        """

        # create input structure
        self._write_structure(self.inputs.structure, folder, self._INPUT_COORDS_FILE)

        # create ORCA input file
        self._write_input_file(self.inputs.parameters, folder, self._INPUT_FILE)

        settings = self.inputs.settings.get_dict() if 'settings' in self.inputs else {}

        # create code info
        codeinfo = CodeInfo()
        codeinfo.cmdline_params = settings.pop('cmdline', []) + [self._INPUT_FILE]
        codeinfo.stdout_name = self._OUTPUT_FILE
        codeinfo.join_files = True
        codeinfo.code_uuid = self.inputs.code.uuid

        # create calc info
        calcinfo = CalcInfo()
        calcinfo.cmdline_params = codeinfo.cmdline_params
        calcinfo.stdin_name = self._INPUT_FILE
        calcinfo.stdout_name = self._OUTPUT_FILE
        calcinfo.codes_info = [codeinfo]

        # additional files (e.g. MO guess gbw file)
        if 'file' in self.inputs:
            calcinfo.local_copy_list = []
            for name, obj in self.inputs.file.items():
                if name == 'gbw':
                    calcinfo.local_copy_list.append((obj.uuid, obj.filename, 'aiida_old.gbw'))
                else:
                    calcinfo.local_copy_list.append((obj.uuid, obj.filename, obj.filename))

        # Retrieve list
        calcinfo.retrieve_list = [self._OUTPUT_FILE, self._GBW_FILE, self._HESSIAN_FILE, self._RELAX_COORDS_FILE]
        calcinfo.retrieve_list += settings.pop('additional_retrieve_list', [])
        return calcinfo

    def _write_input_file(self, parameters: Dict, folder: Folder, filename: str) -> None:
        """Function that writes ORCA input file"""
        params = parameters.get_dict()

        charge = params.get('charge')
        if charge is None:
            raise ValueError('Missing mandatory key "charge" in input parameters')
        mult = params.get('multiplicity')
        if mult is None:
            raise ValueError('Missing mandatory key "multiplicity" in input parameters')

        input_file_string = render_orca_input(params)

        with open(folder.get_abs_path(filename), mode='w', encoding='utf-8') as fobj:
            fobj.write(input_file_string)
            # coordinate section
            fobj.write(f'\n* xyzfile {charge} {mult} {self._INPUT_COORDS_FILE}\n')

    @staticmethod
    def _write_structure(structure: StructureData, folder: Folder, filename: str) -> None:
        """Function that writes a structure to a file in an XYZ format"""

        # create file with the XYZ structure
        ase_struct = structure.get_ase()
        # ORCA cannot read the extended XYZ format, hence plain=True is needed.
        # https://wiki.fysik.dtu.dk/ase/ase/io/formatoptions.html#ase.io.extxyz.write_extxyz
        ase_struct.write(folder.get_abs_path(filename), format='extxyz', plain=True)
