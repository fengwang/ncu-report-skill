# Product Requirements Document: ncu-report-skill RTX 5090 Adaptation

**Version:** 1.0
**Date:** 2026-06-04
**Status:** Draft

---

## 1. Executive Summary

Adapt the existing `ncu-report-skill` from targeting NVIDIA B200 (sm_100, CC 10.0) to targeting NVIDIA GeForce RTX 5090 (sm_120, CC 12.0). The adapted skill will serve as a comprehensive Nsight Compute profiling framework for CUDA kernels on the RTX 5090, with emphasis on low-latency LLM inference workloads in a single-user decode scenario.

Despite both GPUs belonging to the Blackwell architecture family, they have fundamentally different compute capabilities, memory hierarchies, and operational characteristics. This is a full replacement — not a parameter swap.

## 2. Problem Statement

The current skill is built around B200's data-center Blackwell profile: 148 SMs, 64 warps/SM, 228 KB shared memory/SM, 192 GB HBM3e at 8 TB/s. Every threshold, metric name, diagnosis pattern, and optimization recommendation is calibrated for those parameters.

The RTX 5090 differs in every dimension that matters for kernel profiling:

| Parameter | B200 (current) | RTX 5090 (target) | Impact |
|---|---|---|---|
| Compute Capability | 10.0 (sm_100) | 12.0 (sm_120) | Binary incompatible; metric names may differ |
| Max Warps/SM | 64 | 48 | Occupancy ceilings change |
| Max Blocks/SM | 32 | 24 | Launch geometry constraints tighter |
| Shared Mem/SM | 228 KB | 100 KB | Tiling strategies must shrink |
| Memory Bandwidth | 8 TB/s (HBM3e) | ~1.8 TB/s (GDDR7) | 4.4× lower; decode is deeply memory-bound |
| VRAM | 192 GB | 32 GB | Model size constrained |
| L2 Cache | 126 MB | 96 MB | Persistent L2 budget tighter |

Using the B200 skill on an RTX 5090 will produce incorrect occupancy calculations, wrong threshold diagnoses, and misleading optimization recommendations.

## 3. Target User

A CUDA developer profiling kernels on a local RTX 5090 workstation, working on:
- Custom CUDA kernels for LLM inference (attention, GEMM, fused operators)
- Framework-level kernel analysis (TensorRT-LLM, vLLM, PyTorch)
- General CUDA kernel optimization

Primary inference scenario: **single-user, low-latency autoregressive decode** where memory bandwidth is the dominant bottleneck.

## 4. Hardware Target — RTX 5090 Verified Specifications

### 4.1 Locally Verified (from cudaDeviceProp query)

| Parameter | Value | Source |
|---|---|---|
| GPU Name | NVIDIA GeForce RTX 5090 | `nvidia-smi` |
| Compute Capability | 12.0 | `cudaDeviceProp.major/minor` |
| SM Count | 170 | `cudaDeviceProp.multiProcessorCount` |
| Max Threads/SM | 1,536 | `cudaDeviceProp.maxThreadsPerMultiProcessor` |
| Max Threads/Block | 1,024 | `cudaDeviceProp.maxThreadsPerBlock` |
| Max Blocks/SM | 24 | `cudaDeviceProp.maxBlocksPerMultiProcessor` |
| Warp Size | 32 | `cudaDeviceProp.warpSize` |
| Shared Memory/SM | 102,400 B (100 KB) | `cudaDeviceProp.sharedMemPerMultiprocessor` |
| Shared Memory/Block (default) | 49,152 B (48 KB) | `cudaDeviceProp.sharedMemPerBlock` |
| Registers/SM | 65,536 (256 KB) | `cudaDeviceProp.regsPerMultiprocessor` |
| Registers/Block | 65,536 | `cudaDeviceProp.regsPerBlock` |
| L2 Cache | 100,663,296 B (96 MB) | `cudaDeviceProp.l2CacheSize` |
| Persistent L2 Max | 62,914,560 B (60 MB) | `cudaDeviceProp.persistingL2CacheMaxSize` |
| Memory Bus Width | 512 bit | `cudaDeviceProp.memoryBusWidth` |
| Global Memory | 33,711,521,792 B (~31.4 GB) | `cudaDeviceProp.totalGlobalMem` |
| Max Grid Dim | 2,147,483,647 × 65,535 × 65,535 | `cudaDeviceProp.maxGridSize` |
| Max Block Dim | 1,024 × 1,024 × 64 | `cudaDeviceProp.maxThreadsDim` |

### 4.2 From Official Sources (high confidence)

