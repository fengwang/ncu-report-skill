# Specification: Metric Validation

## ADDED Requirements

### Requirement: Validated Metric List

The curated metric list in `helpers/ncu_utils.py` SHALL contain only metric names that have been validated against actual `action.metric_names()` output from an ncu report collected on the local RTX 5090 (sm_120).

#### Scenario: Metric present on sm_120
WHEN a metric from the curated list is checked against `action.metric_names()` output
THEN it MUST appear in the output (case-sensitive exact match)

#### Scenario: Metric absent on sm_120
WHEN a metric from the old B200 list does not appear in sm_120's `action.metric_names()` output
THEN it MUST be removed from the curated list OR replaced with the correct sm_120 name

#### Scenario: Unverifiable metric
WHEN a metric cannot be validated (e.g., requires specific kernel type not available in the test kernel)
THEN it MUST be annotated with `# UNVERIFIED on sm_120` in the source code

### Requirement: Metric Diff Documentation

A documented diff between sm_100 and sm_120 metric names SHALL be produced.

#### Scenario: Diff categories
WHEN the metric diff is produced
THEN it MUST categorize metrics as: present-on-both, removed-on-sm_120, new-on-sm_120

### Requirement: Validation Threshold

At least 80% of metrics in the curated list MUST be confirmed present on sm_120 via `action.metric_names()`.

#### Scenario: Below threshold
WHEN fewer than 80% of curated metrics are confirmed present
THEN the session MUST escalate to a dedicated metric discovery sub-task before updating analysis scripts
