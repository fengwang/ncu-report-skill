# Profiling Workflow — End-to-End

This is the complete checklist from "user asks to profile" to "final report". Every step has a short rationale and a pointer to the detailed doc.

---

## Phase 0 — Create a new run directory

**Always start here.** See [`00-directory-layout.md`](00-directory-layout.md) for the full convention.

```bash
# At the repo root
PROFILE_RUN_DIR=profile/<descriptive_run_name>        # e.g. <kernel>_v1_baseline
mkdir -p "$PROFILE_RUN_DIR"/{harness,reports,analysis}
```

- Pick a new, descriptive name for this run. Never reuse an existing directory.
- If you're profiling a new version of a kernel you've profiled before, that's a **new** run (e.g. `<kernel>_v2_optimized/`, not overwriting `<kernel>_v1_baseline/`).
- If you're profiling the same version against a different workload, that's also a new run — or, at minimum, each workload's `.ncu-rep` gets a distinct tag and the analysis scripts are kept separate.

Every artifact produced in subsequent phases is written **only** under `$PROFILE_RUN_DIR`. Never into a sibling run's directory.

---

## Phase 0.5 — Frame the problem (before any tools)

Before typing any commands, answer these in your head (or in a short note to the user):

1. **What kernel(s) am I profiling?** Get the exact kernel name or regex. Kernels are often templated (`foo_kernel<8, 256>`) and ncu's `-k "regex:..."` needs to match the *demangled* name.
2. **Which workload / input shape?** If the kernel takes variable-sized inputs, pick a **specific** real workload — don't invent shapes. If the user has multiple representative shapes, profile the hottest one first; profile others only if the first reveals nothing.
3. **Which dispatch path?** Many production kernels branch on input shape or other runtime values to pick different grid configs or template instantiations. Profile each *active* dispatch path separately — treating them as one kernel will average out the real patterns.
4. **What question am I answering?** "Why is this slow?" is too vague. Better: "At shape X, is the kernel latency-bound or bandwidth-bound?" or "We spent 2 weeks on optimization Y — did it actually help?"
5. **What is the baseline?** If there's a reference implementation (torch, cuBLAS, a previous version), profile it too for comparison.

If any of 1-4 are unclear, **ask the user** before profiling. Profiling the wrong thing wastes an hour.

---

## Phase 1 — Environment check

```bash
# 1. ncu CLI is available
ncu --version   # expect: NVIDIA (R) Nsight Compute Command Line Profiler 2026.1.x or newer

# 2. GPU is visible
nvidia-smi      # confirm the GPU model and driver version

# 3. CUDA compiler is available
nvcc --version  # CUDA Toolkit, used for -lineinfo builds

# 4. ncu_report Python module path (needed for parsing reports)
find /usr/local/cuda* -name "ncu_report*" -type f 2>/dev/null
# Typical: /usr/local/cuda-XX.X/nsight-compute-YYYY.X.0/extras/python/ncu_report.py

# 5. Permissions. On a clean server, ncu usually works without sudo because
#    RestrictProfilingToAdminUsers is 0 by default. If you see ERR_NVGPUCTRPERM,
#    see 09-common-issues.md.
```

Put `ncu_report` on `$PYTHONPATH` so scripts work:
```bash
export PYTHONPATH=$PYTHONPATH:/usr/local/cuda-XX.X/nsight-compute-YYYY.X.0/extras/python
python3 -c "import ncu_report; print('OK')"
```

Also set a writable `HOME` before running ncu to silence the "Could not deploy stock section files" warning:
```bash
export HOME=/some/writable/dir   # or just use your normal $HOME
```

---

## Phase 2 — Build a profile target

**Option A (preferred): standalone harness.** Build a small C++ driver that launches your kernel directly. See [`02-harness-guide.md`](02-harness-guide.md). This is the right choice when:

- The kernel lives inside a JIT/template build system (TVM-FFI, PyTorch inline, Triton, CUTLASS JIT) where you can't easily add `-lineinfo`.
- You want fast iteration — the harness compiles in < 5 seconds, vs minutes for rebuilding the whole framework.
- You want precise control over inputs (e.g., load specific workload tensors from the dataset).

**Option B: profile through existing binary.** Skip the harness if:

- The build system already compiles with `-lineinfo` (check the nvcc command line).
- You *need* to profile in-context (e.g., kernel interacts with other kernels, host-side CPU work matters).

