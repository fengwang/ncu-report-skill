# Specification: GDDR7 Memory Strategy

Covers capability N-3 (GDDR7 Memory Strategy).

---

## ADDED Requirements

### Requirement: Memory Hierarchy Section

The programming guide SHALL contain a "Memory Hierarchy" section covering the RTX 5090's GDDR7-based memory system.

#### Scenario: GDDR7 bandwidth documented
WHEN the Memory Hierarchy section is read
THEN it states the theoretical peak bandwidth as ~1,792 GB/s (derived: 28 Gbps × 512-bit bus / 8) and notes effective bandwidth is typically 85-90% of theoretical.

#### Scenario: L2 cache documented
WHEN the Memory Hierarchy section is read
THEN it states L2 cache size as 96 MB and persistent L2 max as 60 MB.

#### Scenario: Shared memory documented
WHEN the Memory Hierarchy section is read
THEN it states: 100 KB/SM total, 48 KB/block default, 99 KB/block opt-in max (via `cudaFuncSetAttribute`), with 1 KB reserved per block by the runtime.

#### Scenario: VRAM constraint documented
WHEN the Memory Hierarchy section is read
THEN it states global memory as ~31.4 GB (marketed as 32 GB) and discusses implications for model/data sizing.

#### Scenario: No HBM references
WHEN `grep -i 'HBM' blackwell-cuda-programming.md` is run
THEN the output is empty.
