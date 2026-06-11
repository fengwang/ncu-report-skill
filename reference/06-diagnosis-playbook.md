# Diagnosis Playbook — Pattern → Cause → Fix

For each observed NCU signal, what does it typically mean, and what's the first fix to try? This synthesizes the RTX 5090 programming guidelines (see `blackwell-cuda-programming.md` at the repo root) with the profiling signals.

Read this after you've gathered the metrics (via [`05-analysis-dimensions.md`](05-analysis-dimensions.md)) — here you translate metrics into diagnoses and fix directions.

---

## How to use this doc

For each *observation* below, read:

- **Signals** — what specific metric values flag this pattern.
- **Why** — the underlying cause.
- **First-line fix** — the cheapest change to try.
- **Deeper fixes** — when first-line isn't enough.
- **Exceptions** — kernel types where this pattern is actually *expected* and should be left alone.

Most kernels will match 2-4 patterns simultaneously. **Rank them by magnitude** using NCU's `Est. Speedup: X%` fields (from `--page details`) and the stall-percentage breakdown. Fix the biggest one first.

---

## Pattern A — Small grid / SM idle

**Signals:**
- `launch__waves_per_multiprocessor < 0.5`
- `launch__grid_size < device__attribute_multiprocessor_count` (e.g., 64 blocks on a 170-SM RTX 5090)
- NCU rule: *"The grid for this launch is configured to execute only N blocks, which is less than the M multiprocessors used."* with `Est. Speedup: 50-90%`

**Why:** each CTA occupies at most one SM; with fewer CTAs than SMs, some SMs are completely idle throughout the kernel.

**First-line fix:** increase grid size. Look for a dimension the kernel currently doesn't parallelize:
- Add a split along `K` (split-K for reductions / attention).
- Split across heads / channels if grouped.
- Use Grid-stride loops so one block does multiple work units — but only if work units are cheap.

**Deeper fixes:**
- **Persistent kernel**: launch one block per SM, each block dequeues work items from an atomic counter. Good for dynamic-shape cases.
- **Fuse with adjacent kernels** so more work fits in one launch.

**Exceptions:**
- LLM decode (batch=1, query_len=1) is fundamentally small. Split-K over KV length is the standard mitigation.
- Final reduction stages of a multi-level reduction are naturally small; fuse them into the producing kernel.

**Cross-ref:** See `blackwell-cuda-programming.md` § Ensure Sufficient Parallelism.

---

## Pattern B — Tail effect (variable-length inputs)

**Signals:**
- Multi-workload: `max_seq_len / avg_seq_len > 3` in input distribution.
- Per-SM active cycles span 5-100× between slowest and fastest SM (from `--page details` distribution).
- PM timeline shape: long gradual tail at the end (visible via `plot_timeline.py`).
- `launch__waves_per_multiprocessor > 1.05` with partial last wave.
- NCU rule: `"partial wave may account for up to X% of the total runtime"`.

**Why:** each CTA iterates some variable-size inner loop. When sequences have vastly different lengths, a few long-sequence CTAs keep running after everyone else finished.

**First-line fix (cheap):**
- **Packed batching / sorting**: sort inputs by length (at the application level) so CTAs running concurrently do roughly equal work.
- **Split long sequences across more CTAs**: add a `split_factor` grid dimension; each CTA handles `ceil(seq_len / split_factor)` tokens, and a small post-reduction combines partials.

**Deeper fixes:**
- **Chunkwise kernel**: break each sequence into fixed-size chunks, process chunks in parallel, then stitch with a small recurrence. This is the approach of flash-linear-attention's `chunk_delta_rule_fwd` for Mamba/GLA-style recurrences.
- **Classify-and-dispatch**: short sequences go through the simple path (one CTA per seq), long sequences through the chunked path.

**Exceptions:**
- Short kernels (< 10 µs) where partial-wave cost is absolute-small.
- Workloads where you already pre-sort / pre-pack.

**Cross-ref:** See `blackwell-cuda-programming.md` § Optimize Grid/Block Configuration.

---

## Pattern C — Uncoalesced global loads

**Signals:**
- `l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum / l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum > 5` (ideal is 4).
- NCU rule: *"uncoalesced global accesses resulting in N excessive sectors (X% of the total)"*.
- NCU rule: *"On average, only Y of the 32 bytes transmitted per sector are utilized"*.
- Primary stall reason on the offending load line is `long_scoreboard`.

**Why:** lanes in a warp access non-contiguous addresses; hardware fetches extra sectors that only a few lanes use.