Either way, **make sure `-lineinfo` is in the nvcc command**. Without it, source-level analysis won't work.

**Tile kernel variant (CUDA 13.3+):** If the kernel uses `__tile_global__` / `cuda::tiles`, the compilation command changes:
```bash
nvcc -std=c++20 -arch=sm_120 --enable-tile -lineinfo -O3 -o my_tile_kernel my_tile_kernel.cu
```
Critical differences from SIMT:
- `--enable-tile` is **required** — without it, tile annotations are silently ignored and the kernel compiles as an empty stub
- `-std=c++20` is required (tile API uses C++20 concepts)
- Launch syntax: `kernel<<<grid>>>()` (single chevron argument, no threads-per-block)
- The compiler chooses the thread count per block — you cannot control it directly

See `blackwell-cuda-programming.md` § Tile Kernel Programming Model for the full API reference.

---

## Phase 2.5 — Framework kernel identification (when source is unavailable)

**Use this phase when profiling kernels from LLM inference frameworks** (TensorRT-LLM, vLLM, PyTorch) where you don't have access to the kernel source code and can't build a standalone harness.

### When this applies

- Profiling production inference workloads running through TensorRT-LLM or vLLM
- Analyzing `torch.compile`-generated or Triton-JIT-compiled kernels
- Any scenario where the kernel binary exists but source is unavailable or impractical to extract

### Step 1: Identify the target kernel

You need the exact kernel name before profiling. Methods:

**Via Nsight Systems (recommended for framework workloads):**
```bash
nsys profile -o timeline ./run_inference.py
nsys stats timeline.nsys-rep --report cuda_gpu_kern_sum
# Lists all kernels ranked by total GPU time — pick the hottest
```

**Via cuobjdump (for compiled binaries):**
```bash
cuobjdump --dump-function-names /path/to/compiled.so
# For TensorRT-LLM: check the engine .so or the TRT runtime library
```

**Framework-specific kernel naming patterns:**
- **TensorRT-LLM:** fused kernels often named `tensorrt_llm::kernels::*` or `cutlass::*`. Multi-head attention variants use names like `fmha_*` or `flash_*`.
- **vLLM:** uses a mix of Triton-compiled kernels (names like `triton_*` with hash suffixes) and CUDA kernels (from FlashInfer, FlashAttention, or custom CUDA).
- **PyTorch `torch.compile`:** generates Triton kernels with names like `triton_poi_fused_*_0` — these names change between runs. Use `TORCH_COMPILE_DEBUG=1` to dump generated code.
- **Triton JIT:** kernel names include a hash that changes when the source or config changes. Profile a single run; don't expect name stability across runs.

### Step 2: Profile without source

Without `-lineinfo` in the compile flags, per-line stall attribution is unavailable. Collect only `--set full` (skip `--set source`):

```bash
ncu --set full \
    --section PmSampling --section PmSampling_WarpStates \
    -k "regex:YOUR_KERNEL_NAME" \
    -c 1 \
    -o $PROFILE_RUN_DIR/reports/full_<tag> \
    ./run_inference [args]
```

### What you can still analyze

| Analysis | Available? | Notes |
|---|---|---|
| SM throughput / DRAM throughput | Yes | SOL metrics work without source |
| Occupancy & launch geometry | Yes | Grid/block sizes, register/shared-mem limits |
| Aggregate stall breakdown | Yes | Which stall reasons dominate |
| Tensor core utilization | Yes | Whether tensor cores are being used and which sub-pipe |
| PM sampling timeline | Yes | Tail effect, pipeline bubbles |
| Memory access patterns | Yes | Coalescing quality, L1/L2 hit rates |
| Per-source-line stall hotspots | **No** | Requires `-lineinfo` at compile time |
| SASS instruction attribution | **No** | Requires `-lineinfo` |

### What to do with the results

Without per-line attribution, focus on aggregate diagnosis:
- Use the six-dimension framework (05-analysis-dimensions.md) — all six dimensions work with aggregate metrics.
- Use the diagnosis playbook (06-diagnosis-playbook.md) — most patterns use aggregate signals.
- Map findings to **framework-level configuration** rather than code changes: batch size, quantization settings, attention implementation choice, context length limits.

### Framework-specific action mapping

Use this table to translate ncu profiling findings into framework-level configuration changes. Each row maps an observed profiling signal to the most likely fix in each framework.

