# Specification: Evidence Gap Resolution

## ADDED Requirements

### Requirement: G-1 — Max Dynamic Shared Memory Per Block

The maximum dynamic shared memory per block on RTX 5090, obtainable via `cudaFuncSetAttribute(kernel, cudaFuncAttributeMaxDynamicSharedMemorySize, N)`, SHALL be determined experimentally.

#### Scenario: G-1 resolved
WHEN a test kernel calls `cudaFuncSetAttribute` with increasing N values
THEN the maximum accepted value MUST be documented in the gap resolution report

### Requirement: G-2 — Metric Name Diff

A complete diff between the B200 curated metric list and sm_120's `action.metric_names()` output SHALL be produced.

#### Scenario: G-2 resolved
WHEN the diff is produced
THEN it MUST categorize each B200 metric as: present, removed, or renamed on sm_120

### Requirement: G-5 — TMEM Metric Availability

The availability of TMEM-related metrics on RTX 5090 SHALL be checked by examining `action.metric_names()` output for `tmem` or `TMEM` substrings.

#### Scenario: G-5 resolved
WHEN the metric list is searched for TMEM-related names
THEN the result (present or absent) MUST be documented

### Requirement: G-6 — ncu_report Import Path

The verified `ncu_report` Python module import path SHALL be documented.

#### Scenario: G-6 resolved
WHEN `python3 -c "import ncu_report; print(ncu_report.__file__)"` is run
THEN the output path MUST be documented and the import MUST succeed

### Requirement: G-8 — Shared Memory Carveout Options

The available shared memory carveout configurations on RTX 5090 SHALL be tested via `cudaFuncSetCacheConfig`.

#### Scenario: G-8 resolved
WHEN different `cudaFuncCacheConfig` values are tested
THEN the results (which values are accepted) MUST be documented
