# PRE-REG: end-to-end substrate loop HARD regime -- learned-vs-symbolic bridge (v2)

Anchor: `integration_end_to_end_loop_bridge_HARD_v2`
Cell: `experiments/exp_integration_end_to_end_loop_bridge_HARD_v2.py`
Owner: exp_dev. Date: 2026-07-05.
Predecessor: `integration_end_to_end_loop_bridge_v1` (CHAIN_GRADE; the VET flagged 3 scope limits addressed here).

## Prior-work check (substrate concept-query, MANDATORY)
`bash tools/substrate_query.sh "learned bridge beats symbolic cleanup cross-algebra hand-off co-trained
denoising reasoning to generation"` -> top hit cosine=0.2705 ("RF exp_dev hand-off federated unlearning",
unrelated). NONE at cosine>0.30. This learned-vs-symbolic-bridge separation question is genuinely NEW, not
a rediscovery of a prior arc cell.

## Question (the VET's expansion criterion)
v1 measured cotrained_linear end2end=1.000 AND naive_symbolic end2end=1.000 -- a TIE. The co-trained bridge
was NOT shown uniquely necessary (a parameter-free symbolic cleanup->clean-code-lookup tied it). v1 was
object-slot-only (subj/rel handed clean), single-hop, D_store=3, V=1024. MEASURED@data/exp_integration_end_
to_end_loop_bridge_v1/metrics.json:arms.cotrained_linear.end2end_mean=1.0, arms.naive_symbolic.end2end_mean=1.0.

v2 asks: **is there a regime where the LEARNED bridge BEATS symbolic cleanup?** If yes -> the co-trained
bridge is load-bearing for the glass-box loop. If no (symbolic ties/beats at every tested regime) -> the
substrate's reason->generate composition is EFFECTIVELY SYMBOLIC and the learned bridge is not load-bearing
-- an honest, useful NEGATIVE for the glass-box story. Both outcomes are reported honestly (constructive; no vs-LLM).

## Three stressors added over v1 (the VET's expansion targets)
1. SUBJECT + OBJECT both recovered-noisy-and-bridged (v1 handed subj/rel clean). End-to-end exact-ordered
   now gates on TWO bridged slots -> the bridge carries more load; per-slot advantage compounds. (Relation
   stays a clean query KEY -- you legitimately know what you asked.)
2. MULTI-HOP reasoning: objects bound under a composite role PATH of length `hops` (circular-conv of hops
   distinct roles); recovery unbinds the same composite. hops=3 at hard compounds unbind crosstalk.
3. OBJECT INTERFERENCE: hard regime V=4096 + NEAR-NEIGHBOUR HUB CLUSTERS (the D_store fillers of a trace
   are a cosine cluster, mean pairwise cosine ~0.74 MEASURED) -> symbolic NN-argmax mis-commits under crowding.

EASY-REGIME RAIL (control): single-hop, D_store=3, V=1024, uniform-random fillers == v1's regime. Its job:
prove any hard-regime separation is STRESSOR-induced, not a bridge artefact.

## The mechanism distinction under test
- `naive_symbolic`: HARD argmax of the recovered HV into the nearest test concept (BGE cosine), then emit
  that concept's CLEAN generation code. Parameter-free. Wins the generation argmax whenever its NN-pick is
  right (emits a bit_agree=1.0 code).
