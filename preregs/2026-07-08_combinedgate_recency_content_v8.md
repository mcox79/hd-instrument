# Pre-reg: COMBINED recency+content arbitration gate v8 (attention-routing capstone)

- anchor_name: `substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu`
- cell: `experiments/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py`
- date: 2026-07-08
- queue: overnight_queue (GPU); FULL
- extends: recency-gate v5 (`exp_substrate_gen_lm_contextgate_depth_v5_n8192_gpu.py`, MEASURED_MECHANISM) + content-gate v7 (`exp_substrate_gen_lm_contentgate_noisycue_v7_n8192_gpu.py`, CHAIN_GRADE noisy-cue). Both HALVES of selective admission proven SEPARATELY; this is the ARBITRATION capstone.
- brain-grounding: `notes/research_content_gate_brain_grounding_2026-07-08.md`

## Why (capstone of the attention-routing arc)
recency-gate v5 (MM) selects the most-recent slot and flattens noise-compounding; content-gate v7 (CG) INFERS relevance from a noise-floor cue (cue_snr~1.8) and routes to a FLAG-cued slot. Selective admission is proven in each half in isolation. The capstone: a SINGLE gate that ARBITRATES recency AND content when BOTH signals are present -- use content when a reliable cue exists, fall back to recency when it does not. Brain-ground: biased-competition (Desimone & Duncan 1995; Reynolds & Heeger 2009 normalization) combines multiple top-down biases through a shared normalization pool -- a strong sharp bias suppresses a weak/flat one WITHOUT a hand-set switch; PBWM (Frank/O'Reilly) arbitrates gating by value. The COMBINED gate = graded competition between a recency-prior (fixed top-down bias, in logit units) and a content-cue bias (scaled query-key match), arbitrated by softmax over their SUM. This is a synthetic-primitive test (top-1 recall discriminator), NOT a language benchmark.

## Prior-work check (substrate concept-query, mandatory)
`bash tools/substrate_query.sh "combined recency content gate arbitration attention routing biased competition"` -> top cosine 0.419 (wordnet `contention`), 0.389 (note `Coordination / contention`), 0.378 (wordnet/framenet `attention`), 0.372 (`combination`). All lexical wordnet/framenet/coordination entities; NONE at cosine>0.30 touch the MECHANISM (an instance-varying gate that arbitrates a recency prior against a content-cue bias). Consistent with SUBSTRATE-KNOWS-NOTHING. Direct predecessors v5 + v7 read end-to-end. **Prior-work check: NONE at cosine>0.30 on the mechanism; genuine novel synthesis (arbitration) of the two proven half-gates, not a rediscovery.**

## Corpus (the arbitration test)
Each instance carries BOTH a recency signal and a content signal. Three types, mixed ~1/3 each per (seed,K,q):
- ALIGNED (0): FLAG at slot K-2, VALUE(target) at slot K-1 (== most-recent slot). recency slot == content slot; both single gates AND combined correct (control: signals agree).
- CONFLICT (1): FLAG at slot v-1, VALUE(target) at slot v in {1..K-2} (NOT most-recent); slot K-1 holds a DISTRACTOR. CONTENT is ground-truth. A pure-recency gate picks slot K-1 -> WRONG. A content gate picks slot v -> RIGHT. (Recency FAILS here.)
- CUE_ABSENT (2): NO flag anywhere; VALUE(target) at slot K-1 (== most-recent). Content query-key match is flat noise (~1/sqrt(N)) -> a pure-content gate mis-selects -> WRONG. A recency gate picks the most-recent slot -> RIGHT. (Content FAILS here.)
FLAG-present instances carry a NOISY cue (cos(noisy_flag, cb[FLAG]) ~= q, v7-style) so the content half must INFER, not match a handed delta.

## Arms (PAIRED: all evaluated on the SAME held-out instances, from the SAME noisy codes, per (seed,K,q); arms differ ONLY by the gate)
- `RAW` -- uniform gate (equal-weight superposition of all K slot codes). Content+recency-blind; capped ~1/(present value candidates).
- `RECENCY_ONLY` -- v5-style LEARNED fixed per-index gate: per-position empirical target-hit rate -> softmax. Concentrates on the most-recent slot. Content-blind. FAILS on CONFLICT.
- `CONTENT_ONLY` -- v7-style per-instance query-key gate: softmax(cos(code_{j-1},FLAG)/GATE_TAU). Recency-blind. FAILS on CUE_ABSENT.
- `COMBINED` -- ARBITRATES: softmax(content_rel/GATE_TAU + recency_bias). recency_bias = a fixed top-down prior scaled to a gap of RECENCY_GAP_TARGET logits. THE ARM UNDER TEST.
- `COMBINED_SCRAMBLED` -- firing control: the SAME combined formula but the content_rel vector is DERANGED (fixed per-seed permutation) so a sharp cue lands on a WRONG slot. Isolates that the content ORDERING is load-bearing.

## Readout (parameter-free -- confound-avoidance, see IMPORTANT below)
Per arm: gate-weighted SUPERPOSITION of the K raw slot codes -> codebook CLEANUP (cos vs codebook, argmax over the VALUE sub-vocabulary). NO learned Hebbian W, NO roll-bind, NO train pass. IMPORTANT: an initial design used v7's learned mean-outer Hebbian readout; smoke self-test caught that the SHARED learned W ABSORBS the corpus positional prior (slot K-1 is the target 2/3 of the time), leaking a recency bias into EVERY arm and confounding the per-type separation (CONTENT_ONLY hit 0.702 on cue_absent, not the expected ~0.20). The parameter-free gate-select + cleanup readout removes the confound entirely and is the faithful attention-routing readout (attention selects the slot, output = the selected slot's content). Arbitration is isolated ENTIRELY in the gate.

