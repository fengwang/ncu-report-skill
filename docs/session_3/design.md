# Session 3 Design

## Context

The five helper scripts contain B200-specific metric names, hardcoded paths, and sm_100 compile targets. The metric names are the highest-risk item: they're the interface between ncu output and the analysis framework. If metric names silently resolve to zero on sm_120 instead of raising errors, all downstream analysis produces wrong results.

The local environment has RTX 5090 (CC 12.0), CUDA 13.2, ncu 2026.2, and `ncu_report` installed as a system Python package.

## Goals

- All helper scripts target RTX 5090/sm_120 exclusively
- Metric list contains only names confirmed present on sm_120 (or explicitly flagged)
- Evidence gaps G-1, G-2, G-5, G-6, G-8 resolved with hardware evidence
- Scripts maintain existing function signatures and behavior

## Non-Goals

- Adding new analysis features or helper scripts
- Changing the analysis framework structure
- Supporting multiple GPU targets simultaneously

## Decisions

### D1: Metric Validation Procedure

**Chosen**: Write a minimal vector_add kernel to `/tmp`, compile with `sm_120`, profile with `ncu --set full --section PmSampling`, extract metric list via `action.metric_names()`.

**Alternative considered**: Use harness_template.cu directly. Rejected because it's a template with stubs and won't compile without modification. Keeping it as-is preserves its purpose as a user starting point.

### D2: ncu_report Discovery Refactor

**Chosen**: Keep the try/except import pattern. Update `_locate_ncu_report()` to also check for `ncu_report/__init__.py` (package directory) in addition to `ncu_report.py`. Add `/usr/lib/python3.14/site-packages` is not needed — it's already in sys.path. Update the documented path in the docstring.

**Alternative considered**: Remove `_locate_ncu_report()` entirely since the system package works. Rejected because other installations may not have it in site-packages (e.g., standalone ncu installs).

### D3: Throughput Constants in analyze_reports.py

**Chosen**: Add module-level constants `RTX5090_PEAK_BW_GBS = 1792` and `RTX5090_PEAK_FP32_TFLOPS = 104.8` (etc.). Use them in a new display line when printing key metrics. This satisfies the deterministic check (grep for 1792) and provides useful reference data.

**Alternative considered**: Add constants only in comments. Rejected because the deterministic check expects grep-able values, and constants are more useful than comments.

### D4: Stale Reference Fix Scope

**Chosen**: Only change the filename string `08-b200-metric-names.md` → `08-rtx5090-metric-names.md` in SKILL.md and README.md. No other content changes to these files.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| >20% metrics missing on sm_120 | Escalate to dedicated metric discovery. Session plan defines this threshold. |
| Metrics resolve to zero silently | The validation script will check for both existence (in `action.metric_names()`) AND non-zero values |
| ncu requires sudo for profiling | Try without sudo first; use `--target-processes all` flag; fall back to `sudo ncu` |
| Stall metric names changed subtly | Compare full stall metric list, not just the ones in STALL_METRICS |

## Open Questions

- Will `ncu --set full --section PmSampling` work without sudo on this machine?
- Are there new sm_120-specific metrics worth adding to the curated list?