**First-line fix:** rework the thread ↔ data mapping:
- If current pattern is `x[lane * K + i]` (stride K), flip to `x[lane + i * 32]` (coalesced).
- Check AoS layouts: `struct { float a, b; } arr[N]` → `struct { float a[N], b[N]; }` so each field is a separate coalesced stream.

**Deeper fixes:**
- Use shared memory as a transposer: coalesced-load to shared, then arbitrary-access from shared.
- Vectorize: replace scalar `LDG.E` with `LDG.E.64` / `LDG.E.128` (use `float2` / `float4` / `ushort2` types).

**Exceptions:**
- Gather/scatter by random index (sparse matmul, embedding lookup) — fundamentally uncoalesced. Sort the indices for locality if possible.
- Graph / tree traversal.

**Cross-ref:** See `blackwell-cuda-programming.md` § Coalesce Memory Accesses, § Vectorize Memory Access.

---

## Pattern D — Sparse writes (low store efficiency)

**Signals:**
- `smsp__sass_average_data_bytes_per_sector_mem_global_op_st.ratio < 16` (ideal is 32).
- `l1tex__t_sector_pipe_lsu_mem_global_op_st_hit_rate.pct` lower than expected.
- Code contains patterns like `if (lane_id < K) { output[...] = ... }`.

**Why:** only a subset of warp lanes write, so the L1 store buffer flushes half-empty sectors.

**First-line fix:** pack the write. Have the warp collectively produce `K` values first (via shuffle or shared memory reduction), then have exactly `K` contiguous lanes perform `K` consecutive writes.

If `K ≥ 32`: all lanes can write; make sure the per-lane index is contiguous.

If `K < 8`: consider batching multiple iterations' results into a vectorized write (e.g., 4 iterations' output packed into a single `float4`).

**Deeper fixes:**
- Write into shared memory first, then do a coalesced global store at the end of the block.

**Exceptions:**
- Histogram / scatter (inherently sparse) — different optimization path, see Pattern G.

---

## Pattern E — Latency-bound (long-scoreboard-dominated)

**Signals:**
- `smsp__pcsamp_warps_issue_stalled_long_scoreboard / smsp__pcsamp_sample_count > 0.40`.
- `smsp__average_warps_issue_stalled_long_scoreboard_per_issue_active.ratio > 3`.
- `dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed < 10%` (→ not DRAM-bandwidth-bound).
- Hotspot lines are global loads (check `stall_hotspots_<tag>.txt`).

**Why:** warps issue a load, then stall waiting for it to return before the next dependent op. Usually combined with low occupancy or insufficient ILP.

**First-line fix:** increase in-flight memory requests:
- **Unroll the load loop** so 4-8 loads are issued before any value is used. Compiler + hardware reorders.
- **Add more independent warps** — raise occupancy (Pattern J).
- **`cp.async` (Ampere+)** for bulk async loads that don't block issue. Note: TMA and `tcgen05.cp` are data-center Blackwell only, not available on sm_120.

**Deeper fixes:**
- Software pipelining: while tile N is being computed, pre-load tile N+1 into shared memory.
- Move reused data to shared memory so subsequent loads hit L1.

**Exceptions:**
- Pointer chasing / graph traversal — data dep chain is fundamental.

**Cross-ref:** See `blackwell-cuda-programming.md` § Hide Memory Latency, § Pipeline Compute and Memory Access.

---

## Pattern F — Compute-bound but not on tensor cores

**Signals:**
- `sm__inst_executed_pipe_fma.avg.pct_of_peak_sustained_active > 50%`.
- `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed = 0%`.
- Workload is matmul-ish (GEMM, attention, conv).

**Why:** kernel uses scalar FMA via the ALU pipe instead of tensor cores. On RTX 5090, tensor cores deliver 209.5 TFLOPS BF16 vs 104.8 TFLOPS FP32 scalar — 2× higher throughput for BF16→FP32 operations.

**First-line fix:** use `mma.sync` PTX or the WMMA C++ API on sm_120. If hand-rolling is too much, use CUTLASS 4.x or cuBLAS, which are already tuned for the target arch. Note: `wgmma` and `tcgen05.mma` are NOT available on sm_120 (data-center Blackwell only).

**Deeper fixes:**
- Restructure data layout to meet MMA tile-shape constraints (e.g., `m16n8k16` for BF16).
- Use shared memory staging for MMA operand preparation.

