# Specification: dram-metric-names

## MODIFIED Requirements

### Requirement: DRAM metric names use sm_120 validated naming

All DRAM metric references outside `docs/` SHALL use the sm_120 naming convention validated in Session 3. The `_op_` infix distinguishes sm_120 DRAM metrics from sm_100.

#### Scenario: All DRAM read metrics use op_read naming
WHEN `grep -rn 'dram__bytes_read\b\|dram__sectors_read\b' --include='*.md' --include='*.py' --exclude-dir=docs .` is run
THEN zero matches are returned (only `dram__bytes_op_read` and `dram__sectors_op_read` variants exist)

#### Scenario: All DRAM write metrics use op_write naming
WHEN `grep -rn 'dram__bytes_write\b\|dram__sectors_write\b' --include='*.md' --include='*.py' --exclude-dir=docs .` is run
THEN zero matches are returned (only `dram__bytes_op_write` and `dram__sectors_op_write` variants exist)

#### Scenario: Metric suffixes preserved after rename
WHEN a metric like `dram__bytes_read.sum.pct_of_peak_sustained_elapsed` is renamed
THEN the result SHALL be `dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed` (suffix unchanged)

#### Scenario: ncu_utils.py already correct
WHEN `grep -c 'dram__bytes_op_read\|dram__bytes_op_write' helpers/ncu_utils.py` is run
THEN the count SHALL be >= 2 (confirming helpers already use correct names)
