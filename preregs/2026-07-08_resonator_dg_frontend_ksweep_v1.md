# Pre-reg: exp_resonator_dg_frontend_ksweep_v1

Author: hdi_exp_dev | Date: 2026-07-08 | Anchor: resonator_dg_frontend_ksweep_v1

## Question
5x-drill #1 on the skunkworks-CONFIRMED-genuine K5/K6 resonator wall (vanilla oracle_any=0 at K5/K6,
all seeds, N=4096 M=30). Diagnosed as a CONFIG-CONTINGENT CROSSTALK/SNR CAPACITY CLIFF (wall at
M^K ~ N^2, Tsodyks-Feigelman), NOT fundamental basin-multiplicity -- so it should MOVE with N. Does
brain-grounded DIMENSIONAL EXPANSION (the dentate-gyrus DGProjection lever) escape it? The CPU
disentangler (exp_resonator_dg_crosstalk_disentangler_v1, GATE_CLEAR_EXPANSION) already proved on-disk
that expansion 4096->16384 lowers ORACLE crosstalk_std 1.96x (~sqrt(4)) and that the DG mechanism ports
to complex FHRR; this cell tests whether that crosstalk drop CONVERTS to basin REACHABILITY at K5/K6.

## Levers / arms (PAIRED: identical true tuples across arms within each K,seed)
- vanilla   : dense unit-phasor codebooks at N=4096  (reproduces the wall; positive control @ K3/K4)
- expansion : dense unit-phasor codebooks at N=16384 (r=4) -- THE mechanistically-supported rescue arm
- sparsify  : DG-analog sparse-phasor codebooks at N=16384 (top-2%) -- informative-crater ablation
              (disentangler proved this collapses the K-way binding support; kept for in-pipeline parity)
Decode = torch port of the IDENTICAL instrument (exp_resonator_ksweep_reachability_v1 /
_verifier_readout_v1): Glauber-dither + R=10 restart alternating projection + oracle_any reachability +
verifier read-out. Batched over trials x restarts for GPU. K,T0,MAXIT held to the confirmed-negative
harness.

## Measured per (arm, K, seed)
- oracle_any (reachability: any of R=10 restarts lands the true tuple; best over T0 in {0.20,0.35,0.50})
- verifier (best-recon pick among candidates), plurality (control). Invariant: verifier <= oracle_any.

## Capacity math (THEORETICAL@ M^K vs N^2 crosstalk wall; self-tested)
- K5 ratio M^5/N^2: vanilla 1.449 -> expansion 0.091  (SHOULD rescue K5)
- K6 ratio M^6/N^2: expansion 2.72 (> 1; likely NOT rescued at r=4 => modal prediction = PARTIAL)

## Bands (pre-registered BEFORE full; judged on the EXPANSION arm oracle_any, paired vs cratered vanilla)
Per research note (b) + coordinator honest-band directive: PARTIAL is its OWN informative outcome, NOT a fail.
- HARD_PASS (both K5 AND K6 rescued): oracle_any_exp(K5) >= 0.70 AND oracle_any_exp(K6) >= 0.40.
- PARTIAL_RESCUE (K5 rescued only -- the capacity-math MODAL prediction): oracle_any_exp(K5) >= 0.70 AND
  oracle_any_exp(K6) < 0.40. Expansion rescues K5 as predicted; K6 stays above the M^K~N^2 wall at r=4
  (would need larger r). NOT scored as failure.
