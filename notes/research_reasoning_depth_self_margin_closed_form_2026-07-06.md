# Research: does the RNS/FHRR self-margin order-statistic law extend to reasoning-depth self-prediction?

Author: research (Opus synthesis + Sonnet lit-scan x3). Date: 2026-07-06.
Drill type: cadence gap-fill, level-2 operational (verify off-disk against landed cells; no new cell built).

## HEADLINE

**YES, provisionally closed-form-predictable — same order-statistic family as decode-margin, plus one
missing physical ingredient.** The landed `reasoning_depth_keyslots_sharding_v1` cell is MIDDLE_BAND not
because reasoning-depth collapse resists closed form, but because its own pre-registered predictor
(`collision_frac_theo` -> `ln(0.5)/ln(1-coll_frac)`) treats a key-slot occupancy collision as a **binary
guaranteed failure** — structurally the same mistake the RNS union-bound and FHRR asymptotic controls make
(treating "beaten by a competitor" as certain rather than computing the exact probability of still winning
the argmax). Re-deriving the per-hop success probability as a **graceful partial-credit "capture" order
statistic** (a collided slot is a superposition of c stored items; single-shot argmax still recovers the
right one with probability ~1/c, not 0), then composing across depth via the standard series-reliability
law `D* = ln(FLOOR)/ln(p_hop)`, converts the current systematic **+102% under-prediction** (mean
measured/predicted ratio 2.02x, CV 15.6%, n=25 non-censored op-points) into an **unbiased ~0% mean bias**
(ratio 0.98x, CV 11.7%) using nothing more than an untuned, symmetric, zero-parameter Poisson-occupancy
capture model — recomputed off-disk against the ALREADY-LANDED data, zero new trials. An independent
replication point from the sibling cell (`exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1`, a
different code path, different fill regime) lands within 6.4% with the same untuned formula. This is not
yet CG-grade (RNS hit 1.01-1.11x, FHRR hit <=0.05 relative dev) — the untuned symmetric model is a
first-principles sanity check, not the exact V_CHAIN-weighted order statistic — but the direction, size, and
cross-cell stability of the correction is exactly the signature the RNS/FHRR self-margin cells showed before
their exact-prefactor fix landed HARD_PASS. This is a real CG-candidate cell spec, not a rediscovery of an
already-closed lever (the iterative-cleanup lever is separately, correctly, CLOSED — see cross-thread below).

## Cheap decisive test (already run, off-disk, zero new trials)

Recomputed against `data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json:extra.per_op` (30 measured
op-points, 25 non-censored after excluding the 5 points capped at `D_MAX=18`) and cross-checked against
`data/exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1_smoke/metrics.json` (independent cell, same
`KEY_SLOTS=2048` baseline capacity, different NTEST/fill=0.1465):

