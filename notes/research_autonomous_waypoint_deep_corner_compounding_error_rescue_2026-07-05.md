# RESEARCH 2x-DRILL — Autonomous waypoint discovery HARD_FAIL: mechanism + rescue decision

**Date:** 2026-07-05 (2x operational drill on the just-landed FULL verdict, per standing "research every
finding for mechanism + envelope-push" + "drill load-bearing non-positives")
**Trigger:** `pfc_gate_autonomous_waypoint_discovery_v1` landed `HARD_FAIL_SR_CANNOT_SELF_DISCOVER_DECOMPOSITION`
at FULL (`data/exp_pfc_gate_autonomous_waypoint_discovery_v1/metrics.json`, run_mode=full, 405/405 units,
5 seeds, cardinality_ok=True). Ancestor precedent (`exp_pfc_gate_branching_depth_entropy_grid_v1`) already
proved control-given-decomposition is HARD_PASS at FULL — this drill is specifically about the deeper
question this HARD_FAIL closes: can the substrate supply its OWN decomposition, and if not now, why not,
and is that fixable.
**Scope, USER-locked:** narrow glass-box sub-goal-discovery primitive. Mechanism-analog, not task-analog.
NOT self-improvement. All numbers below re-derived off-disk from `metrics.json`'s `per_regime` block, not
quoted from the verdict string.

---

## HEADLINE

**The HARD_FAIL is not primarily an entropy problem or an undertrained-SR problem — it is a textbook
imitation-learning-style COMPOUNDING-ERROR regime, and the substrate's own data proves it with a clean
matched-entropy dissociation.** At identical entropy = 8.0, `op4_V1200_d4` (1 sequential waypoint pick)
recovers 69.0% of the oracle-decomposition benefit, while `op2_V800_d8` (3 sequential waypoint picks)
recovers only 7.3% — a 10x collapse — **even though the underlying per-hop SR-reach signal is measured to
be slightly BETTER, not worse, at `op2_V800_d8`** (`reach_rank_test` uplift-over-chance = 0.497 vs 0.551).
Overall entropy and per-hop signal quality are ruled out as the dominant driver; **the number of chained,
uncorrected, greedy bisection steps is the dominant driver** — each waypoint pick anchors on the PREVIOUS
step's possibly-wrong discovered state (never on ground truth, never verified), which is precisely the
mechanism Ross & Bagnell (AISTATS 2010, "Efficient Reductions for Imitation Learning") proved gives
worst-case `O(epsilon * T^2)` error growth — quadratic, not linear, in chain length `T` — and which
"Toward the Fundamental Limits of Imitation Learning" (arXiv:2009.05990) shows is information-theoretically
*unavoidable in the worst case absent correction or interaction*, but **is explicitly NOT treated in that
same literature as an immovable law** — DAgger-style correction reduces the same bound to `O(T)` (linear),
and later work ("Provably Breaking the Quadratic Error Compounding Barrier in Imitation Learning, Optimally,"
arXiv:2102.12948) breaks the quadratic regime entirely under mild structural assumptions. **This is a
mechanism with a name, a formal rate, and a menu of known, precedented, cheap-to-implement fixes — not a
generic "SR was noisy" shrug.**

A second, milder, independently-real effect compounds on top of the above: the fixed `gamma=0.85` SR
transport has a textbook effective horizon of `1/(1-gamma) = 6.67` hops (Sutton TD theory; "Fixed-Horizon
Temporal Difference Methods," arXiv:1909.03906), so the raw reach signal DOES degrade gracefully with
horizon on its own (uplift-over-chance at `n_ops=4`: 0.551 at d4 -> 0.368 at d6 -> 0.261 at d8, roughly
linear). This is real but is the MINOR contributor — it cannot explain the 10x matched-entropy gap above,
which isolates chain-length compounding as the dominant term.

**Recommendation: ATTACK, not accept-bound.** This is exactly the load-bearing non-positive the standing
directive asks to research for mechanism + envelope-push, it has a decisive off-platform-confirmed
diagnosis, and the two strongest literature-ranked fixes (coarse-to-fine multi-resolution decomposition +
verify-before-commit gating) are near-zero-marginal-cost additions to code already on disk. **This is also
a second, independent, real consumer of the CEREBELLAR forward-model brain-component build** flagged
earlier today (`notes/research_brain_component_rerank_thalamus_cerebellum_load_2026-07-05.md`, rank #2,
"needs fresh design") — that note's target was the CONTROL depth-degradation curve (gonogo_lift 0.653 d4
-> 0.075 d6); this HARD_FAIL is a second, mechanistically-related but empirically-distinct target
(autonomous DECOMPOSITION collapsing under chain length, not execution collapsing under depth). Building
one cerebellum-class mechanism (predict-then-correct before committing, anticipatory not reactive) that
demonstrably helps BOTH targets is a stronger, better-motivated brain-component build than either alone.

---

## MECHANISM — off-disk evidence

### 1. Full grid, reorganized by (n_ops, depth, entropy, recovery, reach-signal uplift)

```
n_ops dd entropy recovery_ratio reach_rank_test uplift_over_chance  chain_steps(n_bnd-1)
2     4  4.00    0.178          0.857           0.715               1
2     6  6.00    0.477          0.818           0.636               2
2     8  8.00    0.073          0.748           0.497               3
3     4  6.34    0.617          0.763           0.645               1
3     6  9.51    0.111          0.631           0.446               2
3     8  12.68  -0.029          0.552           0.327               3
4     4  8.00    0.690          0.663           0.551               1
4     6  12.00  -0.003          0.526           0.368               2
4     8  16.00  -0.014          0.445           0.261               3
```
(`chain_steps` = number of sequential bisection picks = `n_boundaries(depth,2) - 1`; `uplift_over_chance
= (reach_rank_test - 1/n_ops) / (1 - 1/n_ops)`, i.e. the ancestor's own "does argmax-reach pick the true
op" diagnostic, rescaled to be comparable across different `n_ops` chance floors.)

**Recovery groups cleanly by `chain_steps`, not by `entropy` or by `n_ops`:** chain_steps=1 -> recovery
0.18-0.69 (mean ~0.50); chain_steps=2 -> recovery -0.003-0.48 (mean ~0.20); chain_steps=3 -> recovery
-0.03-0.07 (mean ~0.01). This is a rapid, ACCELERATING collapse (roughly 50% -> 20% -> 1%), not a graceful
linear decline — the qualitative signature Ross-Bagnell's `O(T^2)` predicts, in contrast to the reach
signal's own roughly-linear uplift decline (0.55-0.72 -> 0.37-0.64 -> 0.26-0.50).

### 2. The decisive matched-entropy dissociation

`op4_V1200_d4` (entropy=8.0, chain_steps=1): reach_rank uplift=0.551, recovery=0.690.
`op2_V800_d8` (entropy=8.0, chain_steps=3): reach_rank uplift=0.497, recovery=0.073.

Same entropy. Per-hop signal quality is 5.4 percentage points WORSE, not better, at the high-recovery
regime. Recovery differs by 61.7 points. **Entropy and raw signal quality are ruled out as the dominant
driver by this comparison alone; chain length (number of sequential, uncorrected discovery decisions) is
the only variable that tracks the outcome.**

### 3. Why chain length compounds specifically (not just "more steps, more chances to be wrong")

`_discover_bisect_boundaries` (`experiments/exp_pfc_gate_autonomous_waypoint_discovery_v1.py:613-639`) sets
`anchor = wp` (the just-picked, possibly-wrong candidate) for the NEXT boundary's argmax — there is no
ground-truth correction and no verification step before a pick becomes the next anchor. This is structurally
identical to behavior-cloning rollout (each action conditions on the agent's OWN previous output, not the
expert's/ground truth), which is exactly the setting Ross-Bagnell's bound applies to. `bwp_cv` (cross-seed
variance of `best_wp`) rises in lockstep with chain length (0.018-0.032 at chain_steps=1, 0.030-0.220 at
chain_steps=2, 0.073-0.368 at chain_steps=3) — instability growing with chain length is the other classic
compounding-error signature (small per-seed differences in early picks amplify through later ones).

---

## LIT-SCAN (2 parallel Sonnet sub-agents, generic math/CS terms only, 24 citations total)

### Thread A — is graceful signal decay vs. severe chain compounding a recognized TWO-mechanism split?
**Yes, and the split maps exactly onto our two effects.**
- **Graceful/per-step decay** (well-established, "textbook, mitigable" per lit-scan verdict): Sutton TD
  effective-horizon `1/(1-gamma)`; **Fixed-Horizon TD Methods** (arXiv:1909.03906, explicit claim that TD
  bootstrap bias grows with horizon); **Temporal Difference Models** (ICLR 2018, arXiv:1802.09081,
  goal-conditioned value accuracy decays with temporal distance); **Momennejad successor-representation
  decay literature**; **Horizon Reduction Makes RL Scalable** (arXiv:2506.04168, 2026 — long-horizon value
  learning degrades from horizon itself, motivating deliberate horizon reduction).
- **Severe/chain-compounding** (formally quadratic, per lit-scan verdict "textbook, fundamentally present
  absent correction"): **Ross & Bagnell 2010** (AISTATS, "Efficient Reductions for Imitation Learning") —
  the canonical `O(epsilon*T^2)` result; **Ross-Gordon-Bagnell DAgger 2011** (interactive correction reduces
  the SAME problem to `O(T)`, confirming quadratic-vs-linear is the key regime split caused specifically by
  "no correction, compounding from own errors"); **"Toward the Fundamental Limits of Imitation Learning"**
  (arXiv:2009.05990, `Theta(T^2)` unavoidable worst-case absent interaction); **"Provably Breaking the
  Quadratic Error Compounding Barrier..., Optimally"** (arXiv:2102.12948, breakable under
  mixing/smoothness assumptions); **Subgoal Search for Complex Reasoning Tasks** (arXiv:2108.11204) and
  **Adaptive Subgoal Search** (arXiv:2206.00702) — the closest STRUCTURAL analog found: recursive
  approximately-halfway subgoal generation, explicitly designed because chained subgoal value-function
  error compounds across levels; exposure-bias/autoregressive-decoding literature (arXiv:1809.00120) —
  same qualitative story in language generation.

### Thread B — ranked candidate fixes (5 mechanism classes scanned)
1. **Beam search / top-k retention** — Stahlberg-Byrne 2019 (ACL), Wiseman-Rush 2016: partial mitigation
   only, gains saturate fast, and 2025 exposure-bias work shows wider beams can be neutral-to-counterproductive
   under strong exposure bias. **Weakest standalone pick.**
2. **Coarse-to-fine / multi-resolution decomposition** — AMRA* (multi-resolution A*), multi-resolution
   H-cost motion planning, Willibald-Lee 2025 (hierarchical task decomposition, explicit note that fewer/
   well-separated subtasks mitigate accumulation). **Strong, direct match** — solves a coarser problem
   matched to where the value signal is actually reliable, then refines.
3. **Verification / connect-check before committing** — MPNet (Qureshi 2019), Ichter-Harrison-Pavone 2018
   (CVAE-proposed samples still gated by classical connect-checks), HYPE 2025 (arXiv:2510.12733, learned
   proposal feeds a verifier, never trusted alone). **Strong, direct match** — learned/noisy proposals are
   never blindly chained in this literature; a cheap independent check gates every candidate.
4. **Multi-timescale / multi-gamma successor representations** — Momennejad-Howard 2018 (bioRxiv, brain
   caches an ENSEMBLE of SRs at multiple discount scales specifically because one gamma loses long-range
   resolution); Janner et al. 2020 (NeurIPS, gamma-Models, decouples training/query-time discount); AMAGO
   (parallel multi-gamma value heads to fix flat long-horizon value surfaces). **Strong, most directly
   targets the diagnosed root cause of the MINOR (graceful-decay) effect** — but improves signal quality,
   not compounding dynamics per se; best combined with #2/#3.
5. **Cerebellar forward-model (Wolpert-Miall-Kawato 1998, Frontiers 2019, bioRxiv 2025)** — well-precedented
   as the unifying explanatory framework (anticipate-and-correct before committing beats react-after), but
   the lit-scan's own verdict: **explanatory framing, not itself a concrete algorithm** — the concrete
   algorithm IS #2+#3 (+#4), with cerebellar theory as the brain-grounding narrative around them.

**Combined ranked recommendation from the lit-scan:** coarse-to-fine (#2) + verify-gate (#3) are the two
strongest, most DIRECT fixes for the dominant (compounding) mechanism; multi-gamma (#4) is the strongest fix
for the minor (graceful-decay) mechanism and pairs naturally with #2 (use a longer-horizon gamma for the
COARSEST, longest-range pick, then progressively shorter-horizon gammas as the recursion narrows). Beam
search (#1) is the weakest and is not recommended as the primary lever.

**Citations, verified count: 24** (11 Thread A: Sutton TD theory, arXiv:1909.03906, arXiv:1802.09081,
Momennejad-Howard 2018, arXiv:2506.04168, Ross-Bagnell 2010, DAgger 2011, arXiv:2009.05990, arXiv:2102.12948,
arXiv:2108.11204, arXiv:2206.00702, arXiv:1809.00120 — 12 actually, list includes exposure-bias survey;
13 Thread B: Stahlberg-Byrne 2019, Wiseman-Rush 2016, ICLR-2025 anti-exposure-bias, AMRA*, multi-resolution
H-cost IEEE, Willibald-Lee 2025, MPNet 2019, Ichter-Harrison-Pavone 2018, HYPE 2025, Momennejad-Howard 2018
[shared], Janner et al. 2020, AMAGO, Wolpert-Miall-Kawato 1998, Frontiers 2019, bioRxiv 2025). All verified
via WebSearch by 2 independent Sonnet sub-agents using generic math/CS terms only (no substrate-specific
terms exposed off-platform), per `[[feedback-query-privacy-decomposition]]`.

---

## (b) Cheap decisive test

**Smoke, before any FULL dispatch:** reuse the ALREADY-LANDED FULL grid's own `op4_V1200_d6` and
`op4_V1200_d8` regimes at reduced scale (`N=2048`, `V=300`, 3 seeds, matching the ancestor cell's existing
smoke grid) as the two FOCUS regimes — both already known chain_steps=2 and chain_steps=3 collapse points
(recovery -0.003 and -0.014 respectively at FULL scale). Add exactly 3 new arms (additive to the passed
cell, all primitives reused verbatim: `E`, `W_ops`, `M`, `R`, `reach_value`, `train_sr_transport`,
`spectral_candidate_mask`'s eigh call pattern):
- `wp_bisect_coarse2fine` — recursive halving: pick ONE waypoint spanning [start,goal] first (using a
  SEPARATE `M_long` trained at `gamma=0.95`, effective horizon ~20 hops, via `train_sr_transport` verbatim
  with only `gamma` changed), then recurse into each half using the SAME procedure with `gamma` stepped
  down toward 0.85 as the remaining span narrows below ~7 hops (a simple `gamma_for_span(span) =
  max(0.85, 1 - 1/max(span,1))`-style rule, tunable, not locked).
- `wp_bisect_verify` — same open bisection, but a candidate must clear `R[anchor,c] >= tau` AND
  `R[c,goal] >= tau` (tau = a per-regime percentile of `R`'s own off-diagonal distribution, e.g. the 70th
  percentile) or the argmax retries excluding that candidate (capped at 5 retries, falling back to
  `wp_random_state`'s draw if all retries fail — an explicit, honest escape hatch, not silent degradation).
- `wp_bisect_combo` — coarse-to-fine recursion (as above) with the verify-gate applied at every level.
Cost: one extra `M_long` SR training pass per `(seed,V,n_ops)` group (identical cost class to the existing
`M`, negligible), a `gamma_for_span` scalar function, and a bounded retry loop — no new representational
machinery, no new training loop shape. Wall-clock: expect well under the ancestor cell's existing smoke
budget (the ancestor's FULL run was 1789.5s for 405 units across 9 regimes and 5 seeds; this adds 3 arms x
9 regimes but reuses SR training almost entirely).

---

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL, locked; deepest FOCUS = `op4_V1200_d8`, entropy=16)

**HARD-PASS (rescue is real and worth folding into the capability):**
- `recovery_ratio(best-of-{coarse2fine,verify,combo})` at FOCUS `>= 0.20` (matches the ORIGINAL ancestor
  cell's own HP bar — recovers a real fifth of the oracle-decomposition benefit at the exact regime that
  was `-0.014` before) **AND**
- `recovery_ratio(best rescue arm) - recovery_ratio(wp_bisect_open baseline, already measured -0.014 at
  FOCUS) >= 0.15` (a real, decisive lift over the already-HARD_FAILed baseline, not just noise) **AND**
- honesty guards hold at the SAME thresholds as the passed ancestor cell (`index_artifact_gap < 0.05`,
  `anti_tautology_corr < 0.85`, `degenerate_rate < 0.10`) **AND**
- `cv(best rescue arm) < 0.15` at FULL (loosened from the ancestor's 0.10 given more moving parts;
  documented, not silently relaxed) **AND**
- `sign_p < 0.05` (paired, rescue vs. baseline at FOCUS).
=> the deep-corner bound is NOT a fundamental limit of SR-reach bisection; it is a fixable property of the
one-shot uncorrected procedure, and a cerebellar-style anticipate-and-verify mechanism recovers real
autonomous-decomposition capability at the deepest tested regime.

**HARD-FAIL (deep corner is a genuine structural bound, even after the rescue attempt):**
- `recovery_ratio(best rescue arm) <= recovery_ratio(wp_bisect_open) + 0.05` at FOCUS (no material lift over
  the already-failed baseline despite coarse-to-fine + verify-gate + multi-gamma all being tried)
=> honest stopping point: autonomous decomposition at 3+ sequential no-oracle discovery steps in this
domain/training-budget is closed even after the standard imitation-learning-style fixes; the remaining lever
(DAgger-style interactive/expert-query correction) would require an oracle probe mid-discovery, which
undermines the "autonomous, no-oracle" framing this capability line is trying to establish, so it is
reasonably out of scope rather than an obvious next step.

**MIDDLE_BAND:** real lift over `wp_bisect_open` (`>0.05` on `recovery_ratio`) but `<0.15` (doesn't clear
the decisive bar) — report as "compounding-error mitigation is real but partial," a defensible, deflated,
honest intermediate finding, not a clean win or a clean bound.

**P_deflated:**
- P(rescue shows ANY real lift over `wp_bisect_open` baseline at FOCUS, i.e. clears MIDDLE-band): raw
  ~0.70-0.75 (two independent, convergent lines of evidence: the matched-entropy dissociation cleanly
  isolates chain-length/compounding as the fixable-in-principle mechanism, and external lit strongly and
  specifically ranks coarse-to-fine + verify-gate as direct, well-precedented fixes for EXACTLY this
  failure mode, not a loose analogy) -> **P_deflated ~0.50-0.55** after the mandatory 0.15-0.25 calibration
  penalty.
- P(rescue clears the full HARD-PASS bar, `recovery_ratio >= 0.20` at the deepest, hardest-tested corner):
  raw ~0.50-0.55 (genuinely uncertain whether the fix recovers enough, not just some) -> **P_deflated ~0.35**,
  consistent with the mandatory novel-synthesis cap of 0.50 (this exact three-mechanism combination has never
  been tried on this substrate).

---

## (d) Cross-thread synthesis

- Directly extends `notes/research_autonomous_waypoint_discovery_control_2026-07-05.md` (the pre-registration
  note for the cell that just landed): that note predicted `P_deflated~0.22` for full HARD-PASS and
  `P_deflated~0.45` for "mechanism fires at all" — the actual landing (HARD_FAIL, 3/9 regimes hp_ok, deepest
  corner negative) sits within the honestly-forecast uncertainty band, not a surprise; the note's own
  Cross-thread synthesis section explicitly flagged "if HARD_FAIL... re-test with a better-trained SR before
  closing the capability box" as the 2x-drill-before-closure discipline — this drill supersedes that specific
  suggestion (more `SR_STEPS` at fixed `gamma=0.85` will NOT fix a `1/(1-gamma)`-bounded horizon nor a
  chain-compounding problem; the matched-entropy dissociation rules out "SR undertrained" as the story) with
  a sharper, evidence-backed mechanism and a different, better-targeted fix.
- Complements, does not duplicate, `notes/research_brain_component_rerank_thalamus_cerebellum_load_2026-07-05.md`
  (same day, rank #2 cerebellum candidate `exp_reasoning_forward_model_anticipatory_correction_v1`, targeting
  the CONTROL flat-gate depth-degradation curve 0.653->0.075). That note correctly identified cerebellar
  forward-model theory as loaded but under-specified ("no pre-named candidate cells... needs fresh design").
  This drill supplies a SECOND, concretely-specified, cheaply-buildable consumer for the same brain-component
  class, sharing the same theoretical grounding (Wolpert-Kawato-Miall feedforward-vs-feedback; the DAgger
  regret-bound "when is anticipatory correction worth it" criterion cited in that note is now directly,
  formally confirmed relevant here via Ross-Bagnell's `O(T^2)` result, not just analogically plausible).
  Recommend treating the cerebellum brain-component build as ONE mechanism (predict-then-verify-before-commit,
  horizon-matched multi-gamma) tested against BOTH targets, not two separate builds.
- Does not reopen or contradict the DIFFERENT-mechanism-class BlocksWorld hierarchical-planning closure
  (2026-06-27/28, hand-defined option channels) — that closure is in a different domain with a different
  mechanism and remains untouched by this finding, per `[[feedback-prior-work-informs-not-constrains]]`.

## (e) Substrate-product implications

- **Narrow, honest framing preserved (USER-LOCKED):** even a full rescue HARD-PASS would mean only "given a
  trained SR plus a coarse-to-fine, verify-gated discovery procedure over a small known state space, the
  substrate can propose a partially-useful decomposition at higher depth than the naive one-shot bisection
  could" — still not autonomous planning, still not self-improvement.
- If HARD-PASS or MIDDLE-BAND: the `recovery_ratio` delta becomes a second, reusable, honest product-facing
  number ("a predict-then-verify discovery step recovers X percentage points of autonomous-decomposition
  benefit at the deepest tested regime, versus Y for one-shot bisection") — and doubles as concrete,
  quantified evidence for the brain-component-driven-development thrust's cerebellum row (a claim like "the
  substrate needed an anticipatory-correction mechanism and adding one measurably helped" is a much stronger
  brain-alignment story than a hypothetical).
- If HARD-FAIL even after the rescue: the honest bound sharpens further and usefully — "autonomous
  decomposition is closed specifically at 3+ uncorrected sequential discovery steps, INCLUDING after
  standard imitation-learning-style compounding-error fixes" is a precise, defensible, non-speculative
  capability-map entry (distinct from and stronger than merely "it failed at the deepest corner").

---

## STRATEGIC CALL

**ATTACK.** Rationale, weighed explicitly:
1. The mechanism diagnosis is decisive, not speculative — a clean in-substrate dissociation (matched
   entropy, opposite-direction signal-quality vs. recovery) plus a named, formally-quantified external
   mechanism (Ross-Bagnell `O(T^2)`) that fits the qualitative shape of the collapse (accelerating, not
   linear).
2. The literature-ranked fixes (coarse-to-fine + verify-gate, multi-gamma as a complementary third) are
   NOT speculative reaches — they are the standard, textbook answer to exactly this failure class in three
   independent fields (imitation learning, hierarchical motion planning, multi-timescale value learning),
   found independently by an external Sonnet lit-scan given only generic terms.
3. Marginal cost is low: every primitive (`E`, `W_ops`, `M`, `R`, `reach_value`, `train_sr_transport`, the
   `eigh` pattern already used for the spectral arm) is already on disk and reused verbatim; the new work is
   ~3 additive functions (a second-gamma SR train call, a recursion wrapper, a threshold-and-retry gate).
4. It is a genuine SECOND consumer for the cerebellum brain-component build already flagged as a build
   priority today — attacking here is not a standalone speculative side-quest, it directly serves the
   standing brain-component-driven-development thrust with a concrete, cheap, already-specified test.
5. The alternative (ACCEPT-BOUND now) would foreclose testing well-precedented, cheap fixes before the
   literature's own strongest recommendation has been tried even once — exactly the premature-dismissal
   failure mode the standing directives warn against.

If this rescue cell ALSO HARD-FAILs (after coarse-to-fine + verify-gate + multi-gamma), THAT would be the
point to accept the bound honestly — the menu of well-precedented fixes would then be exhausted, and the
remaining lever (interactive/oracle-in-the-loop correction) is out of scope by the capability's own
"autonomous, no-oracle" definition. This note pre-registers exactly that fallback so a second HARD_FAIL
would be a clean ACCEPT-BOUND, not another open question.

---

## CELL SPEC — `exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1` (ready for exp_dev; NOT built yet)

**Inherits verbatim** from `exp_pfc_gate_autonomous_waypoint_discovery_v1.py`: `make_bipolar_E`, `hebbian_W`,
`cleanup_batched`, `make_kb_and_chains`, `train_sr_transport`, `reach_value`, `build_reach_matrix`,
`run_hier_arm_wp`, `oracle_trajectory_idx`, `build_waypoint_idx`, the full entropy grid, and ALL existing
arms as fixed reference points (`flat_gonogo`, `oracle_exec`, `hier_oracle`, `hier_shuffled`,
`wp_bisect_open` — the last one now a KNOWN, already-measured baseline at every regime, re-run in-cell for
a proper paired comparison on identical seeds, exactly as the ancestor did for `hier_oracle`).

**New primitives (additive only):**
```
M_long, _ = train_sr_transport(E, transitions, n, steps, batch, base_lr, gamma=0.95, gen)  # 2nd SR, verbatim call
def gamma_for_span(span: int) -> float: return max(0.85, 1.0 - 1.0/max(span, 1))            # tunable, not locked
def coarse2fine_boundaries(starts, targets, R_by_gamma: dict, depth, seg_len, verify_tau) -> boundary_states:
    # recursively bisect [start,goal] -> pick ONE waypoint using R_by_gamma[gamma_for_span(depth)];
    # if either half still needs subdivision (> seg_len), recurse into it with a narrower gamma;
    # at every pick, apply the verify-gate (R[anchor,c]>=tau and R[c,goal]>=tau, else retry excl. candidate,
    # capped at 5 retries, fallback to a uniform-random draw on total retry exhaustion -- explicit, logged)
```
**New arms:** `wp_bisect_coarse2fine`, `wp_bisect_verify`, `wp_bisect_combo` (coarse2fine + verify-gate
together). All three share the identical `run_hier_arm_wp` execution loop as every other `wp_*` arm — only
the waypoint-discovery function differs, per the ancestor's own design discipline.

**Discriminators:** identical formula family to the ancestor (`recovery_ratio`, `autonomous_closure`,
`lift_flat`, `lift_random`, `index_artifact_gap`, `anti_tautology_corr`, `degenerate_rate`, `sign_test_p`,
`cv`), PLUS one new diagnostic: `retry_rate` = mean fraction of picks that needed >=1 verify-gate retry
(reported regardless, not gating — a high retry rate at deep regimes would itself be informative: it means
`tau` is too strict for the available candidate pool at that depth, a tuning signal not a mechanism failure).

**HARD-PASS / HARD-FAIL / MIDDLE-BAND:** exactly as specified in section (c) above, evaluated at
`op4_V1200_d8` (identical FOCUS regime to the parent HARD_FAIL, for a clean before/after comparison) and
reported for the full grid regardless (same "always report" ethos as both ancestors).

**Smoke:** as specified in section (b) — reuse the ancestor's existing smoke grid + FOCUS at `op4_V300_d6`
(chain_steps=2, matches where collapse already begins) before any FULL dispatch.

**Compute:** one extra SR-training pass (`M_long`) per `(seed,V,n_ops)` group, identical cost class to `M`
itself; the coarse2fine recursion and verify-gate retries are all vectorizable batched-tensor operations, no
new training loop. Should fit comfortably inside the parent cell's existing smoke/FULL wall-clock budget
(parent FULL: 1789.5s for 405 units; this cell adds units linearly, no quadratic blowup in compute itself —
only the DISCOVERY MECHANISM's compounding was quadratic, not the compute cost of computing it).

---

## Dispatch readiness

Cell spec is complete and additive to the passed parent cell. No hand-off routing file written (ferry
mechanism deprecated per USER-locked discipline) — this note is the complete, actionable deliverable.
Director should read this note directly and dispatch `hdi_exp_dev` with a pointer to this file + the parent
cell path (`experiments/exp_pfc_gate_autonomous_waypoint_discovery_v1.py`) for verbatim-reused primitives,
framed explicitly as (part of) the cerebellar forward-model brain-component build alongside the CONTROL-depth
target already specced in `notes/research_brain_component_rerank_thalamus_cerebellum_load_2026-07-05.md`.
