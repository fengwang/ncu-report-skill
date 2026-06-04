# Session 2 Eval Seeds

## Seed 1: Pattern letter collision detection
**Trigger:** Session plan specifies pattern IDs that collide with existing patterns
**Expected behavior:** Detect collision during brainstorming, propose alternative IDs before implementation
**What happened:** Session plan said I/J/K but existing patterns already used those letters. Caught during brainstorming, resolved as O/P/Q.
**Regression check:** `grep -c 'Pattern O\|Pattern P\|Pattern Q' reference/06-diagnosis-playbook.md` should return >= 3

## Seed 2: Contract YAML stale after brainstorming decisions
**Trigger:** Contract written before brainstorming changes a key decision (pattern IDs)
**Expected behavior:** Flag that contract deterministic checks may reference stale values
**What happened:** Contract YAML check `grep -c 'Pattern I|Pattern J|Pattern K'` matched existing patterns (not the new LLM ones), giving a false positive. The actual check should be `Pattern O|Pattern P|Pattern Q`.
**Lesson:** When brainstorming changes a plan-level decision, verify that contract deterministic checks still test the right thing.

## Seed 3: Cross-reference maintenance after restructure
**Trigger:** Session 1 restructures a document; Session 2 must update cross-references in dependent documents
**Expected behavior:** Map old numbered references to new named sections
**What happened:** All "Blackwell principle N" cross-references in the diagnosis playbook were updated to named section headings from the restructured programming guide.
**Regression check:** `grep -c 'Blackwell principle' reference/06-diagnosis-playbook.md` should return 0

## Seed 4: File rename propagation across references
**Trigger:** File renamed (08-b200-metric-names.md → 08-rtx5090-metric-names.md)
**Expected behavior:** All files referencing the old filename must be updated
**What happened:** Updated references in 04-python-api.md, 07-report-template.md, 09-common-issues.md. However, SKILL.md and README.md (outside blast radius) still reference the old filename.
**Regression check:** `grep -rn '08-b200' reference/` should return empty
**Remaining debt:** SKILL.md and README.md still need updating (Session 3 scope)

## Seed 5: Data-center-only ISA in consumer GPU documentation
**Trigger:** Documentation references ISA features (tcgen05, wgmma, TMEM) not available on target GPU
**Expected behavior:** Replace with available ISA or clearly mark as unavailable
**What happened:** Session 1 discovered sm_120 lacks tcgen05/wgmma/TMEM. Session 2 replaced all fix-direction references with sm_120-available ISA (cp.async, mma.sync/WMMA).
**Regression check:** `grep -n 'tcgen05\|wgmma\|TMEM' reference/06-diagnosis-playbook.md` should only show "not available" disclaimers, not recommendations
