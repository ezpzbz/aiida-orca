# Changelog

## v1.0.0

### BREAKING

- Dropped support for AiiDA 1.x. `aiida-orca` now requires `aiida-core>=2.1,<3`.
  Existing installations pinned to AiiDA 1.x must upgrade AiiDA before
  upgrading this package.
- Dropped support for Python 3.8-3.10; now requires Python `>=3.11` (tested
  against 3.11-3.14).
- **Reinstall required**: the build backend changed from `flit_core` to
  `hatchling`. Existing editable (`pip install -e .`) installs may have stale
  entry-point metadata after pulling this change — reinstall (`uv sync` or
  `pip install -e . --force-reinstall --no-deps`) if `verdi plugin list`
  stops showing `orca.*` entries.

### Added

- Initial ORCA 6 support in the vendored parser: the restructured TDDFT
  absorption-spectrum output table (new "Transition" column, extra energy
  column, renamed transition-moment columns) is now parsed correctly.
  Verified with synthetic snippet tests (`tests/parsers/test_orca6_format.py`)
  since no real ORCA 6 log fixtures were available; some less common ORCA 6
  spectrum sections (SOC-corrected spectra, excited-state reordering) remain
  unported — see comments at the top of `aiida_orca/parsers/cclib/orcaparser.py`.

### Changed

- Packaging migrated to [uv](https://docs.astral.sh/uv/) with a `hatchling`
  build backend. Development workflow is now `uv sync` / `uv run pytest` /
  `uv run ruff check .`, see the `Makefile` for common tasks.
- Replaced `yapf` + `pylint` with `ruff` for linting and formatting; `mypy`
  is retained for type checking on the same scoped file list as before.
- CI now uses `astral-sh/setup-uv` and runs against Python 3.9/3.10/3.11 with
  `aiida-core~=2.1`.

### Removed

- Removed the AiiDA-1.x compatibility shims in the parser (`self.retrieved.open`
  in favor of `self.retrieved.base.repository.open`, and the dummy-cell
  workaround for non-periodic `StructureData`).
- Removed the `reentry scan` CI step (not applicable to AiiDA 2.x plugin
  discovery).

## v0.7.0 and earlier

No changelog was kept; see git history.