## Arbitration boundary (analytic, biased-competition)
content overrides recency on a conflict iff the cue logit q/GATE_TAU exceeds the recency top-down bias RECENCY_GAP_TARGET, i.e. q > GATE_TAU*RECENCY_GAP_TARGET. With GATE_TAU=0.05, RECENCY_GAP_TARGET=3.0 => boundary q* = 0.15. Headline q=0.25 (> q*) => content wins conflicts; the low-q tail (0.12, 0.06 < q*) walks BELOW the boundary => COMBINED falls back to recency even on conflicts (the envelope edge). The invariant is that COMBINED never CATASTROPHICALLY fails (it holds recency-level ~0.65 below the boundary).

## Metric
top-1 recall of the correct VALUE token at QUERY (argmax over the VALUE sub-vocab); chance = 1/|V_SUB| = 0.0625. Per-INSTANCE-TYPE breakdown (aligned/conflict/cue_absent) per arm -- the arbitration IS the per-type pattern. Headline K=6, headline realistic q=0.25.

## Bands (pre-registered; headline K=6, q=0.25)
- **VALID-ONLY-IF** (corpus creates the arbitration pressure): RAW in (1.3*chance, 0.50); AND recency FAILS on conflict (rec_conf < comb_conf-0.05); AND content FAILS on cue_absent (con_abs < comb_abs-0.05). Else INCONCLUSIVE (saturation-vacuous / no arbitration pressure).
- **HARD_PASS** [COMBINED only]: COMBINED beats BOTH singles on the mixed corpus (COMB-REC >= 0.10 AND COMB-CON >= 0.10) AND beats EACH on its failure sub-regime (conflict: COMB-REC >= 0.20; cue_absent: COMB-CON >= 0.20) AND scramble fires (COMB-SCR >= 0.20) AND COMBINED >= cap+0.30. => the combined gate genuinely arbitrates -- the full attention-routing capability.
- **MIDDLE_BAND**: COMBINED beats both singles on mixed and scramble fires, but misses a strict sub-regime / scramble / cap+0.30 gate. Real but partial arbitration; the per-type pattern is the finding.
- **HARD_FAIL_NO_ARBITRATION**: COMBINED <= max(single)+0.03 on the mixed corpus. The combined gate does not arbitrate -- collapses to (or below) the better single signal. Honest deflation.
- **ENVELOPE** (reported regardless of tier): the invariant COMB - max(single) per q; the q at which it crosses zero locates the arbitration boundary q* empirically (predicted 0.15).

