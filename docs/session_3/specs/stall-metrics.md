# Specification: Stall Metrics Verification

## MODIFIED Requirements

### Requirement: Stall Metric Names Verified

The `STALL_METRICS` list in `helpers/extract_stall_hotspots.py` SHALL contain only metric names confirmed present on sm_120.

#### Scenario: All stall metrics exist
WHEN each metric in STALL_METRICS is checked against `action.metric_names()` output from the local 5090
THEN at least 80% MUST be present

#### Scenario: Missing stall metrics handled
WHEN a stall metric from the B200 list does not exist on sm_120
THEN it MUST be removed from STALL_METRICS or annotated as UNVERIFIED

### Requirement: PM Sampling Metrics Verified

The `DEFAULT_METRICS` list in `helpers/plot_timeline.py` SHALL contain only metric names confirmed present on sm_120 (or with explicit "may not populate" annotations already present).

#### Scenario: PM sampling metrics checked
WHEN each metric in DEFAULT_METRICS is checked against the ncu report
THEN missing metrics MUST be either removed or retain the existing "may not populate" annotation
