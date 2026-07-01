# Pre-registration: substrate_cleanup_family_WM_K_cliff v1 (ARM4 / B3K3 design)

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M)
**Trigger:** Research phase-diagram gap analysis a36917be
(`notes/research_phase_diagram_gap_analysis_next_cells_2026-07-01.md` sec 1);
Axis-F cleanup-family at WM K-cliff scale, CG=0.55, HIGH payoff, 5x-drill
escalation eligible if HP.

## Anchor and file naming

Task literal name: `cleanup_family_WM_K_cliff_v1`.
Anchor slug (avoids data-dir collision): `substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_seed_{7,13,19}`.

**Collision rationale** — two prior cells share the "v1"/"v1p1" slug:
- v1 (2026-06-30): N=8192, num_banks=16, 5-arm set (no_cleanup + classical +
  modern + iterative + kNN); OOM'd on GPU at cleanup_no_cleanup 1.91 GiB alloc.
- v1p1 (2026-06-30): N=4096, num_banks=8 memory-fit retry; MIDDLE_BAND
  (pred_differ=10/10, cliff_log2_span=2.322; discriminated cleanups but did
  not clear chain-grade discriminator).

This cell has a DIFFERENT experimental design (see below), and the "v1" label
in the task refers to the first cell in the new Research-directed program at
this arm set. Using the disambiguated anchor slug avoids overwriting the two
prior cells' data dirs while filing under the task-named pre-reg.

## Experimental design (differs from v1/v1p1)

| Axis | This cell (v1-arm4-b3k3) | Prior v1p1 |
|------|--------------------------|------------|
| Cleanups (OUTER) | classical / modern_continuous / iterative / **wta_baseline** | no_cleanup / classical / modern / iterative / **k_NN** |
| Arm count | 4 | 5 |
| B (num_banks) sweep | **{4, 16, 64}** | 8 fixed |
| K design | **K_cliff-relative per B: {K_cliff/2, K_cliff, 2*K_cliff}** where K_cliff(B)=256*B | absolute: {50,100,250,500,1000} |
| Regime | RANDOM only | RANDOM + ADVERSARIAL |
| N | 8192 | 4096 (v1p1 memory-fit) |
| Seeds | 3 (7, 13, 19) | 3 |
| Cardinality FULL / SMOKE | **36 / 8** | 50 / 15 |

## Files

- Core module: `experiments/_substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_core.py`
- Seed cells: `experiments/exp_substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_seed_{7,13,19}.py`
- Cleanup primitives inlined in core (bipolar torch tensors; chunked matmul).

## Cleanup primitives (OUTER axis, 4 arms)

| Family | Mechanism | Citation |
|--------|-----------|----------|
| `wta_baseline` | one-shot argmax over codebook -> snap to nearest bipolar code | reference floor |
| `classical_hopfield` | Hebbian W = X.T @ X / M (zero-diag); iterate sign(s @ W) | Hopfield 1982 |
| `modern_hopfield_continuous` | softmax-attention update: sign(softmax(beta * s @ X.T) @ X) | Ramsauer 2021 |
| `iterative_attractor` | L2-normalized cosine softmax with sqrt(D)-scaled beta (brain-canonical CA3) | Treves-Rolls |

Shared params: `beta=8.0`, `hop_max_steps=4`, `CUE_COS=0.70`, `SIGMA=1.0`.
Chunked matmul across codebook rows (`_CHUNK_M=128`) bounds peak allocation
under the v1-OOM class.

## Sweep and cardinality

K_cliff(B) = 256 * B => K_cliff(4)=1024, K_cliff(16)=4096, K_cliff(64)=16384.

Per-B K sweep FULL:
- B=4:  K in {512, 1024, 2048}
- B=16: K in {2048, 4096, 8192}
- B=64: K in {8192, 16384, 32768}

**FULL cardinality per seed:** 4 cleanups * 3 B * 3 K = **36 phase points**.
**FULL cardinality across 3 seeds:** 108 total.
**SMOKE cardinality per seed:** 4 cleanups * 1 B (B=4) * 2 K ({K_cliff, 2*K_cliff}) = **8 phase points**.

