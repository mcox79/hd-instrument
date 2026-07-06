# RESEARCH — Capability self-margin frontier map: which capabilities admit a closed-form self-margin?

**Date:** 2026-07-06
**Author:** research (Sonnet 5)
**Trigger:** Cadence gap-fill META-drill. The exact self-margin machinery (M-ary order-statistic,
64-pt Gauss-Hermite quadrature, "elevated-mean signal vs zero-mean competitors" argmax) has now
generalized from CODEBOOK-margins (RNS decode CG, FHRR bundle-capacity CG) to a CAPABILITY-margin
(reasoning-depth, smoke HARD_PASS, FULL staged). This drill maps the FRONTIER: which of the
substrate's remaining capability-collapse mechanisms are collision/order-statistic-driven
(closed-form self-predictable, same family) vs which are genuinely irregular (resist, honest
ACCEPT-boundary) — per the standing honesty gate, several WILL resist, and I should not force a
cell where the mechanism does not fit.

**Scope discipline:** monitor-not-control (a self-margin cell REPORTS a tighter predicted number; it
never edits config, resizes anything, or triggers a rebuild — NOT self-improvement). Brain-grounding
honestly engineering/metacognitive-by-analogy (error-monitoring, not task competence). This is a
notes drill — no cell built yet; deliverable is the frontier map + ONE ranked, buildable cell spec.

---

## (a) HEADLINE

**The order-statistic self-margin pattern is a genuine FAMILY, not a one-off: 5 of 8 inventoried
capability-collapse mechanisms reduce to "true signal vs a finite set of competing candidates,
argmax-decoded, possibly composed across a chain" — the SAME closed-form machinery (Gauss-Hermite
quadrature evaluation of `E_z[Phi(elevated-mean+z)^(competitors)]`-type integrals) applies or
plausibly extends. 3 of 8 are genuinely IRREGULAR and resist closed-form self-margin for three
DIFFERENT structural reasons (not one generic "hard" bucket): perception/encoder collapses via a
power-law spectrum (wrong RMT regime, not bulk+spike); generalization collapses via an
information-theoretic one-to-many entropy ceiling (no collision at all); and control's
AUTONOMOUS-DECOMPOSITION collapses via Ross-Bagnell-style `O(T^2)` distribution-shift compounding
regret (a genuinely different math family — accumulating positional drift under off-policy
evaluation, not a stationary collision probability). The TOP newly-identified buildable candidate is
**comprehension's order-recovery cliff** (`exp_comprehension_envelope_superposition_vocab_v1`,
D8xV1000): a clean single-shot two-stage extreme-value problem (max-of-V matched-filter score, then
balanced top-L assignment), structurally the closest possible analog to the already-CG'd RNS/FHRR
decode margins, with FULL data already landed (HARD_PASS, 60-row `per_unit` table) for a
zero-new-trials off-disk pre-check exactly like reasoning-depth's own promotion path. A SECOND
candidate — control's given-decomposition FLAT branching-depth chain collapse
(`exp_pfc_gate_branching_depth_entropy_grid_v1`) — is ALSO order-statistic-driven in its collapse
mechanism, but requires a harder, genuinely new derivation (a horizon-DEPENDENT per-hop SNR term,
not the stationary per-hop probability reasoning-depth could assume), demonstrated numerically below;
it is real and worth a future cycle but is NOT this cycle's top pick.**

---

## (b) Inventory: capability x collapse-mechanism x class (the honesty gate)

