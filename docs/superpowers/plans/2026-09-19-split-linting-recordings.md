# Split Linting Recordings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish separate OpenTofu and direct-RPC linting recordings, then make the site lead with the former and link the latter as technical evidence.

**Architecture:** The provider recorder writes two casts from the same pinned package and a schema-v2 manifest hashes both. The direct RPC runner gains a stable terminal format; the verifier checks those human-readable rows. The Hugo page embeds the two distinct static assets and its checks require both.

**Tech Stack:** Python 3.11, pytest, Bash, asciinema v2, Hugo, Cloudflare Pages.

---

### Task 1: Make direct RPC evidence readable and verifiable

**Files:**
- Modify: `ci/run-provider-linting-rpcs.py`
- Modify: `ci/provider_linting_proof.py`
- Modify: `tests/proof/test_provider_linting_proof.py`

- [ ] **Step 1: Write failing tests.** Require `terminal` output to contain a stable row for each `(kind, attribute, rule_id)`, a package hash, and a 7/7 summary; require the verifier to reject an omitted terminal row.
- [ ] **Step 2: Run the focused proof test and verify it fails.**

  Run: `uv run pytest tests/proof/test_provider_linting_proof.py -q`

  Expected: failure because `terminal` is not an accepted format and no readable-row proof parser exists.

- [ ] **Step 3: Implement the smallest format and parser.** Add `terminal` to the explicit CLI choices, render stable fixed-field rows from existing diagnostic records, and make the verifier assert the parsed catalog and package hash.
- [ ] **Step 4: Re-run the focused proof test.**

  Run: `uv run pytest tests/proof/test_provider_linting_proof.py -q`

  Expected: PASS.

### Task 2: Record and verify two purpose-specific casts

**Files:**
- Create: `ci/provider-linting-opentofu-demo.sh`
- Create: `ci/provider-linting-direct-rpc-demo.sh`
- Modify: `ci/record-provider-linting.sh`
- Modify: `ci/provider_linting_proof.py`
- Modify: `docs/guides/provider-linting-proof.md`
- Test: `tests/proof/test_provider_linting_proof.py`
- Test: `tests/proof/test_provider_linting_docs.py`

- [ ] **Step 1: Write failing tests.** Require a two-cast manifest with `opentofu` and `direct_rpc` assets, reject a missing direct cast, and require documentation to distinguish the four-path OpenTofu demonstration from seven-path direct proof.
- [ ] **Step 2: Run the focused tests and verify they fail.**

  Run: `uv run pytest tests/proof/test_provider_linting_proof.py tests/proof/test_provider_linting_docs.py -q`

  Expected: failure because schema v1 has one `cast` entry and the guide still describes one recording.

- [ ] **Step 3: Implement the smallest split.** Move only OpenTofu commands to its demo script; invoke only the direct runner with `--format terminal` in the direct demo; record, retime, redact, verify, and atomically publish both casts and the schema-v2 manifest.
- [ ] **Step 4: Re-run focused tests.**

  Run: `uv run pytest tests/proof/test_provider_linting_proof.py tests/proof/test_provider_linting_docs.py -q`

  Expected: PASS.

### Task 3: Present both recordings correctly on the site

**Files:**
- Modify: `/Users/tim/.config/superpowers/worktrees/site-pyvider-com/provider-linting/content/linting.md`
- Modify: `/Users/tim/.config/superpowers/worktrees/site-pyvider-com/provider-linting/scripts/sync-provider-linting-proof.py`
- Modify: `/Users/tim/.config/superpowers/worktrees/site-pyvider-com/provider-linting/scripts/check-linting-site.py`
- Modify: `/Users/tim/.config/superpowers/worktrees/site-pyvider-com/provider-linting/scripts/smoke-linting-preview.py`
- Test: `/Users/tim/.config/superpowers/worktrees/site-pyvider-com/provider-linting/tests/test_linting_site.py`
- Test: `/Users/tim/.config/superpowers/worktrees/site-pyvider-com/provider-linting/tests/test_linting_preview_smoke.py`

- [ ] **Step 1: Write failing site contracts.** Require two distinct player targets, two downloaded cast assets, a primary OpenTofu title, and a technical section with the exact boundary wording.
- [ ] **Step 2: Run focused tests and verify they fail.**

  Run: `python3 -m unittest tests.test_linting_site tests.test_linting_preview_smoke -v`

  Expected: failure because the page and syncer know only `provider-linting.cast`.

- [ ] **Step 3: Implement the smallest page and sync changes.** Embed the product cast first, render a concise technical-coverage section for the direct cast, retain the manifest link, and update asset/smoke checks for both casts.
- [ ] **Step 4: Re-run focused tests.**

  Run: `python3 -m unittest tests.test_linting_site tests.test_linting_preview_smoke -v`

  Expected: PASS.

### Task 4: Record, sync, stage, and prove the complete change

**Files:**
- Modify generated artifacts in provider and site repositories only through their checked recorder/sync workflows.

- [ ] **Step 1: Run provider proof verification.** Rebuild the coordinated package, record both casts, and run `uv run pytest tests/proof -q` plus the manifest verifier.
- [ ] **Step 2: Sync the exact successful CI artifact to the site.** Verify both assets and the manifest before transactional installation.
- [ ] **Step 3: Run full site verification.** Run all site tests, Ruff, Hugo, rendered-page check, and preview smoke check.
- [ ] **Step 4: Deploy only the feature branch to Cloudflare Pages.** Follow `docs/deployment.md`; record the exact URL and smoke output. Do not promote production.

## Review

The plan covers the readable direct output, two checked provider assets, the site’s two-player presentation, and staging-only verification. It deliberately does not modify OpenTofu or change the upstream protocol boundary.
