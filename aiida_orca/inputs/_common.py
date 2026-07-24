"""Shared helpers for typed ORCA input builders."""


def build_parameters(
    *,
    keywords: list[str],
    charge: int,
    multiplicity: int,
    blocks: dict | None = None,
    extra_keywords: list[str] | None = None,
) -> dict:
    """Assemble the ``parameters`` dict consumed by :class:`~aiida_orca.calculations.orca_orca.OrcaCalculation`.

    :param keywords: the ``!`` line tokens (method, basis, job type, ...).
    :param charge: total molecular charge.
    :param multiplicity: spin multiplicity.
    :param blocks: ``%block ... end`` sections, e.g. ``{'eprnmr': {'NUCLEI': '...'}}``.
    :param extra_keywords: tokens for an additional ``!`` line.
    :return: dict shape expected by ``OrcaCalculation``'s ``parameters`` input.
    """
    parameters: dict = {
        'charge': charge,
        'multiplicity': multiplicity,
        'input_keywords': list(keywords),
    }
    if extra_keywords:
        parameters['extra_input_keywords'] = list(extra_keywords)
    if blocks:
        parameters['input_blocks'] = blocks
    return parameters
