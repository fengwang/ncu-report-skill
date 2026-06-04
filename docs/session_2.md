# Session 2: Reference Docs & Diagnosis Framework

**Risk Level:** Medium
**Estimated Effort:** Half-day
**Prerequisites:** Session 1 complete (SKILL.md and programming guide updated)

---

## Objective

Update all 10 reference documents in `reference/` to target RTX 5090. Recalibrate the diagnosis playbook thresholds for 170 SMs, ~1.8 TB/s bandwidth, 100 KB shared/SM, and 48 warps/SM. Add LLM-specific diagnosis patterns for single-user decode workloads.

## Scope

### In Scope

1. **reference/00-directory-layout.md** — Minor update: change any B200 references in naming conventions.

2. **reference/01-workflow.md** — Update the 6-phase profiling workflow:
   - Phase 2: compile target → sm_120
   - Phase 3: ncu collection flags — verify section names are valid for sm_120
   - Phase 5: diagnosis references → recalibrated thresholds
   - Add: guidance for profiling framework kernels (TensorRT-LLM, vLLM) where source is unavailable

3. **reference/02-harness-guide.md** — Update compilation commands and template references for sm_120.

4. **reference/03-collection.md** — Update ncu command recipes:
   - Compile target flags
   - Any sm_120-specific section or metric set names
   - Verify `--set full`, `--set source`, `--section PmSampling` work on sm_120

5. **reference/04-python-api.md** — Update ncu_report API patterns:
   - Import path for CUDA 13.2 ncu_report module
   - Reference the renamed metric list (no longer `B200_KEY_METRICS`)
   - Update example metric names if any are sm_100-specific

6. **reference/05-analysis-dimensions.md** — Recalibrate all six dimensions:
   - **Occupancy**: 48 warps/SM max, 24 blocks/SM max, 100 KB shared/SM, 65536 regs/SM
   - **Tail effect**: threshold scales from 148 SMs → 170 SMs
   - **Stalls**: verify stall reason names apply to sm_120
   - **Tensor core**: update throughput figures, add precision-specific sub-pipe identification
   - **Timeline**: update PM sampling interpretation for GDDR7 latency characteristics
   - **Memory**: ~1.8 TB/s ceiling, GDDR7 access patterns, 96 MB L2, 60 MB persistent L2

7. **reference/06-diagnosis-playbook.md** — Recalibrate existing 8 patterns + add LLM patterns:
   - Pattern A (small grid): threshold → grid < 170 blocks
   - Pattern B (tail effect): scale for 170 SMs
   - Pattern C (uncoalesced): same signal, but bandwidth impact is 4.4× worse on GDDR7
   - Pattern D (sparse writes): same mechanics
   - Pattern E (latency-bound): DRAM latency characteristics may differ for GDDR7
   - Pattern F (compute without tensor): update FLOPS figures
   - Pattern G (atomic contention): same mechanics
   - Pattern H (bank conflicts): shared memory size context changes
   - **New Pattern I**: Decode bandwidth ceiling — single-token decode hitting DRAM bandwidth wall
   - **New Pattern J**: KV-cache thrashing — KV-cache exceeds L2 capacity (96 MB), causing excessive DRAM traffic
   - **New Pattern K**: Quantization mismatch — kernel using FP16 when FP8/FP4 tensor cores are available, leaving throughput on the table

8. **reference/07-report-template.md** — Update the report template:
   - GPU reference line → RTX 5090
   - Bandwidth ceiling references
   - Roofline figures

9. **reference/08-b200-metric-names.md** → **reference/08-rtx5090-metric-names.md** — Rename file. Update content:
   - Change title and references from B200/sm_100 to RTX 5090/sm_120
   - Flag metric names that are carried forward from sm_100 as "unverified on sm_120"
   - Note the incremental validation approach: metrics will be confirmed in Session 3
   - Document known naming patterns for Blackwell metrics

10. **reference/09-common-issues.md** — Update:
    - Permission issues (same on consumer GPUs, possibly different modprobe path)
    - CUDA 13.2 / ncu 2026.2 specific gotchas
    - GDDR7 memory reporting differences if any
    - Consumer GPU-specific issues (display driver interference, power throttling under profiling)

### Out of Scope

- Modifying helper Python scripts (Session 3)
- Actually validating metric names on the GPU (Session 3)
- Running end-to-end profiling (Session 4)

## Files Modified

| File | Action | Description |
|---|---|---|
| `reference/00-directory-layout.md` | Modify | Minor B200 → RTX 5090 references |
| `reference/01-workflow.md` | Modify | Compile target, ncu flags, framework profiling guidance |
| `reference/02-harness-guide.md` | Modify | Compilation commands for sm_120 |
| `reference/03-collection.md` | Modify | ncu command recipes for sm_120 |
| `reference/04-python-api.md` | Modify | Import paths, metric list reference |
| `reference/05-analysis-dimensions.md` | Major rewrite | All six dimensions recalibrated |
| `reference/06-diagnosis-playbook.md` | Major rewrite | 8 patterns recalibrated + 3 new LLM patterns |
| `reference/07-report-template.md` | Modify | GPU reference, bandwidth figures |
| `reference/08-b200-metric-names.md` | Rename + rewrite | → `08-rtx5090-metric-names.md` |
| `reference/09-common-issues.md` | Modify | Consumer GPU issues, CUDA 13.2 gotchas |

## Deliverables

1. All 10 reference documents updated for RTX 5090.
2. File `08-b200-metric-names.md` renamed to `08-rtx5090-metric-names.md`.
3. Three new LLM diagnosis patterns (I, J, K) in the playbook.
4. Framework kernel profiling guidance in the workflow document.

## Exit Criteria

| ID | Check | Method |
|---|---|---|
| E2-1 | No B200/sm_100 references in any reference/ file | `grep -ri "sm_100\|B200" reference/` returns empty |
| E2-2 | All occupancy limits match RTX 5090 specs | Manual check: 48 warps, 24 blocks, 100 KB shared, 65536 regs in analysis dimensions |
| E2-3 | Diagnosis patterns reference RTX 5090 parameters | Pattern A threshold is 170, bandwidth references are ~1.8 TB/s |
| E2-4 | LLM patterns I, J, K exist | Patterns present in 06-diagnosis-playbook.md with signal/cause/fix structure |
| E2-5 | Metric names file renamed | `ls reference/08-rtx5090-metric-names.md` succeeds |
| E2-6 | No file named `08-b200-metric-names.md` | `ls reference/08-b200-metric-names.md` fails |

## References

- `docs/prd.md` §4 — Hardware specs for threshold recalibration
- `docs/evidence_map.md` §5 — Diagnosis threshold evidence
- `docs/evidence_map.md` §6 — LLM inference pattern evidence
- `docs/session_1.md` — Depends on programming guide being updated first