## Smoke result (N=1024, seed 7, CPU; SAME code path as FULL, FULL CUE_Q_GRID x K_GRID; cardinality 50=1*5*2*5; run_mode=smoke; verdict HARD_PASS)
MEASURED@`data/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu_smoke/metrics.json`:
- @K6 headline q=0.25 (cue_snr=8.0, cap=0.200, chance=0.0625): RAW=0.198, RECENCY[all=0.656, conflict=0.000], CONTENT[all=0.709, cue_absent=0.138], COMBINED[all=1.000, aligned=1.000, conflict=1.000, cue_absent=1.000], SCRAMBLED=0.338. COMB-REC=+0.344, COMB-CON=+0.291, conflict win=+1.000, cue_absent win=+0.862, scramble_sep=+0.662.
- ENVELOPE @K6 (invariant COMB-max(single) per q): {1.0:+0.291, 0.5:+0.291, 0.25:+0.291, 0.12:+0.046, 0.06:-0.016}. Fallback crosses zero between q=0.12 and q=0.06, straddling the analytic boundary q*=0.15. Below q*, COMBINED conflict drops (q0.12:0.284, q0.06:0.006) while cue_absent stays 1.000 and aligned stays 1.000 -- graded fall-back, never catastrophic (COMB_all stays 0.658-0.753). At q=0.06 the weak cue still carries marginal conflict signal that pure-content captures, so the forced recency-fallback is -0.016 below CONTENT there: an HONEST envelope edge, not a headline claim (headline q=0.25 is solidly in the win regime).
- @K10 (cap=0.111): same pattern; RAW=0.102, RECENCY[all=0.651,conf=0.000], CONTENT[all=0.699,abs=0.106], COMBINED[all=1.000] at q>=0.25; invariant {1.0..0.25:+0.301, 0.12:+0.038, 0.06:-0.019}.
- recency gate concentrates on most-recent slot: g_rec@K6=[0.026,0.037,0.039,0.039,0.039,0.82] (argmax=5=K-1), beta~0.99 normalizes the top-down recency bias to a 3.0-logit gap.
- cue calibration (self-test): cos(noisy_flag,FLAG)~=q at q in {1.0,0.5,0.12} (abs err < 0.08).
- self-test PASS: gate_readout one-hot slot-selection; noise calibration; type fractions 1/3; cue_absent has NO flag; recency argmax==K-1; recency_bias gap==3.0; discriminator-fires arbitration pattern at K6/q0.25 small-scale.
- TELEMETRY-SENSITIVITY (self-test, guards against an analytically-pinned metric): (T2) relabeling targets to random tokens collapses COMBINED top1 to 0.06 (chance); (T1) RELOCATING the flag on conflict instances moves the COMBINED-recovered token to the new slot (top1@new=0.92 >> top1@old=0.20). The metric genuinely reads which-slot-is-relevant.

