"""Base work chain to run an ORCA calculation"""

from aiida.common import AttributeDict
from aiida.engine import BaseRestartWorkChain, while_
from aiida.plugins import CalculationFactory

OrcaCalculation = CalculationFactory('orca_main')  # pylint: disable=invalid-name


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

        arguments = [calculation.process_label, calculation.pk, calculation.exit_status, calculation.exit_message]
        self.report('{}<{}> failed with exit status {}: {}'.format(*arguments))
        self.report('Action taken: {}'.format(action))


#EOF
