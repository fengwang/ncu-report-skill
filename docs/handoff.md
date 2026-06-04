# Session Handoff

## State Snapshot
- Session: 2 (Reference Docs & Diagnosis Framework)
- Branch: fea/5090
- Last commit: dd680e0 (Session 1); Session 2 changes uncommitted
- Changed files: All 10 files in reference/ (08-b200-metric-names.md renamed to 08-rtx5090-metric-names.md)
- Checks run: All 8 deterministic checks from session contract; sharded review (correctness, architecture, performance); adversarial verification
- Checks not run: Actual metric name validation on sm_120 hardware (Session 3); helper script updates (Session 3); end-to-end profiling (Session 4)
- Current status: Session 2 done condition satisfied. Awaiting commit.

## Narrative Context
Session 2 updated all 10 reference documents from B200/sm_100 to RTX 5090/sm_120. The six-dimension analysis framework was recalibrated for 170 SMs, 48 warps/SM, 24 blocks/SM, 100 KB shared/SM, and ~1.8 TB/s DRAM bandwidth. The diagnosis playbook's 14 existing patterns (A-N) were recalibrated, data-center-only ISA references (tcgen05/wgmma/TMEM) replaced with sm_120-available ISA (cp.async/mma.sync/WMMA), and three new LLM-specific patterns added (O: decode bandwidth ceiling, P: KV-cache thrashing, Q: quantization mismatch). The metric names file was renamed from B200 to RTX 5090 with all metrics flagged as "unverified on sm_120". Phase 2.5 was added to the workflow for profiling framework kernels without source access. Consumer GPU-specific troubleshooting was added to the common issues document. All cross-references were updated from numbered "Blackwell principle N" format to named section headings matching Session 1's restructured programming guide.

## Decision Log
| Decision | Chosen | Rejected | Reason | Contract Ref |
|---|---|---|---|---|
| LLM pattern IDs | O, P, Q (append) | I, J, K (replace existing) | Existing I-N patterns already assigned; renumbering would break continuity | Session plan collision |
| DC-only ISA in fix directions | Replace with sm_120 ISA | Remove entirely, Keep annotated | Keeps fix directions actionable for RTX 5090 | Session 1 discovery |
| Framework guidance placement | New Phase 2.5 | Expand Phase 2, Appendix | Most discoverable position in workflow | Session plan §3 |
| Cross-reference format | Named section headings | Remove, Keep numbered | More robust against future restructures | Session 1 restructure |
| Pattern Q table header | "TFLOPS/TOPS" with per-row annotations | "Dense TFLOPS/TOPS" | FP4 row is sparse; mixed column header was misleading | Sharded review finding |

## Next Priority Queue
1. **Session 3: Helper scripts + metric validation** — Update helpers/ncu_utils.py (rename B200_KEY_METRICS), validate metric names against local RTX 5090 ncu output using `action.metric_names()`.
2. **Session 4: End-to-end validation** — Run the full profiling workflow on the local RTX 5090 (harness → compile → collect → parse → diagnose → report).

## Warnings And Gotchas
- Environment issues: None. RTX 5090 + CUDA 13.2 + ncu 2026.2 all confirmed working.
- Known failing tests: None (no test suite exists for the skill itself).
- Deferred risks:
  - All metric names in `08-rtx5090-metric-names.md` are carried forward from the prior Blackwell baseline and flagged as "unverified on sm_120". Session 3 MUST validate these against actual ncu output.
  - The `helpers/ncu_utils.py` still references `B200_KEY_METRICS` — Session 3 must rename this.
  - Session contract YAML (`docs/session_2_contract.yaml`) deterministic check references "Pattern I|J|K" but actual LLM patterns are O/P/Q. The contract YAML is informational only (the actual patterns are correct in the deliverable).
  - SKILL.md and README.md still contain file-path references to `08-b200-metric-names.md` (annotated with "file rename pending Session 2" from Session 1). These files are outside Session 2's blast radius — Session 3 should update these references.
  - The comparison table in `blackwell-cuda-programming.md` Architecture Overview contains data-center Blackwell numbers (228 KB shared, 192 GB memory, 8 TB/s bandwidth) in the "Data-Center Blackwell" comparison column. Project contract M-4 grep will match these. A decision is needed in a future session on whether to keep the comparison table.
- Files future sessions must not casually edit: All 10 reference files are now self-consistent for RTX 5090. Any edits must maintain this consistency, especially the diagnosis playbook thresholds and cross-references.

## Eval Seeds
- Missed check: The session contract deterministic checks reference "Pattern I|J|K" but the actual patterns are O/P/Q. Future contracts should be updated when brainstorming changes the plan.
- New regression test candidate: `grep -rci 'sm_100\|B200\|b200' reference/ | grep -v ':0$'` — should return empty after all sessions.
- New regression test candidate: `grep -c 'Pattern O\|Pattern P\|Pattern Q' reference/06-diagnosis-playbook.md` — should return >= 3.
- Instruction update candidate: Session 2 discovered that SKILL.md and README.md still reference `08-b200-metric-names.md` by filename. These are outside the session 2 blast radius but need updating. Session 3 should include this in its scope.
