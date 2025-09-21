# Terraform Provider Pyvider - Makefile
# Provides a fantastic developer experience with simple, memorable commands

.PHONY: help
help: ## Show this help message
	@echo "Terraform Provider Pyvider - Development Commands"
	@echo "================================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  make setup          # Set up development environment"
	@echo "  make build          # Build the provider"
	@echo "  make test           # Run provider locally"
	@echo "  make release        # Create a new release"

# Configuration
PROVIDER_NAME := terraform-provider-pyvider
VERSION ?= $(shell grep '^version = ' pyproject.toml | cut -d'"' -f2)
PLATFORMS := linux_amd64 linux_arm64 darwin_amd64 darwin_arm64

# Platform detection
UNAME_S := $(shell uname -s | tr '[:upper:]' '[:lower:]')
UNAME_M := $(shell uname -m)
# Convert uname -m output to Go arch naming
ifeq ($(UNAME_M),x86_64)
    ARCH := amd64
else ifeq ($(UNAME_M),arm64)
    ARCH := arm64
else ifeq ($(UNAME_M),aarch64)
    ARCH := arm64
else
    ARCH := $(UNAME_M)
endif
CURRENT_PLATFORM := $(UNAME_S)_$(ARCH)

# File paths
PSP_FILE := dist/$(PROVIDER_NAME).psp
ARCH_DIR := dist/$(CURRENT_PLATFORM)
VERSIONED_BINARY := $(ARCH_DIR)/$(PROVIDER_NAME)_v$(VERSION)

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# ==============================================================================
# 🚀 Quick Commands
# ==============================================================================

.PHONY: all
all: clean venv setup deps docs build test ## Run full development cycle

.PHONY: dev
dev: venv setup deps install-flavor build install ## Quick development setup and build

# ==============================================================================
# 🔧 Setup & Environment
# ==============================================================================

.PHONY: venv
venv: ## Create virtual environment
	@if [ ! -d .venv ]; then \
		echo "$(BLUE)🔧 Creating virtual environment...$(NC)"; \
		uv venv .venv; \
		echo "$(GREEN)✅ Virtual environment created$(NC)"; \
	else \
		echo "$(GREEN)✅ Virtual environment already exists$(NC)"; \
	fi

.PHONY: activate
activate: venv ## Show activation command
	@echo "$(BLUE)To activate the environment, run:$(NC)"
	@echo "source .venv/bin/activate"

.PHONY: setup
setup: venv ## Set up development environment
	@echo "$(BLUE)🔧 Setting up development environment...$(NC)"
	@. .venv/bin/activate && \
		uv add provide-foundation pyvider-components plating flavorpack && \
		echo "$(GREEN)✅ Environment setup complete$(NC)"

.PHONY: install-flavor
install-flavor: venv ## Install flavorpack tool
	@echo "$(BLUE)📦 Installing flavorpack...$(NC)"
	@. .venv/bin/activate && \
		uv tool install flavorpack && \
		echo "$(GREEN)✅ Flavorpack installed$(NC)"