## SCHEMA-VET / META-RULE fields
- cardinality_ok: true. EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(K_GRID)*len(CUE_Q_GRID) = 3*5*2*5 = 150 (FULL). Verdict counts len(per_unit); emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if short. CARD_OK (sweep axes = q x K).
- arms_differ_verified: true (smoke: 5 distinct arm digests over all (K,q) top1 points; ARMS-MUST-DIFFER hash gate in main()).
- final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace).
- except-ordering: `except SystemExit: raise` before `except Exception` (no BaseException / bare except; grep gates clean).
- crlb_n/a: "top-1 recall on a parameter-free gate-select + cleanup readout has no closed-form CRLB; the discriminator is the arm-vs-arm recall GAP whose content+recency-blind floor is the combinatorial candidate cap (THEORETICAL). The cue-detectability floor is the codebook noise floor 1/sqrt(N) (THEORETICAL)."
- discriminator_reachability: true. HARD_PASS (COMBINED >= cap+0.30 AND beats each single on its failure sub-regime by >= 0.20) is on the achievable side (smoke COMBINED=1.000 at q=0.25; singles capped on their failure sub-regime by construction).
- baseline_in_band: true. RAW in (0.0625, 0.50) at all q (smoke ~0.20 @K6, ~0.10 @K10); each single gate < COMBINED on its failure sub-regime (INCONCLUSIVE gate enforces the arbitration pressure exists).
- discriminator survives scale: analytical + smoke. cue_snr=q*sqrt(N) is N-invariant; smoke (N=1024, floor 0.031) is the HARDER cue-inference test and witnesses arbitration at the same cue_snr; FULL (floor 0.011) is more robust. Smoke runs the FULL CUE_Q_GRID x K_GRID at the headline K. (Rules A + B + C satisfied.)
- HP_SCOPE: {COMBINED: [COMB-REC>=0.10, COMB-CON>=0.10, conflict win>=0.20, cue_absent win>=0.20, scramble_sep>=0.20, COMB>=cap+0.30]}. RAW/RECENCY_ONLY/CONTENT_ONLY = single-signal references (each capped on its failure sub-regime; VALID-ONLY-IF gate; NOT HARD_PASS gated). COMBINED_SCRAMBLED = firing control (must NOT pass).
- calibration_check: default_ok_for_this_regime. GATE_TAU=0.05 (v7 value), RECENCY_GAP_TARGET=3.0 top-down bias in LOGIT units -- both FIXED a priori (NOT tuned per-q or per-instance). BETA per (seed,K) only NORMALIZES the learned recency gate to that fixed logit gap. The arbitration boundary q*=GATE_TAU*RECENCY_GAP_TARGET=0.15 is analytic; the discriminator-fires self-test (arbitration on BOTH sub-regimes at the fixed knobs) is the health gate. RECENCY_TAU=0.2 (recency gate sharpness; g_rec[K-1]~0.82 in smoke).
- multi_seed_smoke: N/A -- top-1 recall is deterministic accuracy (capacity-sweep exemption of META_RULE_smoke_single_seed_inflates_AUC), not a continuous AUC/ECE score; FULL runs 3 seeds (SEEDS=[7,17,23]; resumable_seeds iterates all; cardinality gate 150 enforces all 3 seeds x all units landed).

## Defensive error-checking (section 13)
- cell_chunked: false (single-file multi-seed; per-seed checkpoint via write_partial/aggregate_partials; run_seed ~1s/seed parameter-free so runner-death loses at most one cheap seed; resumable).
- start_marker_written: true (_start_marker.json at main() entry).
- crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback, atomic).
- heartbeat_present: true (emit_heartbeat per unit, 150 units FULL).
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: line_buffered_stdout (sys.stdout.reconfigure(line_buffering=True) at cell start; per-(K,q) print each < 1s; timeout_s=1800 so field declared).
- run_mode_verification: FULL landed metrics must show run_mode=full (cell defaults RUN_MODE via HDLAB_RUN_MODE or --smoke; queue dispatches FULL with no --smoke => full; smoke landed run_mode=smoke verified). Orchestrator verifies post-ship.

