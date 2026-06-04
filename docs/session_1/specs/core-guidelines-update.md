# Specification: Core Guidelines Update

Covers capabilities M-1 (Core Guidelines), M-2 (Special Kernel Types), M-3 (Pre-Coding Checklist).

---

## MODIFIED Requirements

### Requirement: Guidelines Hardware Numbers

All 16 core guidelines SHALL use RTX 5090 hardware numbers. The following substitutions MUST be applied throughout:

| B200 Value | RTX 5090 Value |
|---|---|
| 148 SMs | 170 SMs |
| 64 warps/SM | 48 warps/SM |
| 32 blocks/SM | 24 blocks/SM |
| 228 KB shared/SM | 100 KB shared/SM |
| 227 KB shared/block | 99 KB opt-in max/block, 48 KB default |
| 8 TB/s bandwidth | ~1.8 TB/s bandwidth |
| 126 MB L2 | 96 MB L2 |
| 192 GB HBM | 32 GB GDDR7 |
| sm_100a | sm_120a |

#### Scenario: Guideline 1 — occupancy limits
WHEN Guideline 1 (sufficient parallelism) is read
THEN active warps reference uses 48 warps/SM (not 64).

#### Scenario: Guideline 3 — shared memory capacity
WHEN Guideline 3 (shared memory) exception text mentions shared memory capacity
THEN it references 100 KB/SM (not 228 KB).

#### Scenario: Guideline 6 — register pressure
WHEN Guideline 6 mentions registers per SM
THEN it uses 65,536 registers (same as B200, verified on RTX 5090).

#### Scenario: Guideline 11 — grid/block config
WHEN Guideline 11 mentions SM count for wave size calculation
THEN it uses 170 SMs (not 148).

### Requirement: Guidelines Language

All 16 guidelines SHALL be written in English (currently in Chinese).

#### Scenario: No Chinese text in guidelines
WHEN the guidelines section is searched for CJK characters
THEN zero matches are found.

### Requirement: Special Kernel Types — LLM Decode

The "Special Kernel Types" section SHALL update the LLM Decode Attention entry to reference RTX 5090 bandwidth constraints (~1.8 TB/s) and VRAM limits (32 GB).

#### Scenario: LLM decode references RTX 5090
WHEN the LLM Decode Attention entry is read
THEN it mentions ~1.8 TB/s bandwidth as the memory-bound ceiling and the much higher memory-boundedness compared to data-center GPUs.

### Requirement: Pre-Coding Checklist

The pre-coding checklist SHALL be updated to remove items referencing tcgen05, TMEM, and 2CTA, and add items for mma.sync and GDDR7-specific considerations.

#### Scenario: No tcgen05 in checklist
WHEN the checklist is searched for "tcgen05", "TMEM", "2CTA", "cta_group"
THEN zero matches are found.

#### Scenario: sm_120a compile target in checklist
WHEN the checklist's first item (compile target) is read
THEN it asks "Is the compile target `-arch=sm_120a`?"

#### Scenario: SM count in checklist
WHEN the checklist mentions filling all SMs
THEN it references 170 SMs (not 148).
