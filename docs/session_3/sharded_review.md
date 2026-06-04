# Session 3 Sharded Review Results

## Reviewers

1. **Correctness** — DRAM metric patterns, throughput constants, ncu_report discovery, import consistency
2. **Architecture/Maintainability** — Invariants, function signatures, cross-file consistency
3. **Tests/Validation** — Deterministic checks, gap resolution, metric validation evidence

## Consolidated Findings

### Fixed (Session 3)

| # | Severity | Finding | Fix |
|---|---|---|---|
| C-3 | Medium | `RTX5090_KEY_METRICS` missing 3 pcsamp stall metrics (`tex_throttle`, `sleeping`, `misc`) that `extract_stall_hotspots.py` has | Added the 3 metrics. All confirmed present on sm_120. |

### Deferred (Outside Session 3 Blast Radius)

| # | Severity | Finding | Affected Files | Session |
|---|---|---|---|---|
| C-1 | High | `reference/08-rtx5090-metric-names.md` still has old DRAM names (`dram__bytes_read` instead of `dram__bytes_op_read`) and "unverified" caveat | `reference/08-rtx5090-metric-names.md` | Session 4 |
| C-2 | High | Old DRAM metric names in 10+ reference/doc files | `reference/01,03,04,05,06,07,09`, `blackwell-cuda-programming.md`, `SKILL.md:85` | Session 4 |
| A-3 | Low-Med | PM sampling metric names in reference docs still list old stall-breakdown timeseries | `reference/08-rtx5090-metric-names.md`, `reference/04-python-api.md` | Session 4 |

### Accepted (No Fix Needed)

| # | Severity | Finding | Reason |
|---|---|---|---|
| C-4 | Low | PM sampling `dram__bytes` (aggregate) is different from `dram__bytes_op_read` (per-direction) | Correct — different metric namespaces. Script handles missing metrics gracefully. |
| A-4 | Info | Throughput constants only used for display | Good forward-looking placement. |
| A-5 | Low | `load_action()` may allow premature GC of report | Pre-existing, not Session 3 scope. |
| A-6 | Info | `_locate_ncu_report()` doesn't cover NixOS/snap | PYTHONPATH fallback covers edge cases. |
| A-7 | Info | No backward-compat alias for `B200_KEY_METRICS` | By design per project contract C-4. |
| C-6 | Nit | Comment references `ncu 2026.2` — may become stale | Useful provenance, minor staleness risk. |

## Invariant Verification

| Invariant | Status |
|---|---|
| INV-2: stdlib + ncu_report only | PASS |
| INV-3: Six-dimension framework preserved | PASS |
| Function signatures unchanged | PASS |
| Script argument format unchanged | PASS |
| No B200/sm_100 in helpers/ | PASS |
| Harness targets sm_120 | PASS |

## Deterministic Checks

All 5 session contract checks pass (see tests/validation review for details).
