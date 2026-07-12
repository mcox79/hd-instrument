# Pre-reg: held-out-ENTITY inductive probe -- GPU re-route v2 (FULL-FIDELITY re-fit to fire the oracle)

- Anchor: `course_c_heldout_entity_inductive_probe_gpu1024_v2`
- Cell: `experiments/exp_heldout_entity_inductive_probe_cskg_gpu1024_v2.py` (wrapper) over
  `experiments/exp_heldout_entity_inductive_probe_cskg_v1.py` (base)
- Supersedes: `course_c_heldout_entity_inductive_probe_gpu1024_v1` (landed INCONCLUSIVE_ORACLE_UNDERFIT;
  MEASURED@data/exp_course_c_heldout_entity_inductive_probe_gpu1024_v1/metrics.json)
- Filed: 2026-07-12
- Queue: `overnight_queue` (GPU; `import torch` at wrapper top routes here per PROT-020; fpe_dim=1024 fits the card;
  resumable via FitCheckpoint)

## Question (unchanged from v1; now made ANSWERABLE)

Does the current glass-box KGE geometry (`ONESHOT_ROTATE` phase-rotation + `ADDITIVE_TRANSE`) GENERALIZE to entities
ENTIRELY ABSENT from train (true induction), or only memorize search over the trained entity set? v1 could not
answer because its ORACLE positive control did not fire (arena not certified answerable). v2 restores full fit
fidelity so the ORACLE fires and the verdict is INTERPRETABLE.

## What changed vs v1 (fit fidelity ONLY -- everything else identical)

| knob | v1 (moderated) | v2 (un-moderated) | rationale |
|---|---|---|---|
| epochs | 200 | **500** | anchor-1 fired the l2 oracle at 250; pushed to 2x (low end of the 2-3x escalation cap) for the harder held-out-entity oracle |
| n_neg | 64 | **128** | anchor-1 ranking pressure (drives gold toward rank-1 out of N; sharpens the folded held-out-tail codes) |
| k | 24 | 24 (unchanged) | capacity-relevant knob, matched to the completed gpu1024 FULL_CFG |

Everything else IDENTICAL: the held-out-entity split (`HELDOUT_ENTITY_FRAC=0.15`), arms
(ONESHOT_ROTATE/ADDITIVE_TRANSE), controls (RANDOM_CODES/CODEALIAS/BASELINE_POP), the ORACLE_TRANSDUCTIVE gate,
batch=8192, neg_chunk=16, ckpt_every=20, seeds=[7,13,17], n_heldout_eval<=3000, all bands.

Why more epochs cannot manufacture a false GENERALIZE: a held-out tail has NO learned vector in the
ONESHOT/ADDITIVE arms (random-init by split construction), so those arms stay ~random-code at ANY epoch. Epochs only
sharpen the SEEN and ORACLE (folded held-out) geometry -> raising epochs strictly and only improves the ORACLE's
ability to fire, which is exactly the interpretability lever this run needs. THEORETICAL@this prereg (per-entity
embedding tables, GraIL/NBFNet architectural fact).

Anchor-1 fidelity provenance (the fired-oracle recipe): MEASURED@data/exp_course_c_rotate_cskg_l2_seed_{7,17,23}_gpu1024_v1/metrics.json
(config k=24 epochs=250 n_neg=128; verdict MIDDLE_BAND_PARTIAL -> their ORACLE cleared the >=0.15 direct gate, i.e.
did NOT land INCONCLUSIVE_ORACLE_UNDERFIT).

## Pre-reg bands (verbatim from v1; the HARD GATE is oracle_fires)

Let `margin = max(ONESHOT, ADDITIVE) held-out hits@10 - RANDOM_CODES held-out hits@10` (mean over seeds).
The verdict is reported ONLY when `oracle_fires` (ORACLE hits@10 - RANDOM hits@10 >= `ORACLE_FIRE_MARGIN=0.10`).

- HARD-PASS: `margin >= 0.05` AND oracle_fires AND not broken -> `HARD_PASS_INDUCTIVE_ENTITY_TRANSFER` (GENERALIZES;
  the inductive question is alive at scale).
- MIDDLE-BAND: `0.02 <= margin < 0.05` AND oracle_fires -> `MIDDLE_BAND_PARTIAL_ENTITY_TRANSFER`.
- HARD-FAIL: `margin < 0.02` AND oracle_fires -> `HARD_FAIL_MEMORIZED_NO_ENTITY_TRANSFER` (PROVEN MEMORIZE; replicates
  the SR-code HARD_FAIL, MEASURED@data/exp_grounding_learned_sr_heldout_reasoning_v1/metrics.json). Deflated-prior
  expectation P=0.15-0.20 (CITED@notes research_does_it_scale note).
- ESCALATION BRANCH (honest, do NOT force a null): if the ORACLE still does NOT clear 0.10 at this full/max fidelity,
  the base cell returns `INCONCLUSIVE_ORACLE_UNDERFIT`. Interpret as `INCONCLUSIVE_ORACLE_CEILING`: the per-entity
  KGE fit itself cannot support held-out-entity inference at this scale -- itself directional evidence toward the
  factorized map-builder (per the scaling drill). Cap held at ep=500 (2x); ep=750 (3x) is the remaining headroom
  before declaring a hard ceiling. Do NOT burn beyond the cap.
- Also gated INCONCLUSIVE if `n_heldout < 20` (`INCONCLUSIVE_TOO_FEW_HELDOUT`) or a control beats POP by > 0.03
  (`BROKEN_TEST_CONTROL_BEATS_POP`).

## Oracle-fire target (this run's success criterion)