| Parameter | Value | Source |
|---|---|---|
| GPU Die | GB202-300-A1 | NVIDIA whitepaper, TechPowerUp |
| Process | TSMC 4NP | NVIDIA whitepaper |
| CUDA Cores | 21,760 (128/SM) | NVIDIA product page |
| Tensor Cores (5th gen) | 680 (4/SM) | NVIDIA product page |
| RT Cores (4th gen) | 170 (1/SM) | NVIDIA product page |
| Base Clock | 2,017 MHz | NVIDIA product page |
| Boost Clock | 2,407 MHz | NVIDIA product page |
| Memory Type | GDDR7 | NVIDIA product page |
| Memory Data Rate | 28 Gbps/pin | NVIDIA product page |
| Memory Bandwidth | ~1,792 GB/s | Derived: 28 Gbps × 512 bits / 8 |
| TDP | 575 W | NVIDIA product page |
| PCIe | 5.0 × 16 | NVIDIA product page |
| NVLink | Not supported | NVIDIA product page |
| TMEM/SM | 256 KB | NVIDIA Blackwell tuning guide |

### 4.3 Compute Throughput (from NVIDIA + community benchmarks)

| Precision | Dense | Sparse (2:4) |
|---|---|---|
| FP64 (CUDA cores) | ~1.64 TFLOPS | — |
| FP32 (CUDA cores) | 104.8 TFLOPS | — |
| TF32 (Tensor) | 104.75 TFLOPS | 209.51 TFLOPS |
| BF16/FP16 (Tensor) | 209.51 TFLOPS | 419.01 TFLOPS |
| FP8 (Tensor) | 419.01 TFLOPS | 838.02 TFLOPS |
| INT8 (Tensor) | 838 TOPS | 1,676 TOPS |
| FP4 (Tensor) | ~1,676 TOPS | 3,352 TOPS |

### 4.4 Derived Parameters

| Parameter | Value | Derivation |
|---|---|---|
| Max Warps/SM | 48 | 1,536 threads/SM ÷ 32 threads/warp |
| Total CUDA Cores | 21,760 | 170 SMs × 128 cores/SM |
| Arithmetic Intensity Threshold (BF16, roofline) | 116.8 FLOPs/byte | 209.51 TFLOPS ÷ 1.792 TB/s |
| Arithmetic Intensity Threshold (FP32, roofline) | 58.5 FLOPs/byte | 104.8 TFLOPS ÷ 1.792 TB/s |

## 5. Toolchain Requirements

| Tool | Required Version | Local Version |
|---|---|---|
| CUDA Toolkit | ≥ 12.8 (13.x recommended) | 13.2 (V13.2.78) |
| Nsight Compute CLI (ncu) | ≥ 2026.1 | 2026.2.0.0 |
| NVIDIA Driver | ≥ 570.xx | 610.43.02 |
| Compile Target | `-arch=sm_120` | — |

## 6. Use Cases

### UC-1: Profile a Custom CUDA Kernel
The user writes a `.cu` kernel (e.g., fused attention, quantized GEMM). The skill guides them through building a standalone harness, collecting ncu reports with the right flags for sm_120, parsing metrics, diagnosing bottlenecks, and producing an evidence-backed optimization report.

### UC-2: Profile a Framework Kernel
The user runs an LLM inference framework (TensorRT-LLM, vLLM, PyTorch). The skill helps identify which kernel to profile, collect reports on opaque compiled kernels, interpret metrics without source access, and map findings to framework-level configuration changes.

### UC-3: Diagnose Memory-Bound Decode
Single-token autoregressive decode on RTX 5090. The skill helps identify whether the bottleneck is DRAM bandwidth, L2 capacity, coalescing quality, or KV-cache layout — and recommends quantization or access pattern changes.

### UC-4: Evaluate Quantization Impact
The user profiles the same kernel under different precisions (FP32 → BF16 → FP8 → FP4). The skill helps collect comparable reports, extract precision-specific tensor core utilization, and assess the accuracy/throughput tradeoff.

### UC-5: General CUDA Kernel Optimization
Any CUDA kernel on RTX 5090 — not necessarily LLM-related. The skill provides the full six-dimension analysis framework, calibrated for sm_120 hardware limits.

## 7. Functional Requirements

### FR-1: Hardware Specification Accuracy
All hardware parameters referenced in the skill MUST match the RTX 5090 verified specs (Section 4.1–4.3). No B200 specs SHALL remain in any file.

### FR-2: Compile Target
All compilation examples, harness templates, and collection commands MUST target `sm_120` (CC 12.0). References to `sm_100` MUST be removed.

### FR-3: Occupancy & Launch Geometry
Occupancy calculations MUST use RTX 5090 limits: 48 warps/SM, 24 blocks/SM, 1,536 threads/SM, 100 KB shared memory/SM, 65,536 registers/SM.

