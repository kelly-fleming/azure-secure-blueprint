#!/usr/bin/env bash
set -Eeuo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$repo_root"

trap 'status=$?; printf "Offline checks failed (exit %s) at line %s.\n" "$status" "$LINENO" >&2; exit "$status"' ERR

if ! command -v bicep >/dev/null 2>&1; then
  printf '%s\n' 'Install standalone Bicep CLI 0.37.4 on PATH; see docs/TOOLCHAIN.md.' >&2
  exit 1
fi
if ! command -v python >/dev/null 2>&1; then
  printf '%s\n' 'Install Python 3.12 or newer on PATH as python; see docs/VALIDATION.md.' >&2
  exit 1
fi
if ! python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)'; then
  printf '%s\n' 'Python 3.12 or newer is required; ensure python on PATH selects that interpreter.' >&2
  exit 1
fi

mkdir -p -- build
rm -f -- build/main.json build/dev.parameters.json

bicep lint infra/main.bicep
bicep build infra/main.bicep --outfile build/main.json
bicep build-params params/dev.bicepparam --outfile build/dev.parameters.json
python -m unittest discover -s tests -v
