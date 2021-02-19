"""AiiDA-ORCA plugin -- Main Calculations"""

import io
import six

from aiida.engine import CalcJob
from aiida.orm import Dict, SinglefileData, StructureData
from aiida.common import CalcInfo, CodeInfo


class OrcaCalculation(CalcJob):
    """
    This is a OrcaCalculation, subclass of JobCalculation,
    to prepare input for an ab-initio ORCA calculation.
    For information on ORCA, refer to: https://orcaforum.kofo.mpg.de/app.php/portal
    This is responsible for doing main calculations in ORCA.
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
        spec.input('parameters', valid_type=Dict, required=True, help='Input paramters to generate the input file.')
        spec.input('settings', valid_type=Dict, required=False, help='additional input parameters')
        spec.input_namespace(
            'file',
            valid_type=SinglefileData,
            required=False,
            help='additional input files like gbw or hessian',
            dynamic=True
        )

        # Specify default parser
        spec.input('metadata.options.parser_name', valid_type=six.string_types, default=cls._PARSER, non_db=True)

        spec.input('metadata.options.withmpi', valid_type=bool, default=False)

        # Exit codes
        spec.exit_code(
            100, 'ERROR_NO_RETRIEVED_FOLDER', message='The retrieved folder data node could not be accessed.'
        )

        # Output parameters
        spec.output('output_parameters', valid_type=Dict, required=True, help='the results of the calculation')
        spec.output('relaxed_structure', valid_type=StructureData, required=False, help='relaxed structure')
        spec.output_node = 'output_parameters'

    def prepare_for_submission(self, folder):
        """Create the input files from the input nodes passed to this instance of the `CalcJob`.

        :param folder: an `aiida.common.folders.Folder` to temporarily write files on disk
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        from aiida_orca.utils import OrcaInput  #pylint: disable=import-outside-toplevel

        # create input structure(s)
        if 'structure' in self.inputs:
            self._write_structure(self.inputs.structure, folder, self._INPUT_COORDS_FILE)

        settings = self.inputs.settings.get_dict() if 'settings' in self.inputs else {}

        # create code info
        codeinfo = CodeInfo()
        codeinfo.cmdline_params = settings.pop('cmdline', []) + [self._INPUT_FILE]
        codeinfo.stdout_name = self._OUTPUT_FILE
        codeinfo.join_files = True
        codeinfo.code_uuid = self.inputs.code.uuid

        # create calc info
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.cmdline_params = codeinfo.cmdline_params
        calcinfo.stdin_name = self._INPUT_FILE
        calcinfo.stdout_name = self._OUTPUT_FILE
        calcinfo.codes_info = [codeinfo]

        # files or additional structures
        if 'file' in self.inputs:
            calcinfo.local_copy_list = []
            for name, obj in self.inputs.file.items():
                if name == 'gbw':
                    calcinfo.local_copy_list.append((obj.uuid, obj.filename, 'aiida_old.gbw'))
                else:
                    calcinfo.local_copy_list.append((obj.uuid, obj.filename, obj.filename))

        # Retrive list
        calcinfo.retrieve_list = [self._OUTPUT_FILE, self._GBW_FILE, self._HESSIAN_FILE, self._RELAX_COORDS_FILE]
        calcinfo.retrieve_list += settings.pop('additional_retrieve_list', [])

        # create ORCA input file
        # inp = OrcaInput(self.inputs.parameters.get_dict(), remote_path=remote_path)
        inp = OrcaInput(self.inputs.parameters.get_dict())
        with io.open(folder.get_abs_path(self._INPUT_FILE), mode='w') as fobj:
            fobj.write(inp.render())

        return calcinfo

    @staticmethod
    def _write_structure(structure, folder, name):
        """Function that writes a structure and takes care of element tags"""

        # create file with the structure
        mol = structure.get_pymatgen_molecule()

        # from https://github.com/materialsproject/pymatgen/blob/
        # 5a3284fd2dce70ee27e8291e6558e73beaba5164/pymatgen/io/gaussian.py#L411
        def to_string(num):
            return '%0.6f' % num

        coords = []
        for site in mol:
            coords.append(' '.join([site.species_string, ' '.join([to_string(j) for j in site.coords])]))

        with io.open(folder.get_abs_path(name), mode='w') as fobj:
            fobj.write(u'{}\n\n'.format(len(coords)))
            fobj.write(u'\n'.join(coords))


#EOF
