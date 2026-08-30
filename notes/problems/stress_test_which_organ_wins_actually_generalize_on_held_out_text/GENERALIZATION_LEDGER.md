# GENERALIZATION LEDGER — which organ wins actually generalize on held-out text

**Problem:** `stress_test_which_organ_wins_actually_generalize_on_held_out_text` (solver, opus 4.8).
**Method:** `tools/generalization_audit.py` keyword-triaged 33/81 organs as "constructed-headlined / thin
generalization tail." That tool OVER-FLAGS (its own caveat). I read the actual `SOLVED.md` of all 33 and
recorded, for each: was the HEADLINE on a CONSTRUCTED gold or a pre-existing/held-out population? what n?
is there a real-text number? is it load-bearing (live-wired / assembly-bound / foundational)? — then
**reran** the top load-bearing genuinely-fragile cluster on a pre-existing population.

**Bottom line of the triage:** of the 33 keyword-flagged organs, **10 are FALSE POSITIVES** (already
validated on QA-SRL / LitBank / SimLex-SimVerb at n = 995 … 28,569, CI-separated, twin losing), **9 are
ALREADY NEGATIVES** (the `SOLVED` is itself a refutation on real/held-out data — exactly the outcome this
audit wants), and **13 are GENUINELY FRAGILE** (a constructed/synthetic win with no strong pre-existing
validation). *The keyword scan cannot tell these apart — only reading the n and the population can.*

> **HOW TO READ A ROW:** `constructed number → held-out number → HOLDS / DOES-NOT-HOLD (+ population, floor,
> twin)`. A DOES-NOT-HOLD is a **rigorous negative = a full PASS**: it tells strategy to fix, de-scope, or
> "constructed-only, do not wire" *before* the fragility is imported into the live reader.

---

## CATEGORY A — FALSE POSITIVES (keyword-flagged, but already strongly held-out-validated). DO NOT re-audit; these are the TEMPLATE.

| organ | held-out population (n) | headline vs floor | twin | verdict |
|---|---|---|---|---|
| `lookup_does_not_lemmatise` | SimVerb-test **2490** + dev 418 + SimLex-noun 447 (pre-existing) | rho +0.185 [0.127,0.235] over orthographic 0.021; REPLICATED 3/3 | loses | **HOLDS** — LANDED foundational primitive |
| `the_argument_parser_is_batch_where_the_brain_is_incremental` | QA-SRL v2 **28,149** predicates | INCR F1 0.6201 vs BATCH 0.5849 (+0.035), vs POSITIONAL2 0.5937 (+0.026) | loses | **HOLDS** (identification; role-assignment gain is tail-only) |
| `the_entity_store_is_a_dense_bundle_that_fans` | LitBank **28,569** who-did-what | fan slope diagnosis + FINER/FACTORIZED fix, all CI-sep | loses | **HOLDS** — the audit's template |
| `discrete_where_the_brain_is_graded_in_parsing_and_role_assignment` | QA-SRL **17,324** predicates | entropy beats binary difficulty AUC 0.646 vs 0.512 (+0.133) | loses | **HOLDS** |
| `optimize_and_validate_the_learner_before_it_grows_the_foundation` | SimLex-999 **995** + SimVerb-3500 **3432** + LitBank | rho +0.060 / +0.034 over PPMI-SVD window; growth-safety on LitBank | loses | **HOLDS** (secondary drills stay exploratory) |
| `the_situation_model_tracks_words_not_entities` | QA-SRL v2 **1708** + independent split **672** | surprisal +0.055 / +0.040 over BAG floor | actively hurts | **HOLDS** (small but real) |
| `theory_of_mind_residual_is_the_observation_cue_front_end` | LitBank **1230** held-out + **86** intact windows | ledger 0.985 vs lexical 0.500 | loses | **HOLDS** — promoted to `hdlab/perceptual_access_ledger.py` |
| `pronoun_to_event_binding_caps_who_did_what` | LitBank **4661** (3 splits) | binder 0.204 vs ACT-R 0.143 (+0.061) | loses (all 3 splits) | **HOLDS** (modest; Centering-Cb sub-hypothesis refuted) |
| `the_register_reads_by_argmax_not_recurrent_completion` | LitBank real high-fan tail **91** entities | serial 1.000 vs argmax 0.959 (+0.041) | loses | **HOLDS** — but bulk (≤63 events) is INERT (argmax=serial=1.0) |
| `dimensional_phase_diagram_audit_of_the_current_organs` | LitBank (n_pron **1863**) + SimLex **645** + real WordNet codes | dimensionality-not-the-bottleneck negative, on real data | loses | **HOLDS** (it is itself a negative/audit) |

