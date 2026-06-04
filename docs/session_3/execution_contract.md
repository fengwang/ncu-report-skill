# Session 3 Execution Contract

## Planned File Changes

| File | Change Type | Description |
|---|---|---|
| `helpers/ncu_utils.py` | Major modify | Rename metric list, update content, fix discovery |
| `helpers/analyze_reports.py` | Modify | Update import, add throughput constants |
| `helpers/extract_stall_hotspots.py` | Modify | Verify/update stall metric names |
| `helpers/plot_timeline.py` | Modify | Verify/update PM sampling metric names |
| `helpers/harness_template.cu` | Modify | Compile target sm_100 → sm_120 |
| `helpers/README.md` | Modify | Compile example, variable name, path |
| `SKILL.md` | Narrow fix | Filename reference only |
| `README.md` | Narrow fix | Filename reference only |

## Allowed Blast Radius

- All files in `helpers/` except `safetensors_loader.h` and `list_flashinfer_workloads.py`
- `SKILL.md` — filename reference only
- Root `README.md` — filename reference only
- Temp files in `/tmp` (not committed)

## Forbidden Files

- `reference/*`
- `blackwell-cuda-programming.md`
- `helpers/safetensors_loader.h`
- `helpers/list_flashinfer_workloads.py`

## First Test to Write

Metric validation script (Task 1-2): compile temp kernel → collect ncu report → extract metric names → diff against B200 list. This is the critical gate.

## Checks After Each Task

| After Task | Check |
|---|---|
| 1 (validation setup) | ncu report collected, metric list extracted |
| 2 (metric diff) | >=80% metrics confirmed present |
| 3 (gap experiments) | G-1, G-5, G-8 results documented |
| 4 (ncu_utils.py) | `grep -c 'B200_KEY_METRICS' helpers/ncu_utils.py` returns 0 |
| 5 (analyze_reports.py) | `grep -c '1792' helpers/analyze_reports.py` returns >= 1 |
| 6-7 (stall + timeline) | No B200 references in these files |
| 8-10 (harness + refs) | `grep -rci 'B200\|b200\|sm_100\|sm100' helpers/ | grep -v ':0$'` empty |
| 11 (final) | All deterministic checks pass |

## Review Axes (End of Session)

1. **Correctness**: Metric names match actual sm_120 output; constants match PRD
2. **Tests**: Validation procedure documented and reproducible
3. **Performance**: No impact (these are analysis scripts, not runtime code)

## Adversarial Verifier Brief

The verifier should check:
- That the metric list was actually validated against hardware (not just renamed)
- That stall metrics and PM sampling metrics were independently checked
- That throughput constants match PRD Section 4 values
- That no B200/sm_100 references remain in any in-scope file
- That the ncu_report discovery fallback actually works for package directories

## Concrete Done Condition

1. All 5 deterministic checks from session contract pass
2. Metric list validated with >=80% confirmed present on sm_120
3. All 5 evidence gaps (G-1, G-2, G-5, G-6, G-8) resolved with documented findings
4. Bandwidth constant ~1792 GB/s present in analyze_reports.py
5. No B200/sm_100 references in helpers/ or in the filename references of SKILL.md/README.md
