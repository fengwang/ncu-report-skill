# Session 1 Implementation Plan

---

## Execution Order

Tasks are ordered by dependency: SKILL.md first (smaller, establishes the pattern), then the programming guide (largest), then README.md (smallest), then verification.

The programming guide is written as a complete new file (full rewrite), not incremental edits, because the structure changes are too extensive for in-place editing.

---

## Task 1: SKILL.md Updates (Tasks 1.1–1.6)

### Step 1.1: Define verification test
```bash
# This must return empty after all SKILL.md edits
grep -i 'sm_100\|B200\|b200' SKILL.md
# This must return >= 1 match
grep -c 'sm_120' SKILL.md
```

### Step 1.2: Edit frontmatter
- File: `SKILL.md` lines 1-4
- Change `description`: "B200 / sm_100" → "RTX 5090 / sm_120"
- Change title: "B200 / Nsight Compute" → "RTX 5090 / Nsight Compute"

### Step 1.3: Edit target hardware line
- File: `SKILL.md` ~line 10
- Replace: "NVIDIA B200 (sm_100, CC 10.0, 148 SMs, 192 GB HBM3e)" → "NVIDIA GeForce RTX 5090 (sm_120, CC 12.0, 170 SMs, 32 GB GDDR7)"

### Step 1.4: Edit critical lessons
- File: `SKILL.md` ~lines 75-76
- Replace references to "B200" and "sm_100" with "RTX 5090" and "sm_120"

### Step 1.5: Update metric file reference
- File: `SKILL.md` ~line 57
- Note: The file `08-b200-metric-names.md` will be renamed in Session 2. For now, update the description text to say "sm_120 metric names" but keep the file path unchanged (file rename is out of blast radius).

### Step 1.6: Run verification
```bash
grep -i 'sm_100\|B200\|b200' SKILL.md  # must be empty
grep -c 'sm_120' SKILL.md  # must be >= 1
```

### Commit point: SKILL.md updated

---

## Task 2: Programming Guide — Full Rewrite (Tasks 2.1–6.6)

### Strategy
Write `blackwell-cuda-programming.md` as a complete new file. The structure is:

```
1. Target Platform & Verified Specs
2. Architecture Overview
3. Memory Hierarchy
4. Tensor Core Programming
5. Precision Spectrum & Roofline
6. LLM Inference Profiling
7. Preamble: Why This Document
8. Guideline Overview Table
9. Guidelines 1–16
10. Special Kernel Types
11. Pre-Coding Checklist
```

### Step 2.1: Define verification tests
```bash
# Must return empty
grep -rci 'sm_100\|B200\|b200\|HBM\|228 KB\|227 KB\|148 SM\|8 TB\|126 MB\|192 GB' blackwell-cuda-programming.md
# Must return >= 1
grep -c '1792\|1.792\|1.8 TB' blackwell-cuda-programming.md
grep -c '170' blackwell-cuda-programming.md
grep -c 'sm_120' blackwell-cuda-programming.md
# Must have LLM section
grep -c 'LLM Inference' blackwell-cuda-programming.md
```

### Step 2.2: Write sections 1–6 (new content)
Write the first half of the file: Target Platform through LLM Inference. These are entirely new sections with no B200 analog.

Key data to embed:
- Hardware table: all values from PRD §4.1
- GDDR7: 1,792 GB/s theoretical, ~1,500 GB/s effective
- Shared memory: 100 KB/SM, 48 KB default, 99 KB opt-in
- Roofline breakpoints: compute from PRD §4.3 throughput / 1.792 TB/s
- LLM: KV formula, 32 GB sizing examples, quantization comparison

### Step 2.3: Write sections 7–11 (adapted content)
Translate and adapt the existing Chinese content. Apply the number substitution table from the design. Every guideline gets RTX 5090 numbers.

### Step 2.4: Run verification tests from Step 2.1

### Commit point: Programming guide rewritten

---

## Task 3: README.md Updates (Tasks 7.1–7.3)

### Step 3.1: Define verification test
```bash
grep -i 'sm_100\|B200\|b200' README.md  # must be empty
```

### Step 3.2: Edit description
- Replace "B200 (sm_100)" with "RTX 5090 (sm_120)" in description paragraph

### Step 3.3: Edit requirements
- Update toolchain: "tested with 13.2" (already correct), "ncu 2026.2" (update from 2026.1)
- Update metric note: "sm_120 metric names"

### Step 3.4: Run verification

### Commit point: README.md updated

---

## Task 4: Full Verification (Tasks 8.1–8.4)

### Step 4.1: Run all deterministic checks from session contract
```bash
grep -rci 'sm_100\|B200\|b200' SKILL.md blackwell-cuda-programming.md README.md | grep -v ':0$'
grep -c 'sm_120' SKILL.md
grep -c '170' SKILL.md
grep -c '1792\|1.792\|1.8 TB' blackwell-cuda-programming.md
```

### Step 4.2: Manual review of hardware tables against PRD §4.1

### Step 4.3: Verify LLM section content
- Decode bandwidth analysis references ~1.8 TB/s
- KV-cache formula present
- Precision roofline table covers FP4–FP64

### Step 4.4: Verify tcgen05/TMEM/2CTA documentation
- Architecture overview states these are not available on sm_120
