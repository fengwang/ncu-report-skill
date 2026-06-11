# Session 5 Execution Contract

## Planned File Changes

| File | Action | Description |
|---|---|---|
| `ENVIRONMENT.md` | Modify | CUDA 13.2 → 13.3 |
| `blackwell-cuda-programming.md` | Modify | Version bump + tile kernel programming section (~120-150 lines) |
| `README.md` | Modify | Version bump |
| `reference/01-workflow.md` | Modify | Tile kernel harness/collection/diagnosis variants |
| `reference/04-python-api.md` | Modify | Path version bump |
| `reference/05-analysis-dimensions.md` | Modify | Tile kernel notes on all 6 dimensions |
| `reference/06-diagnosis-playbook.md` | Modify | 4 new tile diagnosis patterns (R–U) |
| `reference/08-rtx5090-metric-names.md` | Modify | Tile kernel metric behavior section |
| `reference/09-common-issues.md` | Modify | Version bump + tile kernel gotchas |
| `helpers/harness_template.cu` | Modify | Tile variant section (#if 0 guarded) |
| `SKILL.md` | Modify | Tile kernel mention |
| `docs/project_contract.md` | Modify | Version 1.1, CUDA 13.3, 5 sessions |
| `profile/validation_run/*.cu` | Create (gitignored) | 3 validation kernels + SIMT comparison |

## Allowed Blast Radius

Session contract `allowed_files` plus `ENVIRONMENT.md` (approved in brainstorming D1):
- `SKILL.md`, `blackwell-cuda-programming.md`, `reference/01-workflow.md`, `reference/05-analysis-dimensions.md`, `reference/06-diagnosis-playbook.md`, `reference/08-rtx5090-metric-names.md`, `reference/09-common-issues.md`, `README.md`, `reference/04-python-api.md`, `helpers/harness_template.cu`, `docs/project_contract.md`, `ENVIRONMENT.md`

**Forbidden:** `helpers/ncu_utils.py`, `helpers/analyze_reports.py`, `helpers/extract_stall_hotspots.py`, `helpers/plot_timeline.py`, `docs/session_1*` through `docs/session_4*`

## First Test to Write

Not a code test — first validation is Task 1.2: `grep -rci 'CUDA 13\.2' ... | grep -v ':0$'` returning empty after version bump.

First hardware test: Task 2.2 — tile vector_add compiles with `nvcc -arch=sm_120`.

## Checks After Each Task

| After Task | Check |
|---|---|
| 1 | `grep -rci 'CUDA 13\.2' ... | grep -v ':0$'` — empty |
| 2 | Tile vector_add compiles, runs, profiles; SIMT comparison documented |
| 3 | Tile GEMM compiles, runs; tensor core metrics recorded |
| 4 | Tile reduction compiles, runs; atomic metrics recorded |
| 5 | Hint code and TMA status documented |
| 6 | `grep -c 'Tile Kernel\|tile kernel\|__tile_global__' blackwell-cuda-programming.md` >= 3 |
| 6 | `grep -c '__restrict__\|assume_aligned\|irange\|partition_view' blackwell-cuda-programming.md` >= 4 |
| 7 | `grep -c 'tile.*kernel\|Tile.*Kernel\|tile.*pattern\|Tile.*Pattern' reference/06-diagnosis-playbook.md` >= 4 |
| 7 | `grep -c 'atomic.*contention\|atomic.*tile\|tile.*atomic' reference/06-diagnosis-playbook.md` >= 1 |
| 9 | `grep -c 'tile\|Tile\|__tile_global__' reference/09-common-issues.md` >= 2 |
| 10 | `grep -c 'tile\|Tile' SKILL.md` >= 1 |
| 10 | `grep -c '13\.3' docs/project_contract.md` >= 1 |
| 10 | `grep -c 'all 5 sessions' docs/project_contract.md` >= 1 |

## Review Axes (End of Session)

1. Correctness — tile content matches hardware validation data; no hypothetical claims without caveats
2. Security — no new attack surface (documentation-only changes)
3. Architecture — six-dimension framework preserved; tile content additive not replacing
4. Performance — not applicable (documentation, not code optimization)

## Adversarial Verifier Brief

The verifier SHALL check:
1. Tile kernel content is grounded in real ncu output, not copy-pasted from NVIDIA docs without sm_120 contextualization
2. Diagnosis patterns reference specific ncu metrics validated on hardware
3. Performance annotations are connected to specific profiling signals
4. Decision framework has concrete criteria (not just "use tiles for simple kernels")
5. Atomic contention pattern is tile-specific, not generic CUDA atomics advice
6. Existing SIMT content is unchanged by the version bump
7. Zero CUDA 13.2 references outside docs/

## Concrete Done Condition

All 9 deterministic checks from session contract pass. Tile kernel programming guide section exists with ≥3 decision factors. At least 4 tile diagnosis patterns with ncu metric references. Common issues updated. SKILL.md mentions tiles. ncu metrics validated on real hardware. Project contract updated.
