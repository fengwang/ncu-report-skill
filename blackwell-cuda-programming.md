# GPU Kernel Programming Guide

## Target Platform

All guidance in this document targets the following development environment:

- **GPU:** NVIDIA GeForce RTX 5090 (Compute Capability 12.0, monolithic GB202 die, 170 SMs)
- **CUDA Toolkit:** 13.3
- **Compile target:** `sm_120a` (`-arch=sm_120a` or `-gencode arch=compute_120a,code=sm_120a`)

Compilation example:
```bash
nvcc -arch=sm_120a -lineinfo -O3 -o my_kernel my_kernel.cu
```

---

## RTX 5090 Architecture — Key Parameters

| Parameter | Value |
|---|---|
| GPU Die | GB202-300-A1 (monolithic) |
| Process | TSMC 4NP |
| Compute Capability | 12.0 (sm_120) |
| SM Count | 170 |
| CUDA Cores | 21,760 (128/SM) |
| Tensor Cores (5th gen) | 680 (4/SM) |
| Max Threads/SM | 1,536 |
| Max Warps/SM | 48 |
| Max Blocks/SM | 24 |
| Warp Size | 32 |
| Registers/SM | 65,536 (256 KB) |
| Shared Memory/SM | 100 KB (102,400 B) |
| Shared Memory/Block (default) | 48 KB (49,152 B) |
| Shared Memory/Block (opt-in max) | 99 KB (101,376 B) |
| Reserved Shared Memory/Block | 1 KB (1,024 B) |
| Tensor Memory (TMEM) | Not available on sm_120 |
| L2 Cache | 96 MB (100,663,296 B) |
| Persistent L2 Max | 60 MB (62,914,560 B) |
| Memory Type | GDDR7, 28 Gbps/pin |
| Memory Bus Width | 512-bit |
| Memory Bandwidth | ~1,792 GB/s (theoretical peak) |
| Global Memory | ~31.4 GB (33,711,521,792 B) |
| Base Clock | 2,017 MHz |
| Boost Clock | 2,407 MHz |
| TDP | 575 W |
| PCIe | 5.0 × 16 |
| NVLink | Not supported |

---

## Architecture Overview

### GB202 — Monolithic Consumer Blackwell

The RTX 5090 uses the monolithic GB202 die. Unlike data-center Blackwell (dual-die GB100 connected via NV-HBI), the RTX 5090 is a single chip with no inter-die communication overhead and no NVLink connectivity.

### sm_120 vs Data-Center Blackwell: What's Different

Despite both being "Blackwell" GPUs, the consumer sm_120 and data-center Blackwell have fundamentally different programming models at the Tensor Core level:

| Feature | Data-Center Blackwell | RTX 5090 (sm_120) |
|---|---|---|
| Tensor Core PTX | tcgen05 (single-thread MMA) | mma.sync (warp-cooperative) |
| Warpgroup MMA | wgmma (Hopper-era) | Not available |
| Tensor Memory (TMEM) | 256 KB/SM, dedicated TC memory | Not available |
| CTA Pair (2CTA) | Two SMs cooperate via cta_group | Not available |
| FP4 via PTX | tcgen05 path | Not available (library-only) |
| FP8 via PTX | Available (both paths) | mma.sync only |
| Thread Block Clusters | Up to 16 | Up to 8 (validated) |
| Shared Memory/SM | 228 KB | 100 KB |
| Memory | 192 GB @ 8 TB/s | 32 GB GDDR7 @ ~1.8 TB/s |

**Practical consequence:** NVIDIA documentation describing tcgen05 instructions, TMEM allocation, or cta_group modifiers applies only to data-center Blackwell. On the RTX 5090, Tensor Core programming uses the same `mma.sync` / WMMA interface as Ada Lovelace (sm_89) and Ampere (sm_80), albeit with 5th-generation hardware providing higher throughput and new precision formats.

### What IS Available on sm_120

- **mma.sync PTX:** Warp-cooperative matrix multiply-accumulate. Supports FP16, BF16, TF32, FP8 (e4m3/e5m2), INT8, INT4 via inline PTX.
- **WMMA C++ API:** Higher-level wrapper around mma.sync. Easier to use, fewer shape options.
- **cp.async:** Asynchronous global-to-shared memory copy (Ampere+). Does not tie up registers.
- **Thread Block Clusters:** Cooperative groups of thread blocks that can access each other's shared memory (DSMEM). Inherited from Hopper. See section below.
- **sm_120a:** Architecture-specific variant enabling sm_120-only compiler optimizations.

### Thread Block Clusters

RTX 5090 supports Thread Block Clusters (confirmed via `cudaDevAttrClusterLaunch`). A cluster is a group of thread blocks guaranteed to be co-scheduled and able to access each other's shared memory via Distributed Shared Memory (DSMEM).

**Launch configuration:**
```cpp
cudaLaunchConfig_t config = {};
config.gridDim = grid;
config.blockDim = block;
cudaLaunchAttribute attrs[1];
attrs[0].id = cudaLaunchAttributeClusterDimension;
attrs[0].val.clusterDim = {2, 1, 1};  // 2-block cluster
config.numAttrs = 1;
config.attrs = attrs;
cudaLaunchKernelEx(&config, kernel, args...);
```

**DSMEM access:** Within a cluster, any block can read/write another block's shared memory using `cluster.map_shared_rank()`. Access patterns should be coalesced and aligned to 32-byte segments (same rules as global memory).

**When to use:** Clusters benefit kernels where neighboring blocks share input data (e.g., halo exchange in stencil computations, tiled convolutions). The DSMEM bandwidth adds to L2 bandwidth rather than replacing it.

**Profiling note:** Cluster-related NCU metrics include cluster scheduling overhead and DSMEM traffic. If cluster blocks are poorly co-located, scheduling overhead can negate the DSMEM benefit.

---

## Memory Hierarchy

### GDDR7 @ ~1.8 TB/s

The RTX 5090 uses GDDR7 memory at 28 Gbps per pin over a 512-bit bus, yielding a theoretical peak bandwidth of ~1,792 GB/s. Effective sustained bandwidth under typical profiling is 85–90% of peak (~1,520–1,610 GB/s).

This is **4.4× lower** than data-center Blackwell's 8 TB/s. Kernels that are memory-bandwidth-bound on data-center GPUs are even more severely bandwidth-bound on RTX 5090. Single-token LLM decode — already bandwidth-bound on data-center GPUs — is _deeply_ bandwidth-bound here.

**Key implication:** On RTX 5090, the roofline breakpoint (the arithmetic intensity where a kernel transitions from memory-bound to compute-bound) is 4.4× lower than data-center Blackwell for the same precision. Many kernels that are compute-bound on high-bandwidth data-center GPUs become memory-bound on RTX 5090.

### L2 Cache — 96 MB

The RTX 5090 has 96 MB of L2 cache, with up to 60 MB available for persistent L2 (`cudaDeviceProp.persistingL2CacheMaxSize`). Use `cudaCtxSetLimit(cudaLimitPersistingL2CacheSize, bytes)` and stream-level `cudaAccessPolicyWindow` to pin hot data (e.g., KV-cache, frequently reused weight tiles) in L2.

### Shared Memory — 100 KB/SM

| Configuration | Size |
|---|---|
| Default per block | 48 KB |
| Opt-in max per block | 99 KB (via `cudaFuncSetAttribute`) |
| Per SM total | 100 KB |
| Runtime reserved per block | 1 KB |

To request more than 48 KB of dynamic shared memory per block:
```cpp
cudaFuncSetAttribute(kernel, cudaFuncAttributeMaxDynamicSharedMemorySize, 101376);
kernel<<<grid, block, 101376>>>();
```

The maximum requestable is 101,376 bytes (99 KB). Requesting 102,400 (full 100 KB) fails because the runtime reserves 1 KB per block.

**Occupancy trade-off:** A block using 99 KB of shared memory can only have one block per SM (since 2 × 99 KB > 100 KB). This limits occupancy to `min(48, block_warps)` warps out of 48 maximum. For memory-latency-bound kernels, the reduced occupancy may hurt performance more than the larger shared memory helps.

---

