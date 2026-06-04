# RTX 5090 (sm_120) Metric Name Reference

> **Validation status:** Validated on RTX 5090 (sm_120) with Nsight Compute 2026.2. Session 3 confirmed 93 of 100 original metrics present; 7 DRAM metrics required an `_op_` infix rename (all corrected in this document). Metric names can change between compute capability versions — always verify with `action.metric_names()`.

This document lists metric names validated on the local RTX 5090 with Nsight Compute 2026.2. Names that differ from earlier compute capability versions are listed in the rename table below.

If a metric returns `None` on your kernel, first check this doc, then enumerate available names:

```python
action.metric_names()
```

---

## Metric names that changed

| Stock skill name (older GPU) | RTX 5090 / sm_120 name (validated) |
|---|---|
| `smsp__inst_executed_op_global_ld.sum` | **`smsp__sass_inst_executed_op_global_ld.sum`** |
| `smsp__inst_executed_op_global_st.sum` | **`smsp__sass_inst_executed_op_global_st.sum`** |
| `smsp__inst_executed_op_local_ld.sum` | **`smsp__sass_inst_executed_op_local_ld.sum`** |
| `smsp__inst_executed_op_local_st.sum` | **`smsp__sass_inst_executed_op_local_st.sum`** |
| `smsp__inst_executed_op_shared_ld.sum` | **`smsp__sass_inst_executed_op_shared_ld.sum`** |
| `smsp__inst_executed_op_shared_st.sum` | **`smsp__sass_inst_executed_op_shared_st.sum`** |
| `l1tex__average_t_sectors_per_request_pipe_lsu_mem_global_op_ld.ratio` | (not available directly; compute from `l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum / l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum`) |
| `dram__bytes.sum` | (not directly; use `dram__bytes_op_read.sum + dram__bytes_op_write.sum`) |
| `sm__inst_executed_pipe_fmaheavy.*` | *not present on Blackwell* — use `sm__inst_executed_pipe_fma.*` instead |
| `smsp__warps_issue_stalled_<reason>_per_issue_active.pct` | **`smsp__average_warps_issue_stalled_<reason>_per_issue_active.ratio`** (note `average_` prefix and `ratio` suffix) |

---

## Canonical sm_120 metric set (curated, validated)

These metric names have been validated on the local RTX 5090 (sm_120) with Nsight Compute 2026.2. Session 3 confirmed 93 of 100 original metrics present (7 DRAM metrics required an `_op_` infix rename, all corrected below). 3 pcsamp stall metrics were added for completeness (103 total). Always verify for your specific ncu version by enumerating with `action.metric_names()` — NVIDIA occasionally renames metrics between compute capability versions.

### Launch geometry / occupancy
```
launch__grid_size
launch__block_size
launch__grid_dim_x, launch__grid_dim_y, launch__grid_dim_z
launch__block_dim_x, launch__block_dim_y, launch__block_dim_z
launch__thread_count
launch__waves_per_multiprocessor
launch__registers_per_thread
launch__shared_mem_per_block
launch__shared_mem_per_block_static
launch__shared_mem_per_block_dynamic
launch__occupancy_limit_blocks
launch__occupancy_limit_registers
launch__occupancy_limit_shared_mem
launch__occupancy_limit_warps
device__attribute_multiprocessor_count
device__attribute_max_warps_per_multiprocessor
sm__maximum_warps_per_active_cycle_pct              # theoretical occupancy %
```

### SOL (Speed-of-Light) / throughput
```
sm__throughput.avg.pct_of_peak_sustained_elapsed
gpu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed
gpu__compute_memory_access_throughput.avg.pct_of_peak_sustained_elapsed
gpu__compute_memory_request_throughput.avg.pct_of_peak_sustained_elapsed
l1tex__throughput.avg.pct_of_peak_sustained_active
lts__throughput.avg.pct_of_peak_sustained_elapsed
dram__bytes_op_read.sum
dram__bytes_op_read.sum.pct_of_peak_sustained_elapsed
dram__bytes_op_read.sum.per_second                       # achieved BW
dram__bytes_op_write.sum
dram__bytes_op_write.sum.pct_of_peak_sustained_elapsed
dram__sectors_op_read.sum
dram__sectors_op_write.sum
```

### Timing
```
gpu__time_duration.sum                                # units: ns (check .unit())
smsp__cycles_active.avg
smsp__issue_active.avg.per_cycle_active               # issue rate per scheduler
smsp__issue_active.avg.pct_of_peak_sustained_active
```

