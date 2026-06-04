# Evidence Map

This document traces every major claim in the RTX 5090 adaptation to its evidence source, confidence level, and known gaps.

**Confidence Scale:**
- **Verified** — Confirmed from local hardware query (`cudaDeviceProp`, `nvidia-smi`) or tool output.
- **Official** — From NVIDIA product pages, whitepapers, or developer documentation.
- **High** — Multiple independent reliable sources agree.
- **Medium** — Single source or minor source disagreements.
- **Speculative** — Inferred, extrapolated, or from unverified community reports.

**Rule:** Speculative claims MUST NOT become MUST/SHALL requirements. They may inform SHOULD/MAY guidance or be flagged for validation.

---

## 1. Core Hardware Specifications

| Claim | Evidence | Source | Confidence | Gap / Risk |
|---|---|---|---|---|
| CC 12.0 / sm_120 | `cudaDeviceProp.major=12, minor=0` | Local GPU query | Verified | None |
| 170 SMs | `cudaDeviceProp.multiProcessorCount=170` | Local GPU query | Verified | None |
| 1,536 max threads/SM | `cudaDeviceProp.maxThreadsPerMultiProcessor=1536` | Local GPU query | Verified | None |
| 48 max warps/SM | Derived: 1536 ÷ 32 = 48 | Derived from verified data | Verified | None |
| 24 max blocks/SM | `cudaDeviceProp.maxBlocksPerMultiProcessor=24` | Local GPU query | Verified | **Disagrees with some web sources claiming 32.** Local value is authoritative. |
| 100 KB shared mem/SM | `cudaDeviceProp.sharedMemPerMultiprocessor=102400` | Local GPU query | Verified | Some sources claim 128 KB. 102,400 B = 100 KB is the runtime-reported max carveout. |
| 48 KB shared mem/block (default) | `cudaDeviceProp.sharedMemPerBlock=49152` | Local GPU query | Verified | Opt-in max via `cudaFuncSetAttribute` may be higher — needs validation in Session 3. |
| 65,536 regs/SM (256 KB) | `cudaDeviceProp.regsPerMultiprocessor=65536` | Local GPU query | Verified | None |
| 96 MB L2 cache | `cudaDeviceProp.l2CacheSize=100663296` | Local GPU query | Verified | None |
| 60 MB persistent L2 max | `cudaDeviceProp.persistingL2CacheMaxSize=62914560` | Local GPU query | Verified | None |
| 512-bit memory bus | `cudaDeviceProp.memoryBusWidth=512` | Local GPU query | Verified | None |
| ~31.4 GB global memory | `cudaDeviceProp.totalGlobalMem=33711521792` | Local GPU query | Verified | Marketed as 32 GB; difference is OS/driver reserved. |

## 2. Clock Speeds & Throughput

| Claim | Evidence | Source | Confidence | Gap / Risk |
|---|---|---|---|---|
| Base clock 2,017 MHz | Product specifications | NVIDIA official product page | Official | Actual sustained clocks vary with thermal/power state. |
| Boost clock 2,407 MHz | Product specifications | NVIDIA official product page | Official | This is maximum boost; sustained boost under ncu profiling may be lower due to power draw. |
| ~1,792 GB/s memory bandwidth | 28 Gbps × 512 bits ÷ 8 | Derived from official specs | Official | Theoretical peak. Effective bandwidth is ~85-90% in practice. |
| FP32 104.8 TFLOPS | 21,760 cores × 2,407 MHz × 2 (FMA) | Derived from official specs | Official | Boost-clock dependent. |
| BF16/FP16 Tensor 209.51 TFLOPS (dense) | NVIDIA spec sheet, multiple sources | NVIDIA, RunPod, Spheron | High | Some rounding variance across sources (209–210 range). |
| FP8 Tensor 419 TFLOPS (dense) | NVIDIA spec sheet | NVIDIA | High | None |
| FP4 Tensor sparse 3,352 TOPS | NVIDIA marketing ("AI TOPS") | NVIDIA | Official | This is the sparse (2:4) figure. Dense FP4 is ~1,676 TOPS. |
| FP64 ~1.64 TFLOPS | 1/64 of FP32 rate | Architecture documentation | High | Consumer Blackwell intentionally limits FP64. |

## 3. Architecture Features