## Tensor Core Programming

### Available ISA: mma.sync

On sm_120, Tensor Core operations use the `mma.sync` PTX instruction — the same warp-cooperative MMA interface available since Ampere (sm_80). A warp of 32 threads collectively performs a matrix multiply-accumulate on fragments distributed across the warp's registers.

Supported shapes and types (non-exhaustive):

| Shape (MxNxK) | A Type | B Type | C/D Type |
|---|---|---|---|
| m16n8k16 | f16/bf16 | f16/bf16 | f32 |
| m16n8k16 | tf32 | tf32 | f32 |
| m16n8k32 | e4m3/e5m2 | e4m3/e5m2 | f32 |
| m16n8k32 | s8 | s8 | s32 |
| m16n8k16 | f16/bf16 | f16/bf16 | f16 |

### WMMA API

For simpler use cases, the WMMA C++ API wraps `mma.sync` behind `nvcuda::wmma::fragment` and `wmma::mma_sync()`:

```cpp
#include <mma.h>
using namespace nvcuda;

wmma::fragment<wmma::matrix_a, 16, 16, 16, __half, wmma::row_major> a;
wmma::fragment<wmma::matrix_b, 16, 16, 16, __half, wmma::col_major> b;
wmma::fragment<wmma::accumulator, 16, 16, 16, float> c;
wmma::fill_fragment(c, 0.0f);
wmma::mma_sync(c, a, b, c);
```

### Recommended Development Path

For production GEMM/MMA workloads, use **cuBLAS** or **CUTLASS 3.x/4.x** rather than hand-writing `mma.sync` PTX. These libraries:
- Automatically select optimal tile sizes, pipeline depths, and register allocation for sm_120
- Handle FP4 operations internally (FP4 is not accessible via user-written PTX on sm_120)
- Provide pre-tuned kernels for common shapes

Hand-written `mma.sync` is appropriate for custom fused kernels where library routines don't fit (e.g., fused attention + residual + RMSNorm).

### Why tcgen05 and wgmma Are Absent

NVIDIA's Blackwell architecture documentation describes `tcgen05` as the 5th-generation Tensor Core instruction set. However, tcgen05 is exclusive to data-center Blackwell. Attempting to compile tcgen05 PTX for sm_120 produces:

```
ptxas error: Instruction 'tcgen05.alloc' not supported on .target 'sm_120'
```

Similarly, Hopper's `wgmma` (warpgroup MMA) is not available on sm_120. The consumer Blackwell Tensor Cores provide their throughput gains through wider execution units exposed through the existing `mma.sync` interface, not through a new ISA.

**For profiling:** when analyzing cuBLAS/CUTLASS-generated SASS on RTX 5090, you will see `HMMA` (half-precision MMA) and `IMMA` (integer MMA) instructions — the SASS encodings of `mma.sync`. You will NOT see tcgen05 or wgmma opcodes.

---

## Precision Spectrum & Roofline

### Throughput and Roofline Breakpoints

The roofline breakpoint is the arithmetic intensity (FLOPs/byte) at which a kernel transitions from memory-bandwidth-bound to compute-bound. Below the breakpoint: optimize for memory. Above: optimize for compute.

All breakpoints use the RTX 5090 theoretical peak bandwidth of 1,792 GB/s.

| Precision | Peak Throughput | Breakpoint (Dense) | Breakpoint (Sparse 2:4) | PTX mma.sync on sm_120 |
|---|---|---|---|---|
| FP64 (CUDA cores) | 1.64 TFLOPS | 0.9 FLOPs/byte | — | N/A (CUDA cores) |
| FP32 (CUDA cores) | 104.8 TFLOPS | 58.5 FLOPs/byte | — | N/A (CUDA cores) |
| TF32 (Tensor) | 104.75 TFLOPS | 58.5 FLOPs/byte | 116.9 | Yes |
| BF16/FP16 (Tensor) | 209.51 TFLOPS | 116.9 FLOPs/byte | 233.8 | Yes |
| FP8 (Tensor) | 419.01 TFLOPS | 233.8 FLOPs/byte | 467.6 | Yes |
| INT8 (Tensor) | 838 TOPS | 467.6 OPs/byte | 935.3 | Yes |
| FP4 (Tensor) | ~1,676 TOPS | 935.3 OPs/byte | 1,870.5 | **No** (library-only) |

### FP4 on sm_120: Library-Only

The RTX 5090 hardware supports FP4 operations (NVIDIA markets 3,352 TOPS sparse), but the `mma.sync` PTX ISA on sm_120 does not expose FP4 types. Attempting FP4 mma.sync produces:

```
ptxas error: Instruction 'mma with FP6/FP4 floating point type' not supported on .target 'sm_120'
```

FP4 is accessible only through cuBLAS and CUTLASS 4.x, which use internal architecture-specific code paths. When profiling cuBLAS FP4 kernels on RTX 5090, you will observe Tensor Core utilization, but you cannot replicate the behavior with inline PTX.

### Practical Guidance

- **LLM inference (decode):** Arithmetic intensity is ~2 FLOPs/byte for a GEMV — well below every breakpoint. Decode is always memory-bandwidth-bound on RTX 5090. Optimize for memory access, not compute.
- **LLM inference (prefill / large batch):** GEMM arithmetic intensity scales with batch size. BF16 GEMM with large batches can become compute-bound (above the 116.9 FLOPs/byte breakpoint).
- **General GEMM:** Most GEMM configurations are compute-bound above the breakpoint. Ensure Tensor Core utilization > 50%.
- **Element-wise / reduction:** Always memory-bound. Optimize for coalescing and vectorized access.

---

## LLM Inference Profiling

This section covers profiling LLM inference kernels on RTX 5090, focused on the **single-user, low-latency autoregressive decode** scenario.

### Why Decode is Deeply Memory-Bandwidth-Bound

In autoregressive decode, each token generation performs a GEMV (matrix-vector multiply) against the model weights. The arithmetic intensity is approximately:

```
AI_decode ≈ 2 × K / (K × bytes_per_param) = 2 / bytes_per_param
```

| Weight Precision | bytes/param | Arithmetic Intensity | BF16 Breakpoint | Status |
|---|---|---|---|---|
| FP16/BF16 | 2 | 1.0 FLOPs/byte | 116.9 | **117× below breakpoint** |
| FP8 | 1 | 2.0 FLOPs/byte | 233.8 | **117× below breakpoint** |
| INT4 | 0.5 | 4.0 FLOPs/byte | 116.9 | **29× below breakpoint** |
| FP4 | 0.5 | 4.0 FLOPs/byte | 935.3 | **234× below breakpoint** |

Decode on RTX 5090 is memory-bandwidth-bound by a factor of 30–230× depending on precision. No amount of Tensor Core optimization changes this — the bottleneck is getting data from GDDR7 to the SMs.

**Decode throughput ceiling (theoretical):**
```
tokens/s ≈ bandwidth / bytes_per_token
         = 1,792 GB/s / (model_params × bytes_per_param)
```

| Model | FP16 | FP8 | INT4 |
|---|---|---|---|
| 7B | ~128 tok/s | ~256 tok/s | ~512 tok/s |
| 13B | ~69 tok/s | ~138 tok/s | ~276 tok/s |
| 70B | Doesn't fit | Doesn't fit | ~51 tok/s |

These are theoretical peaks assuming 100% bandwidth utilization and model weights fitting in VRAM. Real throughput is typically 60–80% of these values.

### KV-Cache Memory Budget

KV-cache memory per token:
```
KV_bytes_per_token = 2 × num_layers × num_kv_heads × head_dim × bytes_per_element
```

The factor of 2 accounts for both K and V tensors.

| Model Config | Layers | KV Heads | Head Dim | FP16 (2B) | FP8 (1B) |
|---|---|---|---|---|---|
| Llama 3 8B (GQA) | 32 | 8 | 128 | 128 KB/tok | 64 KB/tok |
| Llama 3 70B (GQA) | 80 | 8 | 128 | 320 KB/tok | 160 KB/tok |
| Mistral 7B (GQA) | 32 | 8 | 128 | 128 KB/tok | 64 KB/tok |