### FR-4: Diagnosis Thresholds
The diagnosis playbook MUST recalibrate all pattern-detection thresholds for RTX 5090. Example: "small grid" pattern threshold changes from `grid < 148 blocks` (B200) to `grid < 170 blocks` (RTX 5090).

### FR-5: Metric Name Compatibility
The curated metric list MUST be adapted for sm_120. Metric names that differ between sm_100 and sm_120 MUST be updated. The approach is incremental: start from the B200 baseline, flag known differences, and fix names as they are validated.

### FR-6: Memory Hierarchy Guidance
Analysis and optimization guidance MUST reflect GDDR7 characteristics: ~1.8 TB/s bandwidth (not 8 TB/s), 96 MB L2 (not 126 MB), 100 KB shared/SM (not 228 KB), 48 KB default shared/block (not 227 KB).

### FR-7: LLM Inference Content
The skill SHOULD include LLM-specific diagnosis patterns and optimization recipes, covering:
- Autoregressive decode bottleneck analysis (memory-bandwidth-bound regime)
- KV-cache access pattern profiling
- Quantized GEMM tensor core utilization (FP4, FP8, INT8, BF16)
- Attention kernel profiling (FlashAttention variants, fused attention)
- Framework kernel interpretation (TensorRT-LLM, vLLM, PyTorch)

### FR-8: Precision-Specific Guidance
The skill SHOULD cover the full precision spectrum (FP4, FP8, INT8, BF16/FP16, TF32, FP32) with:
- Roofline breakpoints per precision
- Tensor core pipe identification in ncu metrics
- Expected throughput ranges for each format

### FR-9: General CUDA Profiling
The skill MUST retain its general-purpose CUDA profiling capability. LLM content is additive, not a replacement for the core six-dimension analysis framework.

### FR-10: Helper Scripts
Python helpers MUST work with ncu_report from the local Nsight Compute installation. The `B200_KEY_METRICS` list MUST be renamed and adapted for RTX 5090.

## 8. Non-Functional Requirements

### NFR-1: Self-Contained
The skill MUST remain usable without internet access. All hardware specs, metric names, and thresholds MUST be embedded in the skill files.

### NFR-2: Locally Verifiable
All claims about RTX 5090 behavior SHOULD be verifiable on the local workstation (RTX 5090 + CUDA 13.2 + ncu 2026.2).

### NFR-3: No External Dependencies
Helper scripts MUST use only Python standard library plus the `ncu_report` module shipped with Nsight Compute. No pip-installed packages.

### NFR-4: Backward Compatibility — Not Required
B200 support is explicitly dropped. No backward compatibility with sm_100 is required.

## 9. Architecture & Design Constraints

- **File structure is preserved.** The existing directory layout (SKILL.md, blackwell-cuda-programming.md, helpers/, reference/) remains the same. Files are modified in place.
- **Naming:** File `08-b200-metric-names.md` should be renamed to reflect RTX 5090 targeting.
- **LLM content is additive.** New LLM-specific sections are added to existing documents (programming guide, diagnosis playbook, analysis dimensions). No new top-level files unless justified.
- **Incremental metric validation.** The metric list starts from the B200 baseline and is corrected as metrics are tested on the local 5090. Unverified metrics are flagged, not silently removed.

## 10. Dependencies

| Dependency | Status | Risk |
|---|---|---|
| Local RTX 5090 GPU | Available | None |
| CUDA 13.2 toolkit | Installed | None |
| ncu 2026.2 CLI | Installed | None |
| ncu_report Python module | Available at CUDA install path | Verify import path |
| GPU perf counter access | May require `sudo ncu` or modprobe config | Low — documented in 09-common-issues.md |

## 11. Success Criteria

1. Every hardware parameter in the skill matches verified RTX 5090 specs.
2. Zero references to B200, sm_100, or B200-specific values remain in any file.
3. The harness template compiles and runs on the local RTX 5090 with `-arch=sm_120`.
4. The six-dimension analysis framework produces correct diagnoses when applied to an ncu report collected on the local 5090.
5. The curated metric list contains only metrics confirmed to exist on sm_120.
6. LLM decode-specific diagnosis patterns are present and reference RTX 5090 bandwidth/memory constraints.
7. The full end-to-end workflow (harness → collect → parse → diagnose → report) completes on the local 5090.

## 12. Out of Scope

- Multi-GPU profiling or NVLink guidance (RTX 5090 has no NVLink).
- Batched/throughput-oriented LLM serving optimization (primary focus is single-user decode).
- B200 backward compatibility.
- Framework-specific plugin development (the skill provides profiling guidance, not framework patches).
- Nsight Systems (nsys) integration — the skill focuses on Nsight Compute (ncu).
- Model training workloads — inference only.
