# Project Contract: ncu-report-skill RTX 5090 Adaptation

**Version:** 1.1 (amended for CUDA 13.3 / session 5)
**Date:** 2026-06-11

This contract was compiled in two passes: (1) drafted from the PRD, repository evidence, and hardware research; (2) adversarially reviewed to remove unsupported, ambiguous, over-specified, and untestable requirements. Only the revised contract is presented.

---

## 1. Scope

Replace all NVIDIA B200 (sm_100, CC 10.0) targeting in the `ncu-report-skill` repository with NVIDIA GeForce RTX 5090 (sm_120, CC 12.0) targeting. Add LLM inference diagnosis content focused on single-user low-latency decode. Retain the general-purpose CUDA profiling capability. Upgrade from CUDA 13.2 to CUDA 13.3 and add tile kernel (`__tile_global__`, `cuda::tiles`) programming model support.

## 2. Invariants

These conditions MUST hold at all times during and after the adaptation:

| ID | Invariant |
|---|---|
| INV-1 | The skill directory layout (SKILL.md, blackwell-cuda-programming.md, helpers/, reference/) is preserved. No top-level files are added or removed without explicit justification. |
| INV-2 | Helper scripts depend only on Python standard library + `ncu_report` module. No pip-installed packages. |
| INV-3 | The six-dimension analysis framework (occupancy, tail effect, stalls, tensor core, timeline, memory) is preserved. Dimensions may be recalibrated but not removed. |
| INV-4 | The harness template compiles and runs on the local RTX 5090 (CUDA 13.3, sm_120). |
| INV-5 | The diagnosis playbook pattern→cause→fix structure is preserved. Patterns may be recalibrated, added, or updated but the structure remains. |
| INV-6 | Every hardware parameter referenced in any file matches RTX 5090 verified specs (see PRD §4.1). |

## 3. Requirements

### 3.1 MUST (blocking — session cannot pass without these)

| ID | Requirement | Testable By |
|---|---|---|
| M-1 | All B200/sm_100 hardware specifications are replaced with RTX 5090/sm_120 specifications from verified local GPU data. | `grep -ri "sm_100\|B200\|sm100\|b200" .` returns zero matches (excluding docs/ and git history). |
| M-2 | Compile target in all examples is `-arch=sm_120` or equivalent. | `grep -r "sm_100\|compute_100" .` returns zero matches (excluding docs/). |
| M-3 | Occupancy calculations use: 48 warps/SM, 24 blocks/SM, 1,536 threads/SM, 100 KB shared/SM, 65,536 regs/SM. | Manual review of reference/05-analysis-dimensions.md and SKILL.md. |
| M-4 | Memory parameters use: ~1.8 TB/s bandwidth, 96 MB L2, 32 GB VRAM, GDDR7, 512-bit bus. No HBM references. | `grep -ri "HBM\|8 TB\|126 MB\|192 GB" .` returns zero matches (excluding docs/). |
| M-5 | Diagnosis playbook thresholds are recalibrated for RTX 5090 parameters. | Each pattern has a numeric threshold referencing RTX 5090 specs (170 SMs, 1.8 TB/s, etc.). |
| M-6 | The curated metric list is renamed from `B200_KEY_METRICS` and contains only metrics believed to exist on sm_120. | Variable renamed; no `B200` prefix remains in helpers/ncu_utils.py. |
| M-7 | Harness template targets sm_120 and includes a working compilation command. | `nvcc -arch=sm_120 -lineinfo harness_template.cu -o test_harness` succeeds. |

### 3.2 SHOULD (expected — deviation requires documented reason)

| ID | Requirement | Testable By |
|---|---|---|
| S-1 | LLM inference section added to the diagnosis playbook with at least 3 LLM-specific patterns (decode bandwidth, KV-cache, quantized GEMM). | Patterns exist in reference/06-diagnosis-playbook.md with signal/fix pairs. |
| S-2 | Programming guide (blackwell-cuda-programming.md) rewritten for RTX 5090 consumer Blackwell constraints. | Section on shared memory strategy references 100 KB/SM limit, not 228 KB. |
| S-3 | Roofline breakpoints documented for each supported precision (FP4, FP8, INT8, BF16, FP16, TF32, FP32). | Table of breakpoints exists in analysis dimensions or programming guide. |
| S-4 | Framework kernel profiling guidance added for at least TensorRT-LLM and vLLM. | Section exists in workflow or diagnosis playbook covering opaque kernel analysis. |
| S-5 | Metric names validated against local 5090 ncu output. Unverified metrics flagged in the metric list. | Metric list has comments or annotations distinguishing verified from unverified. |
| S-6 | Shared memory opt-in maximum per block validated via `cudaFuncSetAttribute` test. | Validated value documented in programming guide. |
| S-7 | File `08-b200-metric-names.md` renamed to reflect RTX 5090 targeting. | File name contains "rtx5090" or "sm120" instead of "b200". |

### 3.3 MAY (optional — nice to have)

| ID | Requirement |
|---|---|
| O-1 | GDDR7-specific memory access pattern guidance (bank structure, burst length differences from HBM). |
| O-2 | Persistent L2 cache partitioning strategy for KV-cache pinning (up to 60 MB available). |
| O-3 | Power-management profiling notes (575W TDP, clock throttling under sustained load). |
| O-4 | FP4/NVFP4 dual-level scaling explanation and profiling methodology. |
| O-5 | Comparison table showing key differences from B200 (for users familiar with data-center Blackwell). |

## 4. Acceptance Criteria (project-level)

The project is complete when:

1. All M-* requirements pass their testable-by checks.
2. At least 5 of 7 S-* requirements are implemented (deviations documented).
3. The end-to-end workflow (harness → compile → collect → parse → diagnose → report) completes successfully on the local RTX 5090.
4. No file in the repository (outside of docs/) references B200, sm_100, or B200-specific hardware values.
5. CUDA version is 13.3 across all files (no 13.2 references outside docs/).
6. Tile kernel programming model documented with profiling guidance and at least 4 diagnosis patterns.

## 5. Constraints

| ID | Constraint | Rationale |
|---|---|---|
| C-1 | No new pip dependencies. | Skill must work on any machine with ncu installed. |
| C-2 | No internet access required at runtime. | Profiling happens on air-gapped workstations. |
| C-3 | Preserve existing file structure. | Consumers of the skill rely on current paths. |
| C-4 | B200 backward compatibility is NOT required. | Explicit decision — clean replacement. |
| C-5 | No code changes to safetensors_loader.h or list_flashinfer_workloads.py unless they reference B200 specs. | These are data-format utilities, not GPU-specific. |

## 6. Definition of Done

A session is done when:
1. All MUST items in its session contract pass their deterministic checks.
2. All modified files are committed with descriptive messages.
3. No regressions in files outside the session's `allowed_files` blast radius.
4. The handoff requirements in the session contract are met.

The project is done when all 5 sessions are complete and the project-level acceptance criteria (§4) pass.