**32 GB VRAM budget example (Llama 3 8B, INT4 weights, FP16 KV):**
- Model weights: ~4 GB
- KV-cache at 128K context: 128 KB × 131,072 = 16 GB
- Activations + overhead: ~2 GB
- Total: ~22 GB — fits in 32 GB
- Maximum context with INT4 weights + FP16 KV: ~200K tokens before VRAM exhaustion

**32 GB VRAM budget example (Llama 3 8B, FP8 weights, FP8 KV):**
- Model weights: ~8 GB
- KV-cache at 128K context: 64 KB × 131,072 = 8 GB
- Total: ~18 GB — fits comfortably

### Quantization Impact on Decode

Lower precision reduces memory traffic proportionally, directly increasing decode throughput:

| Precision | Bytes/Param | Relative Bandwidth | Theoretical Speedup vs FP16 |
|---|---|---|---|
| FP16/BF16 | 2.0 | 1.0× | Baseline |
| FP8 | 1.0 | 0.5× | ~2.0× |
| INT4 / FP4 | 0.5 | 0.25× | ~4.0× |

Caveats:
- Dequantization overhead (especially for block-scaled formats like NVFP4) reduces the theoretical speedup by 5–15%.
- INT4/FP4 weight quantization may degrade model quality. Per-layer sensitivity analysis is recommended.
- FP4 on RTX 5090 requires cuBLAS/CUTLASS (no PTX path).

### ncu Signals for Decode Bottleneck Diagnosis

