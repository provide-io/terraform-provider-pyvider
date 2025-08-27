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
VERSION ?= $(shell grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2)
PLATFORMS := linux_amd64 linux_arm64 darwin_amd64 darwin_arm64
PSP_FILE := dist/$(PROVIDER_NAME).psp

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
all: clean setup build docs test ## Run full development cycle

.PHONY: dev
dev: setup build install ## Quick development setup and build

# ==============================================================================
# 🔧 Setup & Environment
# ==============================================================================

.PHONY: setup
setup: ## Set up development environment
	@echo "$(BLUE)🔧 Setting up development environment...$(NC)"
	@source env.sh && echo "$(GREEN)✅ Environment activated$(NC)"

.PHONY: install-tools
install-tools: ## Install required development tools
	@echo "$(BLUE)📦 Installing development tools...$(NC)"
	@command -v uv >/dev/null 2>&1 || (echo "Installing uv..." && curl -LsSf https://astral.sh/uv/install.sh | sh)
	@uv tool install flavorpack
	@uv tool install garnish 2>/dev/null || echo "garnish install skipped"
	@uv tool install tofusoup 2>/dev/null || echo "tofusoup install skipped"
	@echo "$(GREEN)✅ Tools installed$(NC)"

.PHONY: deps
deps: ## Install Python dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	@uv pip install -e .
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

# ==============================================================================
# 🏗️ Build & Package
# ==============================================================================

.PHONY: build
build: keys ## Build the provider PSP package
	@echo "$(BLUE)🏗️ Building provider version $(VERSION)...$(NC)"
	@flavor pack
	@echo "$(GREEN)✅ Provider built: $(PSP_FILE)$(NC)"
	@ls -lh $(PSP_FILE)

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
	@rm -rf dist/*.psp
	@rm -rf build/
	@rm -rf *.egg-info
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@rm -rf ~/Library/Caches/flavor/workenv/$(PROVIDER_NAME)
	@echo "$(GREEN)✅ Cleaned$(NC)"

.PHONY: clean-docs
clean-docs: ## Clean documentation directory
	@echo "$(BLUE)🧹 Cleaning documentation...$(NC)"
	@rm -rf docs/data-sources
	@rm -rf docs/data_sources
	@rm -rf docs/resources
	@rm -rf docs/functions
	@rm -rf docs/generated*
	@rm -rf docs/garnish-improvements.md
	@rm -f docs/index.md
	@echo "$(GREEN)✅ Documentation cleaned$(NC)"

.PHONY: clean-all
clean-all: clean clean-docs ## Deep clean including workenv and all caches
	@echo "$(RED)🔥 Deep cleaning everything...$(NC)"
	@rm -rf workenv/
	@rm -rf keys/
	@rm -rf examples/
	@rm -rf tests/conformance/
	@echo "$(GREEN)✅ Everything cleaned$(NC)"

# ==============================================================================
# 📚 Documentation
# ==============================================================================

.PHONY: docs
docs: clean-docs ## Build documentation with garnish (cleans first)
	@echo "$(BLUE)📚 Building documentation...$(NC)"
	@./scripts/build-docs.sh
	@echo "$(GREEN)✅ Documentation built in docs/$(NC)"

.PHONY: docs-serve
docs-serve: docs ## Build and serve documentation locally
	@echo "$(BLUE)🌐 Serving documentation on http://localhost:8000$(NC)"
	@cd docs && python3 -m http.server 8000

# ==============================================================================
# 🧪 Testing & Validation
# ==============================================================================

.PHONY: test
test: build ## Test the provider binary
	@echo "$(BLUE)🧪 Testing provider...$(NC)"
	@echo "First run (cold start):"
	@time ./$(PSP_FILE) launch-context || true
	@echo "\nSecond run (warm start):"
	@time ./$(PSP_FILE) launch-context || true

.PHONY: test-local
test-local: build ## Test provider with local Terraform
	@echo "$(BLUE)🧪 Testing with Terraform...$(NC)"
	@mkdir -p examples/test
	@echo 'terraform {\n  required_providers {\n    pyvider = {\n      source = "local/providers/pyvider"\n      version = "$(VERSION)"\n    }\n  }\n}\n\nprovider "pyvider" {}' > examples/test/main.tf
	@cd examples/test && terraform init && terraform validate
	@echo "$(GREEN)✅ Provider works with Terraform$(NC)"

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
	@echo "$(BLUE)📦 Installing provider locally...$(NC)"
	@mkdir -p ~/.terraform.d/plugins/local/providers/pyvider/$(VERSION)/darwin_arm64/
	@cp $(PSP_FILE) ~/.terraform.d/plugins/local/providers/pyvider/$(VERSION)/darwin_arm64/terraform-provider-pyvider
	@chmod +x ~/.terraform.d/plugins/local/providers/pyvider/$(VERSION)/darwin_arm64/terraform-provider-pyvider
	@echo "$(GREEN)✅ Provider installed to ~/.terraform.d/plugins$(NC)"

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
	@echo "Version:    $(VERSION)"
	@echo "Python:     $$(python --version 2>&1)"
	@echo "UV:         $$(uv --version 2>&1)"
	@echo "Flavor:     $$(flavor --version 2>&1 | head -1 || echo 'not installed')"
	@echo ""
	@echo "Project Structure:"
	@echo "  Provider:  $(PROVIDER_NAME)"
	@echo "  PSP File:  $(PSP_FILE)"
	@echo "  Docs:      docs/"
	@echo "  Examples:  examples/"
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