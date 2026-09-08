# POST-COMPACTION HANDOFF -- chain_multi_step_plans_and_scripts_for_the_generative_world_model

**Written 2026-09-08 before an intentional compaction. Owner: "We'll tackle all of those components after compaction."**
This is the entry point for resuming. Read this, then SOLVED.md + BRAIN_FOUNDATIONAL_ANALYSIS_2026-09-08.md (sec.12 = the
complete component audit). Solver scope: write experiments/ + verification/ + this folder only; NO hdlab (Q111);
NO external LLM at inference; heavy runs are ~110s CPU (inline OK).

## 2026-09-08 POST-COMPACTION UPDATE -- BUILD-QUEUE STEP 1-2 DONE (located negative)
Built the FORWARD EVENT-TRANSITION model (steps 1-2 below) to the research-pinned spec (SEM bound HRR role-filler
rep + schema-conditioned nonlinear transition + Rabovsky N400-update-magnitude + inverse-planning diagnostic +
closed forward loop; T over 141k-147k ATOMIC xEffect/oEffect/Causes pairs). Cell: exp_multistep_forward_transition_v1.py.
Detail: FORWARD_TRANSITION_RESULT_2026-09-08.md. Witness EXTENDED to 23/23 (W20-W23).
- The organ is CONSTRUCTION-VALIDATED: operator smoke-gate Cohen's d 0.26->0.68 (schema-conditioned PASSES >=0.5).
- DECISIVE DISSOCIATION: doubling the operator strength (gate +164%) barely moved the task (+0.008->+0.019; every
  variant TIES base 0.2773, none beats its info-free twin); the confound "+18pt" is a TWIN-FAILING ARTIFACT.
- So the forward-prediction bet is a LOCATED NEGATIVE, proven NOT a weak-operator artifact: GENERAL-commonsense
  forward prediction does not discriminate the causal edge at TellMeWhy granularity. The forward loop CAN now close
  (forward_expect_fn ready) -- chain-fidelity progress -- but closing it alone does not cross this task.
- REMAINING ROUTE (only one the evidence leaves open): the STORY-SPECIFIC recurrent generative loop (steps 4-5 below,
  online-learned dynamics), NOT a general forward prior. Research pin: notes/research_forward_event_transition_n400_causal_2026-09-08.md.

## WHERE WE ARE (status)
- STATUS: PARTIAL. Witness: `.venv/Scripts/python.exe verification/test_multistep_meansend_chain.py` (19/19, ~15s).
- GENUINE ADVANCE (banked): the ATL-hub means-end (ATOMIC PPMI+SVD) cracked the parent's coverage wall 8.7%->88%
  and DOUBLED the goal-subset win (me2 0.5326, +0.2391 CI[0.1304,0.3587] CI-sep, twin loses p=0) on TellMeWhy non-adj.
- FULL-POPULATION: TIES base 0.2773 (located negative). Traced to the mechanism level (below).

## THE COMPLETE COMPONENT AUDIT (owner's 4-step re-frame; END -> up; only 3/9 are 100% brain-foundational)
The end component ("why q?") = causal-network RETRIEVAL (sm.ultimate_cause over sm.causal_links) -- brain-foundational
IN FORM (Trabasso-van den Broek 1985; Graesser 1994). Its INPUT chain is where the signal is lost:
- I1 causal LINKS: `_read_causation`->`causal_net_cause` = connective-position + hardcoded force sets + recency
  (_causal_network.py:143). CHEAP post-hoc cascade. NOT brain-foundational. **Signal LOST here.**
- I2 forward prediction + N400 error (Kuperberg-Jaeger 2016; Rabovsky 2018; Kutas-Hillyard 1980): predictive_reader
  (patient-feature grain, discarded for causation); n400_coherence_monitor is BACKWARD-ONLY (forward_expect_fn=None)
  + unwired to causation. **HALF the mechanism + unwired.** Prototype-confirmed: backward-only N400 is ANTI-selective.
