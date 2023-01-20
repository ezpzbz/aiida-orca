# -*- coding: utf-8 -*-
"""AiiDA-ORCA output parser"""
import pathlib
import shutil
import tempfile

import numpy as np

from pymatgen.core import Molecule

from aiida.parsers import Parser
from aiida.common import OutputParsingError, NotExistent
from aiida.engine import ExitCode
from aiida.orm import Dict, StructureData

from .cclib.utils import PeriodicTable
from .cclib.ccio import ccread


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
        try:
            out_folder = self.retrieved
        except NotExistent:
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        process_cls = self.node.process_class
        fname_out = process_cls._OUTPUT_FILE  # pylint: disable=protected-access
        fname_relaxed = process_cls._RELAX_COORDS_FILE  # pylint: disable=protected-access

        if fname_out not in out_folder.list_object_names():
            return process_cls.exit_codes.ERROR_OUTPUT_STDOUT_MISSING

        try:
            with self.retrieved.open(fname_out, 'rb') as handle:
                with tempfile.NamedTemporaryFile('w+b') as tmpfile:
                    shutil.copyfileobj(handle, tmpfile)
                    parsed_obj = ccread(tmpfile.name)
                parsed_dict = parsed_obj.getattributes()
        except Exception:  # pylint: disable=broad-except
            return self.exit_codes.ERROR_OUTPUT_STDOUT_PARSE

        def _remove_nan(parsed_dictionary: dict) -> dict:
            """cclib parsed object may contain nan values in ndarray.
            It will results in an exception in aiida-core which comes from
            json serialization and thereofore dictionary cannot be stored.
            This removes nan values to remedy this issue.
            See:
            https://github.com/aiidateam/aiida-core/issues/2412
            https://github.com/aiidateam/aiida-core/issues/3450

            Args:
                parsed_dictionary (dict): Parsed dictionary from `cclib`

            Returns:
                dict: Parsed dictionary without `NaN`
            """

            for key, value in parsed_dictionary.items():
                if isinstance(value, np.ndarray):
                    non_nan_value = np.nan_to_num(value, nan=123456789, posinf=2e308, neginf=-2e308)
                    parsed_dictionary.update({key: non_nan_value})

            # Hack for full TDDFT calculations without the TDA approximation,
            # which do not provide CI coefficients and cclib parser returns NaNs.
            # In this case we're deleting the entry,
            # which seems safer than returning bogus info.
            # This is not handled by the code above
            # because the value is not a numpy array.
            if 'etsecs' in parsed_dictionary and np.isnan(parsed_dictionary['etsecs'][0][0][-1]):
                del parsed_dictionary['etsecs']

            return parsed_dictionary

        output_dict = _remove_nan(parsed_dict)

        if parsed_dict.get('optdone', False):
            with out_folder.open(fname_relaxed, 'rb') as handle:
                with tempfile.NamedTemporaryFile('w+b', suffix=pathlib.Path(fname_relaxed).suffix) as tmpfile:
                    shutil.copyfileobj(handle, tmpfile)
                    tmpfile.flush()
                    relaxed_structure = StructureData(pymatgen_molecule=Molecule.from_file(tmpfile.name))
            self.out('relaxed_structure', relaxed_structure)

        pt = PeriodicTable()  # pylint: disable=invalid-name

        output_dict['elements'] = [pt.element[Z] for Z in output_dict['atomnos'].tolist()]

        self.out('output_parameters', Dict(dict=output_dict))

        return ExitCode(0)
