#!/usr/bin/env bash
# Drive the packaged provider through whichever engine CI installed.
#
# `TF_BIN` names it -- `tofu` or `terraform` -- because the two are not
# interchangeable for this provider. Only Terraform has a `query` command, and
# it is the only path that reaches a list resource; OpenTofu has no `action` or
# `state_store` block at any version, 1.13.0-beta1 included. A suite that runs
# one engine cannot see what the other refuses, and this one ran OpenTofu only.
#
# Extracted from test-conformance.yml rather than parameterised in place: the
# steps were 150 lines of inline bash, and every `tofu` in them had to become a
# variable.
set -euo pipefail

TF_BIN="${TF_BIN:?TF_BIN must name the engine binary (tofu or terraform)}"
SMOKE_DIR="${SMOKE_DIR:-/tmp/smoke-test-production}"
VERIFIER_DIR="examples/resource/private_state_verifier"

rule() { echo "════════════════════════════════════════════════════════════════"; }

smoke_production() {
  rule; echo "🔥 SMOKE TEST 1: Production Mode (Minimal Configuration)"; rule
  mkdir -p "${SMOKE_DIR}"
  cat > "${SMOKE_DIR}/main.tf" <<'EOF'
terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = ">= 0.0.1"
    }
  }
}

provider "pyvider" {}

output "test" {
  value = "smoke test - production mode"
}
EOF
  echo "📋 Configuration:"; cat "${SMOKE_DIR}/main.tf"; echo
  cd "${SMOKE_DIR}"
  echo "🔧 ${TF_BIN} init"; "${TF_BIN}" init; echo
  echo "📊 ${TF_BIN} plan"; "${TF_BIN}" plan; echo
  echo "✅ PASS: smoke test 1"; rule
}

smoke_testmode_rejected() {
  rule; echo "🔥 SMOKE TEST 2: Test Mode Rejection"; rule
  cd "${VERIFIER_DIR}"
  unset PYVIDER_TESTMODE
  echo "🔧 ${TF_BIN} init"; "${TF_BIN}" init; echo
  echo "📊 ${TF_BIN} plan (expecting rejection)"
  set +e
  "${TF_BIN}" plan 2>&1 | tee /tmp/testmode-false.log
  local rc=${PIPESTATUS[0]}
  set -e
  if [ "${rc}" -eq 0 ]; then
    echo "❌ FAIL: test-only component was NOT rejected"; cat /tmp/testmode-false.log; exit 1
  fi
  # Two rejections are both correct, and which one the engine reports depends on
  # whether it already knows the type.
  #
  # A fresh plan has no state, so the config is validated against the advertised
  # schema. pyvider filters test-only components out of that schema in
  # production mode (handlers/utils.py:180), so the type is simply not offered
  # and the answer is "Invalid resource type".
  #
  # The friendlier "requires test mode" diagnostic (handlers/utils.py:253)
  # guards read_resource and import_resource_state, reached only when the type
  # is already in state -- a plan cannot get there.
  #
  # Accepting only the second made this step fail for a provider refusing
  # exactly as intended.
  if grep -qi "invalid resource type\|test-only.*requires test mode\|test mode.*required\|does not support resource type" /tmp/testmode-false.log; then
    echo "✅ PASS: test-only component correctly rejected without test mode"; rule
  else
    echo "❌ FAIL: plan failed with an unexpected error (exit ${rc})"; cat /tmp/testmode-false.log; exit 1
  fi
}

smoke_testmode_ok() {
  rule; echo "🔥 SMOKE TEST 3: Test Mode Success"; rule
  cd "${VERIFIER_DIR}"
  # The previous smoke test left an init'd directory behind.
  rm -rf .terraform terraform.tfstate* .terraform.lock.hcl
  export PYVIDER_TESTMODE=true
  echo "   PYVIDER_TESTMODE=${PYVIDER_TESTMODE}"; echo
  echo "🔧 ${TF_BIN} init"; "${TF_BIN}" init; echo
  echo "📊 ${TF_BIN} plan"; "${TF_BIN}" plan; echo
  echo "🚀 ${TF_BIN} apply -auto-approve"; "${TF_BIN}" apply -auto-approve; echo
  echo "📤 ${TF_BIN} output"; "${TF_BIN}" output; echo
  echo "✅ PASS: test-only component works with test mode enabled"; rule
}

full_suite() {
  rule; echo "🧪 FULL CONFORMANCE SUITE (${TF_BIN})"; rule
  export PYVIDER_TESTMODE=true
  # stir prefers OpenTofu wherever both are installed, so the engine is named
  # rather than inferred. Requirement sidecars in the corpus skip the
  # directories a given engine cannot run, with the reason.
  export TOFUSOUP_TF_COMMAND="${TF_BIN}"
  echo "   PYVIDER_TESTMODE=${PYVIDER_TESTMODE}"
  echo "   TOFUSOUP_TF_COMMAND=${TOFUSOUP_TF_COMMAND}"; echo
  cd examples
  soup stir --recursive
  echo; echo "✅ All provider conformance tests passed"; rule
}

case "${1:-}" in
  smoke-production)         smoke_production ;;
  smoke-testmode-rejected)  smoke_testmode_rejected ;;
  smoke-testmode-ok)        smoke_testmode_ok ;;
  full)                     full_suite ;;
  *) echo "usage: $0 {smoke-production|smoke-testmode-rejected|smoke-testmode-ok|full}" >&2; exit 2 ;;
esac
