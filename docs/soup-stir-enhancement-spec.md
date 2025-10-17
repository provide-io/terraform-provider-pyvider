# Tofusoup `soup stir` Enhancement Specification

## Executive Summary

This document outlines comprehensive enhancements to the `soup stir` command to dramatically improve Terraform/OpenTofu example testing capabilities. These improvements will make `soup stir` a superior replacement for traditional shell-based test scripts while providing rich feedback, parallel execution, and intelligent test management.

## Current State Analysis

### Existing Capabilities
- ✅ Parallel test execution with real-time status display
- ✅ Rich failure reporting with structured log extraction
- ✅ Performance metrics tracking (elapsed time per test)
- ✅ Resource/data source/function/output counting
- ✅ Automatic test directory detection
- ✅ JSON-structured logging with error extraction

### Current Limitations
- ❌ Limited to single-level directory structures
- ❌ No support for nested example hierarchies
- ❌ Cannot filter or categorize tests
- ❌ No batch processing for many small tests
- ❌ Missing provider build integration
- ❌ Limited reporting formats
- ❌ No test result caching
- ❌ No CI/CD-specific output formats

## Enhancement Specifications

### 1. Hierarchical Test Discovery

#### Requirements
- Support nested directory structures of arbitrary depth
- Handle multiple test patterns simultaneously
- Auto-detect common Terraform file patterns

#### Implementation Checklist
- [ ] Add `--pattern` flag for glob patterns
  ```bash
  soup stir --pattern "docs/examples/**/main.tf"
  soup stir --pattern "**/*.tf" --pattern "!**/modules/**"
  ```
- [ ] Add `--recursive` flag for deep scanning
  ```bash
  soup stir --recursive docs/examples
  ```
- [ ] Support `.soupignore` file for exclusions
- [ ] Implement smart detection of test boundaries (presence of `main.tf`, `*.tf` files, or `.soup/` marker)

#### Example Usage
```bash
# Find all tests in nested structure
soup stir --recursive terraform-provider-pyvider/docs/examples

# Use multiple patterns
soup stir --pattern "examples/**/test_*.tf" --pattern "docs/**/example.tf"
```

### 2. Test Categorization & Filtering

#### Requirements
- Category-based test selection
- Tag-based filtering
- Name pattern matching
- Test type filtering (data source, resource, function)

#### Implementation Checklist
- [ ] Add `--filter` flag for path-based filtering
  ```bash
  soup stir --filter "function/*"
  soup stir --filter "data_source/lens_jq/*"
  ```
- [ ] Add `--tags` flag for metadata filtering
  ```bash
  soup stir --tags "basic,example"
  soup stir --tags "!slow"  # Exclude slow tests
  ```
- [ ] Add `--type` flag for component type filtering
  ```bash
  soup stir --type "data_source"
  soup stir --type "function,resource"
  ```
- [ ] Support regex patterns in filters
  ```bash
  soup stir --filter-regex ".*_test$"
  ```
- [ ] Implement test metadata extraction from:
  - Directory names
  - File comments
  - `soup.toml` configuration

### 3. Batch Testing Mode

#### Requirements
- Group multiple small tests for efficient execution
- Intelligent batching strategies
- Configurable batch sizes
- Category-based batching

#### Implementation Checklist
- [ ] Add `--batch-size` flag for fixed-size batches
  ```bash
  soup stir --batch-size 10  # Process 10 tests per worker
  ```
- [ ] Add `--batch-by-category` flag for logical grouping
  ```bash
  soup stir --batch-by-category  # Group by parent directory
  ```
- [ ] Add `--batch-strategy` flag for different approaches
  ```bash
  soup stir --batch-strategy size     # By test file size
  soup stir --batch-strategy time     # By estimated runtime
  soup stir --batch-strategy affinity # By resource dependencies
  ```
- [ ] Implement batch result aggregation
- [ ] Add batch-level timeout controls
- [ ] Support partial batch failure handling

### 4. Progressive Test Execution

#### Requirements
- Multi-phase testing with early termination
- Quick validation modes
- Configurable execution stages

#### Implementation Checklist
- [ ] Add `--quick` flag for fast validation
  ```bash
  soup stir --quick  # Only init + validate
  ```
