# Session 3 Proposal

## Motivation

The helper scripts and CUDA harness template still target B200/sm_100. Analysis scripts reference `B200_KEY_METRICS` containing metric names validated only on sm_100. The harness compiles for `compute_100,code=sm_100`. Five evidence map gaps (G-1, G-2, G-5, G-6, G-8) remain unresolved, all requiring hardware validation on the local RTX 5090.

## Specific Changes

1. **Validate metric names on sm_120 hardware** — Compile a test kernel, collect an ncu report with `--set full`, extract `action.metric_names()`, diff against current B200 metric list.
2. **Rename and update metric list** — `B200_KEY_METRICS` → `RTX5090_KEY_METRICS` with validated metric names.
3. **Fix ncu_report discovery** — Update `_locate_ncu_report()` to handle package directories (not just `.py` files) and add the correct candidate path.
4. **Update throughput constants** — Add RTX 5090 bandwidth (~1.792 TB/s) and peak compute constants to analyze_reports.py.
5. **Update harness compile target** — `compute_100,code=sm_100` → `compute_120,code=sm_120`.
6. **Resolve evidence gaps** — G-1 (max shared mem/block), G-2 (metric diff), G-5 (TMEM metrics), G-6 (import path), G-8 (carveout options).
7. **Fix stale filename references** — Update `08-b200-metric-names.md` → `08-rtx5090-metric-names.md` in SKILL.md and README.md.

## Capabilities

### New Capabilities
- **metric-validation**: Validated RTX 5090 metric list with verification annotations
- **throughput-constants**: RTX 5090 peak bandwidth and compute constants in analyze_reports.py

### Modified Capabilities
- **metric-list**: B200_KEY_METRICS → RTX5090_KEY_METRICS with validated content
- **ncu-report-discovery**: Updated path resolution for package-style ncu_report modules
- **stall-metrics**: Stall metric names verified against sm_120
- **pm-sampling-metrics**: PM sampling metric names verified against sm_120
- **harness-compile-target**: sm_100 → sm_120
- **helpers-readme**: Updated compile examples and metric list references

## Impact

- **Code**: All 5 helper scripts + helpers/README.md + SKILL.md + root README.md
- **APIs**: `B200_KEY_METRICS` export renamed to `RTX5090_KEY_METRICS` (breaking for any external consumer, but no known external consumers)
- **Dependencies**: None added. ncu_report import mechanism simplified.
