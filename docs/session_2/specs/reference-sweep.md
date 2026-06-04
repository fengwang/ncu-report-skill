# Spec: Reference File B200→RTX 5090 Sweep (MC-4)

## MODIFIED Requirements

### Requirement: 00-directory-layout.md Updates

#### Scenario: Compile flags in environment variable example
WHEN the nvcc example in the environment variable section uses `-gencode` flags
THEN it SHALL target `sm_120` (not `compute_100,code=sm_100`)

#### Scenario: Example run directory name
WHEN example run directory names reference a GPU
THEN they SHALL use "rtx5090" (not "b200")

### Requirement: 02-harness-guide.md Updates

#### Scenario: Compile command in template section
WHEN the nvcc compile command is shown
THEN it SHALL target `sm_120` with `-arch=sm_120` or `-gencode=arch=compute_120,code=sm_120`

### Requirement: 03-collection.md Updates

#### Scenario: Set mapping table GPU reference
WHEN the rough mapping table references a GPU and ncu version
THEN it SHALL say "RTX 5090, ncu 2026.2" (not "B200, ncu 2026.1")

### Requirement: 04-python-api.md Updates

#### Scenario: ncu_report module path
WHEN the import path for ncu_report is shown
THEN it SHALL reference `nsight-compute-2026.2.0` (not `2026.1.0`)

#### Scenario: Metric names file reference
WHEN the document links to the metric names reference
THEN it SHALL link to `08-rtx5090-metric-names.md` (not `08-b200-metric-names.md`)

### Requirement: 07-report-template.md Updates

#### Scenario: Target GPU line in template
WHEN the report template shows the target GPU
THEN it SHALL say "NVIDIA RTX 5090 (170 SM, CC 12.0)" (not "NVIDIA B200 (148 SM, CC 10.0)")

#### Scenario: Compile flags in template
WHEN compile flags are shown in the template
THEN they SHALL target sm_120

### Requirement: Zero B200 references across all minor files

#### Scenario: Global sweep
WHEN `grep -ri 'B200\|sm_100' reference/00-directory-layout.md reference/02-harness-guide.md reference/03-collection.md reference/04-python-api.md reference/07-report-template.md` is run
THEN it SHALL return zero matches
