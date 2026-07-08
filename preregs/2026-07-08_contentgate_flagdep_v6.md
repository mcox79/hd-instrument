# Pre-reg: CONTENT-dependent context gating (flagged-dependency corpus) v6

- anchor_name: `substrate_gen_lm_contentgate_flagdep_v6_n8192_gpu`
- cell: `experiments/exp_substrate_gen_lm_contentgate_flagdep_v6_n8192_gpu.py`
- date: 2026-07-08
- queue: overnight_queue (GPU); FULL
- extends: `exp_substrate_gen_lm_contextgate_depth_v5_n8192_gpu.py` (commit 4692cd9cc; keeps RAW + RECENCY_GATE as content-blind controls)
- brain-grounding: `notes/research_content_gate_brain_grounding_2026-07-08.md`

## Prior-work check (substrate concept-query, mandatory)
`bash tools/substrate_query.sh "content-dependent context gating query-key attention over temporal memory slots instance-varying relevant slot"` -> top cosine 0.335 (wordnet entity `content`), 0.307 (git-internals temporal-versioning note), 0.301 (NL slot-filling ATIS). NONE above 0.30 touch the mechanism (per-instance content-match gating over temporal slots). Grep of `exp_wave14_moe_attention_routing_v1` confirms it does soft attention over STATIC expert-prototype keys (MoE routing), not a per-instance content-match over a scrolling K-slot temporal window with an instance-varying relevant slot. `exp_pfc_gate_*`, `exp_cortex_attention_binding_router_*`, `exp_query_margin_gate_smoke_v1`, `exp_substrate_working_memory_multi_bank_routing_v1` do not test instance-varying content-slot gating. **Prior-work check: NONE at cosine>0.30 on the mechanism; genuine gap, not a rediscovery.**

## Hypothesis
v5's recency gate is index-selection (fixed per-slot weight); it is guaranteed to fail when the informative slot's POSITION varies per instance. A per-instance content-match (query-key) gate `g_j = softmax(cos(cb[FLAG], cb[tok_at_slot_{j-1}])/tau)` (biased-competition / Hopfield==attention, Ramsauer 2020) selects the relevant slot by CONTENT and should exceed the content-blind cap.

## Corpus (regime where recency provably fails)
Variable-lag flagged-dependency instances over VOCAB=70. FLAG=id 69; VALUE sub-vocab V_SUB={0..15} (16 tokens). Each instance = a K-slot window: slot v-1 = FLAG, slot v = target VALUE, v ~ uniform {1..K-1} (target POSITION uniform => zero positional info). The K-1 NON-FLAG slots hold DISTINCT V_SUB distractors (incl. slot v), so every candidate looks like a valid VALUE and a content-blind readout is combinatorially capped at 1/(K-1). chance = 1/|V_SUB| = 0.0625.

## Arms (PAIRED: all arms evaluated on the SAME held-out instances per seed)
- `RAW` -- uniform roll-bind bundle (v5 enc_raw). Content-blind control. Expected ~1/(K-1).
- `RECENCY_GATE` -- v5 fixed per-index gate (per-slot next-token predictiveness, applied identically to every instance). Content-blind control. Expected ~1/(K-1) (per-slot predictiveness ~equal since target position uniform).
- `CONTENT_GATE` -- NEW per-instance query-key gate (query=FLAG code, keys=per-slot predecessor codes). Mechanism arm.
- `CONTENT_GATE_SCRAMBLED` -- firing control: same relevance spectrum, deranged so the peak lands on a WRONG slot. Must NOT recover.

## Metric
top-1 recall of the correct VALUE at QUERY positions (argmax over full VOCAB); bpc reported for continuity. Headline at K=6 (research analytic example: 1/(K-1)=0.20).

