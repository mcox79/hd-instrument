# Research (cross-domain, self-authored, no sub-agents): does STACKING independent corrections push the
# compounding-reasoning-drift frontier further, and what is the correctness-calibrated selector to stack with
# the just-landed KB-grounded gate?

**Date:** 2026-07-09. **Trigger:** the KB-grounded exogenous-check cell (`pfc_gate_waypoint_rescue_kb_grounded_check_v1`,
verdict `MIDDLE_BAND_FLATNESS_BELOW_50`, tier atom referenced in dispatch as `BARRIER2_REFINED`) landed and PUSHED
the compounding-drift frontier from entropy-8 (where four self-derived rescue variants sat at recovery~0.02-0.03)
out to entropy-12 — but the grounded rescue itself decays with depth. Question: does control theory / AI / biology
/ physics predict that STACKING a second, genuinely independent correction channel with the KB-gate suppresses the
compounding wall SUPER-linearly (pushes the frontier further than either alone), and what is the buildable design?

**Verified off-disk before drilling (per Fix#28, re-derived from `metrics.json`, not requoted from the dispatch brief):**
`data/exp_pfc_gate_waypoint_rescue_kb_grounded_check_v1/metrics.json`, `run_mode=full`, `n_seeds=5`,
`cardinality_ok=true`, `completed_units=300/300`.

| regime | entropy | chain_steps | recovery_rescue (`wp_kb_grounded_gate`) | flatness_ratio | `hp_ok` | `kb_fresh_rate` | `independence_corr` |
|---|---|---|---|---|---|---|---|
| `op4_V1200_d4` | 8.0 | 1 | 0.9257 | 1.00 (anchor) | false | 0.000 | -0.363 |
| `op4_V1200_d6` | 12.0 | 2 | 0.4864 | 0.525 | **true** | 0.013 | 0.069 |
| `op4_V1200_d8` | 16.0 | 3 | 0.2444 | 0.264 | false | 0.063 | 0.047 |

`rescue_capability_frontier="op4_V1200_d6"`, `max_entropy_hp_ok=12.0`, `spearman_delta_vs_entropy=-0.205`
(delta-over-verify shrinks as entropy grows — the decay is real, not noise). The decay is a strikingly clean
geometric sequence: `0.4864/0.9257=0.5255`, `0.2444/0.4864=0.5025` — **within measurement noise of a constant
~0.51x per added chain-step**, i.e. the grounded channel is not "eventually failing," it is decaying at a
**steady per-hop hazard rate**, and `kb_fresh_rate` (fraction of hops where no confirmed KB edge exists, forcing
a reset) is rising in lockstep (0.000 -> 0.013 -> 0.063) as entropy/depth grow. This is the load-bearing empirical
clue this whole drill pivots on (see HEADLINE point 2).

---

## HEADLINE

**1. Theory says YES — stacking independent correction channels suppresses error multiplicatively (exponentially
in the number of channels), not merely additively, and this is the SAME underlying law across four unrelated
fields, confirmed with an exact formula in two of them:**

- **Kinetic proofreading (Hopfield 1974/Ninio 1975):** if one independent test fails to catch a mismatch a
  fraction `p` of the time, `N` independent tests fail only `p^N` of the time — Hopfield's own stated
  equivalence is that `N` successive tests each worth free-energy `dF` are thermodynamically identical to ONE
  test worth `N*dF`. This is a literal multiplicative (exponential-in-N) law, not additive.
- **Concatenated error-correcting codes (Forney 1966):** inner-code + outer-code combined minimum distance
  scales as `D' >= d_inner * d_outer` (multiplicative), and for L-level concatenation the residual failure rate
  is an L-fold exponentially-decreasing function of L — the same "product of independent-stage survival
  probabilities" law as kinetic proofreading, in a completely different field.
- **Quantum error correction (cyclic/repeated syndrome extraction):** independently confirmed literature term
  "exponential suppression of bit or phase errors with cyclic error correction" — same law again, physical
  substrate.
- **Chain-of-thought verifier theory (2026 PAC-learning-for-verifiers literature):** a learned, sufficiently
  independent verifier is stated to "exponentially amplify reliability," and error/abstention rates of a
  verifier-gated generator are bounded in terms of the verifier's own soundness/completeness mistake bounds —
  the AI-native version of the identical structural claim.

**The unifying formal statement:** if two correction channels independently catch an error with probabilities
`a` and `b` (i.e. their FAILURE events are independent), the probability an error escapes BOTH is `(1-a)(1-b)`,
not `1 - a - b`. Compounded across `depth` hops, escape probability is `[(1-a)(1-b)]^depth` — an ADDITIONAL
`(1-b)^depth` suppression factor on top of whatever channel `a` alone achieves. **Because the wall itself is
exponential in depth, any genuinely independent per-hop improvement gets exponentially amplified in its effect
on how far the frontier extends** — this is not a modest constant-factor gain, it is specifically the kind of
lever that should show up as "the frontier moves from entropy-12 to entropy-16 or beyond," not just "recovery at
entropy-16 ticks up a few points." This directly explains, post-hoc, why the KB-gate alone already produced a
big, discrete frontier jump (entropy-8 -> entropy-12) rather than a smooth uniform lift across all entropies:
depth-compounded gains from an independent channel are inherently front-loaded at exactly the frontier boundary.

**2. The sharpest caveat, and the reason this is NOT a free lunch — the current decay pattern is itself evidence
of a likely SHARED failure cause, which would blunt naive multiplicative stacking:** `kb_fresh_rate` (KB has no
confirmed edge -> forced reset) climbs from 0.0% to 1.3% to 6.3% as entropy/chain_steps grow, while the KB's raw
edge coverage is presumably fixed/static regardless of task entropy. The clean, steady ~0.51x-per-step decay
looks exactly like what you'd get if **branching factor / reachable-state-space grows faster than fixed KB
edge density**, i.e. a coverage-density problem, not a "this specific channel design is flawed" problem. **If a
second, differently-designed correction channel (a calibrated selector) ALSO ultimately depends on the same
underlying evidence density (however indirectly) to make correct per-hop judgments, its failure mode will be
correlated with the KB-gate's failure mode even if its point-estimate is uncorrelated with the raw `M`/`R`
error** (`independence_corr` — the OLD screen) — because correlated FAILURE MODES and correlated POINT
ESTIMATES are different things, and only one of them is currently screened for. **This is the single most
important design implication of this drill: the existing independence screen (`corr(signal, M_error)`) is
necessary but not sufficient for stacking to pay off multiplicatively; a NEW, second screen —
`corr(channel_A_failure_mask, channel_B_failure_mask)` — must be added and must ALSO be near-zero, or stacking
degrades to redundant/sub-additive gain despite both channels individually passing the existing screen.** Control
theory names this precisely: two "independent" sensors that are both secretly slaved to the same unobserved
common-cause state (here: local KB coverage density) do not add independent Fisher information even if their
individual noise processes are formally uncorrelated with the state estimate being corrected — this is the
textbook failure mode in multi-sensor Kalman fusion when sensors share an unmodeled common bias/error source, and
it is exactly the risk this drill's stacked-cell design must pre-register against.

**3. Cross-domain convergence on WHERE the calibrated-selector's independence must come from:** "Calibrated
Selective Classification" (arXiv:2208.12084) trains a rejection/confidence head `g` SEPARATELY from the base
model `f`, using an S-MMCE calibration loss on held-out data with adversarially-simulated distribution shifts —
directly transferable design pattern. Critically, their `g` still consumes meta-features DERIVED FROM `f`'s own
outputs (confidence, entropy, outlier score) — this is a WEAKER independence than what this drill's headline
diagnosis (Rank-3 screen, prior drill) demands. The double-machine-learning / cross-fitting literature (Chernozhukov
et al.) gives the rigorous fix: independence by CONSTRUCTION via disjoint sample-splitting — nuisance-function
estimation and target-parameter estimation are trained on non-overlapping folds specifically so their errors
cannot share optimizer noise or training-corpus correlation (the exact failure diagnosed in the prior drill for
`M` vs `M_rev`). The calibrated-selector design below adopts cross-fitting, not meta-feature dependence, as its
independence mechanism.

**4. Finer frontier map (lever 3) — physics predicts this should be a SMOOTH exponential decay, not a percolation
cliff, and the data so far agrees:** random-graph percolation theory has two distinct, well-separated thresholds
— a giant-component threshold at mean-degree `~1/n` (sharp, discontinuous-looking even at scale) and a FULL
connectivity threshold at `p > (ln n)/n` (a much higher bar). If the KB-coverage-vs-branching-factor picture in
point 2 is right, a genuine percolation-style cliff would show a sudden, sharp drop in recovery across a narrow
entropy window, not the steady ~50%-per-step geometric decay actually measured across three consecutive points.
**Honest prediction: the entropy 8->20 sweep will show continued smooth geometric decay (soft frontier), not a
sharp wall**, meaning the practical fix is either (a) more independent channels (this drill) or (b) increasing
raw KB coverage density (a data problem, addressed separately) — NOT waiting for/hunting a discrete critical
point. This is falsifiable: a sudden drop of ratio well below 0.3 at some single entropy step, followed by
flattening, would instead indicate a genuine percolation-like coverage threshold and redirect the fix toward KB
density rather than channel count.

---

## Correctness-calibrated selector: design (provably independent of the SR/`M` estimator's error, by construction)

```
# Cross-fitting split (per double-ML / Calibrated-Selective-Classification literature):
# SR/M training corpus and selector calibration corpus are DISJOINT folds -- never share a trajectory,
# a training epoch, an optimizer instance, or a noise seed. This is independence BY CONSTRUCTION, not
# an empirical hope, per [[cross-fitting]] citations below.

def selector_features(anchor, candidate, raw_kb_edges) -> FeatureVec:
    # Every feature below is computed from RAW graph structure or non-learned heuristics --
    # zero shared computation, zero shared parameters, zero shared training noise with M/R.
    return FeatureVec(
        kb_out_degree(anchor, raw_kb_edges),          # raw structural, not SR-derived
        kb_path_count_bfs(anchor, candidate, raw_kb_edges, max_hops=2),  # raw BFS, not R-matrix lookup
        admissible_lower_bound_h(anchor, candidate),  # non-learned heuristic (A*-style h(n))
        held_out_historical_hitrate(candidate_type, calib_fold),  # frozen calibration fold, disjoint from SR train
    )

def train_selector(calib_fold):  # calib_fold disjoint from SR/M training fold, by construction
    # small, non-SR model family (e.g. gradient-boosted trees / logistic regression on selector_features) --
    # deliberately a DIFFERENT architecture/inductive bias, not a second neural net sharing M's optimizer
    raw_selector = fit_classifier(selector_features, ground_truth_correct, calib_fold)
    calibrated_selector = isotonic_regression(raw_selector, held_out_calibration_labels)
    return calibrated_selector

def wp_calibrated_selector_gate(start, goal, R, raw_kb_edges, calibrated_selector, tau) -> boundary_seq:
    # at each hop: accept M/R's top candidate if EITHER channel independently confirms
    # (OR-gate, kinetic-proofreading-style: escape requires BOTH independent checks to miss)
    for candidate in topk(R):
        if kb_confirms_edge(anchor, candidate, raw_kb_edges) or calibrated_selector(features) >= tau:
            commit(candidate); break
    else:
        reset_fresh_from_kb(start, goal)  # ARM_C_FRESH-style, never carry an unconfirmed pick forward
```

**Mandatory pre-registration screens (both required, the second is NEW):**
1. `corr(calibrated_selector_confidence, M_error)` (existing Rank-3 screen, extended to the new channel) — predict
   near-zero by cross-fitting construction.
2. `corr(kb_gate_failure_mask, selector_failure_mask)` (**NEW** — this is the point-2 caveat operationalized) —
   predict this is the harder one to pass; if it comes back high, stacking will be sub-additive regardless of
   screen 1, and the honest read is "both channels are secretly reading the same coverage-density signal."

---

## (b) Cheap decisive test — buildable cell

**Step 0 (near-zero cost, do FIRST):** retroactively compute `corr(kb_gate_failure_mask, X)` for every feature
already logged in `metrics.json` per-seed arrays for the landed KB-gate cell (`kb_fresh_rate`, `kb_confirm_std`,
entropy, chain_steps) — if `kb_fresh_rate` alone predicts most of the KB-gate's residual failure (which the
0.0/0.013/0.063 progression strongly suggests), this is a free, no-new-compute confirmation of point 2's
diagnosis before any new dispatch.

