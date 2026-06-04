# Specification: framework-action-mapping

## ADDED Requirements

### Requirement: Framework-specific action mapping table in workflow

`reference/01-workflow.md` Phase 2.5 SHALL contain a table mapping ncu profiling findings to framework-level configuration changes for TensorRT-LLM, vLLM, and PyTorch.

#### Scenario: Action mapping table exists
WHEN Phase 2.5 of `reference/01-workflow.md` is reviewed
THEN it SHALL contain a table with columns for ncu finding, TensorRT-LLM action, vLLM action, and PyTorch action

#### Scenario: Table covers common findings
WHEN the action mapping table is reviewed
THEN it SHALL include rows for at least: low tensor core utilization, DRAM bandwidth saturation, small grid / low occupancy, and register spill

#### Scenario: Actions are framework-specific
WHEN any row in the action mapping table is reviewed
THEN the actions SHALL reference framework-specific configuration knobs (e.g., `--quantization` for vLLM, not generic advice)

### Requirement: RTX 5090 VRAM budget planning

`reference/01-workflow.md` Phase 2.5 SHALL contain VRAM budget guidance for RTX 5090's 32 GB.

#### Scenario: VRAM budget section exists
WHEN Phase 2.5 is reviewed
THEN it SHALL contain model size estimation formulas and example budgets for common model sizes (7B, 13B, 70B) at different precisions

#### Scenario: 32 GB constraint referenced
WHEN the VRAM section is reviewed
THEN it SHALL explicitly reference RTX 5090's ~31.4 GB usable VRAM and OOM mitigation strategies

### Requirement: Expanded kernel naming patterns

`reference/01-workflow.md` Phase 2.5 SHALL expand the existing kernel naming bullet list into a more complete reference.

#### Scenario: Kernel naming covers all three frameworks
WHEN the kernel naming section is reviewed
THEN it SHALL cover TensorRT-LLM, vLLM, and PyTorch kernel naming patterns with enough detail to identify kernel type (attention, GEMM, elementwise) from the name
