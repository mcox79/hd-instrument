# Pre-registration: consol_conjunction_replay_v1

Cell: `experiments/exp_consol_conjunction_replay_v1.py`
Anchor: `consol_conjunction_replay_v1`
Date: 2026-07-15
Author: exp_dev
Routing target: `remote_cpu_queue` (glass-box CPU; ~25s/5-seed FULL). Also run locally to completion (foreground, thread-capped) for the immediate verdict.

## Hypothesis (2x-drill on the consolidation negative)

The consolidation envelope-push (`exp_consol_inductive_entity_replay_cskg_v1`) found interleaved-replay BEATS compute-matched
continual but only MATCHES a fair FREQUENCY bar on SINGLE-RELATION inductive inference (frequency-capped). Hypothesis: on a
CONJUNCTION target (label needs combining >=2 constituents; every proper subset is at chance), interleaved-replay-learned codes
should BEAT frequency where single-relation couldn't -- tying consolidation-replay to the frontier-validated conjunction mechanism.

## Arena (reused from the VET'd `exp_interaction_nonadditive_discovery_v1` / `exp_joint_dual_channel_readout_v1`)

- PARITY over K=4 ordinal constituents (L=4 levels each), N_ENT=220 combos, QUERY_FRAC=0.45, held-out NOVEL combos.
- PARITY is THE canonical frequency-unsolvable conjunction: fixing any single constituent leaves the parity of the remaining
  constituents UNIFORM -> per-constituent mutual information with the label is EXACTLY 0. THEORETICAL@parity single-driver MI=0.
- AND2 = bit0 & bit1 carried as REPORTED CONTEXT (not gated).

## Mechanism under test = the minibatch SCHEDULE

All schedule arms fit the SAME parity-capable SYMMETRIC-PRODUCT-lens readout (shared content codes c(L,d) unit phasors +
one linear head; z = native FHRR product-bind of the K content codes; feat=[Re z, Im z]) with the SAME CE loss and the SAME
per-combo gradient exposure (each train combo trained P_max times in every arm). The ONLY difference is minibatch ORDER,
built as a single flat index stream so example-exposure AND optimizer-step count are IDENTICAL across arms:
- INTERLEAVED: i.i.d. minibatch replay over all train combos (P_max shuffled passes). The mechanism.
- CONTINUAL: task-blocked by constituent-0 level (block_by=1, L blocks; standard task-incremental non-i.i.d. stream), P_max
  passes per block in order, no replay. Compute-matched.
- SHUFFLE: interleaved schedule, train labels permuted (structure destroyed). Must-fail schedule arm.

Reference arms: FREQ_NULL = max(HOMOPHILY, POP) (fair frequency bar, provably ~chance on parity); MEMORIZE; ORACLE = gold
(arena-answerable ceiling). Under-trained probe (P_probe=3) checks the schedule-null is not a full-P ceiling artifact.

## PRIMARY discriminator + PRE-REGISTERED bands (fixed before the FRESH-seed run; H = ORACLE - chance; all HYPOTHESIZED)

PRIMARY discriminator = the SCHEDULE contrast INTERLEAVED-vs-CONTINUAL (the consolidation question). INTERLEAVED-vs-FREQ_NULL is
the readout-works / arena-answerable gate.

- ARENA-VALID (load-bearing): ORACLE fires (ORACLE - chance >= 0.30) AND FREQ_NULL_novel at chance (<= chance + 0.08, the
  FAIRNESS gate) AND SHUFFLE flat (<= chance + 0.25*H; telemetry-sensitivity) AND READOUT-WORKS (INTER - FREQ_NULL >=
  max(0.10*H, 0.10) AND INTER - chance >= 0.30*H) AND compute-matched AND >=20 novel.
- HARD_PASS: arena-valid AND INTER - CONTINUAL >= max(0.10*H, 0.03) on a majority of seeds (replay MANUFACTURES a conjunction
  advantage over compute-matched continual).
- REFUTE: arena-valid AND INTER - CONTINUAL <= 0.01 (readout learns the conjunction + beats frequency, but the SCHEDULE is
  irrelevant -> the conjunction-beats-frequency is a READOUT effect, not a CONSOLIDATION effect). Valuable, drill-worthy.
