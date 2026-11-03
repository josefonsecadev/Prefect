#!/bin/bash
set -euo pipefail
set -a
source /runtime/reader.env
set +a
exec /usr/lib/trino/bin/launcher --etc-dir=/etc/trino run
