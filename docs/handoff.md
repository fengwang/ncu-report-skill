# Session Handoff

## State Snapshot
- Session: 5 (CUDA 13.3 Upgrade — Tile Kernel Support)
- Branch: fea/5090
- Last commit: 683ebab (Session 5 plan and contract); Session 5 changes uncommitted
- Changed files: ENVIRONMENT.md, README.md, SKILL.md, blackwell-cuda-programming.md, helpers/harness_template.cu, reference/01-workflow.md, reference/04-python-api.md, reference/05-analysis-dimensions.md, reference/06-diagnosis-playbook.md, reference/08-rtx5090-metric-names.md, reference/09-common-issues.md (11 files, 360 insertions, 9 deletions)
- Checks run: All 9 deterministic checks (all pass); sharded review (4 findings, all fixed); adversarial verification (8/11 pass, 2 partial, 1 confirmed — all caveated in docs)
- Checks not run: None — all checks executed
- Current status: Session 5 done condition satisfied. Awaiting commit.

## Narrative Context
Session 5 completed two major workstreams: (1) hardware validation of tile kernels on RTX 5090 and (2) content writing grounded in validation data.

**CUDA 13.3 version bump:** 7 references to "CUDA 13.2" / "cuda-13.2" replaced across 5 files. Zero stale references remain.

**Hardware validation (3 tile kernels):**
- Element-wise vector_add: confirmed `--enable-tile` flag required, compiler chooses block_size=128, `partition_view` + `load_masked`/`store_masked` pattern works, SIMT vs tile metric comparison documented
- GEMM with ct::mma (256×256×256 FP16→FP32): tensor core metrics confirmed working (`sm__pipe_tensor_cycles_active = 28.5%`), compiler chooses block_size=256
- Reduction with ct::atomic_add: atomic metrics confirmed (`lts__d_atomic_input_cycles_active.max.pct = 29.2%`), barrier stall from ct::sum reduction
- Hint architecture code 1200: accepted by nvcc on sm_120
- TMA hardware: `device__attribute_tensor_map_access_supported = 1` (hardware present; compiler lowering unconfirmed)

**Content:** 133-line tile kernel programming section in programming guide (API reference, decision framework, performance annotations, profiling behavior). 4 diagnosis patterns (R–U) with hardware-validated ncu metrics. 6 analysis dimension tile annotations. 5 common issues (enable-tile flag, launch syntax, cross-calling, _ic constants, hint placement). Tile variant in harness template. Tile mention in SKILL.md.

## Decision Log
| Decision | Chosen | Rejected | Reason | Contract Ref |
|---|---|---|---|---|
| ENVIRONMENT.md blast radius | Add to allowed_files | Exclude from check | Has stale CUDA 13.2 ref, simple fix | Brainstorming D1 |
| Validation strategy | Progressive 3-kernel | Single comprehensive; minimal+caveat | Isolates metric sources; addresses adversarial concern about trivial-only validation | Brainstorming D2 |
| Harness template | Tile variant in existing file | Separate file; no modification | One file, both models, no new top-level files | Brainstorming D3 |
| Task ordering | Validate first, then content | Content first; interleaved | Tile ncu behavior unknown; content must be grounded in real data | Brainstorming D4 |
| Pattern S validation | Caveat that gather was not profiled | Fabricate comparison | Review finding F1: no gather kernel was profiled | Sharded review |
| TMA claim scope | Hardware attribute only | Claim compiler lowering | Review finding F2: ncu TMA metrics not checked | Sharded review |

## Next Priority Queue
1. **Commit Session 5 changes** — all work is ready to commit
2. **Update docs/evidence_map.md** — Mark tile kernel validations as resolved (in docs/, outside blast radius)
3. **Merge fea/5090 to main** — All 5 sessions complete, project-level acceptance criteria met

## Warnings And Gotchas
- Environment issues: ncu_report system package has a broken symlink for `libnvperf_host.so` (pre-existing, from Session 4).
- Known failing tests: None (no test suite exists).
- Deferred risks:
  - **MEDIUM**: Pattern S (partition_view vs gather) diagnosis pattern is not hardware-validated. The advice is directionally correct but the specific metric trade-off is not quantified. A future session could add a gather-path tile kernel ncu comparison.
  - **MEDIUM**: TMA compiler lowering on sm_120 is not confirmed via ncu metrics. Hardware attribute is present; actual TMA instruction generation depends on access pattern and tile shape. A future session could profile the `hint_allow_tma` kernel with ncu and check for TMA-specific counters.
  - **LOW**: `load_action()` in ncu_utils.py discards the report object, risking premature GC. Pre-existing bug from Session 4.
- The validation artifacts in `profile/validation_run/` are gitignored and should not be committed.

## Eval Seeds
- New regression test: `grep -rci 'CUDA 13\.2' --include='*.md' --include='*.py' --include='*.cu' --include='*.h' --exclude-dir=docs . | grep -v ':0$'` — must return empty.
- New regression test: `grep -c 'Tile Kernel\|tile kernel\|__tile_global__' blackwell-cuda-programming.md` — must return >= 3.
- New regression test: `grep -c 'tile.*kernel\|Tile.*Kernel\|tile.*pattern\|Tile.*Pattern' reference/06-diagnosis-playbook.md` — must return >= 4.
- New regression test: Compile `profile/validation_run/tile_vector_add.cu` with `nvcc -std=c++20 -arch=sm_120 --enable-tile -lineinfo -O3` — must succeed.
- Instruction update: `--enable-tile` is required and NOT implied by `-std=c++20` or `-arch=sm_120`. This should be prominently documented in any tile kernel compilation guidance.
- Instruction update: `cutile::hint` placement is context-sensitive: `occupancy` on function declaration, `latency`/`allow_tma` on statement. Getting this wrong produces a silent warning, not an error.
- Instruction update: Tile kernel launch syntax accepts both `<<<grid>>>` and `<<<grid, 1>>>`. The single-arg form is preferred and matches NVIDIA samples.
