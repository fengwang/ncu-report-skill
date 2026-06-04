# Session 4 Sharded Review

**Date:** 2026-06-04

## Reviewers

| Reviewer | Focus | Result |
|---|---|---|
| Correctness | DRAM renames, hardware numbers, throughput values, G-4/G-7 results | Pass (3 findings fixed) |
| Security/Safety | Command injection, sudo, hardcoded paths, GPU damage | Pass (0 findings) |
| Architecture | Invariants, structure, duplication, checklist integration | Pass (1 finding fixed) |
| Adversarial Verifier | Falsify all 6 done-condition claims | Pass (all claims hold) |

## Findings

### Fixed (Critical/High/Medium)

| ID | Severity | File | Finding | Fix |
|---|---|---|---|---|
| C-1 | High | reference/09-common-issues.md:257 | G-4 text claimed RTX 5090 cluster max of 8 "matches" data-center max of 16 — it does not | Corrected to state data-center supports 16, RTX 5090 supports 8 |
| C-2 | Medium | reference/08-rtx5090-metric-names.md:3,5,17 | Stale "unverified" preamble contradicted the now-validated body | Updated to "Validated on RTX 5090 with ncu 2026.2" |
| C-3 | Low | blackwell-cuda-programming.md:70 | Cluster column said "Available" without the validated limit | Changed to "Up to 8 (validated)" |
| A-1 | Low | reference/04-python-api.md:77 | PM sampling example changed metric but lacked clarifying comment | Added "sm_120 hardware-counter timeseries" comment |

### Not Fixed (Nit / Deferred)

| ID | Severity | File | Finding | Reason |
|---|---|---|---|---|
| A-2 | Low | blackwell-cuda-programming.md | TFLOPS peaks repeated in precision recipes vs earlier roofline table | Acceptable — self-contained recipes are more usable than cross-references |
