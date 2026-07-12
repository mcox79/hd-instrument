# Pre-reg: held-out-ENTITY inductive probe (CSKG-core) -- Anchor 1, does-it-scale hand-off

- Anchor: `heldout_entity_inductive_probe_cskg_v1`
- Cell: `experiments/exp_heldout_entity_inductive_probe_cskg_v1.py`
- Hand-off: `notes/exp_dev_handoff_research_does_it_scale_reasoning_vs_frequency_2026-07-12.md` (Anchor 1)
- Research note: `notes/research_does_it_scale_reasoning_vs_frequency_scaling_law_2026-07-12.md`
- Filed: 2026-07-12
- Queue: `remote_cpu_queue` (scoring/re-fit pass over the CSKG-core graph; no GPU; resumable via fit-checkpoint)

## Question

Does the current glass-box KGE geometry (`ONESHOT_ROTATE` phase-rotation + `ADDITIVE_TRANSE`) GENERALIZE to
entities ENTIRELY ABSENT from train (true induction), or does it only do memorized search over the trained entity
set? This is the single cheapest falsifier of "does naive N-scaling of the current mechanism work" -- per
GraIL/NBFNet (CITED@research note HEADLINE 5) a fixed per-entity embedding table cannot encode an unseen entity by
construction, and this substrate already got a clean HARD_FAIL on the structurally similar SR-code mechanism
(`grounding_learned_sr_heldout_reasoning_v1`, 3 seeds FULL, HARD_FAIL, held-out reach@2 0.1148 vs random-code 0.104,
delta 0.011 < 0.05; MEASURED@data/exp_grounding_learned_sr_heldout_reasoning_v1/metrics.json).

## Design (held-out-ENTITY split; reuses the completed rotate machinery verbatim)

- Corpus: `build_cskg_core_triples(0, k_core=12, 0, seed)` -> same CSKG-core graph as the completed run
  (~25,752 entities / 29 relations; MEASURED@data/exp_course_c_rotate_cskg_l2_seed_17_gpu1024_v1/metrics.json).
- Split: withhold `HELDOUT_ENTITY_FRAC = 0.15` of entities from EVERY train edge. Per-entity codes for withheld
  entities are NEVER updated by SGD (they stay at random init BY CONSTRUCTION). train = edges with BOTH endpoints
  seen. Held-out queries = edges with the GOLD TAIL withheld and the head seen (rank an unseen tail).
- Arms (PAIRED on the SAME held-out queries + candidate set):
  - `ONESHOT_ROTATE` -- rotation fit on both-seen edges; gold-tail code = random init.
  - `ADDITIVE_TRANSE` -- additive-TransE fit (functional-form head-to-head).
  - `RANDOM_CODES` -- random phases + relations (the random-code control = the bar to clear by >=0.05).
  - `CODEALIAS` -- fitted relation rotations THETA + RANDOM entity codes (necessity control; if ONESHOT ~ CODEALIAS
    the fitted entity geometry adds nothing on unseen entities).
  - `ORACLE_TRANSDUCTIVE` -- SAME rotation fit but held-out edges FOLDED INTO the fit (gold-tail codes learned);
    POSITIVE CONTROL proving the arena registers positive signal.
  - `BASELINE_POP` -- frequency incumbent; held-out tails have train freq 0 -> ~floor (fit-independence sanity).