**Step 1 (smoke, reuse ancestor grid verbatim):** `N=2048`, `V=300`, 3 seeds, `op4_V300_d6` FOCUS, `chain_steps=2`,
per standing SMOKE=FULL branch-parity discipline. New arms: `wp_calibrated_selector_gate` (standalone, no KB) and
`wp_stacked_kb_plus_selector` (OR-gate combination per pseudocode above).

**Step 2 (FULL, if smoke clears):** identical 5-regime grid as the landed KB-gate cell
(`op4_V1200_d4/d6/d8`, `op3_V1000_d8`, `op2_V800_d8`), paired seeds `[7,17,23,31,41]`, reusing
`wp_bisect_verify`/`wp_replay_generate_select`/`wp_kb_grounded_gate` verbatim as required-already-measured
controls (no new information, paired comparison only). THREE new arms: `wp_calibrated_selector_gate` (standalone),
`wp_stacked_kb_plus_selector` (combined), plus the two mandatory correlation screens above.

**Step 3 (only if Step 2 clears HARD-PASS or strong MIDDLE_BAND):** extend the entropy sweep to `d10`/`d12`
equivalents (entropy ~20, per lever 3) on whichever arm(s) survived, to map where the now-pushed frontier
actually sits and whether decay stays geometric (predicted) or shows a percolation-like cliff (point 4).

