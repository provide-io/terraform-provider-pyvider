# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
  `provider-linting-proof.json`, with the same packaged provider verified in
  the direct and OpenTofu lanes.

### Supply chain

- Builds now consume Pyvider 0.8.1 and pyvider-components 0.8.0 from public PyPI;
  the proof commands run with released TofuSoup 0.8.2.
  Provenance records each release tag commit, wheel filename, and wheel SHA-256
  instead of injecting sibling source trees.
- Release publication is bound to one successful numeric build run at the
  exact release commit. Linux, macOS, and required Windows archives plus the
  proof files are checksummed, signed, published, downloaded, and reverified.
