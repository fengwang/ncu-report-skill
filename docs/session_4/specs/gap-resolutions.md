# Specification: gap-resolutions

## ADDED Requirements

### Requirement: G-4 cluster launch support documented

The result of testing `cudaLaunchKernelEx` with cluster dimensions on RTX 5090 SHALL be documented in `reference/09-common-issues.md`.

#### Scenario: Cluster test executed
WHEN a test kernel attempts `cudaLaunchKernelEx` with `cudaLaunchAttributeClusterDimension = {2,1,1}` on RTX 5090
THEN the outcome (supported, rejected, or unavailable) SHALL be recorded

#### Scenario: Documentation exists
WHEN `reference/09-common-issues.md` is reviewed
THEN it SHALL contain a section documenting RTX 5090 cluster launch support status with the test result

### Requirement: G-7 effective bandwidth measured

The effective GDDR7 bandwidth under ncu profiling conditions SHALL be measured and documented in `reference/09-common-issues.md`.

#### Scenario: Bandwidth measured with dedicated kernel
WHEN a device-to-device copy kernel (float4, ≥256 MB buffers) is profiled under ncu on RTX 5090
THEN `dram__bytes_op_read.sum.per_second` and `dram__bytes_op_write.sum.per_second` SHALL be extracted

#### Scenario: Result compared to theoretical
WHEN the bandwidth measurement is documented
THEN it SHALL state both the measured value and the theoretical peak (1.792 TB/s) with the percentage achieved

#### Scenario: Throttling caveat included
WHEN the bandwidth measurement is documented
THEN it SHALL note any thermal/power throttling observed during the measurement
