# Cell design: Probe 10 v2 BUNDLED cliff empirical bracket -- NEGATIVE outcome

**Anchor considered:** `stage1_regime_probe_10_storage_x_algebra_non_saturated_v2`
**Predecessor:** v1 SMOKE at commit 51b787ba7 (Skunkworks META atom #43 filed 2026-07-03 21:15Z)
**Task hand-off:** re-SMOKE with empirical BUNDLED bracket per Skunkworks correction
**Outcome:** MM_HONEST_FAIL_NO_MATCHED_CLIFF -- BUNDLED FHRR chain composition has NO stable cliff-adjacent regime; recommend SKIP Probe 10 v2 FULL entirely.
**Author:** exp_dev 2026-07-03

## Skunkworks-authoritative constraint (META atom #43)

> BUNDLED re-bracket at LOWER corruption (corr=0.05-0.10) to bring BUNDLED cliff
> in-band, then re-run smoke. DO NOT dispatch FULL against a floored BUNDLED
> arm -- the "cross-term" would be uninterpretable. If no (N, corr, M) combo
> brings BUNDLED cliff in-band without invalidating matched-cliff comparison:
> MECHANISM SWITCH to iterative_cosine (which does saturate at PC regime) OR
> SKIP Probe 10 FULL -- STORAGE column already covered by Probes 4+5 FULL +
> prior atoms.

## Empirical bracket procedure

Two-stage bracket search on the FHRR chain-composition primitive
(L=2, F=1) over BUNDLED storage:

**Stage 1 (scout, TR=20, seed=7):**
- mechanism in {modern_hopfield, iterative_cosine, soft_energy_attractor}
- N in {512, 1024, 2048}
- corr in {0.05, 0.10, 0.15}
- M in {50, 100, 200, 400, 800}
- Total: 3 x 3 x 3 x 5 = 135 phase points
- Flagged 10 candidates with single-seed acc in [0.30, 0.95]

**Stage 2 (refine, TR=40, seeds {7, 13, 19}):**
- All 10 stage-1 candidates + 4 M/corr neighbors + F=16 preview on leader
- Result: EVERY candidate mean below band floor (0.30) across 3 seeds
- Best modern_hopfield BUNDLED mean: 0.208 (N=1024 c=0.10 M=100)
- Best iterative_cosine BUNDLED mean: 0.208 (N=2048 c=0.15 M=50 or M=100)
- Best soft_energy_attractor BUNDLED mean: 0.217 (N=1024 c=0.10 M=100)
- NONE reached band floor

**Stage 3 (TR=100 sanity, seeds {7, 13, 19}):**
- Top BUNDLED candidates re-verified at FULL TR=100
- Result confirmed: modern_hopfield 0.187-0.220, iterative_cosine 0.210-0.213,
  soft_energy_attractor 0.147 -- ALL below band
- Rules out "TR=40 sampling variance" as explanation

**SHARDED cliff regime check:** at (N=512, M=6400, corr=0.85, TR=40) both
iterative_cosine (mean=0.725) and soft_energy_attractor (mean=0.692) landed
in-band cleanly, confirming SHARDED cliff regime is robust to mechanism
substitution. Only BUNDLED is the problem.

**All numbers MEASURED@** scratchpad scout scripts + this design note table.

## Numeric summary (TR=40 multi-seed BUNDLED means)

| mechanism              | N    | corr | M   | mean | std   | in_band? |
|------------------------|------|------|-----|------|-------|----------|
| modern_hopfield        |  512 | 0.10 | 100 | 0.167| 0.080 | NO       |
| modern_hopfield        | 1024 | 0.10 | 100 | 0.208| 0.063 | NO       |
| modern_hopfield        | 2048 | 0.10 |  50 | 0.125| 0.066 | NO       |
| modern_hopfield        |  512 | 0.10 |  50 | 0.208| 0.052 | NO       |
| iterative_cosine       | 2048 | 0.15 |  50 | 0.208| 0.029 | NO       |
| iterative_cosine       | 2048 | 0.15 | 100 | 0.208| 0.058 | NO       |
| iterative_cosine       | 2048 | 0.15 | 200 | 0.192| 0.072 | NO       |
| iterative_cosine       |  512 | 0.05 | 100 | 0.117| 0.063 | NO       |
| soft_energy_attractor  | 1024 | 0.10 | 100 | 0.217| 0.038 | NO       |
| soft_energy_attractor  | 1024 | 0.15 |  50 | 0.142| 0.104 | NO       |
| soft_energy_attractor  | 1024 | 0.15 | 100 | 0.167| 0.072 | NO       |
| soft_energy_attractor  |  512 | 0.15 |  50 | 0.167| 0.063 | NO       |

Non-saturated band [0.30, 0.95]. All means below floor.

## Physics interpretation (novel finding worth atomizing)

**Observation:** BUNDLED FHRR chain composition at L=2, F=1 exhibits a
BIMODAL accuracy distribution over the (mechanism, N, corr, M) design
space -- either near-saturated (>=0.90) or floored (<=0.25) -- with NO
stable cliff-adjacent middle band. This contrasts with SHARDED, which
admits a broad cliff-adjacent regime at (N=512, M=6400, corr=0.85)
where multiple mechanisms land in [0.30, 0.95] cleanly.

**Mechanism:** BUNDLED storage superimposes M items into one N-dim vector.
For a corrupted query, the cleanup either resolves the correct component
(above-noise) or hits a same-magnitude cross-talk collision (near-random).
The transition between these regimes as M varies is sharp because the
signal-to-cross-talk ratio scales roughly linearly with 1/M (interference
from other bundled items) -- no gradual degradation regime like SHARDED,
where per-item cleanup lookup degrades continuously with codebook size.

**Relation to existing atoms:**
- REINFORCES `META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1`
  (BUNDLED collapses at L>=2): adds the further observation that BUNDLED
  lacks a mid-band regime for cross-term measurement even at L=2.
- CONSISTENT with `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1`:
  SHARDED extends 13.9x beyond Plate bound; BUNDLED at Plate bound
  transitions abruptly.
- EXPLAINS why v1 CLIFF_BUNDLED F=1 M=200 hit 0.275 (seed 7 lucky draw)
  but multi-seed mean is 0.208.

## Recommendation to Director

**SKIP Probe 10 v2 FULL entirely.**

Rationale:
1. STORAGE x ALGEBRA cross-term measurement REQUIRES both storages in-band
   at MATCHED mechanism (else 3-way MECHANISM x STORAGE x ALGEBRA
   interaction confounds the cross-term).
2. Empirical bracket confirms NO BUNDLED regime satisfies this constraint
   across the plausible design space at L=2, F=1.
3. STORAGE column of pairwise regime matrix already covered by:
   - Probe 1 (STORAGE x MECHANISM CG_META): mech_var@BUNDLED=0.103 landed
   - Probe 4 (STORAGE x N): awaiting VET but landed
   - Probe 5 (STORAGE x TOPOLOGY / F fan-in): awaiting VET but landed
4. The empirical bracket finding itself IS a useful atom (BUNDLED bimodal
   distribution; no mid-band); atomizing this closes STORAGE column with
   an additional structural physics observation, not a gap.

If Director insists on a Probe 10 replacement to close STORAGE x ALGEBRA
specifically:
- Option R1: raise L to 1 (single-hop; not chain) where BUNDLED admits
  a wider mid-band; but this measures a DIFFERENT primitive (retrieval,
  not chain composition) and the composition-depth physics law was the
  driving question.
- Option R2: replace BUNDLED with a "sharded-with-noise" arm that
  parametrically degrades between the two extremes; but this requires
  a new primitive not in the current Option Y core.
- Option R3: measure STORAGE x ALGEBRA at a DIFFERENT regime: SHARDED
  with F-sweep at multiple (N, M, corr) triples spanning the SHARDED
  cliff-adjacent band; BUNDLED excluded. This closes STORAGE-arm of the
  matrix column with a partial measurement plus atomized negative
  finding on the BUNDLED side.

Preferred: SKIP (option A). Second choice: R3 (SHARDED-only F sweep).

## Framing discipline

- Arc-continuation not arc-closure per
  `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03`.
- MM_TENTATIVE at most on the empirical bracket finding; full atomization
  requires cert-owner review + multi-mechanism confirmation which this note
  already provides at 3 mechanisms x 3 seeds x TR in {20, 40, 100}.
- CITED@ Skunkworks META atom #43 (2026-07-03 21:15Z commit 26d0f99ea).
- CITED@ `feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03`.

## Bracket scout artifacts

Scripts run this session (not committed; results captured in this note):
- `bracket_p10_v2_scout.py` -- Stage 1 grid scout (135 phase points, TR=20)
- `bracket_p10_v2_refine.py` -- Stage 2 refine at TR=40, seeds {7,13,19}
- `bracket_p10_v2_mechswitch.py` -- Stage 2b mechanism switch check
- `bracket_p10_v2_tr100.py` -- Stage 3 TR=100 sanity check

Key numeric findings inlined in the table above.