**Exceptions:**
- Non-matrix workloads (reduction, sort, element-wise) — tensor cores don't help.
- Small matrices (M, N, K < 32) — tensor-core tiles are too coarse.

**Cross-ref:** See `blackwell-cuda-programming.md` § Use Tensor Cores Effectively.

---

## Pattern G — Atomics contention

**Signals:**
- `long_scoreboard` samples concentrate on `ATOM` / `RED` SASS instructions.
- `lts__t_sectors_op_atom.sum` or `lts__t_sectors_op_red.sum` is large.
- L2 throughput is high but compute throughput is low.

**Why:** many threads atomically updating few locations → serialization.

**First-line fix:** hierarchical reduction.
- Within-warp: `__shfl_down_sync` (no atomic).
- Within-block: shared memory reduction (no atomic).
- Between blocks: single atomic at the end per block.

**Deeper fixes:**
- Shared-memory histogram that flushes to global in one coalesced pass.
- Bucketing: thread writes to `output[tid % N_buckets]`, followed by a merge kernel.

**Exceptions:**
- NCCL-style communication — atomics are fundamental there.

**Cross-ref:** See `blackwell-cuda-programming.md` § Reduce Atomic Contention.

---

## Pattern H — Shared-memory bank conflicts

**Signals:**
- `l1tex__data_pipe_lsu_wavefronts.avg.pct_of_peak_sustained_elapsed` high for shared-mem ops.
- `short_scoreboard` stalls concentrated on shared-memory load lines.
- Access pattern has regular strides that align to bank boundaries.

**Why:** shared memory has 32 banks; same-bank accesses serialize.

**First-line fix:** padding. `__shared__ float tile[32][33]` instead of `[32][32]` breaks regular bank alignment.

**Deeper fixes:**
- Swizzle: XOR-scramble indices so accesses spread across banks.
- Restructure data layout so warp lanes access different banks.

**Exceptions:**
- Broadcast reads (all lanes read same address) are conflict-free.
- Low shared-mem access volume — don't bother.

**Cross-ref:** See `blackwell-cuda-programming.md` § Avoid Shared Memory Bank Conflicts.

---

## Pattern I — Synchronization overhead

**Signals:**
- `smsp__pcsamp_warps_issue_stalled_barrier` > 20% of samples.
- Source hotspot line is `BAR.SYNC`.

**Why:** `__syncthreads()` waits for the slowest warp. Combined with any per-warp work imbalance, this amplifies.

**First-line fix:**
- Replace block-level syncs with warp-level primitives (`__shfl_sync`, `__ballot_sync`, `__syncwarp`) where only warp-scoped synchronization is needed.
- Reduce total sync count — consolidate multiple synchronized phases.

**Deeper fixes:**
- Warp-specialized execution: producer warps and consumer warps with mbarrier instead of `__syncthreads`.

**Cross-ref:** See `blackwell-cuda-programming.md` § Reduce Synchronization Overhead.

---

## Pattern J — Low achieved vs theoretical occupancy

**Signals:**
- `sm__maximum_warps_per_active_cycle_pct > 50` but `sm__warps_active.avg.pct_of_peak_sustained_active << 50`.
- NCU rule: *"The difference between calculated theoretical (X%) and measured achieved occupancy (Y%) ..."*.

**Why:** Theoretical occupancy is the max warps that *could* be resident. Achieved is how many are *actually* running. Gap is caused by: stalls (leaves slots empty), imbalance (some SMs empty), short kernel (warmup dominates).

**Reading:** if the gap is large AND Pattern B (tail effect) is present, fixing imbalance will close the gap. If no imbalance, look at stall reasons (Pattern E, H, I).

**First-line fix:** look for the stall reason causing the gap and address that pattern.

---

## Pattern K — Register spill

**Signals:**
- `smsp__sass_inst_executed_op_local_ld.sum > 0` or `smsp__sass_inst_executed_op_local_st.sum > 0`.
- NCU rule: *"N bytes spilled to local memory"* in Instruction Statistics.
- `launch__registers_per_thread > 128`.

**Why:** compiler couldn't fit all live variables in registers, spilled some to local memory (which is DRAM-backed).

**First-line fix:** `__launch_bounds__(maxThreadsPerBlock, minBlocksPerMultiprocessor)` on the kernel. This tells the compiler to stay within a register budget.

**Deeper fixes:**
- Reduce the number of live values: recompute values instead of caching, split the kernel into two.
- Move per-thread arrays to shared memory with explicit indexing.

**Exceptions:**
- Large fused kernels (FlashAttention) accept some spill in exchange for larger savings upstream.

