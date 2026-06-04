# Session Handoff

## State Snapshot
- Session: 1 (Foundation — Core Specs & Programming Guide)
- Branch: fea/5090
- Last commit: bbf00ce (pre-session; implementation not yet committed)
- Changed files: SKILL.md, blackwell-cuda-programming.md, README.md
- Checks run: All 4 deterministic checks from session contract; sharded review (correctness, architecture, performance); adversarial verification
- Checks not run: End-to-end profiling validation (Session 4); metric name validation (Session 3); helper script updates (Session 3)
- Current status: Session 1 done condition satisfied. Awaiting commit.

## Narrative Context
Session 1 replaced all B200 (sm_100) targeting with RTX 5090 (sm_120) across the three in-scope files. The programming guide was fully rewritten in English (was Chinese) with a new structure organized around sm_120's actual capabilities. Live GPU validation revealed that sm_120 lacks tcgen05, wgmma, TMEM, and 2CTA — the four headline data-center Blackwell features. The guide was restructured around the actually-available ISA (mma.sync/WMMA) with new sections for GDDR7 memory strategy, Thread Block Clusters, precision roofline breakpoints, and LLM inference profiling. All hardware numbers were verified against PRD §4.1 and confirmed by three independent reviewers plus an adversarial verifier.

## Decision Log
| Decision | Chosen | Rejected | Reason | Contract Ref |
|---|---|---|---|---|
| Language | English | Chinese, bilingual | PRD and reference docs are English | Session plan |
| Compile target | sm_120a | sm_120, both | User preference for arch-specific features | Session plan §Key Decisions |
| Comparison column | RTX 5090 only | vs H100, vs B200, vs RTX 4090 | Single-target guide, less clutter | User decision |
| DC-only features | Remove entirely | Keep as "not available", brief note | Cleaner document, user preference | Session plan §Out of Scope |
| Guide structure | Full restructure (B) | Preserve structure (A), hybrid (C) | Too many removed sections for in-place edit | Design §D-1 |
| Tensor Core section | Document mma.sync as available ISA | Recommend libraries only | Profiling requires understanding ISA-level behavior | Design §D-2 |
| FP4 documentation | Library-only with explicit note | Skip entirely, pretend PTX works | Hardware supports FP4 but PTX doesn't on sm_120 | Design §D-3 |

## Next Priority Queue
1. **Session 2: Reference docs update** — Update reference/05-analysis-dimensions.md, reference/06-diagnosis-playbook.md, and other reference docs. Rename reference/08-b200-metric-names.md.
2. **Session 3: Helper scripts + metric validation** — Update helpers/ncu_utils.py (rename B200_KEY_METRICS), validate metric names against local 5090 ncu output.
3. **Session 4: End-to-end validation** — Run the full profiling workflow on the local RTX 5090.

## Warnings And Gotchas
- Environment issues: None. RTX 5090 + CUDA 13.2 + ncu 2026.2 all confirmed working. GPU commands execute successfully.
- Known failing tests: None (no test suite exists yet for the skill itself).
- Deferred risks:
  - File `reference/08-b200-metric-names.md` still has "b200" in its filename (4 file-path references in SKILL.md and README.md, annotated with "file rename pending Session 2"). Session 2 must rename this file and update all references.
  - The comparison table in the Architecture Overview section contains data-center Blackwell numbers (228 KB shared, 192 GB memory, 8 TB/s bandwidth) for context. These are in the "Data-Center Blackwell" column, not as RTX 5090 claims. Project contract M-4 grep (`HBM|8 TB|126 MB|192 GB`) will match these. Session 2+ should decide whether to remove the comparison table or accept these as intentional context.
  - NCU metric names throughout the programming guide are inherited from B200; Session 3 will validate them on sm_120.
  - FP4 is documented as "library-only" based on PTX compilation test. The actual internal code paths used by cuBLAS for FP4 on sm_120 are not documented — profiling FP4 cuBLAS kernels may reveal unexpected behavior.
  - Thread Block Clusters section added based on `cudaDevAttrClusterLaunch` returning 1, but maximum cluster size on RTX 5090 was not tested. Session 3 should verify.
- Files future sessions must not casually edit: SKILL.md and blackwell-cuda-programming.md are now self-consistent for RTX 5090. Any edits must maintain this consistency.

## Eval Seeds
- Missed check: The PRD §4.4 has a typo — BF16 roofline breakpoint listed as 116.8 should be 116.9 (209.51/1.792 = 116.91). The skill files correctly use 116.9. Consider adding a check that catches PRD/skill divergence.
- New regression test candidate: `grep -rci 'sm_100\|B200\|b200' SKILL.md blackwell-cuda-programming.md README.md | grep -v ':0$'` — should return only file-path references.
- Instruction update candidate: The brainstorming phase discovered that sm_120 lacks tcgen05/wgmma/TMEM — this was a significant surprise. Future sessions should verify feature availability via compilation tests before assuming data-center Blackwell documentation applies to consumer Blackwell.
