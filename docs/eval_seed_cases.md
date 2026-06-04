# Eval Seed Cases

Test scenarios for validating that each session's deliverables meet acceptance criteria. Each case has a deterministic check method and expected outcome.

---

## Session 1: Foundation

### ES-1.1: B200 Reference Elimination (Top-Level Files)
- **Input:** Modified SKILL.md, blackwell-cuda-programming.md, README.md
- **Check:** `grep -ri "sm_100\|B200\|b200\|sm100" SKILL.md blackwell-cuda-programming.md README.md`
- **Expected:** Empty output (zero matches)
- **Failure means:** Stale B200 reference survived

### ES-1.2: SM Count Accuracy
- **Input:** SKILL.md hardware parameter table
- **Check:** Extract SM count value from SKILL.md
- **Expected:** 170 (not 148)
- **Failure means:** B200 SM count not updated

### ES-1.3: Shared Memory Accuracy
- **Input:** blackwell-cuda-programming.md shared memory section
- **Check:** Extract shared memory per SM value
- **Expected:** 100 KB or 102,400 bytes (not 228 KB)
- **Failure means:** B200 shared memory limit not updated

### ES-1.4: Compile Target
- **Input:** All compilation examples across modified files
- **Check:** `grep -i "sm_1[0-9][0-9]" SKILL.md blackwell-cuda-programming.md README.md`
- **Expected:** Only sm_120 matches (no sm_100)
- **Failure means:** Wrong compile target

### ES-1.5: LLM Inference Section Exists
- **Input:** blackwell-cuda-programming.md
- **Check:** `grep -i "LLM\|decode\|inference" blackwell-cuda-programming.md | head -5`
- **Expected:** Matches in section headings or major content blocks
- **Failure means:** LLM content not added

### ES-1.6: Bandwidth Reference
- **Input:** blackwell-cuda-programming.md
- **Check:** `grep -i "1.8 TB\|1792\|1.792" blackwell-cuda-programming.md`
- **Expected:** At least one match (RTX 5090 bandwidth)
- **Failure means:** Still references B200's 8 TB/s or no bandwidth cited

### ES-1.7: No HBM References
- **Input:** blackwell-cuda-programming.md
- **Check:** `grep -i "HBM" blackwell-cuda-programming.md`
- **Expected:** Empty (RTX 5090 uses GDDR7, not HBM)
- **Failure means:** HBM-specific content not removed

### ES-1.8: Precision Roofline Table
- **Input:** blackwell-cuda-programming.md
- **Check:** `grep -c "FP4\|FP8\|INT8\|BF16\|FP16\|TF32\|FP32" blackwell-cuda-programming.md`
- **Expected:** >= 7 (all precisions mentioned)
- **Failure means:** Incomplete precision coverage

---

## Session 2: Reference Docs & Diagnosis

### ES-2.1: B200 Reference Elimination (Reference Files)
- **Input:** All files in reference/
- **Check:** `grep -ri "sm_100\|B200\|b200\|sm100" reference/`
- **Expected:** Empty output
- **Failure means:** Stale reference in docs

### ES-2.2: Metric Names File Renamed
- **Input:** reference/ directory listing
- **Check:** `ls reference/08-*`
- **Expected:** `reference/08-rtx5090-metric-names.md` exists; `reference/08-b200-metric-names.md` does not
- **Failure means:** File rename incomplete

### ES-2.3: Diagnosis Pattern A Threshold
- **Input:** reference/06-diagnosis-playbook.md
- **Check:** Extract "small grid" pattern threshold
- **Expected:** References 170 blocks (RTX 5090 SM count)
- **Failure means:** B200 threshold (148) not updated

### ES-2.4: Occupancy Limits in Analysis Dimensions
- **Input:** reference/05-analysis-dimensions.md
- **Check:** Extract occupancy limits
- **Expected:** 48 warps/SM, 24 blocks/SM, 100 KB shared/SM, 65536 regs/SM
- **Failure means:** B200 occupancy limits (64 warps, 32 blocks, 228 KB) not updated

### ES-2.5: LLM Diagnosis Patterns Exist
- **Input:** reference/06-diagnosis-playbook.md
- **Check:** `grep -c "Pattern I\|Pattern J\|Pattern K" reference/06-diagnosis-playbook.md`
- **Expected:** >= 3
- **Failure means:** LLM patterns not added

### ES-2.6: LLM Pattern Specificity
- **Input:** reference/06-diagnosis-playbook.md, Pattern I (decode bandwidth)
- **Check:** Pattern I mentions RTX 5090 bandwidth (~1.8 TB/s) and a concrete ncu metric signal
- **Expected:** Both present
- **Failure means:** Pattern is too generic, not actionable for profiling

### ES-2.7: Framework Profiling Guidance
- **Input:** reference/01-workflow.md
- **Check:** `grep -i "framework\|TensorRT\|vLLM\|opaque\|without source" reference/01-workflow.md`
- **Expected:** At least one match
- **Failure means:** No guidance for profiling framework kernels

---

## Session 3: Helpers & Code

### ES-3.1: Metric List Renamed
- **Input:** helpers/ncu_utils.py
- **Check:** `grep "B200_KEY_METRICS" helpers/ncu_utils.py`
- **Expected:** Empty (variable renamed)
- **Failure means:** Old variable name persists

