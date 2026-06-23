# exp_dev hand-off — research: 5x DEEPER high-noise substrate-product strategy (refuse-aware confluence)

**Filed:** 2026-06-23 by Research (Opus 4.7).

**Trigger:** Shannon-floor META (rows 675-678) chain-grade-eligible across encoder type / M / N_DIM. Decoder-side mechanism families exhausted (4 families HARD_FAIL). Encoder-side drill orthogonal (parallel handoff). This drill closes the question: substrate-product posture at high noise is REFUSE-AWARE GRACEFUL DEGRADATION via already-shipped `hdlab/refuse_gate.py` + `hdlab/conformal.py` primitives. Cheap ~30-min CPU cell pre-registered; HARD-PASS would elevate "envelope OR refuse; never confidently-wrong" to chain-grade-eligible META. Composes with KF1 refuse_gate_audit cert evidence + 7-field lit base.

**Source research note:** `notes/research_5x_deeper_high_noise_substrate_product_strategy_2026-06-23.md`.

**Pause state:** check `data/orchestrator_paused.flag` before dispatching; this handoff is gated like all exp_dev dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: exact seed counts, batch sizes, smoke profile, FULL profile, anchor name, ETA, queue choice. Research has pre-registered HARD-PASS / HARD-FAIL thresholds inside the source note; exp_dev binds those into the cell.

---

## Anchor candidates (rank-ordered, with anchor pointer + substrate-product reading + tier hint + why-now)

### Anchor 1 (TOP — primary): `prod_regime_refuse_envelope_v1` (substrate-as-refuse-aware confluence test)

- **Anchor pointer:** source-note section "Primary cell: `prod_regime_refuse_envelope_v1`"; pre-registered ARMS = {ARM_BASE_ARGMAX, ARM_REFUSE_GATED, ARM_CONFORMAL_SET}; sigmas = `[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]`; M=200, N_DIM=2048, n_seeds=5; substrate-only-decode-gate=TRUE; zero LLM calls.
- **Substrate-product reading:** if HARD-PASS, the META "Shannon-floor exists AND substrate refuses calibrated-honestly outside envelope" goes chain-grade-eligible — substrate becomes the safety-wedge against LLM confident-hallucination at high noise. If HARD-FAIL, refuse-aware framing closes; substrate must descope to envelope-only operation (sigma<=1.0 hard limit) with no refuse-aware fallback.
- **Tier:** local_cpu_queue (numpy matmul only; ~30 min CPU; no GPU needed; no encoder upgrade needed — uses random bipolar codebook at N=2048 matching META row 675).
- **Why now:** Shannon-floor parent META chain-grade-eligible TODAY; the question "what to do about it" needs answering same-cycle per `feedback_results_to_application_cadence_same_cycle_atomize_and_hdlab_update_USER_2026-06-22.md`. Decoder + encoder mechanism families exhausted; refuse-aware is the structurally-right substrate-product move per L1-L5 synthesis. Substrate primitives ALREADY shipped (`hdlab/refuse_gate.py` + `hdlab/conformal.py` Read-verified 2026-06-23) — this is composition not novel construction. Cheap (~30 min CPU) and decisive.

### Anchor 2 (secondary, composes inside envelope): `kinetic_proofreading_2step_gate_v1`

- **Anchor pointer:** source-note section "Kinetic proofreading (Hopfield 1974)" — substrate-native 2-step substrate check; query substrate twice with independence-perturbation; accept iff both return same atom. Predicts error rate squared inside envelope.
- **Substrate-product reading:** lifts silent-error-rate inside envelope at ~2x compute cost. NOT a Shannon-floor-break; a tightening inside the calibrated envelope. Composes WITH ARM_REFUSE_GATED, not as alternative.
- **Tier:** local_cpu_queue (cheap; ~15 min CPU).
- **Why now:** independent cross-check on Anchor 1; if Anchor 1 HARD-PASSES, this anchor stacks; if Anchor 1 MIDDLE_BAND, this anchor's lift may tip into HARD_PASS. **Dispatch ONLY after Anchor 1 verdict** per cheapest-first-cross-cell-orthogonality discipline.

### Anchor 3 (open follow-up if Anchor 1 HARD_PASS): `mondrian_stratified_refuse_v1`

- **Anchor pointer:** source-note section "Next-drill candidate (per Trigger C adjacency-cascade)"; per-noise-stratum tau via Mondrian conformal. Tightens coverage; adjacency anchor = `coding-theory` field per advisor.
- **Substrate-product reading:** if substrate confidence calibration is sigma-band-dependent, per-band tau gives tighter coverage and higher accept-rate at low noise without sacrificing refuse-rate at high noise.
- **Tier:** local_cpu_queue (~30 min CPU).
- **Why now:** queued only after Anchor 1 HARD_PASS verdict; cheap follow-up; advances coding-theory adjacent field.

### Anchor 4 (open follow-up if Anchor 1 HARD_FAIL — open mechanism path): `ldpc_substrate_codebook_v1`

- **Anchor pointer:** source-note section "L2 table" row 5 (LDPC) + "Next-drill candidate (HARD_FAIL branch)". Substrate codebook with parity-check structure; iterative belief-propagation decoder; capacity-approaching at known noise channel.
- **Substrate-product reading:** capacity-approaching ECC inside the substrate codebook itself — this redesigns the encoder side toward an explicit ECC code, capacity-approaching at known channel. Novel-synthesis P_deflated=0.20 (capped).
- **Tier:** likely overnight_queue or remote_cpu (~1 week novel-synthesis + theory work).
- **Why now:** queued only if Anchor 1 HARD_FAIL; this is the open mechanism path noted in source-note L1 #5. Do NOT dispatch unless refuse-aware closes — keep substrate-effort focused on cheap-confluence FIRST.