### Warp activity
```
sm__warps_active.avg.pct_of_peak_sustained_active     # achieved occupancy %
sm__warps_active.avg.per_cycle_active
sm__warps_active.max.per_cycle_active
sm__warps_active.min.per_cycle_active
smsp__warps_active.avg.per_cycle_active               # per sub-partition
smsp__warps_eligible.avg.per_cycle_active
smsp__warps_eligible.max.per_cycle_active
```

### Compute pipelines
```
sm__inst_executed.avg.per_cycle_active                # IPC
sm__inst_executed_pipe_fma.avg.pct_of_peak_sustained_active
sm__inst_executed_pipe_fma.avg.pct_of_peak_sustained_elapsed
sm__inst_executed_pipe_alu.avg.pct_of_peak_sustained_active
sm__inst_executed_pipe_alu.avg.pct_of_peak_sustained_elapsed
sm__inst_executed_pipe_lsu.avg.pct_of_peak_sustained_active
sm__inst_executed_pipe_lsu.avg.pct_of_peak_sustained_elapsed
sm__inst_executed_pipe_xu.avg.pct_of_peak_sustained_active
sm__inst_executed_pipe_fp64.avg.pct_of_peak_sustained_active
sm__inst_executed_pipe_adu.avg.pct_of_peak_sustained_active

sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_active
sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed
sm__pipe_tensor_subpipe_hmma_cycles_active.avg.pct_of_peak_sustained_elapsed
sm__pipe_tensor_subpipe_imma_cycles_active.avg.pct_of_peak_sustained_elapsed
sm__pipe_tensor_subpipe_dmma_cycles_active.avg.pct_of_peak_sustained_elapsed
sm__ops_path_tensor_op_hmma_src_bf16_dst_fp32_sparsity_off.avg   # raw BF16→FP32 tensor ops
```

### Cache hit rates
```
l1tex__t_sector_hit_rate.pct                                       # overall L1
lts__t_sector_hit_rate.pct                                         # overall L2
l1tex__t_sector_pipe_lsu_mem_global_op_ld_hit_rate.pct             # L1 hit on global loads
l1tex__t_sector_pipe_lsu_mem_global_op_st_hit_rate.pct             # L1 hit on global stores
```

### Memory access counts & sectors
```
smsp__sass_inst_executed_op_global_ld.sum                          # global LD instruction count
smsp__sass_inst_executed_op_global_st.sum                          # global ST count
smsp__sass_inst_executed_op_local_ld.sum                           # local LD (register spill)
smsp__sass_inst_executed_op_local_st.sum                           # local ST (register spill)
smsp__sass_inst_executed_op_shared.sum                             # total shared mem ops
smsp__sass_inst_executed_op_shared_ld.sum
smsp__sass_inst_executed_op_shared_st.sum

l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum                     # L1 sectors for global LD
l1tex__t_sectors_pipe_lsu_mem_global_op_ld_lookup_hit.sum
l1tex__t_sectors_pipe_lsu_mem_global_op_ld_lookup_miss.sum
l1tex__t_sectors_pipe_lsu_mem_global_op_st.sum                     # L1 sectors for global ST
l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum                    # LD request count
l1tex__t_requests_pipe_lsu_mem_global_op_st.sum                    # ST request count
# sectors/request = sectors.sum / requests.sum (ideal = 4 for 128B coalesced)
smsp__sass_average_data_bytes_per_sector_mem_global_op_st.ratio    # store efficiency (max 32)
```

### Stall reasons — aggregate ratios
```
smsp__average_warps_issue_stalled_long_scoreboard_per_issue_active.ratio
smsp__average_warps_issue_stalled_short_scoreboard_per_issue_active.ratio
smsp__average_warps_issue_stalled_wait_per_issue_active.ratio
smsp__average_warps_issue_stalled_barrier_per_issue_active.ratio
smsp__average_warps_issue_stalled_membar_per_issue_active.ratio
smsp__average_warps_issue_stalled_math_pipe_throttle_per_issue_active.ratio
smsp__average_warps_issue_stalled_mio_throttle_per_issue_active.ratio
smsp__average_warps_issue_stalled_lg_throttle_per_issue_active.ratio
smsp__average_warps_issue_stalled_tex_throttle_per_issue_active.ratio
smsp__average_warps_issue_stalled_not_selected_per_issue_active.ratio
smsp__average_warps_issue_stalled_branch_resolving_per_issue_active.ratio
smsp__average_warps_issue_stalled_dispatch_stall_per_issue_active.ratio
smsp__average_warps_issue_stalled_drain_per_issue_active.ratio
smsp__average_warps_issue_stalled_no_instruction_per_issue_active.ratio
smsp__average_warps_issue_stalled_sleeping_per_issue_active.ratio
smsp__average_warps_issue_stalled_misc_per_issue_active.ratio
smsp__average_warps_issue_stalled_selected_per_issue_active.ratio       # productive (= 1.0)
```

