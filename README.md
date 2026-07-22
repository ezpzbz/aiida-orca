![logo](./miscellaneous/aiida-orca_logo.png)

# aiida-orca
[AiiDA](www.aiida.net) plugin for [orca](https://orcaforum.kofo.mpg.de/app.php/portal) package

**DISCLAIMER**: Under heavy development!

[![Actions Status](https://github.com/pzarabadip/aiida-orca/workflows/Build/badge.svg)](https://github.com/pzarabadip/aiida-orca/actions)
[![PyPI version](https://badge.fury.io/py/aiida-orca.svg)](https://badge.fury.io/py/aiida-orca)
[![Docs status](https://readthedocs.org/projects/aiida-orca/badge)](http://aiida-orca.readthedocs.io/)
[![codecov](https://codecov.io/gh/ezpzbz/aiida-orca/branch/main/graph/badge.svg)](https://codecov.io/gh/ezpzbz/aiida-orca)
[![GitHub license](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/pzarabadip/aiida-orca/blob/master/LICENSE)

Compatible with AiiDA >=2.1,<3 and ORCA up to v6 (see [CHANGELOG](CHANGELOG.md)).


<!-- [![PyPI version](https://badge.fury.io/py/aiida-orca.svg)](https://badge.fury.io/py/aiida-orca) -->
<!-- [![PyPI pyversions](https://img.shields.io/pypi/pyversions/aiida-orca.svg)](https://pypi.python.org/pypi/aiida-orca/) -->

<!-- [![DOI](https://zenodo.org/badge/201230518.svg)](https://zenodo.org/badge/latestdoi/201230518) -->


# Installation
The latest release can be installed from `PyPI`
```console
pip install aiida-orca
```

The current development version can be installed via
```console
git clone https://github.com/pzarabadip/aiida-orca.git
cd aiida-orca
pip install .
```

For development, we use [uv](https://docs.astral.sh/uv/) for dependency management:
```console
git clone https://github.com/pzarabadip/aiida-orca.git
cd aiida-orca
make install  # or: uv sync && uv run pre-commit install
make test     # or: uv run pytest tests
make check    # or: uv run ruff check . && uv run mypy ...
```

# aiida-common-workflows
The `aiida-orca` package is available in the
[aiida-common-workflow](https://github.com/aiidateam/aiida-common-workflows) package.
You may try it to have a quick setup and exploration of `aiida-orca` and many more packages.
For further details, please check [our paper](https://www.nature.com/articles/s41524-021-00594-6) on `aiida-common-worlflows`.

# Contribution guide
We welcome contribution to the code either it is a new feature implementation or bug fix.
Please check the [Developer Guide](https://aiida-orca.readthedocs.io/en/develop/developer_guide/index.html)
in documentation for the instructions.

# Issue reporting
Please feel free to open an issue to report bugs or requesting new features.


# Acknowledgment
I would like to thank the funding received from the European Union’s Horizon 2020 research and innovation programme under the Marie Skłodowska-Curie Actions and cofinancing by the South Moravian Region under agreement 665860. This software reflects only the authors’ view and the EU is not responsible for any use that may be made of the information it contains.

<!-- ![aiida-orca](miscellaneous/ackn_logo.png) -->
