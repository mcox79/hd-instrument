# SYNTHESIS -- deep brain-foundational audit of the semantic-meaning barrier (2026-08-06)

USER-requested (after the generalization probe showed the wired organs don't generalize to real prose):
"deep audit of the brain-foundational aspect of every component we're using on this barrier, and exactly,
precisely, how the brain does it." 4 parallel per-component audits (research, Sonnet) + Director synthesis.
Source notes: audit_brain_semantic_representation_similarity_2026-08-06.md (A),
audit_brain_feature_acquisition_grounding_2026-08-06.md (B), audit_brain_categorization_control_2026-08-06.md (C),
audit_brain_composition_situationmodel_2026-08-06.md (D). All disk-VET'd for their load-bearing claims.

## THE BARRIER (precise)
The wired goal-owner/outcome-valence organs are HARD_PASS on hand-authored instruments but score owner-acc 0.30
vs recency 0.70 on real McGuffey prose (open-vocab verb-typing fix moved it to 0.50; remaining blockers are
CONSTRUCTIONS beyond verbs -- predicate-nominal praise, affect-states). The barrier = OPEN-VOCAB GROUNDED MEANING.

## CONSOLIDATED BRAIN-vs-US MAP (per component: exact brain mechanism | ours | verdict)
| Component | How the brain does it (precise, cited) | Ours | Verdict |
|---|---|---|---|
| SIMILARITY | ATL transmodal hub: learned graded DISTRIBUTED pattern; similarity = SHARED-FEATURE CORRELATION (Cox/Rogers/Shimotake 2024 intracranial vATL) | FHRR bundle-cosine over feature vectors | **MECHANISM + FORMAT FAITHFUL** (cosine-over-features = shared-feature correlation). Gap = feature SOURCE + no grounding-spokes + no context-control layer. |
| FEATURES | ~65 experiential dims (Binder 2016) EMERGENT from error-driven Hebbian learning + CLS consolidation across grounded spokes; ABSTRACT concepts (goal/hope/fail/praise) ground via affect + mentalizing + metaphor + DOPAMINERGIC REWARD-PREDICTION-ERROR; new words via Bayesian taxonomic prior (Xu-Tenenbaum) + SYNTACTIC BOOTSTRAPPING | hand-named, hand-assigned symbolic tags | **CORE GAP, 2 parts:** (a) supplied->LEARNED = cheap/piloted (NNSE-on-PPMI, bootstrapping); (b) abstract-symbolic->GROUNDED = the LOAD-BEARING WALL (unsolved even in literature) -- BUT goal/outcome concepts ground via reward-PE we OWN (pfc_gate_cfrpe_trained_v2 HARD_PASS). |
| CATEGORIZATION | "good boy=goal met" via a VERB-FREE 4-stage path: (1) CONSTRUCTION licenses evaluative reading (Goldberg CxG); (2) CONTENT-BLIND VALUATION (OFC/vmPFC/ventral-striatum, same as monetary reward; Izuma/Ruff-Fehr); (3) graded no-threshold membership; (4) DISCOURSE-COHERENCE INFERENCE binds valuation to the goal (Kintsch CI, Trabasso Goal->Attempt->Outcome) | hard-threshold argmax over VERB-lemma cosine; only tokens surviving lemma_verb() | **RIGHT METRIC, WRONG SHAPE** (verb-only structural blind spot -- never sees good/boy/are). Steps 1,2,4 UNREPRESENTED. We OWN valuation (grounded_appraisal_sim) + situation-model. |
| COMPOSITION+BINDING | LATL minimal composition (Bemis-Pylkkanen) + LIFG unification (Hagoort); hippocampal relational binding; TENSOR-PRODUCT/superposition code fits real who-did-what-to-whom fMRI BETTER than segregated registers (Lalisse-Smolensky 2021 reanalysis of Frankland-Greene) | FHRR bind (role*filler) + bundle + GoalOutcomeRegister/CausalLinkRegister + coref | **OUR MOST FAITHFUL cluster -- fMRI-VINDICATED** (role*filler+bundle = the tensor-product code that fits brain data). NOT the barrier. |

## THE DECISIVE FINDING (the "slight difference that means success vs failure")
Similarity (A) and binding (D) are FAITHFUL -- neither is the barrier. The barrier is TWO things:
1. **FEATURES: supplied vs LEARNED+GROUNDED.** Learned = cheap (piloted). GROUNDED-abstract = the deep wall,
   BUT the concepts our organ needs (goal/outcome-valence) ground in REWARD-PREDICTION-ERROR, which we OWN
   (pfc_gate_cfrpe). Three of four audits converged on this independently.
2. **SHAPE: lexical/verb-typing vs CONSTRUCTION -> VALUATION -> BRIDGING-INFERENCE.** The mg2 "good boy=goal met"
   case has ZERO shared verb/theme/lexical content between the goal clause and outcome clause -- so NO similarity,
   verb-typing, or theme-match can EVER bridge them (we could perfect all of them and still fail). Only BRIDGING
   INFERENCE over non-lexical pragmatic/social links (Graesser Class-7 causal-antecedent inference; Kintsch
   construct-integrate; EST schema forward-prediction) solves it -- and this inferential layer DOES NOT EXIST in
   the substrate. **We have been attacking outcomes with LEXICAL machinery where the brain uses INFERENCE.**

## RECOMMENDED DIRECTION (Director)
Stop chasing supplied-feature coverage (wrong shape, doesn't scale). Two moves, mostly OWNED organs:
- **NEAR-TERM (highest leverage, fixes the wrong-shape gap + the exact real-prose blockers):** add the
  CONSTRUCTION -> VALUATION -> BRIDGING-INFERENCE path. Detect evaluative/affect constructions (predicate-nominal
  praise, affect-states) -> route to the OWNED valuation organ (grounded_appraisal_sim) for a POS-blind
  goal-congruence appraisal (NOT verb-typing) -> BIND the valuation to the goal-state via a bridging-inference
  ADD-ON to the OWNED GoalOutcomeRegister (D's specified cheap decisive test: hand-authored evaluative-speech-act
  bridging bank, strict add-on, NO new binding operator, pre-reg HARD-PASS/HARD-FAIL). This structurally fixes
  the "good boy=goal met" class that lexical methods CANNOT reach.
- **DEEP (the wall / grounded-foundation pivot):** ground abstract goal/outcome-valence concepts in the
  REWARD-PREDICTION-ERROR signal (pfc_gate_cfrpe, owned) -- the brain's actual grounding for these (Reber 2017
  vmPFC coupling: sequence outcome-valence/goal grounding first). Feature-LEARNING (NNSE-on-PPMI / bootstrapping)
  reduces hand-supply in parallel (cheap).

## STRATEGIC SHIFT
The recent negatives (generalization probe, splitter->construction finding) were NOT telling us to type more
verbs. They were telling us the MEANING PATH has the wrong SHAPE: lexical/verb-typing + supplied-ungrounded
features, where the brain runs grounded (reward-PE) features + a construction/valuation/INFERENCE architecture.
The mechanism and binding are already faithful; the missing pieces (bridging inference; abstract-concept
grounding) are buildable largely from organs we've already PROVEN (grounded_appraisal_sim, pfc_gate_cfrpe,
GoalOutcomeRegister). This is a genuine fork the USER should see before committing the build sequence.