## Section 15 gates (composition / sweep)
- sweep_alignment_verdict: ALIGNED. Swept params = q (cue-quality of FLAG-present instances) x K. effective_params_per_primitive: content_gate's true-slot key match = q (confirmed by cos calibration); content+recency-blind cap = 1/(K-1); recency prior is corpus-fixed. No nominal-vs-effective mismatch.
- bracket_includes_discriminating_band / discriminating_fraction: the q-axis walks the arbitration boundary q*=0.15 -- q in {1.0,0.5,0.25} above (content wins conflicts), q in {0.12,0.06} below (fall-back edge). The transition IS the finding; the invariant curve crosses zero in the swept range. discriminating_fraction ~ 0.4 (2/5 q-points in the transition/fall-back band).
- composition_edges: content_relevance(query-key over noisy codes) -> combined_gate(softmax(content_rel/tau + recency_bias)) -> gate_readout(gate-weighted superposition) -> codebook cleanup. SHAPE_MATCH at each edge (relevance (B,K) -> gate (B,K) -> superposition (B,N) -> cleanup (B,VOCAB)). No SHAPE_MISMATCH.
- positive_control_arms: RECENCY_ONLY reproduces v5's most-recent-slot concentration (g_rec argmax==K-1). CONTENT_ONLY reproduces v7's query-key content gate (correct on cue-present, fails on cue_absent). COMBINED at q=1.0 reproduces the handed-cue arbitration (COMB=1.000). regime_extension_audit: v5 recency + v7 noisy-content -> v8 ARBITRATION of both; SHAPE_DRIFT is the point (the novel synthesis). The single-gate arms ARE the positive controls at this regime.
- functional_requirements: (1) select the most-recent slot when no reliable cue -> RECENCY_ONLY learned per-position gate; (2) INFER the relevant slot from a graded/noisy content cue -> CONTENT_ONLY query-key softmax; (3) ARBITRATE both when both signals present -> COMBINED softmax(content_rel/tau + recency_bias) normalization; (4) isolate genuine content-match from any peaked admission -> COMBINED_SCRAMBLED derangement control; (5) prove the readout does not leak the positional prior -> parameter-free gate-select + cleanup (no learned W); (6) prove the metric reads which-slot-is-relevant -> telemetry T1/T2 self-tests.

## Compute architecture
batched-GPU. Per (seed,K,q): ONE eval pass over BATCH=256 windows; the noisy per-slot code tensor (B,K,N) is built ONCE per batch and all FIVE arms derived from it (shared codes => arms differ only by gate). Readout is PARAMETER-FREE (gate-weighted superposition + codebook cleanup; NO learned W, NO train pass) so wall time is dominated by build_slot_codes + a few matmuls; no sequential dependency. Storage: no_storage / no_composition. Peak GPU est < 1 GB at N=8192 (no N x N weight matrices).

## Config
- FULL: N=8192, SEEDS=[7,17,23], K_GRID=[6,10], headline K=6, headline q=0.25, CUE_Q_GRID=[1.0,0.5,0.25,0.12,0.06], M_TRAIN=8000 (recency-gate stats only), M_EVAL=2400, M_GATE=2000, BATCH=256, GATE_TAU=0.05, RECENCY_TAU=0.2, RECENCY_GAP_TARGET=3.0 (=> arb boundary q*=0.15), TYPE_FRACS=[1/3,1/3,1/3], V_SUB=16, FLAG=69.
- timeout_s: 1800 (smoke 3s CPU at N=1024 x 50 units; FULL on GPU 3 seeds N=8192 x 2 K x 5 q = 150 units parameter-free, est 1-5 min incl. GPU warmup; 1800 gives generous headroom).

## Number provenance (META_RULE_AC)
- content+recency-blind cap 1/(K-1): THEORETICAL@combinatorial (guess among present candidates).
- chance 1/16=0.0625: THEORETICAL@|V_SUB|=16.
- codebook noise floor 1/sqrt(N): THEORETICAL@random-code cosine std.
- arbitration boundary q*=GATE_TAU*RECENCY_GAP_TARGET=0.15: THEORETICAL@biased-competition logit crossover.
- all smoke arm/curve/sub-regime/envelope/telemetry values: MEASURED@`data/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu_smoke/metrics.json`.
- FULL arm values: HYPOTHESIZED (not yet run); expected COMBINED arbitrates at q>=0.25 across all 3 seeds (invariant > +0.25 at headline), RAW/singles capped, fall-back edge near q*=0.15 at FULL floor.