**Cross-ref:** See `blackwell-cuda-programming.md` § Control Register Pressure.

---

## Pattern L — FP64 used unintentionally

**Signals:**
- `sm__pipe_fp64_cycles_active.avg.pct_of_peak_sustained_active > 0` in a kernel that "should" be FP32.

**Why:** C/C++ floating-point literals (`1.0`, `0.5`, `3.14`) default to `double`. A `float x = a + 1.0 * b;` promotes `a + 1.0*b` to double.

**First-line fix:** add `f` suffix to all literals: `1.0f`, `0.5f`, `3.14f`. Add `__expf` / `__logf` / `__sinf` variants for transcendentals.

**Cross-ref:** See `blackwell-cuda-programming.md` § Use Appropriate Math Precision.

---

## Pattern M — Pipeline bubbles (no compute/memory overlap)

**Signals:**
- PM timeline of `sm__throughput` and `dram__throughput` shows a sawtooth (high compute ↔ high DRAM alternating).
- `long_scoreboard` stalls high but DRAM throughput also high.

**Why:** kernel loads a tile, computes on it, loads next tile — single-buffered.

**First-line fix:** double-buffer. Use two shared-memory tiles; while computing on tile A, load tile B. `__syncthreads` between phases.

**Deeper fixes:**
- Multi-stage pipeline (3-4 stages). Use `cp.async` for async loads on sm_120.

**Cross-ref:** See `blackwell-cuda-programming.md` § Pipeline Compute and Memory Access.

---

## Pattern N — Warp divergence

**Signals:**
- `smsp__thread_inst_executed_per_inst_executed.ratio < 32` (far from the 32 ideal).
- Branch efficiency metric low in `--page details`.
- Divergent branches cluster on specific source lines.

**Why:** lanes in a warp take different paths at a branch; hardware serializes.

**First-line fix:**
- Rearrange so all lanes in a warp take the same branch. Sort / partition data if possible.
- Convert `if (cond) a else b` to branchless `mask * a + (1-mask) * b` — cheap if both sides are cheap.

**Exceptions:**
- Tree reductions in warps (last few steps have half / quarter / ... active). Use `__shfl_down_sync` to handle cleanly.
- Boundary handling (a few warps at tensor edge) — not worth fighting.

**Cross-ref:** See `blackwell-cuda-programming.md` § Avoid Warp Divergence.

---

## Pattern O — Decode bandwidth ceiling (LLM-specific)

**Signals:**
- `dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed > 80%`.
- `launch__grid_size` is small (batch=1, single-token decode → few thread blocks).
- `sm__throughput.avg.pct_of_peak_sustained_elapsed` is low (DRAM is the bottleneck, not compute).
- Kernel is identified as a decode-phase operation (attention or GEMV with batch=1).

**Why:** single-token autoregressive decode is fundamentally memory-bandwidth-bound. Each decode step reads the entire weight matrix and KV-cache but produces only one output token. On RTX 5090 with ~1.8 TB/s DRAM bandwidth (4.4× lower than data-center Blackwell), decode kernels are proportionally more bandwidth-starved.

For a 7B FP16 model: ~14 GB of weights must be read per token. At 1.8 TB/s, that's ~7.8 ms per token — a hard floor that no compute optimization can break.

**First-line fix:**
- **Quantize weights:** FP16 → FP8 halves the bytes read, roughly doubling decode token throughput. FP4 (library-only on sm_120) halves again.
- **Quantize KV-cache:** FP16 → FP8/INT8 reduces attention's memory footprint.
- **Operator fusion:** fuse adjacent memory-bound ops to reduce total DRAM round-trips.

**Deeper fixes:**
- **Speculative decoding:** generate multiple candidate tokens in a single step, then verify in batch — amortizes the weight-read cost over multiple tokens.
- **Batching (if latency budget allows):** even batch=2 doubles the arithmetic intensity, moving the kernel closer to the compute-bound regime.
- **Model-level:** use a smaller model, or a model with fewer layers / smaller hidden dimension that fits the bandwidth budget.

**Exceptions:**
- Batched inference (batch > 4) — the kernel is likely compute-bound, not bandwidth-bound.
- Prefill phase (processing the full prompt) — prefill is typically compute-bound due to high arithmetic intensity.

**Cross-ref:** See `blackwell-cuda-programming.md` § Why Decode is Deeply Memory-Bandwidth-Bound.

---

## Pattern P — KV-cache thrashing (LLM-specific)

