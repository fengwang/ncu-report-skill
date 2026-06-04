# Session 2 Proposal

## Motivation

All 10 reference documents still target B200/sm_100. Every threshold, example, metric name reference, and fix direction assumes data-center Blackwell parameters. Using these docs to profile on RTX 5090 produces incorrect diagnoses. Session 1 updated the core files; Session 2 completes the reference layer.

## Changes

1. Replace all B200/sm_100 hardware values with RTX 5090/sm_120 across 10 reference files
2. Recalibrate diagnosis thresholds for 170 SMs, ~1.8 TB/s, 48 warps/SM, 100 KB shared/SM
3. Add 3 LLM-specific diagnosis patterns (O, P, Q) for single-user decode workloads
4. Add framework kernel profiling guidance (Phase 2.5 in workflow)
5. Rename metric names file from B200 to RTX 5090
6. Update ISA references from DC-only (tcgen05/wgmma/TMEM) to sm_120-available (cp.async/mma.sync/WMMA)
7. Update cross-references to match Session 1's restructured programming guide
8. Add consumer GPU-specific troubleshooting (display driver, power throttling)

## Capabilities

### New Capabilities

| ID | Capability | Spec File |
|---|---|---|
| NC-1 | LLM decode diagnosis patterns (O, P, Q) | `specs/llm-diagnosis-patterns.md` |
| NC-2 | Framework kernel profiling guidance (Phase 2.5) | `specs/framework-profiling-guidance.md` |
| NC-3 | Consumer GPU troubleshooting section | `specs/consumer-gpu-issues.md` |

### Modified Capabilities

| ID | Capability | Spec File |
|---|---|---|
| MC-1 | Six-dimension analysis framework (RTX 5090 recalibration) | `specs/analysis-dimensions-recalibration.md` |
| MC-2 | Diagnosis playbook thresholds (8 existing patterns) | `specs/diagnosis-threshold-recalibration.md` |
| MC-3 | Metric names reference (rename + sm_120 flagging) | `specs/metric-names-migration.md` |
| MC-4 | Reference file B200→RTX 5090 sweep (minor files) | `specs/reference-sweep.md` |

## Impact

- **Files**: All 10 files in `reference/` (modify 9, rename+rewrite 1)
- **APIs**: None
- **Dependencies**: None (no new deps)
- **Cross-file consistency**: All metric file links (`08-b200-metric-names.md`) must update to new filename, all cross-references to programming guide must update to named sections
