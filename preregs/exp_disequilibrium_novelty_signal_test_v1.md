# Prereg: exp_disequilibrium_novelty_signal_test_v1

Date: 2026-08-04. Author: Director (main thread, no dispatch). Measurement-first decisive-DIRECTION
test. Cites notes/research_self_extending_grounded_knowledge_prior_art_2026-08-04.md parts (b)/(c)/(h).

## Question
Before building a schema-minting operator for the self-extending grounded-knowledge acquirer: does
a signal our EXISTING organs already compute distinguish "this passage needs a genuinely-new
causal-role schema" from "this fits an existing schema slot"? If yes, minting is a cheap routing
ACTION on top of existing organs. If no, a dedicated novelty-detector must be built first.

Two signals tested (coordinator upgrade 2026-08-04 added the brain-faithful PRIMARY):
- PRIMARY (brain-faithful): the prediction-error RESIDUAL MAGNITUDE from hdlab/predictive_coding.py
  (Friston / Rao-Ballard; the CA1 match-mismatch / mPFC schema-incongruence signal). The current
  situation-model schema library is Hebbian-encoded into W (native causal schema templates as
  autoassociative fixed points); each item's causal structure is presented as the observed pattern;
  residual_magnitude(observed, predict(W, observed)) = how unexplained the item is by the library.
- SECONDARY (the note's original): the self_improving_loop / situation_model_accumulate FHRR
  coherence-margin (top1-vs-runner-up cleanup margin) of a cause-attribution decode, scored against
  the FIXED existing role vocabulary vs an EXTENDED vocabulary (fresh causal role allowed).

## Items (n=18)
The 8 causal cross-span multi_candidate_causal_attribution items (grapp_mcca_001,003,004,005 from
gold_grounded_appraisal_richer_v1.jsonl + grapp_mcca_006,007,008,009 from
gold_grounded_causal_crossspan_v2_DRAFT.jsonl -- the v2 DRAFT file holds 4; the other 4 mcca items
live in the appraisal_richer file; together they are the 8 the note refers to) + the 10 detective
items (gold_causal_crossspan_detective_v3_DRAFT.jsonl crossspan_det_001..010).

## Labels (BLIND to BOTH signals -- from causal STRUCTURE only)
Binary label per item, one uniform criterion applied before any signal was computed:
- fits_existing_schema: the true cause is a DIRECT AGENTIVE PHYSICAL ACT on the affected entity
  (kill/stab/pour/tear/drop/take/instrument-mediated kill), representable by the current
  agent/patient/theme/CAUSE/EFFECT vocabulary.
- needs_new_schema: identifying the true cause requires a causal-role type the current vocab LACKS
  -- OMISSION (failure-to-act), MISREPRESENTATION/DECEPTION (forgery/disguise/framing/staging),
  SOCIAL/INDIRECT (collusion / unwitting-intermediary / instigation), or COUNTERFACTUAL/NON-AGENTIVE
  (no crime occurred / natural death / self-caused / animal reaction).
Labels + per-item causal-structure justification + the fine-grained feature set are enumerated in
the experiment file's ITEMS table (flagged needs_director_review=True).

## Current role vocabulary being labeled against (enumerated from disk)
situation_model_accumulate semantic roles {agent, patient, theme, recipient, addressee, speaker}
(verify_situation_model_accumulate.py / _multibank_dropin.py); CausalLinkRegister meta-roles
{CAUSE, EFFECT}; read_anne_glassbox {agent, mentioned}. No distinct causal-role TYPE exists for
bribe/dare/provocation/omission/misrepresentation/counterfactual/social -- all collapse to generic
agenthood or the single generic CAUSE role.

## Method
- N=1024, seeds 0..29 (30), deterministic (seeded RNG per seed; sorted iteration). Per-item value =
  mean over seeds. Both signals reuse existing organs unchanged (no new mechanism).
- PRIMARY residual: W = Hebbian sum of native-schema-template autoassociative fixed points
  (the current library's expressible causal schemas: physical_harm, physical_help, theft,
  instrument, accident -- each a majority-bundle of NATIVE feature atoms). Each item's observed =
  majority-bundle of its causal-account feature atoms (native + non-native). residual via
  hdlab.predictive_coding.predict + residual_magnitude, verbatim.
- SECONDARY coherence-margin: FHRR cause-attribution register (reuses situation_model_accumulate
  unit_phase_vec/binding/bundling/cleanup_argmax): OUTCOME register = bundle over candidates of
  bind(role, filler); decode true cause by unbind(role)+cleanup over fillers; margin = top1-runnerup.
  Fixed vocab: non-native true cause force-fit to CAUSE and its distractor also collapses to CAUSE
  (collision); extended vocab: fresh role for the true cause. margin_fixed is the disequilibrium
  signal (predicted LOW for needs_new).

## PRE-REGISTERED BANDS (set before looking at results; applied to BOTH signals)
Direction: needs_new_schema is the HIGH-residual / LOW-coherence-margin class.
- HARD_PASS: the two label classes separate on the signal -- mean gap >= 0.05 (on the signal's
  native [0,1] scale) AND non-overlapping inter-quartile ranges. => the disequilibrium signal is
  already free in an existing organ; minting = a routing ACTION to add.
- HARD_FAIL: distributions overlap >50% (Mann-Whitney U two-sided p > 0.10). => existing organ
  insufficient as the minting trigger; a dedicated detector must be built first.
- MIDDLE: partial separation (neither band fully met) -- report honestly + route.

## Guards
Glass-box; organs reused unchanged; no borrowed embedding/LLM/parser; deterministic; labels BLIND
to both signals (fairness -- the whole test is invalid if labels are signal-informed); contamination
clean (labels+features fixed in-file before running). n=18 TINY + underpowered -- decisive-DIRECTION
only, not a powered claim. KNOWN CAVEAT (front-of-report): the item->feature-set / native-vs-non-native
typing is Director-supplied; a "separation" result shows the organ can SCORE novelty GIVEN a faithful
typing, not that it produces the typing autonomously (that gap is itself decision-relevant).