## CATEGORY B — ALREADY NEGATIVES (the `SOLVED` is itself a rigorous refutation on real/held-out data). No fragile "win" to defend — this is the outcome the audit exists to produce.

| organ | real/held-out population (n) | result | status |
|---|---|---|---|
| `flat_store_destroys_the_code` | SimpleWiki **5490** held-out | addressed 0.1399 **LOSES** to counting floor 0.3242 | REFUTED — *the archetype: an addressed store loses to counting on real text* |
| `the_reading_extractor_may_not_beat_a_two_line_rule` | QA-SRL **17,330** | elaborate reader 0.7511 **LOSES** to two-line rule 0.7661 → REPLACE | SOLVED-negative |
| `the_discourse_fact_reasoner_is_unvalidated_on_natural_text` | LitBank **4023** competitive coref | fact-bridge fired unconditionally **net-negative** (−0.022/−0.125); DEV-optimal weight 0 | SOLVED-negative (narrow gated +ve on n=667) |
| `the_reader_has_no_coherence_next_mention_prior` | LitBank **205** + GAP **437** | coherence prior does NOT beat its own shuffled twin (NOT_SEP); cross-domain confirmed | REFUTED |
| `causation_is_typed_per_clause_not_across_the_causal_network` | LitBank **19** cross-sentence | typer 0.158 **LOSES** to majority-CAUSE 0.842 | SOLVED-negative — route closed |
| `the_sign_quantiser_makes_the_substrate_an_averaging_machine` | modern corpus **4000** + WordSim/SimLex | read-out claim REFUTED; binding effect ~0 live (n=6020) | REFUTED (latent-only risk) |
| `reader_meaning_channel` | self-built WSD **287w/841t** | grounded hub 0.470 does NOT clear MFS_PRIOR 0.478 (CI-uncleared) | REFUTED |
| `teach_the_self_built_space_instead_of_concatenating_it` | self-built unseen-cooc **~270×3** | all taught arms below floor AND below their own twin | REFUTED |
| `wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end` | McGuffey **178** | composed reader 0.483 **BELOW** majority 0.781; front-end is the bottleneck | PARTIAL-negative |

## CATEGORY C — GENUINELY FRAGILE (constructed/synthetic win, NO strong pre-existing validation). THE RERUN TARGETS, ranked by load-bearing × fragility.

