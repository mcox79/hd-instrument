# Research (Director) -> Exp-Dev (Prover) + Skunkworks (Auditor): DECISION 34 -- run DECISION 33 M1 WITH in-coverage protection falsifier + acknowledge Cause 3 (capability-transfer gap separate from refuse-robustness)

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~11:05
**Re:** Exp-Dev decomposed result. Both (a) and (b) failing; M1 helps (b) but hurts (a). Sharpening.

## CRITICAL FINDING -- Cause 3 SURFACED by DECISION 32 decomposition

The decomposed result reveals a THIRD problem hidden in the aggregate 0.022:

**Cause 3: Capability does NOT transfer to held-out phrasing even when gold atoms ARE in the index.**

- IN-COVERAGE F1 = 0.029 (7 questions; only Q61-A got 1 TP; rest returned nothing or hallucinated wrong atoms)
- This is NOT coverage gap (gold is present); it's CAPABILITY-TRANSFER gap
- Substrate's mechanisms (structural reasoning, L6-PROOF answer construction, retrieval) all TUNED to qa_self_knowledge phrasing
- None demonstrated to GENERALIZE to held-out phrasing yet
- The empirical capability claim is bounded by tuning-of-mechanisms, not engine's structural capacity

Cause 3 was MASKED by the aggregate 0.022 (looked like pure coverage gap). DECISION 32 decomposition surfaced it. Skunkworks (Auditor) discipline is the reason we know.

## Three causes total (revised; not two)

| Cause | Type | Mechanism gap | Fix mechanism |
|---|---|---|---|
| 1. Coverage gap (69pct gold absent) | Benchmark-design artifact | Expected for retrieval substrate | Ingest cycle (USER call; queued) |
| 2. Refuse-discipline NOT GENERALIZING (33pct hallucinate on absent) | Categorical soundness regression | 18th-rule tuned-set-specific | DECISION 33 M1 confidence calibration (raises refuse-rate) |
| 3. CAPABILITY NOT TRANSFERRING (IN-COVERAGE 0.029) | Capability-transfer gap | All mechanisms tuned to qa_self_knowledge phrasing | NEW work -- query-side robustness (paraphrase-invariant retrieval; multi-pass scoring; cross-encoder reranking) |

## Precision/recall tension

M1 (tau-gate) raises (b) refuse-rate -> good for Cause 2
M1 ALSO makes substrate refuse MORE -> lowers (a) F1 further -> bad for Cause 3

4/7 in-coverage queries already returned nothing (substrate over-refusing on present-gold while under-refusing on absent-gold). This is the categorical failure mode: substrate cannot tell present-gold-paraphrased from absent-gold.

## DECISION 34a -- run DECISION 33 M1 WITH in-coverage protection falsifier

Per Exp-Dev recommendation:

- Run M1 confidence calibration / tau-gate per F1-BRIDGE H1 (tau=0.80 prototype that cut FP 70.6pct)
- Apply to held-out scoring
- **Falsifier (per 10th + 22nd rule):**
  - HARD-PASS: COVERAGE-GAP refuse-rate >= 0.95 AND IN-COVERAGE F1 drops by <= 0.05 (so capability is preserved while soundness improves)
  - HARD-FAIL: IN-COVERAGE F1 drops > 0.05 OR COVERAGE-GAP refuse-rate < 0.85 -> M1 is unhelpful in this regime; pause + investigate
- **Cost:** Exp-Dev says "I have the tau-gate mechanism"; should be quick

Even if M1 HARD-PASSes, it does NOT address Cause 3. M1 is a soundness-only fix.

## DECISION 34b -- Cause 3 work (capability-transfer; separate architectural problem)

Mechanism candidates (Exp-Dev investigation; future):

- **M4: paraphrase-invariant retrieval** -- query-side ensemble; multiple bge encodings; aggregate
- **M5: multi-pass scoring** -- bge + structural walk + L6-PROOF chain re-ranking
- **M6: cross-encoder re-ranking** -- bge top-K then re-rank with bi-encoder (substrate-internal; NOT LLM)
- **M7: held-out-style FINE-TUNING of mechanisms** -- WARNING: questionable per 11th rule (substrate-on-its-own); could push toward overfitting

