# Session 4 Execution Contract

**Date:** 2026-06-04

---

## Planned File Changes

| File | Change Type | Description |
|---|---|---|
| SKILL.md | Modify | Fix 1 DRAM metric name |
| blackwell-cuda-programming.md | Modify | Fix 2 DRAM names + add precision profiling recipes |
| reference/01-workflow.md | Modify | Fix 1 DRAM name + add framework walkthrough content |
| reference/03-collection.md | Modify | Fix 1 DRAM name |
| reference/04-python-api.md | Modify | Fix 2 DRAM names + fix PM sampling metrics |
| reference/05-analysis-dimensions.md | Modify | Fix 5 DRAM names |
| reference/06-diagnosis-playbook.md | Modify | Fix 3 DRAM names + add decode checklist |
| reference/07-report-template.md | Modify | Fix 1 DRAM name |
| reference/08-rtx5090-metric-names.md | Modify | Fix 8 DRAM names + fix PM sampling + remove unverified caveat |
| reference/09-common-issues.md | Modify | Fix 1 DRAM name + add G-4 and G-7 results |
| .gitignore | Modify | Add profile/validation_run/ |
| profile/validation_run/REPORT.md | Create (gitignored) | Validation report |

## Allowed Blast Radius

All files in the session contract's `allowed_files` list, PLUS expanded to include: SKILL.md, reference/08-rtx5090-metric-names.md, reference/04-python-api.md, reference/03-collection.md, reference/07-report-template.md (per D1 decision).

**Forbidden:** `docs/*` (except docs/session_4/ planning artifacts), helper scripts other than for bug fixes discovered during validation.

## First Test to Write

```bash
grep -rn 'dram__bytes_read\b\|dram__bytes_write\b\|dram__sectors_read\b\|dram__sectors_write\b' \
  --include='*.md' --include='*.py' --exclude-dir=docs . | wc -l
```
Expected: ~22 before fix, 0 after fix.

## Checks After Each Task

| Task | Check |
|---|---|
| 1 (DRAM fix) | grep for old DRAM names = 0; grep for new names in ncu_utils >= 2 |
| 2 (Recipes) | grep for 'Profiling BF16/FP8/INT8/FP4' >= 4 in programming guide |
| 3 (Framework) | grep for 'action mapping' and 'VRAM budget' >= 1 each in workflow |
| 4 (Checklist) | grep for 'Decode Optimization' >= 1 in playbook; no old DRAM names in checklist |
| 5 (Gaps) | G-4 and G-7 results documented in common-issues |
| 6 (Validation) | All 6 phases produce output; REPORT.md exists |
| 7 (Consistency) | B200 sweep = 0; DRAM name sweep = 0 |

## Review Axes

- **Correctness:** DRAM names, hardware numbers, metric values
- **Security:** No secrets, no external URLs introduced
- **Tests:** All spec scenarios pass their grep/verification checks
- **Architecture:** No new top-level files; existing structure preserved
- **Performance:** Not applicable (content changes only)

## Adversarial Verifier Brief

The verifier sees: session contract, git diff, and deterministic check results. Its job is to falsify:
1. "All DRAM metric names are correct" — search for any old name, including in comments and string literals
2. "LLM content is RTX 5090-specific" — check for generic GPU advice without 5090 values
3. "End-to-end workflow works" — check REPORT.md for placeholders or copy-pasted values
4. "Cross-file consistency holds" — check hardware numbers match across files
5. "Gap resolutions are complete" — check G-4 and G-7 have concrete results, not hedged non-answers

## Concrete Done Condition

All 8 session contract acceptance criteria pass:
1. End-to-end workflow completes (6 phases, real hardware)
2. analyze_reports.py: no metric-not-found errors
3. extract_stall_hotspots.py: produces stall ranking
4. plot_timeline.py: produces ASCII timeline
5. Zero B200/sm_100 references outside docs/
6. Decode optimization checklist exists in playbook
7. Precision profiling recipes exist for FP4, FP8, INT8, BF16
8. Validation REPORT.md exists with evidence-backed findings

Plus: G-4 and G-7 gaps resolved, framework walkthrough complete, DRAM names corrected everywhere.
