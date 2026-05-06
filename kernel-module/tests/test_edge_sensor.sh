#!/bin/bash
# test_edge_sensor.sh — Validates edge_sensor kernel module behavior
# Requires: sudo, kernel module built at ../src/edge_sensor.ko

set -e

MODULE_NAME="edge_sensor"
MODULE_PATH="$(dirname "$0")/../src/edge_sensor.ko"
PROC_FILE="/proc/edge_sensor"
PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

echo "=== edge_sensor module tests ==="
echo ""

# --- Test: module file exists ---
echo "[1] Module file exists"
if [ -f "$MODULE_PATH" ]; then
    pass "$MODULE_PATH found"
else
    fail "$MODULE_PATH not found — run 'make' first"
    exit 1
fi

# --- Test: load module ---
echo "[2] Load module"
if sudo insmod "$MODULE_PATH" 2>/dev/null; then
    pass "insmod succeeded"
else
    fail "insmod failed"
    exit 1
fi

# --- Test: procfs entry created ---
echo "[3] /proc/edge_sensor exists"
if [ -f "$PROC_FILE" ]; then
    pass "$PROC_FILE created"
else
    fail "$PROC_FILE not found"
    sudo rmmod "$MODULE_NAME" 2>/dev/null
    exit 1
fi

# --- Test: output format ---
echo "[4] Output format (key=value)"
OUTPUT=$(cat "$PROC_FILE")
echo "     Output: $(echo "$OUTPUT" | tr '\n' ' ')"

VALID_FORMAT=true
while IFS= read -r line; do
    if [[ ! "$line" =~ ^[a-z_]+=[-]?[0-9]+$ ]]; then
        fail "bad format: '$line'"
        VALID_FORMAT=false
    fi
done <<< "$OUTPUT"
if [ "$VALID_FORMAT" = true ]; then
    pass "all lines match key=value format"
fi

# --- Test: expected keys present ---
echo "[5] Expected keys present"
for key in cpu_temp_c mem_pressure_pct tcp_retrans_segs; do
    if echo "$OUTPUT" | grep -q "^${key}="; then
        pass "$key present"
    else
        fail "$key missing"
    fi
done

# --- Test: value ranges ---
echo "[6] Value sanity checks"
CPU_TEMP=$(echo "$OUTPUT" | grep "^cpu_temp_c=" | cut -d= -f2)
MEM_PCT=$(echo "$OUTPUT" | grep "^mem_pressure_pct=" | cut -d= -f2)
TCP_RETRANS=$(echo "$OUTPUT" | grep "^tcp_retrans_segs=" | cut -d= -f2)

if [ "$CPU_TEMP" -ge -1 ] && [ "$CPU_TEMP" -le 120 ]; then
    pass "cpu_temp_c=$CPU_TEMP (range: -1 to 120)"
else
    fail "cpu_temp_c=$CPU_TEMP out of range"
fi

if [ "$MEM_PCT" -ge -1 ] && [ "$MEM_PCT" -le 100 ]; then
    pass "mem_pressure_pct=$MEM_PCT (range: -1 to 100)"
else
    fail "mem_pressure_pct=$MEM_PCT out of range"
fi

if [ "$TCP_RETRANS" -ge -1 ]; then
    pass "tcp_retrans_segs=$TCP_RETRANS (>= -1)"
else
    fail "tcp_retrans_segs=$TCP_RETRANS invalid"
fi

# --- Test: multiple reads return data ---
echo "[7] Multiple reads consistent"
OUTPUT2=$(cat "$PROC_FILE")
if [ -n "$OUTPUT2" ] && echo "$OUTPUT2" | grep -q "^cpu_temp_c="; then
    pass "second read returns valid data"
else
    fail "second read failed or empty"
fi

# --- Test: unload module ---
echo "[8] Unload module"
if sudo rmmod "$MODULE_NAME" 2>/dev/null; then
    pass "rmmod succeeded"
else
    fail "rmmod failed"
fi

# --- Test: procfs entry removed ---
echo "[9] /proc/edge_sensor removed after unload"
if [ ! -f "$PROC_FILE" ]; then
    pass "$PROC_FILE removed"
else
    fail "$PROC_FILE still exists"
fi

# --- Summary ---
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