| Claim | Evidence | Source | Confidence | Gap / Risk |
|---|---|---|---|---|
| GB202-300-A1 die | Die analysis photos, product teardowns | TechPowerUp, Geeky Gadgets | High | None |
| TSMC 4NP process | NVIDIA whitepaper | NVIDIA RTX Blackwell whitepaper | Official | None |
| 5th gen Tensor Cores (tcgen05) | Architecture documentation | NVIDIA Blackwell tuning guide | Official | Availability of tcgen05 PTX on sm_120 needs compile-time verification in Session 1. |
| TMEM 256 KB per SM | Blackwell architecture docs | NVIDIA Blackwell tuning guide | Official | Runtime accessibility on consumer Blackwell (vs data-center) is **not independently verified**. |
| No NVLink | Product specifications | NVIDIA product page | Official | None |
| PCIe 5.0 × 16 | Product specifications | NVIDIA product page | Official | None |
| 575 W TDP | Product specifications | NVIDIA product page | Official | None |
| GDDR7 at 28 Gbps/pin | Product specifications | NVIDIA product page | Official | None |

## 4. Metric Name Compatibility (sm_100 → sm_120)

| Claim | Evidence | Source | Confidence | Gap / Risk |
|---|---|---|---|---|
| `smsp__sass_inst_executed_op_*` naming exists on sm_120 | Documented for sm_100; sm_120 compatibility assumed | NVIDIA NCU docs for Blackwell | Medium | **Not validated on local 5090.** Metric names can change between CC versions. Session 3 will validate incrementally. |
| Stall ratio metrics use `.ratio` suffix on sm_120 | Documented for sm_100 | NVIDIA NCU docs | Medium | **Not validated.** Same risk as above. |
| `dram__bytes_read.sum + dram__bytes_write.sum` pattern | Documented for sm_100 | NVIDIA NCU docs | Medium | Needs validation. GDDR7 controller may report differently than HBM3e. |
| Some B200 metrics may not exist on sm_120 | CC version differences historically cause metric changes | Historical precedent (Ampere→Hopper→Blackwell) | High | **The full metric list MUST be validated.** This is the highest-risk area of the adaptation. |
| `action.metric_names()` can enumerate available metrics | NCU Python API documentation | NVIDIA NCU docs | High | Reliable method for runtime validation. |

## 5. Diagnosis Thresholds

| Claim | Evidence | Source | Confidence | Gap / Risk |
|---|---|---|---|---|
| "Small grid" threshold: grid < 170 blocks | Derived from 170 SMs (one block/SM = minimum for full utilization) | Derived from verified SM count | Verified | Simple derivation; correct. |
| Memory bandwidth ceiling ~1.8 TB/s affects decode diagnosis | RTX 5090 has 4.4× less bandwidth than B200 | Derived from verified specs | Verified | The 4.4× bandwidth gap makes RTX 5090 decode workloads ~4× more memory-bound than equivalent B200 workloads at same batch size. |
| Occupancy ceiling at 48 warps/SM | Verified max warps/SM = 48 | Local GPU query | Verified | None |
| Shared memory tiling must fit 100 KB/SM, 48 KB/block default | Verified limits | Local GPU query | Verified | Opt-in max per block is unknown — could be up to 100 KB. Needs `cudaFuncSetAttribute` test. |
| Roofline BF16 breakpoint at ~117 FLOPs/byte | 209.51 TFLOPS ÷ 1.792 TB/s | Derived | High | Depends on sustained boost clock and effective bandwidth. |

## 6. LLM Inference Patterns

| Claim | Evidence | Source | Confidence | Gap / Risk |
|---|---|---|---|---|
| Single-token decode is memory-bandwidth-bound on RTX 5090 | Arithmetic intensity of decode ≪ roofline breakpoint | First principles + industry consensus | High | Well-established for all GPUs; RTX 5090's lower bandwidth makes it more pronounced. |
| KV-cache access dominates decode memory traffic | Standard transformer architecture property | Industry knowledge | High | None |
| FP8 quantization reduces decode memory traffic ~2× vs FP16 | Half the bytes per element | First principles | High | Actual speedup depends on dequantization overhead. |
| FP4 (NVFP4) is natively supported on RTX 5090 tensor cores | Blackwell architecture feature | NVIDIA documentation | Official | Framework maturity for FP4 is still developing (TensorRT-LLM has support, vLLM partial). |
| FlashAttention-style fused attention reduces memory traffic | Avoids materializing full attention matrix | Algorithm property | High | Specific implementation for sm_120 may differ from sm_100 version. |
| 32 GB VRAM fits ~35B FP16 or ~70B INT4 models | Model size estimation (2 bytes/param FP16, 0.5 bytes/param INT4) + KV-cache overhead | Standard estimation | Medium | Actual fit depends on KV-cache size (context length × layers × heads × head_dim × 2 × batch × precision). |
| TensorRT-LLM provides highest throughput on Blackwell | NVIDIA benchmarks, community benchmarks | RunPod, NVIDIA blog | High | May not hold for all model sizes/configurations. |

