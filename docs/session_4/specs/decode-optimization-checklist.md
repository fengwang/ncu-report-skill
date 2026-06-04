# Specification: decode-optimization-checklist

## ADDED Requirements

### Requirement: Decode optimization checklist in diagnosis playbook

`reference/06-diagnosis-playbook.md` SHALL contain a section titled "Single-User Decode Optimization Checklist" or equivalent, with ordered steps for optimizing single-token autoregressive decode on RTX 5090.

#### Scenario: Checklist exists in playbook
WHEN `grep -c 'Decode Optimization\|decode.*checklist\|Checklist.*Decode' reference/06-diagnosis-playbook.md` is run
THEN the count SHALL be >= 1

#### Scenario: Checklist has characterization phase
WHEN the checklist is reviewed
THEN Steps 1-5 SHALL cover bottleneck characterization: confirm decode kernel, DRAM BW utilization, tensor core utilization, dominant stall reason, L2 hit rate

#### Scenario: Checklist has optimization phase
WHEN the checklist is reviewed
THEN Steps 6-13 SHALL cover optimization actions: quantization, coalescing, KV-cache, occupancy, register spill, persistent L2, attention implementation, warp divergence

#### Scenario: Checklist has verification phase
WHEN the checklist is reviewed
THEN Steps 14-16 SHALL cover verification: re-profile, regression check, documentation

#### Scenario: Each step has metric and threshold
WHEN any checklist step is reviewed
THEN it SHALL specify: the ncu metric name, the RTX 5090 threshold, and the action if the check fails

#### Scenario: Checklist uses correct DRAM metric names
WHEN the checklist references DRAM metrics
THEN it SHALL use `dram__bytes_op_read` / `dram__bytes_op_write` (sm_120 names), not the old names

#### Scenario: Checklist references existing patterns
WHEN a checklist step overlaps with Pattern O, P, or Q
THEN it SHALL reference the pattern by name (e.g., "see Pattern O") rather than duplicating the content
