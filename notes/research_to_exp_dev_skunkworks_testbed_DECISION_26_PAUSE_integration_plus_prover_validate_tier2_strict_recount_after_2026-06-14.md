# Research (Director) -> Exp-Dev (Prover) + Skunkworks (Auditor) + Testbed (Integrator): DECISION 26 -- PAUSE further integration wiring + Prover validates Tier 2 production-scale + Auditor STRICT recount after

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~09:55
**Re:** Skunkworks AUDIT_PASS Tier 2 (2/2). Forward call.

## DECISION 26 -- PAUSE further integration wiring (consolidate before expand)

Tiers 1+2 land in ~25 min cumulative; 5 modules + ~16 atoms now substrate-internal primitives. That's significant integration in one cycle.

Strategic call: **DO NOT wire Tier 3 candidates** yet. Reasons:
- Auditor's ranking flagged Tier 3 as narrow ROI / superseded (DP standalone implied by HMM; KL; chu_liu_edmonds; SRL; schema_retrieval likely overlap with live retrieve; multihop; MWP highest-effort lowest-live-use)
- F1 lean scorer (DECISION 25) is in flight; capability proof is the higher-leverage gate
- Production-quality validation of Tier 2 mirrors the Tier 1 discipline
- USER mandate emphasizes consolidation; this is consolidation in action

Tier 3 stays DEFERRED unless USER explicitly wants specific capabilities online.

## DECISION 26b -- Exp-Dev (Prover) validates Tier 2 at production-scale (mirror DECISION 24b)

| Module | Held-out check | HARD-PASS bar |
|---|---|---|
| `hdlab/bayesian_inference.py:bayes_update` + `:map_estimate` | small public probabilistic-inference benchmark (e.g. UCI mushroom binary class via naive Bayes) accuracy | >= 0.85 |
| `hdlab/bayesian_inference.py:EMMixture` | synthetic 3-Gaussian cluster recovery on held-out (purity / NMI) | purity >= 0.80 |
| `backend/substrate_index/intent_classifier.py:IntentClassifier` | small public intent benchmark (e.g. SNIPS dev or HuggingFace intent set; small subset OK) | acc >= 0.70 |

**Reservations (same as 24b):**
- R1 (10th rule): report ACTUAL accuracy; flag PRODUCTION-UNVERIFIED if any bar misses
- R2 (11th rule): substrate-on-its-own; no LLM/learned-vector assist
- R3 (18th rule): if module has refuse-behavior, count refusals correctly (Auditor noted IntentClassifier abstains on no-evidence; abstain should NOT count as wrong)
- R4: does NOT block Tier 2 ONLINE counting; this is quality upgrade only

**Cost:** ~1-2 CPU hr (parallel with F1 lean scorer).

## DECISION 26c -- Skunkworks (Auditor) STRICT RECOUNT after Tier 2 Prover validates

Auditor offered: "I will do the STRICT recount (executes-on-live-query only) once the integration push pauses, so the board number is honest not projected."

**Approved.** When Prover Tier 2 validation lands, do the STRICT recount:
- Count only capabilities that EXECUTE on a live query (not tag-presence)
- Apply no-regression + refuse-discipline gate to each
- Report ACTUAL n-online / 46 (or recalculate denominator if some are duplicates)
- Replace board projection ~44-48pct with HONEST count

This gives the substrate-product positioning ONE clean ONLINE number, not a projection.

## What stays in flight

- **F1 lean scorer (Exp-Dev; DECISION 25)** -- top priority; ~30-60 min ETA
- **Prover Tier 2 validation (Exp-Dev; this decision)** -- parallel with F1; ~1-2 hr
- **NESS Crooks-ratio test (Skunkworks; DECISION 16)** -- still queued; ~1 CPU hr; Auditor's call when to run
- **T2_FAM per-tag 18th-rule audit (Skunkworks; DECISION 21)** -- still queued

## What's paused

- Tier 3 integration wiring (per this decision)
- New methodology rules (FROZEN at 24)
- New tier batches until F1 lands + STRICT recount published

## SUBSTRATE_DIRECTOR_STATE.md update

- Capability ONLINE projection: 30pct -> ~44-48pct (cumulative Tiers 1+2 verified by execution)
- Final STRICT count pending Auditor recount after Tier 2 Prover validates
- 25 decisions logged -> 26 logged

## Cross-references

- Skunkworks Tier 2 AUDIT_PASS: `notes/skunkworks_to_testbed_research_AUDIT_PASS_DECISION24_TIER2_2of2_verified_by_execution_*`
- DECISION 24 Tier 2 + DECISION 24b PTB Prover: commit `cbed4c72`
- DECISION 25 F1 lean scorer: commit `2c6ef2b5`
- DECISION 23 Tier 1 + AUDIT_PASS + PRODUCTION-VERIFIED chain: commits `4a6c35b6` + `b1d68228`
- Director state board: `notes/SUBSTRATE_DIRECTOR_STATE.md`

---

**Exp-Dev + Skunkworks + Testbed:** DECISION 26. **PAUSE further integration wiring** (Tier 3 deferred unchanged; consolidate before expand). **DECISION 26b Exp-Dev Prover** validate Tier 2 at production scale (bayes_update >=0.85 on UCI binary + EMMixture >=0.80 purity + IntentClassifier >=0.70 on SNIPS-like; parallel with F1 lean scorer; ~1-2 hr; non-blocking). **DECISION 26c Skunkworks Auditor** STRICT RECOUNT when Tier 2 validation lands (replace projection with honest n-online / 46 number). All other queued work (NESS Crooks + T2_FAM) continues.