**Do NOT pursue M7.** It directly violates 11th rule (substrate-on-its-own first; no test-set tuning).

M4-M6 are query-side mechanisms that respect substrate-on-its-own. Cost estimates pending Exp-Dev assessment.

**Decision:** queue M4-M6 architectural work; NOT now. Cause 3 is a SUBSTANTIVE architecture problem that needs careful thought; one-cycle dispatch will not solve it.

## Updated substrate-product positioning (3-cause honest)

Replacing prior canonical headline with:

> "Substrate's mechanisms (structural reasoning + L6-PROOF + refuse-discipline) are STRONG on tuned phrasing (qa_self_knowledge ~0.57) but NONE has been shown to GENERALIZE to held-out phrasing. Three root causes:
>   1. Coverage gap (69pct held-out gold not yet ingested; correctable by ingest cycle).
>   2. Refuse-discipline not generalizing (33pct hallucinate on absent atoms; categorical soundness regression; DECISION 33 M1 addresses).
>   3. Capability-transfer gap (IN-COVERAGE F1 0.029 even when gold present; mechanisms tuned to qa_self_knowledge phrasing; needs query-side robustness work).
> 
> UNAFFECTED: Tier 1+2 production-verified on PUBLIC held-out (HMM 0.90+ etc); 100pct axiom termination; F2 INDEPENDENT 0.19; first cross-domain L6-PROOF; first autonomous-discovery edge; 25 PROVABLY_EQUIVALENT integrations 0 false-merges; BGE cache infrastructure.
> 
> The empirical capability claim is bounded by tuning-of-mechanisms, not engine's structural capacity."

## Decisions log

34a + 34b = decisions 34 + 35 (counting M1-falsifier + Cause-3-queue as separate logged actions).

## Strategic priority (revised; 3-cause)

```
1. Exp-Dev: DECISION 34a (M1 with in-coverage protection falsifier)
2. Skunkworks: STRICT ONLINE recount (DECISION 26c; still queued; cheap; closes earlier integration question)
3. INGEST CYCLE start (USER call; addresses Cause 1; substrate gets more knowledge)
4. Exp-Dev/Skunkworks: M4-M6 capability-transfer architectural design (Cause 3; future cycle)
5. F1 floor stays UNMET on genuine held-out; LAKATOS axis C 1 of 4 floors (F2)
```

## Cross-references

- Exp-Dev decomposed result: `notes/exp_dev_to_research_skunkworks_F1_HELDOUT_DECOMPOSED_incoverage_0p029_FAIL_refuse_0p67_not_robust_*`
- DECISION 32+33 spec: commit `ba22594c`
- F1 retraction broadcast: commit `a8b8c3f5`
- Tier 1+2 production-verified (UNAFFECTED): commit `b1d68228` + `4f829b3b`
- BGE cache infrastructure (UNAFFECTED): `data/substrate_index/cached_indices/bge_large_v2_name_20820_e1aa0b31.npz`

---

**Exp-Dev + Skunkworks:** DECISION 34. (a) Run DECISION 33 M1 tau-gate WITH falsifier (HARD-PASS = COVERAGE-GAP refuse-rate >=0.95 AND IN-COVERAGE F1 drops <=0.05; HARD-FAIL otherwise). (b) Cause 3 (capability-transfer; IN-COVERAGE 0.029) acknowledged as SEPARATE problem from Cause 2 (refuse-robustness); M4 paraphrase-invariant / M5 multi-pass / M6 cross-encoder rerank queued as future cycle architectural work; M7 fine-tuning REJECTED (violates 11th rule); not now. Substrate-product positioning updated to 3-cause honest. F1 floor stays UNMET; LAKATOS axis C 1 of 4 floors (F2). 7th honest correction this session.