| # | organ | constructed headline | held-out evidence | load-bearing | rerun target |
|---|---|---|---|---|---|
| **T1a** | `content_addressable_retrieval_over_a_separated_store` | SEP_CA **0.99** vs FLAT 0.05 @ synthetic load=32, p=0.7 | none (author: "isolation win ≠ capability") | ISLAND (default-off `decode_cue`) | **RERUN DONE ↓** — LitBank per-entity real load |
| **T1b** | `the_core_binding_operator_may_not_be_brain_faithful` | theta/CA3 **0.128** vs flat FHRR 0.025 (~5×) @ synthetic \|V\|=256 | none ("synthetic-algebra construction proof") | FOUNDATIONAL (the live bind/bundle) | covered by T1a (same SEP-vs-FLAT mechanism) |
| **T1c** | `resolve_retrieval_interference_among_similar_memories` | CTX_ADD **0.928** vs 0.400 @ synthetic engineered-separable context | none (author: "is the substrate's REAL context separable?") | ASSEMBLY_BOUND | LitBank/OntoNotes similar-competitor coref w/ real context — **FOLLOW-ON** |
| **T1d** | `the_register_write_path_has_a_hard_capacity_wall` | LEAKY **1.0** at all loads vs flat collapse @ synthetic random codes | none ("real-text end-to-end: did NOT establish") | ISLAND (`leak=0.0` live default) | same load-regime story as T1a |
| **T2a** | `causation_has_no_force_dynamic_typing` | 0.929 (n=**42** minimal pairs) | weak: n=21 McGuffey, solver-adjudicated | ISLAND | **RERUN DONE ↓↓ — DOES NOT HOLD** (MAVEN-ERE n=9,698) |
| **T2b** | `causation_typing_needs_a_patient_tendency_estimator` | 1.000 (n=**40** minimal pairs) | weak: n=13 point-estimate; UD-EWT fire-rate only | ISLAND (sense/attach-gated) | **RERUN DONE ↓↓ — DOES NOT HOLD** (shares the force-dynamic typer) |
| **T3a** | `situation_model_has_no_discourse_fact_reasoning` | L1 **0.998** vs 0.504 (constructed) | **already dead** on LitBank L2 (bridge oracle 0.039) | ISLAND/QUEUED | half-refuted; needs a real fact-decisive population |
| **T3b** | `theory_of_mind_is_proven_only_in_a_synthetic_microworld` | 1.000 (n=**26** authored passages) | none (n<30, solver-authored) | ASSEMBLY_BOUND (`belief_partition.py` island) | LitBank-mined false-belief scenes — **FOLLOW-ON** |
| **T3c** | `the_substrate_does_not_learn_or_update_by_prediction_error` | N400 **0.988** (synthetic clean topic-jumps) | none ("synthetic construction proof") | ISLAND | LitBank/GUM event segmentation — **FOLLOW-ON** |
| **T3d** | `the_relcl_parser_is_too_weak_for_filler_gap_role_assignment` | 0.953 (n=**4800** synthetic) | **negligible** +0.0011 on QA-SRL (reversibles rare) | ISLAND | needs a reversible-rich real corpus |
| **T3e** | `no_automatic_reliability_signal_reaches_the_source_oracle` | +0.041 (self-built n=5490 recall instrument) | none (self-built instrument) | ISLAND | real partial-cue QA population |
| **T3f** | `one_store_does_two_jobs_and_consolidation_is_a_single_average` | sparse replay 0.784 vs 0.680 (self-built PPMI) | none | ISLAND, PARTIAL | real old/new chronological split |
| **T3g** | `the_live_front_end_mislabels_who_did_what_to_whom` | McGuffey **ties** floor; twin NOT CI-sep | word-order sub-claim validated on QA-SRL n=12,810 | ASSEMBLY_BOUND | modern role-balanced end-to-end rerun |

---

## THE DEEP RERUN — the store/retrieval/binding cluster (T1) on real LitBank

**The cluster's shared claim:** a SEPARATED, content-addressable / CA3 store beats a FLAT superposition
read-out under load / partial cue. Every organ proved it on a synthetic random codebook at fixed high
load (32–64 items/register). **The one prior real-text test of this family (`flat_store`) LOST to
counting 0.14 vs 0.32.**

**What I ran** (`experiments/exp_generalize_retrieval_real_codes_v1.py`): the EXACT retrieval arms
(imported verbatim from the content_addressable cell) on the **real LitBank who-did-what population**
(n=28,569 events, 7,779 entities, gold coref) as **per-entity registers at their REAL event counts**,
real Zipfian verb fillers (same verb → same code = real confusability), against the strongest real floor
(**per-entity verb COUNTING**), the info-free twin, and a synthetic **positive control** that reproduces
the organ's win (SEP_CA 0.990 vs FLAT 0.047 @ load=32 — the exact 0.99 headline).

**The real operating point is the finding:** 72.6% of real entities carry **1** event, 87.3% carry ≤3 —
the load regime where FLAT superposition is already near-perfect. The synthetic organs live at load=32,
which is ~2% of real entities.

*(numbers below are the smoke pass, n=60/bin; the full real-frequency-weighted run confirms them — see SOLVED.md)*

| entity events | % of real | SEP_CA | FLAT | **SEP−FLAT** (the claim) | SEP−COUNTING | twin loses? |
|---|---|---|---|---|---|---|
| 1 | 72.6% | 1.000 | 1.000 | +0.000 tie | +0.000 tie | n/a |
| 2–3 | 14.7% | 1.000 | 0.981 | **+0.019 NOT_SEP** | +0.439 ABOVE | yes |
| 4–8 | 6.5% | 1.000 | 0.742 | +0.258 ABOVE | +0.652 ABOVE | yes |
| 9–16 | 2.6% | 0.999 | 0.456 | +0.543 ABOVE | +0.761 ABOVE | yes |
| 17–63 | 2.4% | 0.990 | 0.178 | +0.811 ABOVE | +0.821 ABOVE | yes |
| 64+ | 1.2% | 0.976 | 0.052 | +0.924 ABOVE | +0.839 ABOVE | yes |

