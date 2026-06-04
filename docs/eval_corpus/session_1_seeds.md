# Eval Seeds from Session 1

## Seed 1: sm_120 ISA Assumption Trap

**Issue caught:** The evidence map and PRD assumed tcgen05/wgmma/TMEM would be available on sm_120 based on "Blackwell architecture" documentation. Live compilation testing proved all three are data-center-only.

**Eval question:** When adapting documentation between data-center and consumer variants of the same architecture, should feature availability be assumed or verified?

**Expected behavior:** Always verify via compilation test (`nvcc -arch=sm_120` with inline PTX) before writing guidance that assumes a feature exists. NVIDIA architecture docs describe the architecture family, not the specific compute capability.

**Regression test:**
```bash
# tcgen05 must NOT compile for sm_120
echo '__global__ void f(){asm volatile("tcgen05.alloc.cta_group::1.sync.aligned.shared::cta.b32 [%0], %1;" : : "r"(0u), "r"(32u));}' > /tmp/t.cu
nvcc -arch=sm_120 -c /tmp/t.cu 2>&1 | grep -q "not supported" && echo "PASS" || echo "FAIL"
```

## Seed 2: PRD Rounding Error

**Issue caught:** PRD §4.4 lists BF16 arithmetic intensity threshold as 116.8 FLOPs/byte. Correct value: 209.51 / 1.792 = 116.91 → rounds to 116.9.

**Eval question:** Should session acceptance criteria verify consistency between the PRD and the implementation, or only internal consistency?

**Expected behavior:** Flag PRD divergence as a finding. The skill files should use the mathematically correct value, not blindly copy the PRD.

## Seed 3: File Path Reference vs Content Reference

**Issue caught:** The deterministic check `grep -ri 'B200' ...` matches file paths to `reference/08-b200-metric-names.md` even though the surrounding text has been updated. This creates false positives in the acceptance criteria.

**Eval question:** Should deterministic grep checks exclude markdown link targets (file paths)?

**Expected behavior:** Either (a) the grep check should exclude hyperlink URLs/paths, or (b) the acceptance criteria should acknowledge file-path exceptions when the referenced file is outside the blast radius. Session 1 chose option (b) with inline annotations.

## Seed 4: Shared Memory Opt-In Resolved Early

**Issue caught:** Gap G-1 (shared memory opt-in max per block) was planned for Session 3 but resolved in Session 1 via a simple `cudaFuncSetAttribute` test. Result: 99 KB (101,376 bytes) with 1 KB reserved.

**Eval question:** Should low-effort validation gaps be resolved opportunistically in earlier sessions?

**Expected behavior:** Yes — if the test takes < 1 minute and provides high-value information for the current session's content (e.g., shared memory guidance), resolve it early. Update the evidence map to reflect the resolution.
