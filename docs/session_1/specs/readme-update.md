# Specification: README.md Update

Covers capability M-5 (README.md).

---

## MODIFIED Requirements

### Requirement: GPU Target in README

README.md SHALL reference RTX 5090 (sm_120) instead of B200 (sm_100) in all locations: description, requirements section, and any inline references.

#### Scenario: Description updated
WHEN the first paragraph / description of README.md is read
THEN it references RTX 5090 and sm_120 (not B200 / sm_100).

#### Scenario: Requirements section updated
WHEN the Requirements section is read
THEN it mentions CUDA 13.2 (tested), ncu 2026.2 (tested), and sm_120 metric names.

#### Scenario: Zero B200 references
WHEN `grep -i 'B200\|sm_100\|sm100' README.md` is run
THEN the output is empty.

### Requirement: Toolchain Versions

The README.md requirements section SHALL list accurate toolchain versions matching the local verified environment.

#### Scenario: Toolchain versions match local
WHEN the Requirements section is read
THEN it lists: CUDA Toolkit 13.2, Nsight Compute 2026.2, and notes the skill is optimized for RTX 5090 / sm_120 metric names.
