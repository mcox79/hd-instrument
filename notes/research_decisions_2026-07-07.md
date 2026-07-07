
- 2026-07-07T17:28:27Z research: 2x negative-revival on resonator self-margin HARD-FAIL -> notes/research_resonator_basin_proliferation_self_predictability_2026-07-07.md. Mechanism CONFIRMED (convergence-basin/spurious-joint-fixed-point proliferation, cross-validated 3 independent lit-scans + substrate's own 2026-05-19 history, same Frady-Sommer/Karunaratne-Langenegger paper family). Self-predictability: NO ready closed form this cycle (P_deflated=0.65 negative finding), but this is an effort/scoping boundary not a fundamental one (unlike row 8b) -- own z_init=16.8 derivation verified to <1%, combinatorial-count check honestly HARD-FAILs by ~10x (informative, localizes the real derivation gap). No 4th CG_META family minted. Concrete near-term actionable: apply substrate's own validated ACF rescue (cap_map row 51, codebook-size axis) to the untested factor-count axis (this cell) -- template experiments/exp_wave14b_acf_resonator.py.

- 2026-07-07 (brain-component-driven-development, next-arc audit): re-ranked all 5 missing/weak brain-component
  candidates (thalamus, cerebellum x2 targets, basal-ganglia, neuromodulation, CLS-consolidation, cortical
  microcircuit) for a PROVEN CONSUMER post-thalamic-router-shelving. 4/6 confirmed still consumer-less
  (thalamus pre-shelved; CLS tied to deferred general-knowledge ingest; neuromodulation-as-encoder-gain-knob
  is my own unevidenced hypothesis; cortical-microcircuit 2x narrow HARD_FAIL banked) -- unchanged from the
  07-06 backup's own conclusion, no new evidence today. 1 cerebellum target (autonomous-decomposition waypoint
  chain) is NOW CLOSED (`exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1` FULL HARD_FAIL, DELTA=0.004).
  TOP PICK: cerebellum-class SR-rollout anticipatory-bias mechanism for the OTHER target -- the already-BUILT,
  already-HARD_PASS-at-d4 PFC-BG gate's (`exp_pfc_gate_cfrpe_trained_v2`) own measured depth-degradation
  (gonogo_lift 0.653->0.075, d4->d6). Prior lever (multi-gamma/branching, smoke-only) found NOT the driver;
  2 fresh external lit-scans independently confirm gamma-only is an established-insufficient fix class in the
  literature, and find the specific anticipatory-forward-model-for-gating-horizon combination has NO direct
  precedent (novel synthesis, P capped). Full cell spec (3-arm smoke, CPU, reuses on-disk SR machinery) in
  notes/research_brain_component_consumer_ranking_cerebellum_control_depth_2026-07-07.md.

- 2026-07-07 (2x drill, converging negative -- noise-compounding bound across 3 cells): resonator K-way
  basin proliferation, autonomous waypoint HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL, cerebellar SR-rollout
  (recovered_frac=-1.40) all show recurrent/multi-step decode underperforming single-step. VERDICT: CONTRABLE,
  not fundamental -- TWO distinct sub-mechanisms, neither shared by reasoning-depth's survival. Class A (no
  external reset mid-iteration, resonator): fully deterministic zero-T coupled search, no randomization axis
  exists in the code today (confirmed by source re-read). Class B (self-referential correction, waypoint +
  cerebellar rollout): fresh on-disk re-read finds `retry_rate_combo=0.0`/`fallback_rate_combo=0.0` at the
  deepest FULL-tested waypoint regime -- the verify-gate NEVER triggered, proving it checked the pick against
  the SAME noisy R matrix that produced it (decision-feedback-equalizer-style correlated error, not
  regenerative-repeater-style independent reset) -- explains why a well-precedented rescue still landed
  DELTA=0.004. Reasoning-depth survives because each hop is a hard argmax decode against a FIXED EXTERNAL
  codebook (regenerative-digital-repeater property, zero residual noise on success, i.i.d per-hop failure,
  composes as p^D). TOP candidate: finite-temperature Glauber relaxation + redundant-restart plurality vote on
  the resonator K4 case -- converges independently with field advisor's own #2-ranked D1 candidate. Full note:
  notes/research_noise_compounding_bound_deep_mechanism_2026-07-07.md. P_deflated=0.50 (mechanism diagnosis,
  capped) / 0.28 (rescue clears MIDDLE) / 0.20 (rescue clears HARD-PASS).

- 2026-07-07 (forward-derivation, 970K scale-test forecast): classified the encoder's two readouts
  by decode regime per the self-margin taxonomy -- discrete SBC block-argmax algebra (K=128 x L=32)
  = disjoint-block/collision-count (holds at 970K, combinatorial margin ~180 orders of magnitude,
  P_deflated~0.60-0.65 HARD-PASS); continuous dense retrieval (`ret_agree10`) = order-statistic/
  distance-concentration (ALREADY failing at 0.18-0.27 at 18% of scale, forecast to degrade further
  with NO cliff, P_deflated~0.05 HARD-PASS at 970K on plain SBC). GSBC graded-code lever already
  measures 1.5-3x better at the SAME 177,899 scale (0.31-0.68) but its own density-dial retune is
  unverified past ~160K and is the one place a genuine Donoho-Tanner-class sharp cliff is plausible
  (P_deflated~0.30-0.35, capped, HARD-PASS at 970K IF retuned). Cheapest next action: CPU-only
  near-duplicate density measurement in the real `entities.jsonl` (Test 0), before any GPU scale-test
  dispatch. Full note: notes/research_encoder_970k_marchenko_pastur_codebook_collision_forecast_2026-07-07.md.
  3 parallel Sonnet lit-scans, 33 verified external sources, zero substrate-novel terms sent externally.