### Stretch (already-banked future composition): `hdlab/noise_envelope.py` primitive ship

- **Anchor pointer:** source-note section "What to ship to hdlab/ if HARD-PASS". Composed primitive `query(cue, mode='argmax_with_refuse'|'conformal_set', tau, q)` wrapping the two existing primitives + envelope-disclosure response shape.
- **Substrate-product reading:** hdlab/ primitive update SAME CYCLE as Anchor 1 HARD_PASS per `feedback_results_to_application_cadence_same_cycle_atomize_and_hdlab_update_USER_2026-06-22.md`.
- **Tier:** local (Python wrapper; ~30 min implementation).
- **Why now:** ship only after Anchor 1 HARD_PASS; not a cell, a primitive add.

---

## Context pointers (file paths, not summaries)

- `notes/research_5x_deeper_high_noise_substrate_product_strategy_2026-06-23.md` — source research note; full L1-L5 synthesis + 7 citations + pre-reg bands.
- `notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md` — parallel orthogonal drill; option (a) encoder upgrade; do NOT subsume.
- `notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md` — parent rejection; decoder-side 4 families closed.
- `data/exp_cleanup_floor_learned_encoder_v1/metrics.json` — META branch #3 anchor (chain-grade-eligible).
- `data/exp_cleanup_floor_M_scan_v1/metrics.json` — META branch #2.
- `data/exp_cleanup_floor_N_DIM_scan_v1/metrics.json` — META branch #3 (N).
- `hdlab/refuse_gate.py` — load-bearing primitive (CERT 584/585 evidence base; n8 / U1 production).
- `hdlab/conformal.py` — load-bearing primitive (split-conformal coverage guarantee).
- `notes/research_substrate_NEGATIVES_2x_negative_was_positive_3x_scour_USER_DIRECTIVE_2026-06-20.md` — KF1 refuse_gate cert atom evidence.
- `notes/substrate_capability_map.md` — current cap_map; refuse_gate_audit domain has 2 cert atoms.

---

## Contract

- Pre-reg per source note (HARD_PASS / HARD_FAIL / MIDDLE_BAND bands ALREADY defined) — bind verbatim; do not re-derive.
- Self-test per [[feedback-formula-selftests]] — sigma=0.0 ARM_BASE_ARGMAX must reach recall@1=1.000; ARM_REFUSE_GATED accept_rate at sigma=0.0 must be >=0.95.
- Multi-seed FULL on smoke clearance; smoke = 1 seed at 3 sigmas; FULL = 5 seeds at 9 sigmas.
- Queue routing: local_cpu_queue for Anchor 1 + 2 + 3 (numpy-only; no GPU needed); overnight_queue for Anchor 4 only if HARD_FAIL branch fires.
- Ship via `bash tools/orchestrator/queue_add.sh local_cpu_queue prod_regime_refuse_envelope_v1 <script> <prereg> <timeout>`.
- Post-ship REMOTE VERIFY (where applicable; local-only for Anchor 1).
- Per [[feedback-fix26-predispatch-verify-the-referent-gate]]: run `tools/predispatch_check.py prod_regime_refuse_envelope_v1` BEFORE spawning the cell-author — check `data/recent_landings.jsonl` + `data/substrate_index/atoms.jsonl` for prior evidence; refuse-aware substrate has 2 prior cert atoms (KF1 domain), check whether this exact cell name already ran.
- Per [[feedback-substrate-mine-capacity-before-extrapolating-2026-06-22]]: scour Store FIRST for any prior `refuse_envelope_*` cells before assuming this is novel. Confidence-calibration evidence may already exist somewhere; if it does, this cell is a delta-test not a foundational measurement.

---

## Autonomy declaration

Research has set: anchor topic + ARMS list + sigma sweep + HARD-PASS/HARD-FAIL/MIDDLE_BAND bands + sanity self-tests + decisive metrics (silent_error_rate, ood_refuse_rate, recall@1_accepted, confidence_calibration, accept_rate, prediction-set size). exp_dev decides: exact seed values (research suggests 5 seeds), exact dispatch script path/name, smoke-vs-full split, runtime estimate, atomization framing on PASS, integration with downstream cells. Cell-author may add additional control ARMs but MUST preserve the 3 pre-registered ARMS as-is for verdict comparability.

Per [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]]: cert classification must read per-ARM `metrics.json` not the `verdict_msg` framing. Each ARM's HARD-PASS is independent of the others; partial pass on ARM_REFUSE_GATED alone is sufficient for "substrate-as-refuse-aware" META eligibility — ARM_CONFORMAL_SET is corroboration, ARM_BASE_ARGMAX is null-baseline.

Per [[feedback-empowered-to-experiment-where-lit-says-dismissed]]: stochastic resonance and ensemble sqrt(N) are LIT-DISMISSED for single-shot inference; substrate-native variants ARE NOT this drill's focus (closed in L2) but if exp_dev sees a substrate-native rephrase that survives the L2 filter, dispatch is encouraged as a parallel ARM.
