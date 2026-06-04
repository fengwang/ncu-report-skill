# Specification: Precision Spectrum & Roofline

Covers capability N-5 (Precision Roofline Table).

---

## ADDED Requirements

### Requirement: Precision Roofline Table

The programming guide SHALL contain a table showing, for each supported precision format (FP4, FP8, INT8, BF16/FP16, TF32, FP32, FP64): peak throughput (TFLOPS/TOPS), arithmetic intensity breakpoint (FLOPs/byte), and whether it is accessible via PTX mma.sync on sm_120 or library-only.

#### Scenario: Table covers all precisions
WHEN the precision roofline table is read
THEN it includes rows for: FP4 (sparse/dense), FP8 (sparse/dense), INT8, BF16/FP16, TF32, FP32, and FP64.

#### Scenario: Breakpoints use RTX 5090 bandwidth
WHEN the arithmetic intensity breakpoints are calculated
THEN they use ~1,792 GB/s (RTX 5090 theoretical peak) as the bandwidth denominator.

#### Scenario: FP4 marked as library-only
WHEN the FP4 row in the precision table is read
THEN it explicitly states that FP4 is accessible only through cuBLAS/CUTLASS (not via PTX mma.sync on sm_120).

#### Scenario: FP8 PTX availability noted
WHEN the FP8 row is read
THEN it notes FP8 is accessible via both PTX mma.sync and cuBLAS/CUTLASS on sm_120.

### Requirement: Roofline Interpretation Guidance

The section SHALL include a brief explanation of how to use the roofline breakpoints: if a kernel's arithmetic intensity is below the breakpoint for its precision, it is memory-bandwidth-bound; above it, compute-bound.

#### Scenario: Roofline interpretation present
WHEN the precision section is read
THEN it contains guidance on interpreting arithmetic intensity relative to the breakpoint values.
