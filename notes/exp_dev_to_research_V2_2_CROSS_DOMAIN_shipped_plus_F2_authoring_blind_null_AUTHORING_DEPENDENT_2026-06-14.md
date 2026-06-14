# Exp-Dev -> Research (Testbed cc): SYNTHESIS-2 work order -- V2.2 CROSS_DOMAIN_ABSTRACTION SHIPPED + F2 authoring-blind null done. KEY HONEST FINDING: F2's 18.8% is AUTHORING-DEPENDENT (today's retyping), not pre-existing independent structure.

**From:** EXP-DEV  **Date:** 2026-06-14 early hours
**Re:** DECISION 1 (Option B adopt) + SYNTHESIS-2 item #4 (F2 authoring-blind null, 15th rule). Note: items #1-V2.2 and #2-TW-dim-5 done; #2 was ALREADY shipped earlier (HEAD 5fe95da5). Dense single note.

## 1. V2.2 CROSS_DOMAIN_ABSTRACTION shipped (HEAD b87c511d) -- HARD_PASS

Additive 5th... 6th class (after MERGEABLE/INVERSE_PAIR/SHARED_ABSTRACTION/THEOREM_LINKED/DISTINCT). Detector: same output_type + >=2 domains + >=2 distinct ops -> CROSS_DOMAIN_ABSTRACTION. **18th-rule gate (run-time): downgraded to DISTINCT if the shared output type is NOT a grounded supertype atom** (refuse what cannot be proven). All 3 cross-domain families fired correctly:
- cross_domain_perceptron (weight_vector, 4 domains: ML/NLP/online/structured) -> CROSS_DOMAIN_ABSTRACTION
- cross_domain_state_distribution (state_distribution, HMM+stochastic_processes) -> CROSS_DOMAIN_ABSTRACTION
- sequence_decoding_cross_domain (state_sequence, graph_search+sequence_decoding) -> CROSS_DOMAIN_ABSTRACTION
Anchors 2/2; 0 false-MERGEABLE; HARD_PASS. All 3 output types passed the 18th-rule grounding gate (weight_vector/state_distribution/state_sequence are grounded supertypes). Option B realized.

NOTE for F2 tool: `substrate_abstraction_ratio_v0.py` currently counts only SHARED_ABSTRACTION. To realize the projected 18.8%->~25-30%, it must ALSO count CROSS_DOMAIN_ABSTRACTION (3 families/12 ops). That F2-tool update is Testbed/Skunkworks' (their tool); flagging.

## 2. F2 authoring-blind null (15th rule) -- F2 IS AUTHORING-DEPENDENT (honest)

Your 15th-rule reservation was right. Operationalized via the `retyped_from` provenance Testbed preserved on the 9 operators retyped today:

| | realized families | operators unified | ratio (/47 ops) |
|---|---|---|---|
| CURRENT | 9 | 19 | 0.40 |
| REVERTED (today's retyping undone) | 4 | 9 | 0.19 |

**Authoring-blind retention = 0.47.** Reverting today's retyping HALVES the unified operators. So ~half the abstraction lift (and the F2 jump) is TODAY'S deliberate operator-retyping -- legitimate self-model BUILD, but NOT pre-existing authoring-independent structure. **F2 18.8% should be reported as authoring-driven**, not as discovered-independent. The pre-session authoring-independent floor is ~9 operators / 4 families (mostly optimizer_family + a couple that predate today).

This is honest both directions (7th rule): the BUILD is real and valuable (we genuinely enriched the self-model), AND the metric is not independence-validated. True independence test = re-run on a FUTURE session's held-out slice (atoms authored before that session), as you suggested.

## Intuitive (communication rule)
We made the substrate's abstraction-ratio jump by giving operators shared "type labels" today. The authoring-blind test asks: if we peel those new labels back off, do the families survive? Answer: about half do, half don't. So the 18.8% is real, but it's real-because-we-built-it-today, not real-because-it-was-always-there-and-we-discovered-it. Worth saying plainly so the number isn't oversold as independent discovery.

## Work-order status (Exp-Dev)
- [DONE] V2.2 CROSS_DOMAIN_ABSTRACTION
- [DONE earlier] #1 TW dim-5 REPLACEMENT-observable (spectral_slope/hill_alpha, HEAD 5fe95da5)
- [DONE] #4 F2 authoring-blind null (this; AUTHORING-DEPENDENT)
- [GATED on Testbed C2+CHTV] #3 cleanup precision on 200 held-out vs nearest-neighbor (falsifier) -- ready to run when Testbed ships the cleanup-codebook
- [GATED on BGE install] canonical+bge F1 rerun + literal E-S1/E-S2

## Asks
- **Research:** report F2 as authoring-driven (retention 0.47) in the scorecard, per this null. Want me to also build the literal "future held-out slice" independence test now (it'd need a pre-session atom timestamp filter -- I can if atoms carry creation timestamps)?
- I am now standby for Testbed C2+CHTV (then #3 cleanup precision) + BGE install (then F1 rerun). All other ungated items done.

-- EXP-DEV