**Signals:**
- `lts__t_sector_hit_rate.pct` < 50% during attention kernels.
- `dram__bytes_op_read.sum` is significantly larger than expected from weight reads alone — the excess is KV-cache reload from DRAM.
- Estimated KV-cache size exceeds 96 MB (RTX 5090 L2 capacity).

**KV-cache size estimation:**
```
kv_bytes = 2 × num_layers × num_kv_heads × head_dim × seq_length × bytes_per_element
```
Example: 32 layers × 8 KV heads × 128 head_dim × 4096 seq_len × 2 bytes (FP16) × 2 (K+V) = 512 MB — well beyond the 96 MB L2.

**Why:** when the KV-cache exceeds L2 capacity, every attention pass must reload KV entries from DRAM. This converts attention from a compute-bound operation (where data is reused from L2) to a bandwidth-bound operation (where DRAM is the bottleneck). On RTX 5090 with 96 MB L2 and 60 MB persistent L2, the cache pressure is tighter than on data-center GPUs.

**First-line fix:**
- **Quantize KV-cache:** FP16 → FP8 or INT8 halves the cache footprint.
- **Persistent L2 partitioning:** use `cudaCtxSetLimit(cudaLimitPersistingL2CacheSize, ...)` to reserve up to 60 MB of L2 for KV-cache. Requires `cudaStreamSetAttribute` per-stream.

**Deeper fixes:**
- **GQA / MQA:** grouped-query or multi-query attention architectures reduce the number of KV heads, shrinking the cache.
- **Reduce context length:** if the use case allows, shorter contexts fit in L2.
- **Sliding window attention:** only cache the most recent N tokens' KV pairs.
- **PagedAttention (vLLM):** reduces fragmentation but does not reduce total KV size.

**Exceptions:**
- Short context lengths where KV-cache fits comfortably in L2 (< 96 MB).
- Multi-head attention with very few layers (unlikely to exceed L2).

**Cross-ref:** See `blackwell-cuda-programming.md` § KV-Cache Memory Budget.

---

## Pattern Q — Quantization mismatch (LLM-specific)

**Signals:**
- `sm__pipe_tensor_subpipe_hmma_cycles_active.avg.pct_of_peak_sustained_elapsed > 0` (FP16/BF16 tensor pipe is active).
- `sm__pipe_tensor_subpipe_imma_cycles_active.avg.pct_of_peak_sustained_elapsed = 0` (INT8 pipe is idle).
- No FP8 tensor core activity visible in metrics.
- The workload is known to be quantizable to FP8 or FP4.

**Why:** RTX 5090 tensor cores support a full precision spectrum with increasing throughput:

| Precision | TFLOPS/TOPS | Roofline breakpoint (FLOPs/byte) |
|---|---|---|
| FP32 (scalar) | 104.8 | 58.5 |
| BF16/FP16 (tensor, dense) | 209.5 | 116.9 |
| FP8 (tensor, dense) | 419.0 | 233.8 |
| INT8 (tensor, dense) | 838 | 467.6 |
| FP4 (tensor, sparse 2:4)* | 3,352 | 1,870 |

*FP4 figure is structured sparsity (2:4); all others are dense.

Using FP16 when FP8 is viable means 2× less compute throughput and no bandwidth savings. For decode workloads that are already bandwidth-bound, quantization simultaneously reduces memory traffic AND increases compute throughput.

**First-line fix:**
- **Enable FP8 inference:** most LLM frameworks (TensorRT-LLM, vLLM) support FP8 weight quantization. Switch the model to FP8 and re-profile.
- **Verify tensor pipe utilization:** after switching to FP8, check that `sm__pipe_tensor_subpipe_imma_cycles_active` or the FP8-specific pipe is now active.

**Deeper fixes:**
- **FP4/NVFP4 quantization:** provides another 2× throughput, but is library-only on sm_120 (no direct PTX access). TensorRT-LLM has FP4 support.
- **Mixed-precision quantization:** quantize most layers to FP8/FP4, keep accuracy-sensitive layers (e.g., first/last, attention logits) at FP16.

**Exceptions:**
- Accuracy-critical layers where quantization degrades output quality beyond acceptable thresholds.
- Small matrices (M, N, K < 32) where tensor core tile overhead exceeds the precision benefit.
- Already using the lowest viable precision — no room to quantize further.

**Cross-ref:** See `blackwell-cuda-programming.md` § Quantization Impact on Decode.

---

## Tile Kernel Diagnosis Patterns (CUDA 13.3+)

