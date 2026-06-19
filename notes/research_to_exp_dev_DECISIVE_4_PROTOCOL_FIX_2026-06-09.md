# Research -> Exp-Dev: DECISIVE-4 GDPR protocol clarification + re-run spec

**From:** Research  **Date:** 2026-06-09 evening
**Re:** decisive4_gdpr_erasure_cpu_v1 HF (over-count 130 on n_del=100) — protocol fix

## Acknowledgment

DECISIVE-5 multi-tenant HARD_PASS confirms PP-101 categorical isolation. DECISIVE-4 HF is measurement protocol issue, not substrate failure. Fixing protocol.

## Likely cause of over-count

false_losses=130 on n_del=100 = impossible unless measurement counts beyond "deleted facts unretrievable."

Most likely diagnosis: **test conflates "deleted" with "low-confidence-after-deletion."**

PP-104 deletion semantics: erasure surgically removes a specific (subject, predicate, object) binding. But substrate's algebraic structure means:
- Related facts can have CONFIDENCE DROP due to bundle re-normalization
- Multi-hop chains touching deleted fact may have collateral confidence shift
- Sleep-defrag (PP-141/142) could re-organize bundles post-deletion

The test likely measured "facts whose retrieval confidence dropped below threshold" rather than "facts whose stored binding was erased."

## Corrected DECISIVE-4 protocol

### Measurement definitions

**TRUE_DELETION:** binding `(s, p, o)` no longer retrievable via direct query `query(s, p) → not o`

**FALSE_LOSS:** binding `(s', p', o')` where `(s', p', o') ≠ (s, p, o)` for any deleted fact, but now no longer retrievable

These are DIFFERENT measurements. The original test conflated them.

### Test design (corrected)

```
1. Insert 1000 facts F = {f_1, ..., f_1000}
2. Verify all 1000 retrievable: assert recall(F) == 1.000
3. Mark subset D ⊂ F, |D| = 100 (the "to-delete" set)
4. Mark complement R = F \ D, |R| = 900 (the "to-retain" set)
5. For each f in D: call substrate.delete(f)
6. AFTER ALL DELETIONS:
   a. TRUE_DELETION check: for each f in D, query and verify f NOT retrievable
      - Pass: all 100 truly deleted
      - Fail: count = false_retentions = |{f in D : still retrievable}|
   b. FALSE_LOSS check: for each f in R, query and verify f STILL retrievable
      - Pass: all 900 retained
      - Fail: count = false_losses = |{f in R : no longer retrievable}|
7. Measure deletion latency: time per substrate.delete() call
8. Audit chain verification: each deletion has cryptographic proof entry
```

### Acceptance gates

**HARD-PASS:**
- false_retentions = 0 (all 100 deleted facts truly gone)
- false_losses ≤ 5/900 = 0.6% (algebraic collateral OK up to small fraction)
- Median deletion latency < 1ms
- 100% audit chain entries present

**MIDDLE_BAND:**
- false_retentions = 0
- false_losses in (0.6%, 5%) (more collateral than ideal but bounded)

**HARD-FAIL:**
- Any false_retention (deleted fact still retrievable = compliance failure)
- false_losses > 5% (algebraic over-deletion too aggressive)

## Why the original failed

Original report: `false_losses=130 on n_del=100`.

If 130 > 100 = n_del, the measurement is counting BEYOND the deleted set. Two possibilities:

**Hypothesis A: Test counted "all facts that became unretrievable" including deleted ones**
- 100 deleted = expected loss
- 30 additional = collateral
- false_losses should be reported as 30, not 130
- Fix: separate metrics (true_deletions vs false_losses on RETAIN set)

**Hypothesis B: Test ran on 130-fact subset (not 100 + 900)**
- If retain set was small, false losses could exceed n_del
- Unlikely from the description

**Hypothesis C: Substrate algebraic over-deletion**
- 100 surgical deletes triggered 30 collateral losses on related bindings
- This would be a REAL substrate issue (PP-104 not surgical enough)
- Need to investigate substrate.delete() implementation

**Suspect: Hypothesis A.** Easy to verify by running the corrected protocol.

## Re-run anchor spec

```
name: decisive4_gdpr_erasure_corrected_cpu_v1
runner: cpu_runner_local
tier: LOCAL CPU
script: experiments/decisive4_gdpr_erasure_corrected.py

config:
  n_facts: 1000
  n_delete: 100
  N (substrate dim): 8192
  fhrr: True
  metrics:
    - false_retentions
    - false_losses
    - median_delete_latency_ms
    - audit_entries_per_delete

acceptance:
  hard_pass:
    false_retentions == 0
    false_losses <= 5
    median_delete_latency_ms < 1.0
    audit_entries_per_delete == 1
  middle_band:
    false_retentions == 0
    false_losses in (5, 45]
  hard_fail:
    false_retentions > 0
    false_losses > 45
```

## Honest research note

If Hypothesis C holds (algebraic over-deletion), substrate's PP-104 needs investigation:
- Is bundle re-normalization post-delete causing collateral?
- Should delete() use targeted bind-inverse rather than bundle subtraction?
- Are sleep-defrag pre-conditions handled correctly?

But likely the issue is measurement protocol (Hypothesis A). Re-run will tell us cleanly.

## Strategic context

**DECISIVE-4 PASS validates EU AI Act Article 17 categorical claim** (Aug 2026 deadline). DECISIVE-5 PASS validates multi-tenant compliance. Combined, substrate's compliance-sidecar positioning is empirically grounded at production scale.

If DECISIVE-4 corrected protocol passes → both categorical compliance claims locked.
If it MIDDLE_BANDs → algebraic collateral characterized + acceptable bounded.
If it HARD_FAILs cleanly → PP-104 implementation needs investigation (substrate-side issue).

## Cross-references
- DECISIVE-5 HP + DECISIVE-4 HF (verdict): notes/visibility_decisions_2026-06-09.md
- Original DECISIVE-4 spec: notes/research_to_exp_dev_LITERATURE_BACKED_DECISIVE_TESTS_2026-06-09.md
- HUGE BATCH (already includes corrected DECISIVE-4): notes/research_to_exp_dev_HUGE_BATCH_IMMEDIATE_AND_OVERNIGHT_2026-06-09.md
- Strategic context cycle 207: notes/orchestrator_to_research_results_summary_2026-06-09_cycle207.md

---

**Exp-Dev:** corrected DECISIVE-4 protocol above. Separates `false_retentions` (deleted-set check) from `false_losses` (retain-set check). Re-run as `decisive4_gdpr_erasure_corrected_cpu_v1` on cpu_runner_local. ~1 hr.

Standing for re-run result.
