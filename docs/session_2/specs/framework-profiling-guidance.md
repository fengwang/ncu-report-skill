# Spec: Framework Kernel Profiling Guidance (NC-2)

## ADDED Requirements

### Requirement: Phase 2.5 — Framework Kernel Identification

The workflow document (`01-workflow.md`) SHALL include a new Phase 2.5 section between Phase 2 (Build) and Phase 3 (Collect) for profiling framework kernels where source code is unavailable.

The section SHALL cover:
- When this phase applies: profiling TensorRT-LLM, vLLM, PyTorch compiled kernels
- Kernel identification methods: `torch.profiler`, `nsys`, `cuobjdump --dump-function-names`
- What analysis is still possible without `-lineinfo` (aggregate metrics: yes; per-line stalls: no)
- How to use `--set full` without `--set source` when source is unavailable
- Framework-specific kernel naming patterns (Triton JIT names, TensorRT fused kernel names)

#### Scenario: User profiles TensorRT-LLM kernel
WHEN a user wants to profile a kernel from TensorRT-LLM where they have no source access
THEN Phase 2.5 SHALL guide them to identify the kernel via `nsys` or `cuobjdump`, profile with `--set full` only, and interpret aggregate metrics without per-line attribution

#### Scenario: User profiles vLLM kernel
WHEN a user profiles a vLLM inference workload
THEN Phase 2.5 SHALL note that vLLM uses a mix of Triton-compiled and CUDA kernels, and guide identification of which kernel type is in use

#### Scenario: User profiles PyTorch compiled kernel
WHEN a user profiles a `torch.compile`-generated kernel
THEN Phase 2.5 SHALL guide them to use `TORCH_COMPILE_DEBUG=1` to find generated code, and note that Triton kernels have dynamic names across runs
