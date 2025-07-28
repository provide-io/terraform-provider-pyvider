#!/bin/bash
# pyvider/components/tf/nested_data_test/run_diagnostic.sh
# Systematic diagnostic script for nested data issues

set -e

echo "🔍 Pyvider Nested Data Diagnostic Test Suite"
echo "=============================================="

# Setup
TEST_DIR="$(dirname "$0")"
LOG_FILE="$TEST_DIR/diagnostic.log"
RESULTS_FILE="$TEST_DIR/test_results.json"

# Clear previous logs
> "$LOG_FILE"
> "$RESULTS_FILE"

echo "📝 Test directory: $TEST_DIR"
echo "📋 Log file: $LOG_FILE"
echo "📊 Results file: $RESULTS_FILE"
echo ""

# Function to run a test and capture results
run_test() {
    local test_name="$1"
    local test_description="$2"
    local terraform_target="$3"
    
    echo "🧪 Testing: $test_name - $test_description"
    
    # Record test start
    echo "=== $test_name - $test_description ===" >> "$LOG_FILE"
    echo "Started at: $(date)" >> "$LOG_FILE"
    
    # Initialize if needed
    if [ ! -f ".terraform.lock.hcl" ]; then
        echo "   Initializing Terraform..."
        if ! terraform init >> "$LOG_FILE" 2>&1; then
            echo "   ❌ FAILED: Terraform init failed"
            echo "   See $LOG_FILE for details"
            return 1
        fi
    fi
    
    # Try to plan the specific target
    echo "   Planning..."
    if terraform plan -target="$terraform_target" >> "$LOG_FILE" 2>&1; then
        echo "   ✅ PLAN: Success"
        
        # Try to apply
        echo "   Applying..."
        if terraform apply -auto-approve -target="$terraform_target" >> "$LOG_FILE" 2>&1; then
            echo "   ✅ APPLY: Success"
            
            # Try to get output
            echo "   Getting output..."
            if terraform output -json >> "$RESULTS_FILE" 2>&1; then
                echo "   ✅ OUTPUT: Success"
                echo "   🎉 $test_name: COMPLETE SUCCESS"
                return 0
            else
                echo "   ⚠️  OUTPUT: Failed"
                echo "   🔶 $test_name: PARTIAL SUCCESS (apply worked but output failed)"
                return 2
            fi
        else
            echo "   ❌ APPLY: Failed"
            echo "   🔴 $test_name: APPLY FAILURE"
            return 3
        fi
    else
        echo "   ❌ PLAN: Failed"
        echo "   🔴 $test_name: PLAN FAILURE"
        return 4
    fi
}

# Function to analyze error logs
analyze_errors() {
    echo ""
    echo "🔍 Error Analysis"
    echo "=================="
    
    # Look for specific error patterns
    if grep -q "inconsistent map element types" "$LOG_FILE"; then
        echo "🎯 FOUND: CTY type inconsistency error"
        echo "   Pattern: inconsistent map element types"
        grep -A 5 -B 5 "inconsistent map element types" "$LOG_FILE"
    fi
    
    if grep -q "cty.String then cty.Map" "$LOG_FILE"; then
        echo "🎯 FOUND: String -> Map type conflict"
        grep -A 3 -B 3 "cty.String then cty.Map" "$LOG_FILE"
    fi
    
    if grep -q "DynamicPseudoType" "$LOG_FILE"; then
        echo "🎯 FOUND: Dynamic type issue"
        grep -A 3 -B 3 "DynamicPseudoType" "$LOG_FILE"
    fi
    
    if grep -q "OPENTOFU CRASH" "$LOG_FILE"; then
        echo "🎯 FOUND: OpenTofu crash"
        grep -A 10 -B 5 "OPENTOFU CRASH" "$LOG_FILE"
    fi
    
    echo ""
}

# Clean start
echo "🧹 Cleaning previous state..."
terraform destroy -auto-approve >> "$LOG_FILE" 2>&1 || true

echo ""
echo "🚀 Starting Progressive Tests"
echo "============================="

# Level 1: Simple Map Test (should work)
echo ""
if run_test "Level1" "Simple string-to-string map" "data.pyvider_simple_map_test.level1"; then
    LEVEL1_SUCCESS=true
else
    LEVEL1_SUCCESS=false
    echo "❌ Level 1 failed - basic string maps don't work"
    analyze_errors
    echo "🛑 Stopping here - fundamental issue with string maps"
    exit 1
fi

