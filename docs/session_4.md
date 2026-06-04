# Session 4: LLM Content & End-to-End Validation

**Risk Level:** High
**Estimated Effort:** Half-day
**Prerequisites:** Sessions 1–3 complete (all files updated, metrics validated)

---

## Objective

Complete the LLM inference content across the skill. Validate the entire skill end-to-end by running the full profiling workflow on the local RTX 5090: build a harness, collect ncu reports, parse with Python helpers, apply the diagnosis framework, and produce a report. Fix any issues discovered during validation. Resolve remaining evidence map gaps G-4 and G-7.

## Scope

### In Scope

1. **LLM content finalization** — Ensure all LLM-specific content from Sessions 1–2 is cohesive:
   - Review the programming guide's LLM section for consistency with diagnosis patterns I/J/K
   - Add precision-specific profiling recipes: how to profile FP4, FP8, INT8, BF16 kernels and compare
   - Add framework profiling walkthrough: profiling a TensorRT-LLM or vLLM kernel without source
   - Add single-user decode optimization checklist: ordered steps from "identify bottleneck" to "verify improvement"

2. **End-to-end validation** — Run the complete 6-phase workflow on the local 5090:
   - **Phase 0**: Create a test profile directory `profile/validation_run/`
   - **Phase 1**: Verify environment (ncu, GPU, ncu_report, permissions)
   - **Phase 2**: Build a test kernel using the harness template (simple GEMM or memory-bandwidth kernel)
   - **Phase 3**: Collect two ncu reports:
     - `ncu --set full --section PmSampling` (overview + timeline)
     - `ncu --set source --section SourceCounters` (per-line stalls)
   - **Phase 4**: Run all Python helpers:
     - `analyze_reports.py` — extract key metrics, verify no metric-not-found errors
     - `extract_stall_hotspots.py` — verify stall analysis produces output
     - `plot_timeline.py` — verify PM sampling data is plottable
   - **Phase 5**: Apply diagnosis framework — does the analysis produce sensible results?
   - **Phase 6**: Generate a report following `reference/07-report-template.md`

3. **Fix-forward** — Any issue found during validation:
   - Metric names that fail → update in ncu_utils.py and propagate
   - Script errors → fix in the helper that failed
   - Incorrect thresholds → update in reference docs
   - Missing ncu sections → update collection recipes

4. **Gap resolution:**
   - **G-4**: Attempt a cluster launch on RTX 5090 to confirm/deny cluster support. Document finding.
   - **G-7**: Run a bandwidth benchmark kernel under ncu to measure effective GDDR7 bandwidth under profiling conditions. Compare with theoretical 1.792 TB/s.

5. **Cross-file consistency check** — Final review:
   - All hardware numbers consistent across SKILL.md, programming guide, reference docs, and helpers
   - All metric names consistent between ncu_utils.py and reference docs
   - All diagnosis thresholds consistent between playbook and analysis dimensions
   - No orphaned B200 references anywhere in the repo

### Out of Scope

- Profiling actual LLM inference frameworks (TensorRT-LLM, vLLM) — the validation uses a simple test kernel, not a real LLM workload. Real LLM profiling is the user's workflow after the skill is complete.
- Performance optimization of the helper scripts themselves.
- Publishing or releasing the updated skill.

## Files Modified

| File | Action | Description |
|---|---|---|
| Any file from Sessions 1–3 | Bugfix | Fix issues discovered during validation |
| `blackwell-cuda-programming.md` | Modify | LLM content finalization, precision profiling recipes |
| `reference/01-workflow.md` | Modify | Framework profiling walkthrough |
| `reference/06-diagnosis-playbook.md` | Modify | Decode optimization checklist |

## Validation Procedure

```
=== Phase 1: Environment Check ===
nvidia-smi                          # GPU visible
nvcc --version                      # CUDA 13.2
ncu --version                       # 2026.2
python3 -c "import ncu_report"      # Module importable

=== Phase 2: Build Harness ===
# Use the harness template or a simple bandwidth kernel
nvcc -arch=sm_120 -lineinfo -o profile/validation_run/harness \
     helpers/harness_template.cu

=== Phase 3: Collect Reports ===
ncu --set full --section PmSampling \
    -o profile/validation_run/reports/full \
    profile/validation_run/harness

ncu --set source --section SourceCounters \
    -o profile/validation_run/reports/source \
    profile/validation_run/harness

=== Phase 4: Parse & Analyze ===
python3 helpers/analyze_reports.py \
    profile/validation_run/reports/full.ncu-rep

python3 helpers/extract_stall_hotspots.py \
    profile/validation_run/reports/source.ncu-rep

python3 helpers/plot_timeline.py \
    profile/validation_run/reports/full.ncu-rep

=== Phase 5: Diagnose ===
# Manual: apply the six-dimension framework to the parsed output
# Verify each dimension produces meaningful values (not NaN, not zero-everywhere)

=== Phase 6: Report ===
# Generate profile/validation_run/REPORT.md following the template
```

## Deliverables

1. Successful end-to-end validation run with artifacts in `profile/validation_run/`.
2. All bugs found during validation fixed and committed.
3. LLM decode optimization checklist in the diagnosis playbook.
4. Precision-specific profiling recipes in the programming guide.
5. Framework profiling walkthrough in the workflow document.
6. Gap resolution:
   - G-4: Cluster launch support on RTX 5090 (confirmed or denied)
   - G-7: Effective GDDR7 bandwidth under profiling (measured value)
7. Cross-file consistency confirmed (zero B200 references outside docs/).

## Exit Criteria

| ID | Check | Method |
|---|---|---|
| E4-1 | End-to-end workflow completes | All 6 phases produce output without errors |
| E4-2 | analyze_reports.py runs clean | No metric-not-found warnings, produces structured output |
| E4-3 | extract_stall_hotspots.py runs clean | Produces per-line stall ranking |
| E4-4 | plot_timeline.py runs clean | Produces ASCII timeline plot |
| E4-5 | No B200 references in repo (outside docs/) | `grep -ri "B200\|sm_100\|sm100" --include='*.md' --include='*.py' --include='*.cu' --include='*.h' --exclude-dir=docs .` returns empty |
| E4-6 | LLM optimization checklist exists | Section present in diagnosis playbook |
| E4-7 | Precision profiling recipes exist | Section present in programming guide covering FP4, FP8, INT8, BF16 |
| E4-8 | Validation report generated | `profile/validation_run/REPORT.md` exists and follows template structure |

## Risk Mitigation

- **Metric failures during parsing**: If >5 metrics fail, batch-fix in ncu_utils.py before re-running. Don't fix one-at-a-time.
- **ncu permission denied**: If `ncu` fails without sudo, document the workaround in 09-common-issues.md and re-run with `sudo ncu`.
- **Clock throttling under profiling**: ncu may cause the GPU to clock down (575W TDP, display driver running). If bandwidth measurements are unexpectedly low, note the effective-vs-theoretical gap.
- **Validation artifacts**: The `profile/validation_run/` directory is for validation only. Add it to `.gitignore` — it should not be committed.

## References

- `docs/evidence_map.md` Gaps G-4, G-7 — Remaining validation targets
- `docs/prd.md` §11 — Project-level success criteria
- `docs/project_contract.md` §4 — Project-level acceptance criteria
- All session plans (Sessions 1–3) — Prerequisite work this session validates
