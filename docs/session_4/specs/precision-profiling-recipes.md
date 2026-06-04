# Specification: precision-profiling-recipes

## ADDED Requirements

### Requirement: Per-precision profiling recipes in programming guide

`blackwell-cuda-programming.md` SHALL contain profiling recipes for BF16/FP16, FP8, INT8, and FP4 precisions on RTX 5090.

#### Scenario: Each recipe has required elements
WHEN a precision recipe section is reviewed
THEN it SHALL contain: (1) when to use this precision, (2) which tensor core pipe metric identifies it, (3) an exact ncu collection command, (4) key metrics with expected ranges, (5) comparison baseline

#### Scenario: BF16 recipe exists
WHEN `grep -c 'BF16.*recipe\|Profiling BF16\|BF16/FP16' blackwell-cuda-programming.md` is run
THEN the count SHALL be >= 1

#### Scenario: FP8 recipe exists
WHEN `grep -c 'FP8.*recipe\|Profiling FP8' blackwell-cuda-programming.md` is run
THEN the count SHALL be >= 1

#### Scenario: INT8 recipe exists
WHEN `grep -c 'INT8.*recipe\|Profiling INT8' blackwell-cuda-programming.md` is run
THEN the count SHALL be >= 1

#### Scenario: FP4 recipe exists
WHEN `grep -c 'FP4.*recipe\|Profiling FP4\|NVFP4' blackwell-cuda-programming.md` is run
THEN the count SHALL be >= 1

#### Scenario: Cross-precision comparison recipe exists
WHEN `blackwell-cuda-programming.md` is reviewed
THEN it SHALL contain a section on comparing the same kernel across multiple precisions

### Requirement: Recipes use RTX 5090-specific values

Recipes SHALL reference RTX 5090 throughput values (209.5 TFLOPS BF16 dense, 419 TFLOPS FP8 dense, etc.) and bandwidth (1.792 TB/s). No generic or B200 values.

#### Scenario: RTX 5090 throughput referenced
WHEN the precision recipes section is reviewed
THEN it SHALL contain at least one reference to RTX 5090 tensor core throughput values
