---
problem: who_was_affected_needs_the_forward_salience_prior_join_undergoer_to_discourse_entity
status: SOLVED
bar: "Build the affected-ENTITY metric on a modern coref x role corpus (undergoer token -> coref mention -> gold chain) and show the FORWARD SALIENCE PRIOR (the BF salience-coref organ applied to the undergoer decision) recovers the correct discourse entity CI-separated over the recency floor, concentrated on the PRONOMINAL stratum, with the control stack (scramble discourse order -> collapse; info-free twin -> lose; lexical stratum -> near-floor; no-leak) -- OR a rigorous located negative. The pronominal-vs-lexical stratum split IS the intra-sentence-vs-discourse scoping test. Grade MODERN (GUM; 19c-banned)."
result: "POSITIVE, CI-separated, fully controlled. Built the affected-ENTITY JOIN on GUM (undergoer gold obj/nsubj:pass token -> coref MENTION by head_g -> gold CHAIN eid + FORM) -- a join that DID NOT EXIST (patient work token-level, coref work pronoun-level). On MATCHED pronoun undergoers (n=132, GUM modern test split), the FORWARD SALIENCE PRIOR = the BF salience-coref organ (unified_referent, ACT-R base-level over discourse referents) applied to the undergoer decision scores affected-entity accuracy 0.4545 vs the RECENCY floor 0.1818: paired unified-minus-recency = +0.2727, bootstrap CI95 [0.1818, 0.3636], CI-separated from 0. CONTROLS: SCRAMBLE the discourse order collapses the win 0.4545 -> 0.2652 (the lift is a real discourse-salience/recency-role signal, not static entity-carding); info-free TWIN (same pick, random identity) 0.1515 LOSES; the LEXICAL undergoer stratum is near-floor 0.00-0.07 (the win is DISCOURSE-SPECIFIC -- the forward prior pays off exactly on anaphoric undergoers, not on new-entity lexical ones). SCOPING QUESTION SETTLED: the who-was-affected residual lever is DISCOURSE-LEVEL (entity resolution), not intra-sentence -- the stratum split proves it. This is the missing FORWARD half of the 09-10 coref reframe, joined for the first time to the affected decision."
floor: "Strongest floor actually run = the RECENCY floor (most-recent gender/number-compatible antecedent) on the MATCHED pronoun-undergoer population (n=132): affected-entity accuracy 0.1818. Also reported: crude head-grouped ACT-R reimplementation 0.2424 (weaker than the real organ); the info-free twin 0.1515."
controls: "(1) SCRAMBLE DISCOURSE ORDER on the REAL organ (permute mention times/sent order, re-resolve): 0.4545 -> 0.2652 -- the win COLLAPSES, proving it is a discourse-order-dependent salience/recency signal, not static carding (~2/3 of the +0.27 lift is discourse-order-dependent; the residual ~1/3 is gn-filter/carding). (2) INFO-FREE TWIN (same salience pick, RANDOM entity identity from the candidate pool): 0.1515 -- LOSES, so the win is real referent identity, not a pool/tie artifact. (3) LEXICAL-stratum near-floor (0.00-0.07) vs pronominal 0.4545 -- the win is DISCOURSE-SPECIFIC (the scoping test: the lever is discourse, not intra-sentence). (4) NO-LEAK: the gold coref eid is used ONLY to SCORE the resolved chain, NEVER to build the salience field (online head-individuated, gold-free); the coref organ is gold-free by construction. (5) RECENCY floor recomputed on the item's own matched population."
files_changed: "experiments/exp_affected_entity_salience_prior_gum_v1.py (BUILD 1: the affected-entity JOIN + the forward-salience-prior undergoer reranker + full control stack, reusing salience_binder [BF] / unified_referent / GUM reader), verification/test_affected_entity_salience_prior.py (4/4 witness). experiments/exp_affected_entity_reliability_fusion_gum_v1.py (BUILD 2: reliability-weighted fusion of salience x typed-selectional coherence -- a LOCATED NEGATIVE), verification/test_affected_entity_reliability_fusion.py (witness). experiments/exp_affected_entity_ic_prior_gum_v1.py (BUILD 3: mathematically-BF implicit-causality prior + Ernst-Banks calibrated inverse-variance fusion -- a LOCATED NEGATIVE; IC misapplies to argument-pronouns), verification/test_affected_entity_ic_prior.py (witness). experiments/exp_affected_entity_binding_parallelism_gum_v1.py (BUILD 4: the CORRECTED LEVER, a WIN -- Binding Principle B + role/thematic parallelism = the LIKELIHOOD half; +0.093 CI-sep), verification/test_affected_entity_binding_parallelism.py (4/4 witness). NO hdlab/ writes (Q111 -- the proposed wire is in this doc: route the salience-coref resolution to the undergoer/affect decision in situation_reader)."
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