The following patterns apply to tile kernels (`__tile_global__`, `cuda::tiles`). They complement the SIMT patterns above — both sets can coexist in a single report if the application mixes tile and SIMT kernels.

### Pattern R — Tile Kernel Low Occupancy

**Signal:** `sm__warps_active.avg.pct_of_peak_sustained_active` is below 50% on a tile kernel. `launch__occupancy_limit_warps` shows a low ceiling despite hardware supporting 48 warps/SM.

**Cause:** The tile compiler chose a block size (visible in `launch__block_size`) that limits occupancy. This happens when:
- The tile shape is large, forcing the compiler to allocate more registers per block
- The partition_view shape creates blocks with high shared memory footprint
- The default occupancy target is too conservative for the workload

**Fix:**
1. Add `[[cutile::hint(0, occupancy=N)]]` on the `__tile_global__` function declaration to guide the compiler toward N concurrent blocks per SM.
2. Reduce tile shape dimensions (smaller tiles → fewer registers → more blocks).
3. Check `launch__block_size` — if the compiler chose a large block size, the tile shape may be unnecessarily wide.

**Validated on RTX 5090:** Element-wise tile kernel had `sm__warps_active.avg.pct = 46.8%` with compiler-chosen 128 threads/block and `launch__occupancy_limit_warps = 12`. The occupancy hint can increase this.

### Pattern S — Partition_view vs Gather Memory Inefficiency

**Signal:** High `l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum` relative to data volume, or high `long_scoreboard` stall ratio despite regular access patterns.

**Cause:** Using gather/scatter (pointer arithmetic + `ct::load()`) where partition_view would enable structured, TMA-eligible access. Gather produces independent per-element loads that may not coalesce optimally.

**Fix:**
1. Restructure data layout to enable `partition_view` (contiguous, regularly strided).
2. Add `ct::assume_aligned(ptr, 16_ic)` to enable TMA lowering.
3. Use `load_masked`/`store_masked` for boundary safety instead of manual index clamping.

**Note:** A direct partition_view vs gather ncu comparison was not profiled in this session. The guidance to prefer partition_view is based on NVIDIA documentation (partition_view enables structured/TMA-eligible access) and the general principle that structured access patterns allow more compiler optimization. Add a gather-path tile kernel ncu run to quantify the specific trade-off on sm_120.

### Pattern T — Tile MMA Underutilization

**Signal:** `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_active` is below 20% in a `ct::mma()` kernel.

**Cause:**
- Tile dimensions don't align with hardware MMA shape (tensor cores operate on fixed tile sizes)
- Insufficient K-dimension depth — loop body too small to keep the tensor pipe fed
- Missing optimization hints causing the compiler to generate suboptimal scheduling

**Fix:**
1. Check tile shape matches hardware MMA dimensions: for FP16→FP32, use shapes that are multiples of 16 (M, N) and 16 (K).
2. Add `[[cutile::hint(0, latency=5)]]` on the load statements feeding `ct::mma()` to guide prefetching.
3. Use `ct::irange()` for the K-loop to enable compiler loop pipelining.
4. Add `ct::assume_divisible(K, 16_ic)` to eliminate boundary checks in the inner loop.

**Validated on RTX 5090:** Tile GEMM (32×64×64 tiles, FP16→FP32) achieved `sm__pipe_tensor_cycles_active.avg.pct = 28.5%` and `sm__inst_executed_pipe_tensor_subpipe_hmma.avg.pct = 13.9%` with `ct::irange()` and latency hints. Top stall was `sleeping` (4.6) indicating the compiler is managing warp yield/resume around tensor ops.

### Pattern U — Tile Atomic Contention

**Signal:** `lts__d_atomic_input_cycles_active.max.pct_of_peak_sustained_elapsed` exceeds 20%, or `smsp__average_warps_issue_stalled_mio_throttle_per_issue_active.ratio` exceeds 5.0 in a tile kernel using `ct::atomic_add`.

**Cause:** Many blocks performing device-scope atomics on the same address (e.g., global reduction via `ct::atomic_add` with `thread_scope_device_t`).

**Fix:**
1. Use `ct::sum(tile, dim)` for intra-block reduction first, then a single `ct::atomic_add` per block for the cross-block accumulation.
2. If contention is severe, use a two-stage approach: first-stage tile kernel writes partial results to an array (one per block), second-stage kernel reduces the partials.
3. Check `l1tex__t_sectors_pipe_lsu_mem_global_op_atom.sum` — this should equal the block count for optimal single-atomic-per-block patterns.
4. If atomic count >> grid size, the tile code is performing per-element atomics instead of per-block — restructure to reduce first.