- I3 grounded meaning channel (ATL hub, Lambon-Ralph): meaning_foundation LATENT (no live read()-time consumer). **Not live.**
- I4 participant binding (Heim/Kamp file-cards): surface positional/recency, coref-blind. Deviation, but MEASURED NOT the
  cap (object-sharing != causation).
- I5 parse (incremental predictive; Bornkessel-Schlesewsky): spaCy arc-eager hard-commit; parse_once decode="exact" =
  graded parser HARD MAP, marginals discarded ("change NO head", graded_parser.py:29). Non-faithful (not the loss: 0.98).
- I6 means-end knowledge: ATOMIC PPMI+SVD hub. **BRAIN-FOUNDATIONAL (this work).**
- ARCH the loop (Rao-Ballard; Friston; Kuperberg): FEED-FORWARD pipeline; predictive loop unclosed. **Dominant deviation.**
- DEC decision (McClelland-Rumelhart; Thagard ECHO; Gold-Shadlen DDM): additive/max-union; ECHO+DDM unbuilt. Partial.

## THE ORDERED BUILD PLAN (the components to tackle after compaction -- dependency order)
The crossing = make causal-link inference ONLINE-PREDICTIVE. The signal is there (per-engine ladder: a PERFECT goal
engine alone = +0.25 full-pop). Build, in order:
1. **FORWARD EVENT-TRANSITION MODEL (the one genuinely-missing organ).** Predict q's EVENT from C's event over the
   grounded meaning channel (predictive_reader is the wrong grain -- patient features, not next events). This is the
   core generative transition (TEM/SEM-style, Whittington 2020 / Franklin 2020). Learned offline (admissible static
   asset) or online propose-verify; glass-box rollout at inference.
2. **CLOSE THE N400 FORWARD LOOP.** Supply n400_coherence_monitor.forward_expect_fn = the forward event-transition
   prediction, so the N400 is a genuine prediction-ERROR signal (not backward gist-coherence). Score cause(C,q) =
   the forward prediction-error REDUCTION C gives q.
3. **WIRE THE GROUNDED MEANING CHANNEL LIVE (I3).** meaning_foundation -> a live read()-time consumer (the forward
   model predicts over it). This is the KNOWLEDGE-LEVER north star (curated foundation first, then online grow).
4. **CONSUME THE PREDICTIVE SIGNAL IN CAUSAL-LINK INFERENCE (I1).** Replace/augment _read_causation's cue-cascade with
   the predictive-integration signal (cause = min prediction error). Strategy lands hdlab (Q111).
5. **THE RECURRENT LOOP (ARCH).** Situation model feeds top-down expectations DOWN into parse/coref/sense-selection;
   prediction error flows UP. bound_event_backbone (LANDED default-on) is the shared event-state; wire predictive_reader
   + n400 into it. ~60% built default-off per the parent's full-chain eval.
6. (secondary) graded-parse marginals as a graded structure signal (I5); signed-pairwise ECHO coherence + DDM commit (DEC).
NOTE: this IS the parent's named MAIN EVENT (the recurrent generative world-model) + strategy's live coref (E3). It is a
MULTI-CELL program, not a single solver cell. Sequence: build the forward transition model FIRST (steps 1-2 are one cell,
measurable in isolation on the grounded channel), then wire live (steps 3-5, Q111).

## REUSABLE ASSETS (import, do NOT rebuild) -- with pointers
- compute_causal_link + build_frames + build_verbnet_endstate_map (experiments/exp_joint_causal_simulate_v1.py): the
  LANDED precise causal composer (STRIPS result-state->precondition + force-dynamics + inverse-planning + affect).
- MeansEnd + build_indices (experiments/exp_multistep_meansend_chain_v1.py): the ATL-hub means-end (ATOMIC PPMI+SVD) +
  inverse-planning diagnosticity. THE brain-foundational goal engine.