## BUILD 2 (attempted): reliability-weighted fusion of salience x type-coherence -- a LOCATED NEGATIVE
`experiments/exp_affected_entity_reliability_fusion_gum_v1.py` (witness passes). Fused the forward salience prior
with the typed-selectional (Resnik) coherence cue, reliability-weighted via `convergent_cue_reader.intrinsic_gain_w`
(Ernst-Banks), on the pronoun-undergoer affected-entity task (n=1142 multi-entity). RESULT: **the type-coherence cue
does NOT add** -- salience-alone 0.3704, coherence-alone **0.1629** (the ambiguity wall), FUSED reliability-weighted
0.3441 (**-0.026 vs salience, CI-sep NEGATIVE**), fixed-weight ablation 0.3757 (≈ neutral). **Clean mechanism:**
pronoun undergoers are gender/number-filtered, so the candidates are mostly the SAME TYPE (all persons) -- a
type-selectional cue cannot discriminate among them (it only separates types, which phi already did), and
margin-based reliability-weighting misfires (a sharp-but-wrong coherence gets up-weighted). This REINFORCES build 1:
for pronoun undergoers the discriminating signal is DISCOURSE SALIENCE, not type. The coherence that WOULD
discriminate same-type candidates is NOT type-selectional -- it is entity-STATE / event-world-knowledge / implicit
causality (which entity plausibly undergoes THIS event given the discourse), the genuinely deeper next build.

## BUILD 3 (attempted): implicit-causality next-mention prior -- a LOCATED NEGATIVE (with a mathematically-BF fusion win)
`experiments/exp_affected_entity_ic_prior_gum_v1.py` (witness `verification/test_affected_entity_ic_prior.py`).
Research prescribed IC (Garvey-Caramazza; Hartshorne-Snedeker; Kehler-Rohde) as the same-type-discriminating prior;
VERIFY-FIRST confirmed a populated stratum (IC-verb governs 158/1142 = 14%; salience wrong on 64%). Built it
mathematically BF per owner directive: the EMPIRICAL Ferstl-2011 305-verb human IC norm (not the BF_SPIRIT categorical
psych_verb_frames), the BF salience_binder, and Ernst-Banks CALIBRATED INVERSE-VARIANCE fusion (informedness weights,
held-out even-split -- NOT the BF_SPIRIT margin-based convergent_cue_reader that misfired in build 2), GATED.
RESULT: **LOCATED NEGATIVE.** On the IC-present stratum (n=80): salience 0.2875, **IC-alone 0.05 (BELOW chance)**,
calibrated fusion 0.25 (-0.038, not CI-sep). **CLEAN MECHANISM:** IC is a next-mention prior for a FOLLOWING pronoun
in a causal continuation ("frightened Bill because HE" -> the CAUSE); our undergoer pronoun is the verb's own
ARGUMENT ("frightened HIM"), whose referent is set by coref/salience, not by the verb's causal bias (which is about a
DIFFERENT participant). IC structurally does not predict argument-pronoun referents. **TWO VALIDATIONS:** (1) the
mathematically-BF calibrated inverse-variance fusion WORKED as designed -- it DOWN-weighted the bad cue (w_ic 0.107
<< w_sal 0.376), unlike build-2's margin weighting which UP-weighted a confident-wrong cue; the gate held. (2)
Combined with build 2, a convergent principled result: for undergoer-pronoun affected-entity resolution, the SALIENCE
PRIOR is the lever; neither type-coherence (phi subsumes it) nor IC (wrong configuration) adds. The residual (~55%)
needs the deeper entity-STATE / generative world-model, or is genuinely ambiguous.

