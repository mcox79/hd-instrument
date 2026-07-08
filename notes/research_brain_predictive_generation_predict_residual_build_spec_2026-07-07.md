# exp_dev hand-off -- research: brain-grounded predictive-generation mechanism

Filed-by: research sub-agent
Date: 2026-07-07
Trigger: notes/research_brain_predictive_generation_mechanism_2026-07-07.md
Urgency: MEDIUM -- sequenced FOLLOW-ON to an already-recommended probe, not a standalone priority. Do not
front-run `CLEANUP_PER_STEP` (from `notes/research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md`)
with this arm; add both to the same cell/dispatch cycle if convenient (they share a harness and baselines),
but the decision-sequencing table in the research note governs which result matters most.

---

## Pause state

Experiment below is PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ONE anchor candidate only. Experiment design details (exact TD-bootstrap
delta-rule form, residual-unbind implementation, smoke/FULL grid, seed values) are to be authored by exp_dev
from the research note + the cited existing cell/primitive files. Do NOT treat the description below as an
implementation spec.

---

## Anchor candidates (rank-ordered)

### Anchor 1: `PREDICT_RESIDUAL_TD` arm on `exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py`

Anchor pointer: research note Section 3 ("BUILD RECOMMENDATION") and the "Cheap decisive test" section.

Substrate-product reading: adds a new arm to the SAME already-GPU-proven cell the sibling `CLEANUP_PER_STEP`
arm targets (`exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py`, N=8192, already landed MIDDLE_BAND:
single=62.1, ensemble=43.1, bigram_count=55.8, trigram_count_oracle=20.4 perplexity). Composes FOUR existing
primitives (sequence/positional binding, `hdlab/iterative_attractor.py` CA3-style cleanup, the existing
hetero-associative `W_hetero` context->next-item matrix, argmax/lookup decode) plus TWO small, well-specified
algorithmic changes grounded in this cycle's lit-scan:
  (a) inject the prediction RESIDUAL (`unbind(encode(actual_token), hetero_associative_readout(W_hetero,
      c_{t-1}))`) into the context accumulator at each step, instead of the raw token encoding (the
      predictive-coding/free-energy-principle read: Rao & Ballard 1999; Sennesh/Millidge et al. arXiv:2111.10530
      Kalman-filter-as-fixed-point derivation);
  (b) replace `W_hetero`'s static count/Hebbian update rule with a TD(0)-bootstrapped delta rule (the
      successor-representation read: Dayan 1993; Stachenfeld, Botvinick & Gershman 2017, *Nat. Neurosci.* 20;
      Barreto et al. 2017/2019 successor-features generalization to vector feature spaces).
Per-step CA3 cleanup (identical to the sibling `CLEANUP_PER_STEP` arm) is retained on top of both changes --
this arm is additive to, not a replacement for, the sibling arm.

Tier hint: same GPU tier as the sibling `CLEANUP_PER_STEP` arm (reuses its harness, corpus, baselines --
no new corpus, no new codebook, no new baseline-building). Smoke first at reduced-corpus scale, K in {1,2,3}
matching the sibling arm's smoke grid, before any FULL dispatch.

Why-now: the sibling `CLEANUP_PER_STEP` arm is the shallow-version antidote (denoise raw-accumulated context
after the fact); this arm is the deep-version antidote (reduce how much noise enters the accumulator per step
in the first place, via prediction-residual injection, PLUS make the associative matrix itself self-correcting
via bootstrapped learning rather than static counting). Both mechanisms are independently well-evidenced in the
neuroscience literature (this cycle's 3 parallel lit-scans, ~19 sources verified via direct search) and are
complementary, not redundant, per the research note's Section 2 analysis (repeater-style cleanup vs.
differential/predictive-encoder-style noise reduction). Running both arms in the same dispatch cycle costs
little marginal smoke time since they share a harness, and the decision-sequencing table (research note Section
3) tells exp_dev / Director which result governs the next move regardless of which arm lands first.

