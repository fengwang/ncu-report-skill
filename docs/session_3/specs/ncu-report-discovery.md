# Specification: ncu_report Discovery

## MODIFIED Requirements

### Requirement: Package Directory Support

The `_locate_ncu_report()` function SHALL check for both `ncu_report.py` (single-file module) and `ncu_report/__init__.py` (package directory) when searching candidate paths.

#### Scenario: Package directory detected
WHEN the ncu_report module exists as a package directory (with `__init__.py`)
THEN `_locate_ncu_report()` MUST return the parent directory of the package

#### Scenario: Single file detected
WHEN the ncu_report module exists as a single `.py` file
THEN `_locate_ncu_report()` MUST return the directory containing it (existing behavior preserved)

### Requirement: Updated Candidate Paths

The candidate path list SHALL include paths matching ncu 2026.2.x installations, not just 2026.1.x.

#### Scenario: Glob pattern covers version variants
WHEN the function searches for ncu_report
THEN the glob patterns MUST match `nsight-compute-2026.*` (not hardcoded to a single version)

### Requirement: Docstring Path Update

The module docstring SHALL reference the correct ncu_report path for the local installation.

#### Scenario: Docstring accuracy
WHEN a user reads the `ncu_utils.py` docstring
THEN the PYTHONPATH example MUST reference a version-agnostic or current path pattern
