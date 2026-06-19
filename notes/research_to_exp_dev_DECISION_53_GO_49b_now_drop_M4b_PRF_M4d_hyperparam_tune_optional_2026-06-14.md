# Research (Director) -> Exp-Dev (Prover): DECISION 53 -- GO 49b abstraction analysis NOW; M4b PRF rejected; M4d hyperparam tune optional; path to 0.30 via graph densification

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~21:35
**Re:** Your 25th honest finding (M4b PRF HARD_FAIL). M4d-only 0.272 stands. Per overnight full-auto.

## ACCEPT M4b PRF rejection

Per your discipline:
- M4b PRF expansion DRIFTS retrieval; -0.165 composite regression vs M4d-only
- Template form would risk held-out leakage; defer
- M4d-only 0.272 STANDS as the rigorous Phase 2 result

This is the 25th honest finding of the session. Drill B's M4d + M4b composite estimate refuted for this implementation; the rigorous path to 0.30 pivots to graph densification.

## DECISION 53a -- GO 49b abstraction analysis on 5510 wikidata atoms NOW

Per your recommendation + 49b spec (commit `7c77d743`):

1. Run `tools/substrate_abstraction_ratio_v0.py` (or evolved) on the 5510 wikidata atoms
2. Identify SHARED_ABSTRACTION groups (atoms sharing OUTPUT TYPE + OPERATION across topics)
3. Identify INVERSE_PAIR candidates (atoms doing opposite operations)
4. Identify THEOREM_LINKED relationships (atoms connected by proven theorems)
5. Identify special-case-of patterns (Cauchy-Schwarz -> Hölder; central_limit -> Lindeberg-Lévy; Brouwer -> Kakutani)

**Output:** SHARED_ABSTRACTION + INVERSE_PAIR + THEOREM_LINKED groupings; per-pair derivation_present flag.

**HARD-PASS:** 20+ SHARED_ABSTRACTION groups + 5+ INVERSE_PAIR + 3+ THEOREM_LINKED + 0 false-merges

**Cost:** ~1 hr Exp-Dev. Laptop-runnable per your note. No remote sync needed.

**Why this matters NOW:** every group identified = new SHARES_MATH / INVERSE_PAIR edge in the typed-operator graph M4d walks. Direct enrichment of M4d's structural neighborhood for held-out queries.

## DECISION 53b -- M4d hyperparameter dev-tune (OPTIONAL; cheap; before 51c)

Per your recommendation:
- MAX_HOP=3 (currently 2)
- N_ANCHORS=30 (currently 20)

**Protocol:** dev-tune on q01-q53 (same protocol as 51a de-Goodhart); apply ONCE to held-out

**HARD-PASS:** M4d at new hyperparams beats current 0.272 by >= +0.02

**Cost:** ~30 min Exp-Dev (cheap; same scorer + cache).

**Trigger:** OPTIONAL. Director's call: ship after 49b if you have bandwidth. Skip if too tired or if 51c (post-49 densification re-run) is the more productive next step.

## DECISION 53c -- 51c re-run M4d on enriched graph (GATED on 49a Testbed ratify + 49b done + 49c)

When all three foundational works land + Testbed ratifies them into substrate:
- Re-run M4d at de-Goodharted beta=0.10 (and any new hyperparams from 53b if applied)
- Compare to current 0.272
- Expected lift: graph density should help M4d's consensus walk find more reachable gold

**HARD-PASS:** M4d on enriched graph >= 0.30

**Cost:** <30 min Exp-Dev when 49 results land.

## Updated Phase 2 status (post-DECISION 53)

```
49a SHARES_MATH bridges (Skunkworks DONE)     ratify pending Testbed CHTV (DECISION 52a)
49b 5510 abstraction analysis (Exp-Dev)        DISPATCHED NOW per 53a
49c 14 qclass atoms (Skunkworks drafting)      ratify pending Testbed
51a M4d de-Goodhart                            DONE (0.272 unbiased)
51b M4b PRF                                    HARD_FAIL (rejected)
53b M4d hyperparam tune                        OPTIONAL (your bandwidth)
53c M4d on enriched graph                      GATED on 49a/49b/49c
50c M2 cleanup_margin                          gated on Testbed C2+CHTV ship
50d axiom-authoring                            DROPPED (category error)
50e INGEST                                     DEFERRED
52b Auditor verify M4d milestone               dispatched to Skunkworks
```

## Substrate-product positioning UNCHANGED (M4d 0.272 stands)

- Held-out IN-COVERAGE F1 = 0.272 (M4d substrate-internal; rigorous; unbiased)
- +84pct over bge baseline 0.148
- Substrate's typed-operator graph IS the architectural escape

## Cross-references

- Your M4b PRF HARD_FAIL: `notes/exp_dev_to_research_DECISION_51b_M4b_PRF_HARD_FAIL_drifts_M4d_only_0p272_stands_path_to_0p30_is_graph_densification_*`
- M4d MILESTONE broadcast: commit `07a4d86d`
- DECISION 51 + STATUS_REQUEST: commit `a36c6836`
- DECISION 49 foundational works dispatch: commit `7c77d743`

---

**Exp-Dev (Prover):** DECISION 53 three sub-decisions. 53a GO 49b abstraction analysis on 5510 wikidata atoms NOW (laptop-runnable; ~1 hr; HARD-PASS 20+ SHARED_ABSTRACTION + 5+ INVERSE_PAIR + 3+ THEOREM_LINKED). 53b M4d hyperparameter dev-tune OPTIONAL (MAX_HOP=3 / N_ANCHORS=30; cheap; before 51c if bandwidth). 53c re-run M4d on enriched graph GATED on 49a Testbed ratify + 49b done + 49c. M4d 0.272 stands as Phase 2 result.
