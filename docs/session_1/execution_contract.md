# Session 1 Execution Contract

---

## Planned File Changes

| File | Action | Estimated Lines |
|---|---|---|
| `SKILL.md` | Targeted edits (~15 changes) | ~92 lines (minor changes) |
| `blackwell-cuda-programming.md` | Full rewrite | ~700-800 lines (new content) |
| `README.md` | Targeted edits (~10 changes) | ~156 lines (minor changes) |

## Allowed Blast Radius

- `SKILL.md` — modify
- `blackwell-cuda-programming.md` — full rewrite
- `README.md` — modify
- `docs/session_1/*` — create (planning artifacts)

**Forbidden:** helpers/*, reference/*, .gitignore, any file not listed above.

## First Test to Write

```bash
# Baseline (should have matches now, should have 0 after implementation)
grep -rci 'sm_100\|B200\|b200' SKILL.md blackwell-cuda-programming.md README.md | grep -v ':0$'
```

## Checks After Each Task

| After Task | Check |
|---|---|
| Task 1 (SKILL.md) | `grep -i 'sm_100\|B200' SKILL.md` returns empty; `grep -c 'sm_120' SKILL.md` >= 1 |
| Task 2 (Programming guide) | `grep -rci 'sm_100\|B200\|b200\|HBM' blackwell-cuda-programming.md` returns 0; `grep -c 'LLM Inference' blackwell-cuda-programming.md` >= 1 |
| Task 3 (README.md) | `grep -i 'sm_100\|B200' README.md` returns empty |
| Task 4 (Full verification) | All session contract deterministic checks pass |

## Review Axes

Per session contract (medium risk):
1. **Correctness** — Do all hardware numbers match PRD §4.1?
2. **Architecture** — Is the guide self-consistent and properly structured?
3. **Performance** — Are roofline breakpoints and threshold values correctly calculated?

## Adversarial Verifier Brief

The verifier will attempt to falsify: "All B200 content is replaced with correct RTX 5090 content, and the programming guide accurately reflects sm_120 capabilities."

Attack vectors:
1. Search for any surviving B200-specific number (148, 228, 227, 64 warps, 32 blocks, 8 TB/s, 126 MB, 192 GB, HBM)
2. Check if tcgen05 code examples or TMEM guidance survived
3. Verify roofline breakpoints are calculated with 1.792 TB/s (not 8 TB/s)
4. Check LLM section for generic advice not tied to RTX 5090 constraints

## Concrete Done Condition

All of the following must be true:
1. `grep -rci 'sm_100\|B200\|b200' SKILL.md blackwell-cuda-programming.md README.md | grep -v ':0$'` returns empty
2. `grep -c 'sm_120' SKILL.md` returns >= 1
3. `grep -c '170' SKILL.md` returns >= 1 (SM count)
4. `grep -c '1792\|1.792\|1.8 TB' blackwell-cuda-programming.md` returns >= 1
5. `grep -c 'LLM Inference' blackwell-cuda-programming.md` returns >= 1
6. Hardware parameter table in SKILL.md matches PRD §4.1
7. Programming guide LLM section references ~1.8 TB/s bandwidth and 32 GB VRAM
8. Precision roofline table covers FP4, FP8, INT8, BF16, FP16, TF32, FP32
9. tcgen05, TMEM, 2CTA documented as "not available on sm_120"
