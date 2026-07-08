# Pre-reg: NOISY/INFERRED-cue content gating (robustness envelope) v7

- anchor_name: `substrate_gen_lm_contentgate_noisycue_v7_n8192_gpu`
- cell: `experiments/exp_substrate_gen_lm_contentgate_noisycue_v7_n8192_gpu.py`
- date: 2026-07-08
- queue: overnight_queue (GPU); FULL
- extends: `exp_substrate_gen_lm_contentgate_flagdep_v6_n8192_gpu.py` (v6; keeps RAW + RECENCY_GATE content-blind controls + CONTENT_GATE_SCRAMBLED firing control)
- brain-grounding: `notes/research_content_gate_brain_grounding_2026-07-08.md`

## Why (VET 2026-07-08)
v6 executed content-addressed admission and hit CONTENT=1.000, but on a corpus where the FLAG cue gave an EXACT cos=1.0 query-key delta (the predecessor of the true slot IS the pure codebook FLAG vector). That is a HANDED delta: the gate matches a perfect signal rather than INFERRING relevance. v6 tiered MEASURED_MECHANISM ("too easy by construction"; the scramble->chance control proved the lift is real SELECTION, but of a handed cue). VET promotion path (MM -> CG): make the cue NOISY/INFERRED (cos<1, degrading toward the codebook noise floor) so the gate must infer relevance from a graded, noise-corrupted match. If content-selection still beats the 1/(K-1) content-blind cap at a REALISTIC (near-floor) cue-quality, that promotes MM->CG (the real Stage-4 attention-routing test). This is a synthetic-primitive test (top-1 recall discriminator), NOT a language benchmark; bpc reported for continuity only.

## Prior-work check (substrate concept-query, mandatory)
`bash tools/substrate_query.sh "noisy inferred content cue graded query-key attention slot selection robustness envelope"` -> top cosine 0.322 (wordnet `contention`), 0.318 (wordnet/framenet `attention`), 0.295 (`intention`). All lexical wordnet/framenet entities; NONE at cosine>0.30 touch the mechanism (graded/noisy cue robustness envelope over an instance-varying content-slot gate). Consistent with the SUBSTRATE-KNOWS-NOTHING anchor. Direct predecessor = v6 (read end-to-end). **Prior-work check: NONE at cosine>0.30 on the mechanism; genuine novel extension of v6, not a rediscovery.**

## What changes vs v6
The FLAG marker deposited at slot v-1 is no longer the pure codebook vector `cb[FLAG]`. For a cue-quality `q`, the flag slot's CODE is corrupted to `noisy = normalize(q*cb[FLAG] + sqrt(1-q^2)*random_unit)` so `cos(noisy, cb[FLAG]) ~= q` (self-test asserts cos calibration). `q=1.0` reproduces v6's handed delta (top of sweep); `q -> noise_floor(N)=1/sqrt(N)` = the flag is indistinguishable from a random distractor. The SAME noisy per-slot code tensor is built ONCE per batch and shared across all four arms per (K,q), so arms differ ONLY by the admission gate (v6 discipline preserved). The content gate's KEY at slot j is `cos(slot_code_{j-1}, cb[FLAG])` -- at the true slot the match is ~q not 1.0: the gate must INFER.

## Sweep axes
- PRIMARY: cue-quality `q` in `CUE_Q_GRID = [1.0, 0.7, 0.4, 0.25, 0.15, 0.08, 0.04, 0.02, 0.01]` (the robustness envelope; the low tail 0.02/0.01 sits at/below the FULL floor 1/sqrt(8192)=0.011 so the FULL run captures the break-point).
- SECONDARY: window length `K in {6, 10}` (K>=6 per VET: K=4 breaches the 0.50 discrimination guard). Two well-separated caps (0.200, 0.111).
- cue detectability scales as `cue_snr = q*sqrt(N)` (mean-shift q against a 1/sqrt(N) noise floor over K candidate slots) -> the BREAK-POINT is N-invariant in cue_snr. Reported in BOTH cue_snr (primary) and q (secondary).

