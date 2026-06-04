#!/usr/bin/env python3
"""ASCII-plot PM sampling timeseries from .ncu-rep files.

PM sampling metrics (those prefixed `pmsampling:`) have per-instance values
that form a time-ordered series across the kernel's execution. Plotting the
series reveals tail effects, pipeline bubbles, and sawtooth patterns that
are invisible in aggregate metrics.

Produces `<run-dir>/analysis/pm_timeline_plots.txt` with ASCII plots for each
requested metric.

Usage:
    python3 plot_timeline.py --run-dir profile/myrun \\
            --report profile/myrun/reports/full_<tag>.ncu-rep --tag <tag>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ncu_utils import load_action, per_instance_values  # noqa: E402


# Default metric list — validated against RTX 5090 / sm_120 with ncu 2026.2.
# sm_120 PM sampling provides hardware-counter timeseries rather than the
# per-stall-reason breakdowns available on earlier architectures. The plotter
# shows "no data" for any metric that doesn't populate on a given report.
DEFAULT_METRICS = [
    "pmsampling:smsp__warps_active.sum",
    "pmsampling:dram__bytes.avg.pct_of_peak_sustained_elapsed",
    "pmsampling:dram__bytes.sum.per_second",
    "pmsampling:l1tex__data_pipe_lsu_wavefronts.avg.pct_of_peak_sustained_elapsed",
    "pmsampling:sm__inst_executed_pipe_alu_size_64b_realtime.avg.pct_of_peak_sustained_elapsed",
    "pmsampling:sm__pipe_fma_cycles_active_realtime.avg.pct_of_peak_sustained_elapsed",
    "pmsampling:pcie__throughput.avg.pct_of_peak_sustained_elapsed",
    "pmsampling:gpc__cycles_elapsed.avg.per_second",
]


def ascii_plot(vals, label, max_rows=20, max_cols=80):
    """Return list of ASCII strings rendering the timeseries."""
    if not vals:
        return [f"{label}: no data"]

    # Filter None → 0
    vals = [v if v is not None else 0.0 for v in vals]

    # Trim leading/trailing zeros
    lead = 0
    for v in vals:
        if v > 0: break
        lead += 1
    trail = 0
    for v in reversed(vals):
        if v > 0: break
        trail += 1
    active = vals[lead:len(vals) - trail] if trail else vals[lead:]
    n = len(active)
    if n == 0:
        return [f"{label}: all zero"]

    # Bucket into max_cols columns
    ncols = min(max_cols, n)
    bucket_size = max(1, n // ncols)
    buckets = []
    for c in range(ncols):
        s = c * bucket_size
        e = min(n, (c + 1) * bucket_size)
        chunk = active[s:e]
        buckets.append(sum(chunk) / len(chunk) if chunk else 0.0)
    mx = max(buckets) if buckets else 1.0
    if mx == 0:
        mx = 1.0

    lines = [f"\n{label}",
             f"  (n={n} active samples, leading_zero={lead}, trailing_zero={trail}, max={mx:.3g})"]
    for r in range(max_rows, 0, -1):
        threshold = mx * r / max_rows
        row = "".join("#" if b >= threshold else " " for b in buckets)
        lines.append(f"  {threshold:8.2g} | {row}")
    lines.append("  " + " " * 10 + "-" * len(buckets))
    lines.append("  " + " " * 10 + " (time →)")
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--report", type=Path, action="append", required=True)
    ap.add_argument("--tag", type=str, action="append", required=True)
    ap.add_argument("--metric", type=str, action="append", default=None,
                    help="Override default metric list.")
    ap.add_argument("--rows", type=int, default=20)
    ap.add_argument("--cols", type=int, default=80)
    args = ap.parse_args()

    if len(args.report) != len(args.tag):
        ap.error("--report and --tag counts must match")

    metrics = args.metric or DEFAULT_METRICS
    analysis_dir = args.run_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    out_lines = []
    for rep, tag in zip(args.report, args.tag):
        if not rep.exists():
            print(f"[skip] {rep} not found", file=sys.stderr)
            continue
        action = load_action(rep)
        out_lines.append(f"\n{'=' * 60}\n{tag}: {rep.name}\n{'=' * 60}")
        for m in metrics:
            vals = per_instance_values(action, m)
            if vals is None:
                out_lines.append(f"\n{m}: no instances")
                continue
            out_lines.extend(ascii_plot(vals, m, args.rows, args.cols))

    out_path = analysis_dir / "pm_timeline_plots.txt"
    out_path.write_text("\n".join(out_lines))
    print(f"-> {out_path}")


if __name__ == "__main__":
    main()