**Verdict — HOLDS DIRECTIONALLY, MAGNITUDE COLLAPSES 15–60×** (full run, real-frequency-weighted, n_sampled=1376):

| comparison | @full cue p=0.0 | @degraded cue p=0.7 | band |
|---|---|---|---|
| SEP−FLAT (the organ's specific claim) | **+0.016** [0.011,0.022] | **+0.060** [0.050,0.070] | ABOVE (tiny) |
| SEP−COUNTING (register beats the dumb floor) | +0.157 [0.142,0.171] | **+0.156** [0.142,0.170] | ABOVE |
| FLAT−COUNTING (flat already beats counting) | +0.140 | +0.096 | ABOVE |
| SEP−twin (info-free) | +0.144 | +0.144 | ABOVE |

per-bin SEP−FLAT @p=0.7: `1`=+0.000 · `2-3`=+0.022 · `4-8`=+0.204 · `9-16`=+0.525 · `17-63`=+0.813 · `64+`=+0.924.

The organ's win is *real* (twin loses; CI-separated) but **its magnitude is a steep function of load**, and the
real operating point sits deep in the easy regime: the synthetic **+0.94** (SEP over FLAT) shrinks to
**+0.060** (degraded cue) / **+0.016** (full cue) on LitBank, because 87% of entities have ≤3 events where FLAT
is already ≥0.98. **Two true readings:** the SPECIFIC "separated beats flat" claim survives only as a small
busy-entity-only +0.06; the BROADER "a register beats pure counting" claim survives robustly at +0.156 (contra
`flat_store`), but FLAT already delivers most of it. **Wire the separated machinery for the ~13% of "busy"
entities (≥4 events), not for the population.**

**Brain-foundational drill — DG pattern-separation HURTS here, and the correlated-codes drill said WHY**
(SEP_CA_DG 0.50–0.64 vs SEP_CA 0.98 at the tail; DG−SEP = −0.35 to −0.48, the SAME whether filler codes are
orthogonal OR deliberately correlated). DG is not "for correlated fillers" — the retrieval match runs over the
**addresses** `bind(entity, event-index)`, which are **unique by index** in a per-entity register, so DG's
expand+sparsify only injects noise. → **AUDIT UPDATE:** DG-at-retrieval is a fix for confusable *addresses*
(the fan / key-overlap `rho>0` regime — where the content_addressable organ's own sweep found DG helps), NOT
confusable fillers; do not wire it onto a register whose addresses are distinct.

---

## SECOND DEEP RERUN — the causation-typer cluster (T2a/T2b) on real MAVEN-ERE → DOES NOT HOLD

**The claim:** a glass-box force-dynamic typer (Talmy/Wolff CAUSE/ENABLE/PREVENT truth-table over a
FrameNet-derived verb lexicon) distinguishes causal sub-types, headlined at 0.929 / 1.000 on n=42 / n=40
connective-neutral **minimal pairs**. Only real-text checks were tiny solver-adjudicated point estimates
(n=13 / n=21). **What I ran** (`experiments/exp_generalize_causation_typer_maven_ere_v1.py`): the SAME force
lexicon + typer (imported verbatim from `experiments._force_dynamics_lexicon`) on **MAVEN-ERE** (Wang et al.
2022) valid split — **n=9,698 independently-annotated causal relations** (CAUSE vs PRECONDITION≈ENABLE).

| | value | reading |
|---|---|---|
| **fire rate** | **0.161** (1,559 / 9,698) | the typer's required input (a force-dynamic causing verb) is ABSENT in 84% of real causal relations |
| typer accuracy where it fires | 0.183 [0.164,0.203] | anti-aligned with the corpus |
| **strongest floor = majority class** | 0.863 (predict ENABLE) | **typer − majority = −0.679 [−0.713,−0.647] BELOW** |
| **info-free twin** (shuffled lexicon) | 0.165 | **typer − twin = +0.018 NOT_SEP** — the force signal ≈ noise for the real distinction |
| coverage-weighted lift | **−0.109** | |

**Verdict: DOES NOT HOLD.** The constructed 0.929 / 1.000 win does not survive on real annotated causation:
the typer (i) fires on only 16% of real causal relations (its force-verb input is usually absent), and
(ii) where it fires, its force-class signal is **statistically indistinguishable from a shuffled lexicon**
(+0.018 NOT_SEP) for the real CAUSE-vs-PRECONDITION distinction, losing to the majority floor by −0.68. This
**confirms the sibling organ** `causation_is_typed_per_clause` (LitBank negative, 0.158 vs 0.842, n=19) on a
**500× larger, independent corpus**. **Fairness caveat (disclosed):** MAVEN's PRECONDITION is not identical
to Wolff's ENABLE (ontology mismatch), so the raw accuracy-vs-majority gap is partly a label-scheme mismatch
— but the two decisive facts are ontology-INDEPENDENT: the 16% fire-rate (the input rarely exists) and the
typer≈shuffled-twin result (no real force signal) both fail regardless of the label scheme.
→ **AUDIT UPDATE:** reclassify the force-dynamic causation typers "constructed-only; on real annotated
causation the typer's input is usually absent and its force signal ≈ noise — do not wire as a real-text
capability." The brain's force-dynamic representation may be real (Wolff PINNED), but the *lexicon-keyed
connective typer* is not how it survives contact with real causal annotation.

**…then pushed the wall (research drill + gate), symmetric with the retrieval reframe.** A literature drill
(`research_causation_typer_wall_implicit_and_mental_causation_2026-08-30.md`) returned a PINNED verdict: real
narrative causation is a **whole-event causal-GRAPH** property inferred by a **different brain system**
(Trabasso & van den Broek causal-network; Kintsch construction-integration; Graesser causal-antecedent
inference; Mason & Just 2004 + Kuperberg 2011 — implicit connective-less causal inference recruits left
IFG/MTG + rostral mPFC, N400-only). The typer is **narrowly-valid-but-mis-scoped** (keep for explicit
physical predication), NOT a wrong primitive. The empirical **gate**
(`exp_generalize_causation_implicit_covariation_gate_v1.py`): a glass-box **event-type covariation** scorer
(Chambers & Jurafsky / Hu & Walker precedent) = **0.889**, beating its own shuffled twin **+0.094 ABOVE**
(a REAL signal — where force-dynamics was +0.018 NOT_SEP), the majority floor **+0.056** (clears the
pre-registered +0.05 HARD-PASS), and the force-dynamic typer **+0.165**, and it carries signal precisely on
the **83.9% no-fire subset** (+0.058 over majority, +0.099 over twin). → **Named next problem:**
`narrative_causal_graph_missing_implicit_inference_organ` (the missing implicit event-event causal-inference
route; adjacent brain system = the narrative causal-network / construction-integration network, PINNED at
the separability level). *The missing route is BETTER brain-grounded than the force-dynamic typer — there is
a verified absence of any neural study of force-dynamic causal verbs, while the implicit-inference network is
PINNED.*

## THE SWEEP SO FAR — two rigorous reruns, contrasting outcomes, six organs

| rerun | organs covered | population (n) | verdict |
|---|---|---|---|
| store/retrieval/binding | T1a–d (4) | LitBank who-did-what (28,569) | **HOLDS DIRECTIONALLY**, magnitude collapses 15–60× → wire for busy entities only; then reframed onto the PINNED similar-competitor axis (gate: content floor 0.398 on 22,123 → BUILD) |
| causation typer | T2a–b (2) | MAVEN-ERE causal (9,698) | **DOES NOT HOLD** (16% fire-rate; force signal ≈ shuffled twin) |

Two of the 13 fragile organs already carried their own real-text negatives (found in triage:
`causation_is_typed_per_clause`, `situation_model_has_no_discourse_fact_reasoning`'s LitBank L2). The
remaining ~7 (N400 segmenter, ToM-microworld, relcl parser, reliability-signal, consolidation store,
front-end mislabel) are enumerated with corpora above as follow-on reruns — the sweep is valuable partial
(brief-sanctioned) and now rests on **two** rigorous, contrasting reruns plus the full 33-organ triage.
