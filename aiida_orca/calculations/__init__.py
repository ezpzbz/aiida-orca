"""AiiDA-ORCA plugin -- Calculations"""

import io
import six

from aiida.engine import CalcJob
from aiida.orm import Computer, Dict, StructureData
from aiida.common import CalcInfo, CodeInfo, InputValidationError


class OrcaCalculation(CalcJob):
    """
    This is a OrcaCalculation, subclass of JobCalculation,
    to prepare input for an ab-initio ORCA calculation.
    For information on ORCA, refer to: https://orcaforum.kofo.mpg.de/app.php/portal
    """

    # Defaults
    _DEFAULT_INPUT_FILE = 'aiida.inp'
    _DEFAULT_OUTPUT_FILE = 'aiida.out'
    _DEFAULT_COORDS_FILE_NAME = 'aiida.xyz'
    _DEFAULT_PARSER = 'orca_base_parser'
    _DEFAULT_RESTART_FILE_NAME = 'aiida.gbw'

    @classmethod
    def define(cls, spec):
        super(OrcaCalculation, cls).define(spec)

        # Input parameters
        spec.input('structure', valid_type=StructureData, required=False, help='the main input structure')
        spec.input('parameters', valid_type=Dict, help='the input parameters')
        spec.input('settings', valid_type=Dict, required=False, help='additional input parameters')

        # Specify default parser
        spec.input(
            'metadata.options.parser_name', valid_type=six.string_types, default=cls._DEFAULT_PARSER, non_db=True
        )

        spec.input('metadata.options.withmpi', valid_type=bool, default=False)

        # Exit codes
        spec.exit_code(
            100, 'ERROR_NO_RETRIEVED_FOLDER', message='The retrieved folder data node could not be accessed.'
        )

        # Output parameters
        spec.output('output_parameters', valid_type=Dict, required=True, help='the results of the calculation')
        spec.output('output_structure', valid_type=StructureData, required=False, help='optional relaxed structure')
        spec.default_output_node = 'output_parameters'

    def prepare_for_submission(self, folder):
        """Create the input files from the input nodes passed to this instance of the `CalcJob`.

        :param folder: an `aiida.common.folders.Folder` to temporarily write files on disk
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        from aiida_orca.utils import OrcaInput

        # create ORCA input file
        inp = OrcaInput(self.inputs.parameters.get_dict())

        # create input structure(s)
        if 'structure' in self.inputs:
            self._write_structure(self.inputs.structure, folder, self._DEFAULT_COORDS_FILE_NAME)

        with io.open(folder.get_abs_path(self._DEFAULT_INPUT_FILE), mode="w", encoding="utf-8") as fobj:
            fobj.write(inp.render())

        settings = self.inputs.settings.get_dict() if 'settings' in self.inputs else {}

        # create code info
        codeinfo = CodeInfo()
        codeinfo.cmdline_params = settings.pop('cmdline', []) + [self._DEFAULT_INPUT_FILE]
        codeinfo.stdout_name = self._DEFAULT_OUTPUT_FILE
        codeinfo.join_files = True
        codeinfo.code_uuid = self.inputs.code.uuid

        # create calc info
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.cmdline_params = codeinfo.cmdline_params
        calcinfo.stdin_name = self._DEFAULT_INPUT_FILE
        calcinfo.stdout_name = self._DEFAULT_OUTPUT_FILE
        calcinfo.codes_info = [codeinfo]

        calcinfo.retrieve_list = [self._DEFAULT_OUTPUT_FILE, self._DEFAULT_RESTART_FILE_NAME]
        calcinfo.retrieve_list += settings.pop('additional_retrieve_list', [])

        # symlinks
        calcinfo.remote_symlink_list = []
        calcinfo.remote_copy_list = []
        if 'parent_calc_folder' in self.inputs:
            comp_uuid = self.inputs.parent_calc_folder.computer.uuid
            remote_path = self.inputs.parent_calc_folder.get_remote_path()
            copy_info = (comp_uuid, remote_path, self._DEFAULT_PARENT_CALC_FLDR_NAME)
            if self.inputs.code.computer.uuid == comp_uuid:  # if running on the same computer - make a symlink
                # if not - copy the folder
                calcinfo.remote_symlink_list.append(copy_info)
            else:
                calcinfo.remote_copy_list.append(copy_info)

        # check for left over settings
        if settings:
            raise InputValidationError(
                "The following keys have been found " + "in the settings input node {}, ".format(self.pk) +
                "but were not understood: " + ",".join(settings.keys())
            )

        return calcinfo

    @staticmethod
    def _write_structure(structure, folder, name):
        """Function that writes a structure and takes care of element tags"""

        # create file with the structure
        mol = structure.get_pymatgen_molecule()

        # from https://github.com/materialsproject/pymatgen/blob/
        # 5a3284fd2dce70ee27e8291e6558e73beaba5164/pymatgen/io/gaussian.py#L411
        def to_s(num):
            return "%0.6f" % num

        coords = []
        for site in mol:
            coords.append(" ".join([site.species_string, " ".join([to_s(j) for j in site.coords])]))

        with io.open(folder.get_abs_path(name), mode="w") as fobj:
            fobj.write(u'{}\n\n'.format(len(coords)))
            fobj.write(u'\n'.join(coords))
