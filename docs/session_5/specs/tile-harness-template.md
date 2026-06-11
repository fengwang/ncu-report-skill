# Spec: NC-8 — Tile Kernel Harness Template Variant

## MODIFIED Requirements

### Requirement: Tile kernel section in harness template
helpers/harness_template.cu SHALL contain a tile kernel variant section.

#### Scenario: Tile section exists
WHEN harness_template.cu is read
THEN it SHALL contain a `#if 0` / `#endif` guarded section with a tile kernel example
AND a comment SHALL explain how to enable the tile path (change `#if 0` to `#if 1`)

#### Scenario: Tile kernel includes
WHEN the tile section is read
THEN it SHALL include `#include <cuda_tile.h>` inside the guarded section

#### Scenario: Tile launch syntax
WHEN the tile section is read
THEN the launch SHALL use `kernel<<<blocks, 1>>>` pattern

#### Scenario: SIMT section unchanged
WHEN the existing SIMT kernel stub (outside the `#if 0` guard) is read
THEN it SHALL be identical to the pre-Session-5 version

### Requirement: Harness backward compatibility
The harness template SHALL compile as a SIMT harness by default (tile section disabled).

#### Scenario: Default compilation
WHEN harness_template.cu is compiled with `nvcc -arch=sm_120` without modifications
THEN it SHALL compile with the same behavior as before Session 5