`oracle_fire_target: ORACLE_TRANSDUCTIVE held-out hits@10 - RANDOM_CODES held-out hits@10 >= 0.10` (mean over 3
seeds). v1 measured this margin at 0.0119 (< 0.10 -> INCONCLUSIVE). The 2x-epoch / 2x-n_neg fidelity bump targets
clearing 0.10 so the zero-geometry arms become interpretable.

## Four validity-preflight checks (declared; fired at self-test scale, SAME path as v1)

1. positive_control_passes: ORACLE recovers held-out tails and clears RANDOM by the fire margin.
2. metric_moves: held-out hits@10 moves across [RANDOM, ONESHOT, ORACLE].
3. negative_control_fails_with_margin: RANDOM + CODEALIAS sit below ORACLE by the fire margin (>=2 repeats).
4. full_gates_exercised_at_selftest: `aggregate_and_verdict` runs on the planted per-seed, firing every fail-closed
   gate (arms_differ / oracle_fires / broken_test_guard / enough_heldout / band_gate).

## Self-test result (MEASURED; self-test path is UNCHANGED by the fidelity bump -> fires identically)

The v2 edit touches ONLY `FULL_CFG` (the real-data fit). `SELFTEST_CFG` and `mechanism_selftest()` are byte-for-byte
unchanged, so the self-test fires the ORACLE deterministically exactly as measured on the v1 gpu run
(MEASURED@data/exp_course_c_heldout_entity_inductive_probe_gpu1024_v1/metrics.json:mechanism_selftest):

- ORACLE_TRANSDUCTIVE h@10 = 0.3333 (recovers held-out tails when codes learned) -> positive control fires.
- ONESHOT = RANDOM = CODEALIAS = 0.0263 (near chance; held-out entity has a random code). ADDITIVE = 0.0614.
  POP = 0.0000 (at floor; fit-independence confirmed).
- oracle_margin = 0.30701 (>> 0.10); metric moves; arms_differ = True (6 distinct sigs); validity_preflight_ok = True.
- The self-test HARD_FAILs the run (SystemExit 1) if the oracle does not recover/fire -> the discriminator is
  gated at cell entry before any real-data compute.

## Compute architecture

class (c) MIXED. Storage SHARDED (per-entity phase codes; per-type relation rotations). device=cuda on
overnight_queue (fpe_dim=1024 fits the 8GiB card; held-out PRIMARY metric is fpe_dim-independent). GPU-batched
minibatch SGD fits; neg-scoring chunked (neg_chunk=16) so the (batch,n_neg,k) transient never materializes whole.
Readouts query-chunked (the (nq,N) map never materialized whole). Per-fit FitCheckpoint every 20 epochs to the v2
anchor dir -> any timeout/outage/sleep resumes each arm from its last epoch (fingerprint keys on epochs+n_neg so
the ep=500 config starts fresh, never stale-resumes the v1 ep=200 checkpoints). Per-seed empty_cache between seeds.

## SCHEMA-VET fields

- cell_chunked: false (in-process 3-seed loop; each fit outage-resumable via FitCheckpoint + per-seed write_partial;
  per-seed process isolation is provided by the overnight runner's per-run invocation). start_marker_written: true.
  crash_diagnostic_present: true. heartbeat_present: true. defensive_error_checking: passed_all_4_patterns.
- final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
- arms_differ_verified: true (>=4 distinct sigs asserted per seed; v1 measured 6). arms_differ_exempted: none.
- cardinality_ok: true (EXPECTED_N_UNITS = n_seeds = 3; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H wired).
- crlb_n/a: "chance hits@10 = 10/N ~ 0.0004 at N~25.7k; HARD-PASS 0.05-above-random is achievable (the ORACLE
  positive control demonstrates recovery when the code exists); discriminator_reachability OK."
- baseline_in_band: ORACLE positive control must fire above RANDOM+margin; RANDOM/POP near the 10/N floor.
- discriminator survives scale: analytical (B) -- per-entity embedding tables cannot encode an unseen entity by
  construction (GraIL/NBFNet), so the null persists at ANY N; ORACLE-fires proves the metric can move at scale.
- calibration_check: adaptive_with_discriminator_gate (HELDOUT_ENTITY_FRAC / ORACLE_FIRE_MARGIN pre-registered, not
  tuned on real data; the planted self-test verifies ORACLE recovers when codes are learned).
- progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints; timeout_s >= 1800).
- run_mode: full (base main() defaults run-mode=full; runner invokes without --self-test/--smoke; section-16 post-dispatch
  run_mode verification required at landing).
- HP_SCOPE: the inductive HARD-PASS gate applies to ONESHOT_ROTATE / ADDITIVE_TRANSE only. ORACLE = positive control
  (must fire); RANDOM/CODEALIAS = must-not-clear-bar controls; POP = fit-independence sanity.

## Timeout justification (exceeds the 14400 soft cap; justified)

Set `--timeout 21600` (6h). v1 ran 3 seeds in 3024s at ep=200/n_neg=64. v2 at ep=500/n_neg=128 scales ~2.5x
(epochs) x ~1.65x (doubled neg-scoring, ~65% of per-epoch fit cost) ~= 4.1x -> expected ~12400s (~3.5h). The 6h
ceiling gives margin for GPU contention + the doubled neg-scoring; per-fit FitCheckpoint every 20 epochs makes any
timeout a RESUME (no lost compute), not a loss.

## Dispatch (overnight_queue; exp_dev hands to orchestrator -- push + SCP-ship, exp_dev cannot push)

`bash tools/orchestrator/queue_add.sh overnight_queue course_c_heldout_entity_inductive_probe_gpu1024_v2 \
  experiments/exp_heldout_entity_inductive_probe_cskg_gpu1024_v2.py \
  preregs/2026-07-12_heldout_entity_inductive_probe_cskg_gpu1024_v2.md 21600`