Pre-reg bands (full detail + honesty-gate resolution in the research note):
  HARD-PASS: `PREDICT_RESIDUAL_TD` beats `CLEANUP_PER_STEP` by >= 0.2 bits at K>=3, improvement grows (not
    shrinks) with K, `W_hetero`'s TD-bootstrap prediction accuracy improves monotonically over the corpus
    stream (not diverging), holds across >= 3 seeds (CV <= 0.15).
  HARD-FAIL: performs the same as or worse than `CLEANUP_PER_STEP` at all K, OR the TD-bootstrap update
    diverges/oscillates, OR the residual turns out noisier than the raw token (a real, specifically flagged
    risk given the substrate's own ~0.507 concept-recall rate per `exp_n1_concept_lm_substrate_native_token_decode_v3_1`
    -- roughly half of predictions are wrong, so a naively-computed residual against a wrong prediction could
    inject MORE noise, not less).
  MIDDLE_BAND: helps at low K (2-3) but advantage does not persist/grow at higher K -- route to the
    disjoint-block/frame-slot-style context-encoding fallback lever (already named in the sibling note) rather
    than iterating further on this arm.
  P_deflated ~0.25-0.30 (see research note falsifiable-predictions section for full derivation).

---

## Context pointers (file paths, not summaries)

- This drill's research note: d:/AI/hd-instrument/notes/research_brain_predictive_generation_mechanism_2026-07-07.md
- Sibling probe note (shallow-version antidote, run/sequence FIRST or alongside): d:/AI/hd-instrument/notes/research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md
- Cell to extend (shared with sibling arm): experiments/exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py
  + data/exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu*/metrics.json
- Cleanup primitive (existing, do not reimplement): hdlab/iterative_attractor.py, hdlab/cleanup_family.py
- Sequence/positional binding primitive (existing): hdlab/sequence_memory.py, hdlab/char_positional_encoder.py
- Concept-recall-rate reference (0.507, the residual-noise risk source): exp_n1_concept_lm_substrate_native_token_decode_v3_1
  metrics.json
- 4 prior HARD_FAIL/MIDDLE_BAND context-depth cells (do not re-run as-is; this arm is a NEW composition, not a
  retread): exp_n2_context_depth_hd_binding_v1, exp_n5_trigram_concept_lm_v1,
  exp_substrate_direct_gen_lm_wikitext_trigram_v3_n8192_gpu (all HARD_FAIL); the 2ndorder-trigram cell itself
  (MIDDLE_BAND, the cell being extended).
- Reasoning-depth survival-law reference (quantitative target for depth-curve fit, carried not re-derived):
  notes/research_reasoning_depth_self_margin_closed_form_2026-07-06.md
- att1-family cleanup risk flag (independently documented, applies to BOTH this arm and the sibling arm since
  both retain per-step cleanup): notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md

---

## Contract section

This handoff proposes ONE anchor, additive to the sibling `CLEANUP_PER_STEP` handoff. Exp_dev authors the exact
TD-bootstrap delta-rule form for `W_hetero` (following the standard TD(0) update `M(s,s') <- M(s,s') +
alpha*(delta_{s,s'} + gamma*M(s_next,s') - M(s,s'))` generalized to the substrate's vector/feature representation
per the successor-features formalism, Barreto et al.), the exact residual-unbind implementation, smoke grid, and
seed count. Do not treat the pseudocode in the research note's Section 3 as literal implementation code -- it is
a mechanism sketch, not a spec.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing the exact TD-bootstrap delta-rule implementation (learning rate alpha, discount gamma, whether to
  use a running-average or fixed-alpha update) within standard TD(0)/successor-features practice
- Choosing whether to dispatch this arm in the SAME cell/cycle as the sibling `CLEANUP_PER_STEP` arm or
  sequence it after (per the decision-sequencing table in the research note, but exp_dev may judge the marginal
  smoke cost of running both together is low enough to do so regardless of sequencing preference)
- Choosing smoke vs FULL seed counts and grid density within the pre-registered bands above
- Choosing local CPU vs remote_cpu_queue / GPU routing per the SMOKE-only-local rule

Exp_dev is NOT autonomous in:
- Declaring this arm supersedes or replaces the sibling `CLEANUP_PER_STEP` arm -- both are additive per-step
  cleanup remains in both arms; this arm only changes WHAT gets accumulated and HOW `W_hetero` learns
- Declaring CG promotion (Skunkworks/VET decides the tier per landed-VET discipline)
- Reopening the iterative-cleanup mechanism itself as a lever (CA3-style cleanup is retained unchanged from the
  sibling arm; the novelty here is residual-injection + TD-bootstrap learning, not a different cleanup method)
