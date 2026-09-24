# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **The conformance run no longer depends on httpbin.org or JSONPlaceholder.**
  The `pyvider_http_api` examples take their URLs from `var.api_base_url` and
  `var.json_api_base_url` (defaulting to the public services, so a reader's
  copy works as written), and every `soup stir` run -- CI, the cast recording
  and `make test-examples` -- now goes through `ci/with-http-api-stub.sh`, which
  starts a small standard-library server on a free loopback port and points both
  variables at it. A slow httpbin.org was what made the `delay/3` example flaky.
  Checked with all outbound HTTP blocked: the examples pass on OpenTofu 1.12.6
  and Terraform 1.16.1 with the server, and fail without it.

### Documentation

- **Examples regenerated from pyvider-components' corrected bundles.** The list
  resource query examples said to run `tofu query`, which does not exist; they
  now name `terraform query` (Terraform 1.14+). The `secret_note` resource
  example declares its measured 1.11 floor for write-only attributes, and the
  `http_api` data source page carries the null-safe example.

## [0.6.1] - 2026-09-22

### Fixed

- **String functions answer like OpenTofu 1.13's go-cty.** Builds now consume
  pyvider-cty 0.6.3, which segments grapheme clusters by Unicode 17.0.0 and maps
  `upper`, `lower` and `title` from Go's Unicode 17.0.0 case tables. The 0.6.0
  binary counted clusters by Unicode 16.0.0 and took case mappings from the
  packaged interpreter's `unicodedata`, so provider functions could disagree
  with OpenTofu's built-ins on characters added since.
- **The `http_api` example survives a failed request.** A request that times
  out or cannot connect reports `error_message` and leaves `status_code` and
  `response_time_ms` null, and the example's comparisons and response-time
  summaries raised on that null instead of reporting the failure. They now
  fall back to `false` or `null`. This failed the conformance run on
  linux_arm64 whenever the example's slow endpoint took longer than its
  10-second timeout.

### Release verification

- **Published releases are verified from their own downloaded bytes.**
  `verify-release.yml` re-checks checksums, the signature, the tag and the
  proof/build binding, then re-runs the linux_amd64 proof against the released
  binary. It runs after every release and can be dispatched against one already
  published; v0.6.0 was verified this way.

## [0.6.0] - 2026-09-22

### Added

- Added seven direct provider lint checks across provider, resource, data
  source, ephemeral resource, list resource, action, and state-store
  configuration paths. Stable selectors can enable all rules, groups, exact
  rules, and exact exclusions.
- Added separate OpenTofu experimental lint validation that reaches four OpenTofu
  paths through ordinary validation RPCs. It does not claim that OpenTofu has
  shipped a provider-lint transport.
- Added three paced, user-runnable recordings and
  `provider-linting-proof.json`: separate direct and OpenTofu lanes and a
  released provider walkthrough. The Part 7 tutorial, which tests, packages, and
  verifies a provider-authored lint rule end to end, lives in
  [provide-io/pyvider-tutorial](https://github.com/provide-io/pyvider-tutorial).

### Supply chain

- Builds now consume Pyvider 0.8.1 and pyvider-components 0.8.0 from public PyPI;
  the proof commands run with released TofuSoup 0.8.2.
  Provenance records each release tag commit, wheel filename, and wheel SHA-256
  instead of injecting sibling source trees.
- Release publication is bound to one successful numeric build run at the
  exact release commit. Linux, macOS, and required Windows archives plus the
  proof files are checksummed, signed, published, downloaded, and reverified.
