# Spec: Analysis Dimensions Recalibration (MC-1)

## MODIFIED Requirements

### Requirement: Dimension 1 — SM Occupancy & Launch Geometry

All hardware parameters in Dimension 1 SHALL use RTX 5090 verified specs.

#### Scenario: SM count in wave math
WHEN occupancy and wave calculations reference SM count
THEN the value SHALL be 170 (not 148)

#### Scenario: Warp limits in occupancy analysis
WHEN occupancy analysis references max warps per SM
THEN the value SHALL be 48 (not 64)

#### Scenario: Block limits in occupancy analysis
WHEN occupancy analysis references max blocks per SM
THEN the value SHALL be 24 (not 32)

#### Scenario: Shared memory limits
WHEN occupancy analysis references shared memory per SM
THEN the value SHALL be 100 KB (not 228 KB)

#### Scenario: Default shared memory per block
WHEN shared memory per block default is referenced
THEN the value SHALL be 48 KB (not 227 KB)

#### Scenario: Register limits
WHEN register limits are referenced
THEN the value SHALL be 65,536 per SM (256 KB)

### Requirement: Dimension 2 — Thread-Block Balance

PM sampling interval note SHALL reference RTX 5090 instead of B200.

#### Scenario: PM sampling interval
WHEN PM sampling characteristics are discussed
THEN the reference SHALL say "RTX 5090" instead of "B200"

### Requirement: Dimension 4 — Tensor Core Utilization

Tensor core section SHALL reference sm_120-available ISA (mma.sync/WMMA) instead of tcgen05.

#### Scenario: Tensor core ISA reference
WHEN fix directions mention tensor core programming approaches
THEN they SHALL reference mma.sync and WMMA API (not tcgen05.mma or TMEM)

### Requirement: Dimension 5 — SM Utilization Timeline

PM sampling interval note SHALL reference RTX 5090.

#### Scenario: PM sampling interval caveat
WHEN the PM sampling timing caveat is stated
THEN it SHALL reference RTX 5090 instead of B200

### Requirement: Dimension 6 — Memory Access Pattern

DRAM bandwidth references SHALL use ~1.8 TB/s.

#### Scenario: Bandwidth ceiling reference
WHEN DRAM bandwidth capacity is referenced
THEN the value SHALL be ~1.8 TB/s (not 8 TB/s)

### Requirement: GPU identifier references

All references to "B200" or "sm_100" SHALL be replaced with "RTX 5090" or "sm_120".

#### Scenario: No B200 references remain
WHEN `grep -ri 'B200\|sm_100' reference/05-analysis-dimensions.md` is run
THEN it SHALL return zero matches
