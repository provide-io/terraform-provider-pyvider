# Plating Example Migration Status

## Objective
Migrate all working examples from static `examples/` directory into `.plating` structure and fix all generated examples to validate correctly.

## Completed Work

### 1. ✅ Removed "Complete" Auto-Merge Examples
**File**: `plating/src/plating/example_compiler.py`
- Reduced from 500 → 220 lines
- Removed `_generate_combined_example()` - per-component merges
- Removed `_generate_complete_example()` - cross-component showcase
- Removed `complete_example_path` from `CompilationResult`

**Results**:
- Examples generated: 159 → 126 (33 fewer merged files)
- Largest file: 1746 lines → 551 lines ✅
- Zero `complete/` directories ✅

### 2. ✅ Fixed `round()` Function Calls in Numeric Examples
**File**: `pyvider-components/src/pyvider/components/functions/numeric_functions.plating/examples/example.tf`

Fixed 13 instances of `provider::pyvider::round(value)` → `provider::pyvider::round(value, precision)`:
- Line 32-35: `average_monthly` - added `, 2`
- Line 54: `monthly_cost` - added `, 2`
- Line 63-66: `average_requests` - added `, 0`
- Line 95: `final_amount` - added `, 2`
- Line 110-111: String interpolations - added `, 2`
- Line 116: String interpolation - added `, 0`
- Line 133: String interpolation - added `, 2`
- Line 141: String interpolation - added `, 0`
- Line 160-161: Output values - added `, 2`
- Line 166: Output value - added `, 0`
- Line 181: Output value - added `, 2`
- Line 189: Output value - added `, 0`

## Current Status

### Validation Results (Last Run)
- **Passed**: 10/126 examples (7.9%)
- **Failed**: 116/126 examples

### Examples That Pass
All "basic" variants:
- `function/add/basic`
- `function/divide/basic`
- `function/max/basic`
- `function/min/basic`
- `function/multiply/basic`
- `function/round/basic`
- `function/subtract/basic`
- `function/sum/basic`
- `resource/file_content/basic`
- `resource/file_content/multiline`

### Known Issues

**After fixing numeric examples, need to re-test:**
- `function/add/example` - should now pass
- `function/divide/example` - should now pass
- `function/multiply/example` - should now pass
- `function/subtract/example` - should now pass
- `function/sum/example` - should now pass
- `function/round/example` - should now pass
- All `resource_calculations` variants - should now pass

**Still need fixing:**
1. **String manipulation functions** - Many failures in:
   - `function/format*` examples
   - `function/join*` examples
   - `function/lower*` examples
   - `function/upper*` examples
   - `function/split*` examples
   - `function/replace*` examples
   - `function/truncate*` examples
   - `function/to_camel_case*` examples
   - `function/to_kebab_case*` examples
   - `function/to_snake_case*` examples

2. **Collection functions** - Failures in:
   - `function/length*` examples
   - `function/lookup*` examples
   - `function/contains*` examples

3. **Type conversion** - Failures in:
   - `function/tostring*` examples

4. **Data source examples** - Failures in:
   - `data_source/*` examples

5. **Resource examples** - Some failures in:
   - `resource/local_directory/*` (except basic)
   - `resource/file_content/*` (except basic/multiline)
   - `resource/private_state_verifier/*`
   - `resource/timed_token/*`

## Next Steps

### 1. Re-validate After Numeric Fixes
```bash
cd /Users/tim/code/gh/provide-io/terraform-provider-pyvider
rm -rf docs/examples
make generate-docs
./scripts/validate_all_examples.sh 2>&1 | tee validation_results.log
```

### 2. Identify Common Failure Patterns
Run validation and analyze failures:
```bash
grep "✗" validation_results.log | sort | uniq -c | sort -rn
```

Common error types to look for:
- Missing function arguments
- Undefined variables
- Invalid resource references
- Init failures (missing provider blocks)

### 3. Fix Remaining .plating Examples

**Priority 1 - String Functions** (likely similar issues to numeric):
- Check for missing required arguments
- Source: `pyvider-components/src/pyvider/components/functions/string_manipulation.plating/examples/*.tf`

**Priority 2 - Collection Functions**:
- Source: `pyvider-components/src/pyvider/components/functions/collection_functions.plating/examples/*.tf`

**Priority 3 - Resources**:
- `pyvider-components/src/pyvider/components/resources/*/examples/*.tf`

### 4. Migrate Working Test Examples

The `examples/` directory contains working test configurations:
```
examples/
├── numeric_functions_test/     ✅ Validates
├── string_functions_test/      ✅ Validates
├── file_content_test/          ✅ Validates
├── local_directory_test/       ✅ Validates
├── jq_test/                    ✅ Validates
├── integrated_test/            ✅ Validates
└── ... (more working tests)
```

**Action**: Extract working examples from these test directories and add as additional `.plating/examples/*.tf` files.

### 5. Remove Static Examples Directory
After all examples are migrated and validating:
```bash
rm -rf examples/
git add examples/
git commit -m "Remove static examples directory - all migrated to plating"
```

## Validation Script

Created: `/Users/tim/code/gh/provide-io/terraform-provider-pyvider/scripts/validate_all_examples.sh`

Runs `terraform init`, `validate`, `plan`, and `apply` on all 126 generated examples.

## Files Modified

### In plating repository:
- `src/plating/example_compiler.py` - Removed complete example generation

### In pyvider-components repository:
- `src/pyvider/components/functions/numeric_functions.plating/examples/example.tf` - Fixed round() calls

### In terraform-provider-pyvider repository:
- `scripts/validate_all_examples.sh` - Created validation script
- `docs/examples/` - Regenerated from plating

## Expected End State

1. **All 126+ examples validate successfully** (terraform init, validate, plan, apply)
2. **No static `examples/` directory** - everything generated from `.plating`
3. **All `.plating/examples/*.tf` files are high quality** and demonstrate real-world usage
4. **Documentation is always up-to-date** - generated from code via plating
5. **No files over ~600 lines** - all examples are focused and readable

## Quick Commands Reference

```bash
# Regenerate docs from plating
make generate-docs

# Validate all examples
./scripts/validate_all_examples.sh

# Test specific example
cd docs/examples/function/add/example
terraform init && terraform validate && terraform plan

# Find all .plating example files
find /Users/tim/code/gh/provide-io/pyvider-components -path "*/.plating/examples/*.tf"

# Count examples by type
ls -1 docs/examples/*/* | wc -l
```

## Contact

Last updated: 2025-10-16
Status: In progress - numeric functions fixed, 116 examples still need fixes
