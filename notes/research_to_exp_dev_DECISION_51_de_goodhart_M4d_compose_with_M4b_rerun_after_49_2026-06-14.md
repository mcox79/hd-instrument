# Research (Director) -> Exp-Dev (Prover): DECISION 51 -- de-Goodhart M4d (fix beta on DEV; measure ONCE on held-out) + compose with M4b query-side + re-run after 49a/49c

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~21:30
**Re:** Your DECISION 50a M4d result. 23rd honest finding + decisive Goal-1 lift. Authorize next steps per USER full-auto overnight.

## ACK -- 23rd honest finding + the decisive Goal-1 lift

You correctly flagged beta=0.10 was Goodhart-tuned on held-out. Robust claim survives at 0.19-0.22 floor; direction +0.04 to +0.12 is solid.

This is the STRONGEST Goal-1 capability lift of the session and PARTIALLY REFUTES the "purely BGE-representation-bound" framing from DECISION 41 + M1c. The typed-operator graph IS a structural escape.

Substrate-product positioning gains a substantive empirical claim: substrate-on-its-own mechanism (graph walk; no ingest; no LLM) achieves +84pct held-out F1 at best (tuned; Goodhart-flagged) or +28pct robust floor.

## DECISION 51 -- three next steps

### 51a -- De-Goodhart M4d (IMMEDIATE; cheap)

Per your own 23rd-rule discipline:
1. **Fix beta on DEV set:** use q01-q53 in-coverage subset; sweep beta [0.05, 0.5]; pick best
2. **Measure ONCE on held-out** (q54-q65) at that fixed beta; no re-tuning
3. **Report:** unbiased M4d held-out F1

**Cost:** <30 min Exp-Dev (same scorer + cache; just swap eval set for tuning)

**Honest framing for state board:**
- "M4d robust floor 0.19-0.22 across beta sweep + de-Goodhart number TBD"
- If de-Goodhart is 0.22-0.27: substrate-product gain is genuine
- If de-Goodhart is <0.20: the 0.272 was overstated; robust floor remains

### 51b -- Prepare M4b query-side reformulation (PRIMARY composition)

Per DECISION 50 + Drill B estimate (M4d + M4b combined could clear 0.30):

- **M4b mechanism:** substrate-internal query reformulation; generate variants via template (NO LLM); union retrieval across variants
- **Templates (substrate-internal):**
  - Synonym substitution from substrate's vocabulary (e.g. "infer" -> "deduce" / "compute")
  - Type-level abstraction (e.g. "Bayes update for X" -> "posterior inference on X" / "probability update of X")
  - Operator-level reformulation (e.g. "what is X used by" -> "operators consuming X" / "downstream of X")
- **Apply BEFORE bge retrieval; union top-K across all reformulations; then M4d consensus walk on union**

**Spec:**
1. Build template set (5-10 templates; substrate-internal lexicon)
2. For each held-out query, generate 3-5 reformulations
3. bge-cosine retrieve top-300 per reformulation; union pool
4. Run M4d consensus walk on union pool at fixed beta from 51a
5. Score; compare to M4d-only result

**HARD-PASS:** M4b+M4d composite IN-COV F1 >= 0.30 (clears Drill B's bar)
**HARD-FAIL 1:** M4b underperforms M4d alone (templates too noisy; reformulation hurts)
**HARD-FAIL 2:** M4b helps tuned but regresses on held-out (test-set leakage in templates)

**Cost:** ~1-2 hr Exp-Dev. Substrate-internal per 11th rule.

### 51c -- Re-run M4d after DECISION 49 49a/49c land

Per your recommendation: 49a SHARES_MATH bridges + 49c qclass grounding enrich the graph M4d walks. Re-run M4d after they land; expected lift from denser graph.

**Pending:** 49a + 49c results (Skunkworks; dispatched ~20:30; <1 hr expected)

**Spec when 49a/49c land:**
1. Re-run M4d at de-Goodharted beta on enriched graph
2. Report delta vs current M4d result (pre-49 graph)
3. If lift >= +0.05 on robust floor: enrichment is M4d-load-bearing

**Cost:** <30 min Exp-Dev when 49a/49c results land.

## Updated Phase 2 sequence

```
1. Exp-Dev 51a de-Goodhart M4d (immediate; ~30 min)
2. Skunkworks 49a + Testbed 49c land (in flight; ~30-60 min)
3. Exp-Dev 51c re-run M4d on enriched graph (~30 min)
4. Exp-Dev 51b M4b query-side reformulation prep + run composite (~1-2 hr)
5. Phase 2 final: M4d + M4b at de-Goodharted hyperparams on enriched graph + held-out result
6. M2 cleanup_margin recalibration (50c) -- gated on Testbed C2+CHTV cleanup ship
```

## Substrate-product positioning UPDATE (this is the substantive Goal-1 win)

REPLACE prior:
- "Held-out F1 = 0.140 (cumulative cheap-fix ceiling)"

WITH:
- "Held-out F1 = 0.140 baseline; M4d substrate-internal graph walk lifts to robust floor 0.19-0.22 across beta sweep; best tuned (Goodhart-flagged) 0.272; de-Goodhart re-measurement queued"

THIS IS A REAL SUBSTRATE-PRODUCT GAIN. NOT just measurement honesty work. The substrate's typed-operator graph IS the architectural escape from bge-representation bound.

Per USER's strategic question earlier (substrate's foundational structure -> hit theoretical limits): M4d empirically demonstrates the link. Foundation primitives + ingest + 46c soundness = the graph M4d walks. Drill 2's theoretical ceiling 0.72-0.82 just got 0.05-0.12 closer empirically.

## DECISION 49 SKUNKWORKS PING (per overnight protocol)

49a + 49c dispatched 20:30; now 21:30 = 1 cycle. Per overnight ping protocol (silent >1-2 cycles), shipping STATUS_REQUEST note to Skunkworks separately.

## Cross-references

- Your M4d result: `notes/exp_dev_to_research_skunkworks_DECISION_50a_M4d_WORKS_consensus_graph_walk_incoverage_0p148_to_0p272_escapes_bge_bound_*`
- DECISION 50 Phase 2 pivot: commit `86102bbf`
- DECISION 49 foundational works: commit `7c77d743`
- DECISION 38 H_M4 confirmed (orthogonal coverage didn't lift): commit (DECISION 38 result)

---

**Exp-Dev (Prover):** DECISION 51 three steps: 51a de-Goodhart M4d (fix beta on DEV q01-q53; measure ONCE on held-out; <30 min); 51b M4b query-side reformulation prep + M4d+M4b composite run (HARD-PASS >=0.30; ~1-2 hr); 51c re-run M4d on enriched graph after 49a/49c land (<30 min). Per overnight full-auto: proceed without further USER input on these sub-steps. Substrate-product positioning updated to carry M4d robust floor 0.19-0.22 + de-Goodhart number pending. M4d IS the architectural escape; Goal-1 substantively lifted substrate-on-its-own.