## Arms (PAIRED: all evaluated on the SAME held-out instances, from the SAME noisy codes, per (seed,K,q))
- `RAW` -- uniform roll-bind bundle. Content-blind; ~1/(K-1); Q-INDEPENDENT (noisy flag is just one more distractor) -> a flat-across-q RAW curve is a built-in sanity check that only CONTENT depends on cue-quality.
- `RECENCY_GATE` -- v6 fixed per-index gate. Content-blind; ~1/(K-1); Q-independent.
- `CONTENT_GATE` -- per-instance query-key gate on the (noisy) codes; must infer relevance from a graded match. THE ARM UNDER TEST.
- `CONTENT_GATE_SCRAMBLED` -- firing control: same relevance spectrum, deranged so the peak lands on a WRONG slot. Must NOT recover.

## Metric
top-1 recall of the correct VALUE at QUERY (argmax over full VOCAB); chance = 1/|V_SUB| = 0.0625. Headline K=6. bpc reported for continuity.

## Bands (pre-registered; headline K=6; realistic point = grid q with cue_snr closest to SNR_TARGET=7)
- **VALID-ONLY-IF** (corpus discriminates): at q=1.0, RAW<=0.35 AND RECENCY<=0.35 (near cap). If either > 0.50 => INCONCLUSIVE (saturation-vacuous inverse). If both < 1.5x chance => INCONCLUSIVE_READOUT_AT_CHANCE.
- **HARD_PASS** (CG-promotion) = at the realistic point (cue_snr~7, genuinely inferred): CONTENT-RECENCY >= 0.30 AND CONTENT >= cap+0.30, AND scramble_sep(q=1.0) >= 0.30, AND CONTENT degrades MONOTONICALLY as q falls, AND CONTENT(q=1.0) >= 0.60. => content-addressed selection survives realistic cue noise (the gate INFERS, not matches a handed delta) -> MM promotes to CG.
- **MIDDLE_BAND** = content-selection real (CONTENT-RECENCY >= 0.15 at some q<1.0 with cue_snr<=20; scramble fires) but does NOT clear the realistic (cue_snr~7) bar -- beats the cap only at higher cue-quality. Noise-fragile inference; the break-point is the finding; stays MM (honest deflation).
- **HARD_FAIL** = CONTENT-RECENCY < 0.15 already at the FIRST noisy point (q=0.7). => content-selection collapses to the cap the moment the cue is anything but exact -> v6 only worked with the handed delta -> stays MM.
- **BREAK-POINT** (KEY ENVELOPE FINDING, reported regardless of tier): the cue_snr (and q) at which CONTENT-RECENCY first falls below 0.15 (content-selection stops beating the cap) as q descends.

## Smoke result (N=1024, seed 7, CPU; SAME code path as FULL, FULL CUE_Q_GRID x K_GRID; cardinality 72=1*4*2*9)
MEASURED@`data/exp_substrate_gen_lm_contentgate_noisycue_v7_n8192_gpu_smoke/metrics.json` (verdict HARD_PASS):
- @K6 (cap=0.200, floor=0.0312): CONTENT_GATE top1 by q = {1.0:1.000, 0.7:1.000, 0.4:1.000, 0.25:1.000, 0.15:1.000, 0.08:0.961, 0.04:0.775, 0.02:0.580, 0.01:0.504}. RAW flat {~0.205-0.229} (raw_span=0.024). RECENCY flat {~0.204-0.248}. SCRAMBLED {~0.06 rising to 0.17 at q<=0.02}.
- @K10 (cap=0.111): CONTENT_GATE {1.0..0.15: 1.000, 0.08:0.919, 0.04:0.611, 0.02:0.359, 0.01:0.251}. RAW/RECENCY flat ~0.08.
- realistic point q=0.25 (cue_snr=8.0): CONTENT=1.000, lift_vs_recency=+0.775, scramble_sep(q=1.0)=+0.935, monotone=True.
- cue calibration MEASURED: cos_true tracks q ({1.0:1.000, 0.7:0.699, 0.4:0.400, 0.25:0.250, 0.15:0.150, 0.08:0.079, 0.04:0.040, 0.02:0.018, 0.01:0.012}).
- content-gate concentration (argmax==true slot) degrades with noise: {q1.0:1.000 ... q0.08:0.981, q0.04:0.806, q0.02:0.589, q0.01:0.546} (K=6).
- self-test PASS: noise calibration, content-gate concentration hi(1.00)->lo(0.38), scramble_off=1.00, discriminator-fires envelope at K=6 small-scale (q1.0 CON=1.00 RAW=0.20 lift+0.80; q0.04 CON=0.47 shrunk).
- BREAK-POINT @smoke: lift_vs_recency stays >= 0.15 across the WHOLE grid (K6 min lift @q0.01 = 0.504-0.246=+0.258; K10 min = 0.251-0.076=+0.175); lift<0.30 first at q=0.01 (cue_snr=0.32, SUB-noise-floor). => content-selection survives to at/below the codebook noise floor; break in cue_snr ~ 0.3.
- NOTE scale: smoke N=1024 (floor 0.031) is the HARDER test (coarser floor); at FULL N=8192 (floor 0.011) the SAME q grid gives higher cue_snr so content-selection is MORE robust -- the knee is witnessed in smoke at the N-invariant cue_snr.