- [ ] Add `--progressive` flag for staged execution
  ```bash
  soup stir --progressive  # init → validate → plan → apply
  ```
- [ ] Add `--stages` flag for custom stage selection
  ```bash
  soup stir --stages init,validate,plan  # Skip apply
  ```
- [ ] Add `--fail-fast` flag for immediate termination
  ```bash
  soup stir --fail-fast  # Stop all tests on first failure
  ```
- [ ] Implement stage-specific timeouts
- [ ] Add stage result persistence for resume capability

### 5. Comparison & Regression Testing

#### Requirements
- Compare results between test runs
- Detect performance regressions
- Track test stability over time

#### Implementation Checklist
- [ ] Add `--baseline` flag for comparison
  ```bash
  soup stir --baseline previous-run.json
  ```
- [ ] Add `--compare-with` flag for branch comparison
  ```bash
  soup stir --compare-with main-branch
  ```
- [ ] Implement result diffing algorithm
- [ ] Add performance regression detection
  - [ ] Execution time comparison
  - [ ] Resource count changes
  - [ ] Memory usage tracking
- [ ] Generate comparison reports
- [ ] Add `--threshold` flag for regression limits
  ```bash
  soup stir --threshold "time:+10%"  # Fail if 10% slower
  ```

### 6. Provider Management Integration

#### Requirements
- Automatic provider building before tests
- Provider version management
- Multiple provider support

#### Implementation Checklist
- [ ] Add `--rebuild-provider` flag
  ```bash
  soup stir --rebuild-provider
  ```
- [ ] Add `--provider-path` flag for custom providers
  ```bash
  soup stir --provider-path dist/terraform-provider-pyvider.psp
  ```
- [ ] Add `--provider-version` flag
  ```bash
  soup stir --provider-version "0.1.0"
  ```
- [ ] Implement provider build detection
  - [ ] Check modification times
  - [ ] Verify checksums
  - [ ] Auto-rebuild if source newer than binary
- [ ] Support multiple provider testing
  ```bash
  soup stir --providers "pyvider:0.1.0,aws:5.0.0"
  ```
- [ ] Add provider installation verification

### 7. Enhanced Reporting

#### Requirements
- Multiple output formats
- Rich HTML reports
- CI/CD integration formats
- Time series tracking

#### Implementation Checklist
- [ ] Add `--output-format` flag
  ```bash
  soup stir --output-format json
  soup stir --output-format junit
  soup stir --output-format markdown
  soup stir --output-format html
  ```
- [ ] Implement HTML report generation
  - [ ] Interactive test result browser
  - [ ] Log viewer with syntax highlighting
  - [ ] Performance charts
  - [ ] Failure categorization
- [ ] Add `--report-dir` flag for output location
  ```bash
  soup stir --report-dir reports/$(date +%Y%m%d)
  ```
- [ ] Implement JUnit XML for CI systems
- [ ] Add GitHub Actions annotations format
  ```bash
  soup stir --output-format github-annotations
  ```
- [ ] Generate markdown summary tables
- [ ] Add `--verbose` levels
  ```bash
  soup stir -v     # Basic verbosity
  soup stir -vv    # Detailed logs
  soup stir -vvv   # Debug mode
  ```

### 8. Test Configuration Generation

#### Requirements
- Auto-generate soup configurations from examples
- Detect test requirements
- Create optimal test settings

#### Implementation Checklist
- [ ] Add `soup init` command
  ```bash
  soup init --from-examples docs/examples
  ```
- [ ] Add `soup generate-config` command
  ```bash
  soup generate-config --pattern "**/*.tf"
  ```
- [ ] Implement configuration inference
  - [ ] Detect required providers
  - [ ] Identify test dependencies
  - [ ] Suggest parallelization settings
  - [ ] Generate appropriate timeouts
- [ ] Support configuration templates
- [ ] Add interactive configuration wizard
  ```bash
  soup init --interactive
  ```

### 9. Smart Caching

#### Requirements
- Cache test results based on content hashes
- Incremental testing support
- Distributed cache capability

#### Implementation Checklist
- [ ] Add `--cache` flag for enabling cache
  ```bash
  soup stir --cache
  ```
