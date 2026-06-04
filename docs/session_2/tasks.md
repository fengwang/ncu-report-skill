# Session 2 Tasks

## 1. Metric Names File Migration

- [ ] 1.1 Rename `reference/08-b200-metric-names.md` → `reference/08-rtx5090-metric-names.md` via git mv
- [ ] 1.2 Update title and all B200/sm_100 references in file content to RTX 5090/sm_120
- [ ] 1.3 Add "unverified on sm_120" annotations to all metric groups
- [ ] 1.4 Update discovery commands (`--chip gb202`, ncu version 2026.2)
- [ ] 1.5 Verify: `grep -ri 'B200\|sm_100' reference/08-rtx5090-metric-names.md` returns empty

## 2. Analysis Dimensions Recalibration

- [ ] 2.1 Update Dimension 1: SM count 148→170, warps 64→48, blocks 32→24, shared mem 228KB→100KB
- [ ] 2.2 Update Dimension 2: PM sampling note B200→RTX 5090
- [ ] 2.3 Update Dimension 4: tensor core ISA tcgen05→mma.sync/WMMA, remove TMEM reference
- [ ] 2.4 Update Dimension 5: PM sampling note B200→RTX 5090
- [ ] 2.5 Update Dimension 6: bandwidth references 8 TB/s→~1.8 TB/s
- [ ] 2.6 Update all "B200" and "sm_100" text references to "RTX 5090" and "sm_120"
- [ ] 2.7 Verify: all 6 deterministic checks for this file pass

## 3. Diagnosis Playbook Recalibration + LLM Patterns

- [ ] 3.1 Update Pattern A: grid threshold 148→170 SMs
- [ ] 3.2 Update Pattern B: tail effect SM count 148→170
- [ ] 3.3 Update Pattern C: add GDDR7 bandwidth impact note (~1.8 TB/s)
- [ ] 3.4 Update Pattern E: replace tcgen05.cp with cp.async, add sm_120 context
- [ ] 3.5 Update Pattern F: replace tcgen05.mma/wgmma/TMEM with mma.sync/WMMA, update TFLOPS figures
- [ ] 3.6 Update all remaining B200/sm_100 references in the file
- [ ] 3.7 Update all "Blackwell principle N" cross-references to named section headings
- [ ] 3.8 Add Pattern O — Decode bandwidth ceiling
- [ ] 3.9 Add Pattern P — KV-cache thrashing
- [ ] 3.10 Add Pattern Q — Quantization mismatch
- [ ] 3.11 Verify: `grep -ri 'B200\|sm_100' reference/06-diagnosis-playbook.md` returns empty
- [ ] 3.12 Verify: Patterns O, P, Q present with signal/cause/fix structure

## 4. Minor Reference File Updates

- [ ] 4.1 Update `reference/00-directory-layout.md`: compile flags sm_100→sm_120, example dir b200→rtx5090
- [ ] 4.2 Update `reference/02-harness-guide.md`: compile flags sm_100→sm_120
- [ ] 4.3 Update `reference/03-collection.md`: "B200, ncu 2026.1" → "RTX 5090, ncu 2026.2"
- [ ] 4.4 Update `reference/04-python-api.md`: ncu_report path 2026.1.0→2026.2.0, metric file links
- [ ] 4.5 Update `reference/07-report-template.md`: GPU line, compile flags, bandwidth
- [ ] 4.6 Verify: zero B200/sm_100 matches in all 5 minor files

## 5. Workflow — Framework Profiling Guidance

- [ ] 5.1 Add Phase 2.5 section to `reference/01-workflow.md` for framework kernel identification
- [ ] 5.2 Verify: Phase 2.5 exists with TensorRT-LLM, vLLM, PyTorch guidance

## 6. Common Issues — Consumer GPU Section

- [ ] 6.1 Update B200 references in `reference/09-common-issues.md` to RTX 5090
- [ ] 6.2 Add consumer GPU-specific issues section (display driver, power throttling, compositor, boost clocks)
- [ ] 6.3 Update ncu_report path and metric file references
- [ ] 6.4 Verify: zero B200/sm_100 matches in 09-common-issues.md

## 7. Final Verification

- [ ] 7.1 Run all deterministic checks from session contract
- [ ] 7.2 Verify all 10 reference files have zero B200/sm_100 references
- [ ] 7.3 Verify old metric names file is gone and new one exists