## SCHEMA-VET / META-RULE fields
- cardinality_ok: true. EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(K_GRID)*len(CUE_Q_GRID) = 3*4*2*9 = 216 (FULL). Verdict counts len(per_unit); emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if short. CARD_OK (sweep axes = q x K).
- arms_differ_verified: true (smoke: 4 top1 (K,q)-curves distinct at q=1.0; ARMS-MUST-DIFFER hash gate over all (K,q) points in main()).
- final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace).
- except-ordering: `except SystemExit: raise` before `except Exception` (no BaseException / bare except; grep gates clean).
- crlb_n/a: "top-1 recall on a content-addressed Hebbian readout has no closed-form CRLB; the discriminator is the arm-vs-arm recall GAP whose content-blind floor is the combinatorial 1/(K-1) cap (THEORETICAL). The cue-detectability floor is the codebook noise floor 1/sqrt(N) (THEORETICAL); break-point reported in cue_snr."
- discriminator_reachability: true. HARD_PASS (CONTENT >= cap+0.30 at realistic cue_snr~7) is on the achievable side (smoke CONTENT=1.000 at cue_snr=8.0); content-blind cap 1/(K-1)=0.20 (K=6) is below the realistic-point CONTENT.
- baseline_in_band: true. Content-blind arms in (chance=0.0625, 0.50) at ALL q (smoke RAW ~0.21, RECENCY ~0.23 at K=6; ~0.08 at K=10).
- discriminator survives scale: analytical + smoke. cue_snr=q*sqrt(N) is N-invariant; smoke (N=1024, floor 0.031) is the HARDER test and witnesses the break at the same cue_snr; FULL (floor 0.011) is more robust. Smoke runs the FULL CUE_Q_GRID x K_GRID at the real K. (Rules A + B + C satisfied.)
- HP_SCOPE: {CONTENT_GATE: [lift_vs_recency>=0.30 @ realistic cue_snr~7, CONTENT>=cap+0.30, scramble_sep(q=1.0)>=0.30, monotone, CONTENT(q=1.0)>=0.60]}. RAW/RECENCY = content-blind controls (VALID-ONLY-IF cap gate, flat-across-q sanity; NOT HARD_PASS gated). CONTENT_GATE_SCRAMBLED = firing control (must NOT pass).
- calibration_check: default_ok_for_this_regime. GATE_TAU=0.05 FIXED and Q-AGNOSTIC -- the gate does NOT know q; a fixed temperature is the honest inferred test (adapting tau to q would leak the answer). content-gate concentration self-test + per-q content_gate_conc diagnostic are the gate-health gates. RECENCY_TAU=0.1 (v6 value).
- multi_seed_smoke: N/A -- top-1 recall is deterministic accuracy (capacity-sweep exemption of META_RULE_smoke_single_seed_inflates_AUC), not a continuous AUC/ECE score; FULL runs 3 seeds regardless (n_seeds propagation verified: SEEDS=[7,17,23], resumable_seeds iterates all, write_partial per seed, aggregate_partials over SEEDS -- cardinality gate 216 enforces all 3 seeds x all units landed).

## Defensive error-checking (section 13)
- cell_chunked: false (single-file multi-seed; per-seed checkpoint via write_partial/aggregate_partials; run_seed ~seconds/seed so runner-death loses at most one cheap seed; resumable).
- start_marker_written: true (_start_marker.json at main() entry).
- crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback, atomic).
- heartbeat_present: true (emit_heartbeat per unit, 216 units).
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: line_buffered_stdout (sys.stdout.reconfigure(line_buffering=True) at cell start; per-(K,q) print each < 60s; timeout_s=3600 >= 1800 so field required).
- run_mode_verification: FULL landed metrics must show run_mode=full (cell defaults RUN_MODE via HDLAB_RUN_MODE or --smoke; queue dispatches FULL with no --smoke => full). Orchestrator verifies post-ship.