## 7. Toolchain Compatibility

| Claim | Evidence | Source | Confidence | Gap / Risk |
|---|---|---|---|---|
| CUDA 13.2 supports sm_120 | nvcc compiles and runs on local 5090 | Local tool output | Verified | None |
| ncu 2026.2 supports Blackwell profiling | Tool version and successful GPU detection | Local tool output | Verified | Full sm_120 section/metric support needs validation during profiling. |
| Driver 610.43 supports RTX 5090 | GPU detected and functional | nvidia-smi output | Verified | None |
| `ncu_report` Python module path follows CUDA install convention | Documented pattern | NVIDIA NCU docs | High | Exact path needs verification: `/usr/local/cuda-13.2/nsight-compute-2026.2.0/extras/python/` |
| `sudo ncu` or modprobe may be needed for perf counters | Documented requirement for non-root profiling | NVIDIA NCU docs, current skill's 09-common-issues.md | High | Applies to all Linux systems; not RTX 5090-specific. |

## 8. B200 vs RTX 5090 Differences

| Claim | Evidence | Source | Confidence | Gap / Risk |
|---|---|---|---|---|
| sm_100 binaries do NOT run on sm_120 | Different compute capabilities | CUDA architecture rules | Verified | None — this is a hard CUDA constraint. |
| B200 has dual-die (GB100), RTX 5090 is monolithic (GB202) | Architecture documentation | NVIDIA whitepapers | Official | Eliminates all dual-die/NV-HBI considerations from the skill. |
| B200's 228 KB shared/SM vs RTX 5090's 100 KB fundamentally changes tiling | Verified specs | Local GPU query vs B200 docs | Verified | Kernels tuned for B200's large shared memory will fail or perform poorly. |
| B200's 2CTA (CTA-pair) cluster mode may not apply to RTX 5090 | B200-specific TPC cooperation feature | NVIDIA Blackwell tuning guide | Medium | **Needs verification.** The 2CTA feature may be data-center only. |
| Warp-level tensor core execution (tcgen05) applies to both | Blackwell architecture-wide feature | NVIDIA documentation | High | ISA availability on sm_120 should be confirmed by attempting PTX compilation. |
| HBM-specific optimizations (multi-bank, cross-die) do not apply | RTX 5090 uses GDDR7 | Hardware difference | Verified | All HBM-specific guidance must be removed or replaced with GDDR7 guidance. |

---

## Key Gaps Requiring Session-Level Validation

| Gap ID | Description | Planned Resolution | Session |
|---|---|---|---|
| G-1 | Max shared memory per block with opt-in (`cudaFuncSetAttribute`) | Write a test kernel that requests max shared memory | Session 3 |
| G-2 | sm_120 metric name compatibility with B200 metric list | Collect ncu report on local 5090, extract `action.metric_names()` | Session 3 |
| G-3 | tcgen05 PTX availability on sm_120 | Attempt compilation of tcgen05 PTX instructions targeting sm_120 | Session 1 |
| G-4 | 2CTA cluster mode availability on consumer Blackwell | Check `cudaDeviceProp` cluster-related fields or attempt cluster launch | Session 1 |
| G-5 | TMEM runtime accessibility on RTX 5090 | Profile a tensor-core kernel and check for TMEM metrics | Session 3 |
| G-6 | `ncu_report` Python module import path on CUDA 13.2 | Verify the exact filesystem path and test import | Session 3 |
| G-7 | Effective GDDR7 bandwidth under profiling | Run a bandwidth benchmark kernel under ncu | Session 4 |
| G-8 | Shared memory carveout options on sm_120 | Test `cudaFuncSetCacheConfig` with various values | Session 3 |
