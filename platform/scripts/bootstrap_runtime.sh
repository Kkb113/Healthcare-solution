#!/usr/bin/env bash
# Run inside the existing Ubuntu 24.04 WSL distribution (Java 21 prerequisite).
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
bootstrap_env="$HOME/.venvs/healthcare-bootstrap"
runtime_env="$HOME/.venvs/healthcare-platform"
python3 -m venv "$bootstrap_env"
"$bootstrap_env/bin/python" -m pip install --quiet 'uv==0.12.12'
"$bootstrap_env/bin/uv" python install 3.12.13
"$bootstrap_env/bin/uv" venv "$runtime_env" --python 3.12.13 --allow-existing
"$bootstrap_env/bin/uv" pip sync "$repo_root/platform/requirements-linux.lock" --python "$runtime_env/bin/python" --require-hashes --quiet
"$runtime_env/bin/python" -B "$repo_root/platform/scripts/check_local_runtime.py"
