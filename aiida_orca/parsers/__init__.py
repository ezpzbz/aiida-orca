"""AiiDA-ORCA output parser"""
import io
import os
import re
import numpy as np
from cclib import io
from cclib.parser.utils import PeriodicTable

import pymatgen as mp

from aiida.parsers import Parser
from aiida.common import OutputParsingError, NotExistent
from aiida.engine import ExitCode
from aiida.orm import Dict, SinglefileData, StructureData


class OrcaBaseParser(Parser):
    """Basic AiiDA parser for the output of Orca"""

    def parse(self, **kwargs):
        """
        It uses cclib to get the output dictionary.
        Herein, we report all parsed data by ccli in output_dict which
        can be parsed further at workchain level.
        If it would be an optimization run, the relaxed structure also will
        be stored under relaxed_structure key.
        """
        opt_run = False

        try:
            out_folder = self.retrieved
        except NotExistent:
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        fname_out = self.node.process_class._OUTPUT_FILE  #pylint: disable=protected-access
        fname_relaxed = self.node.process_class._RELAX_COORDS_FILE  #pylint: disable=protected-access
        # fname_traj = self.node.process_class._TRAJECTORY_FILE  #pylint: disable=protected-access
        # fname_hessian = self.node.process_class._HESSIAN_FILE  #pylint: disable=protected-access

        if fname_out not in out_folder._repository.list_object_names():  #pylint: disable=protected-access
            raise OutputParsingError('Orca output file not retrieved')

        parsed_obj = io.ccread(os.path.join(out_folder._repository._get_base_folder().abspath, fname_out))  #pylint: disable=protected-access

        parsed_dict = parsed_obj.getattributes()

        def _remove_nan(parsed_dictionary):
            """
            cclib parsed object may contain nan values in ndarray.
            It will results in an exception in aiida-core which comes from
            json serialization and thereofore dictionary cannot be stored.
            This removes nan values to remedy this issue.
            See:
            https://github.com/aiidateam/aiida-core/issues/2412
            https://github.com/aiidateam/aiida-core/issues/3450
            """
            for key, value in parsed_dictionary.items():
                if isinstance(value, np.ndarray):
                    non_nan_value = np.nan_to_num(value, nan=123456789, posinf=2e308, neginf=-2e308)
                    parsed_dictionary.update({key: non_nan_value})

            return parsed_dictionary

        output_dict = _remove_nan(parsed_dict)

        keywords = output_dict['metadata']['keywords']

        #opt_pattern = re.compile('(GDIIS-)?[CZ?OPT]', re.IGNORECASE)

        #if any(re.match(opt_pattern, keyword) for keyword in keywords):
        #opt_run = True
        opt_run = False
        for keyword in keywords:
            if 'opt' in keyword.lower():
                opt_run = True

        if opt_run:
            relaxed_structure = StructureData(
                pymatgen_molecule=mp.Molecule.
                from_file(os.path.join(out_folder._repository._get_base_folder().abspath, fname_relaxed))  #pylint: disable=protected-access
            )
            # relaxation_trajectory = SinglefileData(
            #     file=os.path.join(out_folder._repository._get_base_folder().abspath, fname_traj)  #pylint: disable=protected-access
            # )
            self.out('relaxed_structure', relaxed_structure)
            # self.out('relaxation_trajectory', relaxation_trajectory)

        pt = PeriodicTable()  #pylint: disable=invalid-name

        output_dict['elements'] = [pt.element[Z] for Z in output_dict['atomnos'].tolist()]

        self.out('output_parameters', Dict(dict=output_dict))

        return ExitCode(0)


#EOF