---

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE_BAND)

All quantities computed exactly as the landed KB-gate cell's schema (`recovery_rescue`, `flatness_ratio`,
`delta_recovery`, `independence_corr`) so results are directly comparable; FOCUS = `op4_V1200_d8` (entropy=16,
chain_steps=3), reusing `op4_V1200_d6` (entropy=12) as the "already-cleared" comparison point.

**HARD-PASS (super-additive/multiplicative stacking confirmed — frontier genuinely extends):**
- `recovery_rescue(wp_stacked_kb_plus_selector)` at FOCUS `>= 0.35` (materially above KB-alone's 0.2444) **AND**
- **super-additivity, not just "the better of the two":** `gain(stacked) > gain(kb_alone) + gain(selector_alone)`
  where `gain = recovery_rescue - recovery_verify` (0.0182 baseline) — this is the operational test for
  "multiplicative," distinguishing real stacking from picking whichever channel is locally better **AND**
- `flatness_ratio(stacked)` at `d8` `> 0.264` (KB-alone's measured flatness) by `>= 0.10` absolute **AND**
- `corr(selector_confidence, M_error) <= 0.15` **AND** `corr(kb_gate_failure_mask, selector_failure_mask) <= 0.20`
  (**the new, harder screen — this is the one point 2 predicts is most likely to fail**) **AND**
- `hp_ok` extends to `op4_V1200_d8` (entropy=16) or beyond — i.e. `max_entropy_hp_ok > 12.0`, the literal
  frontier-push criterion **AND** honesty guards at ancestor thresholds (`index_artifact_gap<0.05`,
  `anti_tautology_corr<0.85`, `degenerate_rate<0.10`, `cv<0.15`, `sign_p<0.05` paired vs KB-gate alone).
=> the wall is specifically a single-channel-independence deficit, not a coverage/entropy floor; stacking
independent corrections is a general, reusable lever for this capability class, matching the
kinetic-proofreading/concatenated-code/QEC/verifier-theory convergence.

**HARD-FAIL (stacking is redundant — the point-2 shared-cause diagnosis is confirmed):**
- `recovery_rescue(wp_stacked_kb_plus_selector)` at FOCUS `<= recovery_rescue(wp_kb_grounded_gate) + 0.03`
  (i.e. `<= 0.274` — no material improvement over KB-alone despite a genuinely differently-designed,
  cross-fit-independent second channel) **OR**
- `corr(kb_gate_failure_mask, selector_failure_mask) > 0.5` (the two channels' failures are strongly correlated
  — confirms the shared-coverage-density-cause diagnosis directly) **OR**
- `gain(stacked) <= max(gain(kb_alone), gain(selector_alone))` (purely redundant, no combination benefit at all).
=> this would be a mechanistically INFORMATIVE hard-fail (unlike the four prior self-referential failures): it
would confirm that BOTH channels are ultimately reading the same underlying coverage-density signal through
different windows, meaning the fix is a DATA problem (grow KB edge density at the frontier regime) not a
channel-count problem — a specific, actionable redirect, not a generic "wall is fundamental" closure.

**MIDDLE_BAND:** additive-but-not-superadditive gain (`gain(stacked)` in `[gain(kb)+gain(sel)*0.5,
gain(kb)+gain(sel))`), or `corr(failure masks)` in `(0.20, 0.5]` (partial correlation — some genuine independent
signal, but contaminated by the shared coverage-density cause) — report as "stacking adds real but
sub-multiplicative value; the shared coverage-density cause is real but not total."

**Honest prior:** raw ~0.35 for MIDDLE-or-better (theory strongly favors SOME stacking benefit — four fields
converge on the multiplicative law, and this is a mechanistically well-motivated design, not a guess) ->
**P_deflated ~0.15-0.20** after the mandatory 0.15-0.25 lit-scan calibration penalty. **P(full HARD-PASS, frontier
literally extends past entropy-12): raw ~0.20** (point 2's shared-cause diagnosis is a real, data-grounded
concern — `kb_fresh_rate`'s clean monotonic rise makes "the two channels share a bottleneck" a live, not merely
hedged, possibility) -> **P_deflated ~0.10-0.12**, well under the mandatory 0.50 novel-synthesis cap. This is the
**6th attempt on this wall overall** (four self-referential failures + one exogenous-grounding MIDDLE_BAND) but
the **first that (a) explicitly targets a NEW, cross-domain-converged failure mode (correlated failure masks, not
correlated point-estimates) and (b) is falsifiable in a way that is informative even on HARD-FAIL** (redirects to
a data-coverage fix rather than closing the capability outright) — flagged **HIGH-PROB-SUPERIOR relative to a
naive 7th self-referential variant**, but NOT flagged high-prior in absolute terms; the point-2 caveat is the
single largest risk to the whole thesis and is exactly what Step 0's near-zero-cost retroactive check should
resolve before any new dispatch.

---

## (d) Cross-thread synthesis

- **Directly extends** `notes/research_compounding_error_bound_5x_drill_new_mechanism_class_cross_domain_2026-07-09.md`
  (this same day): that drill's Rank-1 pick (exogenous KB-grounded gate) has now LANDED as `MIDDLE_BAND_FLATNESS_BELOW_50`
  with a real, measured frontier push (entropy-8 -> entropy-12) exactly as predicted, and its Rank-6 finding
  ("confidence calibration degrades under distribution shift; any future confidence-based selector must be
  calibrated against exogenous labels") is the direct blueprint for this drill's calibrated-selector design — this
  is not a new idea invented fresh, it is that drill's own Rank-6 caution turned into a buildable, cross-fit-based
  design now that Rank-1's KB-gate has proven the exogenous-independence principle works empirically.
- **Sharpens** the prior drill's Rank-3 (Kalman-observability independence screen) by identifying that it is
  necessary but NOT sufficient for STACKING specifically — the new failure-mask-correlation screen is a genuine
  addition to standing discipline, not a restatement.
- **Extends** `notes/research_deep_chain_reasoning_bounded_compounding_error_brain_first_2026-07-08.md` and
  `notes/research_community_routed_glassbox_reasoning_scale_invariant_brain_first_2026-07-08.md`: the same
  fresh-grounding-vs-carried-forward-estimate principle (`ARM_C_FRESH` HARD_PASS, slope=0.0010 vs
  `COMPOUND` slope=0.0976) is reused here as the reset-fallback branch of the stacked-gate pseudocode.
- Does not reopen unrelated closures (option-critic/BlocksWorld, algebraic-topo, quantum-info, dynamics fields)
  per `[[feedback-prior-work-informs-not-constrains]]`.
- Recommend Rank-3's independence screen (now doubled — signal-vs-estimator AND failure-vs-failure) become a
  STANDING pre-registration requirement for ANY future multi-channel correction cell, not just this one.

## (e) Substrate-product implications

- **If HARD-PASS:** the product story upgrades from "we found ONE fix for autonomous multi-hop drift" to "drift
  correction is a composable, stackable capability with a general design pattern (exogenous grounding + cross-fit
  calibrated selection, OR-gated, reset-on-miss) that follows the same multiplicative-suppression law used in DNA
  replication fidelity, modern error-correcting codes, and verified reasoning theory" — a materially stronger and
  more differentiated claim, and one with a clear NEXT lever (a third independent channel) rather than a dead end.
- **If HARD-FAIL via the correlated-failure-mask route specifically:** this is the FIRST diagnostically actionable
  negative in this whole 6-attempt sequence — it says the bottleneck is raw KB coverage density at high
  entropy/depth, not mechanism design, and redirects effort to a concrete, measurable data-engineering fix (grow
  edge density in the specific regimes where `kb_fresh_rate` is high) rather than a 7th mechanism attempt or
  outright capability closure.
- Either outcome, the **failure-mask-correlation screen** should be added to the standing pre-registration
  checklist for compounding-error rescue candidates (extends the existing Rank-3 discipline), and the
  **percolation-vs-smooth-decay distinction (lever 3)** should be tracked as a general diagnostic for any future
  "does X capability have a hard wall or a soft frontier" question in this program — it is cheap (reuses existing
  metrics fields) and directly actionable either way.

---

## Citations (verified count: 15, all live-URL-confirmed via WebSearch/WebFetch this session, generic
math/science terms only per `[[feedback-query-privacy-decomposition]]`; no substrate-specific framing exposed
off-platform)

1. Hopfield, J.J. (1974), "Kinetic proofreading," PNAS — `p^N` multiplicative error-suppression law, N
   independent tests = 1 test at N*dF, via Wikipedia "Kinetic proofreading" (fetched directly).
2. Ninio, J. (1975), independent co-discovery of kinetic proofreading (re-confirmed, reused from same-day
   ancestor drill).
3. "Speed, dissipation, and error in kinetic proofreading," PNAS 10.1073/pnas.1119911109 (search-confirmed
   discrimination-ratio scaling `(e^(E1-E2))^N`; direct fetch blocked HTTP 403, formula corroborated via
   WebSearch summary + Wikipedia direct fetch).
4. Concatenated error correction code — Wikipedia (fetched directly): multiplicative minimum-distance scaling
   `D' >= d_inner * d_outer`; L-fold exponentially-decreasing failure rate for L-level concatenation.
5. Forney, D. (1966) concatenated codes origin, via Wikipedia citation above.
6. "Exponential suppression of bit or phase errors with cyclic error correction," PMC8279951 (quantum error
   correction, same multiplicative-suppression law, independent physical substrate).
7. "On Learning Verifiers for Chain-of-Thought Reasoning," arXiv:2505.22650 / OpenReview — verifier soundness
   bounds generator error rate; "exponentially amplify reliability" via learned verifier.
8. "Online Learnability of Chain-of-Thought Verifiers: Soundness and Completeness Trade-offs," arXiv:2603.03538.
9. Ross, Gordon, Bagnell (2011), DAgger — external-oracle query converts `O(T^2)` to `O(T)` regret (reused,
   re-confirmed context from same-day ancestor drill; theoretical ceiling framing for the calibrated-selector's
   cheap in-substrate approximation).
10. "Calibrated Selective Classification," arXiv:2208.12084 (fetched directly) — S-MMCE loss, held-out
    adversarially-shifted calibration data, selector trained separately from base model (design template,
    with the noted limitation that their `g` still uses `f`-derived meta-features).
11. Chernozhukov et al., Double/Debiased Machine Learning — cross-fitting/sample-splitting for independence
    BY CONSTRUCTION between nuisance-function estimation and target estimation (search-confirmed via multiple
    2026 cross-fitting papers, e.g. arXiv:2605.15856 "crossfit" engine).
12. "Machine learning for causal inference: on the use of cross-fit estimators," PMC8012235.
13. Kalman filter multi-sensor fusion — ScienceDirect/PMC12609212/PMC8434080 (search-confirmed): centralized,
    distributed, sequential fusion architectures theoretically equivalent under cross-uncorrelated noise;
    corroborates the point-2 caveat (fusion gains require genuinely uncorrelated sensor noise, not just
    formally-independent point estimates).
14. Percolation theory / giant-component threshold vs full-connectivity threshold — emergentmind "Percolation
    Phase Transition"; giant component at mean-degree ~1/n (sharp), full connectivity at `p > (ln n)/n` (higher
    bar) — used for the smooth-decay-vs-cliff falsifiable prediction (lever 3).
15. Condorcet's Jury Theorem / ensemble independence requirements — Wikipedia; competence + independence as
    the two necessary conditions; explicit literature caveat that identically-trained ensemble members produce
    correlated errors and reduced gains (direct precedent for the point-2 caveat in a third, unrelated field).

All searches used generic math/science terms ("kinetic proofreading error rate formula independent stages,"
"concatenated error correcting codes multiplicative error rate," "sensor fusion Kalman filter independent
measurement channels," "Condorcet jury theorem superlinear error reduction," "selective prediction calibration
cross-fitting distribution shift," "percolation threshold giant component versus smooth exponential decay,"
"double machine learning cross-fitting independence nuisance estimator") — no substrate-novel mechanism names,
cell names, configs, or numerical parameters were exposed off-platform, per `[[feedback-query-privacy-decomposition]]`.
One `metrics.json` file was read locally (not searched externally) for verified-off-disk grounding, per Fix#28.
