# Spec: Consumer GPU Troubleshooting (NC-3)

## ADDED Requirements

### Requirement: Consumer GPU-Specific Issues Section

The common issues document (`09-common-issues.md`) SHALL include a dedicated section for consumer GPU-specific profiling issues that do not apply to data-center GPUs.

The section SHALL cover:
- Display driver interference: desktop compositor competing for GPU cycles
- Power throttling: 575W TDP may throttle under sustained profiling load
- Boost clock variability: consumer GPUs have less predictable sustained clocks than data-center GPUs
- GPU shared with desktop: X11/Wayland compositor uses GPU memory and cycles

#### Scenario: Profiling jitter on RTX 5090
WHEN a user sees inconsistent profiling results across runs on RTX 5090
THEN the consumer GPU issues section SHALL guide them to check display driver interference, lock clocks, and consider closing the desktop compositor

#### Scenario: Power throttling during profiling
WHEN ncu replays cause sustained high GPU load and results show unexpectedly low throughput
THEN the section SHALL advise checking `nvidia-smi -q -d POWER` for throttling and suggest clock locking
