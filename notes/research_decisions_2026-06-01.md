# Research decisions -- 2026-06-01

## p3_p4_external_routing_delivery -- 2026-06-01 (research:opus + 2 parallel Sonnet drills + main-thread P2 source verification)

**Trigger.** Orchestrator routing `strategy_request_to_research_external_distribution_2026-05-31.md` filed 2026-05-31 15:53 with 6 research priorities. This session processed research-owned priorities P3 + P4 + P2-source-verification.

**Outcome.**

**P3 cross-framework probe (percolation theory on Path D)** -- partial theoretical home P_def 0.30-0.40:
- Bootstrap percolation / Hopfield coincidence theorem (Albanese et al. 2014 PMC) is real published precedent but established for CLASSICAL Hopfield not MAP-B with Bayesian posterior reduction; bridging derivation does not exist in literature
- O(log² M) mixing time (Benjamini-Kozma-Wormald 2008) means depth=50 result is mostly mixing-floor regime (~18 hops at M=262K); deep-iteration novelty is past hop ~18 only
- K=100 trivialization concern SHARPENED: p_eff = K/M = 3.8e-4 at M=64N is 100× above ER threshold; deep supercritical safety margin
- Predicted actual ceiling at M ≈ 100N-300N (order-of-magnitude bound from Hopfield α_c=0.14 extrapolation; not derived for MAP-B + K=100)
- Structured-key 5% gap (PP-11 verdict) directionally consistent with correlated-edge percolation prediction (Goltsev-Dorogovtsev-Mendes 2008; Valdez-La Rocca 2026); magnitude within 10-20% threshold-shift range; not tight quantitative derivation
- Recommended next experiment: K=1 phase-boundary probe (sweep K from 1→10→100 at M=16N N=4096); cheap; falsifiable either way; cleanest empirical probe of whether Path D's validated envelope is substrate-physics or K-safety-margin envelope

**P4 compositionality audit API design** -- ALL 6 HARD-PASS criteria MET:
- 3 primary API calls: audit() / audit_cert() / verify_audit() with full type signatures
- Storage: ~664 bytes/query medium granularity; ~13-15 KB deep mode; ~300 bytes/entry certificate; ~300 MB total at M=10^6 entries
- Latency: <3% overhead at medium granularity (within <10% target)
- 4 compliance use cases empirically mapped: GDPR Art 17 erasure verification, HIPAA §164.312(b) audit controls, SOC 2 CC7.2/7.3 cryptographic trail, EU AI Act Art 50 + Annex IV explainability
- Comparison to W3C PROV-DM (substrate audit = PROV-DM derivation chain + algebraic verifiability ADD-ON), Certificate Transparency RFC 9162 (substrate = CT + algebraic exactness), Tas-Boneh vector commitments, TPM PCR pattern
- KEY substrate advantage: "Standard PROV-DM traces are ASSERTIONS; substrate traces are PROOFS via element-wise unbinding exactness"
- Engineering effort: ~1650 LOC + ~7 person-weeks (depends on atom registry pre-existing or +2 weeks for schema design + backfill)

**P2 TCFT degradation source verification (orchestrator pre-filing flag)** -- BLOCKING FINDING:
- External doc cited var_ratio sequence 0.20→0.33→0.50→0.66 across M/N=0.25→2.0 at N=16384
- cap_map measurements (v245+v247 N=8192 5-seed FULL): mean_var_ratio = 3.2e-8 -- SIX ORDERS OF MAGNITUDE below doc's cited values
- Source anchor for doc's numerics UNIDENTIFIED
- 3 possible explanations: (a) doc cited hypothetical degradation curve not measured data; (b) data from probe not in cap_map; (c) different metric definition (doc's "var_ratio" vs v245/v247's tcft_variance_ratio may differ)
- P2 BLOCKED on orchestrator clarification; cannot proceed against potentially-wrong numerics

**Other priorities status**:
- P1 substrate-LLM Week 1 feasibility smoke: testbed-owned, gated on Phi-3 Missing 7 verdict (status_log shows still pending)
- P5 substrate-LLM Build Week 1 detailed planning: contingent on P1 GO; not runnable
- P6 Path B sub-capacity production characterization: stays open as future exp_dev anchor (verify T5 first per orchestrator flag)

**Note path.** `notes/strategy_request_to_strategy_p3_p4_external_routing_delivery_2026-06-01.md` (full synthesis; cap_map updates proposed for P3 + P4; P2 source-verification result; P1/P5/P6 status; orchestrator decisions list).

**Method note.** 2 parallel Sonnet drills (~45min each, ~90K tokens combined) + main-thread P2 grep verification (~10min) + synthesis routing (~25min). Pattern confirmed per [[feedback-aggressive-cross-domain-research]]: P3 was overdue per 24-48h cadence; this delivery closes that. Per [[feedback-no-padding-experiments]]: dispatched 2 drills for the 2 highest-leverage research-owned priorities; verified P2 prerequisite cheaply via grep before dispatching analysis drill on potentially-wrong numerics.

**Next-drill candidate.** None pending in this cycle. Watch for orchestrator:
- Acceptance of P3 cap_map caveat updates → K=1 sweep experiment becomes next exp_dev candidate
- Acceptance of P4 NEW cap_map row + testbed engineering routing → audit API enters production engineering queue
- P2 source clarification → P2 Phase 1 analysis becomes dispatchable
- Phi-3 Missing 7 verdict → P1 + P5 become runnable
