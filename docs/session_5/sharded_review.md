# Session 5 Sharded Review

## Findings

| # | Severity | Axis | Finding | Fix | Status |
|---|---|---|---|---|---|
| 1 | High | Correctness | Pattern S fabricated "2× gather comparison" — no gather kernel was profiled | Replaced with honest caveat noting the comparison was not run | Fixed |
| 2 | Medium | Correctness | TMA validation confirms hardware presence only, not compiler lowering | Added caveats in programming guide and metric reference | Fixed |
| 3 | Medium | Performance | Rule-of-thumb guidance missing sm_80+ architecture requirement | Added "(requires sm_80+; sm_90+ for TMA)" to the sentence | Fixed |
| 4 | Low | Correctness | Metric name inconsistency (per_cycle_active vs pct_of_peak_sustained_active) | Changed to pct form consistent with rest of codebase | Fixed |

## Security
No new attack surface — documentation-only changes.

## Architecture
Six-dimension framework preserved. Tile additions are strictly additive. Pattern→cause→fix structure maintained in all 4 new patterns.