- HARD_FAIL (neither rescued): oracle_any_exp(K5) < 0.70 -- expansion lowered ORACLE crosstalk (proven in
  the disentangler) but did NOT move BASIN reachability; sharpens the basin-count-vs-crosstalk distinction
  (informative negative, feeds candidate #2 theta-gamma re-encoding as the next escape).

## Positive control (Gate D -- reproduce prior AT TEST REGIME) + discriminator-fires
- vanilla arm K3 oracle_any in [0.95,1.00] (ref 0.992), K4 in [0.72,0.90] (ref 0.806),
  both MEASURED@data/exp_resonator_verifier_readout_v1/metrics.json. Outside tol => torch port diverged =>
  HARD_FAIL_POSITIVE_CONTROL (K5/K6 untrusted).
- DISCRIMINATOR-FIRES: vanilla arm MUST crater at K5 (oracle_any < 0.30, reproducing the confirmed
  negative). If vanilla K5 does not crater, the wall was not reproduced => HARD_FAIL_DISCRIMINATOR_VACUOUS.

## Formula self-test (PASS)
Capacity-math anchors (K5 base=1.448, exp=0.091; K6 exp=2.72 > 1); K=1 decode recovers truth (numpy
mirror of the torch port); sparse-phasor sparsity in [0.015,0.030].

## Compute architecture
Class: (a) batched-GPU. torch.cuda complex64; the R=10 restarts x TRIAL_CHUNK trials are batched into one
B=(chunk*R) tensor per unbind step (matmul-heavy: (B,N)@(N,M) and (B,M)@(M,N) per factor per MAXIT).
N_exp=16384 arms are the GPU-batching candidates (per USER-LOCKED GPU-batching mandate). Trial-chunking
(TRIAL_CHUNK=40 -> B=400) bounds peak memory ~1.5 GB at K6 N_exp=16384. Storage: no_storage (decode-only).
CUDA required for FULL (env HDLAB_ALLOW_CPU_FULL=1 override only for debugging); FATAL if absent.

## Discriminator-survives-scale (SMOKE justification)
The crater-boundary K SHIFTS with N (crater-K = smallest K with M^K/N_exp^2 > ~1). SMOKE runs at
N_base=2048 (vanilla) -> expansion 8192, where K5 ratio moves 5.8 (vanilla crater) -> 0.36 (expansion
rescue), directly demonstrating expansion-rescues-K5 at half the FULL N. Smoke gate = "exists K where
vanilla craters (<0.30) AND expansion lifts >=0.20"; the FULL judges the shifted K5/K6 at N_exp=16384
(ratio 0.091) via the calibrated 0.70/0.40 bands + analytical capacity-math (option B).

## SCHEMA-VET fields
- arms_differ_verified: true (META_RULE_AF; vanilla/expansion/sparsify reachability hashes distinct at K5;
  HARD_FAIL if bit-identical).
- final_metrics_atomicity: tmp_replace (write_metrics) + per-seed write_partial + resumable_seeds resume.
- cardinality_ok: EXPECTED_N_UNITS = 3 seeds x 4 K x 3 arms = 36; HARD_FAIL_CARDINALITY_META_RULE_H if
  len(per_seed)!=3 OR any seed lacks all 12 arms.
- crlb / discriminator_reachability: bands bracket the capacity-math (K5 exp ratio 0.091 => reachable);
  both PARTIAL and HARD_PASS physically reachable. reachable = true.
- baseline_in_band / positive_control_arms: vanilla K3 [0.95,1.00], K4 [0.72,0.90] (Gate D); vanilla-crater
  gate at K5.
- HP_SCOPE: {oracle_any_exp_K5: [HARD_PASS_0.70, PARTIAL_0.70], oracle_any_exp_K6: [HARD_PASS_0.40]}.
  The vanilla + sparsify arms do NOT inherit the rescue HARD_PASS gate (vanilla = baseline/positive-control
  expected to crater; sparsify = expected-crater ablation).
- calibration_check: default_ok_for_this_regime (reconstruction verifier is parameter-free argmax; T0 grid
  matched to the confirmed-negative harness).
- functional_requirements: "raise crosstalk SNR to escape the M^K~N^2 wall" -> dimensional expansion via
  DGProjection expansion (existing primitive, re-wired to the resonator factor codebooks as complex FHRR).
- start_marker_written / crash_diagnostic_present / heartbeat_present: true (_write_start_marker;
  _write_crash_metrics via except Exception with SystemExit/KeyboardInterrupt re-raised FIRST; _heartbeat).
- progress_logging: print_flush_true + per-arm heartbeat jsonl.
- cell_chunked: false (3-seed loop with per-seed write_partial + resumable_seeds checkpoint/resume).
- PAIRED: identical true tuples (rng seed*1000+K, arm-independent) + matched-seed codebooks across arms.

## Smoke result (2026-07-08, CPU) -- cell VALIDATED; discriminator fires; full-N preview is DECISIVE NEGATIVE
Cell mechanics + torch port VALIDATED:
- SMOKE_GATE_PASS at default smoke (N_base=2048 -> expansion 8192, seed 3): expansion RESCUES the crater-
  boundary K4 (vanilla 0.000 -> expansion 0.708, lift 0.708). The expansion lever demonstrably MOVES
  reachability. Torch port faithful: expansion K4 @ N=4096 = 0.708 ~ numpy reference K4 = 0.806.
- sparsify arm craters everywhere (0.000), matching the disentangler collapse.

FULL-N discriminator PREVIEW (targeted CPU probe at the FULL's actual regime N_base=4096 -> expansion
N=16384, K5, TR=24; MEASURED@data/exp_resonator_dg_frontend_ksweep_v1_smoke partials seed 3, 7):
- expansion K5 @ N=16384 (K5 ratio M^5/N^2 = 0.091) = **0.000** across seeds 3 AND 7 (960 trajectories,
  ZERO truth-hits). Also 0.000 at N=8192 (ratio 0.362). vanilla K5 = 0.000 (all). sparsify K5 = 0.000.
=> The expansion arm does NOT rescue K5 at the FULL regime. Preview = HARD_FAIL.

MECHANISM (the informative negative): the disentangler PROVED the K5 basin is crosstalk-CLEAN at
N=16384 (ORACLE-unbind recover=1.00, margin=0.988, crosstalk_std -1.96x). Yet the full resonator DECODE
reaches it 0/960 times. => The K5/K6 wall is a BASIN-REACHABILITY / convergence-dynamics wall, NOT a
crosstalk-SNR capacity cliff. Dimensional expansion lowers crosstalk (real, proven) but crosstalk is not
the binding constraint at K5 -- so expansion does NOT escape the wall. This CONFIRMS the research note's
pre-registered HARD_FAIL band + its honest gap ("decorrelation raises pure capacity, not basin count"),
now with on-disk evidence. (p_basin(K5) < 1/960 ~ 0.001, expansion-invariant across N in {4096,8192,16384}
=> not restart-budget-liftable at any realistic R either.)

## Dispatch DECISION: DO NOT DISPATCH GPU (honest abort per DISCRIMINATOR-MUST-SURVIVE-SCALE)
The CPU preview at the EXACT full regime (N=16384, K5, 2 seeds, 960 trajectories) decisively shows the
expansion arm = 0.000 => the GPU FULL is predicted HARD_FAIL. Dispatching would burn GPU (against the
once-per-stage GPU discipline) only to reconfirm a negative already visible at full-N. Per the exp_dev
rule "reject the full dispatch if discriminator preview shows no signal; honest abort beats fake verdict."

OPTIONAL canonical reconfirmation (only if the director wants the official multi-seed negative on the
remote queue -- predicted HARD_FAIL):
  bash tools/orchestrator/queue_add.sh overnight_queue resonator_dg_frontend_ksweep_v1 \
    experiments/exp_resonator_dg_frontend_ksweep_v1.py preregs/2026-07-08_resonator_dg_frontend_ksweep_v1.md 10800

## Forward routing (mechanism-driven)
The wall is decode-dynamics, not encode-crosstalk => escape must change the DECODE/ENCODING, not the
dimension. Elevates: (1) candidate #2 theta-gamma SEQUENTIAL re-encoding (never pose the K-way joint
search; K*M sequential slots instead of M^K), and (2) ACF asymmetric-codebook-factorizer decode-side
rescue (cap_map row 51). Expansion is NOT dead -- it cleanly rescues crosstalk-limited K (K4) and could
compose with a reachability fix; it is simply orthogonal to the K5 reachability wall.
