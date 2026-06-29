# Pre-registration: substrate_pc_encoder_family_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** USER directive (Research, 2026-06-28) — first systematic COMPONENT-SUBSTITUTION phase diagram. Prior phase diagrams (PC v1/v2/v2.1/v2.2; capacity multi-bank; lock-in amp v2; sequence-binding K-cliff; multihop v4) all sweep CONFIG PARAMETERS within a FIXED mechanism. We don't know if the current mechanism choice is best or first. This cell starts at the most load-bearing lever: **encoder family**, on the most-characterized primitive: **pattern completion**.

## Anchor

`substrate_pc_encoder_family_phase_diagram_v1_seed_{7,13,19}` (3 sibling files; chunked-per-seed per USER 2026-06-28).

Shared core: `experiments/_substrate_pc_encoder_family_phase_diagram_v1_core.py`.

## Routing

- **Smoke queue:** local (laptop CPU; `.venv/Scripts/python.exe` direct invocation, then `local_cpu_queue` for traceability)
- **Full queue:** **overnight_queue** (GPU; 4 encoders x 120 inner pts x 1 seed each is matmul-heavy at N=8192; complex64 FHRR matmul especially benefits from CUDA)
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes through Orchestrator (request via SendMessage post-smoke).

## Why this cell exists (the gap)

Substrate has ~30 levers across ~9 categories (encoder, binding, cleanup, routing, schema, sequence, temporal, refuse, storage). Most chain-grade primitives — TRACE, ultrametric clustering, multi-bank capacity, multihop, sequence-binding, refuse-gate, lock-in amp — have been characterized with a **bipolar-binary** encoder (`+/-1` codebook) as a fixed default. This default is **inherited from CERT 591 (Skunkworks)** and never independently audited as "best" for the downstream primitive.

PC v2.2 (commit `2daf9b55`) gives us a clean operating zone: corruption cliff 0.461 (N=2048) — 0.486 (N=16384), 9 dense MB pts in [0.46, 0.50], no silent saturation. This is the **ideal baseline** for component substitution: same primitive, same regime, change encoder.

**Cross-domain prior:** prior session noted "sparse-bipolar 20-300x bundle lift" (`reference_operational_findings_2026-06-23_late_session.md`). HRR / FHRR are brain-grounded (FHRR is biologically-plausible Plate-Eliasmith complex representation). All four families have published reasons to dominate in specific regimes.

## Encoder families (the OUTER axis)

Four families, each with same `(M_items, N_dim)` codebook footprint but distinct representation:

| Family | Codebook elements | Score (Q vs X) | Corruption model |
|--------|-------------------|----------------|------------------|
| `binary_bipolar` | `{-1, +1}^N`, dense | `Q @ X.T` real | bit-flip fraction `c` |
| `hrr_real` | `N(0, 1/N)^N`, dense real | `Q @ X.T` real | Gaussian noise with norm-matched magnitude |
| `fhrr` | unit-modulus complex `exp(i*phi_k)` in `C^(N/2)`, dense | `Re(Q . conj(X))` | phase perturbation of magnitude `2*pi*c` to fraction `c` of bins |
| `sparse_bipolar` | `{-1, 0, +1}^N`, density `s/N=0.05` | `Q @ X.T` real | bit-flip on the ACTIVE (nonzero) bits, fraction `c` |

All four use the **same iterative softmax-Hopfield cleanup** with `beta=8.0`:
```
Q_{t+1} = sign_op( softmax(beta * score(Q_t, X)) @ X )
```
where `sign_op` is family-specific (sign for bipolar/sparse; identity for HRR-real with L2-normalize after; unit-modulus normalize for FHRR phase).

**Why this is apples-to-apples:** corruption_frac `c` is defined per-encoder to produce EQUAL expected initial cosine `1 - 2c` between corrupted query and source. This is the **information-theoretic** common axis. Cleanup pipeline, score function, M_items, N_dim all matched. Only the encoder family differs.

**Selftest validation:** for each encoder, verify `E[cos(Q_0, source) | c]` is in `[1-2c - delta, 1-2c + delta]` for `delta=0.05`, `c in {0.1, 0.3, 0.5}`, N=2048, M=50, seed=7. If any family fails this calibration, the cell HARD_FAILs at selftest before any phase points run.

## Sweep axes

| Axis | Values | Count |
|------|--------|-------|
| encoder_family (OUTER) | {binary_bipolar, hrr_real, fhrr, sparse_bipolar} | 4 |
| N (inner) | {2048, 8192} | 2 |
| corruption_frac (inner) | {0.20, 0.35, 0.45, 0.475, 0.50} | 5 |
| cleanup_iters (inner) | {1, 5} | 2 |

