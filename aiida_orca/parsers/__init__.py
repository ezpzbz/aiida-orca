# -*- coding: utf-8 -*-
"""AiiDA-ORCA output parser"""
import pathlib
import shutil
import tempfile

import ase.io
import numpy as np

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
            # Change this when we drop AiiDA 1.x support
            # with self.retrieved.base.repository.open(fname_out) as handle:
            with self.retrieved.open(fname_out) as handle:
                parsed_obj = ccread(handle)
                parsed_dict = parsed_obj.getattributes()
        except Exception:  # pylint: disable=broad-except
            self.logger.error(f'Could not parse file {fname_out}')
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

            # ORCA does not provide CI coefficients for full TDDFT calculations
            # without the TDA approximation, and cclib parser then returns NaNs in the 'etsecs' field.
            # In this case we're deleting the entry, which seems safer than returning bogus info.
            # This is not handled by the code above because the value is not a numpy array.
            if 'etsecs' in parsed_dictionary and np.isnan(parsed_dictionary['etsecs'][0][0][-1]):
                self.logger.info(
                    'ORCA does not print CI coefficients for full TDDFT, removing "etsecs" field from output dict'
                )
                del parsed_dictionary['etsecs']

            return parsed_dictionary

        output_dict = _remove_nan(parsed_dict)

        if parsed_dict.get('optdone', False):
            # Change this when we drop AiiDA 1.x support
            #with out_folder.base.repository.open(fname_relaxed) as handle:
            with out_folder.open(fname_relaxed) as handle:
                ase_structure = ase.io.read(handle, format='xyz', index=0)
            if not ase_structure:
                self.logger.error(f'Could not read structure from output file {fname_relaxed}')
                return self.exit_codes.ERROR_OUTPUT_PARSING
            # Temporary hack to support AiiDA 1.x, which needs default cell
            # even for non-periodic structures.
            ase_structure.set_cell([1.0, 1.0, 1.0])
            relaxed_structure = StructureData(ase=ase_structure)
            self.out('relaxed_structure', relaxed_structure)

        if output_dict.get('atomnos') is not None:
            pt = PeriodicTable()  # pylint: disable=invalid-name
            output_dict['elements'] = [pt.element[Z] for Z in output_dict['atomnos']]

        self.out('output_parameters', Dict(dict=output_dict))

        if output_dict.get('metadata') and output_dict['metadata'].get('success'):
            return ExitCode(0)
        return self.exit_codes.ERROR_CALCULATION_UNSUCCESSFUL