Smoke design intentionally exercises the DISCRIMINATOR-MUST-SURVIVE-SCALE
predicate: K=2*K_cliff at B=4 (K=2048) is the smallest K value where WTA is
expected to floor while modern/iterative are expected to lift. If smoke does
not fire the discriminator at B=4, full dispatch is BLOCKED per META_RULE
DISCRIMINATOR-MUST-SURVIVE-SCALE (a smaller B smoke that fails the discriminator
predicts full-B will also fail).

## CRLB / capacity-feasibility (META_RULE_AG)

Matched-filter SNR at cleanup entry:
`SNR = sqrt(N) / sqrt(M-1)` where M = K_per_bank * n_banks.
Cliff at SNR ~ 1 => M ~ N + 1 => K_per_bank ~ N/n_banks.

Task specifies K_cliff(B) = 256 * B; at N=8192 that matches N/n_banks only at
B ~ 32; the task uses a substrate-empirical K_cliff calibration from prior WM
K-cliff v3 CG. Design HONORS the task calibration (K_cliff = 256 * B) rather
than substituting the matched-filter formula. Both formulas are logged in the
per-point output for cross-check.

Discriminator reachability at K=2*K_cliff:
- B=4:  K=2048, M=8192, SNR ~ sqrt(8192)/sqrt(8191) ~ 1.0  DISCRIMINATING
- B=16: K=8192, M=131072, SNR ~ sqrt(8192)/sqrt(131071) ~ 0.25  FLOOR-ish
- B=64: K=32768, M=2097152, SNR ~ 0.06  DEEP FLOOR

The K=2*K_cliff discriminator is at or well below matched-filter cliff at all B;
this is by design — WTA/naive cleanup floors, but modern-Hopfield exponential
capacity + iterative-attractor basin descent may still lift.

## Pre-reg bands (LOCKED at module init)

Per-point tiers (META_RULE_AF):
- SATURATED: `recall >= 0.995`
- HARD_PASS: `0.80 <= recall < 0.995`
- MIDDLE_BAND: `0.50 <= recall < 0.80`
- FLOOR: `recall <= 0.10`
- HARD_FAIL: otherwise

**Cell-level FULL discriminator (task-mandated):**

At K=2*K_cliff, at each B, compute `max_lift = max(recall[non-wta]) - recall[wta_baseline]`
across 3 seeds. Require:
- `mean_lift >= 0.10`, AND
- cross-seed `cv < 0.08` on the winning non-wta arm

**HARD_PASS:** at least 1 B produces seed-consistent lift >= 0.10 (cv<0.08)
AND `META_RULE_AX` all 6 cleanup pairs pred+mech distinct
AND `META_RULE_Q` no suspect-1.000 at K=K_cliff (contamination-free)
AND cardinality_ok per seed.

**MIDDLE_BAND:** discriminator fires at >= 1 B but Q-saturation contamination
at K=K_cliff detected (META_RULE_Q trip) OR some B show partial lift >= 0.05
but no B seed-consistent at lift >= 0.10.

**HARD_FAIL:** all 4 cleanups collapse to within +/- 0.05 recall at K=2*K_cliff
across all B (cleanup choice capability-orthogonal at WM scale, matching PC
finding) OR distinctness self-report fails OR cardinality breach.

**Smoke discriminator (DISCRIMINATOR-MUST-SURVIVE-SCALE):**

At smoke (B=4, K in {1024, 2048}, N=8192, single seed), require:
- cardinality_ok (observed 8 == expected 8), AND
- all 6 cleanup pairs pred+mech distinct (META_RULE_AX), AND
- at least 1 non-WTA cleanup lifts recall >= 0.10 above WTA at K=2*K_cliff (K=2048)

If any of these fail: BLOCK_DISPATCH (full run predicted to be family-invariant).

## Discipline gates (mandatory; all checked)

- **META_RULE_H (cardinality_ok):** EXPECTED_N_UNITS_FULL=36, EXPECTED_N_UNITS_SMOKE=8.
- **META_RULE_AX (arm-distinctness):** verdict-emitter HARD_FAILs on any pair
  producing identical pred_pattern_hash OR mech_output_hash across the full sweep.
- **META_RULE_AY (self-report distinctness):** distinctness_self_report_pass
  is False -> HARD_FAIL.