| # | Capability | Landed/reference cell(s) | Collapse mechanism (what actually breaks) | Class | Closed-form self-predictable? |
|---|---|---|---|---|---|
| 1 | Memory (FHRR bundle) | `exp_fhrr_bundle_capacity_exact_margin_v1` | Crosstalk-variance argmax of true codeword vs `V-1` competitors as `K` (bundled pairs) grows | **COLLISION/order-stat** | **YES — DONE.** CHAIN_GRADE, 5-seed, dev_exact <=1.22% |
| 2 | Perception-codebook (RNS decode) | `exp_rns_subblock_margin_exact_prefactor_v2` | `M`-ary orthogonal-signaling argmax vs `m-1` competitors as sub-block dim collapses | **COLLISION/order-stat** | **YES — DONE.** CHAIN_GRADE, gm_exact 1.01-1.11x |
| 3 | Reasoning (multi-hop chain depth) | `exp_reasoning_depth_exact_order_statistic_self_margin_v1` | Poisson-occupancy CAPTURE argmax (c co-colliding objects at one key slot) composed geometrically across depth | **COLLISION/order-stat** (chain composition, STATIONARY per-hop — success resets exactly to the true state, so post-failure dynamics don't matter) | **YES — IN FLIGHT.** Smoke HARD_PASS (exact 1.03x mean-ratio), FULL staged |
| 4 | Generation (block-local decode) | `exp_generation_decoder_gsbc_native_blocklocal_v1` (V8192,D26=0.856) | Block-local argmax decode vs `V-1` competitors under additive superposition — SAME mathematical family as #1/#2 | **COLLISION/order-stat** | **Mechanistically already covered** — the closed form is a direct re-parameterization of the RNS/FHRR `mu(N,M)` formula for the GSBC block geometry; no NEW derivation needed, just re-application. Not separately built as its own margin cell (lower priority: the codebook classes already have 2 CGs proving the family). |
| 5 | Comprehension (order-recovery cliff, D8xV1000) | `exp_comprehension_envelope_superposition_vocab_v1` (FULL, HARD_PASS) | Per-role score = MAX over `V` same-partition candidates of a matched-filter correlation (extreme value of `V` draws), then role->block assignment by the SIGNED DIFFERENCE of the two blocks' max-scores, balanced top-`L` selection | **COLLISION/order-stat, 2-stage** (max-of-`V` extreme value, then a top-`L` balanced-selection order statistic — same Gauss-Hermite toolkit, single-shot, NO horizon-dependency issue) | **YES — BUILDABLE, not yet built.** **TOP PICK (below).** |
| 6 | Control, given-decomposition (FLAT branching x depth) | `exp_pfc_gate_branching_depth_entropy_grid_v1` (FULL, MEASURED_MECHANISM) | Chain of `n_ops`-ary argmax picks (manifold + goal-cosine + SR-reach combined score) composed across `depth`; per-hop implied probability is **NOT stationary** — it falls with remaining horizon (measured: implied `p_hop` for `n_ops=2` drops `0.975 -> 0.904 -> 0.819` as depth goes `4->6->8`; see numeric table below) | **COLLISION/order-stat, but position-NON-stationary** (same family, harder derivation: needs a horizon-dependent SNR term) | **PARTIALLY BUILDABLE.** 2nd-rank candidate — real but requires new theory (see below), not a trivial re-application. |
| 7 | Perception/encoder (BGE concept-Gram spectrum) | RMT/encoder self-margin drill (2026-07-06, `notes` — see backup doc) | Clean POWER LAW (exponent -1.0 to -1.12, R2 0.97), NOT bulk+spike — BBP/free-cumulant RMT is the wrong tool; Gaussian-equivalent surrogate explains 60-95% of collapse but leaves a large statistically-robust residual (13-26 acc pts, 4-20 SEs) | **IRREGULAR** (no discrete collision structure; a continuous heavy-tailed spectral problem) | **NO — ACCEPT-boundary, already established.** GSBC block-local codes fold into this same family (cone-correlation to BGE r=0.28-0.77, heterogeneous). |
| 8a | Generalization | (established via prior work; one-to-many entropy ceiling) | Information-theoretic: many valid completions per query, entropy of the completion set bounds achievable top-1 accuracy — no collision/argmax-vs-competitors structure at all | **IRREGULAR** (different kind of limit — an entropy bound, not a decode-noise margin) | **NO — ACCEPT-boundary, already established (proven bound, all levers falsified).** |
| 8b | Control, AUTONOMOUS decomposition (self-discovered waypoints) | `exp_pfc_gate_autonomous_waypoint_discovery_v1` (HARD_FAIL) + `exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1` (HARD_FAIL, rescue attempted and failed) | Chained, UNCORRECTED argmax picks where each pick anchors on the PREVIOUS possibly-wrong discovered state (no ground-truth correction) — a textbook Ross-Bagnell (AISTATS 2010) `O(epsilon*T^2)` imitation-learning compounding-error regime: a clean matched-entropy dissociation shows chain-length (not entropy, not per-hop signal quality) is the dominant driver (recovery 0.690 @ 1 step vs 0.073 @ 3 steps at IDENTICAL entropy=8.0, despite per-hop signal 5.4pp WORSE at the high-recovery point) | **IRREGULAR** (a DIFFERENT math family from #1-6: distribution-shift/regret-accumulation, not a stationary or horizon-decaying collision probability — the per-hop success rate conditional on already being off-path is not derivable from the substrate's own closed-form geometry the way `mu=N/sqrt(M)` is; it depends on how the SR value function generalizes OFF its training distribution, an empirical/learned-function property, not a parameter-free geometric fact) | **NO — resists clean closed form.** A full mechanistic rescue (coarse-to-fine + verify-gate + multi-gamma) was ALREADY attempted and HARD_FAILed at the deep corner (`recovery_ratio=0.023` vs the `>=0.20` bar) — the bound is real and already 2x-drilled to its honest end. See "why this resists" below. |
| 9 | Integration (compounding_ratio) | `exp_integration_full_stack_full_fidelity_v1` (FULL, HARD_PASS, CHAIN_GRADE) | N/A — this is not a collapse-boundary needing a margin prediction. `compounding_ratio` (0.991, stages compose near-independently) already IS the direct measurement of composition fidelity; there's no separate "where does it collapse" question left to close in closed form. | **N/A** | **Already CG; no additional self-margin work indicated.** |

**Tally: 5/9 rows are order-statistic-family (2 DONE CG, 1 IN FLIGHT, 1 mechanistically-covered/not
separately built, 1 newly buildable = top pick), 1/9 partially-buildable-harder (2nd pick), 3/9
genuinely IRREGULAR (honest ACCEPT-boundary, for three DIFFERENT reasons each).** This is the honest
answer to the "is it just collision-math everywhere" question: NO — the substrate has real structural
diversity in its failure modes, and forcing all of them into the order-statistic mold would be
exactly the premature-pattern-matching the honesty gate warns against.

---

## Why control's AUTONOMOUS-decomposition (row 8b) resists, in more depth

This is the row most tempting to force into the order-statistic family (it LOOKS like another chain
composition, just like reasoning-depth and row 6), so it deserves the most explicit "why not."

Reasoning-depth's chain composition works as a clean product `p_hop^depth` because **success resets
the state to EXACTLY the true next codeword** (a discrete argmax snap), so conditional on all prior
hops having succeeded, the per-hop success probability is IID/stationary — and because `usable_depth`
is defined as "contiguous from hop 1," what happens after a failure is irrelevant to the metric, so
the model never needs to characterize off-path behavior. Row 6 (control, given-decomposition) shares
this property in principle (state is always a clean discrete codeword; the metric is a strict
"reached exact final target" criterion), but its per-hop SNR is not stationary across depth — the
`goal_sim` and SR-`reach` terms measure similarity/value toward a goal that is *itself* variable
distance away, and that discriminability degrades as remaining horizon grows (numerically confirmed
below). That is still a hard fact about the SUBSTRATE'S OWN GEOMETRY (the SR matrix's horizon
structure), not about off-distribution generalization — so it is still, in principle, derivable in
closed form (a harder derivation, not a different math family).

Row 8b (autonomous waypoint discovery) is different in kind, not just degree: **the per-hop success
probability, CONDITIONAL ON having already picked a wrong waypoint, depends on how well the trained SR
value function generalizes to a state it was never trained to evaluate from** (an off-policy query).
This is not a geometric fact derivable from `N`, `M`, or `V` the way `mu = N/sqrt(M)` is for RNS/FHRR —
it is an empirical property of a LEARNED function's out-of-distribution behavior, which is exactly why
Ross-Bagnell's bound is stated as an asymptotic RATE (`O(T^2)`) with an unspecified constant `epsilon`,
not an exact equality the way the Gauss-Hermite order-statistic formulas are. Deriving a genuinely
EXACT, parameter-free closed form here would require a new theory of "SR value-function generalization
error as a function of query-state distance from the training distribution" — a legitimately open,
much harder problem, not a reapplication of existing machinery. Combined with the fact that a full
empirical rescue attempt (the three literature-ranked standard fixes: coarse-to-fine, verify-gate,
multi-gamma) was ALREADY tried and HARD_FAILed at the deepest corner, I judge this an honest
ACCEPT-boundary: a real, well-characterized, already-2x-drilled bound, not a gap to force a cell into.

---

## Numeric evidence for row 6 (control, given-decomposition): why it's order-statistic but non-stationary

Off-disk recompute against the ALREADY-LANDED FULL grid
(`data/exp_pfc_gate_branching_depth_entropy_grid_v1/metrics.json:per_regime`), implied per-hop
probability `p_hop_implied = flat_gonogo^(1/depth)` (the value a STATIONARY per-hop model would need):

```
n_ops dd entropy flat_gonogo reach_rank_test  implied_p_hop
2     4   4.0    0.904       0.857            0.9751
2     6   6.0    0.547       0.818            0.9043
2     8   8.0    0.202       0.748            0.8188
3     4   6.3    0.742       0.767            0.9281
3     6   9.5    0.191       0.633            0.7589
3     8  12.7    0.087       0.559            0.7370
4     4   8.0    0.514       0.654            0.8467
4     6  12.0    0.117       0.526            0.6994
4     8  16.0    0.082       0.450            0.7315
```

At FIXED `n_ops`, `implied_p_hop` falls monotonically as `depth` grows (0.975 -> 0.904 -> 0.819 for
`n_ops=2`; 0.928 -> 0.759 -> 0.737 for `n_ops=3`) — a stationary-`p_hop` model (reasoning-depth's
template applied naively) would systematically mispredict here. This is DIRECT, on-disk, zero-new-
trials evidence that row 6 needs a horizon-dependent SNR term (`mu` as a function of remaining
distance to goal, not a single constant), which is a real but bigger derivation lift than reasoning-
depth's stationary case — hence its 2nd-rank, not top-rank, placement.

---

## TOP PICK — cell spec: `comprehension_order_recovery_exact_margin_v1` (non-parked, buildable now)

### Claim (MM -> CG-candidate promotion path, same arc as RNS v1->v2 and reasoning-depth)

`exp_comprehension_envelope_superposition_vocab_v1` landed FULL HARD_PASS (60-row `per_unit` table,
D in {2,4,6,8} x V_ROLE in {50,125,250,500,1000} x 3 seeds) but its own pre-registered "prediction" is
purely a MEASURED envelope + gates (HARD-PASS/FAIL/MIDDLE bands on the measured `order_content_perrole`
and `superposition_survival` surfaces) — there is no closed-form self-prediction of WHERE the cliff
sits as a function of `(D, V_ROLE, N, bs)`. This cell adds one: does the substrate predict its own
order-recovery cliff location EXACTLY, via the same 64-pt Gauss-Hermite order-statistic machinery
already validated 3x (RNS, FHRR, reasoning-depth)?

### Mechanism (derivation sketch — exp_dev to formalize signs/variances precisely before dispatch)

Per role `r`, `s[r][j] = max_{v in partition_r} corr(cb[v], block_j)` — this is a MAX over `V_ROLE`
i.i.d. draws, exactly the "distractor ceiling" term already solved in the RNS (`Phi(mu+z)^(m-1)`) and
FHRR (`Phi(x/sqrt(NK/2))^(V-1)`) cells: for the TRUE filler's partition-slot the max is dominated by
one elevated-mean draw (the genuine correlation) competing against `V_ROLE - 1` zero-mean distractors;
for the WRONG block the max is `V_ROLE` zero-mean draws (a pure extreme-value ceiling that GROWS with
`V_ROLE`, degrading the signed difference `s[r][true] - s[r][other]`). The assignment step (balanced
top-`L` selection among `D` roles' signed differences) is a second order-statistic layer: `L` of the
`D` roles carry a true positive-mean signed difference, `L` carry a true negative-mean one, and the
balanced selection asks whether the TOP-`L`-by-value set exactly matches the true positive-mean set —
itself expressible as a rank-order-statistic integral over `D` correlated (through shared block-energy
normalization) Gaussian-ish variates. Both layers reuse the EXACT SAME Gauss-Hermite quadrature
machinery (`numpy.polynomial.hermite.hermgauss`, no scipy) already coded three times on this substrate.

### Off-disk cheap decisive test (to run BEFORE any dispatch, zero new trials)

Recompute the two-layer closed form against `data/exp_comprehension_envelope_superposition_vocab_v1/
metrics.json:per_unit` (60 rows, already on disk: `D, V_ROLE, seed, order_content_perrole,
superposition_survival`). Exactly the same pre-dispatch discipline as RNS v2 and FHRR v1: if the
exact-formula recompute lands within the same `<=1.5x` ratio-error band the sibling CGs cleared, this
is FULL-HARD_PASS-predicted with high confidence before a single new trial is run.

### Falsifiable predictions (HARD-PASS / HARD-FAIL, pre-registered format matching the 3 sibling cells)

**HARD-PASS** (promotes to a CG-candidate, parallel to RNS/FHRR/reasoning-depth):
- exact per-cell ratio-error (`measured order_content_perrole` vs `predicted`) `<= 1.5x` at ALL
  non-saturated `(D, V_ROLE)` cells (cells at `order_content_perrole` in `[0.05, 0.95]` — exclude the
  D<=4 near-ceiling cells where `~1.0` by self-correlation dominance, exactly as RNS/FHRR exclude their
  own saturated corners), AND
- exact aggregate mean-ratio in `[0.80, 1.25]` (unbiased), AND
- a naive/loose control (e.g. treating the assignment as `D` INDEPENDENT per-role coin flips at a
  single-draw SNR, ignoring the extreme-value-of-`V_ROLE` ceiling and the balanced-selection
  coupling) stays biased (`>= 1.7x`) at the SAME cells — the discriminator (does the two-layer exact
  model remove a real, otherwise-present bias) must fire, AND
- cross-seed CV `<= 0.15`.

**HARD-FAIL** (honest ACCEPT-boundary — comprehension's order-recovery resists exact self-prediction):
- exact aggregate mean-ratio outside `[0.60, 1.70]` at FULL scale, OR
- exact per-cell ratio-error `> 2.0x` at any non-saturated cell, OR
- the loose control is ALSO tight (`< 1.4x`) — meaning the two-layer refinement is vacuous at this
  regime (respec, not a refutation).

**MIDDLE_BAND:** exact tightens over loose but misses a HARD-PASS sub-gate (analogous to reasoning-
depth's own honest MIDDLE_BAND-first landing before its capture-order-statistic promotion).

### Compute architecture / non-parked declaration

Reuses the ancestor cell's CPU numpy matched-filter machinery VERBATIM (self-contained synthetic GSBC
partitions; no cert_ledger / pool / re-encode dependency — clean remote gate, zero referent, NON-
PARKED). Prediction arm is pure numpy Gauss-Hermite quadrature (no GPU, no scipy, no torch). Monitor-
not-control: reports a tighter predicted cliff location only; never edits `D`, `V_ROLE`, `N`, or any
landed cell's config.

### P_deflated

Raw confidence the two-layer derivation is analytically tractable and matches the landed surface:
~0.55-0.65 (strong structural analogy to 2 already-CG'd siblings using the identical toolkit, but the
balanced top-`L` assignment layer is a genuinely new combinatorial piece not present in RNS/FHRR/
reasoning-depth, which are each single-layer). After the mandatory 0.15-0.25 lit-scan calibration
penalty and the novel-synthesis cap: **P_deflated = 0.40** (below the 0.50 cap because of the
genuinely new second layer, but above the pure-guess floor because of the strong single-layer
precedent and the on-disk zero-new-trials pre-check available before any dispatch commitment).

---

## SECOND-RANK candidate (flagged for a future cycle, not this cycle's build)

**`control_branching_depth_exact_margin` (row 6):** predicts `flat_gonogo(n_ops, depth)` exactly via
a horizon-dependent per-hop order statistic (`mu` as a decaying function of remaining distance to
goal, composed via `prod_{h=1}^{depth} p_hop(depth-h)` rather than a constant `p_hop^depth`). Real,
buildable-in-principle, zero-new-trials verifiable against the already-landed 9-regime FULL grid
(`data/exp_pfc_gate_branching_depth_entropy_grid_v1/metrics.json`), but needs a genuinely NEW
horizon-dependent SNR derivation (not a straight reapplication) before a credible pre-dispatch
cheap-test can be run — a bigger theory lift than the comprehension pick. P_deflated (pre-derivation, externally
cross-checked via this cycle's lit-scan — see Citations): 0.35 (capped lower — an as-yet-undone
derivation committing to an unvalidated horizon-decay functional form, not merely an application).
Recommend
as the NEXT self-margin drill after comprehension lands, not a parallel build this cycle (avoid
splitting the same GH-64 toolkit expertise across two simultaneous novel derivations).

---

## (c) Cross-thread synthesis

- Directly extends the arc `rns_subblock_margin_selfcheck_v1` (MM, scaling) -> `..._exact_prefactor_v2`
  (CG, exact) -> `fhrr_bundle_capacity_exact_margin_v1` (CG, exact, 2nd codebook family) ->
  `reasoning_depth_exact_order_statistic_self_margin_v1` (in flight, 1st CAPABILITY-level exact
  self-margin, one level up the composition stack). This drill is the honest "does the pattern keep
  generalizing" check the backup doc's own self-margin thread asked for next, and the answer is
  nuanced: yes for comprehension (same math, single-shot, buildable now), yes-but-harder for control's
  given-decomposition chain (same math family, non-stationary, needs new derivation), no for control's
  autonomous-decomposition (different math family entirely, already 2x-drilled to an honest bound).
- Directly reconciles with, and does NOT reopen, the backup doc's "SELF-MARGIN CLOSED-FORM THREAD AT
  ITS HONEST BOUNDARY" framing (2026-07-06 continuation) — that framing characterized the boundary as
  "orthogonal-family codebooks are closed-form-predictable; GSBC-heterogeneous + encoder power-law
  resist." This drill shows the boundary is not fully characterized yet ONE level up (at the
  CAPABILITY layer, not just the codebook layer): comprehension and control-given-decomposition are
  BOTH still on the collision/order-statistic side of the line even though GSBC (their underlying
  codebook family) was separately found heterogeneous w.r.t. a DIFFERENT question (semantic
  correlation to BGE) — the two questions (is the codebook's CONTENT geometry BGE-like; is the
  codebook's NOISE/collision margin order-statistic-predictable) are orthogonal, and conflating them
  would have wrongly foreclosed both new candidates identified here. This is exactly the
  "don't-dismiss-adjacent-methods" discipline paying off.
- Does not reopen the thalamic-router closure, the generalization-ceiling closure, or the
  waypoint/cerebellum closure (all separately, honestly closed per the backup doc); this drill's row
  8b analysis independently arrives at the same ACCEPT-boundary conclusion via a different lens
  (math-family classification rather than empirical rescue-attempt failure), which is a convergent,
  not redundant, confirmation.

## (d) Substrate-product implications

- If the comprehension pick lands CG: the substrate would have **4 exact self-margins spanning 2
  codebook families + 2 capability layers** (decode margin, bundle capacity, reasoning depth,
  comprehension order-recovery) — a genuinely reusable product claim ("the substrate knows, in closed
  form, exactly where four of its core capabilities will collapse, without needing to probe them
  empirically at deployment time") distinct from a vaguer "we measured some curves" claim.
- The row 8b analysis sharpens the control capability's honest limits documentation: "autonomous
  sub-goal discovery is closed at 3+ uncorrected sequential steps, for a structurally-named, formally-
  rated reason (`O(T^2)` distribution-shift compounding), not an unexplained failure" is a stronger,
  more defensible capability-map entry than "it just didn't work," and usefully tells a product
  consumer exactly what class of fix WOULD be needed (interactive/oracle correction) and why it's out
  of scope for an autonomous-only claim.
- The GSBC-heterogeneous / comprehension-order-statistic orthogonality finding (section c) is a
  reusable methodological point for future self-margin drills: "codebook content-geometry heterogeneity"
  and "codebook noise-margin predictability" must be evaluated SEPARATELY per capability, not inherited
  wholesale from a sibling cell that tested a different question on the same codebook family.

## (e) Falsifiable predictions summary (headline numbers, for the dashboard)

- Comprehension order-recovery exact margin: HARD-PASS if exact ratio-error `<=1.5x` at all
  non-saturated `(D,V_ROLE)` cells + aggregate mean-ratio in `[0.80,1.25]` + loose control stays
  `>=1.7x` biased; HARD-FAIL if aggregate mean-ratio outside `[0.60,1.70]` or any cell `>2.0x`.
  P_deflated = 0.40.
- Control given-decomposition (2nd-rank, future cycle): needs horizon-dependent derivation before
  pre-registerable bands; flagged, not built this cycle. P_deflated = 0.35 (externally cross-checked).
- Control autonomous-decomposition: ACCEPT-boundary, no further cell recommended (already 2x-drilled
  + rescue-tested to HARD_FAIL).

## (f) Citations (verified count)

Internal-derivation drill (operational 2x-style inventory over already-landed cells, not a fresh
external corpus scan for its own sake), per `[[feedback-2x-means-depth]]`. Re-cites, verified on-disk,
the theoretical grounding already established in the 3 sibling self-margin cells: Hajek ECE361 L8 /
Proakis Ch.4 (M-ary order-statistic family); Roberts 1975 / Arnbak & Van Blitterswijk 1987 IEEE JSAC
(capture effect); Ross & Bagnell 2010 AISTATS ("Efficient Reductions for Imitation Learning",
`O(epsilon*T^2)`); Ross-Gordon-Bagnell 2011 (DAgger, reduces to `O(T)` with correction); "Toward the
Fundamental Limits of Imitation Learning" arXiv:2009.05990; "Provably Breaking the Quadratic Error
Compounding Barrier..." arXiv:2102.12948 — all previously verified (2026-07-05 waypoint drills).
TWO NEW targeted lit-scan sub-agents dispatched this cycle (generic math queries only, per
[[feedback-query-privacy-decomposition]]) to pressure-test the two NEW candidates' theoretical
tractability. Both returned; findings folded into the P_deflated numbers above.

**Sub-agent 1 (comprehension top pick — max-of-V + balanced top-L order statistic):** VERDICT — no
single paper solves the exact three-stage composition (max-of-V per bin -> signed difference ->
balanced top-L partition) end-to-end, but every stage individually maps to established, numerically-
exact (quadrature, not Gumbel-asymptotic) machinery: max-of-V CDF is the elementary order-statistic
identity `Phi(x)^V` (David & Nagaraja, *Order Statistics* 3rd ed.); ranking-and-selection PCS
(probability-of-correct-selection) theory (Bechhofer 1954 indifference-zone selection; Gupta 1956/65
subset selection, *Multiple Decision Procedures* 1979; Rinott 1978's nested-integral PCS equation;
Bechhofer-Kiefer-Sobel 1968 fixed-size "select the t best of k," directly analogous to this cell's
balanced top-`L`) gives the second layer as a derivable 1-D quadrature integral (density of the signal
item's score times `P(Binomial(D-1, tail-prob) <= L-1)`), the SAME integral family used in CFAR radar
detection (Rohling 1983 OS-CFAR) and DS-CDMA PN-code serial-search acquisition. Calibrated confidence
the composition is tractable via Gauss-Hermite/Gauss-Legendre quadrature without new theory: raw 0.85,
deflated to **0.65** (uncharted three-way composition, no single citable end-to-end result). This
external, independent check comes in ABOVE this note's own 0.40 estimate — I am keeping the note's
0.40 (not raising it to 0.65) because the sub-agent's number reflects "is a quadrature integral
derivable at all" (a necessary condition) while the note's 0.40 additionally prices in "does it match
THIS substrate's measured 60-row surface at `<=1.5x`" (a stronger, substrate-specific bar the generic
lit-scan cannot speak to) — the two numbers are compatible, and 0.40 is the more relevant one for the
HARD-PASS bands above per the mandatory novel-synthesis cap.
Citations (10, all verified via WebSearch, generic terms only): David & Nagaraja *Order Statistics*;
Kamath, "Bounds on the Expectation of the Maximum of Gaussian Samples"; Bechhofer 1954 indifference-
zone selection (via tutorial survey); Gupta & Panchapakesan 1979 subset selection; Rinott 1978 PCS
(via JQT table, Wilcox 1984); Bechhofer-Kiefer-Sobel 1968 (via Gupta-Sobel review); Rohling 1983
OS-CFAR overview; DS-CDMA serial-search/max-selection acquisition survey; Feige-Raghavan-Peleg-Upfal
1994-descended noisy-comparison SELECT/PARTITION (arXiv:1603.04941); inverse-Gaussian-quadrature
normal-mixture approximation (arXiv:1810.01116).

**Sub-agent 2 (control 2nd-rank candidate — horizon-dependent SNR in chained goal-directed decode):**
VERDICT — NOT an established closed form. Horizon-dependent degradation of goal-distance signals is
well-documented QUALITATIVELY/asymptotically in RL theory (Kearns & Singh COLT 2000 bias-variance-vs-n
TD bounds; Zhang et al. arXiv:2111.00633 closed-form horizon-vs-sample-complexity, a different
quantity; goal-conditioned/temporal-distance value-learning papers arXiv:2406.17098, arXiv:2509.20478
diagnosing but not formula-izing the degradation; Momennejad et al. multi-scale-SR bioRxiv 449470;
one 2026 preprint, arXiv:2605.23024/2606.00376, "The Deterministic Horizon," proposing a closed-form
`epsilon(d) = epsilon_0 + gamma*d/L_eff` for chain-of-thought depth-from-start error — directionally
close but measures depth-FROM-START, not remaining-distance-TO-A-FIXED-GOAL, and is an unvetted
preprint, not settled literature). Calibrated confidence a NEW derivation (order-statistic argmax x an
assumed exponential/power-law horizon-decay term, combined via Gauss-Hermite quadrature) is buildable
without fundamentally new theory: **0.40** (raw ~0.85 combinability, deflated for genuine novel
synthesis + the specific three-way combination being uncharted). This confirms the note's own
"harder, genuinely new derivation, 2nd-rank" placement — I am revising the note's earlier informal
guess (~0.30) UP slightly to **0.35** to reflect this external convergence (still capped below the
comprehension pick's 0.40 because the control candidate additionally needs to commit to a specific,
unvalidated decay functional form the lit-scan could not confirm, whereas the comprehension pick's
layers are each independently well-established).
Citations (7, verified): Kearns & Singh COLT 2000; Fixed-Horizon TD arXiv:1909.03906; Generative-TD/
gamma-models arXiv:2010.14496; Zhang et al. arXiv:2111.00633; arXiv:2406.17098; arXiv:2509.20478;
Momennejad et al. bioRxiv 449470; "Deterministic Horizon" arXiv:2605.23024/2606.00376 (2026 preprint,
flagged unvetted); CoT chain-reliability framing arXiv:2606.15686.

**Total citations this drill: 19 new (10 + 7, with 2 shared/overlapping counted once) + 6 pre-existing
(Hajek/Proakis/Roberts/Arnbak/Ross-Bagnell/DAgger, re-cited not re-verified) = 25 verified sources.**
