# Split provider-linting recordings — design

## Decision

Replace the mixed provider-linting recording with two purpose-specific recordings.

1. **OpenTofu demonstration** (`provider-linting-opentofu.cast`) is the primary
   page player. It shows a real pinned OpenTofu run: linting off by default,
   all Pyvider rules selected, the four validation paths OpenTofu currently
   reaches, and an exact-rule exclusion. It deliberately contains neither
   TofuSoup's lifecycle dashboard nor direct-RPC output.
2. **Direct coverage proof** (`provider-linting-direct-rpc.cast`) is the
   technical player. It drives all seven provider validation RPCs through the
   packaged provider and presents one readable result line per rule, followed
   by a 7/7 summary and the package checksum.

The generic `soup stir` lifecycle run remains part of the repository's normal
conformance coverage, but it is not part of either linting recording. It
answers whether a provider-only fixture can run a lifecycle, not whether lint
rules were observed.

## Evidence contract

The proof manifest becomes a two-cast manifest. It pins the exact checksum and
repository-relative path of both recordings, the same packaged-provider
checksum, source revisions, OpenTofu archive, command catalog, and seven-rule
catalog. The verifier parses the direct recording's readable rows rather than
requiring JSON Lines. A single failed or missing result invalidates the proof.

The direct runner supports two explicit formats:

- `json-lines` for automation and existing protocol-oriented uses;
- `terminal` for the technical recording, with stable, human-readable rows.

## Site experience

The linting page leads with the OpenTofu demonstration under a precise title:
“OpenTofu validation — four currently reached paths.” A second “Technical
coverage” section embeds the direct-RPC cast and says what it proves and what
it does not: all seven Pyvider hooks were reached through the same package; it
does not imply that OpenTofu core reaches all seven today.

The checked manifest and both cast downloads remain available. Preview smoke
and rendered-page contracts must require both players and assets.

## Verification

Tests first establish that the manifest rejects a missing second cast and that
the direct proof accepts seven readable rows but rejects an omitted row. Site
tests first establish that the page embeds both distinct casts and that the
preview probe fetches both files. The final run rebuilds one coordinated
provider package, records both casts, verifies the manifest, syncs the exact
CI artifact to the site, builds Hugo, and deploys only a Cloudflare Pages
feature preview.
