# Review Policy

## Severity
- Critical: security/data-loss/destructive behavior or broken core invariant.
- High: production bug or contract violation that should block merge.
- Medium: likely bug or missing test that should be fixed soon.
- Low: maintainability concern with limited immediate impact.
- Nit: optional cleanup.

## Evidence Bar
- Every High/Critical finding must include concrete evidence.
- Missing tests are High only when they protect a contract requirement or prior bug.
- Do not report style issues already enforced by formatter/linter.

## Review Focus
- Correctness, security, regressions, edge cases, test quality, and architectural boundaries.