| Signal | Indicates |
|---|---|
| `dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed` > 70% | DRAM bandwidth-saturated — this is expected for decode |
| `dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed` < 30% | NOT bandwidth-saturated — investigate L2 hit rate, coalescing, or launch config |
| `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed` < 5% | Tensor Cores nearly idle — expected for decode (GEMV doesn't generate enough work) |
| `long_scoreboard` stalls dominant | Waiting for memory — normal for decode; reducing memory traffic (quantization) is the fix |
| High `l2_tex_hit_rate` on weights | Weights partially cached in L2 — potential for persistent L2 optimization |
| PM Sampling shows flat low utilization | Low parallelism (few blocks active) — consider split-K or persistent kernel approaches |

### Precision-Specific Profiling Recipes

When comparing kernel performance across precisions, use the same input data and grid configuration where possible. Profile each precision separately and compare the metrics below.

#### Profiling BF16/FP16 Kernels

**When to use:** Baseline precision for LLM inference. Use BF16 for training-compatible weights, FP16 for inference-only deployments.
**Tensor Core pipe:** `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed`
**RTX 5090 peak:** 209.5 TFLOPS dense (BF16), 419 TFLOPS with 2:4 sparsity.

```bash
ncu --set full \
    --section InstructionStats --section SourceCounters \
    -k "regex:YOUR_KERNEL" -c 1 \
    -o $PROFILE_RUN_DIR/reports/bf16_<tag> \
    ./your_binary [args]
```

**Key metrics:**
- `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed` — tensor core utilization. >50% is good for compute-bound GEMM; near-zero is expected for decode GEMV.
- `dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed` — DRAM bandwidth utilization vs 1.792 TB/s peak.
- `sm__sass_inst_executed_op_fp16.sum` + `sm__sass_inst_executed_op_bf16.sum` — confirms the kernel is actually using FP16/BF16 instructions (not FP32 fallback).

#### Profiling FP8 Kernels (E4M3 / E5M2)

**When to use:** Primary inference precision. E4M3 for forward pass, E5M2 for gradients (rarely used in inference). Most LLM frameworks default to E4M3 for weight quantization.
**Tensor Core pipe:** Same `sm__pipe_tensor_cycles_active` metric — FP8 uses the same tensor pipe, at 2× throughput vs BF16.
**RTX 5090 peak:** 419 TFLOPS dense (FP8), 838 TFLOPS with 2:4 sparsity.

```bash
ncu --set full \
    --section InstructionStats --section SourceCounters \
    -k "regex:YOUR_KERNEL" -c 1 \
    -o $PROFILE_RUN_DIR/reports/fp8_<tag> \
    ./your_binary [args --precision fp8]
```

**Key metrics:**
- `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed` — should be roughly 2× the BF16 utilization for compute-bound kernels (same work, 2× throughput).
- `dram__bytes_op_read.sum` — should be roughly half of BF16 (1 byte/param vs 2).
- `sm__sass_inst_executed_op_fp8_e4m3.sum` or `sm__sass_inst_executed_op_fp8_e5m2.sum` — confirms FP8 instructions are executing (not FP16 fallback).

**Caveat:** If tensor core utilization is identical to BF16, the kernel may be silently upcasting to FP16. Check the instruction mix.

#### Profiling INT8 Kernels

**When to use:** Weight-only quantization (W8A16) or full INT8 (W8A8). Common in production inference for latency-sensitive deployments.
**Tensor Core pipe:** `sm__pipe_tensor_cycles_active` — INT8 uses a different sub-pipe but the same top-level metric.
**RTX 5090 peak:** 838 TOPS (INT8), 1,676 TOPS with 2:4 sparsity.

```bash
ncu --set full \
    --section InstructionStats --section SourceCounters \
    -k "regex:YOUR_KERNEL" -c 1 \
    -o $PROFILE_RUN_DIR/reports/int8_<tag> \
    ./your_binary [args --precision int8]
```

**Key metrics:**
- `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed` — should show improvement over BF16 for compute-bound kernels.
- `dram__bytes_op_read.sum` — 1 byte/param (same as FP8). For W8A16, activations are still 2 bytes.
- `sm__sass_inst_executed_op_integer.sum` — check for INT8-specific instructions.

**W8A16 vs W8A8:** In W8A16, weights are INT8 but activations are FP16. The GEMM still runs in FP16 tensor mode with on-the-fly dequantization — the bandwidth win is real but the compute win is limited to dequant overhead savings.

#### Profiling FP4 / NVFP4 Kernels

**When to use:** Maximum throughput quantization. NVFP4 uses dual-level block scaling (per-block scale + per-tensor scale) to maintain accuracy. Available on RTX 5090 tensor cores but **library-only** — no direct PTX path on sm_120.
**Tensor Core pipe:** Same `sm__pipe_tensor_cycles_active` metric.
**RTX 5090 peak:** ~1,676 TOPS dense, 3,352 TOPS with 2:4 sparsity (theoretical).

```bash
ncu --set full \
    --section InstructionStats --section SourceCounters \
    -k "regex:YOUR_KERNEL" -c 1 \
    -o $PROFILE_RUN_DIR/reports/fp4_<tag> \
    ./your_binary [args --precision fp4]
```

**Key metrics:**
- `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed` — theoretical 4× improvement over BF16 for compute-bound, though real gains depend on dequantization overhead.
- `dram__bytes_op_read.sum` — 0.5 bytes/param plus scaling metadata. Should be roughly 4× less than BF16.
- Instruction mix — FP4 operations run through library calls (cuBLAS/CUTLASS), not direct HMMA instructions. The instruction profile will show the library's internal kernel patterns.

**Framework support:** TensorRT-LLM supports NVFP4 quantization. vLLM has partial support. Many frameworks silently fall back to FP8 — always verify with the instruction mix metrics that FP4 is actually in use.

#### Cross-Precision Comparison

To compare the same kernel across precisions, collect one report per precision with identical inputs and report the following side by side:

| Metric | BF16 | FP8 | INT8 | FP4 |
|---|---|---|---|---|
| `gpu__time_duration.sum` (ns) | | | | |
| `dram__bytes_op_read.sum` (bytes) | | | | |
| `dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed` | | | | |
| `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed` | | | | |
| `sm__throughput.avg.pct_of_peak_sustained_elapsed` | | | | |

**What to look for:**
- **Decode (memory-bound):** Duration should scale roughly with bandwidth savings: FP8 ≈ 2× faster, FP4 ≈ 4× faster than BF16. If not, check for dequantization overhead or launch config issues.
- **GEMM (compute-bound):** Tensor core utilization should remain similar or increase. Duration scales with throughput: FP8 ≈ 2× faster, INT8 ≈ 4× faster than BF16.
- **Silent fallback:** If FP8/FP4 shows identical duration to BF16, the framework likely fell back to a higher precision. Check the instruction stats section.

---

## Why This Document Exists

As an AI assistant, I have a systematic weakness in GPU kernel development: **I know many GPU programming principles but often forget to apply them when writing code.** I might produce a functionally correct but poorly performing kernel, only recognizing the violated principle after the user points it out.

This document serves three purposes:

1. **Pre-coding checklist** — systematically review guidelines before writing a kernel, not after.
2. **NCU metric correlation** — link each guideline to specific profiling signals, enabling rapid diagnosis from profile data.
3. **Exception marking** — flag legitimate exceptions (LLM decode, reductions, communication kernels) where violating a guideline is correct behavior.

**How to use:**
- **Before writing a kernel:** Read the Architecture Overview to check for applicable hardware features, then review the Pre-Coding Checklist.
- **When optimizing:** Match abnormal NCU metrics to guidelines in the overview table below, then read the detailed guideline.
- **When reviewing:** Check each guideline against the kernel — distinguish real performance problems from inherent kernel characteristics.

---

## Guideline Overview

| # | Guideline | Key NCU Metric | Common Exception |
|---|---|---|---|
| 1 | Ensure sufficient parallelism | Occupancy, wave count | Decode attention (batch=1, seq=1) |
| 2 | Coalesce memory accesses | sectors/request, L1 hit rate | Sparse matrix, AoS layout |
| 3 | Use shared memory to reduce global access | L1/L2 hit rate, DRAM throughput | Element-wise kernel (no data reuse) |
| 4 | Avoid bank conflicts | shared memory wavefronts | Kernel without shared memory |
| 5 | Avoid warp divergence | branch efficiency, predicated inst | Tree-based reduction |
| 6 | Control register pressure | register spill, occupancy | Large fused kernel |
| 7 | Hide memory latency (ILP/TLP) | long_scoreboard stalls | Strictly sequential dependency |
| 8 | Use appropriate math precision | FP32/FP64 pipe util | Scientific computing requiring FP64 |
| 9 | Minimize host-device synchronization | Kernel launch frequency | Debugging phase |
| 10 | Use Tensor Cores effectively | tensor pipe utilization | Non-matrix operations |
| 11 | Optimize grid/block configuration | tail effect, occupancy | Dynamic shape with small input |
| 12 | Reduce atomic contention | long_scoreboard on atomics | Histogram, allreduce |
| 13 | Vectorize memory access | sectors/request, LSU util | Non-aligned access |
| 14 | Use read-only cache path | LDG vs LD ratio | Read-write data |
| 15 | Pipeline compute and memory | SM util timeline | Compute-bound kernel |
| 16 | Reduce synchronization overhead | barrier stalls | Algorithms requiring global sync |

---

## Guideline Details

### Guideline 1: Ensure Sufficient Parallelism (Occupancy & Wave Count)

**Principle:** GPUs hide memory latency through massive thread parallelism. A kernel must launch enough thread blocks to fill all SMs, with enough active warps per SM to switch execution when one warp stalls.

**Quantitative targets:**
- Occupancy ≥ 50% (higher is better for memory-bound kernels)
- Wave count ≥ 2 (fills all 170 SMs at least twice, avoiding tail effect)
- Active warps per SM ≥ 12 (empirical minimum for effective latency hiding)

**NCU diagnosis:**
- `sm__warps_active.avg.pct_of_peak_sustained_active` < 50% → insufficient parallelism
- `launch__occupancy_limit_*` series → identifies whether registers, shared memory, or block size limits occupancy
- PM Sampling timeline shows utilization drop at end → wave count too low; last wave can't fill all 170 SMs

**Fixes:**
- Increase grid size (more blocks)
- Decrease block size to reduce per-block resource usage (but not below 128 threads)
- Reduce per-thread register count (`__launch_bounds__`)
- Reduce per-block shared memory usage

**Exceptions:**
- **LLM decode attention (batch=1):** The query has one token — total compute is tiny. No grid config can fill all 170 SMs. Correct optimization: split-K along the KV sequence dimension, or persistent kernel processing multiple attention heads.
- **Reduction final stages:** Each stage halves parallelism. Fuse the final stages into one warp using `__shfl_down_sync`.
- **Tail-processing kernels:** Handling unaligned tensor tails naturally produces small grids. Merge into the main kernel with masking.

---

### Guideline 2: Coalesce Memory Accesses

**Principle:** When a warp of 32 threads accesses global memory, the hardware coalesces requests into 128-byte cache line transactions. If 32 threads access 32 scattered addresses, up to 32 separate transactions are issued instead of the ideal 1.

**Quantitative targets:**
- `l1tex__average_t_sectors_per_request_pipe_lsu_mem_global_op_ld.ratio` ≈ 4 (ideal: 128B / 32B-sector = 4 sectors for a fully coalesced request)
- Far above 4 (e.g., 16 or 32) indicates severe non-coalescing

**NCU diagnosis:**
- sectors/request far above 4 → non-coalesced access
- `l1tex__t_sector_hit_rate.pct` very low → cache cannot buffer scattered accesses
- Memory Workload Analysis rules report "uncoalesced" warnings
- `dram__throughput` high but effective compute throughput low → bandwidth wasted on useless data

**Fixes:**
- **AoS → SoA:** Convert array-of-structures to structure-of-arrays for contiguous field access
- **Thread-to-data mapping:** Ensure `threadIdx.x` corresponds to the innermost (contiguous) dimension
- **Shared memory transpose:** Load coalesced into shared memory, then access in arbitrary order
- **Padding alignment:** Align each row's start address to 128 bytes

**Exceptions:**
- **Sparse matrix operations (SpMV, SpMM):** Non-zero elements are inherently non-contiguous. Optimize by choosing better sparse formats (ELL, blocked CSR) or using texture cache.
- **Tree/graph traversal:** Pointer-chasing access is inherently non-coalesced. Optimize with BFS-style traversal + sorting for locality.
- **Gather/scatter:** Index-driven indirect access. Consider sorting indices before accessing.

---

### Guideline 3: Use Shared Memory to Reduce Global Access

**Principle:** Shared memory is on-chip storage with ~10–20× the bandwidth and ~10–30× lower latency than global memory. When multiple threads need the same or adjacent data, load it from global memory to shared memory once, then read from shared memory repeatedly.

**Quantitative targets:**
- Use shared memory when data reuse > 1 (same data read by multiple threads or iterations)
- `dram__throughput.avg.pct_of_peak_sustained_elapsed` near peak with low `sm__throughput` → memory-bound, reduce DRAM access

**NCU diagnosis:**
- `dram__throughput` high + `sm__throughput` low → kernel is bandwidth-limited
- `l1tex__t_sector_hit_rate.pct` low → data not being reused/cached effectively
- `smsp__inst_executed_op_shared_ld.sum` = 0 with high `global_ld` → shared memory not used at all
- `long_scoreboard` stalls dominate → waiting for global memory

**Fixes:**
- **Tiling:** Partition input into tiles that fit in shared memory (classic GEMM tiling)
- **Prefetch / double buffering:** Load next tile while computing current tile
- **Shared scalars:** Load broadcast values into shared memory or `__constant__` memory

**Exceptions:**
- **Element-wise kernels (ReLU, Add, Scale, Cast):** Each element accessed once — no reuse. Shared memory adds latency without benefit. Optimize via kernel fusion and vectorized loads.
- **Large working set:** If each block needs more than 99 KB (opt-in max), data cannot fit entirely. Use multi-stage tiling.
- **Occupancy-constrained kernels:** More shared memory per block → fewer blocks per SM → lower occupancy. Balance shared memory utilization against occupancy.

---

### Guideline 4: Avoid Shared Memory Bank Conflicts

**Principle:** Shared memory is organized as 32 banks, with consecutive 4-byte words mapped to consecutive banks. If multiple threads in the same warp access different addresses in the same bank, those accesses are serialized (bank conflict). An N-way conflict makes that access N× slower.

**Quantitative targets:**
- `l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum` / access count → wavefronts per request, ideally 1 (no conflict)

**NCU diagnosis:**
- Shared memory wavefronts per request > 1 → bank conflicts present
- Memory Workload Analysis shared memory section shows high wavefront count
- `stall_barrier` or `stall_short_scoreboard` high with significant shared memory usage → possible bank conflict latency

**Fixes:**
- **Padding:** Add 1 padding element per row: `__shared__ float tile[32][33];` (33 instead of 32)
- **Swizzle pattern:** XOR-transform indices to scatter bank mapping
- **Layout adjustment:** Ensure threads in the same warp access different banks

**Exceptions:**
- **Broadcast access:** All threads reading the same shared memory address triggers hardware broadcast, not conflict.
- **Kernels without shared memory:** Guideline does not apply.
- **Low shared memory access frequency:** If shared memory is accessed only at kernel start/end, conflict impact is negligible.

---

### Guideline 5: Avoid Warp Divergence

**Principle:** A warp of 32 threads executes instructions in lockstep. When threads within a warp take different branches, the hardware executes each path sequentially (using predication), with non-active threads waiting. Severe divergence reduces SIMT efficiency to 1/32.

**Quantitative targets:**
- Branch efficiency (active thread ratio) ≥ 90%
- `smsp__thread_inst_executed_per_inst_executed.ratio` close to 32 → nearly all threads active

**NCU diagnosis:**
- `smsp__thread_inst_executed_per_inst_executed.ratio` far below 32 → few active threads per instruction
- Source view shows high "predicated-off thread %" on branch instructions
- `sm__inst_executed` vs `sm__inst_issued`: issued >> executed → many predicated instructions

**Fixes:**
- **Data reordering:** Sort so adjacent threads take the same branch
- **Branchless computation:** `cond * valueA + (1-cond) * valueB` instead of if-else
- **Warp-granularity branching:** Make branch decisions per-warp (every 32 elements), not per-thread

**Exceptions:**
- **Tree-based reduction (final stages):** Active thread count halves each stage. Only 5 stages total (32→1); use `__shfl_down_sync()`.
- **Boundary/mask handling:** Edge threads masked out at tensor boundaries. Usually affects only the last few warps.
- **Dynamic-shape kernels:** Variable-length sequences in NLP. Mitigate with padding + packing.

---

### Guideline 6: Control Register Pressure

**Principle:** Each SM has 65,536 32-bit registers. More registers per thread → fewer concurrent warps (lower occupancy). When registers run out, the compiler spills to local memory (backed by DRAM), causing extreme latency.

**Quantitative targets:**
- `launch__registers_per_thread` ≤ 128 (128 regs × 384 threads = 49,152 < 65,536; allows 48/48 warps = 100% occupancy with 3 blocks of 128 threads)
- `smsp__inst_executed_op_local_ld.sum` = 0 and `local_st` = 0 → no spill
- Small amounts of spill cached in L1 may have minimal impact

**NCU diagnosis:**
- `local_ld/local_st` > 0 → register spill occurring
- `launch__registers_per_thread` high + `sm__warps_active` low → registers limiting occupancy
- `launch__occupancy_limit_registers` is the binding occupancy limiter
- `l1tex__t_sectors_pipe_lsu_mem_local_op_ld.sum` large → heavy local memory traffic

**Fixes:**
- **`__launch_bounds__(maxThreadsPerBlock, minBlocksPerMultiprocessor)`:** Tell the compiler to target specific occupancy
- **Split large kernels:** An overly complex fused kernel may benefit from splitting
- **Recompute instead of store:** Trade compute for fewer intermediate variables
- **Shared memory for arrays:** Thread-private array data can move to shared memory

**Exceptions:**
- **Large fused kernels (FlashAttention):** Fusion eliminates global memory round-trips. The register-pressure cost is usually worth the memory savings. Accept lower occupancy if there's no significant spill.
- **Compute-bound kernels:** If SM throughput is near 100%, low occupancy isn't a problem — there's no latency to hide.
- **CUTLASS-level hand-tuned kernels:** Register allocation is intentional. Don't blindly adjust.

**sm_120 MMA register pressure warning:** On data-center Blackwell, TMEM offloads MMA accumulators from registers, effectively increasing available register budget for GEMM kernels. On RTX 5090, accumulators reside in registers (mma.sync stores results in register fragments). This makes register pressure _significantly_ worse for MMA-heavy kernels — a GEMM kernel ported from data-center Blackwell may spill registers or lose occupancy on RTX 5090. Monitor `launch__registers_per_thread` aggressively when hand-tuning mma.sync kernels.

---

### Guideline 7: Hide Memory Latency (ILP and TLP)

**Principle:** Global memory latency is 200–800 cycles. GPUs hide it through Thread-Level Parallelism (TLP: multiple warps interleave execution) and Instruction-Level Parallelism (ILP: multiple independent instructions in-flight per thread). A serial load→wait→compute→load pattern leaves the pipeline empty.

**Quantitative targets:**
- `long_scoreboard` stalls should not dominate
- `sm__inst_executed.avg.per_cycle_active` (IPC) should approach theoretical value
- Scheduler eligible warps should not be persistently 0

**NCU diagnosis:**
- `smsp__pcsamp_warps_issue_stalled_long_scoreboard` > 40% → heavy memory wait
- `smsp__warps_eligible.avg.per_cycle_active` near 0 → no warp ready to issue
- SchedulerStats "no eligible" ratio high → all warps stalled
- Source view shows stalls concentrated on first instruction after a load

**Fixes:**
- **Software pipelining / double buffering:** Prefetch next tile while computing current
- **Increase per-thread work:** Each thread issues multiple loads simultaneously
- **`cp.async` (CUDA 11+):** Async global→shared copy without tying up registers
- **Increase occupancy:** More active warps = more TLP (constrained by Guideline 6)

**Exceptions:**
- **Sequential dependency algorithms:** Serial scan, prefix sum serial phase — next step depends on previous result. Optimize at the algorithm level (Blelloch scan).
- **Pointer-chasing:** Linked list, tree query — next address depends on current load result. GPUs are inherently weak here.

---

### Guideline 8: Use Appropriate Math Precision

**Principle:** FP64 throughput is 1/64 of FP32 on RTX 5090 (~1.64 TFLOPS vs 104.8 TFLOPS). Transcendental functions (sin, cos, exp) are 10× slower than their native approximations (__sinf, __cosf, __expf). Use the lowest precision that meets accuracy requirements.

**Quantitative targets:**
- Confirm precision matches requirements: FP16/BF16 for inference, FP32 for accumulation, FP64 only when necessary
- `sm__pipe_fp64_cycles_active` should be near 0 unless FP64 is intentional

**NCU diagnosis:**
- InstructionStats showing high FP64 instruction ratio → check for accidental double-precision (common: `1.0` instead of `1.0f`)
- SFU utilization high → heavy transcendental use; consider approximate versions
- ComputeWorkloadAnalysis showing one pipeline bottlenecked

**Fixes:**
- **Add `f` suffix to all float literals:** `1.0f` not `1.0`, `0.5f` not `0.5`
- **Use fast math intrinsics:** `__fdividef(x, y)`, `__expf()`, `__logf()`
- **Mixed precision:** FP16 compute + FP32 accumulation (native Tensor Core mode)
- **`--use_fast_math` compiler flag:** Auto-replaces standard math with fast versions (sacrifices precision and special-value handling)

**Exceptions:**
- **Scientific/financial computing:** FP64 may be mandatory. Optimize algorithm, not precision.
- **Numerical stability critical paths:** softmax log-sum-exp must accumulate in FP32 even with FP16 inputs.

---

### Guideline 9: Minimize Host-Device Synchronization

**Principle:** Each `cudaDeviceSynchronize()` or implicit sync (e.g., `cudaMemcpy` D2H) stalls the CPU until the GPU finishes all work, creating pipeline bubbles. GPU compute capacity is wasted during sync waits.

**Quantitative targets:**
- This is not a single-kernel issue — use Nsight Systems (nsys) to check timeline gaps.
- Multiple very short kernels (< 10 μs) with CPU gaps between them → excessive sync.

**NCU-related diagnosis:**
- `gpu__time_duration.sum` very small but user reports high end-to-end latency → inter-kernel CPU sync overhead
- Very short kernel duration → sync overhead dominates

**Fixes:**
- **CUDA Streams:** Submit kernels and memcpy to streams for async execution
- **`cudaMemcpyAsync`** instead of `cudaMemcpy`
- **CUDA Events:** Sync specific streams instead of all GPU work
- **CUDA Graphs:** Record a sequence of operations and replay with minimal launch overhead
- **Pinned memory (`cudaMallocHost`):** Required for truly async memcpy

**Exceptions:**
- **Debugging:** Synchronization simplifies error isolation. Remove for production.
- **Control-flow-dependent launches:** CPU needs GPU results for next decision. Consider device-side launch (Dynamic Parallelism) or conditional graph nodes.

---

### Guideline 10: Use Tensor Cores Effectively

**Principle:** RTX 5090 Tensor Cores provide up to 209.5 TFLOPS (BF16 dense) — 2× the CUDA core FP32 rate. Matrix-multiply kernels should use the Tensor Core path (mma.sync/WMMA/cuBLAS) rather than CUDA core FMA.

**Quantitative targets:**
- For GEMM kernels: `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed` > 50%
- FP16/BF16 GEMM with tensor pipe = 0% → not using Tensor Cores at all

**NCU diagnosis:**
- `sm__inst_executed_pipe_tensor.sum` = 0 → no Tensor Core instructions
- Tensor pipe utilization low + DRAM throughput high → Tensor Cores starved for data
- InstructionStats showing FFMA (FP32 FMA) instead of HMMA → fell back to CUDA core path

**Fixes:**
- **Use cuBLAS / CUTLASS / cuDNN:** Pre-optimized for Tensor Cores on sm_120
- **Align matrix dimensions:** M, N, K aligned to 16 (FP16) or 8 (TF32)
- **Correct data layout:** Tensor Cores require specific layouts (column-major or interleaved)
- **WMMA API or PTX mma.sync:** For hand-written kernels

**Exceptions:**
- **Non-matrix operations:** Element-wise, reduction, sort — cannot use Tensor Cores.
- **Small matrices:** When M, N, K are very small, Tensor Core tiles cannot be fully utilized.
- **Precision mismatch:** Tensor Cores support specific combinations. FP64 Tensor Core throughput is extremely limited on RTX 5090.

---

### Guideline 11: Optimize Grid/Block Configuration

**Principle:** Block size affects occupancy, warp count, and shared memory allocation granularity. Grid size determines total parallelism and SM fill rate. Poor configuration leads to uneven SM utilization (partial waves) or reduced occupancy.

**Quantitative targets:**
- Block size: multiple of 32 (warp-aligned); 128 or 256 is a good starting point
- Grid size: multiple of `blocks_per_sm × 170` to avoid partial waves
- Total threads ≥ 170 SMs × 1,536 threads/SM × 2 = 522,240

**NCU diagnosis:**
- PM Sampling tail occupying > 20% of total runtime → grid size not a multiple of wave size
- `sm__warps_active.avg.pct_of_peak_sustained_active` low without resource limits → grid too small
- LaunchStats block size not a multiple of 32 → wasted threads in last warp

**Fixes:**
- **Block size 128 or 256:** Good occupancy-resource balance on most architectures
- **Round grid to wave multiple:** `wave_size = blocks_per_sm × 170`
- **Persistent kernel for small grids:** Each block loops over multiple work units
- **`cudaOccupancyMaxPotentialBlockSize()`:** Auto-compute optimal block size

**Exceptions:**
- **Dynamic shapes:** Input size unknown at compile time. Use persistent kernel + work-stealing.
- **Fixed-function kernels (softmax over vocabulary):** Grid = batch_size. If batch is small, parallelize batch + sequence dimensions.

---

### Guideline 12: Reduce Atomic Contention

**Principle:** Atomic operations (atomicAdd, atomicCAS, etc.) on the same address are serialized. When many threads atomic to few addresses, contention severely degrades performance.

**Quantitative targets:**
- Atomic operations should not be a dominant stall source
- Distribute atomics across many addresses when possible

**NCU diagnosis:**
- `long_scoreboard` stalls concentrated on atomic instructions → contention
- `lts__t_sectors_op_atom.sum` or `lts__t_sectors_op_red.sum` very large → heavy L2 atomic traffic
- L2 throughput high but effective bandwidth low → atomic retries waste bandwidth

**Fixes:**
- **Hierarchical reduction:** Warp-level (`__shfl_down_sync`) → block-level (shared memory) → grid-level atomic. Reduces atomic count from N to gridDim.x.
- **Per-block local buffers:** Write to per-block buffer, merge globally at the end.
- **CAS loop for unsupported types:** FP16 atomicAdd via `atomicCAS` loop.

**Exceptions:**
- **Histogram:** Inherently needs atomics. Use shared-memory histogram + single global merge pass. Maximize bin distribution across threads.
- **Communication kernels (NCCL AllReduce):** Cross-GPU sync requires atomics. NCCL is heavily optimized — don't manually modify.

---

### Guideline 13: Vectorize Memory Access

**Principle:** GPU load/store units can transfer 1/2/4/8/16 bytes per instruction. Using vector types (float2, float4, int4) loads more data per instruction, reducing total instruction count and LSU pressure.

**Quantitative targets:**
- Memory-bound kernels: vectorized loads can reduce load instruction count by 2–4×
- `sm__inst_executed_pipe_lsu.avg.pct_of_peak_sustained_elapsed` high → LSU is the bottleneck; vectorization helps

**NCU diagnosis:**
- LSU pipe utilization near peak → too many load/store instructions
- InstructionStats shows high LDG/STG instruction count
- Source view shows dense load instructions

**Fixes:**
- **Use `float4` / `int4` types:** `float4 val = *reinterpret_cast<float4*>(ptr + idx);`
- **Ensure alignment:** `float4` loads require 16-byte alignment
- **Handle tail elements:** Process remainder with scalar loads

**Exceptions:**
- **Non-aligned data:** Forced vector loads on non-aligned addresses cause undefined behavior or performance degradation.
- **Small tensors:** Vector loads may read past boundaries. Add bounds checking.
- **Compute-bound kernels:** If the bottleneck is compute, vectorization provides limited benefit.

---

### Guideline 14: Use Read-Only Cache Path

**Principle:** GPUs have a dedicated read-only data path (texture cache / `__ldg()` intrinsic / `const __restrict__`). Read-only data on this path avoids competing with read-write data for L1 cache capacity.

**Quantitative targets:**
- Ensure read-only inputs use `const __restrict__` pointer qualifiers
- The compiler usually auto-detects read-only access and uses LDG (texture path load)

**NCU diagnosis:**
- InstructionStats: LDG (read-only) vs LD (general load) ratio → more LDG is better
- `l1tex__t_sector_hit_rate.pct` low despite expected locality → read-only data may not be on the texture path

**Fixes:**
- **Pointer annotation:** `__global__ void kernel(const float* __restrict__ input, float* __restrict__ output)`
- **Explicit `__ldg(&ptr[idx])`:** Force read-only path
- **`__constant__` memory:** For small broadcast data (< 64 KB)

**Exceptions:**
- Modern compilers (CUDA 11+) usually optimize this automatically. Explicit `__ldg` is rarely needed except in complex pointer-aliasing scenarios.
- Read-write data cannot use the read-only path.

---

### Guideline 15: Pipeline Compute and Memory Access

**Principle:** High-performance kernels should split execution into stages (load → compute → store) and use double buffering or multi-stage pipelines to overlap stages on different data. While Tensor Cores compute the current tile, the LSU simultaneously loads the next tile.

**Quantitative targets:**
- PM Sampling timeline should be flat (no periodic oscillation)
- SM throughput and DRAM throughput should both stay high simultaneously

**NCU diagnosis:**
- PM Sampling shows sawtooth pattern (SM and DRAM throughput alternating) → compute and memory not overlapping
- `long_scoreboard` stalls high → compute waiting for data
- SM throughput timeline has periodic valleys → pipeline bubbles

**Fixes:**
- **Double buffering:** Alternate between two shared memory buffers:
  ```cpp
  load(smem_buf[0], global_ptr + 0);
  for (int i = 0; i < num_tiles - 1; i++) {
      load(smem_buf[(i+1)%2], global_ptr + (i+1)*tile_size);
      __syncthreads();
      compute(smem_buf[i%2]);
      __syncthreads();
  }
  compute(smem_buf[(num_tiles-1)%2]);
  ```
- **`cp.async` + commit/wait groups:** Async copy without register intermediates
- **Multi-stage pipeline (CUTLASS 3-stage/4-stage):** Deeper pipelines hide more latency but require more shared memory

**Exceptions:**
- **Compute-bound kernels:** If compute time >> memory time, single buffer suffices.
- **Very short kernels:** < 3 tiles makes pipeline overhead not worthwhile.
- **Large shared memory usage:** Double buffering doubles shared memory requirements. On RTX 5090 with 99 KB max, a double-buffered tile is limited to ~49 KB per buffer. This is significantly tighter than data-center Blackwell's 227 KB.

---

### Guideline 16: Reduce Synchronization Overhead

**Principle:** `__syncthreads()` forces all threads in a block to reach the barrier before continuing. Fast warps must wait for the slowest warp. Excessive synchronization points create bubbles. Grid-level sync (cooperative groups) is even more expensive.

**Quantitative targets:**
- `smsp__pcsamp_warps_issue_stalled_barrier` should not dominate
- Compute between sync points should be large enough to amortize the sync cost

**NCU diagnosis:**
- `barrier` stalls > 30% → sync wait time is too high
- Source view shows high stall sampling on `BAR.SYNC` instructions
- `barrier` + `warp_divergence` both high → divergence makes sync waits longer

**Fixes:**
- **Reduce `__syncthreads()` count:** Merge multiple sync-requiring phases
- **Warp-level primitives:** `__shfl_sync`, `__ballot_sync` don't need block barriers
- **Warp-specialized execution:** Different warps do different work (CUTLASS producer/consumer pattern)
- **`__syncwarp()` instead of `__syncthreads()`:** When only warp-level sync is needed

**Exceptions:**
- **Algorithms requiring global reduce/scan:** Block-to-block sync is unavoidable. Use cooperative groups grid-wide sync or split into multiple kernels.
- **Correctness requirements:** Never sacrifice correctness for performance. If removing a sync creates a race condition, the sync is mandatory.

---

## Special Kernel Types Quick Reference

### LLM Decode Attention (Single Token Generation)

| Inherently Violates | Reason | Alternative Optimization |
|---|---|---|
| Guideline 1 (low parallelism) | Query is 1 token, total compute is tiny | Split-K along KV seq_len; multi-query/GQA reduces head count |
| Guideline 11 (small grid) | batch_size × num_heads may not fill 170 SMs | Persistent kernel; merge multiple heads per block |
| Guideline 15 (no pipeline) | Data volume too small for multi-tile pipeline | Reduce kernel launch overhead; use CUDA Graphs |

On RTX 5090, decode attention is 4.4× more memory-bandwidth-bound than on data-center Blackwell (1.8 TB/s vs 8 TB/s). The primary optimization lever is reducing memory traffic: KV-cache quantization (FP8), GQA/MQA, and persistent L2 caching of hot KV-cache pages.

### Element-wise Kernel (ReLU, Add, Scale, Cast)

| Inherently Violates | Reason | Alternative Optimization |
|---|---|---|
| Guideline 3 (no shared memory) | Each element accessed once, no reuse | Normal — shared memory not needed |
| Guideline 10 (no Tensor Core) | Non-matrix operation | Normal — not applicable |

Optimize via: kernel fusion (reduce launch count and global memory round-trips), vectorized loads (float4), coalescing.

### Reduction (Sum, Max, Softmax)

| Inherently Violates | Reason | Alternative Optimization |
|---|---|---|
| Guideline 5 (warp divergence) | Tree reduction halves active threads each level | Warp shuffle replaces shared memory reduction |
| Guideline 1 (late-stage low parallelism) | Final stages have few active threads | Two-stage: parallel reduce → single-block final |
| Guideline 12 (atomic contention) | Inter-block reduce needs atomics | Minimize atomics via hierarchical reduction |

### GEMM / Matmul

The benchmark for GPU kernel optimization. Focus on: Tensor Core utilization (Guideline 10), shared memory tiling (Guideline 3), pipeline (Guideline 15), bank conflict avoidance (Guideline 4).

If a GEMM kernel's Tensor Core utilization is below 60%, there is almost certainly optimization headroom. On RTX 5090, accumulators reside in registers (no TMEM), so register pressure is higher for GEMM than on data-center Blackwell.

### Scatter / Gather / Embedding Lookup

| Inherently Violates | Reason | Alternative Optimization |
|---|---|---|
| Guideline 2 (non-coalesced) | Index-driven random access | Sort indices before access; use texture cache |
| Guideline 7 (can't hide latency) | Next address depends on current load | Increase per-thread element count |

---

## Tile Kernel Programming Model (CUDA 13.3+)

Tile Kernels are an alternative to traditional SIMT CUDA, introduced in CUDA 13.3. Code operates on entire tile blocks rather than individual threads — the compiler manages thread-level parallelism, shared memory staging, and warp scheduling. The C++ API lives in `<cuda_tile.h>` under the `cuda::tiles` namespace.

### SIMT vs Tile Comparison

| Aspect | SIMT (`__global__`) | Tile (`__tile_global__`) |
|---|---|---|
| Granularity | Individual threads | Entire blocks |
| Indexing | `blockIdx` + `threadIdx` | `ct::bid()` only |
| Parallelism | Programmer-managed warps | Compiler-managed |
| Memory access | Per-element loads/stores | Tile-level operations (partition_view) |
| Shared memory | Explicit `__shared__` declarations | Compiler auto-stages through shared memory |
| Warp divergence | Programmer's concern | Not applicable |
| Compilation | `nvcc -arch=sm_120` | `nvcc -std=c++20 -arch=sm_120 --enable-tile` |
| Launch syntax | `kernel<<<grid, block>>>()` | `kernel<<<grid>>>()` (single chevron arg) |
| Min architecture | sm_35+ | sm_80+ (sm_90+ for TMA) |

### When to Use Tiles vs SIMT — Decision Framework

| Factor | Use Tile Kernel | Use SIMT Kernel |
|---|---|---|
| **Warp-level control needed?** | No — compiler manages warps | Yes — custom warp shuffle, cooperative groups, warp-specialized patterns |
| **Memory access pattern** | Regular, structured (partition_view-friendly) | Irregular, index-dependent, scatter/gather with computed offsets |
| **Prototype speed** | Faster — less boilerplate, compiler handles details | Slower — manual shared memory, sync, tiling |
| **Tensor core usage** | `ct::mma()` — single line | Manual mma.sync PTX or CUTLASS — complex but full control |
| **Performance ceiling** | Compiler-limited — hints guide but don't guarantee | Programmer-controlled — higher ceiling for experts |
| **Debugging** | Harder — compiler transforms obscure source mapping | Easier — direct correspondence between source and execution |

**Rule of thumb:** Start with tile kernels for new work (requires sm_80+; sm_90+ for TMA). Fall back to SIMT when you need explicit warp-level control, custom memory access patterns, or maximum performance tuning beyond what hints provide.

### RTX 5090 Tile Kernel Constraints (sm_120)

- **Supported:** sm_120 fully supports tile kernels (validated on local hardware)
- **TMA hardware present:** `device__attribute_tensor_map_access_supported = 1` on sm_120. Use `ct::assume_aligned(ptr, 16_ic)` + `partition_view` + `[[cutile::hint(0, allow_tma=true)]]` to enable TMA lowering. Note: hardware presence is confirmed; whether the compiler generates TMA instructions for a specific kernel depends on access pattern and tile shape — check for TMA-related ncu metrics to confirm.
- **Shared memory:** The tile compiler auto-stages data through shared memory. The 100 KB/SM limit applies to compiler-managed staging, not programmer-controlled allocation.
- **Hint architecture code:** `1200` is accepted for sm_120 (validated). Use `0` for architecture-independent hints.
- **Compiler-chosen block size:** The tile compiler selects thread count per block (e.g., 128 for element-wise, 256 for GEMM). This is not programmer-controlled.
- **GDDR7 bandwidth context:** RTX 5090's ~1.8 TB/s DRAM bandwidth (vs 8 TB/s on data-center Blackwell) makes memory-bound tile kernels especially sensitive to access efficiency. Partition_view + TMA-eligible access patterns are high-value optimizations on this GPU because they maximize effective bandwidth utilization under a tighter ceiling.

### API Quick Reference

**Declarations:**
- `__tile_global__` — kernel entry point (replaces `__global__`)
- `__tile__` — device helper (replaces `__device__`)
- No cross-calling: `__tile_global__`/`__tile__` cannot call `__device__` functions and vice versa

**Launch:** `kernel<<<grid>>>()` or `kernel<<<grid, 1>>>()` — no threads-per-block argument

**Indexing:** `ct::bid()` returns `uint3` (`.x`, `.y`, `.z`); `ct::num_blocks()` returns `dim3`

**Tile creation:**
```cpp
using f32x256 = ct::tile<float, ct::shape<256>>;
auto z = ct::zeros<f32x256>();       // all zeros
auto o = ct::ones<f32x256>();        // all ones
auto f = ct::full<f32x256>(3.14f);   // fill with value
auto s = ct::iota<ct::tile<int, ct::shape<256>>>();  // 0,1,2,...,255
```

**Memory — partition_view (structured, TMA-eligible):**
```cpp
auto span = ct::tensor_span{ptr, ct::extents{N}};
auto view = ct::partition_view{span, ct::shape{256_ic}};
auto tile = view.load_masked(ct::bid().x);   // boundary-safe load
view.store_masked(result, ct::bid().x);       // boundary-safe store
```

**Memory — gather/scatter (irregular access):**
```cpp
auto offsets = 256 * ct::bid().x + ct::iota<ct::tile<int, ct::shape<256>>>();
auto ptrs = ptr + offsets;
auto tile = ct::load(ptrs);
ct::store(out_ptrs, result);
```

**Primitives:**
- `ct::mma(a_tile, b_tile, acc)` — matrix multiply-accumulate (uses tensor cores)
- `ct::sum(tile, dim)`, `ct::max(tile, dim)`, `ct::min(tile, dim)` — reductions
- `ct::atomic_add(ptr, value, memory_order, scope)` — atomic operations

**Optimization hints:**
```cpp
// Latency hint — on a statement (assignment), not a declaration
[[cutile::hint(0, latency=5)]]
tile = view.load(idx);

// Occupancy hint — on the function declaration
[[cutile::hint(0, occupancy=4)]]
__tile_global__ void my_kernel(...) { ... }

// TMA hint — on a load/store statement
[[cutile::hint(0, allow_tma=true)]]
tile = view.load_masked(idx);
```
Architecture code: `0` = all architectures, `1200` = sm_120 specifically (validated).

### Performance Annotations for Profiling

| Annotation | What It Does | ncu Signal When Missing |
|---|---|---|
| `__restrict__` on pointers | Enables read/write interleaving; compiler can overlap loads and stores | Higher `long_scoreboard` stall ratio; load/store instructions serialized |
| `ct::assume_aligned(ptr, 16_ic)` | Enables TMA lowering for partition_view loads | TMA metrics absent; loads use non-TMA path (higher `l1tex` wavefronts) |
| `ct::irange(lb, ub)` for loops | Enables compiler loop pipelining and vectorization | Higher instruction count; no software pipelining visible in SASS |
| `partition_view` over gather | Structured access enables TMA and compiler optimization | Higher `l1tex__t_sectors_pipe_lsu_mem_global_op_ld` (uncoalesced pattern) |
| `ct::assume_divisible(n, 16_ic)` | Eliminates boundary checks; enables non-masked loads | Unnecessary boundary masking instructions; slightly higher instruction count |

### Profiling Tile Kernels — How ncu Output Differs from SIMT

Based on hardware validation on RTX 5090 (sm_120, CUDA 13.3, ncu 2026.2):

**Occupancy:** The compiler chooses block size (thread count) automatically. `launch__block_size` shows the compiler's choice (e.g., 128 for element-wise, 256 for GEMM). `launch__occupancy_limit_warps` reflects the compiler-determined occupancy ceiling. You cannot tune block size directly — use the `occupancy` hint on the function declaration to guide the compiler.

**Shared memory staging:** The tile compiler stages global memory access through shared memory automatically. `l1tex__data_pipe_lsu_wavefronts_mem_shared.sum` will be non-zero even if your code has no explicit shared memory. This is expected behavior, not a bug.

**Stall signatures:** Stall metrics work with the naming pattern `smsp__average_warps_issue_stalled_<reason>_per_issue_active.ratio`. Validated stall reasons for tile kernels:
- `long_scoreboard` — memory latency (dominant for memory-bound tile kernels, same as SIMT)
- `barrier` — intra-block synchronization (appears in reductions with `ct::sum`)
- `mio_throttle` — memory ordering (appears with atomics)
- `math_pipe_throttle` — compute pipe saturation (appears in GEMM)
- `sleeping` — warp sleeping/yielding (common in GEMM tile kernels)
- `wait` — dependency waiting

**Tensor core metrics:** `ct::mma()` maps to the same tensor core metrics as manual mma.sync:
- `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_active` — tensor pipe utilization
- `sm__inst_executed_pipe_tensor_subpipe_hmma.avg.pct_of_peak_sustained_active` — HMMA instruction throughput
- `sm__ops_path_tensor_op_hmma_src_fp16_dst_fp32_sparsity_off.sum` — total tensor ops (should match M×N×K×2)

**Warp divergence:** Eliminated by the compiler — no warp divergence stalls appear. `smsp__average_warps_issue_stalled_branch_resolving_per_issue_active.ratio` is near zero.

---

## Pre-Coding Checklist

Before writing or optimizing a CUDA kernel on RTX 5090, review:

### RTX 5090 Specific (sm_120a)
0. **Compile target correct?** Using `-arch=sm_120a`?
1. **Can Tensor Cores help?** If GEMM/MMA: ensure cuBLAS/CUTLASS path or hand-written mma.sync with aligned dimensions. Note: accumulators live in registers on sm_120 (no TMEM).
2. **Precision selected?** LLM inference: consider FP8 (direct PTX) or FP4 (cuBLAS only). Training: BF16 + FP8 mixed.
3. **Memory budget?** Does the working set fit in 32 GB VRAM? For LLM: model weights + KV-cache + activations + overhead.
4. **L2 persistence useful?** RTX 5090 has 96 MB L2 (60 MB persistent). Hot data like KV-cache or frequently reused weight tiles can be pinned.
5. **Shared memory plan?** 100 KB/SM total, 48 KB default per block, 99 KB opt-in max. Double buffering limits each buffer to ~49 KB.

### General
6. **Enough threads?** Grid fills all 170 SMs with ≥ 2 waves? (Guidelines 1, 11)
7. **Memory access pattern?** Warp threads access contiguous addresses? (Guideline 2)
8. **Data reuse?** If yes, shared memory tiling planned? (Guideline 3)
9. **Bank conflicts?** Shared memory access needs padding? (Guideline 4)
10. **Branches?** Branch conditions uniform per warp? (Guideline 5)
11. **Registers sufficient?** `__launch_bounds__` set? (Guideline 6)
12. **Compute-memory overlap?** Double buffering or deeper pipeline designed? 99 KB shared memory limits pipeline depth. (Guidelines 7, 15)
13. **Precision correct?** All float literals have `f` suffix? Can FP8 improve throughput? (Guideline 8)
14. **Unnecessary syncs?** Can warp-level ops replace block-level sync? (Guideline 16)
15. **Tensor Cores applicable?** Dimensions aligned? Data types match? (Guideline 10)
16. **Loads vectorized?** Addresses aligned to 8/16 bytes? (Guideline 13)
17. **Pointers annotated with `const __restrict__`?** (Guideline 14)
