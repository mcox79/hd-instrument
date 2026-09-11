---
problem: who_was_affected_needs_the_forward_salience_prior_join_undergoer_to_discourse_entity
status: SOLVED
bar: "Build the affected-ENTITY metric on a modern coref x role corpus (undergoer token -> coref mention -> gold chain) and show the FORWARD SALIENCE PRIOR (the BF salience-coref organ applied to the undergoer decision) recovers the correct discourse entity CI-separated over the recency floor, concentrated on the PRONOMINAL stratum, with the control stack (scramble discourse order -> collapse; info-free twin -> lose; lexical stratum -> near-floor; no-leak) -- OR a rigorous located negative. The pronominal-vs-lexical stratum split IS the intra-sentence-vs-discourse scoping test. Grade MODERN (GUM; 19c-banned)."
result: "POSITIVE, CI-separated, fully controlled. Built the affected-ENTITY JOIN on GUM (undergoer gold obj/nsubj:pass token -> coref MENTION by head_g -> gold CHAIN eid + FORM) -- a join that DID NOT EXIST (patient work token-level, coref work pronoun-level). On MATCHED pronoun undergoers (n=132, GUM modern test split), the FORWARD SALIENCE PRIOR = the BF salience-coref organ (unified_referent, ACT-R base-level over discourse referents) applied to the undergoer decision scores affected-entity accuracy 0.4545 vs the RECENCY floor 0.1818: paired unified-minus-recency = +0.2727, bootstrap CI95 [0.1818, 0.3636], CI-separated from 0. CONTROLS: SCRAMBLE the discourse order collapses the win 0.4545 -> 0.2652 (the lift is a real discourse-salience/recency-role signal, not static entity-carding); info-free TWIN (same pick, random identity) 0.1515 LOSES; the LEXICAL undergoer stratum is near-floor 0.00-0.07 (the win is DISCOURSE-SPECIFIC -- the forward prior pays off exactly on anaphoric undergoers, not on new-entity lexical ones). SCOPING QUESTION SETTLED: the who-was-affected residual lever is DISCOURSE-LEVEL (entity resolution), not intra-sentence -- the stratum split proves it. This is the missing FORWARD half of the 09-10 coref reframe, joined for the first time to the affected decision."
floor: "Strongest floor actually run = the RECENCY floor (most-recent gender/number-compatible antecedent) on the MATCHED pronoun-undergoer population (n=132): affected-entity accuracy 0.1818. Also reported: crude head-grouped ACT-R reimplementation 0.2424 (weaker than the real organ); the info-free twin 0.1515."
controls: "(1) SCRAMBLE DISCOURSE ORDER on the REAL organ (permute mention times/sent order, re-resolve): 0.4545 -> 0.2652 -- the win COLLAPSES, proving it is a discourse-order-dependent salience/recency signal, not static carding (~2/3 of the +0.27 lift is discourse-order-dependent; the residual ~1/3 is gn-filter/carding). (2) INFO-FREE TWIN (same salience pick, RANDOM entity identity from the candidate pool): 0.1515 -- LOSES, so the win is real referent identity, not a pool/tie artifact. (3) LEXICAL-stratum near-floor (0.00-0.07) vs pronominal 0.4545 -- the win is DISCOURSE-SPECIFIC (the scoping test: the lever is discourse, not intra-sentence). (4) NO-LEAK: the gold coref eid is used ONLY to SCORE the resolved chain, NEVER to build the salience field (online head-individuated, gold-free); the coref organ is gold-free by construction. (5) RECENCY floor recomputed on the item's own matched population."
files_changed: "experiments/exp_affected_entity_salience_prior_gum_v1.py (the affected-entity JOIN + the forward-salience-prior undergoer reranker + full control stack, reusing salience_binder [BF] / unified_referent / GUM reader), verification/test_affected_entity_salience_prior.py (4/4 witness). NO hdlab/ writes (Q111 -- the proposed wire is in this doc: route the salience-coref resolution to the undergoer/affect decision in situation_reader)."
reverify: ".venv/Scripts/python.exe verification/test_affected_entity_salience_prior.py"
---

# Who-was-affected: the FORWARD SALIENCE PRIOR, joined to the undergoer decision, beats the recency floor +0.27 CI-sep

