# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "docs" / "guides" / "provider-linting-proof.md"


def guide_text() -> str:
    return GUIDE.read_text(encoding="utf-8") if GUIDE.exists() else ""


@pytest.mark.parametrize(
    "required_text",
    [
        "tests/e2e/provider-linting/main.tf",
        "tests/proof/fixtures/provider-linting/main.tf",
        "provider-linting.cast",
        "provider-linting-proof.json",
        "v1.13.0-beta1",
        "OpenTofu core reaches 4/7",
        "TofuSoup directly proves 7/7",
        "make build-linting-stack",
        "make test-linting-opentofu-binary",
        "make test-conformance-binary",
        "PYVIDER_LINT=provide-io/pyvider:security tofu validate",
        'export PYVIDER_SOURCE="$(cd ../pyvider && pwd -P)"',
        'export COMPONENTS_SOURCE="$(cd ../pyvider-components && pwd -P)"',
        "ci/record-provider-linting.sh",
        "ci/verify-provider-linting-proof.py",
        "uv run pytest tests/proof -q",
        "gh run download",
        "https://github.com/opentofu/opentofu/blob/main/rfc/20260406-linting.md",
        "https://github.com/opentofu/opentofu/issues/4310",
        "https://github.com/opentofu/opentofu/pull/4337",
        "https://github.com/opentofu/opentofu/releases/tag/v1.13.0-beta1",
        "Pyvider's author-facing lint API is supported",
        "OpenTofu describes its built-in linting feature as experimental",
        "ordinary warning diagnostics are a temporary compatibility bridge",
        "publishes both checked artifacts only after verification and rolls back ordinary publication failures",
    ],
)
def test_provider_linting_guide_covers_reproduction_contract(required_text: str) -> None:
    assert required_text in guide_text(), f"guide is missing {required_text!r}"


def test_provider_linting_guide_does_not_advertise_an_unqualified_group() -> None:
    assert "PYVIDER_LINT=security tofu validate" not in guide_text()


def test_provider_linting_guide_is_in_documentation_navigation() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert "Provider linting proof: guides/provider-linting-proof.md" in mkdocs


def test_documentation_navigation_names_the_existing_list_resource_page() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert "file_content: list-resources/file_content.md" in mkdocs


def test_readme_links_to_provider_linting_proof_guide() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/guides/provider-linting-proof.md" in readme
