# -*- coding: utf-8 -*-
"""AiiDA-ORCA input generator"""

from copy import deepcopy


class OrcaInput:
    """Transforms dictionary into ORCA input"""

    def __init__(self, params: dict) -> None:
        """Initializing OrcaInput object

        Args:
            params (dict): Input parameters

        Returns:
            NoReturn: It does not return.
        """

        self._params = deepcopy(params)

    def render(self) -> str:
        """Render input string

        Returns:
            str: The string of input file.
        """
        return '\n'.join(self._render_input(self._params))

    @staticmethod
    def _render_input(params: dict) -> list:
        """Rendering different ORCA input sections

        Args:
            params (dict): Input parameters

        Returns:
            list: List of strings, one per line
        """

        required_keys = ('charge', 'multiplicity')
        for key in required_keys:
            if key not in params:
                raise ValueError(f'Missing mandatory key {key!r} in input parameters')

        output = ['### Generated by AiiDA-ORCA Plugin ###']

        keywords = params.get('input_keywords', ['SP'])
        output.append(f'! {" ".join(keywords)}')

        if extra_keywords := params.get('extra_input_keywords'):
            output.append(f'! {" ".join(extra_keywords)}')

        if blocks := params.get('input_blocks'):
            for key in blocks.keys():
                output.append(f'%{key} ')
                for keyword, val in blocks[key].items():
                    if val is None:
                        output.append(f'\t{keyword}')
                    else:
                        output.append(f'\t{keyword} {val}')
                output.append('end\n')

        # coordinate section
        output.append(f"* xyzfile {params['charge']} {params['multiplicity']} aiida.coords.xyz\n")
        return output