- [ ] Add `--cache-dir` flag for cache location
  ```bash
  soup stir --cache-dir ~/.soup/cache
  ```
- [ ] Implement content hashing
  - [ ] Hash .tf files
  - [ ] Hash provider versions
  - [ ] Hash module dependencies
- [ ] Add cache invalidation rules
  ```bash
  soup stir --cache-invalidate "provider:*"
  soup stir --cache-max-age 24h
  ```
- [ ] Support distributed caching
  ```bash
  soup stir --cache-backend s3://bucket/soup-cache
  ```
- [ ] Add cache statistics reporting
  ```bash
  soup cache stats
  soup cache clean
  ```

### 10. CI/CD Integration

#### Requirements
- CI-friendly output formats
- Proper exit codes
- Machine-readable results
- Integration with popular CI systems

#### Implementation Checklist
- [ ] Add `--ci` flag for CI mode
  ```bash
  soup stir --ci
  ```
- [ ] Implement CI-specific features
  - [ ] Disable color output in CI mode
  - [ ] Generate step summaries
  - [ ] Output timing information
  - [ ] Create artifact directories
- [ ] Add GitHub Actions support
  ```bash
  soup stir --ci github-actions
  ```
  - [ ] Generate workflow summaries
  - [ ] Create annotations
  - [ ] Set output variables
- [ ] Add GitLab CI support
  ```bash
  soup stir --ci gitlab
  ```
- [ ] Add Jenkins support
  ```bash
  soup stir --ci jenkins
  ```
- [ ] Implement proper exit codes
  - 0: All tests passed
  - 1: Test failures
  - 2: Configuration error
  - 3: Provider build failure
  - 4: Timeout

## Implementation Priority

### Phase 1: Core Enhancements (Immediate)
1. ✅ Hierarchical test discovery
2. ✅ Test categorization & filtering
3. ✅ Batch testing mode
4. ✅ Provider management integration

### Phase 2: Advanced Features (Short-term)
5. Progressive test execution
6. Enhanced reporting
7. CI/CD integration

### Phase 3: Optimization (Medium-term)
8. Smart caching
9. Test configuration generation
10. Comparison & regression testing

## Success Metrics

### Performance Targets
- 50% reduction in test execution time through parallelization
- 90% reduction in redundant test runs through caching
- Sub-second test discovery for 1000+ test files

### Usability Goals
- Single command to test all examples
- Zero configuration for common scenarios
- Rich feedback without information overload

### Adoption Metrics
- Replace 100% of shell-based test scripts
- Integrate with all major CI/CD pipelines
- Support all Terraform provider testing patterns

## Migration Path

### From `validate_all_examples.sh`
```bash
# Old approach
./scripts/validate_all_examples.sh

# New approach
soup stir --recursive docs/examples --progressive --report-dir reports
```

### Configuration Migration
```toml
# soup.toml
[stir]
patterns = ["docs/examples/**/main.tf"]
parallel = 24
batch_size = 10
cache = true
progressive = true

[stir.provider]
auto_rebuild = true
path = "dist/terraform-provider-pyvider.psp"
```

## Testing the Enhancements

### Test Coverage Requirements
- Unit tests for each new flag/option
- Integration tests for complex workflows
- Performance benchmarks for optimization features
- End-to-end tests with real provider examples

### Validation Checklist
- [ ] Test with 100+ example files
- [ ] Verify parallel execution efficiency
- [ ] Validate all output formats
- [ ] Test cache hit rates
- [ ] Benchmark against shell scripts
- [ ] Verify CI/CD integrations

## Documentation Requirements

### User Documentation
- [ ] Update README with new features
- [ ] Create migration guide from shell scripts
- [ ] Add example configurations
- [ ] Document best practices
- [ ] Create troubleshooting guide

### Developer Documentation
- [ ] API documentation for extensions
- [ ] Plugin architecture for custom reporters
- [ ] Cache backend interface specification
- [ ] Test discovery protocol documentation

## Conclusion

These enhancements will transform `soup stir` into a comprehensive Terraform testing solution that surpasses traditional approaches in speed, usability, and insight. The phased implementation ensures immediate value delivery while building toward a complete testing ecosystem.