- hdlab/predictive_reader.py (PredictiveReader.surprisal); hdlab/n400_coherence_monitor.py (N400CoherenceMonitor.observe,
  the forward_expect_fn hook at ~:97); hdlab/bound_event_backbone.py (BoundEventBackbone.build, default-on).
- hdlab/meaning_foundation.py (LATENT); hdlab/causal_reasoner.py (CausalGraph traversal); hdlab/state_of_mind.py
  (WorkingOverlay: gender/number agreement + Centering); hdlab/graded_parser.py (marginals, currently discarded).
- Gold: data/corpora/tellmewhy/ (TMW.load_items). Assets: data/cskg_foundation_v1/ (ATOMIC), data/frontend_assets/
  associative_similarity_store_v1.npz (grounded meaning proxy), data/lexicons/name_gender_gazetteer.tsv.
- My cells: exp_multistep_meansend_chain_v1.py (goal engine + ladder + all located negatives),
  exp_multistep_multiengine_v1.py (precise composer + resolved binding), exp_multistep_predictive_v1.py (predictive-
  integration prototype). Metrics in data/exp_multistep_*_v1/metrics.json.

## DO NOT REDO (located negatives, measured this session -- do not re-run)
- coref for the goal engine (surface-agent decomposition was an ARTIFACT; gender-aware resolver plumbing-sound but does
  NOT beat recency; the false-flips are same-person). Resolution QUALITY is not the goal-engine lever on this gold.
- gold-incompleteness as the OTHER-damage explanation (answer-lenient gold: goal engine STILL -0.055 CI-sep below base).
- directional/verb-anchored means-end (over-fire is the hub precision ceiling, not a noun self-match; hurts GOAL).
- well-formedness / degenerate-q filter (marginal).
- teleological-stance ROUTER keyed on the explanandum (qint|goal 0.99 ~= qint|other 0.97 -- does not separate).
- TEMPORAL/SCRIPT order store (hdlab.temporal_script_schema) as a cause-SELECTION cue (context-free; worsens OTHER;
  it is validated for its HOME task = implicit-event ORDERING, not cause-selection).
- AFFECT engine alone (~10% domain).
- multiplicative content-gate (still -0.098 on OTHER).
- BROAD multi-engine competition (U8 lemma engines: promiscuous, physics dead or over-fires; ties).
- PRECISE multi-engine competition (compute_causal_link STRIPS composer): ties; resolved-participant binding fires 2x but
  no precision gain -- object-sharing != causation.
- BACKWARD-only N400 surprise-reduction (predint): ANTI-selective, -0.1445 CI-sep below base -- forward half is essential.
- single-step VerbNet lexicon; GEK co-occurrence (directionless); CSKG retrieval (coverage-bound). External LLM (invariant).

## KEY NUMBERS (do not re-derive)
- base_mult 0.2773 / topical 0.2500 (TellMeWhy non-adj, n=256, GOAL 92 / OTHER 164).
- GOAL: me2 0.5326 (+0.2391 CI-sep, twin loses); coverage me2 88% vs parent single-step 8.7% / CSKG 22%.
- FULL: every arm ties (me_diag +0.0117; compete +0.0156; predint -0.1445 anti-selective).
- PER-ENGINE LADDER (perfect-engine incremental full-pop lift): base 0.277 -> +goal +0.250 -> +physics +0.086 ->
  +mental +0.047 -> +affect +0.043 -> +associative +0.297 (=gold). The goal signal (+0.25) is recoverable via routing/
  competition; associative 39% is base/topical territory (ceiling ~0.70 for the typed engines).

## HAZARD (operational)
This problem folder (untracked) was WIPED once mid-session by a concurrent git operation during strategy's coref commits
(a worktree/clean step). I restored it from context. If PROBLEM.md/SOLVED.md/this file vanish, that is the concurrent-
session git hazard, not a solver error -- restore from git reflog or context. The auto-stage ("hd_metrics_sync auto-stage:
N notes/") periodically commits notes/, which should persist this file.