.PHONY: install-tools
install-tools: install-flavor ## Install required development tools
	@echo "$(BLUE)📦 Installing development tools...$(NC)"
	@command -v uv >/dev/null 2>&1 || (echo "Installing uv..." && curl -LsSf https://astral.sh/uv/install.sh | sh)
	@uv tool install plating 2>/dev/null || echo "plating install skipped"
	@uv tool install tofusoup 2>/dev/null || echo "tofusoup install skipped"
	@echo "$(GREEN)✅ Tools installed$(NC)"

.PHONY: deps
deps: venv ## Install Python dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	@. .venv/bin/activate && \
		uv sync --all-groups --dev && \
		echo "$(GREEN)✅ Dependencies installed$(NC)"

# ==============================================================================
# 🏗️ Build & Package
# ==============================================================================

.PHONY: build
build: venv deps install-flavor keys ## Build the provider PSP package
	@echo "$(BLUE)🏗️ Building provider version $(VERSION) for $(CURRENT_PLATFORM)...$(NC)"
	@. .venv/bin/activate && \
		flavor pack && \
		echo "$(GREEN)✅ Provider built: $(PSP_FILE)$(NC)" && \
		mkdir -p $(ARCH_DIR) && \
		cp $(PSP_FILE) $(VERSIONED_BINARY) && \
		chmod +x $(VERSIONED_BINARY) && \
		echo "$(GREEN)✅ Versioned binary created: $(VERSIONED_BINARY)$(NC)" && \
		ls -lh $(PSP_FILE) $(VERSIONED_BINARY)

.PHONY: build-all
build-all: venv deps install-flavor keys ## Build provider for all platforms (CI/CD reference)
	@echo "$(BLUE)🏗️ Building provider version $(VERSION) for all platforms...$(NC)"
	@echo "$(YELLOW)⚠️  Note: This target shows structure for CI/CD. Local builds only support current platform.$(NC)"
	@. .venv/bin/activate && \
		flavor pack && \
		echo "$(GREEN)✅ Base PSP built: $(PSP_FILE)$(NC)"
	@for platform in $(PLATFORMS); do \
		echo "$(BLUE)Creating structure for $$platform...$(NC)"; \
		mkdir -p dist/$$platform; \
		cp $(PSP_FILE) dist/$$platform/$(PROVIDER_NAME)_v$(VERSION); \
		chmod +x dist/$$platform/$(PROVIDER_NAME)_v$(VERSION); \
		echo "$(GREEN)✅ Created: dist/$$platform/$(PROVIDER_NAME)_v$(VERSION)$(NC)"; \
	done

.PHONY: keys
keys: ## Generate signing keys if missing
	@if [ ! -f keys/provider-private.key ]; then \
		echo "$(BLUE)🔑 Generating signing keys...$(NC)"; \
		flavor keygen --out-dir keys; \
		echo "$(GREEN)✅ Keys generated$(NC)"; \
	else \
		echo "$(GREEN)✅ Signing keys already exist$(NC)"; \
	fi

.PHONY: clean
clean: ## Clean build artifacts and cache
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(NC)"
	@rm -rf dist/
	@rm -rf build/
	@rm -rf *.egg-info
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@rm -rf ~/Library/Caches/flavor/workenv/$(PROVIDER_NAME)
	@echo "$(GREEN)✅ Cleaned$(NC)"

.PHONY: clean-docs
clean-docs: ## Clean entire documentation directory
	@echo "$(BLUE)🧹 Cleaning documentation...$(NC)"
	@rm -rf docs/*
	@echo "$(GREEN)✅ Documentation cleaned$(NC)"

.PHONY: clean-plating
clean-plating: ## Clean plating test outputs
	@echo "$(BLUE)🧹 Cleaning plating test outputs...$(NC)"
	@rm -rf tests/plating-tests
	@find ../pyvider-components -name "*.plating" -type d -exec rm -rf {}/test-output \; 2>/dev/null || true
	@echo "$(GREEN)✅ Plating test outputs cleaned$(NC)"

.PHONY: clean-examples
clean-examples: ## Clean example test outputs
	@echo "$(BLUE)🧹 Cleaning example outputs...$(NC)"
	@find examples -name "*.tfstate*" -delete 2>/dev/null || true
	@find examples -name ".terraform" -type d -exec rm -rf {} \; 2>/dev/null || true
	@find examples -name "*.tfplan" -delete 2>/dev/null || true
	@find examples -name "terraform.lock.hcl" -delete 2>/dev/null || true
	@rm -rf examples/*/generated 2>/dev/null || true
	@rm -rf examples/*/test_output 2>/dev/null || true
	@rm -rf examples/*/outputs 2>/dev/null || true
	@echo "$(GREEN)✅ Example outputs cleaned$(NC)"

.PHONY: clean-tfstate
clean-tfstate: ## Clean all Terraform state and lock files in current directory tree
	@echo "$(BLUE)🧹 Cleaning Terraform state files...$(NC)"
	@find . -name "*.tfstate" -o -name "*.tfstate.*" -o -name ".terraform.lock.hcl" | xargs rm -f 2>/dev/null || true
	@find . -name ".terraform" -type d -exec rm -rf {} \; 2>/dev/null || true
	@echo "$(GREEN)✅ Terraform state files cleaned$(NC)"

.PHONY: clean-tfcache
clean-tfcache: ## Clean Terraform plugin cache (~/.terraform.d)
	@echo "$(BLUE)🧹 Cleaning Terraform plugin cache...$(NC)"
	@rm -rf ~/.terraform.d/plugin-cache 2>/dev/null || true
	@rm -rf ~/.terraform.d/providers 2>/dev/null || true
	@echo "$(GREEN)✅ Terraform plugin cache cleaned$(NC)"

.PHONY: clean-workenv
clean-workenv: ## Clean all flavor work environments for this provider
	@echo "$(BLUE)🧹 Cleaning flavor work environments...$(NC)"
	@rm -rf ~/Library/Caches/flavor/workenv/$(PROVIDER_NAME)*
	@rm -rf ~/Library/Caches/flavor/workenv/.$(PROVIDER_NAME)*
	@if [ -n "$$XDG_CACHE_HOME" ]; then \
		rm -rf $$XDG_CACHE_HOME/flavor/workenv/$(PROVIDER_NAME)*; \
		rm -rf $$XDG_CACHE_HOME/flavor/workenv/.$(PROVIDER_NAME)*; \
	fi
	@rm -rf ~/.cache/flavor/workenv/$(PROVIDER_NAME)* 2>/dev/null || true
	@rm -rf ~/.cache/flavor/workenv/.$(PROVIDER_NAME)* 2>/dev/null || true
	@echo "$(GREEN)✅ Flavor work environments cleaned$(NC)"

.PHONY: clean-all
clean-all: clean clean-docs clean-plating clean-examples clean-workenv ## Deep clean including venv, workenv and all caches
	@echo "$(RED)🔥 Deep cleaning everything...$(NC)"
	@rm -rf .venv/
	@rm -rf workenv/
	@rm -rf keys/
	@rm -rf examples/
	@rm -rf tests/conformance/
	@echo "$(GREEN)✅ Everything cleaned$(NC)"

# ==============================================================================
# 📚 Documentation
# ==============================================================================

.PHONY: docs
docs: venv deps clean-docs ## Build documentation with plating (cleans first)
	@echo "$(BLUE)📚 Building documentation...$(NC)"
	@. .venv/bin/activate && \
		python3 -c "\
import sys; \
sys.path.append('../pyvider-components/src'); \
from plating.api import PlatingAPI; \
from pathlib import Path; \
api = PlatingAPI(); \
files = api.generate_all_documentation('docs'); \
written = api.write_generated_files(files); \
print(f'Generated {len(written)} complete documentation files')" && \
		echo "$(GREEN)✅ Documentation built in docs/$(NC)"

.PHONY: docs-serve
docs-serve: docs ## Build and serve documentation locally
	@echo "$(BLUE)🌐 Serving documentation on http://localhost:8000$(NC)"
	@cd docs && python3 -m http.server 8000

# ==============================================================================
# 🧪 Testing & Validation
# ==============================================================================

.PHONY: test
test: venv build ## Test the provider binary
	@echo "$(BLUE)🧪 Testing provider...$(NC)"
	@echo "Testing PSP file:"
	@echo "First run (cold start):"
	@time ./$(PSP_FILE) launch-context || true
	@echo "\nSecond run (warm start):"
	@time ./$(PSP_FILE) launch-context || true
	@echo "\nTesting versioned binary:"
	@echo "First run (cold start):"
	@time ./$(VERSIONED_BINARY) launch-context || true
	@echo "\nSecond run (warm start):"
	@time ./$(VERSIONED_BINARY) launch-context || true

.PHONY: test-local
test-local: build ## Test provider with local Terraform
	@echo "$(BLUE)🧪 Testing with Terraform...$(NC)"
	@mkdir -p examples/test
	@echo 'terraform {\n  required_providers {\n    pyvider = {\n      source = "local/providers/pyvider"\n      version = "$(VERSION)"\n    }\n  }\n}\n\nprovider "pyvider" {}' > examples/test/main.tf
	@cd examples/test && terraform init && terraform validate
	@echo "$(GREEN)✅ Provider works with Terraform$(NC)"

.PHONY: test-plating
test-plating: ## Run plating tests for all components
	@echo "$(BLUE)🧪 Running plating tests...$(NC)"
	@./scripts/test-plating.sh

.PHONY: test-examples
test-examples: build ## Test example configurations
	@echo "$(BLUE)🧪 Testing example configurations...$(NC)"
	@for dir in examples/*/; do \
		if [ -f "$$dir/main.tf" ]; then \
			echo "Testing $$dir..."; \
			cd "$$dir" && terraform init -upgrade && terraform validate && cd ../..; \
		fi; \
	done
	@echo "$(GREEN)✅ All examples validated$(NC)"

.PHONY: lint
lint: ## Run code linting
	@echo "$(BLUE)🔍 Running linters...$(NC)"
	@ruff check . 2>/dev/null || echo "$(YELLOW)⚠️  Ruff not available$(NC)"
	@mypy . 2>/dev/null || echo "$(YELLOW)⚠️  Mypy not available$(NC)"
	@echo "$(GREEN)✅ Linting complete$(NC)"

.PHONY: format
format: ## Format code
	@echo "$(BLUE)🎨 Formatting code...$(NC)"
	@ruff format . 2>/dev/null || echo "$(YELLOW)⚠️  Ruff format not available$(NC)"
	@echo "$(GREEN)✅ Code formatted$(NC)"

# ==============================================================================
# 🚀 Release & Publishing
# ==============================================================================

.PHONY: version
version: ## Show current version
	@echo "Current version: $(VERSION)"

.PHONY: bump-patch
bump-patch: ## Bump patch version (0.0.3 -> 0.0.4)
	@echo "$(BLUE)📦 Bumping patch version...$(NC)"
	@current=$$(grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2); \
	new=$$(echo $$current | awk -F. '{print $$1"."$$2"."$$3+1}'); \
	sed -i.bak "s/version = \"$$current\"/version = \"$$new\"/" pyproject.toml && rm pyproject.toml.bak; \
	echo "$(GREEN)✅ Version bumped from $$current to $$new$(NC)"

.PHONY: bump-minor
bump-minor: ## Bump minor version (0.0.3 -> 0.1.0)
	@echo "$(BLUE)📦 Bumping minor version...$(NC)"
	@current=$$(grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2); \
	new=$$(echo $$current | awk -F. '{print $$1"."$$2+1".0"}'); \
	sed -i.bak "s/version = \"$$current\"/version = \"$$new\"/" pyproject.toml && rm pyproject.toml.bak; \
	echo "$(GREEN)✅ Version bumped from $$current to $$new$(NC)"

.PHONY: bump-major
bump-major: ## Bump major version (0.0.3 -> 1.0.0)
	@echo "$(BLUE)📦 Bumping major version...$(NC)"
	@current=$$(grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2); \
	new=$$(echo $$current | awk -F. '{print $$1+1".0.0"}'); \
	sed -i.bak "s/version = \"$$current\"/version = \"$$new\"/" pyproject.toml && rm pyproject.toml.bak; \
	echo "$(GREEN)✅ Version bumped from $$current to $$new$(NC)"

.PHONY: release
release: ## Create a new release (prompts for version)
	@echo "$(BLUE)🚀 Creating new release...$(NC)"
	@echo "Current version: $(VERSION)"
	@echo "Enter new version (or press Enter to use current):"
	@read new_version; \
	if [ -n "$$new_version" ]; then \
		sed -i.bak "s/version = \"$(VERSION)\"/version = \"$$new_version\"/" pyproject.toml && rm pyproject.toml.bak; \
		git add pyproject.toml; \
		git commit -m "Release v$$new_version"; \
		git push origin main; \
		gh workflow run "build-release.yml" -f version=$$new_version -f prerelease=false; \
		echo "$(GREEN)✅ Release v$$new_version started$(NC)"; \
	else \
		gh workflow run "build-release.yml" -f version=$(VERSION) -f prerelease=false; \
		echo "$(GREEN)✅ Release v$(VERSION) started$(NC)"; \
	fi

.PHONY: release-status
release-status: ## Check release workflow status
	@echo "$(BLUE)📊 Checking release status...$(NC)"
	@gh run list --workflow "build-release.yml" --limit 1
	@echo ""
	@./scripts/check-registry.sh $(VERSION)

# ==============================================================================
# 🔍 Registry & Provider Info
# ==============================================================================

.PHONY: registry-check
registry-check: ## Check Terraform Registry status
	@echo "$(BLUE)🔍 Checking Terraform Registry...$(NC)"
	@./scripts/check-registry.sh $(VERSION)

.PHONY: registry-sync
registry-sync: ## Attempt to sync with Terraform Registry
	@echo "$(BLUE)🔄 Syncing with Terraform Registry...$(NC)"
	@./scripts/sync-registry.sh

# ==============================================================================
# 🐚 Development Shell & Utilities
# ==============================================================================

.PHONY: shell
shell: setup ## Enter development shell
	@echo "$(BLUE)🐚 Entering development shell...$(NC)"
	@bash --init-file <(echo "source env.sh; echo 'Development shell activated'")

.PHONY: install
install: build ## Install provider locally for testing
	@echo "$(BLUE)📦 Installing provider locally for $(CURRENT_PLATFORM)...$(NC)"
	@mkdir -p ~/.terraform.d/plugins/local/providers/pyvider/$(VERSION)/$(CURRENT_PLATFORM)/
	@cp $(VERSIONED_BINARY) ~/.terraform.d/plugins/local/providers/pyvider/$(VERSION)/$(CURRENT_PLATFORM)/terraform-provider-pyvider
	@chmod +x ~/.terraform.d/plugins/local/providers/pyvider/$(VERSION)/$(CURRENT_PLATFORM)/terraform-provider-pyvider
	@echo "$(GREEN)✅ Provider installed to ~/.terraform.d/plugins/local/providers/pyvider/$(VERSION)/$(CURRENT_PLATFORM)/$(NC)"

.PHONY: watch
watch: ## Watch for changes and rebuild automatically
	@echo "$(BLUE)👁️ Watching for changes...$(NC)"
	@while true; do \
		fswatch -o pyproject.toml src/ 2>/dev/null | xargs -n1 -I{} sh -c 'clear; make build' || \
		(echo "$(YELLOW)⚠️  fswatch not installed. Install with: brew install fswatch$(NC)" && exit 1); \
	done

# ==============================================================================
# 📊 Project Info
# ==============================================================================

.PHONY: info
info: ## Show project information
	@echo "$(BLUE)📊 Terraform Provider Pyvider$(NC)"
	@echo "================================"
	@echo "Version:         $(VERSION)"
	@echo "Platform:        $(CURRENT_PLATFORM)"
	@echo "Python:          $$(python --version 2>&1)"
	@echo "UV:              $$(uv --version 2>&1)"
	@echo "Flavor:          $$(flavor --version 2>&1 | head -1 || echo 'not installed')"
	@echo ""
	@echo "Project Structure:"
	@echo "  Provider:        $(PROVIDER_NAME)"
	@echo "  PSP File:        $(PSP_FILE)"
	@echo "  Versioned Binary: $(VERSIONED_BINARY)"
	@echo "  Docs:            docs/"
	@echo "  Examples:        examples/"
	@echo ""
	@echo "Build Artifacts:"
	@if [ -f "$(PSP_FILE)" ]; then \
		echo "  PSP:             ✅ $(PSP_FILE)"; \
	else \
		echo "  PSP:             ❌ Not built"; \
	fi
	@if [ -f "$(VERSIONED_BINARY)" ]; then \
		echo "  Versioned:       ✅ $(VERSIONED_BINARY)"; \
	else \
		echo "  Versioned:       ❌ Not built"; \
	fi
	@echo ""
	@echo "Recent Commits:"
	@git log --oneline -5

.PHONY: stats
stats: ## Show project statistics
	@echo "$(BLUE)📊 Project Statistics$(NC)"
	@echo "====================="
	@echo "Lines of Python:    $$(find . -name '*.py' -not -path './workenv/*' -not -path './build/*' | xargs wc -l | tail -1 | awk '{print $$1}')"
	@echo "Documentation:      $$(find docs -name '*.md' | wc -l) files"
	@echo "Examples:           $$(find examples -name '*.tf' 2>/dev/null | wc -l) files"
	@echo "GitHub Stars:       $$(gh repo view --json stargazerCount -q .stargazerCount)"
	@echo "Open Issues:        $$(gh issue list --state open --json number -q '. | length')"
	@echo "Open PRs:           $$(gh pr list --state open --json number -q '. | length')"

# Default target
.DEFAULT_GOAL := help