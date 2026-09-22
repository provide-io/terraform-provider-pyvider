# Reproduce the packaged provider linting proof

This repository carries a recorded and machine-checked proof that provider-native
lint findings survive packaging and reach real protocol clients. The proof uses
one coordinated provider binary throughout; it does not substitute editable
Python imports for the packaged artifact.

Pyvider's author-facing lint API is supported. OpenTofu describes its built-in
linting feature as experimental in v1.13.0-rc1. The proof keeps Pyvider's
rules independently selectable while following the upstream implementation as
it evolves.

## What the proof covers

[OpenTofu v1.13.0-rc1][prerelease] validates the real configuration in
[`tests/e2e/provider-linting/main.tf`][opentofu-fixture].
OpenTofu core reaches 4/7 provider validation paths: provider configuration, managed resource, data
source, and ephemeral resource. Its JSON diagnostics are checked for the exact
rule, severity, detail, attribute path, source range, default-off behavior,
configuration and environment selection, and exact exclusion. Validation also
proves that the deliberately unreachable HTTP data source is never contacted.

TofuSoup 0.8.2 directly proves 7/7 paths against the same packaged binary. Its
direct provider-validation lane covers the preceding four paths plus list
resource, action, and state store.

The primary recording is the OpenTofu demonstration. It shows the ordinary
validation flow and the four paths OpenTofu currently reaches. The technical
recording is direct provider validation. It shows seven readable rule
observations through the same packaged provider, including the three paths
OpenTofu core does not reach today. The lifecycle fixture at
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

## Build one release candidate from public packages

Start from a clean checkout of this repository. The stack builder pins
Pyvider 0.8.1 and `pyvider-components` 0.8.0 from public PyPI, verifies the
disposable lock contains only registry sources, hashes the exact wheels packed
by Flavorpack, resolves their public release tags to commits, and writes
`dist/provider-linting-build-provenance.json` beside the candidate archive.

```shell
make build-linting-stack

lint_binary="$PWD/dist/$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')/terraform-provider-pyvider_v$(cat VERSION)"
export PYVIDER_CONFORMANCE_PSP="$lint_binary"
```

Do not rebuild between the following layers. Each target accepts the explicit
binary, and the OpenTofu experimental lint validation and recording paths check its SHA-256
against the build provenance before and after execution.

## Run the OpenTofu JSON suite

The target installs the pinned, checksum-verified v1.13.0-rc1 executable into
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

For the deterministic direct-provider result used by the recording, install the
released runner and run the public suite command:

```shell
uv tool install --refresh tofusoup==0.8.2
soup lint tests/e2e/provider-linting/lint.soup.toml \
  --provider "$PYVIDER_CONFORMANCE_PSP" \
  --lane direct
```

## Record and verify the checked artifacts

The recorder runs the OpenTofu and direct-provider demonstrations against one named
package, refuses a binary other than the one named by build provenance, and
verifies its checksum before and after recording. It publishes four checked films
only after verification and rolls back ordinary publication failures:

- [`provider-linting-opentofu.cast`][opentofu-cast] — the deterministic
  OpenTofu demonstration.
- [`provider-linting-direct.cast`][direct-cast] — the deterministic
  seven-path direct-provider recording.
- [`provider-linting-walkthrough.cast`][walkthrough-cast] — the public
  walkthrough that installs released TofuSoup 0.8.2 and shows both lanes.
- [`tutorial-part7-provider-linting.cast`][tutorial-cast] — the Part 7
  walkthrough that tests and packages the checked-in
  [`examples/tutorials/part7-provider-linting`][tutorial-fixture] provider,
  then verifies its authored rule through both public TofuSoup lanes.
- [`provider-linting-proof.json`][manifest] — the schema-v3 manifest that
  records versions, public tag commits and exact wheel hashes, the binary and
  all four recording checksums, the command list, the seven-rule catalog,
  observation channels, the OpenTofu archive checksum, and CI identity.

```shell
PYVIDER_CONFORMANCE_PSP="$lint_binary" ci/record-provider-linting.sh

uv run python ci/verify-provider-linting-proof.py \
  provider-linting-proof.json \
  provider-linting-opentofu.cast \
  provider-linting-direct.cast \
  provider-linting-walkthrough.cast \
  tutorial-part7-provider-linting.cast

uv run pytest tests/proof -q
```

The verifier parses all four complete casts after stripping terminal controls.
It requires the public `soup lint` commands, separate OpenTofu experimental lint validation,
and the direct lane
results, the released TofuSoup walkthrough, all seven readable direct-provider
observations, matching artifact checksums, the pinned prerelease, and provenance
without secrets or local paths. The manifest's provider revision names the exact
source tree used to build the checked binary; a later repository commit may add
only the generated proof metadata, so compare the recorded revision and hashes
rather than inferring provenance from a filename or a “latest” build.

## Retrieve the exact CI proof

The opt-in `provider-linting-proof` job in `build-provider.yml` downloads that
same run's `provider-linux_amd64` matrix artifact and never invokes Flavorpack
again. It uploads one checked artifact named `provider-linting-proof`.
Identify the unique successful numeric run ID for the intended provider
commit; never substitute another successful run. Then download and verify only
that run:

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
  "$proof_dir/provider-linting-direct.cast" \
  "$proof_dir/provider-linting-walkthrough.cast" \
  "$proof_dir/tutorial-part7-provider-linting.cast"
```

Before publishing the downloaded files, compare the manifest's provider commit
with the workflow head SHA, compare both dependency tag commits and wheel
SHA-256 values with the public releases, and compare its provider-binary checksum with
`provider-linting-build-provenance.json` from the same artifact.

## Upstream basis and migration boundary

The selection model and user-facing semantics follow OpenTofu's accepted
[built-in linter RFC][rfc], [implementation tracker][tracker], [initial
implementation][implementation], and the pinned [v1.13.0-rc1 release][prerelease].
Pyvider does not invent protocol fields. When an official provider-lint protocol
exists, the compatibility adapter can be replaced while rule implementations,
IDs, groups, selectors, and documentation remain stable.

[opentofu-fixture]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/tests/e2e/provider-linting/main.tf
[tofusoup-fixture]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/tests/proof/fixtures/provider-linting/main.tf
[opentofu-cast]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/provider-linting-opentofu.cast
[direct-cast]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/provider-linting-direct.cast
[walkthrough-cast]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/provider-linting-walkthrough.cast
[tutorial-cast]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/tutorial-part7-provider-linting.cast
[tutorial-fixture]: https://github.com/provide-io/terraform-provider-pyvider/tree/main/examples/tutorials/part7-provider-linting
[manifest]: https://github.com/provide-io/terraform-provider-pyvider/blob/main/provider-linting-proof.json
[rfc]: https://github.com/opentofu/opentofu/blob/main/rfc/20260406-linting.md
[tracker]: https://github.com/opentofu/opentofu/issues/4310
[implementation]: https://github.com/opentofu/opentofu/pull/4337
[prerelease]: https://github.com/opentofu/opentofu/releases/tag/v1.13.0-rc1
