![logo](./miscellaneous/aiida-orca_logo.png)

# aiida-orca
[AiiDA](www.aiida.net) plugin for [orca](https://orcaforum.kofo.mpg.de/app.php/portal) package

**DISCLAIMER**: Under heavy development!

[![Actions Status](https://github.com/pzarabadip/aiida-orca/workflows/Build/badge.svg)](https://github.com/pzarabadip/aiida-orca/actions)
[![PyPI version](https://badge.fury.io/py/aiida-orca.svg)](https://badge.fury.io/py/aiida-orca)
[![Docs status](https://readthedocs.org/projects/aiida-orca/badge)](http://aiida-orca.readthedocs.io/)
[![codecov](https://codecov.io/gh/pzarabadip/aiida-orca/branch/develop/graph/badge.svg)](https://codecov.io/gh/pzarabadip/aiida-orca)
[![GitHub license](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/pzarabadip/aiida-orca/blob/master/LICENSE)

Compatible with:

[![aiida-core](https://img.shields.io/badge/AiiDA-%3E=1.6,%3C3.0-007ec6.svg?logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAACMAAAAhCAYAAABTERJSAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAFhgAABYYBG6Yz4AAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAUbSURBVFiFzZhrbFRVEMd%2Fc%2B5uu6UUbIFC%2FUAUVEQCLbQJBIiBDyiImJiIhmohYNCkqJAQxASLF8tDgYRHBLXRhIcKNtFEhVDgAxBJqgmVh4JEKg3EIn2QYqBlt917xg%2BFss%2ByaDHOtzsz5z%2B%2FuZl7ztmF%2F5HJvxVQN6cPYX8%2FPLnOmsvNAvqfwuib%2FbNIk9cQeQnLcKRL5xLIV%2Fic9eJeunjPYbRs4FjQSpTB3aS1IpRKeeOOewajy%2FKKEO8Q0DuVdKy8IqsbPulxGHUfCBBu%2BwUYGuFuBTK7wQnht6PEbf4tlRomVRjCbXNjQEB0AyrFQOL5ENIJm7dTLZE6DPJCnEtFZVXDLny%2B4Sjv0PmmYu1ZdUek9RiMgoDmJ8V0L7XJqsZ3UW8YsBOwEeHeeFce7jEYXBy0m9m4BbXqSj2%2Bxnkg26MCVrN6DEZcwggtd8pTFx%2Fh3B9B50YLaFOPwXQKUt0tBLegtSomfBlfY13PwijbEnhztGzgJsK5h9W9qeWwBqjvyhB2iBs1Qz0AU974DciRGO8CVN8AJhAeMAdA3KbrKEtvxhsI%2B9emWiJlGBEU680Cfk%2BSsVqXZvcFYGXjF8ABVJ%2BTNfVXehyms1zzn1gmIOxLEB6E31%2FWBe5rnCarmo7elf7dJEeaLh80GasliI5F6Q9cAz1GY1OJVNDxTzQTw7iY%2FHEZRQY7xqJ9RU2LFe%2FYqakdP911ha0XhjjiTVAkDwgatWfCGeYocx8M3glG8g8EXhSrLrHnEFJ5Ymow%2FkhIYv6ttYUW1iFmEqqxdVoUs9FmsDYSqmtmJh3Cl1%2BVtl2s7owDUdocR5bceiyoSivGTT5vzpbzL1uoBpmcAAQgW7ArnKD9ng9rc%2BNgrobSNwpSkkhcRN%2BvmXLjIsDovYHHEfmsYFygPAnIDEQrQPzJYCOaLHLUfIt7Oq0LJn9fxkSgNCb1qEIQ5UKgT%2Fs6gJmVOOroJhQBXVqw118QtWLdyUxEP45sUpSzqP7RDdFYMyB9UReMiF1MzPwoUqHt8hjGFFeP5wZAbZ%2F0%2BcAtAAcji6LeSq%2FMYiAvSsdw3GtrfVSVFUBbIhwRWYR7yOcr%2FBi%2FB1MSJZ16JlgH1AGM3EO2QnmMyrSbTSiACgFBv4yCUapZkt9qwWVL7aeOyHvArJjm8%2Fz9BhdI4XcZgz2%2FvRALosjsk1ODOyMcJn9%2FYI6IrkS5vxMGdUwou2YKfyVqJpn5t9aNs3gbQMbdbkxnGdsr4bTHm2AxWo9yNZK4PXR3uzhAh%2BM0AZejnCrGdy0UvJxl0oMKgWSLR%2B1LH2aE9ViejiFs%2BXn6bTjng3MlIhJ1I1TkuLdg6OcAbD7Xx%2Bc3y9TrWAiSHqVkbZ2v9ilCo6s4AjwZCzFyD9mOL305nV9aonvsQeT2L0gVk4OwOJqXXVRW7naaxswDKVdlYLyMXAnntteYmws2xcVVZzq%2BtHPAooQggmJkc6TLSusOiL4RKgwzzYU1iFQgiUBA1H7E8yPau%2BZl9P7AblVNebtHqTgxLfRqrNvZWjsHZFuqMqKcDWdlFjF7UGvX8Jn24DyEAykJwNcdg0OvJ4p5pQ9tV6SMlP4A0PNh8aYze1ArROyUNTNouy8tNF3Rt0CSXb6bRFl4%2FIfQzNMjaE9WwpYOWQnOdEF%2BTdJNO0iFh7%2BI0kfORzQZb6P2kymS9oTxzBiM9rUqLWr1WE5G6ODhycQd%2FUnNVeMbcH68hYkGycNoUNWc8fxaxfwhDbHpfwM5oeTY7rUX8QAAAABJRU5ErkJggg%3D%3D)](https://www.aiida.net/)
[![orca](https://img.shields.io/badge/ORCA-v4.2.1-007ec6.svg)](https://orcaforum.kofo.mpg.de/app.php/portal)
[![orca](https://img.shields.io/badge/ORCA-v5.0-007ec6.svg)](https://orcaforum.kofo.mpg.de/app.php/portal)
[![openmpi](https://img.shields.io/badge/OpenMPI-v2.1.6-007ec6.svg)](https://www.open-mpi.org/)


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
