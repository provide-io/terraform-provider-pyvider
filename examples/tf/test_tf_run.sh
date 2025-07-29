#!/usr/bin/env bash
set -euo pipefail

trap 'echo "🛑 Interrupted by user."; exit 1' SIGINT

for t in *_test; do
  cd "$t"

  rm -rf .terraform* terraform.* >/dev/null 2>&1 || true

  echo "------------------------------------------------------------------"

  if tofu init -reconfigure -upgrade -input=false >/dev/null 2>&1; then
    echo "### ${t} init success. ###########################################"
    tofu plan -input=false \
      || echo "*** aww $t did not plan properly *********************************"
  else
    echo "*** aww $t failed to init ****************************************"
  fi

  echo; echo
  cd ..
done
