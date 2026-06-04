# Specification: Metric List Rename

## MODIFIED Requirements

### Requirement: Variable Rename

The metric list variable `B200_KEY_METRICS` in `helpers/ncu_utils.py` SHALL be renamed to `RTX5090_KEY_METRICS`.

#### Scenario: No B200 prefix in variable names
WHEN `grep 'B200_KEY_METRICS' helpers/ncu_utils.py` is run
THEN it MUST return zero matches

#### Scenario: New variable exported
WHEN `RTX5090_KEY_METRICS` is referenced in `helpers/ncu_utils.py`
THEN it MUST be a module-level list of metric name strings

### Requirement: Import Update in analyze_reports.py

All imports of `B200_KEY_METRICS` in `helpers/analyze_reports.py` SHALL be updated to `RTX5090_KEY_METRICS`.

#### Scenario: No B200 import
WHEN `grep 'B200_KEY_METRICS' helpers/analyze_reports.py` is run
THEN it MUST return zero matches

#### Scenario: RTX5090 import present
WHEN `helpers/analyze_reports.py` is imported
THEN it MUST successfully import `RTX5090_KEY_METRICS` from `ncu_utils`

### Requirement: Comment and Docstring Update

All comments and docstrings referencing B200, sm_100, or the old metric list name SHALL be updated to reference RTX 5090, sm_120, and the new metric list name.

#### Scenario: No B200 references in helpers/
WHEN `grep -ri 'B200\|b200\|sm_100\|sm100' helpers/` is run
THEN it MUST return zero matches