### ES-3.2: B200 Reference Elimination (Helpers)
- **Input:** All files in helpers/
- **Check:** `grep -ri "B200\|b200\|sm_100\|sm100" helpers/`
- **Expected:** Empty
- **Failure means:** Stale reference in code

### ES-3.3: Harness Compilation
- **Input:** helpers/harness_template.cu
- **Check:** `nvcc -arch=sm_120 -lineinfo helpers/harness_template.cu -o /tmp/eval_harness 2>&1; echo $?`
- **Expected:** Exit code 0
- **Failure means:** Harness doesn't compile for sm_120

### ES-3.4: ncu_report Import
- **Input:** Python environment with CUDA 13.2
- **Check:** `python3 -c "import sys; sys.path.insert(0, '<path>'); import ncu_report; print('OK')"`
- **Expected:** Prints "OK"
- **Failure means:** Import path wrong or module incompatible

### ES-3.5: Bandwidth Constant Updated
- **Input:** helpers/analyze_reports.py
- **Check:** `grep -c "1792\|1.792\|1.8" helpers/analyze_reports.py`
- **Expected:** >= 1
- **Failure means:** B200 bandwidth (8000 or 8 TB/s) still used

### ES-3.6: Metric Validation Coverage
- **Input:** Metric validation results from Session 3
- **Check:** Count of validated metrics / total metrics in curated list
- **Expected:** >= 80%
- **Failure means:** Too many unvalidated metrics; risk of silent failures

### ES-3.7: Gap G-1 Resolved
- **Input:** Session 3 outputs
- **Check:** Max dynamic shared memory per block value documented
- **Expected:** Specific byte value (e.g., 101,376 B or 49,152 B)
- **Failure means:** Gap unresolved, shared memory guidance may be wrong

---

## Session 4: LLM Content & Validation

### ES-4.1: End-to-End Workflow Completes
- **Input:** Local RTX 5090, all updated skill files
- **Check:** Run full 6-phase workflow; each phase produces output
- **Expected:** No errors; analyze_reports.py, extract_stall_hotspots.py, plot_timeline.py all produce output
- **Failure means:** Workflow broken; requires fix-forward

### ES-4.2: Global B200 Sweep
- **Input:** Entire repository (excluding docs/)
- **Check:** `grep -ri "B200\|sm_100\|sm100" --include='*.md' --include='*.py' --include='*.cu' --include='*.h' --exclude-dir=docs .`
- **Expected:** Empty
- **Failure means:** Stale reference somewhere in the repo

### ES-4.3: Validation Report Exists
- **Input:** profile/validation_run/
- **Check:** `test -f profile/validation_run/REPORT.md && echo exists`
- **Expected:** "exists"
- **Failure means:** Validation not completed or report not generated

### ES-4.4: Validation Report Quality
- **Input:** profile/validation_run/REPORT.md
- **Check:** Report contains: GPU name (RTX 5090), kernel name, at least 3 of 6 analysis dimensions with metric values, a ranked recommendation
- **Expected:** All present
- **Failure means:** Report is a template with placeholders, not a real analysis

### ES-4.5: LLM Decode Checklist Exists
- **Input:** reference/06-diagnosis-playbook.md
- **Check:** `grep -i "decode.*checklist\|optimization checklist\|Decode Optimization" reference/06-diagnosis-playbook.md`
- **Expected:** At least one match
- **Failure means:** Checklist not added

### ES-4.6: Precision Profiling Recipes
- **Input:** blackwell-cuda-programming.md
- **Check:** Sections or subsections exist for profiling FP4, FP8, INT8, BF16 kernels with ncu commands
- **Expected:** At least 4 precision-specific recipe blocks
- **Failure means:** Recipes missing or incomplete

### ES-4.7: .gitignore Updated
- **Input:** .gitignore
- **Check:** `grep "validation_run\|profile/" .gitignore`
- **Expected:** At least one match
- **Failure means:** Validation artifacts risk being committed

### ES-4.8: Effective Bandwidth Documented (Gap G-7)
- **Input:** Session 4 outputs
- **Check:** Measured effective bandwidth value documented (in programming guide or common issues)
- **Expected:** A concrete number (e.g., "1,520 GB/s measured, 85% of theoretical 1,792 GB/s")
- **Failure means:** Gap unresolved; roofline analysis uses unvalidated theoretical peak

---

## Cross-Cutting Eval Cases

### ES-X.1: Cross-File Consistency — SM Count
- **Check:** `grep -rn "170" SKILL.md blackwell-cuda-programming.md reference/05-analysis-dimensions.md reference/06-diagnosis-playbook.md`
- **Expected:** SM count (170) appears consistently in all files that reference it
- **Failure means:** Inconsistent spec across files

### ES-X.2: Cross-File Consistency — Bandwidth
- **Check:** `grep -rn "1.8 TB\|1792\|1.792" SKILL.md blackwell-cuda-programming.md reference/05-analysis-dimensions.md reference/06-diagnosis-playbook.md helpers/analyze_reports.py`
- **Expected:** Bandwidth (~1.8 TB/s) appears consistently
- **Failure means:** Mixed bandwidth values (some B200, some RTX 5090)

### ES-X.3: Cross-File Consistency — Occupancy Limits
- **Check:** All files referencing warps/SM say 48 (not 64), blocks/SM say 24 (not 32)
- **Expected:** Consistent values
- **Failure means:** Occupancy calculations will give wrong results in some files
