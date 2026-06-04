# Specification: LLM Inference Profiling Section

Covers capability N-6 (LLM Inference Section).

---

## ADDED Requirements

### Requirement: LLM Inference Section Exists

The programming guide SHALL contain a section titled "LLM Inference Profiling" focused on profiling single-user, low-latency autoregressive decode on RTX 5090.

#### Scenario: Section heading present
WHEN `grep -i 'LLM Inference' blackwell-cuda-programming.md` is run
THEN at least one match is found as a section heading.

### Requirement: Decode Bandwidth Analysis

The LLM section SHALL explain why single-token autoregressive decode is deeply memory-bandwidth-bound on RTX 5090, with specific reference to the ~1.8 TB/s bandwidth ceiling.

#### Scenario: Bandwidth-bound explanation
WHEN the decode analysis subsection is read
THEN it explains that decode arithmetic intensity is well below every precision's roofline breakpoint, making it memory-bandwidth-bound, and references ~1.8 TB/s as the RTX 5090 ceiling.

### Requirement: KV-Cache Sizing

The LLM section SHALL include KV-cache memory budget guidance within 32 GB VRAM, with a formula or sizing table showing context length limits per model size and precision.

#### Scenario: KV-cache formula present
WHEN the KV-cache subsection is read
THEN it contains a formula: `KV_bytes = 2 × num_layers × num_kv_heads × head_dim × context_length × bytes_per_element` (or equivalent) and at least one worked example showing how many tokens fit in 32 GB for a specific model configuration.

### Requirement: Quantization Strategy

The LLM section SHALL discuss quantization impact on decode throughput, covering FP4, FP8, INT8, and BF16 with bytes-per-parameter comparisons.

#### Scenario: Precision comparison for decode
WHEN the quantization subsection is read
THEN it contains a comparison of bytes/parameter and estimated tokens/second improvement for each precision level (FP4, FP8, INT8, BF16), noting that lower precision reduces memory traffic proportionally.

### Requirement: RTX 5090-Specific Constraints

All LLM guidance SHALL reference RTX 5090-specific constraints (32 GB VRAM, ~1.8 TB/s bandwidth, 170 SMs).

#### Scenario: No generic LLM advice
WHEN the LLM section is reviewed
THEN every performance claim includes RTX 5090 bandwidth (~1.8 TB/s) or VRAM (32 GB) as a concrete reference point, not generic statements.
