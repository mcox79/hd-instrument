# exp_dev hand-off -- research: self-explanation / introspection primitive (Stage 3, M3 glass-box)

**Filed:** 2026-06-27 PDT by research (sub-agent spawn; main thread will dispatch exp_dev wrapper).

**Trigger:** Research drill `notes/research_drill_2x_self_explanation_introspection_primitive_stage3_2026-06-27.md` (overnight priority; USER load-bearing concern #2 for M3). Faithful self-explanation primitive closes the "doctor who can't show their work" gap in the glass-box conversational target. Two cells designed; ranked Top-1 + Top-2; both CPU-eligible; sit ALONGSIDE 2026-06-27 metacog stack (orthogonal layer, not in conflict).

**Pause state:** check `data/orchestrator_paused.flag`. If paused, file as queued-for-resume; do not auto-dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + MECHANISM POINTERS + DISCRIMINATOR BANDS only. exp_dev (spawn `hdi_exp_dev`) designs ALL of: N_DIM exact value, V_CONCEPTS exact, M_TRIPLES exact, K trace-depth exact, seed selection, smoke profile (must FIRE discriminator at full-N or use full-N preview arm per DISCRIMINATOR-MUST-SURVIVE-SCALE), CARDINALITY_OK breach values, run-mode plumbing, queue choice (local_cpu vs remote_cpu), threshold-fitting on calib set, anchor name suffix, ETA, predispatch_check invocation, smoke-vs-full gating.

Research does NOT specify exact numerical parameters. Bands below are HARD-PASS / HARD-FAIL gating; intermediate parameter tuning is exp_dev autonomy.

---

## Anchor candidates (rank-ordered; both for refill)

### Anchor #1 (Top-1; recommended ship-first) -- `self_explanation_deletion_fidelity_v1`

- **Anchor pointer:** `notes/research_drill_2x_self_explanation_introspection_primitive_stage3_2026-06-27.md` Cell #1.
- **Substrate-product reading:** addresses M3 glass-box property 7-8 (faithful self-explanation). Substrate-product framing: "RAG with native faithful attribution built into the storage primitive" -- a CAPABILITY Wallat ICTIR 2025 documents 57% of LLM RAG systems lack. Differentiator on the doctor-shows-their-work axis.
- **Tier hint:** likely local_cpu (pure numpy + HRR unbind; expected 10-20 min full per CRLB estimate). exp_dev decides.
- **Mechanism pointer:** HRR reverse-cleanup of output O through stored binds (K_i, V_i); contribution_score_i = |inner_product(unbind(O, K_i^{-1}), V_i)|. For each top-K=5 trace atom, deletion-counterfactual arm: re-query with that bind subtracted; faithfulness = Spearman rho(contribution_score, output_delta) over K=5 x N=~500 queries x 3 seeds.
- **Arm contract:** 3 arms must structurally differ (META_RULE_AF). TRUE_TRACE (substrate's bind-based explanation), RANDOM_TRACE (oracle strawman; chance baseline), COSINE_TRACE (raw cosine to query; "obvious explanation" confound).
- **Discriminator bands (research-owned; do NOT relax):**
  - HARD_PASS: TRUE_TRACE rho >= 0.70 AND RANDOM_TRACE rho in [-0.10, +0.10] AND TRUE - COSINE >= 0.15.
  - HARD_FAIL: TRUE rho < 0.40 OR TRUE - COSINE <= 0.
  - MIDDLE_BAND: TRUE rho in [0.40, 0.70] OR TRUE - COSINE in [0.05, 0.15].
- **By-construction-saturation:** if COSINE_TRACE alone HARD_PASS, by-construction-tier down and require cleanup-margin < 0.1 regime before claiming bind-primitive lift.
- **Why now:** USER load-bearing for M3; metacog stack closed today; explanation layer is the next missing piece; CPU-eligible (no overnight queue contention).
- **Critical prior-art FIX:** `substrate_audit_chain_coherence_benchmark_v1` HARD_FAILed because refuse_threshold was 0.55 * mean_known_conf = 0.025 (below noise floor). This cell MUST compute threshold from calib-set cosine percentile that maximizes refuse_accuracy. exp_dev: verify this before smoke.
- **Smoke discipline (THREE SMOKE DISCIPLINES 2026-06-26 + DISCRIMINATOR-MUST-SURVIVE-SCALE):** smoke must FIRE discriminator (observe TRUE > RANDOM rho gap at smoke-N); if smoke shows TRUE-RANDOM gap < 0.20, do NOT dispatch full -- use full-N preview arm to verify discriminator survives scale.

### Anchor #2 (Top-2; ship after Anchor #1) -- `self_explanation_per_step_metacog_attribution_v1`

- **Anchor pointer:** `notes/research_drill_2x_self_explanation_introspection_primitive_stage3_2026-06-27.md` Cell #2.
- **Substrate-product reading:** per-step confidence over the explanation trace -- brain analog of rostrolateral PFC layer-2 readout (2025 macaque PFC paper Cell Neuron S0896-6273(25)00887-6). Substrate-product feature: "I am 0.92 confident on step 1, 0.45 on step 2, 0.88 on step 3" -- a structurally novel feature LLMs cannot ship today.
- **Tier hint:** local_cpu; depends on Anchor #1's deletion data (run AFTER Anchor #1 lands; reuse its deletion arm for the AA ground truth attribution).
- **Mechanism pointer:** per-hop metacog confidence = product over K=5 hops of (cosine_sep_hop_i / max_cosine_sep_hop_i). NeuroFaith Attribution-Agreement: AA = cosine(forward_attribution_vector_from_deletion, claimed_attribution_vector_from_per_step_confidence) per query.
- **Arm contract:** PER_STEP_METACOG (full mechanism), GLOBAL_METACOG (per-query metacog uniform over K steps; control), CONSTANT_CONFIDENCE (1.0 uniform; strawman).
- **Discriminator bands:**
  - HARD_PASS: PER_STEP AA >= 0.60 AND PER_STEP - GLOBAL >= 0.10 AND PER_STEP - CONSTANT >= 0.20.
  - HARD_FAIL: PER_STEP AA < 0.30 OR PER_STEP - GLOBAL <= 0.
  - MIDDLE_BAND: PER_STEP AA in [0.30, 0.60].
- **Independence pre-check (DISCRIMINATOR-MEASURES-MECHANISM lesson from 2026-06-27 metacog-composition-failures drill):** before claiming per-step lift, verify Pearson rho between per-step and global metacog signals < 0.4 on calib set. If correlated >= 0.4, the bar is unfair -- per-step cannot add information over global; cell author MUST report rho explicitly OR redesign to use structurally orthogonal signals (e.g., cleanup-margin + ultrametric-cluster-stability instead of two metacog variants).
- **By-construction-saturation:** if GLOBAL_METACOG alone HARD_PASS, do not claim per-step adds value; route to MM.
- **Dependency:** Anchor #2 needs Anchor #1's HARD_PASS to be meaningful (Cell #2 AA needs Cell #1's deletion-derived ground truth attribution). If Anchor #1 HARD_FAILs, queue Anchor #2 as REVISED (substrate's trace is unfaithful at atom level; per-step layer is undefined). exp_dev: hold Anchor #2 until Anchor #1 lands.

---

## Context pointers (file paths, not summaries)

- `notes/research_drill_2x_self_explanation_introspection_primitive_stage3_2026-06-27.md` -- this drill (Cell #1 + Cell #2 full spec).
- `notes/research_drill_3x_substrate_self_monitoring_metacognition_2026-06-27.md` -- metacog stack state; cosine_sep + entropy AUROC=0.86 single-signals (chain-grade) needed for per-step metacog in Anchor #2.
- `notes/research_drill_2x_metacog_composition_failures_2026-06-27.md` -- DISCRIMINATOR-MEASURES-MECHANISM + signal-independence lesson; applies directly to Anchor #2.
- `experiments/exp_substrate_audit_chain_coherence_benchmark_v1.py` -- prior cell; refuse-gate calibration bug to FIX in Anchor #1 (refuse_threshold = 0.55 * mean_known_conf was below noise floor; use percentile-based threshold instead).
- `experiments/exp_substrate_introspection_toolkit_full_10_categories_v1.py` -- Cat6 DELETION-CERT did not operate (deletion_cert_operational=False); investigate this code path and ensure Anchor #1's deletion arm actually mutates the substrate store.
- `experiments/exp_causal_chain_extraction_end_to_end_v1.py` -- ARM_A_FULL chain-MRR=0.000 vs ARM_C_TEMP_ONLY chain-MRR=0.750 (composition-over-primitive trap). Apply META_RULE_AA fairness-before-tier in Anchor #1 by ensuring COSINE_TRACE strawman runs at the same N as TRUE_TRACE.
- `data/exp_substrate_audit_chain_coherence_benchmark_v1/metrics.json` -- HARD_FAIL provenance=0.678 calib_r=0.072 refuse=0.127.
- `data/exp_substrate_introspection_toolkit_full_10_categories_v1/metrics.json` -- MIDDLE_BAND 42% wrong-confident (confabulation signature).
- `data/exp_meta_knowledge_partition_coverage_v1/metrics.json` -- AUROC values for per-step metacog signals (cosine_sep, entropy).
- `tools/predispatch_check.py` -- run on both anchors per Fix #26.
- `tools/peek_arm_metrics.py` -- use per Fix #28 before any tier/framing claim.

---

## Pre-dispatch verify-the-referent gate (Fix #26)

exp_dev: run
```
python tools/predispatch_check.py self_explanation_deletion_fidelity_v1
python tools/predispatch_check.py self_explanation_per_step_metacog_attribution_v1
```

Expected: 0 matching landings (these are new anchor names); proceed.

If predispatch_check finds prior runs (e.g., from prior auto-renames), DO NOT silently re-run; surface to research first.

---

## Contract

- Research OWNS mechanism + falsifiable bands (above; do NOT relax).
- exp_dev OWNS cell-spec authoring + smoke + dispatch + run_mode plumbing + CARDINALITY_OK pre-reg + queue choice.
- Skunkworks OWNS landed-VET classification + by-construction-saturation tier-down + cert-decision (MM default until promoted).
- Fix #28: read per-arm metrics, NOT verdict_msg framings.
- META_RULE_AB: independence pre-check before composition-lift claim.
- THREE SMOKE DISCIPLINES 2026-06-26: no silent except; smoke FIRES discriminator; band-floor = MIDDLE_BAND.
- DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke discriminator must survive at full-N (use check A/B/C per USER 2026-06-26).
- Atomic write (.tmp + rename) per META_RULE_AH.

## Autonomy declaration

exp_dev decides: N_DIM exact (research suggests >=8192 for cleanup-margin < 0.5 regime; verify with smoke), V_CONCEPTS exact (>=200), M_TRIPLES exact (>=500), K trace depth (research suggests 5), N queries (research suggests 500), seed selection (3), refuse-threshold calibration method (research mandates percentile-based not 0.55*mean), smoke profile (must include full-N preview arm), queue (local_cpu suggested), and anchor name suffix conventions.

Research does NOT specify these numerical parameters. exp_dev SHIPS one cell at a time per Fix #14 (spawn budget <= 3 in-flight).

---

## Word count: ~1080
