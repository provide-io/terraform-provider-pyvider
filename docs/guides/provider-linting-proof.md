# Reproduce the packaged provider linting proof

This repository carries a recorded and machine-checked proof that provider-native
lint findings survive packaging and reach real protocol clients. The proof uses
one coordinated provider binary throughout; it does not substitute editable
Python imports for the packaged artifact.

Pyvider's author-facing lint API is supported.
OpenTofu describes its built-in linting feature as experimental.
Because tfprotov6 does not yet define native provider-lint messages or pass core
lint selections to providers, provider findings are transported as ordinary
warnings: ordinary warning diagnostics are a temporary compatibility bridge,
not the public author API or a new wire protocol.

## What the proof covers

[OpenTofu v1.13.0-beta1][beta] validates the real configuration in
[`tests/e2e/provider-linting/main.tf`][opentofu-fixture].
OpenTofu core reaches 4/7 provider validation paths: provider configuration, managed resource, data
source, and ephemeral resource. Its JSON diagnostics are checked for the exact
rule, severity, detail, attribute path, source range, default-off behavior,
configuration and environment selection, and exact exclusion. Validation also
proves that the deliberately unreachable HTTP data source is never contacted.

OpenTofu declares action, list-resource, and state-store validation RPCs but
does not currently call them from core. TofuSoup directly proves 7/7 paths
against the same packaged binary. The direct RPC suite covers the preceding
four paths plus list resource, action, and state store.

The primary recording is the OpenTofu demonstration. It shows the ordinary
validation flow and the four paths OpenTofu currently reaches; it does not show
the generic `soup stir` lifecycle dashboard or direct-RPC output. The technical recording is direct RPC coverage. It shows seven readable rule observations
through the same packaged provider, including the three paths OpenTofu core
does not reach today. The lifecycle fixture at
[`tests/proof/fixtures/provider-linting/main.tf`][tofusoup-fixture] remains
normal conformance coverage, but it answers a different question and is not a
linting recording.

| Component path | Rule | OpenTofu | TofuSoup direct |
| --- | --- | ---: | ---: |
| Provider | `provide-io/pyvider:insecure-tls` | Yes | Yes |
| Managed resource | `provide-io/pyvider:world-writable-directory` | Yes | Yes |
| Data source | `provide-io/pyvider:insecure-http` | Yes | Yes |
| Ephemeral resource | `provide-io/pyvider:long-lived-lease` | Yes | Yes |
| List resource | `provide-io/pyvider:include-hidden-files` | No | Yes |
| Action | `provide-io/pyvider:long-action-timeout` | No | Yes |
| State store | `provide-io/pyvider:relative-state-store-path` | No | Yes |

The distinction is important: TofuSoup is additional direct protocol proof,
not evidence that OpenTofu core traverses all seven paths today.

## Select provider rules

Provider-side selection and OpenTofu's `-lint` flag are currently separate.
Enable every Pyvider provider rule for one command with:

```shell
PYVIDER_LINT=provide-io/pyvider:all tofu validate
```

Choose a group or exclude one exact rule using the OpenTofu-compatible selector
grammar:

```shell
PYVIDER_LINT=provide-io/pyvider:security tofu validate
PYVIDER_LINT='provide-io/pyvider:all,!provide-io/pyvider:insecure-http' tofu validate
```

An explicitly empty environment value overrides a file setting and disables
provider linting:

```shell
PYVIDER_LINT='' tofu validate
```

For persistent provider selection, add `pyvider.toml` beside the configuration:

```toml
[lint]
rules = ["provide-io/pyvider:all", "!provide-io/pyvider:insecure-http"]
```

To opt into both experimental OpenTofu core rules and Pyvider provider rules,
enable each layer explicitly:

```shell
PYVIDER_LINT=provide-io/pyvider:all tofu validate -lint=all
```

## Build one coordinated package

Start from clean checkouts of this repository, Pyvider, and
`pyvider-components`. The stack builder records each exact Git revision and
source-archive hash, inventories the packaged wheels, and writes
`dist/provider-linting-build-provenance.json` beside the binary.

```shell
export PYVIDER_SOURCE="$(cd ../pyvider && pwd -P)"
export COMPONENTS_SOURCE="$(cd ../pyvider-components && pwd -P)"

make build-linting-stack \
  PYVIDER_SOURCE="$PYVIDER_SOURCE" \
  COMPONENTS_SOURCE="$COMPONENTS_SOURCE"

lint_binary="$PWD/dist/$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')/terraform-provider-pyvider_v$(cat VERSION)"
export PYVIDER_CONFORMANCE_PSP="$lint_binary"
```

