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

## Running against a real ORCA install (local dev/validation)

To run calculations end-to-end against a real ORCA binary (not just the unit tests):

```console
ORCA_EXECUTABLE=/path/to/orca ./scripts/setup_local_orca.sh
```

This creates a SQLite-backed AiiDA profile (`verdi presto`) and registers the
binary as an `InstalledCode` named `orca-local@localhost`. If a RabbitMQ broker
is running locally but on an unsupported version (aiida-core currently only
supports `3.6.0 <= version < 3.8.15` — see
`aiida.brokers.rabbitmq.broker.RabbitmqBroker.is_rabbitmq_version_supported`),
stop it first (e.g. `brew services stop rabbitmq`) so the profile is created
without a broker. Synchronous `aiida.engine.run()` calls work fine without a
broker; only the daemon and `submit()` require one.

## Pull requests

Please open an issue first for larger changes so we can discuss the approach.
Keep PRs focused; run `make check` and `make test` before submitting.