`M_items=300`, `beta=8.0`.

**Cardinality FULL per seed:** `4 * 2 * 5 * 2 = 80` phase points per seed.
**Cardinality SMOKE per seed:** `4 * 1 * 3 * 1 = 12` corner points per seed (N=2048; corruption ∈ {0.20, 0.45, 0.50}; iters=1).

Seeds: 7, 13, 19 (chunked per-seed; 3 sibling files).

Note: inner grid is intentionally tighter than PC v2.2's 180-pt diagram (15 corruption x 4 N x 3 iters) because the OUTER axis (encoder x4) multiplies cost 4x. 80 pts per seed x 3 seeds = 240 grid points total at FULL — chosen to fit overnight GPU budget while spanning enough regimes to discriminate per encoder.

## Hypothesis

**H1 (PRIMARY): Encoders WILL differ in cliff location AND/OR slope.**
- Prediction per encoder (HYPOTHESIZED@):
  - `binary_bipolar`: cliff at ~0.486 (N=8192), matches PC v2.2 (POSITIVE CONTROL — must reproduce)
  - `hrr_real`: cliff shifts LEFT (lower corruption tolerance) — Gaussian real codes have lower per-bit information; predicted cliff ~0.40-0.45 at N=8192
  - `fhrr`: cliff at ~similar location to bipolar (~0.48) but possibly **steeper** (phase coherence either preserved or destroyed)
  - `sparse_bipolar`: cliff shifts RIGHT (higher corruption tolerance) — sparse codes have **higher minimum Hamming distance** between codewords, so noise-floor lower; predicted cliff ~0.50-0.52 at N=8192. This matches the "20-300x bundle lift" prior observation (sparse codes are more crosstalk-resistant).

**H2 (regime-mapping): Different encoders WIN in different regimes.**
- If H1 holds: `sparse_bipolar` wins high-corruption regime; `binary_bipolar` wins easy regime (high saturation); `fhrr` may dominate at intermediate corruption due to phase-cleanup geometry; `hrr_real` likely DOMINATED in all PC regimes (this would be the "negative" finding — useful for downstream cells that should NOT default to HRR for retrieval).

**H3 (positive-control): `binary_bipolar` at (N=8192, c=0.475, T=5) reproduces PC v2.2 cited HP-recall ~0.928 +/- 0.05.** If this control fails, the encoder-comparison harness is broken; cell aborts with CONTROL_FAIL.

**H4 (null): All 4 encoders identical within +/- 0.05 top1 at EVERY (N, c, T) phase point.** If H4 holds, encoder choice doesn't matter for PC — would be a load-bearing **negative** finding (downstream cells free to pick any encoder; encoder is NOT a discriminating lever for PC).

**H5 (dominance): One encoder strictly dominates all others at all phase points.** If H5 holds, would be the strongest finding — substrate should switch default. Most likely candidate is `sparse_bipolar` per prior session observation.

## Discriminator: per (encoder, regime) vs random-floor