### Stall reasons — per-PC (requires `--set source --section SourceCounters`)
```
smsp__pcsamp_sample_count                                           # total sample count
smsp__pcsamp_warps_issue_stalled_long_scoreboard                    # per-PC counts
smsp__pcsamp_warps_issue_stalled_short_scoreboard
smsp__pcsamp_warps_issue_stalled_wait
smsp__pcsamp_warps_issue_stalled_barrier
smsp__pcsamp_warps_issue_stalled_math_pipe_throttle
smsp__pcsamp_warps_issue_stalled_mio_throttle
smsp__pcsamp_warps_issue_stalled_lg_throttle
smsp__pcsamp_warps_issue_stalled_tex_throttle
smsp__pcsamp_warps_issue_stalled_not_selected
smsp__pcsamp_warps_issue_stalled_dispatch_stall
smsp__pcsamp_warps_issue_stalled_drain
smsp__pcsamp_warps_issue_stalled_no_instructions
smsp__pcsamp_warps_issue_stalled_selected
smsp__pcsamp_warps_issue_stalled_branch_resolving
smsp__pcsamp_warps_issue_stalled_membar
```

Each of these has `num_instances() > 0` with `correlation_ids()` that map to PCs. Use `action.source_info(pc)` to map PCs to `(file, line)`.

### PM sampling (time series) — sm_120 hardware-counter metrics

On sm_120, PM sampling provides hardware-counter timeseries rather than the per-stall-reason breakdowns available on earlier architectures. The stall-reason timeseries (`pmsampling:smsp__warps_issue_stalled_*`) do **not** exist on sm_120.

**Validated on RTX 5090 with ncu 2026.2:**
```
pmsampling:smsp__warps_active.sum
pmsampling:dram__bytes.avg.pct_of_peak_sustained_elapsed
pmsampling:dram__bytes.sum.per_second
pmsampling:l1tex__data_pipe_lsu_wavefronts.avg.pct_of_peak_sustained_elapsed
pmsampling:sm__inst_executed_pipe_alu_size_64b_realtime.avg.pct_of_peak_sustained_elapsed
pmsampling:sm__pipe_fma_cycles_active_realtime.avg.pct_of_peak_sustained_elapsed
pmsampling:pcie__throughput.avg.pct_of_peak_sustained_elapsed
pmsampling:gpc__cycles_elapsed.avg.per_second
```

Note: some `pmsampling:` metrics may return empty instance arrays depending on ncu version / driver / GPU pair — always check `m.num_instances() > 0` before using.

---

## Discovering metrics on RTX 5090

```bash
# All available metrics for RTX 5090 (GB202 die)
ncu --query-metrics --chip gb202

# Filter by name pattern
ncu --query-metrics --chip gb202 | grep -i pmsampling
ncu --query-metrics --chip gb202 | grep -i issue_stalled

# Other chip names for reference: gh200 (H200 / Hopper), ga102 (Ampere), etc.
```

From Python, you can also enumerate per-report:
```python
all_names = action.metric_names()      # all metrics collected in this report
```

---

## Gotchas

1. **Metric exists in ncu's list but returns `None` from Python**: the metric wasn't *collected* in this report. Rerun ncu with the right `--section` or `--set`.
2. **Metric value is `0.0`**: either the hardware counter reports zero (e.g., no tensor core activity), or the metric is synthetic and depends on other metrics that weren't collected.
3. **`.avg` vs `.sum` vs `.max`**: each aggregate is a separate metric name. `.avg` is most commonly useful for rates / percentages; `.sum` for counts; `.max` for worst-case analysis.
4. **`pct_of_peak_sustained_elapsed` vs `pct_of_peak_sustained_active`**: `_elapsed` normalizes against total kernel time (including idle SMs); `_active` normalizes against cycles where the SM was actually running. `_elapsed` is more honest for under-utilized kernels.