## Section 15 gates (composition / sweep)
- sweep_alignment_verdict: ALIGNED. Swept params = q (cue-quality) x K. effective_params_per_primitive: content_gate's true-slot key match = q (the swept cue-quality is exactly what the gate experiences -- confirmed by cos_true tracking q in smoke); content-blind cap = 1/(K-1). No nominal-vs-effective mismatch.
- bracket_includes_discriminating_band / discriminating_fraction: the q-axis is designed to WALK the discriminator from saturated (CONTENT=1.0, q>=0.15) through the knee (q in {0.08,0.04,0.02,0.01}) to near-cap -- the envelope IS the finding, so >=4/9 q-points land in the transition band [cap, 1.0). Smoke measured CONTENT @K6 crossing 1.000->0.504 across the low tail. discriminating_fraction (transition points) ~ 0.5.
- composition_edges: content_gate(query-key softmax over noisy codes) -> enc_gate_codes(roll-bind bundle) -> Hebbian readout. SHAPE_MATCH at each edge (gate (B,K) admission consumed by enc_gate_codes; bundle (B,N) consumed by mean-outer readout). No SHAPE_MISMATCH.
- positive_control_arms: RECENCY_GATE reproduces v6's fixed-index gate (content-blind -> cap). CONTENT_GATE at q=1.0 reproduces v6's handed result (CONTENT=1.000 in smoke) AT THIS regime = the positive control for the primitive; the noisy tail is the new probe. regime_extension_audit: v6 exact-cue -> v7 graded/noisy-cue; SHAPE_DRIFT documented (that is the point).
- functional_requirements: (1) INFER the relevant slot from a graded/noisy content cue -> CONTENT_GATE query-key softmax on noisy codes; (2) degrade the cue toward the noise floor -> build_slot_codes(cue_q) with cos-calibrated corruption; (3) map the robustness envelope + break-point -> CUE_Q_GRID sweep + cue_snr reporting; (4) isolate genuine content-match from peaked-admission variance-reduction -> CONTENT_GATE_SCRAMBLED derangement control; (5) prove content-blind ceiling Q-independent -> RAW + RECENCY_GATE flat-across-q + analytic 1/(K-1) cap.

## Compute architecture
batched-GPU. Per (seed,K,q): one train pass + one eval pass over BATCH=256 windows; per batch the noisy per-slot code tensor (B,K,N) is built ONCE and all four arms derived from it (shared codes => arms differ only by gate; avoids 4x recompute). Readout = mean-outer Hebbian (N x N) batched accumulation, one W per arm (4 x 268 MB at N=8192 = ~1.1 GB held during a train pass). content gate = per-instance query-key cosine + softmax (batched). No sequential dependency. Storage: no_storage / no_composition (single-hop content-addressed readout). Peak GPU est < 2 GB at N=8192.

## Config
- FULL: N=8192, SEEDS=[7,17,23], K_GRID=[6,10], headline K=6, CUE_Q_GRID=[1.0,0.7,0.4,0.25,0.15,0.08,0.04,0.02,0.01], M_TRAIN=8000, M_EVAL=2000, M_GATE=2000, BATCH=256, GATE_TAU=0.05, RECENCY_TAU=0.1, SNR_TARGET=7.0, V_SUB=16, FLAG=69.
- timeout_s: 3600 (smoke seed 5s CPU at N=1024 x9 q; FULL on GPU 3 seeds N=8192 x 2 K x 9 q = 216 units, est 5-15 min incl. GPU warmup; 3600 gives generous headroom).

## Number provenance (META_RULE_AC)
- content-blind cap 1/(K-1): THEORETICAL@combinatorial (guess among K-1 present candidates).
- chance 1/16=0.0625: THEORETICAL@|V_SUB|=16.
- codebook noise floor 1/sqrt(N): THEORETICAL@random-code cosine std.
- all smoke arm/curve/concentration/calibration values: MEASURED@`data/exp_substrate_gen_lm_contentgate_noisycue_v7_n8192_gpu_smoke/metrics.json`.
- FULL arm values: HYPOTHESIZED (not yet run); expected CONTENT_GATE holds across the realistic range (break in cue_snr ~ 0.3, likely below the FULL grid min q=0.01 => cue_snr=0.9) with RAW/RECENCY flat at cap.