- `cotrained_linear` (the DELIVERABLE): ridge bridge W fit on reasoning-RECOVERED (noisy) HVs paired with
  the clean target codes (v1's own stated next-step upgrade: co-train on recovered HVs, NOT clean fillers).
  A learned linear DENOISER of the specific reasoning crosstalk -- a capability parameter-free cleanup lacks.
  Emits sign(hv @ W), a NOISY code. Whether the learned denoising edge survives to the end-to-end triple is
  the open question. CITED@Hersche et al. Nat. Nanotech. 2023 (arXiv:2211.05052): naive-vs-cotrained 16.22pt.

## Arms (5; paired trials; per-arm + per-slot reported per Fix#28)
1. `cotrained_linear` (DELIVERABLE) -- W on recovered noisy HVs, HELD-OUT train concepts. code=sign(hv@W).
2. `naive_symbolic` (BASELINE-TO-BEAT) -- NN-argmax -> clean code lookup.
3. `naive_randproj` (FLOOR) -- fixed random projection + sign; bolt-on that ignores target geometry.
4. `stored_direct` (POSCTRL / WIRING gate) -- ORACLE: emit the CLEAN L_gen codes of the true subj/obj
   (perfect bridge). Isolates the 3-slot generation-DECODER ceiling from any bridge quality. If this
   recovers (>=0.70) the decoder works and any arm shortfall is attributable to its BRIDGE.
5. `broken_reasoning` (DISCRIMINATOR) -- object unbound by an UNSTORED role path (identity severed). MUST
   collapse to chance -> proves end-to-end accuracy is attributable to genuine reasoning, not leakage.

## Metric
END-TO-END exact-ordered = (subj_pred, rel_pred, obj_pred) == (S, rel_q, obj_q). Gates on the two BRIDGED
slots (subj + obj); relation is a clean key. Per-slot obj_acc + subj_acc + bridge bit-agreement also reported.

## Pre-registered bands (HYPOTHESIZED@this-prereg; verified vs smoke before dispatch)
Load-bearing comparison = COTRAINED vs NAIVE_SYMBOLIC (paired). margin_hard = cot_hard - sym_hard.
- HARD_PASS (learned bridge load-bearing): margin_hard >= 0.10 AND cross-seed cv(cot_hard) < 0.10 AND the
  easy rail stays TIED (|cot_easy - sym_easy| <= 0.08) -> separation is stressor-induced; composition NOT
  purely symbolic.
- HARD_FAIL (composition effectively symbolic; honest negative): margin_hard <= 0.02 (TIE_EPS) -- symbolic
  ties/beats even after being degraded into band. Learned bridge not load-bearing.
- MIDDLE_BAND: 0.02 < margin_hard < 0.10, OR cv >= 0.10, OR rail not tied.
- INCONCLUSIVE_NO_DISCRIMINATING_POWER: min(cot_hard, sym_hard) >= 0.90 (both saturated -> stressor separated
  nothing). Guarded against at smoke (SMOKE_ITERATE_REGIME).
- Band feasibility (META_RULE_L): HARD_MARGIN=0.10 strictly above TIE_EPS=0.02 (gap 0.08; well separated).

## Discriminator-fires gates (META_RULE_K; all modes; smoke satisfied)
- WIRING: stored_direct (ORACLE decoder ceiling) end2end >= 0.70 in BOTH regimes.
  SMOKE MEASURED@data/exp_integration_end_to_end_loop_bridge_HARD_v2_smoke/metrics.json:
  controls.posctrl_stored_direct_end2end = {easy: 1.0, hard: 1.0}.
- IDENTITY: broken_reasoning end2end <= 0.10 in BOTH regimes. SMOKE MEASURED@same:
  controls.broken_reasoning_end2end = {easy: 0.0, hard: 0.0}; broken_collapsed = {easy: true, hard: true}.
- ARMS-DIFFER (META_RULE_AF): W != R_naive; rec_cotrained != rec_broken; rec_cotrained != rec_symbolic.
  SMOKE MEASURED@same:arms_differ_verified = true.

## Smoke result (MEASURED; 3 seeds, difficulty axes at FULL, only trials/n_train reduced)
- SMOKE_MACHINERY_OK, exit 0, elapsed 51.7s.
- Hard-regime naive_symbolic IN BAND: end2end=0.861 MEASURED@same:regimes.hard.end2end.naive_symbolic
  (0.15 < 0.861 < 0.90 -> stressed but not floored; room to answer cot-vs-sym).
- Per-slot HARD (symbolic dominates, NOT a two-slot artefact):
  cotrained  obj_acc=0.125 subj_acc=0.500 end2end=0.056 bit_agree=0.764  MEASURED@same:regimes.hard.*
  symbolic   obj_acc=0.903 subj_acc=0.958 end2end=0.861 bit_agree=0.977  MEASURED@same:regimes.hard.*
- Easy rail: cot=0.764 sym=1.000 (margin -0.236) MEASURED@same:regimes.easy.end2end.*
- key_comparison.hard_cot_minus_sym = -0.8055; easy_cot_minus_sym = -0.2361; learned_separates_at_hard=false.
- PREVIEW -> FULL will likely land HARD_FAIL (learned linear bridge not load-bearing; symbolic dominates
  every regime + BOTH slots). Root cause: symbolic re-emits a CLEAN code post-argmax; the learned linear
  bridge emits a NOISY code that loses the V=4096 hub-crowded generation argmax. SCOPE: bounded to LINEAR
  bridges; a nonlinear/MLP denoiser is future work (noted in verdict). This is the VET's anticipated,
  useful negative for the glass-box story.

## SCHEMA-VET checklist
- `arms_differ_verified`: True (smoke). arms_differ_exempted: none (the differ-check compares mechanism
  artifacts W vs R_naive + severed-identity + symbolic recovery streams, not perfect-recovery outputs).
- `final_metrics_atomicity`: tmp_replace (metrics.json.tmp then os.replace).
- `cardinality_ok`: EXPECTED_N_UNITS = n_seeds(3) * n_regimes(2) * n_arms(5) = 30. Smoke MEASURED n_units=30/30.
- `except SystemExit: raise` BEFORE `except Exception`; no bare/BaseException (grep-gated, CLEAN).
- `crlb_floor_computed`: chance obj acc = 1/V (hard V=4096 -> 0.000244) THEORETICAL; broken lands here.
  `crlb_n_a` for the bridge itself (learned linear map has no closed-form noise floor; oracle posctrl=1.000
  bounds the decoder ceiling). `discriminator_reachability`: True (HARD_MARGIN=0.10 reachable in principle;
  smoke shows the observed margin is NEGATIVE -> the reachable answer at this regime is HARD_FAIL).
- `baseline_in_band` (META_RULE_AG): the baseline-to-beat = naive_symbolic; hard-regime sym=0.861 in
  (0.15, 0.90) MEASURED. posctrl(oracle)=1.0 recovers; broken=0.0 collapses. Not both-saturated (cot=0.056).
- `calibration_check`: default_ok_for_this_regime (substrate primitives used directly; ridge lambda=1.0 is a
  fixed label-free regularizer; bridge trained on a DISJOINT concept pool run through the SAME regime
  pipeline -- no test leakage; per-output-bit ridge well-posed since n_samples=2*max(64,n_train/2) > N_R=1024).
- `discriminator survives scale`: the DIFFICULTY axes (V, hops, D_store, hub_cluster, N_R=1024, N_G=8192)
  are held at FULL in smoke; smoke reduces ONLY trials (24 vs 60) and n_train (3072 vs 4096); seeds identical
  (3). So the smoke hard-in-band (sym=0.861) IS the full-N preview (option A).
- `progress_logging`: line_buffered_stdout + print_flush_true (per-(regime,seed) print + _heartbeat.jsonl).
  Full run est < 3min so per-seed cadence adequate (60s-cadence rule targets 15min+ cells).
- `cell_chunked`: false (single cell; 3 seeds x 2 regimes inline, wall < 3min; runner-death risk minimal).
  start_marker_written: true; crash_diagnostic_present: true (Exception -> CELL_CRASHED + traceback);
  heartbeat_present: true; defensive_error_checking: passed_all_4_patterns.
- `run_mode verification`: cell defaults run_mode=full (bare invocation / HDLAB_RUN_MODE); asserts written
  run_mode==mode. Post-dispatch VERIFY that landed run_mode==full + size sane (§16).

## §15 composition/sweep gates
- `sweep_alignment_verdict`: ALIGNED. Two named regimes (easy rail + hard); no nominal-vs-effective sweep.
  Each regime's difficulty params are the params the primitives actually experience.
- `discriminating_fraction`: n/a as a parameter sweep; the discriminating contrast is cotrained-vs-symbolic,
  which is measurable at hard (gap 0.805 MEASURED) and the rails (posctrl/broken) fire by construction.
- `composition_edges`:
  - store->reason (multi-hop): SHAPE_MATCH (HRR circular-conv, N_R=1024, real BGE; composite role path is
    iterated bind of the proven primitive).
  - reason->bridge->generate: SHAPE_MISMATCH_adapter_bridge (the cross-algebra/cross-dim seam; adapter = the
    bridge arm under test; the mismatch IS the subject of the experiment, not an unhandled gap).
- `positive_control_arms`: stored_direct (ORACLE clean codes) reproduces the generation-decoder ceiling
  (=1.000 at V=4096 3-slot MEASURED) -> the decoder machinery reproduces the roles-known decoder (CITED
  exp_generation_decoder_roundtrip_v1 exact-ordered ~1.0). regime_extension_audit: the store/reason
  primitive is exercised at N_R=1024 real BGE (its chain-grade regime) with a deeper composite path
  (SHAPE_DRIFT documented: hops>1 accumulates unbind crosstalk by design -- that is the intended stressor).
- `functional_requirements`:
  - perceive+store correlated multi-hop fact -> HRR bundle of composite-role-path-bound BGE fillers.
  - reason multi-hop -> HRR unbind by the composite role path (+ subject-role unbind).
  - cross-algebra hand-off -> the bridge (the arms under test).
  - generate ordered tokens -> bipolar-BSC roles-known decode (generation primitive).

## Compute architecture
Class: (b) sequential-CPU with justification. Per-trial loop has a genuine sequential dependency
(store -> reason -> bridge -> generate). Matmuls are small (V<=4096, N_G=8192); real BGE fillers; wall < 3min
total; not a batching candidate. HRR via FFT (N=1024). Storage strategy: BUNDLED (T = sum of role-bound
fillers) -- exempted from the sharded-default because the bundle CROSSTALK is the reasoning-noise SOURCE the
bridge must denoise; sharded storage would eliminate the crosstalk and defeat the experiment (case b/c of the
storage mandate: the cell IS testing the bundle-crosstalk regime). No persistent substrate store mutation
(read-only; in-memory HRR trace per trial). Real correlated fillers from the compact BGE subset cache
(data/gen_integration_loop_cache/bge_concept_subset_12288_v1.npz, ~47MB; SCP to remote -- untracked npz not
auto-shipped by queue_add).

## Dispatch
- Smoke: local (3 seeds, difficulty at FULL). PASS (SMOKE_MACHINERY_OK, 51.7s, exit 0). Self-test PASS (4.9s, exit 0).
- FULL: remote_cpu_queue (60 trials, 3 seeds, 2 regimes, n_train 4096). timeout 900s (~9x margin over ~100s
  expected). CPU-only. REQUIRES: (1) commit+push to origin/main (harness-denied to exp_dev -> orchestrator),
  (2) SCP the BGE subset cache to the remote before dispatch (untracked npz).
