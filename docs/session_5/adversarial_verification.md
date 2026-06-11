# Session 5 Adversarial Verification

## Summary

| # | Adversarial Case | Verdict | Notes |
|---|---|---|---|
| 1 | No RTX 5090 GDDR7 implications in tile section | PASS (fixed) | Added GDDR7 bandwidth context note |
| 2 | Diagnosis patterns hypothetical | PARTIAL — Pattern S unvalidated | Caveat documented; Patterns R, T, U validated with real ncu data |
| 3 | Performance annotations not connected to ncu metrics | PASS | 5-row table with explicit metric names |
| 4 | Decision framework too simplistic | PASS | 6 factors with concrete bifurcations |
| 5 | Atomic contention is generic CUDA advice | PASS | Tile-specific (ct::sum + ct::atomic_add pattern) |
| 6 | Hint arch code 1200 unverified | PASS | Compiled and ran on sm_120 |
| 7 | TMA validation trivial | CONFIRMED | Hardware attribute only; compiler lowering unconfirmed; caveated in docs |
| 8 | SIMT content broken by version bump | PASS | Only 13.2→13.3 string replacements |
| 9 | Metric validation too trivial | PASS | 3 kernels: element-wise, GEMM/mma, reduction/atomics |
| 10 | Programming guide not actionable | PASS | Cross-referenced to workflow phases 2, 3, 5 |
| 11 | Stale 13.2 in unchecked files | PASS | Zero matches across all file types |

## Residual Risks

1. **Pattern S**: Partition_view vs gather diagnosis pattern lacks hardware-validated metric comparison. The pattern advice is directionally correct (prefer partition_view) but the specific metric trade-off is not quantified.
2. **TMA lowering**: The compiler may or may not generate TMA instructions for partition_view loads on sm_120. Hardware support is confirmed; compiler behavior is access-pattern-dependent and not verified via ncu metrics.

Both risks are explicitly disclosed in the documentation.
