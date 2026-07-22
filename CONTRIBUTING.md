# Contributing

## Development setup

```console
git clone https://github.com/pzarabadip/aiida-orca.git
cd aiida-orca
make install   # uv sync + pre-commit install
```

## Common tasks

```console
make test    # uv run pytest tests
make check   # uv lock --locked, pre-commit run -a, mypy
make build   # uv build
```

Requires a running PostgreSQL and RabbitMQ for the test suite (see
`.github/workflows/ci.yml` for the service configuration used in CI).

## Pull requests

Please open an issue first for larger changes so we can discuss the approach.
Keep PRs focused; run `make check` and `make test` before submitting.