**Validated on RTX 5090:** Tile reduction (1M elements, 4096 blocks, single atomic per block) showed `lts__d_atomic_input_cycles_active.max.pct = 29.2%`, `barrier` stall ratio = 9.1 (from intra-block `ct::sum`), `mio_throttle` stall ratio = 7.9 (from memory ordering). Atomic sector count = 4096 (matches block count — one atomic per block, optimal pattern).

---

## Single-User Decode Optimization Checklist (RTX 5090)

A step-by-step checklist for optimizing single-token autoregressive decode kernels on RTX 5090. Work through all three phases in order. Each step specifies the ncu metric to check, the RTX 5090-calibrated threshold, and what to do if the check fails.

**Prerequisites:** An ncu report collected with `--set full --section PmSampling` on the decode kernel of interest.

### Phase 1 — Characterize the Bottleneck

#### Step 1: Confirm this is a decode kernel
- **Metric:** `launch__grid_size`
- **Threshold:** Grid size is small (typically < 170 blocks for batch=1 single-token decode).
- **If FAIL (large grid):** This is likely a prefill or batched kernel, not decode. The checklist still applies but bandwidth saturation is less likely — the kernel may be compute-bound.
- **If PASS:** Proceed.

#### Step 2: Measure DRAM bandwidth utilization
- **Metric:** `dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed`
- **Threshold:** > 60% means bandwidth-saturated (normal for decode on RTX 5090 at ~1.8 TB/s). < 30% means NOT bandwidth-bound.
- **If > 60%:** Kernel is bandwidth-bound (see Pattern O). Go to Steps 6–8 (reduce bytes moved).
- **If < 30%:** Kernel is latency-bound or underutilized. Go to Steps 9–11.
- **If 30–60%:** Mixed regime. Check Steps 3–5 to narrow down.

#### Step 3: Check tensor core utilization
- **Metric:** `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed`
- **Threshold:** For decode GEMV (batch=1), expect < 5%. For small-batch GEMM, expect 10–50%.
- **If near-zero:** Expected for decode — tensor cores can't fill on tiny matrices. Not actionable.
- **If > 20%:** Kernel has meaningful compute component. Check if it's a batched or prefill kernel misidentified as decode.

#### Step 4: Identify dominant stall reason
- **Metric:** `smsp__average_warps_issue_stalled_long_scoreboard_per_issue_active.ratio`
- **Threshold:** > 3.0 means memory latency dominates.
- **If > 3.0:** Memory-latency-bound. The kernel is waiting for data from DRAM or L2. Reducing traffic (Steps 6–8) or hiding latency (Steps 9–10) will help.
- **If < 1.0:** Check other stall reasons — `math_pipe_throttle` (compute-bound), `barrier` (sync overhead, see Pattern I), `dispatch_stall` (launch config issue).

#### Step 5: Check L2 hit rate
- **Metric:** `lts__t_sector_hit_rate.pct`
- **Threshold:** > 60% means significant L2 caching (weights or KV-cache partially fit). < 30% means most data streams from DRAM.
- **If high hit rate on weights:** Persistent L2 optimization viable (Step 11). Model weights partially fit in 96 MB L2.
- **If low hit rate:** Data is too large for L2. Focus on reducing DRAM traffic.

### Phase 2 — Optimize

#### Step 6: Evaluate quantization opportunity
- **Metric:** Compare `dram__bytes_op_read.sum` across precisions (see `blackwell-cuda-programming.md` § Precision-Specific Profiling Recipes).
- **Threshold:** FP16 → FP8 should halve bytes read. FP8 → FP4 should halve again.
- **If bandwidth-saturated (Step 2 > 60%):** Quantization is the highest-leverage fix. FP8 gives ~2× decode speedup; FP4 gives ~4× (theoretical). See Pattern Q for mismatch diagnosis.
- **If NOT bandwidth-saturated:** Quantization helps bandwidth but won't fix the primary bottleneck.

#### Step 7: Check memory coalescing quality
- **Metric:** `l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum / l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum` (sectors per request)
- **Threshold:** Ideal = 4 (32 threads × 4 bytes / 128-byte cache line). Values > 8 indicate poor coalescing.
- **If > 8:** Uncoalesced access pattern — see Pattern C. Common in KV-cache access with non-contiguous layouts.
- **If ≤ 4:** Coalescing is good. Not the bottleneck.