The exported, canonical source paths remain available to the later conformance
targets so their provenance checks inspect the exact coordinated checkouts.
Do not rebuild between the following layers. Each target accepts the explicit
binary, and the OpenTofu and recording paths check its SHA-256 against the build
provenance before and after execution.

## Run the OpenTofu JSON suite

The target installs the pinned, checksum-verified v1.13.0-beta1 executable into
the repository cache, prints the exact version, and runs the JSON assertions
against [`tests/e2e/provider-linting/main.tf`][opentofu-fixture].

```shell
make test-linting-opentofu-binary \
  PYVIDER_CONFORMANCE_PSP="$lint_binary"
```

## Run the TofuSoup direct suite

The conformance target launches the same package over tfplugin6. The linting
module drives all seven validation RPCs directly; the full target also protects
the provider's existing packaged-protocol behavior.

```shell
make test-conformance-binary \
  PYVIDER_CONFORMANCE_PSP="$lint_binary"
```

For the deterministic seven-line observation stream used by the recording, run
the same direct driver explicitly:

```shell
uv run python ci/run-provider-linting-rpcs.py \
  --binary "$PYVIDER_CONFORMANCE_PSP" \
  --selector provide-io/pyvider:all \
  --format json-lines
```

## Record and verify the checked artifacts

The recorder runs the OpenTofu and direct-RPC demonstrations against one named
package, refuses a binary other than the one named by build provenance, and
verifies its checksum before and after recording. It publishes both checked artifacts only after verification and rolls back ordinary publication failures:

- [`provider-linting-opentofu.cast`][opentofu-cast] — the deterministic
  OpenTofu demonstration.
- [`provider-linting-direct-rpc.cast`][direct-rpc-cast] — the deterministic
  seven-path technical recording.
- [`provider-linting-proof.json`][manifest] — versions, exact source revisions
and archive hashes, binary and recording checksums, the command list, the
seven-rule catalog, observation channels, OpenTofu archive checksum, and CI
identity.

```shell
PYVIDER_CONFORMANCE_PSP="$lint_binary" ci/record-provider-linting.sh

uv run python ci/verify-provider-linting-proof.py \
  provider-linting-proof.json \
  provider-linting-opentofu.cast \
  provider-linting-direct-rpc.cast

uv run pytest tests/proof -q
```

The verifier parses both complete casts after stripping terminal controls. It
requires the OpenTofu commands, default-off and exact-exclusion evidence, the
four-path statement, all seven readable direct-RPC observations, matching
artifact checksums, the pinned beta, and provenance without secrets or local
paths.

## Retrieve the exact CI proof

The opt-in `provider-linting-proof` job in `build-provider.yml` builds from
explicit public Pyvider and component Git refs and uploads one artifact also
named `provider-linting-proof`. Identify the unique successful numeric run ID
for the intended provider commit; never substitute “latest successful”. Then
download and verify only that run:

```shell
proof_run_id=1234567890
proof_dir=$(mktemp -d /tmp/pyvider-linting-proof.XXXXXX)

gh run download "$proof_run_id" \
  --repo provide-io/terraform-provider-pyvider \
  --name provider-linting-proof \
  --dir "$proof_dir"

uv run python ci/verify-provider-linting-proof.py \
  "$proof_dir/provider-linting-proof.json" \
  "$proof_dir/provider-linting-opentofu.cast" \
  "$proof_dir/provider-linting-direct-rpc.cast"
```

Before publishing the downloaded files, also compare the manifest's provider,
Pyvider, and `pyvider-components` revisions with the refs used for that workflow
dispatch, and compare its provider-binary checksum with
`provider-linting-build-provenance.json` from the same artifact.

## Upstream basis and migration boundary

The selection model and user-facing semantics follow OpenTofu's accepted
[built-in linter RFC][rfc], [implementation tracker][tracker], [initial
implementation][implementation], and the pinned [v1.13.0-beta1 release][beta].
Pyvider does not invent protocol fields. When an official provider-lint protocol
exists, the compatibility adapter can be replaced while rule implementations,
IDs, groups, selectors, and documentation remain stable.

[opentofu-fixture]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/tests/e2e/provider-linting/main.tf
[tofusoup-fixture]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/tests/proof/fixtures/provider-linting/main.tf
[opentofu-cast]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/provider-linting-opentofu.cast
[direct-rpc-cast]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/provider-linting-direct-rpc.cast
[manifest]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/provider-linting-proof.json
[rfc]: https://github.com/opentofu/opentofu/blob/main/rfc/20260406-linting.md
[tracker]: https://github.com/opentofu/opentofu/issues/4310
[implementation]: https://github.com/opentofu/opentofu/pull/4337
[beta]: https://github.com/opentofu/opentofu/releases/tag/v1.13.0-beta1
