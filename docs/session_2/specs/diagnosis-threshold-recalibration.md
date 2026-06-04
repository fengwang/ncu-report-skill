# Spec: Diagnosis Threshold Recalibration (MC-2)

## MODIFIED Requirements

### Requirement: Pattern A — Small Grid Threshold

Pattern A's grid threshold SHALL reference 170 SMs (RTX 5090) instead of 148 SMs (B200).

#### Scenario: Small grid example
WHEN Pattern A's signal section gives an example of a small grid
THEN it SHALL say "170-SM RTX 5090" (not "148-SM B200")

### Requirement: Pattern B — Tail Effect SM Count

Pattern B's tail effect calculations SHALL use 170 SMs.

#### Scenario: SM count in tail calculations
WHEN tail effect magnitude is discussed relative to the full GPU
THEN it SHALL reference 170 SMs

### Requirement: Pattern C — Uncoalesced Loads Bandwidth Impact

Pattern C SHALL note that uncoalesced access on GDDR7 (~1.8 TB/s) is proportionally more costly than on HBM.

#### Scenario: Bandwidth impact note
WHEN Pattern C discusses the performance impact of uncoalesced access
THEN it SHALL note the ~1.8 TB/s bandwidth ceiling makes each wasted sector more expensive

### Requirement: Pattern E — Latency-Bound Fix Directions

Pattern E's fix directions SHALL reference sm_120-available async load mechanisms.

#### Scenario: Async load recommendation
WHEN Pattern E recommends async load approaches
THEN it SHALL recommend `cp.async` (Ampere+) and NOT mention `tcgen05.cp` (unavailable on sm_120)

### Requirement: Pattern F — Compute Without Tensor Cores

Pattern F SHALL reference sm_120-available tensor core ISA and throughput figures.

#### Scenario: Tensor core ISA reference
WHEN Pattern F recommends tensor core adoption
THEN it SHALL reference `mma.sync`/`WMMA` and CUTLASS/cuBLAS (not tcgen05.mma or wgmma)

#### Scenario: Throughput comparison
WHEN Pattern F states the throughput advantage of tensor cores
THEN it SHALL use RTX 5090 figures (BF16 tensor: 209.5 TFLOPS vs FP32 scalar: 104.8 TFLOPS = 2x for BF16->FP32)

### Requirement: Cross-Reference Updates

All "Blackwell principle N" cross-references SHALL be updated to named section headings from the restructured programming guide.

#### Scenario: Cross-reference format
WHEN a pattern includes a cross-reference to the programming guide
THEN it SHALL use format "See `blackwell-cuda-programming.md` § <Section Name>"

### Requirement: GPU Identifier Sweep

All "B200" and "sm_100" text SHALL be replaced with "RTX 5090" and "sm_120".

#### Scenario: No B200 references remain
WHEN `grep -ri 'B200\|sm_100' reference/06-diagnosis-playbook.md` is run
THEN it SHALL return zero matches
