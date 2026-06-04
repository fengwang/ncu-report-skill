# Session 2 Execution Contract

## Planned File Changes

| File | Action | Magnitude |
|---|---|---|
| `reference/08-b200-metric-names.md` | Rename + rewrite → `08-rtx5090-metric-names.md` | Major |
| `reference/05-analysis-dimensions.md` | Modify | Major |
| `reference/06-diagnosis-playbook.md` | Modify + append | Major |
| `reference/00-directory-layout.md` | Modify | Minor |
| `reference/01-workflow.md` | Modify + append | Moderate |
| `reference/02-harness-guide.md` | Modify | Minor |
| `reference/03-collection.md` | Modify | Minor |
| `reference/04-python-api.md` | Modify | Minor |
| `reference/07-report-template.md` | Modify | Minor |
| `reference/09-common-issues.md` | Modify + append | Moderate |

## Allowed Blast Radius

Only files listed in the session contract's `allowed_files`:
- All 10 files in `reference/` (including the renamed metric file)
- No changes to SKILL.md, blackwell-cuda-programming.md, README.md, or helpers/*

## First Test to Write

No executable tests (these are markdown documentation files). First verification:
```bash
# After Task 1 (metric names migration):
test -f reference/08-rtx5090-metric-names.md && test ! -f reference/08-b200-metric-names.md && grep -ri 'B200\|sm_100' reference/08-rtx5090-metric-names.md | wc -l
# Expected: file exists, old file gone, 0 B200/sm_100 matches
```

## Checks After Each Task

| Task | Check Command | Expected |
|---|---|---|
| 1 | `test -f reference/08-rtx5090-metric-names.md && test ! -f reference/08-b200-metric-names.md && grep -rci 'B200\|sm_100' reference/08-rtx5090-metric-names.md` | exists, gone, 0 |
| 2 | `grep -rci 'B200\|sm_100' reference/05-analysis-dimensions.md && grep -c '170' reference/05-analysis-dimensions.md` | 0, >0 |
| 3 | `grep -rci 'B200\|sm_100' reference/06-diagnosis-playbook.md && grep -c 'Pattern O' reference/06-diagnosis-playbook.md` | 0, >0 |
| 4 | `grep -rci 'B200\|sm_100' reference/00-directory-layout.md reference/02-harness-guide.md reference/03-collection.md reference/04-python-api.md reference/07-report-template.md` | all 0 |
| 5 | `grep -c 'Phase 2.5' reference/01-workflow.md` | >0 |
| 6 | `grep -rci 'B200\|sm_100' reference/09-common-issues.md` | 0 |

## Review Axes (end of session)

Per session contract:
1. **Correctness** — All hardware values match PRD §4.1, no stale B200 values
2. **Architecture** — File structure preserved, cross-references consistent
3. **Performance** — Diagnosis thresholds correctly calibrated for RTX 5090 characteristics

## Adversarial Verifier Brief

The verifier SHALL check:
- A threshold still references B200 SM count (148) or bandwidth (8 TB/s)
- LLM patterns are too generic (not RTX 5090-specific)
- Metric name file renamed but content still says B200/sm_100
- Occupancy examples use 64 warps/SM or 32 blocks/SM
- Collection recipes use flags or sections not available on sm_120
- Framework profiling guidance assumes source code is available
- Cross-references still say "Blackwell principle N"

## Concrete Done Condition

All of the following pass:
1. `grep -rci 'sm_100\|B200\|b200' reference/ | grep -v ':0$'` returns empty
2. `grep -c '170' reference/06-diagnosis-playbook.md` returns > 0
3. `grep -c '48 warps\|48 warp' reference/05-analysis-dimensions.md` returns > 0
4. `grep -c '24 blocks\|24 block' reference/05-analysis-dimensions.md` returns > 0
5. `test -f reference/08-rtx5090-metric-names.md` succeeds
6. `test ! -f reference/08-b200-metric-names.md` succeeds
7. `grep -c 'Pattern O\|Pattern P\|Pattern Q' reference/06-diagnosis-playbook.md` returns >= 3
8. Framework profiling guidance exists in `01-workflow.md`
