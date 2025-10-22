#!/bin/bash
set -e

# ----------------------------
# Set QUIET=1 for quiet mode, 0 for verbose
# ----------------------------
QUIET=${QUIET:-1}   # Default to quiet if not set

# Helper function to run commands either quietly or verbosely
run_cmd() {
    if [ "$QUIET" -eq 1 ]; then
        "$@" &> /dev/null
    else
        "$@"
    fi
}

# Remove previous project to avoid warnings
[ -d "TestProject" ] && rm -rf TestProject

# ----------------------------
# Create a SciUnit project
# ----------------------------
run_cmd sciunit create TestProject

# ----------------------------
# Prepare a simple script for testing
# ----------------------------
echo -e "#!/bin/bash\necho Hello SciUnit" > hello_world.sh
chmod +x hello_world.sh
# Set the expected output to the output of the test command above
EXPECTED_OUTPUT="Hello SciUnit"

# ----------------------------
# Execute the script via SciUnit
# ----------------------------
OUTPUT=$(run_cmd sciunit exec ./hello_world.sh; echo $? )  # Capture exit code
EXEC_EXIT_CODE=$?

# ----------------------------
# Check that at least one experiment was created
# ----------------------------
EXPERIMENTS=$(sciunit list)  # Not quiet for checks
LIST_EXIT_CODE=$?

# ----------------------------
# Test that SciUnit repeat works
# ----------------------------
# This will rerun the last experiment
LAST_EXPERIMENT_ID=$(sciunit list | tail -n1 | awk '{print $1}')
REPEAT_OUTPUT=$(sciunit repeat "$LAST_EXPERIMENT_ID")
REPEAT_EXIT_CODE=$?

# ----------------------------
# Determine pass/fail
# ----------------------------
PASS=true

# Check sciunit exec did not fail
if [ "$EXEC_EXIT_CODE" -ne 0 ]; then
    echo sciunit exec fail
    PASS=false
fi

# Check there is an experiment to rerun
if [[ "$LIST_EXIT_CODE" -ne 0 || -z "$EXPERIMENTS" ]]; then
    echo sciunit list fail
    PASS=false
fi

# Check that repeat succeeded
if [[ "$REPEAT_EXIT_CODE" -ne 0 || "$REPEAT_OUTPUT" != *"$EXPECTED_OUTPUT"* ]]; then
    echo sciunit repeat fail
    PASS=false
fi

# ----------------------------
# Output results
# ----------------------------
if [ "$QUIET" -eq 1 ]; then
    if [ "$PASS" = true ]; then
        echo "PASS"
        exit 0
    else
        echo "FAIL"
        exit 1
    fi
else
    echo "---------------------------"
    echo "SciUnit Test Report"
    echo "---------------------------"
    echo "Experiment created: $( [ -z "$(sciunit list)" ] && echo NO || echo YES )"
    echo "Execution success: $( [ "$EXEC_EXIT_CODE" -eq 0 ] && echo YES || echo NO )"
    echo "Repeat success: $( [[ "$REPEAT_EXIT_CODE" -eq 0 || "$REPEAT_OUTPUT" == *"$EXPECTED_OUTPUT"* ]] && echo YES || echo NO)"
    echo "Overall: $( [ "$PASS" = true ] && echo PASS || echo FAIL )"
    exit $([ "$PASS" = true ] && echo 0 || echo 1)
fi
