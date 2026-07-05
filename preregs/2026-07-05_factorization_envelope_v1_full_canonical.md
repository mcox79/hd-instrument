# Pre-registration: factorization_envelope_v1 (FULL / envelope-mode canonical run)

Date: 2026-07-05
Cell: experiments/exp_factorization_envelope_v1.py (committed; smoke HARD_PASS)
Queue: remote_cpu_queue (CPU-only cell: DEVICE=cpu, torch.set_num_threads(8))
Run mode: envelope (default, i.e. invoked WITHOUT --smoke)

## Purpose

Decisive GO / NO-GO gate for the #1 build priority: a substrate-native
generation decoder. Measures the resonator factorization envelope (the inverse
of the concept encoder) across three axes at substrate scale N=8192:
  F = factors per term, V = per-factor vocab, D = composition depth.
Codebooks are CLEAN iid bipolar vectors, so the measured envelope is the honest
UPPER BOUND (real correlated encoder fillers can only reduce it).

## Pre-registered verdict bands (BAKED INTO THE CELL - NOT re-invented here)

These are the cell's own thresholds, from verdict_from_results()
(experiments/exp_factorization_envelope_v1.py lines 258-276) and the header
comment block. This prereg only points at them; it does not introduce new bands.

- GO: GEN_svo_1k (F=2, V=1024, D=3, N=8192, RESTARTS=16) mean term-recovery
  >= 0.90 (SUCCESS_THRESH=0.90). Message: "generation-viable: S/V/O recovery
  >= 0.90 at N=8192 high-energy".
- NO_GO: B_V64_hi (F=2, V=64, D=2, N=8192, RESTARTS=16) mean term-recovery
  < 0.50 (cliff too early even at the easiest vocab). Checked FIRST (dominant).
- MIDDLE_BAND: neither GO nor NO_GO. "partial envelope: usable for small
  propositions; chunking needed beyond".

## Grid (built by build_grid(smoke=False); 28 configs)

- Sweep A (factors F): F in {2,3,4} at V=256, D=2, N=8192; each hi (R=16) + lo (R=1).
- Sweep B (vocab V): V in {64,256,1024,4096} at F=2, D=2, N=8192; hi + lo.
- Sweep C (depth D): D in {1,2,3,4,6} at F=2, V=256, N=8192; hi + lo.
- Generation points: GEN_svo_1k (V=1024, D=3), GEN_svo_4k (V=4096, D=3), F=2, R=16, N=8192.
- N-scaling reference: N in {1024,4096} at F=2, V=256, D=2, R=16.
Per config: SEEDS=(7,13,19) x TRIALS=10. RESTARTS=16, MAX_ITER=60 (early-stop on fixed point).

## Discriminator / scale discipline

- Discriminator = the cliff itself. Grid is designed to SPAN success -> failure
  at full N=8192 (the substrate compositional default; deliberately NOT smoked at 2048).
- CARD_OK: sweep axes F/V/D each span >= 3 distinct cardinalities at fixed N=8192.
- R=1 (single-shot) vs R=16 (high-energy) reported side-by-side so a single-shot
  cliff is not mistaken for a fundamental wall.
- Analytic random baseline per term = 1 / V^F (THEORETICAL@combinatorial).

## Smoke gate (already PASSED, HARD)

data/exp_factorization_envelope_v1/metrics.json (run_mode=smoke, ts 2026-07-05T04:30:20Z):
easy_D1=1.000 (must>=0.99), easy_D2=1.000 (peel-off, must>=0.90),
hard_cliff=0.000 (must<0.60). Resonator correctness + peel-off + cliff all confirmed.

## Atomicity / provenance

Final metrics.json written via tmp_replace (write metrics.json.tmp then os.replace)
per META_RULE_AH. Start marker + crash-metrics handlers present. Algebra =
bipolar BSC elementwise product (substrate committed algebra, wave14e/wave14b).

## Note

This is a RE-RUN of the committed cell for the canonical remote-queue landing,
not a redesign. Algebra, grid, and bands are unchanged from the committed cell.
The prior smoke was a local gate; this prereg governs the FULL envelope landing.
