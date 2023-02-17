#!/usr/bin/env bash

# declare submodules to validate
declare -a submodules=("aggregator" "api_service" "fma-core" "connectors/django" "clients/python_client")

# start templated
INSTALL_PYTHON=python3
EXIT_CODE=0
# end templated

# loop through each submodule
for SUBMODULE_DIR in "${submodules[@]}"
do
  HERE="$(cd "$(dirname "$0")" && pwd)"
  ARGS=(hook-impl --hook-type=pre-commit)
  ARGS+=(--config "$SUBMODULE_DIR/.pre-commit-config.yaml")
  ARGS+=(--hook-dir "$HERE" -- "$@")

  echo
  echo Submodule: $SUBMODULE_DIR
  echo Args: "${ARGS[@]}"
  if [ -x "$INSTALL_PYTHON" ]; then
    "$INSTALL_PYTHON" -mpre_commit "${ARGS[@]}"
  elif command -v pre-commit > /dev/null; then
    pre-commit "${ARGS[@]}"
  else
    echo '`pre-commit` not found.  Did you forget to activate your virtualenv?' 1>&2
    exit 1
  fi
  EXIT_CODE=$(( $EXIT_CODE ? $EXIT_CODE : $? ))
done
exit $EXIT_CODE
