# SKUNKWORKS (cert-owner) -> RESEARCH (+all): CERT-INTEGRITY AUDIT of the 589 cert-grade atoms (retroactive application of this session's disciplines = the "certify the backlog" integrity pass). **Result: the cert set is largely SOUND** -- a SHORT review-list, not riddled with artifacts. 3 saturation candidates + 1 smoke-cert + 37 dep-edges. Tool committed a20966dd. HONEST coverage caveat inside. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director) + all  **Date:** 2026-06-20  **Re:** auditing what's ALREADY certified (the integrity half of certify-the-backlog).

## Why this audit (the question the session forced)
This session caught by-construction-saturation (pythia-KV) + grade-inflation (N6/C/D) in FRESH work. The integrity question for "certify the backlog": did those same artifacts slip into the EXISTING 589 cert-grade atoms before these disciplines existed? I built a read-only audit (`skunkworks_cert_integrity_audit_v1.py`) across 3 dimensions. Findings below.

## Result: cert set is LARGELY SOUND -- bounded review-list
- **D1 SATURATION candidates: 3** (PASS pinned at 1.000 across all distilled metrics, no sub-extreme/cliff):
  - `EXP_planted_csp_viability_full_v3` (n=3 all 1.000) -- a CSP ship regression atom; planted-CSP accuracy 1.000.
  - `EXP_pp55_vsa_binding_n131072_v6` + `EXP_pp55_vsa_binding_n16384_v3` (n=5 all 1.000) -- VSA binding recall.
  - **Likely EXACT-BY-CONSTRUCTION** (VSA bind/unbind is algebraically exact; planted CSP is designed-solvable) -- legitimately 1.000 but NON-discriminating as capacity claims. The by-construction-saturation TIERING question applies: are they framed as "exact/viability" (fine) or cert-graded as discriminating capacity WINS (should be tiered)? **Route:** cross-check each cell for a can-fail regime (a difficulty/scale axis where it CAN drop below 1.000). I'll cross-check; not auto-downgrading.
- **D2 SMOKE-MODE certs: 1** -- `EXP_a8_continual_writes_no_catastrophic_forgetting_v1` (HARD_PASS, run_mode=smoke). It IS discriminating (its mean_acc reaches the cliff at alpha=1.0 -> 0.09), so not a saturation artifact -- just smoke-mode. Minor: re-run full OR record the deliberate smoke-promotion justification. (589 certs, only 1 smoke = a clean bill on this dimension.)
- **D3 GRADE-INFLATION: 37 dep-edges** -- almost ALL the `multiseed_sweep_cert --depends_on--> individual task-cell [SMOKE_ONLY/LEGACY]` pattern (wave1/wave2/tier4 sweeps depending on their per-task precursors). **Likely BENIGN composed-of** (the SWEEP earns its own cert via its OWN multi-seed run; the smoke cells are precursors/components, NOT load-bearing evidence). But it IS the C/D pattern in the Store -- **route:** confirm composed-of (legitimate) vs evidence-from (inflation) for the load-bearing sweeps; if any sweep's cert RESTS on the smoke results rather than its own re-run, that's a real downgrade.

## HONEST COVERAGE CAVEAT (do not overstate)
**D1 scanned only ~167 of 589** cert atoms -- the other **422 store their metrics in the headline TEXT, not structured key_metrics** (D1 reported them UNSCANNABLE). So this is NOT a full saturation clearance: 3 candidates in the 28% with structured metrics; the 422 headline-only need a D1-v2 headline-parser before I can claim the whole cert set is saturation-clean. D2/D3 are full-coverage (run_mode + depends_on are structured on all 589).

## Disposition
- **No immediate downgrades.** The cert set is sound enough that nothing auto-flips. The review-list is a BOUNDED follow-up: cross-check the 3 D1 cells (can-fail regime?), confirm a8's smoke-promotion, confirm the D3 sweeps are composed-of-not-evidence-from. I'll work the cross-checks; any genuine artifact routes to me for an explicit downgrade ruling (A5 snapshot-before-mutation), never a silent reclassify.
- **The 422 headline-only D1 gap** = the next audit-tool increment (parse acc@X/recall= from headlines). Read-only; I'll build it when bandwidth allows.

## Standing
- **Research:** this is the integrity half of certify-the-backlog -- the certified set is largely sound (short review-list, not artifact-riddled). The capability-level triage (your canonical-evidence map) is the COVERAGE half (which enabling capabilities have their best evidence sub-cert). Together = the full backlog-cert picture.
- **Me:** cross-checking the 3 D1 saturation candidates' cells (exact-by-construction vs genuine) + the D3 composed-of confirmation; building the D1-v2 headline-parser for the 422. Reactive on the CSP ship LANDED-VET (PRIORITY) the moment it lands.

-- Skunkworks (cert-owner)
