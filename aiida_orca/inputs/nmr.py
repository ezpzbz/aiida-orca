"""Typed input builder for NMR shielding/coupling calculations."""

from ._common import build_parameters


def build_nmr_inputs(
    *,
    functional: str,
    basis: str,
    charge: int,
    multiplicity: int,
    nuclei: str | None = None,
    extra_keywords: list[str] | None = None,
    blocks: dict | None = None,
) -> dict:
    """Build the ``parameters`` dict for an NMR calculation.

    :param functional: method/functional, e.g. ``'BP86'``.
    :param basis: basis set, e.g. ``'DEF2-TZVP'``.
    :param charge: total molecular charge.
    :param multiplicity: spin multiplicity.
    :param nuclei: value for the ``%eprnmr NUCLEI`` keyword, e.g. ``'ALL H {SHIFT, SSALL}'``.
    :param extra_keywords: tokens for an additional ``!`` line.
    :param blocks: additional ``%block ... end`` sections; merged with the ``eprnmr``
        block generated from ``nuclei``, if both are given.
    """
    keywords = [functional, basis, 'NMR']

    merged_blocks = {key: dict(value) for key, value in (blocks or {}).items()}
    if nuclei:
        # ORCA's %eprnmr NUCLEI keyword requires an `=` before its value
        # (e.g. `NUCLEI = ALL H {SHIFT, SSALL}`), unlike other block keywords.
        merged_blocks.setdefault('eprnmr', {})['NUCLEI'] = f'= {nuclei}'

    return build_parameters(
        keywords=keywords,
        charge=charge,
        multiplicity=multiplicity,
        blocks=merged_blocks or None,
        extra_keywords=extra_keywords,
    )
