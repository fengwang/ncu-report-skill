# Specification: RTX 5090 Hardware Specs

Covers capabilities N-1 (RTX 5090 Hardware Specs) and M-4 (SKILL.md Frontmatter & Specs).

---

## ADDED Requirements

### Requirement: RTX 5090 Hardware Parameter Table

The programming guide SHALL contain a single-column hardware parameter table with all values matching PRD §4.1 verified specs. The table SHALL include: SM count, max warps/SM, max blocks/SM, max threads/SM, shared memory/SM, shared memory opt-in max/block, registers/SM, L2 cache, persistent L2 max, memory bus width, global memory, memory bandwidth, CUDA cores, Tensor Cores, boost clock, and TDP.

#### Scenario: Table values match verified specs
WHEN the hardware parameter table is read
THEN every numeric value matches the corresponding value in PRD §4.1 (cudaDeviceProp verified column).

#### Scenario: No B200 values in table
WHEN the hardware parameter table is searched for B200-specific values (148, 228, 227, 64 warps/SM, 32 blocks/SM, 8 TB/s, 126 MB, 192 GB)
THEN zero matches are found.

### Requirement: SKILL.md Hardware Description

SKILL.md frontmatter `description` field SHALL reference RTX 5090 and sm_120. The headline hardware line SHALL state RTX 5090 (sm_120, CC 12.0, 170 SMs, 32 GB GDDR7).

#### Scenario: SKILL.md frontmatter accuracy
WHEN `grep -i 'sm_120' SKILL.md` is run
THEN at least one match is found in the frontmatter description.

#### Scenario: SKILL.md headline specs
WHEN the "Target hardware" line in SKILL.md is read
THEN it references RTX 5090, sm_120, CC 12.0, 170 SMs, and 32 GB GDDR7.

## MODIFIED Requirements

### Requirement: Compile Target

All compilation examples SHALL use `-arch=sm_120a`. No references to `sm_100`, `sm_100a`, `compute_100`, or `compute_100a` SHALL remain.

#### Scenario: Compile target in programming guide
WHEN `grep -i 'sm_1' blackwell-cuda-programming.md` is run
THEN all matches contain `sm_120` (not sm_100).

#### Scenario: Compile target in SKILL.md
WHEN `grep -i 'sm_1' SKILL.md` is run
THEN all matches contain `sm_120` (not sm_100).

## REMOVED Requirements

### Requirement: B200 Hardware References

All references to B200, sm_100, HBM3e, 148 SMs, 228 KB shared memory, 8 TB/s bandwidth, 126 MB L2, and 192 GB VRAM SHALL be removed from SKILL.md, blackwell-cuda-programming.md, and README.md.

**Reason:** B200 backward compatibility is explicitly not required (PRD §8, NFR-4).
**Migration:** All values replaced with RTX 5090 equivalents.

#### Scenario: Zero B200 references
WHEN `grep -ri 'sm_100\|B200\|b200' SKILL.md blackwell-cuda-programming.md README.md` is run
THEN the output is empty.