| Model | mean(measured/predicted) | CV | range |
|---|---|---|---|
| naive occupancy-binary (`ln(0.5)/ln(1-coll_frac)`, the cell's own pre-registered predictor) | 2.021x (under-predicts) | 0.156 | 1.46-2.80x |
| **capture partial-credit** (`p_hop = (1-e^-fill)/fill` via Poisson-occupancy-averaged 1/c, `fill=-ln(1-coll_frac)`) | **0.980x (unbiased)** | **0.117** | 0.83-1.23x |
| cross-cell replication (cortex cell, fill=0.1465, untuned formula) | predicted 9.58 vs measured 9.00 | dev 6.4% | single point |

A further, more revealing re-parametrization: define `k = p_fail_measured / collision_frac_emp` (i.e. "what
fraction of a nominal occupancy-collision event actually causes decode failure"). Across the same 25 points
(2 N values x 3 NTEST difficulties x up to 4 mechanism arms): **mean k = 0.530, CV = 0.107**, i.e. a
collision resolves correctly ~47% of the time (near a fair coin-flip on a 2-way tie, drifting toward 1/3 as
fill rises and 3-way+ collisions become non-negligible — exactly the shape a Poisson-occupancy-weighted `1/c`
average predicts, and exactly why `k` trends up with NTEST/fill in the data: 0.476 -> 0.514 -> 0.612 for the
baseline arm as NTEST goes 24 -> 32 -> 40). This stability (CV ~11%) across capacity (2048-8192), N
(8192/16384), and difficulty is the same kind of "loose-but-consistent multiplicative offset" signature the
RNS cell showed pre-fix (gm_union 2.39-2.73x, itself stable to within ~15%) before the exact order-statistic
prefactor tightened it to 1.01-1.11x.

## Falsifiable predictions for the follow-on cell (NOT yet built — spec only)

Proposed cell: `exp_reasoning_depth_exact_order_statistic_self_margin_v1`. Reuses the
`reasoning_depth_keyslots_sharding_v1` measurement machinery VERBATIM (factored Hebbian store, argmax
cleanup, depth curves, 6 arms). Adds one new PREDICTION arm: the exact per-hop success probability, computed
as `E_c~Poisson(fill)[ P_correct(c+1 colliding items, V_CHAIN-1 non-colliding distractors) ]` via the SAME
Gauss-Hermite order-statistic machinery already validated in `rns_subblock_margin_exact_prefactor_v2` and
`fhrr_bundle_capacity_exact_margin_v1` (not the crude symmetric `1/c` used in this drill's sanity check),
composed across depth via `D* = ln(FLOOR)/ln(p_hop_exact)`. Keeps the current `collision_frac_theo`
occupancy-binary model as the retained loose CONTROL (expected to stay ~2x off, exactly like the RNS
union-bound and FHRR asymptotic controls).

**HARD-PASS** (promotes reasoning-depth self-prediction to a CG-candidate, parallel to RNS/FHRR):
- exact-arm geometric-mean ratio-error (measured/predicted usable-depth) `<= 1.5x` at ALL tested
  (N, NTEST, arm) op-points on a FRESH multi-seed (>=5 seed) FULL dispatch, AND
- relative improvement over the retained occupancy-binary control `>= 1.5x` at every op-point, AND
- the correction is STABLE cross-seed (CV of per-op ratio-error `<= 0.15`) and reproduces the
  off-disk retrospective check on both landed cells to within the same tolerance.

**HARD-FAIL** (honest ACCEPT-boundary — reasoning-depth resists exact closed-form self-prediction):
- exact-arm geometric-mean ratio-error `> 2.0x` at any op-point on fresh dispatch (the untuned
  sanity-check model already got everything inside 1.23x, so blowing past 2x on the REFINED exact
  version would mean higher-order dynamics — e.g. correlated hop-to-hop error, chain-position-dependent
  drift, or V_CHAIN-competitor asymmetry — dominate and the simple i.i.d.-per-hop capture model doesn't
  hold), OR
- the correction constant is NOT stable (CV `> 0.25`) across arms/N/fill, meaning the "same law" framing
  is not supported and reasoning-depth needs its own (non-order-statistic) closed form or stays
  empirically-characterized-only.

**MIDDLE** (current de-facto state): tightens meaningfully vs the occupancy-binary control (as already
demonstrated off-disk: 2.02x -> 0.98x mean, 0.156 -> 0.117 CV) but does not clear the 1.5x CG bar at every
op-point on fresh multi-seed dispatch.

## Cross-thread synthesis

1. **The iterative-cleanup lever is correctly, separately CLOSED.** `exp_cortex_iterative_attractor_
   cleanup_depth_ceiling_v1` (smoke, HARD_FAIL as pre-registered/predicted) proved single-shot argmax IS
   the MAP decoder (modern-Hopfield attractor at beta=12/T=6 converges bit-identically, `max_abs_gap=0.04`);
   iterating cleanup does not extend depth. This drill does NOT reopen that lever — it targets the
   PREDICTION formula for a fixed, already-optimal cleanup mechanism, not the cleanup mechanism itself.
   `usable-depth-vs-N` is flat/N-independent at fixed fill (MEASURED, `rises_with_N=False`), which is itself
   consistent with a **load-parameter-only** (occupancy/fill) dependency — the correct precondition for an
   order-statistic/collision law rather than a dimension-dependent (background-crosstalk) law.

2. **Direct sibling precedent, same codebase, same week:** `rns_subblock_margin_exact_prefactor_v2`
   (HARD_PASS, `gm_exact` 1.01-1.11x vs `gm_union` 2.39-2.73x) and `fhrr_bundle_capacity_exact_margin_v1`
   (HARD_PASS, `dev_exact <= 0.05` vs `dev_asymptotic` 10-35%) both already demonstrate: a naive/loose
   collision-or-crosstalk bound is systematically pessimistic by a STABLE multiplicative factor, and
   replacing it with the exact M-ary order statistic (`E_z[Phi(mu+z)^(m-1)]`-family, Gauss-Hermite
   quadrature) closes the gap to near-exact. The reasoning-depth finding in this drill reproduces the SAME
   signature (stable ~2x offset -> near-unbiased on the fix) one level up the composition stack (per-hop
   decode margin -> multi-hop chain survival).

3. **Cautionary prior-art within this substrate:** an EARLIER, DIFFERENT depth-scaling formula
   (`kmax_depth_scaling_formula_HF`, cap_map v408, 2026-06-05, for resonator-augmented cleanup depth under
   store OVERLOAD load-fraction) was refuted by up to **1526%** miscalibration — a much more dramatic
   failure than anything seen here. That formula addressed a different regime (overload lf, not
   under-capacity occupancy-collision) and a different mechanism (resonator/ensemble rescue, not raw
   key-capacity occupancy). The current finding's ~2x systematic-and-stable offset (closing to ~unbiased
   with an untuned first-principles fix) is a qualitatively much better-behaved discrepancy — consistent
   with "wrong prefactor, right functional form" rather than "wrong model entirely." Flagging this explicitly
   per the substrate's own history of over-claiming closed-form depth formulas before verification.

4. **Lit-scan (3 parallel Sonnet sub-agents, generic-math queries only, no substrate-specific terms):**
   - **Balls-into-bins / occupancy theory** (Raab-Steger, Mitzenmacher-Upfal) treats collision as failure by
     convention — does NOT natively include partial-recovery. [Balls-into-bins survey](https://ccanonne.github.io/files/compx270-chap3.pdf).
   - **Slotted-ALOHA "capture effect"** is the well-established, DIRECT precedent for graceful partial-credit
     collision resolution: Roberts (1975); Arnbak & Van Blitterswijk (1987, IEEE JSAC) give a closed-form
     symmetric-case capture probability `P(capture | i interferers) = 1/(1+z0)^i`, which reduces toward the
     `1/c`-type scaling used in this drill's sanity check as `z0 -> 0`. Decades-old, solidly citable.
   - **Associative-memory literature** (Hopfield 1982; Amit-Gutfreund-Sompolinsky 1985; Willshaw-Buneman-
     Longuet-Higgins 1969; Knoblauch 2008 SIAM exact Willshaw-Palm distribution; Plate 1995/2003; Gallant &
     Okaywe 2013 arXiv:1501.07627; Frady/Kleyko/Sommer VSA-capacity line arXiv:2106.05268) is the SAME
     lineage the substrate's own bundle-capacity work descends from. It treats retrieval as signal-vs-max-
     of-competitors via Gaussian approximation + union/Bonferroni bound — i.e. the FIELD's standard practice
     is exactly the "loose bound" this drill (and the RNS/FHRR cells) are tightening. No source gives a
     clean textbook formula for "P(correct | exactly c items superposed at one slot)" in the VSA/bundling
     sense — the closest exact treatment (Knoblauch 2008) is for binary Willshaw nets, not continuous VSA.
   - **Series-reliability composition** (`p^D = floor`) is textbook-standard reliability engineering
     (reliability block diagrams); DHT/overlay literature (Castro et al. OSDI 2002 secure routing; Chord/
     Kademlia churn studies) confirms multi-hop lookup failure compounds multiplicatively but does not
     package the closed "max usable depth" formula explicitly.
   - **Calibrated verdict from all 3 sub-agents:** every COMPONENT (capture-effect order statistics,
     competing-order-statistic retrieval theory, series-reliability composition) is decades-old, solidly
     established math. The SPECIFIC SYNTHESIS — "occupancy-collision as graceful capture, Poisson-averaged,
     composed geometrically to predict multi-hop associative-chain depth exactly" — is judged a **novel
     combination**, not directly citable as one paper (independent confidence estimates ~0.20-0.25 that this
     exact synthesis exists in the literature already).

## Substrate-product implications (monitor-not-control; NOT self-improvement)

If the follow-on cell HARD_PASSes: the substrate gains a THIRD exact self-margin CG (alongside RNS decode
and FHRR bundle capacity), but this one is qualitatively different — it is a self-prediction about the
substrate's own **REASONING MECHANISM** (how many chained inference hops it can trust before accuracy drops
below a floor), not about a storage/codebook primitive. Framed honestly: the substrate would be able to
compute, in closed form and BEFORE running a chain, "how deep can I reason on this query given my current
effective key-capacity" — a monitor capability (report a number, flag when a planned chain exceeds the
safe depth) with zero write-access to its own config. This is the requested "substrate reasoning about
itself" prize in its narrowest, most honest form: a glass-box self-CHECK on the reasoning mechanism, not
self-improvement (it never resizes key-slots or reshards on its own — that stays a human/exp_dev decision
informed by the number). Brain-grounding: this is closest to a metacognitive confidence/error-monitoring
signal (anterior cingulate-adjacent function honestly by analogy, mechanism not task), not a claim of
task-level reasoning competence.

If the follow-on cell lands at MIDDLE or HARD-FAIL (the honest ACCEPT-boundary): the substrate still has
the CURRENT, already-landed value — a validated, product-usable EMPIRICAL capacity law (usable-depth rises
with key-capacity, N-independent, cleanup-mechanism-closed) which is itself sufficient to inform a practical
"if you need depth D, provision key-capacity >= X" sizing rule, just without an exact closed-form guarantee.
Either outcome is non-parked and actionable.

## Honesty gate resolution

Per the task's explicit ask: reasoning-depth collapse is governed by the family of order-statistic /
collision-averaging math (same conceptual machinery as RNS/FHRR decode-margin), but the FHRR/RNS formulas
cannot be copy-pasted verbatim — they answer "does the correct symbol win a single argmax," while
reasoning-depth additionally needs (a) a collision-conditional PARTIAL-credit order statistic (the
"capture effect" ingredient, well-precedented in ALOHA literature but not yet applied to VSA/HRR bundling in
the wild) and (b) standard series-reliability composition across hops (textbook-trivial). The evidence this
drill gathered off-disk (systematic 2.02x -> 0.98x mean-bias closure, CV 15.6% -> 11.7%, cross-cell 6.4%
replication, all with an UNTUNED zero-parameter model) is strong enough to warrant building the properly
exact version, but not strong enough to claim CG-grade closure without a fresh dispatch — hence MIDDLE-to-
HARD-PASS-candidate framing, not a declared HARD-PASS.

## Citations (verified count)

7 distinct citable sources verified via web search across 3 parallel lit-scan sub-agents (Roberts 1975;
Arnbak & Van Blitterswijk 1987 IEEE JSAC; Hopfield 1982 / Amit-Gutfreund-Sompolinsky 1985; Willshaw-Buneman-
Longuet-Higgins 1969 + Knoblauch 2008 SIAM; Plate 1995/2003; Gallant & Okaywe 2013 arXiv:1501.07627;
Frady/Kleyko/Sommer VSA-capacity arXiv:2106.05268/2111.06077; Castro et al. OSDI 2002). Plus 2 internal
sources verified on-disk (`data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json`,
`data/exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1_smoke/metrics.json`) and 2 sibling CG cells
cited for the order-statistic template (`data/exp_rns_subblock_margin_exact_prefactor_v2/metrics.json`,
`data/exp_fhrr_bundle_capacity_exact_margin_v1/metrics.json`).

## P estimate (calibration penalty applied)

Raw confidence (pre-calibration) that the properly-derived exact V_CHAIN-weighted order statistic clears
the 1.5x CG bar on fresh dispatch: ~0.75-0.80 (the untuned symmetric sanity-check already reaches 0.83-1.23x
range with zero fitting). Per [[feedback-lit-scan-calibration-penalty]], novel-synthesis P is CAPPED at 0.50
regardless of this raw evidence strength (the lit-scan explicitly judges the SPECIFIC combination novel, not
directly precedented). **P_deflated = 0.50 (capped).**
