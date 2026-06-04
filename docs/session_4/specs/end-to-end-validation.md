# Specification: end-to-end-validation

## ADDED Requirements

### Requirement: End-to-end workflow validated on real hardware

The full 6-phase profiling workflow SHALL complete successfully on the local RTX 5090.

#### Scenario: Phase 0 — validation directory created
WHEN validation begins
THEN `profile/validation_run/` SHALL exist AND `profile/validation_run` SHALL appear in `.gitignore`

#### Scenario: Phase 1 — environment verified
WHEN environment check runs
THEN `nvidia-smi` SHALL show RTX 5090, `nvcc --version` SHALL show CUDA 13.2, `ncu --version` SHALL show 2026.2, `python3 -c "import ncu_report"` SHALL succeed

#### Scenario: Phase 2 — harness compiles
WHEN `nvcc -arch=sm_120 -lineinfo -o profile/validation_run/harness helpers/harness_template.cu` is run
THEN compilation SHALL succeed with exit code 0

#### Scenario: Phase 3 — ncu reports collected
WHEN ncu is run with `--set full` and `--set source` configurations
THEN two `.ncu-rep` files SHALL be produced in `profile/validation_run/reports/`

#### Scenario: Phase 4 — analyze_reports.py runs clean
WHEN `python3 helpers/analyze_reports.py profile/validation_run/reports/full.ncu-rep` is run
THEN it SHALL produce structured output with no "metric not found" errors

#### Scenario: Phase 4 — extract_stall_hotspots.py runs clean
WHEN `python3 helpers/extract_stall_hotspots.py profile/validation_run/reports/source.ncu-rep` is run
THEN it SHALL produce per-line stall ranking output

#### Scenario: Phase 4 — plot_timeline.py runs clean
WHEN `python3 helpers/plot_timeline.py profile/validation_run/reports/full.ncu-rep` is run
THEN it SHALL produce ASCII timeline output

#### Scenario: Phase 5 — six-dimension framework produces meaningful values
WHEN the parsed output is analyzed against the six-dimension framework
THEN each dimension (occupancy, tail effect, stalls, tensor core, timeline, memory) SHALL produce non-NaN, non-zero values

#### Scenario: Phase 6 — validation report generated
WHEN `profile/validation_run/REPORT.md` is reviewed
THEN it SHALL follow the template structure from `reference/07-report-template.md` AND contain evidence-backed findings with actual metric values (not placeholders)

### Requirement: Cross-file consistency confirmed

#### Scenario: No B200/sm_100 references outside docs/
WHEN `grep -rci 'B200\|b200\|sm_100\|sm100' --include='*.md' --include='*.py' --include='*.cu' --include='*.h' --exclude-dir=docs . | grep -v ':0$'` is run
THEN zero matches SHALL be returned

#### Scenario: Hardware numbers consistent
WHEN hardware parameters are checked across SKILL.md, blackwell-cuda-programming.md, reference docs, and helpers
THEN all SHALL reference: 170 SMs, 48 warps/SM, 24 blocks/SM, 100 KB shared/SM, 1.792 TB/s bandwidth, 96 MB L2, 32 GB VRAM