| ncu Finding | TensorRT-LLM | vLLM | PyTorch |
|---|---|---|---|
| Low tensor core utilization (`sm__pipe_tensor_cycles_active` < 20%) | Enable FP8 quantization (`--dtype fp8`); check `quantize.py` config | Set `--quantization fp8` or `awq`; verify with `--enforce-eager` off | Use `torch.compile(mode="max-autotune")`; set `dtype=torch.bfloat16` |
| DRAM BW saturated (`dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed` > 70%) | Reduce KV-cache precision (`--kv_cache_dtype fp8`); enable paged KV cache | Tune `--block-size`; enable prefix caching (`--enable-prefix-caching`) | Reduce context length; use FlashAttention (`attn_implementation="flash_attention_2"`) |
| Small grid / low occupancy (`launch__grid_size` < 170) | Increase `max_batch_size`; check tensor parallelism config (TP splits work across GPUs) | Increase `--max-num-seqs`; tune `--max-model-len` | Increase batch size; use `torch.compile` for kernel fusion |
| Register spill (`launch__registers_per_thread` > 128, local memory > 0) | Report to framework team — compiled engine kernels can't be tuned | Same — Triton JIT kernels auto-tune register usage | Check `torch.compile` `fullgraph=True` mode; try `TORCH_COMPILE_MAX_REG=128` |
| High `long_scoreboard` stalls (> 40%) | Normal for decode; reduce memory traffic via quantization or KV-cache optimization | Normal for decode; try `--quantization fp8` to halve memory reads | Normal for decode; enable `torch.backends.cuda.flash_sdp_enabled()` |
| Warp divergence (`smsp__thread_inst_executed_pred_on_per_inst_executed.ratio` < 0.8) | Check attention masking config; variable-length inputs cause divergence in fused kernels | Check `--max-model-len` alignment; ragged batching increases divergence | Use `torch.nn.utils.rnn.pad_sequence` to avoid divergent attention masks |
| L2 hit rate very low (`lts__t_sector_hit_rate.pct` < 20%) on repeated inference | Enable persistent L2 via `cudaCtxResetPersistingL2Cache` between requests; pin hot KV-cache lines | Not directly configurable — framework manages L2 | Use `torch.cuda.memory.CUDAPluggableAllocator` for cache-aware allocation |
| PM sampling shows tail effect (uneven SM utilization over time) | Check `max_batch_size` alignment with TP degree; ensure grid fills all 170 SMs | Tune `--max-num-seqs` to avoid partial waves; check scheduler config | Use `torch.compile` with `dynamic=False` for consistent grid sizes |

### RTX 5090 VRAM budget planning

The RTX 5090 has ~31.4 GB usable VRAM. This constrains which models fit and at what precision.

**Model memory estimation:**
```
model_bytes = num_params × bytes_per_param
kv_cache_bytes = 2 × num_layers × num_kv_heads × head_dim × max_seq_len × batch_size × bytes_per_element
total = model_bytes + kv_cache_bytes + activation_overhead (~10-20%)
```

**Example budgets (approximate, single-user decode):**

| Model | FP16 (2B/param) | FP8 (1B/param) | INT4 (0.5B/param) | Fits in 32 GB? |
|---|---|---|---|---|
| LLaMA-3 8B | 16 GB + KV | 8 GB + KV | 4 GB + KV | FP16: yes (short ctx). FP8/INT4: yes |
| LLaMA-3 13B | 26 GB + KV | 13 GB + KV | 6.5 GB + KV | FP16: barely (no KV room). FP8: yes. INT4: yes |
| LLaMA-3 70B | 140 GB | 70 GB | 35 GB | No — even INT4 doesn't fit. Use offloading or smaller model |

**KV-cache budget for a 8B model (32 layers, 8 KV heads, head_dim=128):**
- Per token: `2 × 32 × 8 × 128 = 65,536 bytes` (FP16) = 64 KB/token
- At 4K context: 256 MB. At 32K context: 2 GB. At 128K context: 8 GB.

**When you'll OOM and what to do:**
1. Reduce `max_seq_len` / `max_model_len` — direct KV-cache savings.
2. Quantize KV-cache to FP8 (`--kv_cache_dtype fp8`) — halves KV memory.
3. Lower model precision (FP16 → FP8 → INT4) — reduces model weight memory.
4. Enable CPU offloading (`--cpu-offload-gb` in vLLM) — trades latency for capacity.
5. Use a smaller model — often the right answer for single-GPU deployment.