For each (encoder, N, c, T) phase point: ARM_MECHANISM (the encoder's PC top1) vs ARM_RANDOM (fresh-random codebook entry instead of corrupted source). Random ~ 1/M = 0.0033 ~ FLOOR.

**Per-encoder discriminating_fraction prediction (HYPOTHESIZED@):**
- binary_bipolar: ~0.40 (16/80 = 20% PASS-or-MB; matches PC v2.2 12% rate adjusted for tighter grid)
- hrr_real: ~0.25 (lower; encoder predicted weaker)
- fhrr: ~0.35
- sparse_bipolar: ~0.45 (higher; encoder predicted stronger)

**Discriminating_fraction (overall) >= 0.30** = pre-reg PASS threshold = (>= 24/80 pts per seed in HARD_PASS+MIDDLE_BAND across all encoders).

## Pre-reg bands (per-point; LOCKED at module init)

| Tier | top1_mechanism | Discriminator (mech - random) |
|------|----------------|-------------------------------|
| SATURATED | >= 0.95 | record but down-weight (Skunkworks Q-rule) |
| HARD_PASS | [0.80, 0.95) | >= 0.50 |
| MIDDLE_BAND | [0.50, 0.80) | >= 0.30 |
| HARD_FAIL | (0.10, 0.50) | mechanism breaking |
| FLOOR | <= 0.10 | substrate at chance |

## Cell-level verdict (FULL, per seed)

- **HARD_PASS_ENCODER_DISCRIMINATION**: cardinality_ok + arms_differ AND (per-encoder hashes also differ pairwise: at least 2 of the 6 encoder-pair-hash comparisons must differ to claim "encoder family matters") AND >= 24/80 points in HARD_PASS+MIDDLE_BAND AND positive control reproduces (binary_bipolar @ N=8192, c=0.475, T=5: top1 >= 0.50)
- **MIDDLE_BAND_ENCODER_DIFFERS_BUT_LOW_DISC**: arms_differ + encoder-pair hashes differ but disc_pts < 24 (encoders measurably different but not enough cliff-edge coverage)
- **MIDDLE_BAND_NULL_ENCODER_INVARIANCE**: arms_differ but ALL encoder-pair hashes IDENTICAL (H4 confirmed — encoders don't matter for PC; cell still useful as honest-negative; routes to Research as "encoder NOT a discriminating lever for PC")
- **HARD_FAIL_CARDINALITY_BREACH**: observed != 80
- **HARD_FAIL_ARMS_IDENTICAL**: substrate and random hashes match for any encoder (mechanism not working)
- **HARD_FAIL_CONTROL_FAIL**: binary_bipolar positive control doesn't reproduce PC v2.2 (test rig broken; halt before any framing claims)

## Cell-level verdict (SMOKE)

- **HARD_PASS_SMOKE**: 12/12 corner points + arms_differ + 4 distinct encoder hashes (META_RULE_AF) + positive control (binary_bipolar @ N=2048, c=0.45) shows top1 >= 0.50 (cliff is observable at smoke scale)
- **HARD_FAIL_SMOKE_ENCODER_COLLAPSE**: 2+ encoders produce identical hashes at smoke (means same codebook generated -- mechanism bug)
- **HARD_FAIL_SMOKE_CONTROL_FAIL**: positive control fails at smoke
- **HARD_FAIL_SMOKE_NO_DISCRIMINATION**: zero cells in HARD_PASS+MIDDLE_BAND tiers at smoke (substrate broken at smoke regime)
- **HARD_FAIL_SMOKE_DISCRIMINATOR_FAILS_SCALE** (USER 2026-06-26): smoke at N=2048 shows zero encoder cliff-edge values in [0.10, 0.95] for c=0.45 (encoders saturated or floored — abort FULL since 4x compute means tighter grid)

## Calibration selftest (encoder-corruption equivalence)

For each encoder ∈ {binary_bipolar, hrr_real, fhrr, sparse_bipolar} at N=2048, M=50, seed=7:
- For c in {0.10, 0.30, 0.50}: build codebook X; corrupt 50 items at c; compute mean cosine(Q_corrupted, source); assert in `[1 - 2c - 0.10, 1 - 2c + 0.10]`.

If ANY encoder fails calibration, selftest exit 1 with verdict_msg naming the failing (encoder, c). This catches the "encoder corruption-model not equivalent across families" bug at selftest time, BEFORE any cell-level phase points run.

## CRLB / noise-floor prediction (META_RULE_AG)

For all encoders with effective N_dim (bipolar/sparse use N; fhrr uses N/2 complex pairs = N real degrees of freedom; hrr_real uses N), noise floor for M_items random patterns:

```python
noise = sqrt(2 * log(M) / N_eff)
cliff_1step = 0.5 * (1 - noise)
# N=2048 M=300 cliff ~ 0.464; N=8192 M=300 cliff ~ 0.482
```

Per-encoder cliff prediction stamps `crlb_1step_cliff_prediction` in metrics.

## Calibration: sparse_bipolar density

`s/N = 0.05` (5% nonzero). For N=2048 this means s=102 nonzero bits per codeword. Sparse encoders have lower effective dimension but higher per-active-bit information density. Corruption frac `c` for sparse_bipolar = "flip c fraction of the ACTIVE bits", which is fewer bit-flips per query but proportionally more damaging to the signal. This keeps cosine(Q_corr, source) ~ `1 - 2c` matched.

## Arms per point (META_RULE_AF)

Each (encoder, N, c, T) point logs TWO arm results:
1. `ARM_MECHANISM` — encoder's pattern completion top1
2. `ARM_RANDOM_FLOOR` — fresh-random codebook entry instead of corrupted source, same cleanup pipeline; floor ~1/M

**arms_differ_sha256** per encoder: SHA-256(json(mech.recall_per_point)) != SHA-256(json(random.recall_per_point)). All 4 encoder arms must differ from their random.

**encoder_pair_hashes** (META_RULE_AF extension): SHA-256(json(top1_per_point_for_encoder_X)) for each encoder. All 4 hashes computed; for chain-grade discrimination claim, at least 2 of the 6 pairs must differ. If ALL 4 identical, that's the H4 NULL finding (encoder doesn't matter).

## Cardinality OK (META_RULE_H)

```
SMOKE: EXPECTED_N_UNITS = 12 (4 encoders x 1 N x 3 corruption x 1 iters x 1 seed)
FULL : EXPECTED_N_UNITS = 80 (4 encoders x 2 N x 5 corruption x 2 iters x 1 seed)
```

HARD_FAIL if observed != expected (silent-drop guard, USER 2026-06-26 META_RULE_J).

## GPU mandate (Fix #24)

- `import torch` at TOP of file (PROT-020 routing-gate)
- `DEVICE = torch.device("cuda")` preferred; CPU fallback ALLOWED for smoke (laptop is CPU-only; smoke is gateable on CPU)
- **FULL on CPU REFUSED** unless `HDLAB_QUEUE=local_cpu_queue` env explicit-route (Fix #24)
- All four encoder pipelines vectorized: codebook materialized once on DEVICE per (encoder, N, seed); cleanup is batched matmul throughout
- complex64 used for FHRR; float32 for bipolar/HRR/sparse
- Per-point peak_mem_mb logged
- GPU util target: `peak_mem_mb / 50` >= 0.5 for 90% of points (FHRR + N=8192 has 2x complex storage; should be well-utilized)

## Chunked-per-seed architecture

3 sibling files: `experiments/exp_substrate_pc_encoder_family_phase_diagram_v1_seed_{7,13,19}.py`.
Shared core: `experiments/_substrate_pc_encoder_family_phase_diagram_v1_core.py`.

Per-seed checkpointing via `experiments/_seed_checkpoint.py` (PROT-021 config-mismatch guard ON; META_RULE_H_ANCHOR check ON).

4 defensive patterns (USER 2026-06-28 hardening):
1. start_marker: STARTED metrics written before any heavy work
2. crash-diag: outer try -> import-crash sentinel with full traceback
3. per-unit checkpoint: write_partial_key per seed
4. heartbeat: per-phase-point flush print (per-encoder per-point)

## Disciplines (mandatory)

- META_RULE_AC: arms differ by SHA-256 (mechanism vs random; per-encoder)
- META_RULE_AE: pre-reg bands LOCKED at module init
- META_RULE_AF: 4 encoder arms produce distinct hashes (else encoder substitution didn't happen — mechanism bug)
- META_RULE_AG: per-encoder per-point CRLB / overlap-floor pre-validation in Python
- META_RULE_AH: tag every number MEASURED@ | HYPOTHESIZED@ | THEORETICAL@
- META_RULE_AN: empirical baseline if cone-formula uncertain (not applicable here; CRLB formula is canonical for random codes)
- META_RULE_H: cardinality_ok mandatory (80 full, 12 smoke)
- META_RULE_J: no silent except; halt on any unit exception
- META_RULE_L: band-floor results = MIDDLE_BAND not HARD_PASS
- META_RULE_M-S (USER 2026-06-24): production-scale calibration applied; verify-referent on per-encoder-discriminator; basis-vs-use-case (labels at readout, NOT in basis); anisotropy-hurts-retrieval (sparse_bipolar is one rescue); 1.000 results suspect (saturation flag mandatory)
- Functional-requirement decomposition: pattern completion = retrieve clean from corrupted (single primitive, no composition; encoder is the substituted COMPONENT)
- Substrate-as-canonical query-first: PC v1/v2/v2.1/v2.2 chain (commit `2daf9b55`) reviewed; this cell extends by SUBSTITUTING the encoder, not the cleanup
- DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26): smoke at N=2048 with cliff-edge corruption (0.45) — if substrate saturated at smoke at smaller N, full grid at N=8192 would saturate harder; abort if smoke shows no cliff
- BAND-FLOOR-IS-MIDDLE-BAND (USER 2026-06-26): clearing 24-MB threshold AND positive control reproducing AND >= 2 encoder-pair-hashes differing — all three required for HARD_PASS; otherwise MIDDLE_BAND
- Honest-downward classification per encoder (USER 2026-06-26): if one encoder dominates all regimes, that's strong; if all 4 cluster within +/- 0.05, that's H4 NULL (honest negative)

## Positive control

`binary_bipolar` at (N=8192, c=0.475, T=5) must reproduce PC v2.2 corruption-cliff measured value top1 >= 0.50 (PC v2.2 evidence: top1=0.55-0.65 at this point at seed 7, MEASURED@ commit 2daf9b55). If control fails: cell HARD_FAILs with verdict CONTROL_FAIL — test rig broken.

## Composition edges (substrate atomization context)

- This cell uses the existing CHAIN-GRADE primitive `iterative_attractor` (modern-Hopfield softmax cleanup) as the FIXED cleanup after encoder. SHAPE_MATCH: each encoder's output shape (M, N_eff) feeds the cleanup unchanged.
- Encoder is the COMPONENT being swept; cleanup primitive is the COMPOSED-WITH-it primitive (unchanged across arms).
- Downstream atomization: HARD_PASS_ENCODER_DISCRIMINATION promotes the winning encoder for `pattern_completion` ROLE; informs downstream cells' default-encoder choice.

## ETA

Per-point on GPU (N=8192, M=300, fhrr complex64 most expensive): ~5-10s. 80 pts/seed * ~8s = ~10-15 min science + 30 s init = ~15-20 min/seed FULL on GPU.

Per-point on CPU (smoke; N=2048, M=300): ~1-2s. 12 pts/seed * 1.5s = ~20s science + 10s init = ~30-45s/seed SMOKE on CPU.

Timeouts:
- SMOKE: 600 s (10 min margin per seed; budget 30-45s expected)
- FULL: 2400 s (40 min margin per seed; budget 15-20 min expected)

## Substrate-only decode gate

`_LLM_CALL_COUNTER[0] == 0` asserted at exit (no LLM calls in this cell; pure substrate mechanism).

## Smoke gate (MUST pass before FULL dispatch)

1. 12 corner points all ran (no silent except per META_RULE_J)
2. cardinality_ok: observed_n_units == 12
3. arms_differ_sha256.differ == True for ALL 4 encoders (each encoder's mechanism distinct from its random floor)
4. encoder_pair_hashes: 4 distinct encoder mechanism hashes (META_RULE_AF — encoder substitution actually happened)
5. positive_control: binary_bipolar @ N=2048, c=0.20 shows top1 >= 0.80 (easy regime saturates as expected for bipolar)
6. cliff observable: at least 1 encoder shows top1 in [0.10, 0.95] at c=0.45 (cliff-edge regime survives at smoke scale)
7. discriminator_pre_check: at least 1 point per encoder in HARD_PASS/MIDDLE_BAND/HARD_FAIL transition band (NOT all SAT or FLOOR per encoder — encoder either spans regime or hits floor everywhere; floor-everywhere encoder is honest negative for that encoder, not a HARD_FAIL of cell)

If gates 1-6 fail, FULL dispatch is HARD-blocked. Gate 7 is informational — encoder failing all transitions at smoke means full grid will likely show encoder is dominated in all regimes (still useful finding; cell ships).

## Encoder-family routing tier classifications

Per-encoder downstream verdict (informational; cell aggregator stamps these):
- DOMINANT_ENCODER: top1_mean > 0.10 above all other encoders averaged across all phase points (strong substitution case for downstream)
- COMPETITIVE_ENCODER: top1_mean within +/- 0.05 of best encoder
- DOMINATED_ENCODER: top1_mean > 0.10 below best encoder (downstream should NOT default to this encoder for PC)

## Outputs

`data/exp_substrate_pc_encoder_family_phase_diagram_v1_seed_{7,13,19}/metrics.json` with:
- per_seed phase_map (list of dicts; one per phase point)
- per_encoder_summary (4 entries; tier classification + top1_mean + cliff_locator)
- encoder_pair_distinctness (6 pair-comparisons; any-differ flag)
- positive_control_result (top1 at binary_bipolar @ N=8192, c=0.475, T=5)
- crlb_predictions_1step (per (encoder, N))
- arms_differ_sha256 (per encoder)
- tier_counts per encoder + overall

Atomization candidates (post-Skunkworks landed-VET):
- if HARD_PASS_ENCODER_DISCRIMINATION: SUBSTRATE_ENCODER_FAMILY_DISCRIMINATING_FOR_PC + WINNING_ENCODER_FOR_PC (whichever encoder dominates)
- if MIDDLE_BAND_NULL_ENCODER_INVARIANCE: ENCODER_NOT_DISCRIMINATING_LEVER_FOR_PC (downstream cells free to pick any)
- if HARD_FAIL: NEEDS-RERUN with smoke-gate-specified fix