- **META_RULE_Q (suspect-1.000):** any arm hitting recall >= 0.995 at K=K_cliff
  is flagged; contamination downgrades HP -> MIDDLE_BAND.
- **META_RULE_AF (arms-must-differ):** 4 cleanup outputs SHA-256 hashed per
  phase point (both mech-output and pred-pattern).
- **META_RULE_AG (CRLB / capacity):** matched-filter SNR + K_cliff calibration
  logged per point; discriminator reachability documented above.
- **META_RULE_AH (atomic-metrics-write):** per-seed via `_seed_checkpoint.write_partial_key`
  then aggregate -> atomic metrics.json rewrite at end.
- **META_RULE_AT (compose):** composes with prior capacity multi-bank alpha-K
  CG (ANCHOR H); shared substrate (bipolar codebook + multi-bank workspace)
  so the composition edge is a shape-match.
- **META_RULE_AW (identical config across seeds):** 3 sibling files import
  same core; SEED is the only delta.
- **DISCRIMINATOR-MUST-SURVIVE-SCALE:** smoke at full-N (N=8192) and
  discriminator-scale K (K=2*K_cliff at B=4) — check A per USER 2026-06-26
  discipline.

## Schema-VET fields

- `cardinality_ok: bool` (per seed)
- `arms_differ_verified: bool` (True at smoke via distinctness_self_report_pass)
- `final_metrics_atomicity: "tmp_replace"`
- `cell_chunked: true` (3 sibling cells, 1 seed each)
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: true` (per-phase-point flush)
- `defensive_error_checking: passed_all_4_patterns`
- `crlb_floor_computed: N/n_banks` (documented above)
- `discriminator_reachability: true` (K=2*K_cliff spans discriminating regime at B=4)
- `baseline_in_band: true` (wta_baseline expected FLOOR at K=2*K_cliff; sits
  in the band we're comparing against)
- `sweep_alignment_verdict: ALIGNED` (K is natural sweep axis for all cleanup
  primitives; no hidden mismatch)
- `discriminating_fraction: ~0.33` (K=2*K_cliff is 1 of 3 K values expected
  to land in the discriminating band; K=K_cliff/2 expected SATURATED across
  arms; K=K_cliff possibly SATURATED for high-capacity arms)
- `composition_edges: bipolar codebook -> multi-bank write -> cleanup -> argmax; SHAPE_MATCH`
- `positive_control_arms: wta_baseline @ K=K_cliff/2 (B=4)` expected >= 0.80
  recall (well below capacity)
- `functional_requirements:` (1) associative recall under bank-routed cue
  survives per-arm; (2) at least one mechanism-cleanup dominates WTA at
  discriminator scale

## Routing and effort estimate

- **Smoke queue:** local CPU (.venv direct invocation via `--smoke`).
  Smoke shape: N=8192, B=4, K in {1024, 2048}, 4 arms, 1 seed = 8 pts.
  Modern-Hopfield 4-step softmax at (8192, 8192) codebook is the bottleneck;
  expected wallclock 60-300s CPU per point.
- **Full queue:** `overnight_queue` (GPU). At B=64 K=32768, codebook rows
  M=2097152, N=8192 => codebook fp32 = 64 GiB — INFEASIBLE. This must be
  handled with reduced codebook + repeat sampling (already in core: cb_size
  capped at max_K_total * 2 with fallback to torch.randint when K_total >
  cb_size). At B=64 K=32768, K_total=32768, cb_size=65536 => codebook 2 GiB
  fp32, fits on 8 GiB GPU. Realistic wallclock estimate 90-180 min per seed.
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes
  through Orchestrator (this run notifies Orchestrator post-smoke).
- **Timeout per seed FULL:** 10800 s (3 h; conservative given B=64 workload
  + PROT-019 mandates >=3600s for anchors N>=4096).
- **Timeout SMOKE:** 1800 s (30 min; safe upper bound for CPU-fallback
  8-point smoke).

## LoC estimate

- Core module: ~600 LoC (4 primitives + per-point eval + selftest + per-seed
  sweep + verdict + smoke-gate)
- 3 sibling cells: ~230 LoC each ~= 690 LoC
- This pre-reg: ~150 lines
- Total: ~1450 LoC (excluding tests)