### Expanded kernel naming patterns

Use kernel names to identify what a kernel does before profiling. This helps prioritize which kernels to investigate.

| Framework | Kernel Name Pattern | Likely Operation | Notes |
|---|---|---|---|
| **TensorRT-LLM** | `tensorrt_llm::kernels::fmha_*` | Flash/fused multi-head attention | Multiple variants for different head sizes and sequence lengths |
| | `cutlass::*gemm*` | GEMM (linear layers) | CUTLASS templates; precision encoded in type parameters |
| | `tensorrt_llm::kernels::quantize*` | Quantization/dequantization | Pre/post-processing for quantized inference |
| | `tensorrt_llm::kernels::apply_*` | Activation functions, RoPE, RMS norm | Fused elementwise kernels |
| | `void fused_*` | Fused multi-op kernels | TRT compiler-generated fusions |
| **vLLM** | `triton_*` + hash suffix | Triton JIT-compiled kernel | Hash changes between runs — profile a single run |
| | `flashinfer::*` or `FlashInfer*` | FlashInfer attention | Used when FlashInfer backend is selected |
| | `flash_fwd_*` or `flash_bwd_*` | FlashAttention | Forward/backward attention kernels |
| | `void paged_attention_*` | Paged attention (vLLM-native) | Core decode attention implementation |
| | `void reshape_and_cache*` | KV-cache update | Writing new KV entries into paged blocks |
| **PyTorch** | `triton_poi_fused_*_N` | `torch.compile` fused pointwise | N is a counter; names change between compilations |
| | `triton_red_fused_*_N` | `torch.compile` fused reduction | Same naming pattern as pointwise |
| | `at::native::*` | Eager-mode ATen kernels | Standard PyTorch ops, not compiled |
| | `cutlass::*` or `cublas*` | GEMM via cuBLAS/CUTLASS | PyTorch delegates to vendor BLAS |
| | `void at_cuda_detail::cub::*` | CUB-based reductions, scans | Sort, topk, cumsum operations |

**Identifying kernel type from the name:**
- **Attention kernels:** look for `fmha`, `flash`, `attention`, `sdpa`, `mha` in the name.
- **GEMM / linear layers:** look for `gemm`, `gemv`, `cutlass`, `cublas`, `matmul`.
- **Elementwise / fused:** look for `fused`, `pointwise`, `poi`, `elementwise`, `apply`.
- **Quantization:** look for `quantize`, `dequant`, `scale`, `cast`.
- **KV-cache:** look for `cache`, `reshape_and_cache`, `paged`.

---

## Phase 3 — Collect profiles

Run two ncu invocations — **both outputs go under `$PROFILE_RUN_DIR/reports/`**. Details in [`03-collection.md`](03-collection.md).

```bash
# (1) Overview — all sections + PM sampling
ncu --set full \
    --section PmSampling --section PmSampling_WarpStates \
    -k "regex:YOUR_KERNEL_NAME" \
    -c 1 \
    -o "$PROFILE_RUN_DIR/reports/full_<tag>" \
    "$PROFILE_RUN_DIR/harness/your_harness" [args]

# (2) Source-level — per-PC stall sampling
ncu --set source --section SourceCounters \
    -k "regex:YOUR_KERNEL_NAME" \
    -c 1 \
    -o "$PROFILE_RUN_DIR/reports/source_<tag>" \
    "$PROFILE_RUN_DIR/harness/your_harness" [args]
```

Run the pair once per (kernel, dispatch path, representative workload) combination.

Each `--set full` run takes ~30-60 seconds with many replay passes. Each `--set source` run takes 5-10 seconds. Plan your time budget.

**Tile kernel collection note:** The same `--set full` and `--set source` flags work for tile kernels — no special sections needed. On RTX 5090, tile kernel profiling produces 2383 metrics across 41 passes, identical to SIMT. All six analysis dimensions produce meaningful data for tile kernels.

---

## Phase 4 — Extract structured data

Do not eyeball the CLI output. Parse reports in Python so you can compare, aggregate, and archive. See [`04-python-api.md`](04-python-api.md) and use the helpers in [`../helpers/`](../helpers/).

Minimum analysis artifacts to produce:

