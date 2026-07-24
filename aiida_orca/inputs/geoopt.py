"""Typed input builder for geometry optimization calculations."""

from ._common import build_parameters


def build_geoopt_inputs(
    *,
    functional: str,
    basis: str,
    charge: int,
    multiplicity: int,
    dispersion: str | None = None,
    extra_keywords: list[str] | None = None,
    blocks: dict | None = None,
) -> dict:
    """Build the ``parameters`` dict for a geometry optimization calculation.

    :param functional: method/functional, e.g. ``'PBE'``.
    :param basis: basis set, e.g. ``'DEF2-SVP'``.
    :param charge: total molecular charge.
    :param multiplicity: spin multiplicity.
    :param dispersion: optional dispersion correction keyword, e.g. ``'D4'``.
    :param extra_keywords: tokens for an additional ``!`` line.
    :param blocks: ``%block ... end`` sections, e.g. ``{'geom': {...}}``.
    """
    keywords = [functional]
    if dispersion:
        keywords.append(dispersion)
    keywords.append(basis)
    keywords.append('OPT')

    return build_parameters(
        keywords=keywords,
        charge=charge,
        multiplicity=multiplicity,
        blocks=blocks,
        extra_keywords=extra_keywords,
    )
