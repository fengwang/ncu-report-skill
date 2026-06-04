# Specification: Stale Filename References

## MODIFIED Requirements

### Requirement: Updated Metric File References

References to the old filename `08-b200-metric-names.md` in SKILL.md and root README.md SHALL be updated to `08-rtx5090-metric-names.md`.

#### Scenario: SKILL.md reference updated
WHEN `grep '08-b200-metric-names' SKILL.md` is run
THEN it MUST return zero matches

#### Scenario: README.md reference updated
WHEN `grep '08-b200-metric-names' README.md` is run
THEN it MUST return zero matches

#### Scenario: No other content changes
WHEN the diff for SKILL.md and README.md is reviewed
THEN ONLY the filename string SHALL have changed (no other content modifications)