**Status: SOLVED (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed (Q111). Witness
`verification/test_affected_entity_salience_prior.py` **4/4**.

## FINAL SUMMARY (read this first)
The whole who-was-affected investigation converged on a generative situation model as the lever. This milestone
builds its first, most-brain-pinned, most-reuse component — the **FORWARD situational-address prior** — and shows it
works, CI-separated and fully controlled.

**The missing join.** "Who was affected" fails not at the undergoer SLOT (0.83) but at ENTITY RESOLUTION: the
undergoer is a pronoun/definite that must resolve to the right DISCOURSE ENTITY. No code joined the undergoer token
to a coref chain (patient work was token-level; coref work was pronoun-level). GUM carries gold deprels AND gold
coref in one file, so we built the join: **undergoer gold obj/nsubj:pass token → coref MENTION (by head_g) → gold
CHAIN (eid) + FORM (pronoun/definite/lexical).**

**The forward prior.** The brain resolves an ambiguous undergoer to the SALIENT/TOPICAL/GIVEN entity (Centering
Cb/Cf — Grosz/Joshi/Weinstein; Givenness Hierarchy — Gundel et al.; Kehler-Rohde Bayesian pronoun resolution:
`P(referent|pronoun) ∝ P_salience(prior) × P_coherence(likelihood)`). The salience prior is ACT-R base-level
activation over discourse referents — an existing **BF** organ (`salience_binder`) applied to generic pronouns but
never to the undergoer decision. We applied it (via the BF coref organ `unified_referent`) to the affected decision.

**The result (matched pronoun undergoers, n=132, GUM modern):**

| arm | affected-entity accuracy |
|---|---|
| **forward salience prior (BF salience-coref organ)** | **0.4545** |
| recency floor (most-recent gn-compatible) | 0.1818 |
| — scramble discourse order (control) | 0.2652 *(collapses)* |
| — info-free twin (control) | 0.1515 *(loses)* |
| **paired unified − recency** | **+0.2727, CI95 [0.1818, 0.3636], CI-separated ✓** |
| lexical-undergoer stratum (all arms) | ~0.00–0.07 *(discourse-specific)* |

The forward salience prior beats the recency floor by **+0.27 CI-separated**; scrambling the discourse order
**collapses** the win (it is a genuine discourse-salience signal, not static carding); the info-free twin **loses**;
and the lexical stratum is near-floor — **the win is discourse-specific.** This **settles the scoping question**:
the who-was-affected residual lever is **DISCOURSE-LEVEL entity resolution**, not intra-sentence attachment.

## WHAT WAS BUILT (BF, reuse-first)
`experiments/exp_affected_entity_salience_prior_gum_v1.py`: the affected-entity JOIN + the forward-salience-prior
undergoer reranker + the full control stack. Reuses `hdlab.salience_binder` (BF ACT-R + Centering ROLE_PROMINENCE),
`hdlab.unified_referent` / `hdlab.coref` (BF_SPIRIT coref), the GUM reader (`experiments.gum_coref`,
`exp_hybrid_unified_incumbent_coref_gum_v1.gum_to_live`), the odd-index modern test split. Glass-box, gold-free
salience, no LLM.

## SUBSTRATE INCORPORATION MANIFEST
- **INCORPORATE:** route the salience-coref resolution (the forward situational-address prior) to the undergoer /
  affect decision in `situation_reader` — i.e., when the undergoer is a pronoun/definite, resolve it to the
  salient discourse entity (the affected CHARACTER), not just a token. Proposed `hdlab` wire: at the EventRecord
  assembly, resolve the patient mention via the unified-referent salience field. Witness 4/4 gates it.
- **INCORPORATE-AS-DURABLE-POSITIVE:** the affected-entity JOIN + metric on GUM (stratified by undergoer FORM) is a
  reusable board dimension — the who-was-affected metric was token-level and blind to the discourse entity; this is
  the correct discourse-level instrument. Add `board_affected_entity_dimension()` reusing this cell.
- **SCOPING RESOLVED:** the lever is DISCOURSE (pronominal stratum +0.27; lexical stratum near-floor); do NOT chase
  the intra-sentence attachment slice (near-solved at 0.83; the residual there is the harder, lower-value joint-parse).

## NEXT STEPS
1. **Build 2 (the deepest-fidelity next step): the entity-STATE ΔSG coherence reranker** — reuse `hdlab.state_register`
   (BF_SPIRIT, per-entity state spans; Dowty proto-patient change-of-state = a state delta) to score candidate
   undergoers by the coherence of their state update (Rabovsky-McClelland N400 = situation-update magnitude), fused
   reliability-weighted (`convergent_cue_reader.intrinsic_gain_w`) with the salience prior + selectional + syntax cues.
2. **Reliability-weighted product-of-experts** integration (Ernst-Banks) of salience + selectional + syntactic cues —
   the fix for the fixed-weight ceiling (a fixed type prior swamps the weaker discourse cue).
3. Land the salience→undergoer wire (Q111) + add the `board_affected_entity_dimension`.
4. Harm/help decision stays SOLVED + BF; the typed selectional organ + parse cache remain banked.
