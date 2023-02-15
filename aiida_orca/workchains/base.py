# -*- coding: utf-8 -*-
"""Base work chain to run an ORCA calculation"""

from aiida.common import AttributeDict
from aiida.engine import BaseRestartWorkChain, ProcessHandlerReport, process_handler, while_
from aiida.plugins import CalculationFactory

OrcaCalculation = CalculationFactory('orca.orca')


class OrcaBaseWorkChain(BaseRestartWorkChain):
    """Workchain to run a orca calculation with automated error handling and restarts."""

    _process_class = OrcaCalculation

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.expose_inputs(OrcaCalculation, namespace='orca')
        spec.outline(
            cls.setup,
            while_(cls.should_run_process)(
                cls.run_process,
                cls.inspect_process,
            ),
            cls.results,
        )
        spec.expose_outputs(OrcaCalculation)
        spec.exit_code(
            300,
            'ERROR_UNKNOWN_UNRECOVERABLE_FAILURE',
            message='The calculation failed with an unidentified unrecoverable error.'
        )
        spec.exit_code(
            301,
            'ERROR_AIIDA_ORCA_UNRECOVERABLE_FAILURE',
            message='The calculation failed with an unrecoverable error coming from aiida-orca.'
        )

    def setup(self):
        """Call the `setup` of the `BaseRestartWorkChain` and then create the inputs dictionary in `self.ctx.inputs`.
        This `self.ctx.inputs` dictionary will be used by the `BaseRestartWorkChain` to submit the calculations in the
        internal loop."""

        super().setup()
        self.ctx.inputs = AttributeDict(self.exposed_inputs(OrcaCalculation, 'orca'))

    def report_error_handled(self, calculation, action):
        """Report an action taken for a calculation that has failed.
        This should be called in a registered error handler if its condition is met and an action was taken.
        :param calculation: the failed calculation node
        :param action: a string message with the action taken"""

        self.report(
            f'{calculation.process_label}<{calculation.pk}> failed with exit status '
            f'{calculation.exit_status}: {calculation.exit_message}'
        )
        self.report(f'Action taken: {action}')

    @process_handler()
    def handle_known_unrecoverable_failure(self, calculation):
        """Handle exit status between 300-399.

           These errors should come from aiida-orca plugin and are not recoverable.
        """
        if calculation.is_failed and calculation.exit_status < 400 and calculation.exit_status > 299:
            self.report_error_handled(calculation, 'unrecoverable aiida-orca error, aborting...')
            return ProcessHandlerReport(True, self.exit_codes.ERROR_AIIDA_ORCA_UNRECOVERABLE_FAILURE)  # pylint: disable=no-member

    @process_handler()
    def handle_unknown_unrecoverable_failure(self, calculation):
        """Handle exit status between 1-299

           These errors come from outside of aiida-orca plugin.
           For now we suppose that all of these are unrecoverable.
        """
        if calculation.is_failed and calculation.exit_status < 300:
            self.report_error_handled(calculation, 'unknown unrecoverable error, aborting...')
            return ProcessHandlerReport(True, self.exit_codes.ERROR_UNKNOWN_UNRECOVERABLE_FAILURE)  # pylint: disable=no-member
