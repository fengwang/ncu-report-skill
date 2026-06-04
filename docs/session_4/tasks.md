# Session 4 Tasks

## 1. DRAM & PM Sampling Metric Fix-Forward

- [ ] 1.1 Rename all `dram__bytes_read` → `dram__bytes_op_read` across 10 files (and write/sectors variants)
- [ ] 1.2 Fix PM sampling metric names in reference/08-rtx5090-metric-names.md
- [ ] 1.3 Fix PM sampling metric names in reference/04-python-api.md
- [ ] 1.4 Verify: grep returns zero old DRAM names outside docs/
- [ ] 1.5 Verify: ncu_utils.py still uses correct names (no regression)

## 2. Precision-Specific Profiling Recipes

- [ ] 2.1 Add BF16/FP16 profiling recipe to blackwell-cuda-programming.md
- [ ] 2.2 Add FP8 profiling recipe
- [ ] 2.3 Add INT8 profiling recipe
- [ ] 2.4 Add FP4/NVFP4 profiling recipe
- [ ] 2.5 Add cross-precision comparison recipe
- [ ] 2.6 Verify: all four precision keywords present in programming guide

## 3. Framework Profiling Walkthrough

- [ ] 3.1 Add framework-specific action mapping table to reference/01-workflow.md
- [ ] 3.2 Add RTX 5090 VRAM budget planning section
- [ ] 3.3 Expand kernel naming patterns reference
- [ ] 3.4 Verify: TRT-LLM, vLLM, PyTorch all covered in action mapping

## 4. Decode Optimization Checklist

- [ ] 4.1 Add Phase 1 (characterization) steps 1-5 to reference/06-diagnosis-playbook.md
- [ ] 4.2 Add Phase 2 (optimization) steps 6-13
- [ ] 4.3 Add Phase 3 (verification) steps 14-16
- [ ] 4.4 Verify: checklist uses correct DRAM metric names (_op_ infix)
- [ ] 4.5 Verify: checklist references existing patterns O, P, Q by name

## 5. Gap Resolutions

- [ ] 5.1 Write and run G-4 cluster launch test kernel
- [ ] 5.2 Document G-4 result in reference/09-common-issues.md
- [ ] 5.3 Write and run G-7 bandwidth measurement kernel
- [ ] 5.4 Document G-7 result in reference/09-common-issues.md

## 6. End-to-End Validation

- [ ] 6.1 Phase 0: Create profile/validation_run/, add to .gitignore
- [ ] 6.2 Phase 1: Verify environment (nvidia-smi, nvcc, ncu, ncu_report)
- [ ] 6.3 Phase 2: Compile harness_template.cu with -arch=sm_120
- [ ] 6.4 Phase 3: Collect ncu reports (full + source sets)
- [ ] 6.5 Phase 4: Run analyze_reports.py, extract_stall_hotspots.py, plot_timeline.py
- [ ] 6.6 Phase 5: Apply six-dimension framework, verify meaningful values
- [ ] 6.7 Phase 6: Generate REPORT.md with evidence-backed findings

## 7. Cross-File Consistency & Cleanup

- [ ] 7.1 grep sweep: zero B200/sm_100 references outside docs/
- [ ] 7.2 Hardware number consistency check (170 SMs, 48 warps, 1.8 TB/s, etc.)
- [ ] 7.3 Metric name consistency check (all files use _op_ DRAM names)
- [ ] 7.4 Remove "unverified on sm_120" caveat from reference/08 header (Session 3 validated 93%)
