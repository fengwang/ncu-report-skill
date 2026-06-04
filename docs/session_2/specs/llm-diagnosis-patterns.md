# Spec: LLM Diagnosis Patterns (NC-1)

## ADDED Requirements

### Requirement: Pattern O — Decode Bandwidth Ceiling

The diagnosis playbook SHALL include Pattern O for detecting single-token decode hitting the DRAM bandwidth wall on RTX 5090.

The pattern SHALL include:
- Signal metrics: `dram__bytes_read.sum.pct_of_peak_sustained_elapsed`, `launch__grid_size`, kernel context (batch=1 decode)
- Cause: single-token autoregressive decode is fundamentally memory-bandwidth-bound at ~1.8 TB/s
- Bandwidth context: 4.4x lower than B200, making decode proportionally more memory-bound
- First-line fix: quantize weights and KV-cache (FP16 -> FP8 -> FP4)
- Deeper fixes: speculative decoding, batching, operator fusion
- Exceptions: batched inference (not single-user decode)
- Cross-reference to programming guide's LLM Inference Profiling section

#### Scenario: Decode kernel at bandwidth ceiling
WHEN a kernel profile shows `dram__bytes_read.sum.pct_of_peak_sustained_elapsed` > 80% AND the kernel is identified as a single-token decode operation (small grid, batch=1)
THEN Pattern O SHALL be diagnosed with the ~1.8 TB/s ceiling as context

#### Scenario: Bandwidth-bound but not decode
WHEN `dram__bytes_read.sum.pct_of_peak_sustained_elapsed` > 80% but the kernel is not a decode operation
THEN Pattern O SHALL NOT be diagnosed (use existing Pattern C/E instead)

### Requirement: Pattern P — KV-Cache Thrashing

The diagnosis playbook SHALL include Pattern P for detecting KV-cache exceeding L2 capacity.

The pattern SHALL include:
- Signal metrics: `lts__t_sector_hit_rate.pct`, `dram__bytes_read.sum`, expected KV-cache size estimation formula
- Cause: KV-cache exceeds 96 MB L2 capacity, causing every attention pass to reload from DRAM
- RTX 5090-specific: 96 MB L2, 60 MB persistent L2 max
- First-line fix: quantize KV-cache (FP16 -> FP8/INT8)
- Deeper fixes: persistent L2 partitioning (cudaCtxSetLimit), reduce context length, GQA/MQA
- KV-cache size estimation formula referencing context_length, layers, heads, head_dim, precision

#### Scenario: Low L2 hit rate during attention
WHEN `lts__t_sector_hit_rate.pct` is below 50% during an attention kernel AND estimated KV-cache size exceeds 96 MB
THEN Pattern P SHALL be diagnosed

#### Scenario: L2 miss but small KV-cache
WHEN `lts__t_sector_hit_rate.pct` is low but KV-cache fits within 96 MB
THEN the low hit rate has a different cause (not Pattern P)

### Requirement: Pattern Q — Quantization Mismatch

The diagnosis playbook SHALL include Pattern Q for detecting higher-precision tensor core usage than necessary.

The pattern SHALL include:
- Signal metrics: `sm__pipe_tensor_subpipe_hmma_cycles_active` (FP16/BF16 pipe), absence of lower-precision pipe activity
- Cause: kernel uses FP16/BF16 when FP8 or FP4 tensor cores are available and could provide 2-4x higher throughput
- Per-precision roofline breakpoints from PRD §4.4
- First-line fix: re-quantize model to FP8, enable framework FP8 mode
- Deeper fixes: FP4/NVFP4 quantization (library-only on sm_120)
- Exceptions: accuracy-critical layers, small matrices where quantization overhead exceeds benefit

#### Scenario: FP16 GEMM with available FP8
WHEN a GEMM kernel shows `sm__pipe_tensor_subpipe_hmma_cycles_active` > 0 AND no FP8 tensor pipe activity AND the model supports FP8 quantization
THEN Pattern Q SHALL be diagnosed with FP8 roofline breakpoint comparison

#### Scenario: Already using optimal precision
WHEN tensor cores are active at the lowest viable precision for the workload
THEN Pattern Q SHALL NOT be diagnosed
