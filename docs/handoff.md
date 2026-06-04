# Session Handoff

## State Snapshot
- Session: 3 (Helpers & Code Adaptation)
- Branch: fea/5090
- Last commit: 6193264 (Session 2); Session 3 changes uncommitted
- Changed files: helpers/ncu_utils.py, helpers/analyze_reports.py, helpers/plot_timeline.py, helpers/harness_template.cu, helpers/README.md, SKILL.md, README.md
- Checks run: All 5 deterministic checks from session contract; sharded review (correctness, architecture, tests); adversarial verification; hardware metric validation on local RTX 5090
- Checks not run: End-to-end profiling workflow (Session 4); analyze_reports.py against a real ncu report; reference doc consistency with new DRAM metric names
- Current status: Session 3 done condition satisfied. Awaiting commit.

## Narrative Context
Session 3 validated the curated metric list against actual RTX 5090 ncu output (2,383 metrics extracted). 93/100 metrics present — the 7 missing were DRAM metrics renamed from `dram__bytes_read` to `dram__bytes_op_read` (same pattern for write/sectors). The curated list was renamed from `B200_KEY_METRICS` to `RTX5090_KEY_METRICS` with all 7 DRAM names corrected and 3 pcsamp stall metrics added for completeness (103 total). PM sampling metrics on sm_120 are entirely different from sm_100 — stall-breakdown timeseries don't exist, replaced with hardware-counter timeseries. All 5 evidence gaps resolved with hardware experiments: G-1 (max shared mem = 96 KB opt-in), G-2 (93% metric compatibility), G-5 (no TMEM on consumer Blackwell), G-6 (ncu_report is a system package), G-8 (all carveout options accepted).

## Decision Log
| Decision | Chosen | Rejected | Reason | Contract Ref |
|---|---|---|---|---|
| Metric list variable name | RTX5090_KEY_METRICS | SM120_KEY_METRICS, KEY_METRICS | Product-name clarity, user brainstorming choice | Session 3 brainstorming |
| Blast radius for SKILL.md/README.md | Expand for filename fix only | Defer to Session 4 | Stale links to renamed file; cosmetic but user-visible | User decision during brainstorming |
| PM sampling metrics | Replace with sm_120 hardware-counter timeseries | Keep old names (would all show "no data") | Old stall-breakdown timeseries don't exist on sm_120 | G-2 validation |
| ncu_report discovery | Keep fallback + fix for package dirs | Remove fallback entirely | Other installations may not have system package | Design D2 |
| Test kernel for validation | Temp kernel in /tmp | Make harness compilable | Harness is a user template; temp kernel is ephemeral | User decision during brainstorming |

## Next Priority Queue
1. **Session 4: End-to-end validation** — Run the full profiling workflow on the local RTX 5090 (harness → compile → collect → parse → diagnose → report).
2. **CRITICAL: Fix old DRAM metric names in reference docs** — 10+ files still use `dram__bytes_read.sum` instead of `dram__bytes_op_read.sum`. These will cause silent `None` returns. Affected files listed in sharded review findings C-1, C-2.
3. **Fix PM sampling metric names in reference docs** — `reference/08-rtx5090-metric-names.md` and `reference/04-python-api.md` still list old stall-breakdown PM sampling metrics.

## Warnings And Gotchas
- Environment issues: ncu_report system package has a broken symlink for `libnvperf_host.so` that was manually fixed by the user. If the system is reinstalled, this may need re-fixing.
- Known failing tests: None (no test suite exists).
- Deferred risks:
  - **HIGH**: Old DRAM metric names (`dram__bytes_read`, `dram__bytes_write`, `dram__sectors_read`, `dram__sectors_write`) persist in 10+ reference/doc files. Session 4 MUST fix these — users following the docs will get `None` on RTX 5090. Full list: `reference/01-workflow.md:215`, `reference/03-collection.md:111`, `reference/04-python-api.md:44,221`, `reference/05-analysis-dimensions.md:230-233,261`, `reference/06-diagnosis-playbook.md:130,331,362`, `reference/07-report-template.md:68`, `reference/09-common-issues.md:230`, `blackwell-cuda-programming.md:316-317`, `SKILL.md:85`.
  - **MEDIUM**: PM sampling metric names in `reference/08-rtx5090-metric-names.md:187-200` and `reference/04-python-api.md:77` still list old stall-breakdown timeseries that don't exist on sm_120.
  - **LOW**: `load_action()` in ncu_utils.py discards the report object, risking premature GC. Pre-existing bug, not Session 3 scope.
  - The "unverified on sm_120" caveat in `reference/08-rtx5090-metric-names.md` header can now be removed (Session 3 validated 93%).
- Files future sessions must not casually edit: All 5 helper scripts are now self-consistent for RTX 5090/sm_120. The DRAM metric names (`_op_` infix) and PM sampling metrics are validated. Any edits must maintain this consistency.

## Eval Seeds
- Missed check: The DRAM metric rename (`dram__bytes_read` → `dram__bytes_op_read`) was discovered during hardware validation but was not anticipated in the session plan or contract. Future contracts should include "diff DRAM metric names" as an explicit validation step.
- New regression test candidate: `grep -c 'dram__bytes_op_read\|dram__bytes_op_write' helpers/ncu_utils.py` — should return >= 2 (confirms sm_120 DRAM names are used).
- New regression test candidate: `python3 -c "from ncu_utils import RTX5090_KEY_METRICS; assert len(RTX5090_KEY_METRICS) >= 100"` — confirms metric list exists and has expected size.
- Instruction update candidate: Session 3 discovered that PM sampling metrics on sm_120 are completely different from sm_100 (hardware-counter timeseries vs stall-breakdown). This was not anticipated in the session plan. Future plans should explicitly scope PM sampling metric validation.
- Instruction update candidate: The `ncu_report` module can be installed as a system Python package (not just under CUDA extras/python). Discovery logic should check for both installation styles.
