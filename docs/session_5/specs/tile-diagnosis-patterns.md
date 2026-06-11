# Spec: NC-4 — Tile Kernel Diagnosis Patterns

## ADDED Requirements

### Requirement: Pattern R — Tile kernel low occupancy
A diagnosis pattern for tile kernel occupancy issues SHALL be added to `reference/06-diagnosis-playbook.md`.

#### Scenario: Pattern R structure
WHEN Pattern R is read
THEN it SHALL follow the pattern→cause→fix structure
AND it SHALL describe: the signal (compiler-managed warps below hardware maximum), the cause (tile shape or hint settings limiting occupancy), and the fix (adjust tile dimensions, tune occupancy hint)

#### Scenario: Pattern R metric references
WHEN Pattern R is read
THEN it SHALL reference specific ncu metrics for detecting low occupancy in tile kernels (from validation data)

### Requirement: Pattern S — Partition_view vs gather inefficiency
A diagnosis pattern for suboptimal tile memory access SHALL be added.

#### Scenario: Pattern S structure
WHEN Pattern S is read
THEN it SHALL describe: the signal (high global memory traffic despite tile-level access), the cause (using gather/scatter where partition_view would enable TMA or structured access), and the fix (restructure data layout for partition_view, add assume_aligned)

### Requirement: Pattern T — Tile MMA underutilization
A diagnosis pattern for tensor core underuse in tile kernels SHALL be added.

#### Scenario: Pattern T structure
WHEN Pattern T is read
THEN it SHALL describe: the signal (low tensor core pipe activity when using ct::mma), the cause (tile shape not matching hardware MMA dimensions, precision mismatch), and the fix (align tile dimensions to MMA hardware, check precision compatibility)

### Requirement: Pattern U — Tile atomic contention
A diagnosis pattern for atomic contention in tile kernels SHALL be added.

#### Scenario: Pattern U structure
WHEN Pattern U is read
THEN it SHALL describe: the signal (high atomic stall ratio), the cause (cross-block device-scope atomics on hot addresses), and the fix (use block-scope atomics with final cross-block reduction, restructure to reduce contention)

#### Scenario: At least 4 tile patterns total
WHEN `grep -c 'tile.*kernel\|Tile.*Kernel\|tile.*pattern\|Tile.*Pattern' reference/06-diagnosis-playbook.md` is run
THEN the count SHALL be >= 4

#### Scenario: Atomic contention pattern present
WHEN `grep -c 'atomic.*contention\|atomic.*tile\|tile.*atomic' reference/06-diagnosis-playbook.md` is run
THEN the count SHALL be >= 1
