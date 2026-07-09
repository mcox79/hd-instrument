# Pre-registration: same-different (identity / relational-match) BAKE-IN primitive

- Anchor: `exp_same_different_bakein_relational_tier_v1`
- Cell: `experiments/exp_same_different_bakein_relational_tier_v1.py`
- Date: 2026-07-09
- Track: innate-scaffolding bake-in #3 (joins dual-number MM + object-permanence MM)
- Source drill: `notes/research_same_different_identity_bakein_primitive_2x_2026-07-09.md`
- Framing: architectural-support / mechanism-analog (NOT task-analog), like the two prior bake-ins.
- Prior-work check (substrate KB, cosine): top hits Gentner-SME structural-alignment gap /
  "structural identity" / relational-memory theory at cosine ~0.31 (adjacent, relational-structure),
  NONE a same-different bake-in cell -> genuinely novel, not a rediscovery.

## Question

Do TWO baked, zero-training, by-construction same-different mechanisms operate on the substrate's
quasi-orthogonal codebook and GENERALIZE to NOVEL held-out items?
1. ITEM-LEVEL free comparator (fixed cosine threshold) -- the FLOOR (sanity; do NOT over-claim).
2. RELATIONAL-TIER unbind-then-compare (`R = bind(A1, inverse(A2))`) -- the HEADLINE, expected
   capacity-limited as composition/scene depth grows (feature-entanglement / structural-semantic
   conflation; the literature's honest ceiling).

## Arms

- `item_tier` (FLOOR): fixed cosine threshold TAU_ITEM=0.30 on codebook vectors. same=(X,corrupt(X,p=0.20)),
  diff=(X,Y). Accuracy on SEEN (construction-pool) vs NOVEL (fresh) items. No training -> the seen-vs-novel
  GAP is the discriminator (also a codebook-leakage detector).
- `relational_tier` (HEADLINE): extract `R = bind(A1, inv(A2)) = F*(F*T) = T` (bipolar self-inverse, exact)
  per observed pair; bundle the queried relation with D-1 distractor relations into a depth-D scene;
  compare two scenes sharing T_query (same-relation) vs independent relations (different-relation null).
  Discriminator `z(D) = (mean cos_same - mean cos_diff)/std cos_diff`. Swept over composition depth D.
- `scrambled_control` (MUST-FAIL): instances built with A2 = independent random G (no relation) ->
  extracted R random -> scenes share no relation -> z MUST stay at chance. If it clears z>3, the
  discriminator measures an artifact (VacuousSmokeError at smoke).

`arms_differ_verified: true` (smoke: item-comparator pair vs relational scene bit-distinct; MEASURED True).
`arms_differ_exempted: []`.

## Discriminator bands (author-picked BEFORE running; both bands)

Relational HEADLINE (z on NOVEL fillers):
- HARD_PASS: `z_same(D_LOW=8) >= Z_PASS=5.0` (strictly above the z>3 floor + margin; META_RULE_L) AND
  graceful degradation (`z(D_min=4) > z(D_max=48)` AND `z(D_max=48) < Z_FLOOR=3.0`, proving a real
  ceiling not saturation) AND material novel generalization (`z_novel(D8) >= 0.70 * z_seen(D8)`) AND
  scrambled control at chance (`z_scr(D8) < Z_FLOOR`) AND item sanity holds.
- HARD_FAIL: `z_same(D_LOWEST=4) < Z_FLOOR=3.0` on NOVEL items (baked unbind-compare gives NO abstract
  2nd-order same-different) OR control leak (`z_scr(D8) >= Z_FLOOR`) OR item sanity fails
  (`HARD_FAIL_ITEM_SANITY`; codebook not quasi-orthogonal -> everything contaminated).
- MIDDLE: clears low-depth z but no crossing (all depths z>3 -> saturation concern) OR novel-gen
  below 0.70 but still above chance.

Item FLOOR (sanity gate, not headline): `item_ok = acc_seen>=0.95 AND acc_novel>=0.95 AND gap<=0.02
AND diff-pair FP<=0.02`.

Cell verdict: HARD_PASS = item_ok AND relational HARD_PASS (>=majority seeds); HARD_FAIL = item fail OR
relational HARD_FAIL (control-leak OR >=majority seeds); else MIDDLE_BAND.

## Feasibility / reachability (crlb_n/a)

- `crlb_n/a`: "the discriminator is a z-score of relational cosine vs a quasi-orthogonal null, not a
  Cramer-Rao noise-floor estimate."
- `discriminator_reachability: true`. THEORETICAL floor `z(D) ~ sqrt(N)/D` at N=8192 (sqrt(N)=90.5):
  D4=22.6, D8=11.3, D16=5.66, D24=3.77, D32=2.83, D48=1.89 -> Z_PASS=5.0 reachable at D8 (11.3>>5.0);
  the fail-side (z<3) also reachable at D32/D48. Both bands physically attainable.
- Item-tier: same-cos ~ 1-2p = 0.60 >> TAU=0.30; diff-cos ~ 0 +/- 1/sqrt(N)=0.011 << TAU -> acc ~ 1.0,
  gap ~ 0 by construction (no training). THEORETICAL.

## SCHEMA-VET gates

- `cardinality_ok: true`. EXPECTED_N_UNITS = n_seeds(3) x n_D(6) = 18 (seed,D) cells; verdict counts
  `n_cells`; `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if short. Smoke: 6/6 cells (1 seed) MEASURED.
- `effective_vs_nominal_parameter_audit`: swept param = D (composition depth); the primitive under test
  (unbind-then-compare over a depth-D bundle) experiences D directly as the bundle size.
  `sweep_alignment_verdict: ALIGNED`.
- `bracket_includes_discriminating_band`: predicted z per D straddles the z=3 threshold (D16=5.66 and
  D24=3.77 clear; D32=2.83 and D48=1.89 fail). Informative-crossing points (z within a factor of the
  threshold, not saturated z>>10 nor deep-chance): D16,D24,D32,D48 = 4/6. `discriminating_fraction: 0.67`
  (>= 0.30). MEASURED smoke z_by_depth = {4:21.98, 8:12.35, 16:5.51, 24:3.51, 32:2.91, 48:1.75}.
- `composition_edges`: single primitive (unbind + bundle + cosine); no primitive->primitive adapter edge.
  `SHAPE_MATCH` (all internal to one VSA op family).
- `positive_control_arms`: item-tier "same" pair reproduces cos ~ 1-2p (bipolar self-inverse) at the test
  regime (N=8192); relational z reproduces THEORETICAL sqrt(N)/D within 35% (self-test T2: z(D8)=11.22 vs
  11.31; z(D16)=5.78 vs 5.66). `regime_extension_audit: SHAPE_MATCH` (synthetic clean bipolar, no drift).
- `functional_requirements`:
  1. "tell two items apart when seen side-by-side" -> fixed cosine threshold on quasi-orthogonal codebook
     (item tier; free by construction).
  2. "tell two relations apart (relation-between-relations)" -> unbind-then-compare relation extraction
     (relational tier; the individuate-then-expose-only-relation-value minimal mechanism).
- `calibration_check: default_ok_for_this_regime` (clean synthetic quasi-orthogonal bipolar; analytical
  z = sqrt(N)/D; no adaptive tuning).

## Cell-hardening

- `cell_chunked: false` (multi-seed handled in one cell via `_seed_checkpoint` per-seed partials + resume;
  3 seeds, small per-seed wall ~ tens of s; single-seed-per-cell not warranted).
- `start_marker_written: true`; `crash_diagnostic_present: true` (Exception -> CELL_CRASHED + traceback,
  atomic tmp+replace; `except SystemExit: raise` before `except Exception`; no BaseException / bare except
  -- grep-gate clean); `heartbeat_present: true` (CellHeartbeat interval 30s); `defensive_error_checking:
  "passed_all_4_patterns"`.
- `final_metrics_atomicity: "tmp_replace"` (write_metrics atomic + per-seed write_partial).
- `progress_logging: "print_flush_true"` (per-seed [progress] lines flush=True; timeout < 1800s so not
  mandatory, included as good practice).
- `run_mode` wired: `--self-test` / `--smoke` / default full; smoke MEASURED run_mode=smoke on disk.

## Compute architecture

- Class: **(b) sequential-CPU with justification**. Cell IS validating substrate primitives with a
  bit-identical numpy reference (bind = elementwise mul, self-inverse); per-seed wall is small
  (smoke 1 seed M=120 = ~7s wall; FULL 3 seeds M=400 estimated ~60-100s); matches the sibling bake-in
  cells (object_permanence, dual_number) which shipped numpy-CPU. The distractor-relation sum is
  vectorized (binomial draw) -- no Python per-item loop over depth. Not a GPU/torch cell, so it is
  ROUTING-INELIGIBLE for overnight_queue (GPU gate rejects numpy-only scripts).
- Storage strategy: **sharded / no-store** -- codebook vectors are individuated by construction
  (quasi-orthogonal); the depth-D bundle is the composition being STRESS-TESTED (the object of the
  D-sweep), not a persistent store. No bundled-store retrieval.

## Routing

- Target queue: **remote_cpu_queue** (marsh@home CPU). Rationale: keeps the cell off the busy local
  `cpu_runner_0` (which holds the grounding probes) per task; numpy-only cell is GPU-ineligible so
  overnight_queue is out; N=8192 < 16384 large-N warn threshold. Remote SCP ship handed to orchestrator
  (exp_dev does not run the remote SCP path per 2026-07-08 lock).

## HYPOTHESIZED outcome (deflated per drill P_deflated)

- Item tier: near-trivial PASS (P~0.55; the FLOOR). HYPOTHESIZED@this prereg.
- Relational tier: clears z>3 at low depth, crosses below z>3 near D~24-32, HARD_PASS with an honest
  composition-depth ceiling mapped (P~0.30; capacity-limited). HYPOTHESIZED@this prereg.
- Smoke MEASURED (1 seed, M=120, full N): HARD_PASS; z_low(D8)=12.35, z_dmax(D48)=1.75, crossing between
  D24(3.51)/D32(2.91), scrambled control |z|<0.12 all depths, item acc 1.0/1.0 gap 0.
  MEASURED@data/exp_same_different_bakein_relational_tier_v1_smoke/metrics.json
