# Specification: pm-sampling-metrics

## MODIFIED Requirements

### Requirement: PM sampling metrics reflect sm_120 hardware-counter equivalents

PM sampling metric lists in reference docs SHALL use the sm_120 hardware-counter timeseries names validated in Session 3, not the old sm_100 stall-breakdown timeseries names.

#### Scenario: reference/08 PM sampling section uses sm_120 names
WHEN the PM Sampling section of `reference/08-rtx5090-metric-names.md` is reviewed
THEN it SHALL contain only hardware-counter timeseries metric names validated on sm_120
AND it SHALL NOT contain old stall-breakdown timeseries names (e.g., `smsp__pcsamp_warps_issue_stalled_*`)

#### Scenario: reference/04 PM sampling example uses sm_120 names
WHEN the PM Sampling code example in `reference/04-python-api.md` is reviewed
THEN it SHALL reference sm_120-compatible PM sampling metrics
