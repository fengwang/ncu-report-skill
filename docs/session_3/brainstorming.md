# Session 3 Brainstorming

## Context

Session 3 is the highest-risk session: metric name compatibility between sm_100 and sm_120 is unverified. Incorrect metric names cause silent failures in analysis scripts (metrics resolve to zero instead of raising errors).

Sessions 1 and 2 are complete. All reference docs and core skill files are updated for RTX 5090/sm_120. The helpers/ directory still references B200/sm_100 throughout.

## Key Discoveries (Pre-Implementation)

1. **ncu_report module location (G-6 resolved)**: The module is installed as a system package at `/usr/lib/python3.14/site-packages/ncu_report/`. It imports directly with `import ncu_report` — no path manipulation needed. The current fallback `_locate_ncu_report()` searches for `ncu_report.py` (single file) but the actual module is a package directory with `__init__.py` and `_ncu_report.so`.

2. **Toolchain confirmed**: nvcc 13.2 at `/opt/cuda/bin/nvcc`, ncu 2026.2.0.0 at `/usr/bin/ncu`, RTX 5090 CC 12.0 detected via nvidia-smi.

3. **Stale references**: SKILL.md and README.md still reference `08-b200-metric-names.md` (renamed in Session 2). Blast radius expanded to include these files for this narrow fix.

## Decisions Made

| Decision | Choice | Rationale |
|---|---|---|
| Variable naming | `RTX5090_KEY_METRICS` | Product-name based; clearer for this specific GPU |
| Blast radius expansion | Fix SKILL.md + README.md filename refs | Session 2 handoff warning; cosmetic fix only |
| Test kernel approach | Temp kernel in /tmp | harness_template.cu stays as user template |
| Validation order | Hardware validation first | Critical path; determines if we escalate |

## Approach: Validate-First

1. Hardware validation first (G-2, G-6, G-1, G-5, G-8)
2. Update helper scripts with validated data
3. Update harness template and references last

This order ensures we discover metric name incompatibilities early, before investing effort in script updates that might need redoing.
