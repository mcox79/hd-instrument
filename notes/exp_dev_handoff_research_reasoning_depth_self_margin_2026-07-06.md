# exp_dev hand-off -- research: reasoning-depth exact self-margin

Filed-by: research sub-agent
Date: 2026-07-06
Trigger: notes/research_reasoning_depth_self_margin_closed_form_2026-07-06.md
Urgency: MEDIUM-HIGH -- non-parked, novel CG-candidate cell for a HEADLINE capability (substrate
predicts its own reasoning-depth limit exactly); off-disk pre-check already shows the fix closes a
systematic 2.02x under-prediction to ~0.98x (unbiased) with an untuned zero-parameter sanity model.

---

## Pause state

Experiment below is PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ONE anchor candidate only. Experiment design details (exact
Gauss-Hermite quadrature implementation, cell grid, seed values) are to be authored by exp_dev from
the research note + the two sibling CG cells' verbatim machinery. Do NOT treat the description below
as an implementation spec.

---

## Anchor candidates (rank-ordered)

### Anchor 1: exp_reasoning_depth_exact_order_statistic_self_margin_v1

Anchor pointer: Research note "Falsifiable predictions for the follow-on cell" section, and the
"Cheap decisive test" table (naive vs capture-partial-credit model comparison).

Substrate-product reading: Reuses `experiments/exp_reasoning_depth_keyslots_sharding_v1.py`
measurement machinery VERBATIM (factored Hebbian store, single-shot argmax cleanup -- already
PROVEN optimal by `exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1`, so do not reopen
iterative cleanup as a lever). Adds ONE new prediction arm: the EXACT per-hop retrieval-success
probability, computed as a Poisson-occupancy-weighted order statistic over c-way key-slot collisions
(c items superposed at one slot competing via argmax against `V_CHAIN-1` non-colliding distractors),
using the SAME Gauss-Hermite-quadrature order-statistic machinery already validated in
`experiments/exp_rns_subblock_margin_exact_prefactor_v2.py` and
`experiments/exp_fhrr_bundle_capacity_exact_margin_v1.py` (NOT the crude symmetric `1/c` used in the
research drill's off-disk sanity check -- that was a zero-parameter gut-check, not the exact
formula). Compose across depth via the standard series-reliability law `D* = ln(FLOOR)/ln(p_hop_exact)`.
Keep the existing `collision_frac_theo` occupancy-binary predictor as the retained loose CONTROL arm
(expected to stay ~2x off, matching the RNS union-bound / FHRR asymptotic control pattern).

Tier hint: CPU-only (numpy Gauss-Hermite quadrature, no GPU needed for the prediction arm; the
measurement arm is the existing verbatim CPU cell). Pre-dispatch cheap check ALREADY DONE (zero new
trials, recomputed off-disk against both landed cells -- see research note). Fresh dispatch: smoke
first (reuse existing smoke grid), then multi-seed (>=5) FULL matching the RNS v2 / FHRR v1 seed
precedent {7,13,19,23,29}.

Why-now: Two sibling self-margin CG cells (RNS subblock margin, FHRR bundle capacity) landed
HARD_PASS this same cycle using the identical exact-order-statistic-vs-loose-bound pattern. The
reasoning-depth cell is MIDDLE_BAND for the SAME structural reason those two were pre-fix (a loose,
binary-failure approximation where the true dynamics are graceful/partial-credit). The off-disk
pre-check (untuned model) already reduces systematic bias from +102% to ~0% and CV from 15.6% to
11.7% -- strong enough evidence to warrant the properly-exact version, which per the RNS/FHRR
precedent (loose ~2.4-2.7x -> exact ~1.0-1.1x; loose 15-58% -> exact <=0.05) plausibly clears the CG
bar on fresh dispatch. This closes the "reasoning-depth self-prediction" gap non-parked -- the
substrate would know, in closed form, how deep it can reason before it breaks.