# Level 2: Mixed Type Map Test (likely to fail)
echo ""
if run_test "Level2_Minimal" "Minimal mixed type map" "data.pyvider_mixed_map_test.level2_minimal"; then
    LEVEL2_MINIMAL_SUCCESS=true
    echo "✅ Mixed types work! Trying complex version..."
    
    # Try complex mixed types
    if run_test "Level2_Complex" "Complex mixed type map" "data.pyvider_mixed_map_test.level2_complex"; then
        LEVEL2_COMPLEX_SUCCESS=true
    else
        LEVEL2_COMPLEX_SUCCESS=false
        echo "❌ Complex mixed types failed, but minimal worked"
    fi
else
    LEVEL2_MINIMAL_SUCCESS=false
    LEVEL2_COMPLEX_SUCCESS=false
    echo "❌ Level 2 failed - mixed types are the problem"
    analyze_errors
fi

# Level 3: Structured Object Test (if Level 2 worked)
echo ""
if [ "$LEVEL2_MINIMAL_SUCCESS" = true ]; then
    if run_test "Level3" "Structured objects with defined schema" "data.pyvider_structured_object_test.level3"; then
        LEVEL3_SUCCESS=true
    else
        LEVEL3_SUCCESS=false
        echo "❌ Level 3 failed - structured objects don't work"
        analyze_errors
    fi
else
    echo "⏭️  Skipping Level 3 (structured objects) - Level 2 failed"
    LEVEL3_SUCCESS=false
fi

# Level 4: Resource Test (if Level 3 worked)
echo ""
if [ "$LEVEL3_SUCCESS" = true ]; then
    if run_test "Level4" "Nested resource with complex state" "pyvider_nested_resource_test.level4"; then
        LEVEL4_SUCCESS=true
    else
        LEVEL4_SUCCESS=false
        echo "❌ Level 4 failed - nested resources don't work"
        analyze_errors
    fi
else
    echo "⏭️  Skipping Level 4 (nested resources) - Level 3 failed"
    LEVEL4_SUCCESS=false
fi

# Level 5: Function Test (independent test)
echo ""
echo "🔧 Testing Level 5 (functions) independently..."
if terraform plan -target="output.level5_function_simple" >> "$LOG_FILE" 2>&1; then
    echo "✅ Functions work with nested data"
    LEVEL5_SUCCESS=true
else
    echo "❌ Functions fail with nested data"
    LEVEL5_SUCCESS=false
    analyze_errors
fi

# Summary
echo ""
echo "📊 Test Summary"
echo "==============="
echo "Level 1 (Simple Maps):     $([ "$LEVEL1_SUCCESS" = true ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "Level 2 (Mixed Types):     $([ "$LEVEL2_MINIMAL_SUCCESS" = true ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "Level 2 (Complex Mixed):   $([ "$LEVEL2_COMPLEX_SUCCESS" = true ] && echo "✅ PASS" || echo "❌ FAIL")"  
echo "Level 3 (Structured Obj):  $([ "$LEVEL3_SUCCESS" = true ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "Level 4 (Nested Resource): $([ "$LEVEL4_SUCCESS" = true ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "Level 5 (Functions):       $([ "$LEVEL5_SUCCESS" = true ] && echo "✅ PASS" || echo "❌ FAIL")"

echo ""
echo "🔍 Key Findings:"

if [ "$LEVEL1_SUCCESS" = false ]; then
    echo "❌ CRITICAL: Basic string maps don't work - fundamental schema issue"
elif [ "$LEVEL2_MINIMAL_SUCCESS" = false ]; then
    echo "❌ ISSUE: Mixed type maps fail - CTY type consistency problem"
    echo "   💡 Recommendation: Use only homogeneous maps (all strings, all numbers, etc.)"
elif [ "$LEVEL2_COMPLEX_SUCCESS" = false ]; then
    echo "⚠️  ISSUE: Complex mixed types fail but simple mixed types work"
    echo "   💡 Recommendation: Limit complexity of mixed type structures"
elif [ "$LEVEL3_SUCCESS" = false ]; then
    echo "⚠️  ISSUE: Well-defined structured objects fail"
    echo "   💡 Recommendation: Use flat schemas instead of nested objects"
else
    echo "✅ All data source tests pass! The issue may be HTTP API specific."
fi

if [ "$LEVEL5_SUCCESS" = true ]; then
    echo "✅ Functions handle nested data correctly"
else
    echo "❌ Functions also fail with nested data - systemic issue"
fi

echo ""
echo "📝 Detailed logs: $LOG_FILE"
echo "📊 Results JSON: $RESULTS_FILE"

# Final error analysis
analyze_errors

echo ""
echo "🏁 Diagnostic Complete"