## BUILD 4 (the corrected lever) -- a WIN: we had built only the PRIOR; the LIKELIHOOD half is the lever
`experiments/exp_affected_entity_binding_parallelism_gum_v1.py` (witness `test_affected_entity_binding_parallelism.py`
4/4). Diagnostic research explained ALL THREE prior negatives with one root cause: pronoun reference is a cascade
phi -> BINDING -> salience -> semantics; we built only the salience PRIOR P(referent) (saturates 0.45) and added
level-4 SEMANTIC cues (type = redundant given phi; IC = wrong configuration). The discriminating action for an
ARGUMENT pronoun is the LIKELIHOOD P(pronoun|referent): (i) BINDING PRINCIPLE B [PINNED universal] = a hard zero
(a co-argument would be a REFLEXIVE, not a plain pronoun; "John hit HIM" => him != John); (ii) role/thematic
PARALLELISM [PINNED] = a soft bias (object pronouns take object antecedents; our subject-biased ROLE_PROMINENCE is
BACKWARDS for object anaphors). **THE KILLER DIAGNOSTIC:** the current subject-biased salience picks the ILLEGAL
co-argument **19.4% of the time** (221/1142) -- it was ranking the Principle-B-forbidden clause-mate subject #1;
that single number mechanistically explains the 0.45 wall. **RESULT (n=1142 pronoun undergoers, GUM gold roles):**
A1 salience 0.3704 -> A2 Principle-B filter (PARAMETER-FREE) **0.4186 (+0.048 CI[0.031,0.065] CI-sep)** -> A5 full
Principle-B + parallelism **0.4632 (+0.093 CI[0.066,0.119] CI-sep)** -- ~doubling the lift, ROBUST across gamma
(0.5->+0.084, 1.0->+0.093, 2.0->+0.060, all CI-sep). CONTROLS: scramble candidate role labels collapses the
parallelism gain (0.463->0.439); info-free uniform-over-Principle-B-survivors loses (0.125). **MATHEMATICALLY BF
(owner-verified):** Principle B = PINNED categorical universal implemented FRESH from the parse (not the
BF-unregistered gold-mention organ); parallelism = the PINNED Bayesian LIKELIHOOD form exp(gamma*1[role-match])
(gamma swept, not adopted -- not the BF_SPIRIT "invented arithmetic"); salience = ACT-R (BF). Upstream all
mathematically BF; the deployment parse is the one declared NOT_BF offline scaffold.
**DEPLOYMENT NUMBER (PREDICTED supervised parse, not gold roles; n=952):** the lever SURVIVES -- A1 salience 0.3603
-> A2 Principle-B **0.4097 (+0.049 CI[0.032,0.067] CI-sep -- essentially IDENTICAL to the +0.048 on gold; the
PINNED co-argument universal is ROBUST to parser error)** -> A5 full **0.4202 (+0.060 CI[0.033,0.089] CI-sep)**; the
parallelism term degrades ~1/3 under noisy predicted role labels (A5 gold +0.093 -> deployed +0.060), Principle B is
unchanged. Illegal-co-argument diagnostic holds (0.19 gold -> 0.21 deployed). This is a genuine DEPLOYMENT win, not a
gold-roles artifact. **This is the correct lever the three semantic negatives pointed to: for argument-pronoun
resolution the win is GRAMMAR (binding + parallelism), not semantics.**