## Bands (pre-registered; evaluated at headline K=6)
- **VALID-ONLY-IF** (discriminator fires / corpus discriminates): RAW <= 0.35 AND RECENCY_GATE <= 0.35 (both near cap). If either > 0.50 => INCONCLUSIVE (saturation-vacuous inverse: readout solves task without content-selection). If both near chance (<1.5x) => INCONCLUSIVE_READOUT_AT_CHANCE.
- **HARD_PASS** = CONTENT_GATE >= 0.70 AND RECENCY_GATE <= 0.30 AND (CONTENT_GATE - CONTENT_GATE_SCRAMBLED) >= 0.30.
- **MIDDLE_BAND** = (CONTENT_GATE - RECENCY_GATE) >= 0.15 but no full HARD_PASS, OR scramble separation in (0, 0.30).
- **HARD_FAIL** = (CONTENT_GATE - RECENCY_GATE) < 0.15 OR CONTENT_GATE_SCRAMBLED matches CONTENT_GATE.

## Smoke result (N=1024, seed 7, CPU; same code path as FULL, FULL K_GRID)
MEASURED@`data/exp_substrate_gen_lm_contentgate_flagdep_v6_n8192_gpu_smoke/metrics.json` (verdict HARD_PASS):
- @K6: RAW=0.244, RECENCY_GATE=0.232, CONTENT_GATE=1.000, SCRAMBLE=0.063; lift_vs_recency=+0.768, scramble_sep=+0.937.
- content-blind caps track 1/(K-1): RAW {K4:0.476, K6:0.244, K8:0.151} vs cap {0.333, 0.200, 0.143}; CONTENT_GATE {1.0,1.0,1.0}.
- self-test: content gate concentrates on FLAGGED slot (conc=1.00, g=1.00); scramble moves off (1.00); discriminator fires at K=5 small-scale (RAW=0.34, CONT=1.00, SCR=0.05).
- NOTE K=4: RAW=0.476 approaches the 0.50 INCONCLUSIVE guard at smoke N=1024 (finite near-orthogonality); headline is K=6 where content-blind arms are cleanly capped. At FULL N=8192 near-orthogonality improves so content-blind arms sit closer to the analytic cap.

## SCHEMA-VET / META-RULE fields
- cardinality_ok: true. EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(K_GRID) = 3*4*3 = 36 (FULL). Verdict counts len(per_unit); emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if short. CARD_OK (sweep axis = K).
- arms_differ_verified: true (smoke: 4 top1 K-curves distinct; ARMS-MUST-DIFFER hash gate in main()).
- final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace).
- except-ordering: `except SystemExit: raise` before `except Exception` (no BaseException / bare except; grep gates clean).
- crlb_n/a: "top-1 recall on a content-addressed Hebbian readout has no closed-form CRLB at this regime; the discriminator is the arm-vs-arm recall GAP whose content-blind floor is the combinatorial 1/(K-1) cap (THEORETICAL, closed-form). RAW/RECENCY must land near it; CONTENT_GATE must exceed 0.70."
- discriminator_reachability: true. HARD_PASS threshold 0.70 for CONTENT_GATE is on the achievable side (smoke=1.000); content-blind cap 1/(K-1)=0.20 at K=6 is below the RECENCY<=0.30 gate.
- baseline_in_band: true. Content-blind arms in (chance=0.0625, 0.50); smoke RAW=0.244, RECENCY=0.232 at K=6.
- discriminator survives scale: analytical -- 1/(K-1) cap is combinatorial (dimension-independent); codebook near-orthogonality IMPROVES with N (1024->8192), so a gap that fires at smoke fires at FULL. Smoke additionally runs the FULL K_GRID at the real K. (Rule A + B satisfied.)
- HP_SCOPE: {CONTENT_GATE: [recall>=0.70, RECENCY<=0.30, scramble_sep>=0.30]}. RAW/RECENCY_GATE = content-blind controls (VALID-ONLY-IF cap gate, NOT HARD_PASS gated). CONTENT_GATE_SCRAMBLED = firing control (must NOT pass).
- calibration_check: default_ok_for_this_regime. GATE_TAU=0.05 (sharp query-key admission; content-gate concentration self-test conc=1.00 is the gate-health gate); RECENCY_TAU=0.1 (v5 value).
- multi_seed_smoke: N/A -- top-1 recall is a deterministic accuracy (per capacity-sweep exemption of META_RULE_smoke_single_seed_inflates_AUC), not a continuous AUC/ECE score; FULL runs 3 seeds regardless.

