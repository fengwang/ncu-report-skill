# Specification: sm_120 Architecture Overview

Covers capability N-2 (sm_120 Architecture Overview).

---

## ADDED Requirements

### Requirement: Architecture Overview Section

The programming guide SHALL contain an "Architecture Overview" section that explains the key architectural properties of the RTX 5090 (GB202, sm_120) relevant to kernel development.

#### Scenario: Monolithic die documented
WHEN the Architecture Overview section is read
THEN it states that RTX 5090 uses the monolithic GB202 die (not dual-die like B200's GB100).

#### Scenario: sm_120 vs sm_100 differences documented
WHEN the Architecture Overview section is read
THEN it explicitly lists features available on sm_100 but NOT on sm_120: tcgen05, wgmma, TMEM, CTA pair (2CTA), NVLink.

#### Scenario: Available features documented
WHEN the Architecture Overview section is read
THEN it lists features confirmed available on sm_120: mma.sync, WMMA, cp.async, Thread Block Clusters, sm_120a architecture-specific variant.

### Requirement: No NVLink Content

No NVLink bandwidth claims, multi-GPU guidance, or NV-HBI (inter-die) content SHALL appear in the programming guide.

#### Scenario: Zero NVLink references
WHEN `grep -i 'NVLink\|NV-HBI\|multi-GPU\|multi.die\|dual.die' blackwell-cuda-programming.md` is run
THEN the output is empty (except in the architecture overview's "not available" list).

### Requirement: No Data-Center-Only Feature Sections

The programming guide SHALL NOT contain sections for: tcgen05 instructions, TMEM (Tensor Memory), CTA Pair / 2CTA, or hardware decompression engine.

#### Scenario: No tcgen05 section
WHEN the programming guide table of contents is scanned
THEN no section titled "tcgen05" or "Tensor Memory" or "CTA Pair" or "2CTA" or "Decompression Engine" exists as a standalone section.