- Metric: filtered hits@10 (PRIMARY_K=10, matches the completed run's `POP_RELFREQ` h@10) on held-out queries.
- Fit config (FULL): k=24 (matches the completed FULL_CFG capacity knob), epochs=200, n_neg=64, batch=8192,
  neg_chunk=16, ckpt_every=20 (outage-resumable), seeds=[7,13,17], n_heldout_eval<=3000.
  Re-fit rationale: the completed gpu1024 run did NOT persist loadable codes; re-fit is faithful for the inductive
  question (the held-out metric is insensitive to seen-side fit sharpness; more epochs only sharpen SEEN geometry).
  HYPOTHESIZED@this prereg.

## Pre-reg bands (verbatim from the hand-off Anchor 1)

Let `margin = max(ONESHOT, ADDITIVE) held-out hits@10 - RANDOM_CODES held-out hits@10` (mean over seeds).

- HARD-PASS: `margin >= 0.05` AND ORACLE fires AND not broken -> real transferable relational signal to genuinely
  unseen entities; the inductive question is alive at scale. `verdict = HARD_PASS_INDUCTIVE_ENTITY_TRANSFER`.
- MIDDLE-BAND: `0.02 <= margin < 0.05` -> weak but nonzero; flag for a second seed/split.
  `verdict = MIDDLE_BAND_PARTIAL_ENTITY_TRANSFER`.
- HARD-FAIL: `margin < 0.02` -> memorized search, not reasoning (replicates the SR-code HARD_FAIL).
  `verdict = HARD_FAIL_MEMORIZED_NO_ENTITY_TRANSFER`. Deflated-prior expectation P=0.15-0.20
  (CITED@research note P_deflated summary).
- Gated INCONCLUSIVE if `n_heldout < 20` (`INCONCLUSIVE_TOO_FEW_HELDOUT`), if ORACLE does not clear RANDOM by
  `ORACLE_FIRE_MARGIN=0.10` (`INCONCLUSIVE_ORACLE_UNDERFIT` -- arena not answerable, cannot separate "no induction"
  from "underfit"), or if a control beats POP by > 0.03 (`BROKEN_TEST_CONTROL_BEATS_POP`).

## Four validity-preflight checks (declared; fired at self-test scale)

1. positive_control_passes: `ORACLE_TRANSDUCTIVE` recovers held-out tails and clears RANDOM by the fire margin ->
   the >=0.05 HARD-PASS bar is achievable when the entity code IS learned (bar not unwinnable/mis-directed).
2. metric_moves: held-out hits@10 moves across [RANDOM, ONESHOT, ORACLE] (not structurally frozen).
3. negative_control_fails_with_margin: RANDOM + CODEALIAS sit below ORACLE by the fire margin (>=2 repeats).
4. full_gates_exercised_at_selftest: `aggregate_and_verdict` runs on the planted per-seed, firing every fail-closed
   gate (arms_differ / oracle_fires / broken_test_guard / enough_heldout / band_gate).

## Self-test result (MEASURED@run 2026-07-12, planted dense-grid held-out-entity arena, single-thread CPU)

- ORACLE_TRANSDUCTIVE h@10 = 0.3333 (recovers held-out tails when codes learned) -> positive control fires.
- ONESHOT = RANDOM = CODEALIAS = 0.0263 (near chance -- held-out entity has a random code; no inductive transfer,
  the architecturally predicted behavior). ADDITIVE = 0.0614. POP = 0.0000 (at floor; fit-independence confirmed).
- oracle margin = 0.3070 (>> 0.10 fire margin); metric moves; arms differ (>=4 distinct sigs); vp_ok = True.
- verdict SELFTEST_PASS, elapsed 18.4s, deterministic (single-thread CPU pin).

## Compute architecture

class (c) MIXED. Storage SHARDED (per-entity phase codes; per-type relation rotations). device=cpu on
remote_cpu_queue. Fits are periodically fit-checkpointed (ckpt_every=20) so an outage/timeout resumes each arm
from its last epoch. Readouts query-chunked (the (nq,N) map is never materialized whole).

## SCHEMA-VET fields

- cell_chunked: false (in-process 3-seed loop, remote_cpu; each fit outage-resumable via FitCheckpoint + per-seed
  write_partial). start_marker_written: true. crash_diagnostic_present: true. heartbeat_present: true.
  defensive_error_checking: passed_all_4_patterns.
- final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
- arms_differ_verified: true (>=4 distinct sigs asserted per seed). arms_differ_exempted: none.
- cardinality_ok: true (EXPECTED_N_UNITS = n_seeds; cardinality-breach verdict wired).
- crlb_n/a: "chance hits@10 = 10/N ~ 0.0004 at N~25.7k; HARD-PASS 0.05-above-random is achievable (ORACLE
  positive control demonstrates recovery when the code exists); discriminator_reachability OK."
- baseline_in_band: ORACLE positive control must fire above RANDOM+margin; RANDOM/POP near the 10/N floor.
- discriminator survives scale: analytical (B) -- per-entity embedding tables cannot encode an unseen entity by
  construction (GraIL/NBFNet), so the null persists at ANY N; ORACLE-fires proves the metric can move at scale.
- calibration_check: adaptive_with_discriminator_gate (HELDOUT_ENTITY_FRAC / ORACLE_FIRE_MARGIN pre-registered,
  not tuned on real data; the planted self-test verifies ORACLE recovers when codes are learned).
- progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints).
- HP_SCOPE: the inductive HARD-PASS gate applies to ONESHOT_ROTATE / ADDITIVE_TRANSE only. ORACLE = positive
  control (must fire); RANDOM/CODEALIAS = must-not-clear-bar controls; POP = fit-independence sanity.

## Dispatch

`bash tools/orchestrator/queue_add.sh remote_cpu_queue heldout_entity_inductive_probe_cskg_v1 \
  experiments/exp_heldout_entity_inductive_probe_cskg_v1.py \
  preregs/2026-07-12_heldout_entity_inductive_probe_cskg_v1.md 14400`