#### Step 8: Diagnose KV-cache access pattern
- **Metrics:** `dram__bytes_op_read.sum` vs expected weight-only traffic. `lts__t_sector_hit_rate.pct` during attention kernels.
- **Threshold:** If DRAM reads significantly exceed model weight reads, the excess is KV-cache reload. See Pattern P for detailed diagnosis.
- **If KV-cache thrashing:** Reduce context length, quantize KV-cache to FP8, or evaluate persistent L2 (Step 11).
- **If KV-cache fits in L2:** Not the bottleneck.

#### Step 9: Check occupancy vs theoretical
- **Metric:** `sm__warps_active.avg.pct_of_peak_sustained_active`
- **Threshold:** Theoretical max = 48 warps/SM on RTX 5090. Achieved < 25% of theoretical suggests room for improvement.
- **If low occupancy:** Check register pressure (Step 10), shared memory usage, or block size. See Pattern J.
- **If occupancy is reasonable (> 50% of theoretical):** Occupancy is not the bottleneck.

#### Step 10: Check for register spill
- **Metric:** `launch__registers_per_thread` and `lmem__size_per_thread`
- **Threshold:** > 128 registers/thread limits occupancy to ≤ 4 blocks/SM. Any local memory (lmem > 0) indicates spill.
- **If spilling:** Reduce register pressure — simplify the kernel, split into phases, use `__launch_bounds__`. See Pattern K.
- **If no spill:** Register pressure is not the bottleneck.

#### Step 11: Evaluate persistent L2 for KV-cache
- **Metric:** `lts__t_sector_hit_rate.pct` before and after enabling persistent L2.
- **Threshold:** RTX 5090 supports up to 60 MB persistent L2 (`cudaDeviceSetLimit(cudaLimitPersistingL2CacheSize, ...)`).
- **If KV-cache ≤ 60 MB:** Pin the KV-cache in L2 using `cudaStreamSetAttribute` with `cudaStreamAttributeAccessPolicyWindow`. Expect L2 hit rate improvement.
- **If KV-cache > 60 MB:** Only the hot portion fits. Pin the most recent tokens' KV entries.

#### Step 12: Check attention implementation
- **Metric:** Compare kernel duration against a known-good FlashAttention/FlashInfer baseline.
- **Threshold:** Non-fused attention (materializing the full attention matrix) uses O(seq_len²) memory. Fused attention uses O(seq_len).
- **If using non-fused attention:** Switch to FlashAttention or FlashInfer. This is usually the single largest optimization available.
- **If already fused:** Check if the implementation is optimal for the head size and sequence length.

#### Step 13: Check warp divergence in attention masking
- **Metric:** `smsp__thread_inst_executed_pred_on_per_inst_executed.ratio`
- **Threshold:** < 0.7 indicates significant warp divergence.
- **If divergent:** Common in causal masking with variable-length inputs. Padding to warp-aligned boundaries reduces divergence. See Pattern N.
- **If not divergent:** Not the bottleneck.

### Phase 3 — Verify Improvement

#### Step 14: Re-profile after changes
- Collect a new ncu report with the same `--set full --section PmSampling` flags.
- Compare `gpu__time_duration.sum` (kernel latency) and `dram__bytes_op_read.sum` (bytes moved) against the baseline.
- A valid improvement shows: lower duration AND lower bytes read (for quantization) or higher bandwidth utilization (for coalescing fixes).

#### Step 15: Check for regressions
- Verify other kernels in the pipeline haven't slowed down (quantization changes affect all layers).
- Check numerical accuracy if precision was reduced — run a reference comparison on model outputs.
- Monitor `gpu__time_duration.sum` across all kernels, not just the one you optimized.

#### Step 16: Document findings
- Record the optimization in the report template format (`reference/07-report-template.md`).
- Include: original metric values, changes made, new metric values, measured speedup.
- Note any trade-offs (accuracy loss, increased code complexity, framework version requirements).

---

## Ranking template for the final report

When you hand back an optimization plan, rank by `(expected speedup) × (effort ratio)`. NCU's `Est. Speedup` is your best estimator.

```
Priority 1: <pattern> — <concrete fix>
  Evidence: <metric value(s)>
  NCU Est. Speedup: X%
  Effort: <low / medium / high>
  Why now: <reason this is the highest-leverage fix>

Priority 2: ...
```

A good rule of thumb: at most 3-5 priorities in the plan. More than that dilutes the signal, and priorities > 5 usually contribute < 5% speedup each.
