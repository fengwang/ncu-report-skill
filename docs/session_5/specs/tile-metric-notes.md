# Spec: NC-9 — Tile Kernel Metric Validation Notes

## MODIFIED Requirements

### Requirement: Tile kernel metric behavior documented
reference/08-rtx5090-metric-names.md SHALL document which existing metrics are meaningful for tile kernels.

#### Scenario: Metric applicability noted
WHEN the metric names reference is read
THEN it SHALL contain a section or annotations indicating which metric categories behave differently for tile kernels vs SIMT

#### Scenario: Validation status
WHEN the tile metric section is read
THEN metrics that were tested on actual tile kernels SHALL be marked as "validated (tile)"
AND metrics whose tile behavior is unknown SHALL be marked accordingly

### Requirement: Tile-specific metric discoveries
Any metrics that only appear or only have meaningful values for tile kernels SHALL be documented.

#### Scenario: New metrics listed
WHEN hardware validation reveals metrics specific to tile kernel execution
THEN those metrics SHALL be added to the reference with their name, description, and which validation kernel produced them
