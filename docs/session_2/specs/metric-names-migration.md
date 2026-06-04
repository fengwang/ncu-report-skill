# Spec: Metric Names Migration (MC-3)

## RENAMED Requirements

### Requirement: File Rename

FROM: `reference/08-b200-metric-names.md`
TO: `reference/08-rtx5090-metric-names.md`

#### Scenario: New file exists
WHEN `ls reference/08-rtx5090-metric-names.md` is run
THEN the file SHALL exist

#### Scenario: Old file removed
WHEN `ls reference/08-b200-metric-names.md` is run
THEN the file SHALL NOT exist

## MODIFIED Requirements

### Requirement: Title and Header Update

The document title SHALL read "RTX 5090 (sm_120) Metric Name Reference" (not "B200 (sm_100)").

#### Scenario: Title content
WHEN the document is opened
THEN the first heading SHALL reference RTX 5090 and sm_120

### Requirement: Metric Validation Status

All metrics carried forward from sm_100 SHALL be annotated as "unverified on sm_120, validation pending Session 3".

#### Scenario: Metric group annotations
WHEN a metric group is listed
THEN it SHALL include a note that these names are carried forward from sm_100 and may differ on sm_120

### Requirement: Discovery Commands

The `ncu --query-metrics` example SHALL use the correct chip identifier for RTX 5090.

#### Scenario: Chip identifier
WHEN the discovery command example is shown
THEN it SHALL use `--chip gb202` with a note that this is the RTX 5090 die

### Requirement: ncu Version Reference

The ncu version reference SHALL be updated to 2026.2 (matching local install).

#### Scenario: Version string
WHEN the document mentions the ncu version
THEN it SHALL say "Nsight Compute 2026.2" (not "2026.1")

### Requirement: No B200 References

Zero occurrences of "B200", "b200", or "sm_100" SHALL remain in the file content.

#### Scenario: Clean grep
WHEN `grep -ri 'B200\|sm_100' reference/08-rtx5090-metric-names.md` is run
THEN it SHALL return zero matches
