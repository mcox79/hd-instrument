# Prereg: coherence_selector_text_transfer_v1 (2026-08-04)

## The load-bearing question
Everything the coherence-SELECTOR earned is IN-SIM. `exp_coherence_selector_novel_types_v3.py`
earned an abstract structural coherence rule (pick the candidate whose EFFECT matches the
OUTCOME) that generalizes to NOVEL sim types at coherence_acc=0.8733 (MEASURED@
data/exp_coherence_selector_novel_types_v3/metrics.json, seeds [7,17,23,31,41]). THE question:
does that sim-earned selector TRANSFER to REAL TEXT? First end-to-end-on-real-text test of the
causal-selection machinery.

## Brain structures named
- The selector = a hippocampal/entorhinal SUCCESSOR-REPRESENTATION backward-transport map
  `M_backward` (learned TD(0)/SR delta-rule; `train_sr_transport`) that, from an OUTCOME state,
  reaches back to its predecessor CAUSE (analogous to hippocampal reverse-replay / relational
  antecedent retrieval). Coherence = `reach_value(outcome, cand, M) = cos(outcome @ M, cand)`.
- The text->vector bridge = a substrate-native VSA/HDC content encoder (`CharTrigramEncoder`,
  Kanerva bag-of-trigrams) standing in for perceptual/lexical cortex encoding a span into a
  distributed code. No borrowed embedding / LLM / parser (glass-box invariant).

## Design (ORACLE structure, isolates SELECTOR-transfer from extraction — like arm-A of the
## prior transfer cell exp_grounded_appraisal_transfer_to_text_v1)
Items (n=7, Director-verified backward-causal, true cause stated/known but NOT most-recent):
- richer_v1: grapp_mcca_001, 003, 004, 005
- crossspan_v2_DRAFT (Director-ACCEPTED): grapp_mcca_007, 008, 009
- EXCLUDE grapp_mcca_006 (Director-REJECTED: mis-annotated span).

Given (oracle) candidate structure: the two competing candidates are the `true_blocker_span`
(slot 0) and `distractor_span` (slot 1). Slot order is a FIXED bookkeeping convention; the
mechanism is never told which slot is the answer — it computes a symmetric coherence score per
candidate and picks argmax. `true_blocker_agent`/`distractor_agent`/`recency_baseline_prediction`/
`recency_baseline_correct` are NEVER read by the selector or raw-match mechanism (contamination
assert). The recency baseline's OWN gold correctness annotation is read ONLY to report the
recency floor, firewalled from every mechanism.

The bridge (crux): for each item encode
- outcome_vec = CharTrigramEncoder.encode(goal_owner + " " + query_span.text)   [2048-dim]
- cand_vec[i]  = CharTrigramEncoder.encode(candidate_span_i.text)               [2048-dim]
Reuse M_backward BIT-IDENTICAL (reconstructed per seed via novel_types_v3's exact procedure; NO
retrain on text). Score_i = reach_value(outcome_vec, cand_vec[i], M_backward); pick argmax.

## Arms
- SIM_SANITY (mechanism-intact proof): reconstruct M_backward per seed, run novel_types_v3's
  arm_novel_1hop unchanged. MUST reproduce coherence_acc >= 0.80 (target 0.8733). Isolates
  "M_backward broken" from "representation doesn't transfer".
- ARM_SELECTOR_TEXT (primary): M_backward reach_value on text-derived vectors, per item, mean
  over 5 seeds.
- ARM_RAWMATCH_TEXT (gap localizer): score_i = cos(cand_vec[i], outcome_vec), NO learned map
  (identity-M control = reach_control_targetcos on text). If this beats baselines but the
  selector does not -> the abstract RULE transfers but the learned MAP does not.
- Baselines: RECENCY (gold-declared, 0/7 by construction) + POSITIONAL-RECENCY (max candidate
  line <= query, transparent) + RANDOM (seeded + analytic 0.5).

## Pre-registered outcomes (can-fail; either is valuable — do NOT force a pass; n=7 is TINY)
- BRIDGES: sim_sanity>=0.80 AND selector_text_acc >= 5/7 (0.714) AND > both recency floors AND
  > 0.5 + margin. => first evidence the sim-earned causal selector transfers to real text.
- CANNOT_BRIDGE_REPRESENTATION_GAP: sim_sanity>=0.80 (M intact) AND selector_text_acc in
  [0.30,0.60] (~chance). => the sim-to-text REPRESENTATION bridge is the gap; M_backward's
  learned geometry (inverse of the sim's fixed permutation T) has no path to text content.
  Routes next build: re-ground the selector on a text-compatible representation.
- PARTIAL: selector in (0.60,0.714); OR rawmatch beats baselines while selector does not (rule
  transfers, map does not); OR sim_sanity itself < 0.80 (reconstruction/mechanism problem ->
  GATE, no transfer claim either way).

## Guards
- Deterministic (encoder deterministic; M per seed deterministic; random seeded). Seeds
  [7,17,23,31,41] (novel_types_v3's own seeds) for M_backward reconstruction.
- Contamination assert: forbidden gold fields never reach any mechanism function.
- n=7 directional feasibility probe, NOT a powered result — stated in verdict.
- Reuses (bit-identical import): exp_coherence_selector_novel_types_v3 (build_perm_transform,
  build_type_base_vectors, build_chain_trajectories, ChainPartition, collect_rollout_transitions,
  train_sr_transport, reach_value, reach_control_targetcos, _arm, N_DIM & all SR hyperparams);
  hdlab.char_trigram_encoder.CharTrigramEncoder.