## FINAL DOCUMENTATION -- TRUE BF STATUS OF EVERY COMPONENT TOUCHED/BUILT
| component | role in this work | TRUE BF status |
|---|---|---|
| harm/help force-dynamic arithmetic (`force_dynamics_valence` proposed) | the ORIGINAL decision (separate SOLVED problem) | **BF_SPIRIT** (Wolff/Talmy force x grounded Warriner valence x Beavers affectedness) |
| `salience_binder.actr_activation` | forward salience prior (milestone 1) | **BF** (registry-confirmed; ACT-R base-level, Anderson/Lewis-Vasishth) |
| `graded_coref_pick` | backward likelihood (deployed pronoun pick) | **BF** |
| Binding PRINCIPLE B filter (built fresh, `exp_affected_entity_binding_parallelism_gum_v1`) | the win's HARD likelihood term | **PINNED universal** (Chomsky 1981/Reinhart) implemented from the parse; NOT the BF-unregistered gold-mention `coreference_resolver._principle_b_filter` |
| role/thematic PARALLELISM (built fresh) | the win's SOFT likelihood term | **PINNED** (Smyth 1994/Stevenson 1995) as the Bayesian likelihood exp(gamma*1[role-match]); gamma SWEPT; NOT the BF_SPIRIT "invented-arithmetic" `coref.CENTER_PARALLEL_BONUS` |
| Ernst-Banks calibrated inverse-variance fusion (built, build 3) | reliability weighting | **PINNED** (Ernst-Banks 2002 MLE / Ma-Pouget); replaced the BF_SPIRIT margin-based `convergent_cue_reader` |
| Ferstl-2011 305-verb IC norm (asset, build 3) | IC cue (located negative) | empirical HUMAN foundation asset (the brain's measured IC signal; not a stand-in); used instead of BF_SPIRIT `psych_verb_frames` |
| typed selectional preference (Resnik/WordNet, built) | knowledge densifier (typed_selectional problem) | **BF_SPIRIT** (Resnik 1996 class-based selectional association over admissible WordNet is-a) |
| `crf_tagger.GlassBoxCRF` calibrated posterior | POS cluster (located negative) | **BF_SPIRIT** representation (calibrated forward-backward), SUPERVISED acquisition |
| `unified_referent` / `online_entity_cluster` / `event_centrality_coref` | coref stack (milestone 1 reuse) | untagged / **BF_SPIRIT** (Heim file-change + ACT-R; gold-free) |
| `pos_tagger` (perceptron), `arc_parser`, `arc_labeler` | THE DEPLOYMENT PARSE SPINE | **NOT_BF** (supervised averaged-perceptrons) -- a DECLARED offline scaffold (project pivot); the deployment number above uses this predicted parse |
| GUM (coref x UD) / UD-EWT / WordNet / Ferstl / selectional_slots(simplewiki) | corpora + norm/foundation assets | modern gold + admissible offline foundations (selectional store reading-grown; WordNet admissible per manifest C5) |

**BF discipline honored (owner directives):** every BF_SPIRIT organ in a WINNING path was upgraded to its mathematical
form before use (margin->inverse-variance; hand-list->empirical norms) or reimplemented mathematically (Principle B,
parallelism). The single un-upgraded NOT_BF dependency is the supervised parse spine, a declared scaffold -- which is
exactly why the headline lever was measured on gold roles AND re-measured on the predicted parse (it survives).

## PRIORITY NEXT STEPS (finalized)
1. **LAND the corrected resolver into the live undergoer/patient pick (Q111 -- strategy lands hdlab).** Wire the
   mathematically-BF Principle-B co-argument filter + role-conditioned (thematic-parallelism) salience into
   `situation_reader`'s patient resolution. Mechanisms exist but are DORMANT/unwired + subject-biased
   (`coreference_resolver._principle_b_filter`, `graded_coref_pick` parallel cue at weight 0). Deployment number
   already measured on the PREDICTED parse: +0.049 (Principle B, robust) to +0.060 (full) CI-sep. Add a
   `board_affected_entity_dimension()` so the win is scored, not latent.
2. **BUILD 5 -- the generative entity-STATE / world-model reranker (the ~40% situation-bound residual; the north
   star).** Reuse `hdlab.state_register` (BF_SPIRIT, per-entity state spans; Dowty proto-patient change-of-state = a
   state delta) to score candidate undergoers by the coherence of their state update (Rabovsky-McClelland N400 =
   situation-update magnitude), fused reliability-weighted by the mathematically-BF Ernst-Banks INVERSE-VARIANCE (NOT
   margin) with the salience prior + binding + parallelism cues. The only lever left for the residual grammar cannot
   reach; the deepest-fidelity, hardest gain.
3. **Recover the deployed parallelism term:** it degrades ~1/3 under predicted role labels; improving the role
   labeler (arc_labeler cluster) or using graded (marginal) role labels would restore the gold-vs-deployed gap.
4. Harm/help decision stays SOLVED + BF; the typed-selectional organ, parse cache, and the located negatives
   (POS hard-commit, type-coherence, IC-misapplication) remain banked as durable negatives.