| Artifact | Tool | What it tells you |
|---|---|---|
| `metrics_key_<tag>.txt` | `analyze_reports.py` | ~90 curated metrics (launch geom, SOL, occupancy, stalls, sectors) |
| `metrics_all_<tag>.json` | `analyze_reports.py` | Full 2000+ metrics, archive for later |
| `compare_<a>_vs_<b>.txt` | `analyze_reports.py` | Side-by-side metric comparison between workloads / versions |
| `stall_hotspots_<tag>.txt` | `extract_stall_hotspots.py` | Top source lines ranked by stall samples |
| `pm_timeline_plots.txt` | `plot_timeline.py` | ASCII time-series plots — reveals tail effect visually |
| `details_<tag>.txt` | `ncu --import ... --page details` | NCU's built-in rule-based suggestions (each with `Est. Speedup: X%`) |

Save everything under `$PROFILE_RUN_DIR/analysis/`. The user will want to re-inspect these; if two runs mix artifacts, you've already failed.

---

## Phase 5 — Diagnose

Work through the six analysis dimensions — see [`05-analysis-dimensions.md`](05-analysis-dimensions.md):

1. **SM occupancy & wave structure** — are enough blocks launched to fill the chip? Is occupancy register- / shared-mem- / block-limited?
2. **Thread-block balance (tail effect)** — do per-SM active cycles match? Does the PM timeline show a clean drop or a gradual tail?
3. **Instruction-level stall analysis** — what stall reason dominates? Which source line generates it?
4. **Tensor Core utilization** — if this is a GEMM-ish kernel, are tensor cores actually being used?
5. **SM utilization timeline** — flat high, flat low, periodic waves, gradual tail?
6. **Memory access pattern** — sectors/request, L1/L2 hit rates, DRAM throughput, register spill.

For each dimension, write down the observed signal *and the specific metric value* that produced it. "Kernel is memory bound" is useless; something like "`dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed = X%` (well below peak) shows the kernel is *not* DRAM-bandwidth-bound — the `long_scoreboard` stall rate of Y% says it's latency-bound on L1" is diagnosis. Fill in X and Y from your own report.

Then consult [`06-diagnosis-playbook.md`](06-diagnosis-playbook.md) which maps observed patterns to likely causes and concrete fixes. **For tile kernels** (`__tile_global__`), also check the tile-specific diagnosis patterns (Patterns R–U) in the playbook, which cover tile occupancy, partition_view vs gather, ct::mma utilization, and atomic contention.

---

## Phase 6 — Write the report

Structure described in [`07-report-template.md`](07-report-template.md). Key elements:

1. **Setup section**: exactly how you profiled (harness path, workloads, ncu commands, metric-name caveats). Required for reproducibility.
2. **Headline numbers**: duration, SM throughput, DRAM throughput, occupancy, tensor core usage. A table on the first page.
3. **Per-dimension analysis** with evidence (metric values + NCU rule text).
4. **Optimization directions** ranked by expected impact (use NCU's `Est. Speedup: X%` when available — these are surprisingly accurate).
5. **Confidence & caveats**.

Keep the report short enough that a busy reader can see the top 3 findings in 30 seconds. Put deep detail in the artifacts, not the prose.

---

## Anti-patterns to avoid

- ❌ **"I ran ncu and it says memory throughput is 14%"** — without naming the metric, workload, and kernel, this is un-actionable. Always give metric + value + what it means.
- ❌ **Profiling with synthetic shapes that don't match real workloads.** A uniform-element batch is a very different problem than a batch with highly skewed per-element work (the latter exposes tail effects the former hides). If the production workload has imbalance, you must profile on an imbalanced workload.
- ❌ **Dumping the full NCU CLI output into the report.** It's noisy, narrow-formatted, and has no interpretation. Extract the numbers, cite the source, add your reading.
- ❌ **Proposing optimizations without evidence.** "Maybe we should use shared memory" is not a profiling result. A real proposal cites a specific source line, its stall-sample count, the relevant NCU rule's `Est. Speedup`, and the mechanism of the fix — e.g. "line L's global-load instruction accounts for N% of `long_scoreboard` samples; NCU reports the access pattern is non-coalesced with M% excess sectors; reshaping the per-thread index from stride-K to contiguous should eliminate most of those stalls."
- ❌ **Missing the #1 finding because you got distracted by a smaller one.** Rank findings by impact. Tail effects and SM idle time often dwarf coalescing issues; fix the big one first.