## Defensive error-checking (section 13)
- cell_chunked: false (single-file multi-seed; per-seed checkpoint via write_partial/aggregate_partials; run_seed is ~seconds/seed so runner-death loses at most one cheap seed).
- start_marker_written: true (_start_marker.json at main() entry).
- crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback, atomic).
- heartbeat_present: true (emit_heartbeat per unit).
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: line_buffered_stdout (sys.stdout.reconfigure(line_buffering=True) at cell start; per-unit print each < 60s; timeout_s=2400 >= 1800 so field required).

## Section 15 gates (composition / sweep)
- sweep_alignment_verdict: ALIGNED. Swept param = K. effective_params_per_primitive: content_gate sees K slots -> content-blind cap = 1/(K-1) (varies with K as intended); the discriminating gap widens with K. No nominal-vs-effective mismatch.
- bracket_includes_discriminating_band / discriminating_fraction: 1.0. Predicted content-blind top1 per K: {K4:0.33, K6:0.20, K8:0.14}; CONTENT_GATE ~1.0. The discriminator (content-vs-blind gap) is large at all 3 K (>0.6) => 3/3 points discriminate.
- composition_edges: content_gate(query-key softmax) -> enc_gate_win(roll-bind bundle) -> Hebbian readout. SHAPE_MATCH at each edge (gate outputs (B,K) admission weights consumed directly by enc_gate_win; bundle (B,N) consumed by mean-outer readout). No SHAPE_MISMATCH.
- positive_control_arms: RECENCY_GATE reproduces v5's fixed-index gate mechanism AT THIS regime (content-blind by construction -> lands at cap, as expected). CONTENT_GATE is a NEW per-instance primitive (no prior chain-grade atom to reproduce); its control is the THEORETICAL 1/(K-1) cap + the CONTENT_GATE_SCRAMBLED firing control. regime_extension_audit: v5 was 1st-order-Markov stream (fixed relevant slot); this is variable-lag flagged corpus (instance-varying relevant slot) -- SHAPE_DRIFT documented (that is the point of the cell).
- functional_requirements: (1) select the relevant past slot by content -> CONTENT_GATE query-key admission; (2) prove position carries zero info -> uniform-v corpus construction; (3) isolate genuine content-match from any peaked admission -> CONTENT_GATE_SCRAMBLED derangement control; (4) prove content-blind ceiling -> RAW + RECENCY_GATE controls + analytic 1/(K-1) cap.

## Compute architecture
batched-GPU. Encoders = elementwise-scaled roll-bind bundles batched over BATCH=256 windows; readout = mean-outer Hebbian (N x N) batched accumulation; content gate = per-instance query-key cosine + softmax (batched). No sequential dependency. Storage: no_storage / no_composition (single-hop content-addressed readout). Peak GPU est < 1.5 GB at N=8192 (W = 268 MB; sequential recency-gate Wj with del).

## Config
- FULL: N=8192, SEEDS=[7,17,23], K_GRID=[4,6,8], headline K=6, M_TRAIN=8000, M_EVAL=2000, M_GATE=2000, BATCH=256, GATE_TAU=0.05, RECENCY_TAU=0.1, V_SUB=16, FLAG=69.
- timeout_s: 2400 (smoke run_seed 2s CPU at N=1024; FULL on GPU 3 seeds N=8192 est few min; 2400 gives generous headroom incl. GPU warmup).

## Number provenance (META_RULE_AC)
- content-blind cap 1/(K-1): THEORETICAL@combinatorial (guess among K-1 present candidates).
- chance 1/16=0.0625: THEORETICAL@|V_SUB|=16.
- all smoke arm values: MEASURED@`data/exp_substrate_gen_lm_contentgate_flagdep_v6_n8192_gpu_smoke/metrics.json`.
- FULL arm values: HYPOTHESIZED (not yet run); expected CONTENT_GATE>=0.70, RECENCY/RAW near cap.