Pre-reg bands (full detail + honesty-gate resolution in the research note):
  HARD-PASS: exact-arm geom-mean ratio-error <= 1.5x at ALL (N, NTEST, arm) op-points on fresh >=5-seed
    FULL dispatch; relative improvement over the retained occupancy-binary control >= 1.5x everywhere;
    cross-seed CV of ratio-error <= 0.15; reproduces the off-disk retrospective check on both landed
    cells within the same tolerance.
  HARD-FAIL (honest ACCEPT-boundary): exact-arm geom-mean ratio-error > 2.0x at any op-point on fresh
    dispatch, OR correction constant unstable (CV > 0.25) across arms/N/fill -- reasoning-depth resists
    exact closed-form self-prediction; stays an empirically-characterized capacity law only.
  MIDDLE: tightens meaningfully vs control (as already shown off-disk) but does not clear 1.5x at every
    op-point on fresh dispatch.

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_reasoning_depth_self_margin_closed_form_2026-07-06.md
- Landed cell to extend (verbatim machinery source): experiments/exp_reasoning_depth_keyslots_sharding_v1.py
  + data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json
- Sibling closed-lever cell (do NOT reopen iterative cleanup): experiments/exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1.py
  + data/exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1_smoke/metrics.json
- Order-statistic template #1 (exact prefactor derivation to reuse): experiments/exp_rns_subblock_margin_exact_prefactor_v2.py
  + data/exp_rns_subblock_margin_exact_prefactor_v2/metrics.json + preregs/rns_subblock_margin_exact_prefactor_v2.md
- Order-statistic template #2 (exact prefactor derivation to reuse): experiments/exp_fhrr_bundle_capacity_exact_margin_v1.py
  + data/exp_fhrr_bundle_capacity_exact_margin_v1/metrics.json + preregs/2026-07_fhrr_bundle_capacity_exact_margin_v1.md
- Prereg to extend: preregs/reasoning_depth_keyslots_sharding_v1.md (Section "Collision model" is the
  loose predictor being replaced)
- Cautionary prior-art (an EARLIER, unrelated depth-scaling formula was refuted 1526% miscalibrated --
  cited in this drill's Cross-thread synthesis Section 3): notes/substrate_capability_map.md around the
  "v407 -> v408" / "KMAX FORMULA REFUTED" entries (2026-06-05).

---

## Contract section

This handoff proposes ONE anchor. Exp_dev authors the exact Gauss-Hermite quadrature formula for
`P_correct(c-way collision, V_CHAIN-1 distractors)` (generalizing beyond the research drill's crude
symmetric `1/c` sanity check, following the same derivation pattern as the RNS `E_z[Phi(mu+z)^(m-1)]`
and FHRR `E_x[Phi(x/sqrt(N*K/2))^(V-1)]` formulas), Poisson-averages it over occupancy multiplicity
`c ~ 1+Poisson(fill)`, and composes across depth. Exp_dev decides smoke grid, seed count for smoke,
and whether to stage FULL local-CPU or remote_cpu_queue per the SMOKE-only-local rule (this looks
like a CPU-scale cell, similar wall-clock class to the RNS v2 sibling: numpy vectorized, ~seconds to
tens of seconds).

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing the exact Gauss-Hermite node count / quadrature implementation (follow RNS/FHRR precedent:
  64-point, numpy `polynomial.hermite.hermgauss`, no scipy)
- Choosing smoke vs FULL seed counts and grid density within the pre-registered bands above
- Choosing local CPU vs remote_cpu_queue routing per the SMOKE-only-local rule
- Writing the cell's arms/controls consistent with the research note's falsifiable-prediction table

Exp_dev is NOT autonomous in:
- Reopening the iterative-cleanup lever (CLOSED by `exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1`;
  single-shot argmax is the fixed, proven-optimal cleanup mechanism for this cell)
- Declaring CG promotion (Skunkworks/VET decides the tier per landed-VET discipline)
- Framing this as self-improvement (monitor-not-control: the cell only REPORTS a tighter depth-limit
  prediction; it never resizes key-slots, reshards, or edits any landed cell's config)
