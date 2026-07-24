#!/usr/bin/env bash
# Set up a local AiiDA profile + ORCA InstalledCode for running/validating
# calculations against a real ORCA binary (development use only).
#
# Usage:
#   ORCA_EXECUTABLE=/path/to/orca ./scripts/setup_local_orca.sh [profile-name]
#
# Notes:
# - Creates a SQLite-backed profile via `verdi presto`.
# - If a RabbitMQ broker is reachable but reports an unsupported version
#   (aiida-core currently only supports 3.6.0 <= version < 3.8.15, see
#   aiida.brokers.rabbitmq.broker.RabbitmqBroker.is_rabbitmq_version_supported),
#   `run()`-based synchronous calculations can crash on completion while
#   broadcasting process state. Stop the broker first (e.g. `brew services
#   stop rabbitmq`) so `verdi presto` creates a broker-less profile instead —
#   broker-less profiles cannot run the daemon/`submit()`, but `run()` works
#   fine and is all local dev/validation needs.
set -euo pipefail

: "${ORCA_EXECUTABLE:?Set ORCA_EXECUTABLE to the path of the ORCA binary}"
PROFILE_NAME="${1:-orca-dev}"

if [ ! -x "$ORCA_EXECUTABLE" ]; then
    echo "error: ORCA_EXECUTABLE ($ORCA_EXECUTABLE) is not an executable file" >&2
    exit 1
fi

verdi presto --profile-name "$PROFILE_NAME"

verdi code create core.code.installed \
    --non-interactive \
    --label orca-local \
    --description "Local ORCA install for dev/validation" \
    --computer localhost \
    --filepath-executable "$ORCA_EXECUTABLE" \
    --default-calc-job-plugin orca.orca \
    --prepend-text "" \
    --append-text ""

echo ""
echo "Profile '$PROFILE_NAME' ready. Code registered as 'orca-local@localhost'."
verdi status