- MIDDLE: arena-valid AND INTER - CONTINUAL in (0.01, HARD_PASS margin).
- INCONCLUSIVE: oracle underfit / freq above chance / shuffle not flat / readout underfit / too few novel / compute unmatched.

HP_SCOPE: the beat-continual gate applies to INTERLEAVED only. ORACLE=ceiling; FREQ_NULL/HOM/POP=frequency bar; SHUFFLE=must-fail
schedule arm; CONTINUAL=compute-matched head-to-head.

## Compute architecture

Class (b) sequential-CPU with justification: product-lens fit is tiny (D=48 complex, N~121 train, P_max*N/batch ~= 900 steps);
whole 5-seed FULL runs in ~25s single-threaded. Storage strategy = no_storage (learned content codes + linear head; no
bundle/shard retrieval). Deterministic integer seeds (PROT-023). Atomic metrics write (tmp + os.replace via write_metrics).

## SCHEMA-VET fields

- cardinality_ok: EXPECTED_N_UNITS = n_seeds (5); cardinality breach -> HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- arms_differ_verified: SHUFFLE sig distinct from INTERLEAVED. arms_differ_exempted: [(INTERLEAVED, CONTINUAL)] -- they
  legitimately coincide bit-identically when both perfectly solve the conjunction (that IS the measured schedule-null).
- final_metrics_atomicity: tmp_replace.
- crlb_n/a: classification accuracy; noise floor = majority-class chance rate (computed per seed); ceiling = gold ORACLE.
- baseline_in_band: FREQ_NULL pinned near chance (single-driver MI=0); ORACLE=1.0; INTERLEAVED between FREQ and ORACLE.
- calibration_check: adaptive_with_discriminator_gate (all margins are fractions of the MEASURED H + absolute floors; the
  schedule-null is robust across probed configs P_max in {2..150}, block_by {1,2}, emb_d {16..48}, batch {8,16}).
- discriminator survives scale: arena is full-scale at self-test (make_X uses full N_ENT); SHUFFLE must-fail fires.
- real_code_path: self-test exercises the REAL hd_bind (FHRR complex product via _config_term), fit_schedule, arm_homophily,
  acc on the real parity arena at full N_ENT. substrate_signature: hd_bind bound against inspect.signature.
- deterministic_seeding: true (fixed integer seeds; no hash()/list(set())).
- defensive_error_checking: start_marker + crash_diagnostic + heartbeat + per-seed failure_class.
- progress_logging: line_buffered_stdout + per-seed flush prints (FULL << 1800s).

## MEASURED outcome (FULL, fresh seeds [101,103,107,109,113], never used in band calibration)

MEASURED@data/exp_consol_conjunction_replay_v1/metrics.json:
- verdict = REFUTE_CONSOLIDATION_NO_SCHEDULE_ADVANTAGE_CONJUNCTION_IS_READOUT_EFFECT
- PARITY novel: INTERLEAVED=1.000, CONTINUAL=1.000, SHUFFLE=0.519, FREQ_NULL=0.477 (chance=0.512), ORACLE=1.000.
- readout_works: INTER - FREQ_NULL = 0.523 (decisive; conjunction genuine + frequency at chance).
- PRIMARY schedule-gap INTER - CONTINUAL = 0.000 (0/3 seed votes for a positive gap) -> REFUTE.
- under-trained probe (P=3): INTER=1.000, CONT=0.998, gap=0.002 -> null holds OFF ceiling (not a saturation artifact).
- compute_matched (step mismatch = 0.000), freq_at_chance, shuffle_flat all clean.

Interpretation (mechanism localization): the substrate's product-lens readout learns the symmetric parity conjunction so
effectively that BOTH schedules saturate -> replay confers NO advantage over compute-matched continual; the conjunction-beats-
frequency is a READOUT property, not a consolidation property. Replay's advantage (CSKG single-relation) requires CROSS-DOMAIN
code INTERFERENCE (entity codes contested across relation-blocks); a coordinate-blocked SYMMETRIC conjunction has none.
Follow-on drill: an interference-bearing conjunction arena (shared codes pulled to conflicting values across blocks) is the
real test of consolidation-on-conjunction.
