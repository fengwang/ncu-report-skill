# Session 1 Brainstorming — Core Specs & Programming Guide

**Date:** 2026-06-04
**Status:** Approved

---

## Context

Session 1 replaces all B200 (sm_100) targeting with RTX 5090 (sm_120) across three files: SKILL.md, blackwell-cuda-programming.md, README.md. The programming guide requires a full rewrite due to fundamental ISA differences between data-center and consumer Blackwell.

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Language | English | Align with PRD and broader audience (was Chinese) |
| Compile target | `sm_120a` | Architecture-specific variant, enables sm_120-only optimizations |
| Comparison column | RTX 5090 only | Single-target guide; no B200/H100 comparison column |
| Data-center-only features | Remove entirely | tcgen05, TMEM, 2CTA, decompression engine, NVLink — all confirmed absent |
| Guide structure | Full restructure | Too many removed sections to preserve original layout |
| Feature validation | Ran live on GPU | All evidence gaps (G-3, G-4, G-5) resolved with ptxas/runtime tests |

## Critical Discovery: sm_120 Tensor Core ISA

**The single most impactful finding:** sm_120 (consumer Blackwell) does NOT share the Tensor Core ISA with sm_100 (data-center Blackwell). Consumer Blackwell uses the Ampere/Ada-era `mma.sync` ISA.

### Validation Results (ran on local RTX 5090, CUDA 13.2)

| Feature | sm_120 Status | Test Method | Evidence |
|---|---|---|---|
| tcgen05 (B200 TC PTX) | **NOT available** | `nvcc -arch=sm_120` PTX compile | ptxas: "Instruction 'tcgen05.alloc' not supported on .target 'sm_120'" |
| wgmma (Hopper TC PTX) | **NOT available** | `nvcc -arch=sm_120` PTX compile | ptxas: "Instruction 'wgmma.mma_async with floating point types' not supported on .target 'sm_120'" |
| cta_group/2CTA | **NOT available** | `nvcc -arch=sm_120` PTX compile | ptxas: "Feature '.cta_group::1' not supported on .target 'sm_120'" |
| TMEM | **NOT available** | Requires tcgen05 (unavailable) | Transitive: TMEM is only accessible via tcgen05 instructions |
| mma.sync FP16/BF16 | **Available** | `nvcc -arch=sm_120` PTX compile | Compiles clean (m16n8k16 shape) |
| mma.sync FP8 (e4m3) | **Available** | `nvcc -arch=sm_120` PTX compile | Compiles clean (m16n8k32 shape) |
| mma.sync FP4 | **NOT available** | `nvcc -arch=sm_120` PTX compile | ptxas: "mma with FP6/FP4 floating point type not supported on .target 'sm_120'" |
| WMMA API | **Available** | `nvcc -arch=sm_120` compile | Compiles clean (nvcuda::wmma) |
| Thread Block Clusters | **Available** | `cudaDevAttrClusterLaunch` query | Returns 1 |
| cp.async | **Available** | `nvcc -arch=sm_120` PTX compile | Compiles clean |
| sm_120a variant | **Available** | `nvcc -arch=sm_120a` compile | Compiles clean |

### Shared Memory Validation

| Property | Value | Source |
|---|---|---|
| sharedMemPerMultiprocessor | 102,400 B (100 KB) | cudaDeviceProp |
| sharedMemPerBlock (default) | 49,152 B (48 KB) | cudaDeviceProp |
| sharedMemPerBlockOptin | 101,376 B (99 KB) | cudaDeviceProp |
| reservedSharedMemPerBlock | 1,024 B (1 KB) | cudaDeviceProp |
| cudaFuncSetAttribute 101376 | Success | Runtime test |
| cudaFuncSetAttribute 102400 | Fails (invalid argument) | Runtime test |

**Conclusion:** Max usable shared memory per block with opt-in is **99 KB** (101,376 bytes). The runtime reserves 1 KB per block.

## sm_100 vs sm_120 Feature Comparison

| Feature | sm_100 (B200) | sm_120 (RTX 5090) |
|---|---|---|
| Die | Dual-die GB100 (NV-HBI) | Monolithic GB202 |
| Tensor Core PTX | tcgen05 (new, 1-thread MMA) | mma.sync (Ampere/Ada era) |
| Warpgroup MMA | wgmma (Hopper) | Not available |
| TMEM | 256 KB/SM | Not available |
| CTA Pair (2CTA) | cta_group::1/::2 | Not available |
| FP4 via PTX | tcgen05 path | Not available (library-only) |
| FP8 via PTX | tcgen05 path + mma.sync | mma.sync only |
| Thread Block Clusters | Up to 16 (non-portable) | Available (max TBD) |
| Shared mem/SM | 228 KB | 100 KB |
| Shared mem opt-in max/block | ~227 KB | 99 KB |
| NVLink | 1.8 TB/s (NVLink 5) | Not available |
| Memory | 192 GB HBM3e @ 8 TB/s | 32 GB GDDR7 @ ~1.8 TB/s |
| L2 Cache | 126 MB | 96 MB |
| Decompression Engine | Available | Not confirmed on consumer |

## Proposed Guide Structure (Full Restructure)

1. **Target Platform & Verified Specs** — RTX 5090 parameter table (single-column, from verified cudaDeviceProp)
2. **Architecture Overview** — Monolithic GB202, sm_120 vs sm_100 key differences, what's NOT available
3. **Memory Hierarchy** — GDDR7 @ ~1.8 TB/s, 96 MB L2 / 60 MB persistent, 100 KB shared/SM (99 KB opt-in)
4. **Tensor Core Programming** — mma.sync/WMMA as the ISA, cuBLAS/CUTLASS as primary development path, why tcgen05/wgmma don't exist here
5. **Precision Spectrum & Roofline** — FP4→FP64 with roofline breakpoints per precision, FP4 library-only note
6. **LLM Inference Profiling** — Single-token decode as memory-bandwidth-bound regime, KV-cache sizing within 32 GB, quantization strategy with RTX 5090 bandwidth constraints
7. **Core Guidelines (1–16, rewritten)** — All numbers updated for RTX 5090, English prose
8. **Special Kernel Types** — Updated reference table including LLM decode attention for RTX 5090
9. **Pre-Coding Checklist** — Updated for sm_120a capabilities

## Blast Radius

| File | Action |
|---|---|
| `SKILL.md` | Replace B200 specs with RTX 5090, update description/compile target/metric reference |
| `blackwell-cuda-programming.md` | Full rewrite per structure above |
| `README.md` | Update GPU target, toolchain versions, description |

## Risks

1. **FP4 documentation gap**: RTX 5090 markets FP4 3,352 TOPS but PTX mma.sync doesn't support FP4 on sm_120. FP4 is only accessible through cuBLAS/CUTLASS library paths. Must document this clearly to avoid user confusion.
2. **Guideline number density**: 16 guidelines × RTX 5090 number swaps across prose, NCU metric references, and exception sections. High risk of missed B200 numbers in deep text.
3. **LLM inference section scope**: New content with no prior template. Must stay within profiling guidance (not general LLM optimization).
