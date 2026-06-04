# Specification: sm_120 Tensor Core Guide

Covers capability N-4 (sm_120 Tensor Core Guide).

---

## ADDED Requirements

### Requirement: Tensor Core Programming Section

The programming guide SHALL contain a "Tensor Core Programming" section documenting the Tensor Core programming model available on sm_120.

#### Scenario: mma.sync documented as primary ISA
WHEN the Tensor Core section is read
THEN it identifies `mma.sync` (Ampere/Ada-era PTX) as the Tensor Core instruction available on sm_120, with supported shapes and precision combinations.

#### Scenario: WMMA API documented
WHEN the Tensor Core section is read
THEN it mentions the WMMA C++ API as an alternative to inline PTX for Tensor Core programming.

#### Scenario: cuBLAS/CUTLASS as recommended path
WHEN the Tensor Core section is read
THEN it recommends cuBLAS and CUTLASS as the primary development path for Tensor Core workloads, especially for FP4 operations.

#### Scenario: tcgen05/wgmma absence explained
WHEN the Tensor Core section is read
THEN it contains a note explaining that tcgen05 (B200/sm_100) and wgmma (Hopper/sm_90) are NOT available on sm_120, with a one-sentence explanation of what this means for users reading NVIDIA's data-center Blackwell documentation.

#### Scenario: No tcgen05 code examples
WHEN `grep -i 'tcgen05' blackwell-cuda-programming.md` is run
THEN matches appear only in the "not available" explanation, not in code examples or practical guidance.
