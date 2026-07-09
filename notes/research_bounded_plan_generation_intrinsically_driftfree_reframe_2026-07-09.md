# Reframe drill: is bounded-plan generation intrinsically drift-free, and is the "3x INCONCLUSIVE" actually a metric-wiring bug hiding a positive?

**Date:** 2026-07-09. **Type:** brain-first + cross-domain reframe drill, USER-directed, self-authored, no
sub-agents. Trigger: v9/v10/v11 of `exp_substrate_gen_lm_replay_propose_score_commit_*` all returned
`INCONCLUSIVE_NO_COMPOUNDING`-class verdicts on the must-fail ACCUMULATE baseline, while the separable positive
(replay-propose-score-commit wins `goal_reach` at all depths, beats random-restart and propose-only, scoring
earns its keep) was already banked. Task: is "no compounding" itself the real positive result (bounded-plan
readout is drift-free BY CONSTRUCTION), and if so what is the correct certification test.

**What was verified off-disk before writing anything** (per Fix#28 — do not re-derive what's already landed,
and do not trust a verdict string without recomputing from the underlying arrays):
- `data/exp_substrate_gen_lm_replay_propose_score_commit_v9_n8192_gpu_smoke/metrics.json`,
  `..._v10_unforgiving_..._smoke/metrics.json`, `..._v11_unique_path_..._smoke/metrics.json` — all three
  `per_seed[0].per_unit[*]` rows read directly (not just `verdict_msg`).
- `experiments/exp_substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu.py` (869 lines) read
  in full, including `_acc_curve` (line 467), `_selftest` (line 565), and `compute_verdict` (line 688).
- `notes/research_native_glassbox_generation_brain_first_2026-07-08.md` and
  `notes/research_deep_chain_reasoning_bounded_compounding_error_brain_first_2026-07-08.md` (the two same-day
  sibling drills this note extends — one derived the brain mechanism for generation, the other independently
  derived the "informational independence, not self-reference" governing law for a different compounding-error
  target).
- `notes/research_bundling_capacity_beyond_fixed_N_theta_gamma_chunking_sparse_2026-07-08.md` (Lisman-Idiart
  theta-gamma clock-division capacity account + Tsodyks-Feigelman sparse-Hopfield capacity — the closed-form
  "capacity is a known, flat function of load" literature this note leans on for the mechanistic argument).

---

## HEADLINE

**Yes — and the "3x INCONCLUSIVE" is not primarily a mechanism failure, it is a metric-wiring bug that is
already fixable from data already on disk.** `_acc_curve` (v11, line 467) computes and returns `intra_decline`
— the artifact-free within-sequence witness (first-half-body-accuracy minus second-half-body-accuracy at a
SINGLE depth) — with its own docstring correctly explaining why the OLD discriminator (`body_token_acc` MEAN
drift between the shallowest and deepest tested depth) is diluted and can even invert sign: the accumulator's
crosstalk-driven degradation is POSITION-anchored (onset around position 8 regardless of total sequence
length), so a longer sequence has proportionally MORE early-perfect positions and its body MEAN can rise even
while its TAIL is compounding worse. `DECLINE_MIN=0.12` and `REPLAY_DECLINE_MAX=0.05` were defined at the top
of the file specifically to gate on `intra_decline` (comments: "D1: within-sequence compounding fires" / "the
bounded arm stays flat at the ceiling"). **But `compute_verdict()` (the function that actually decides
HARD_PASS/INCONCLUSIVE/HARD_FAIL) and the `--self-test --strict` gate never reference `intra_decline`,
`DECLINE_MIN`, or `REPLAY_DECLINE_MAX` anywhere.** Both still compute D1/D1b/D1c from `body_drift = acc_b_lo -
acc_b`, the mean-based metric the file's own docstring says is diluted. This is a dead-code / incomplete-refactor:
someone (a prior cycle) correctly diagnosed the metric flaw, added the fix (`intra_decline` + its thresholds)
to the metrics computation, but never wired it into the actual gate. The three `INCONCLUSIVE_NO_COMPOUNDING`-
class verdicts are measuring the WRONG artifact-suppressed quantity, not reporting a genuine absence of
compounding.

**Hand-recomputed directly from `per_position_acc` arrays already in `..._v11_..._smoke/metrics.json`** (seed=7,
N=4096, no code execution needed — this is arithmetic on numbers already on disk):
- ACCUMULATE `intra_decline` = **0.1667 @ L4**, **0.2166 @ L14** — both clear `DECLINE_MIN=0.12`, and GROWING
  with depth (the qualitative signature of genuine recursive/self-referential compounding, stronger evidence
  than a single-point threshold crossing).
- REPLAY `intra_decline` = **0.0 @ L4**, **0.0 @ L14** (every per-position accuracy in the unique-path regime
  is exactly 1.0 at both depths) — flat at the ceiling, `REPLAY_DECLINE_MAX=0.05` cleared with large margin.
- Under the CORRECT metric, D1 (accumulator compounds), D1b (accumulator-specific), and D1c (REPLAY stays at
  ceiling) all fire cleanly on data that is ALREADY SITTING ON DISK. The `INCONCLUSIVE_NO_COMPOUNDING` verdict
  string was computed from `body_drift = 0.800 - 0.900 = -0.100` (the accumulator's MEAN got BETTER, not worse,
  with depth) — which is real and correctly reported, but is the diluted metric, not the artifact-free one the
  file itself already built and then failed to use.

**The mechanistic answer to the user's question (a):** bounded-plan / competitive-queuing readout is drift-free
by construction for a precise, falsifiable reason — not vaguely "it's brain-like" but because it structurally
LACKS the recursive data-dependency that DEFINES compounding error. ACCUMULATE's update `c_{l+1} = LAMBDA_ACC *
c_l + cb[emitted_l]` is a Markov recursion: the input to step `l+1` is step `l`'s own (possibly already-wrong)
state — this is the exact mathematical shape of Ross-Bagnell `O(T^2)` compounding and of grid-cell path
integration between boundary resets. REPLAY's plan vector, by contrast, is composed ONCE (offline, from an
already-decided, already-scored whole candidate route) and then read out via `peel_sic_readout` — the
ALREADY-BUILT competitive-queuing decoder — which performs winner-take-all-and-subtract against that SAME
FIXED vector L+1 times. There is no data-dependency where extraction at position `p`'s error feeds into the
COMPUTATION of extraction at position `p+1`; each extraction is a fresh argmax against a static bundle with
the already-extracted items subtracted off. This is structurally the "read a fixed external reference
repeatedly" class (regenerative repeater / grid-cell boundary-reset), not the "recursively update a running
state" class — and it is exactly why REPLAY's per-position accuracy in v11 is 1.0 at every position, at every
tested depth, with zero exceptions in the recorded data.

**The falsifiable, sharper form of the claim (what "capacity is the only limit" actually predicts):** whatever
residual degradation CAN occur in a bounded-plan readout must trace to the STATIC crosstalk load of the
bundle — how many items are superposed together (`L+1`) relative to the dimensionality (`N`) — which is a
known, closed-form CAPACITY quantity (Tsodyks-Feigelman sparse-Hopfield-style `P ~ N/(a|ln a|)`, Lisman-Idiart
theta-gamma clock-division capacity, this substrate's own Plate-bound literature), NOT a quantity that grows
with sequence POSITION or ORDER. This makes a specific, testable prediction: two regimes with the SAME
`(L+1)/N` ratio at DIFFERENT absolute scales should show the SAME degradation curve (a "collapse" test,
below). If they don't collapse, there is a genuine position/order-dependent effect beyond pure capacity, and
the strong "provably drift-free by construction" claim is falsified (the mechanism could still be bounded and
useful — just not for the reason claimed).

---

## Cheap decisive test

**TEST 0 — fix the wiring bug and re-run on the EXISTING harness (near-zero cost, do FIRST, before anything
else).** In `experiments/exp_substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu.py`:
1. In `compute_verdict()` (line 688), replace the `body_drift`-based D1/D1b/D1c comparisons (lines 704-705,
   734-749) with `intra_decline`-based ones: pull `acc_id = _val(all_results, "ACCUMULATE", L, "intra_decline")`
   and `rep_id = _val(all_results, "REPLAY", L, "intra_decline")` (the field already exists in every per_unit
   dict returned by `_acc_curve` for `L>=2`), and gate D1 on `acc_id >= DECLINE_MIN`, D1b on
   `acc_id - rep_id >= DECLINE_MIN`, D1c on `rep_id <= REPLAY_DECLINE_MAX` (in addition to the existing
   `rep_b >= REPLAY_BODY_MIN` ceiling check, which stays).
2. Apply the identical swap to the `--self-test --strict` block (lines 622-641).
3. Re-run `python experiments/..._v11_...py --self-test --strict` (CPU, seconds) then `--smoke`. Per the
   hand-recomputation above, this is PREDICTED to print `DISCRIMINATOR-FIRES PASS` and land a `HARD_PASS` or
   `MIDDLE_BAND` (not `INCONCLUSIVE`) verdict on the SAME synthetic corpus/codebook already in use — no new
   experiment design, no new corpus, purely a metric-selection correction with a fully worked-out, disk-derived
   prediction of the outcome.
4. **Honest caveat:** this is a hand-recomputation from the RAW JSON, not a code-execution confirmation — the
   actual patched `compute_verdict()` could behave differently if `aggregate_partials`/`_val` handle rounding,
   NaN, or multi-seed averaging in a way this arithmetic didn't capture (only seed=7, smoke-scale, 2 L-points
   were checked by hand). Test 0's own re-run is the confirmation step, not a foregone conclusion.

**TEST 1 — the RIGHT positive cert (depth-invariance framing), to run AFTER Test 0 confirms the mechanism is
sound.** Reframe the claim from "REPLAY beats a compounding ACCUMULATE" (there may be nothing to beat once
ACCUMULATE's true compounding is correctly measured and margins are set, but the INTERESTING claim was never
really a horse race) to two independently falsifiable properties:
- **(i) Flatness across a WIDE depth grid, not a 2-point secant.** Extend `L_GRID` to `[4, 8, 14, 24, 40]` (or
  further, budget permitting) and require REPLAY's `body_token_acc >= REPLAY_BODY_MIN` AND
  `intra_decline <= REPLAY_DECLINE_MAX` at EVERY point in the grid — a genuinely flat curve, not an endpoint
  comparison. Simultaneously require ACCUMULATE's `intra_decline` to be MONOTONICALLY INCREASING across the
  same grid (the true signature of recursive compounding — stronger than "above threshold at the deepest
  point").
- **(ii) The capacity-collapse kill-test (new, sharper than anything in v9-v11).** Run matched `(L, N)` pairs
  at the SAME `(L+1)/N` ratio but different absolute scales — e.g. `rho ~ 0.005` via `(L=40, N=8192)` vs
  `(L=10, N=2048)`. **HARD-PASS requires REPLAY's `body_token_acc` and `intra_decline` at matched `rho` to
  agree within the noise band (`CV_MAX`)** — direct evidence that bundle-load-relative-to-N is the ONLY
  variable governing REPLAY's fidelity, not depth or read-out position per se. This is the test that actually
  certifies "the plan capacity bound is the only limit," as distinct from merely "REPLAY looks flat on the two
  depths we happened to try."
- Reuses every existing primitive verbatim (`build_graph`, `build_stores`, `propose_walks`,
  `accumulate_path`, `build_plan_vectors`, `readout_paths`, `peel_sic_readout`) — the only additions are a
  wider `L_GRID`, a second `N` value for the collapse pairs, and the collapse-comparison discriminator itself.

---

## Falsifiable predictions

**HARD-PASS (Test 0, cheapest, already arithmetic-verified on seed=7 smoke data):**
- Patched `intra_decline`-based D1 fires: `acc_id(L=14) = 0.2166 >= DECLINE_MIN = 0.12`. **Already true in the
  existing JSON.**
- D1b fires: `acc_id - rep_id = 0.2166 - 0.0 = 0.2166 >= DECLINE_MIN = 0.12`. **Already true.**
- D1c fires: `rep_id(L=4)=0.0, rep_id(L=14)=0.0 <= REPLAY_DECLINE_MAX = 0.05` AND `rep_b >= REPLAY_BODY_MIN=0.80`
  (already true: REPLAY body = 1.0 at both L). **Already true.**
- => predicted outcome of re-running the patched self-test: `DISCRIMINATOR-FIRES PASS`, not `INCONCLUSIVE`.

**HARD-FAIL (Test 0):** re-running the ACTUAL patched code (not the hand arithmetic) produces a DIFFERENT
`intra_decline` value than hand-computed here (e.g. due to seed/aggregation/rounding subtleties this
recomputation missed) such that D1/D1b/D1c do not fire even under the corrected metric. This would mean the
diagnosis (wiring bug) is wrong or incomplete, and the genuine absence of compounding stands as reported.

**HARD-PASS (Test 1, the positive depth-invariance cert):**
- REPLAY `body_token_acc >= 0.80` AND `intra_decline <= 0.05` at EVERY `L` in `[4,8,14,24,40]` (flat curve, not
  a secant) AND
- ACCUMULATE `intra_decline` strictly increasing across the same grid AND
- capacity-collapse: matched-`rho` `(L,N)` pairs agree on REPLAY `body_token_acc`/`intra_decline` within
  `CV_MAX=0.15` AND
- `cv <= 0.15` across `>=3` seeds at FULL `N=8192`.
=> the strong claim holds: bounded-plan competitive-queuing generation is depth-invariant, and the ONLY
variable that can degrade it is bundle load relative to dimensionality — a known, predictable, non-mysterious
capacity law, not a recursive compounding process.

**HARD-FAIL (Test 1):** REPLAY `body_token_acc`/`intra_decline` degrades with `L` in a way that does NOT
collapse cleanly onto a single `(L+1)/N`-indexed curve (matched-`rho` pairs disagree beyond `CV_MAX`) — proves
a genuine position/order-dependent effect exists beyond pure capacity. This is the honest negative the v11
docstring already anticipated at D1c ("the bounded-plan readout also drifts off the unique path — a real
finding about the readout"), now sharpened into a specific, falsifiable claim about WHERE the residual drift
comes from (capacity vs. position) rather than a bare pass/fail on one depth pair.

**MIDDLE_BAND:** flattens/improves relative to ACCUMULATE but the capacity-collapse test shows partial, not
clean, agreement — informative partial: "bounded, better than a recursive accumulator, but not PURELY
capacity-limited; some residual position-dependence remains."

---

## Connection to tonight's converged independent-correction principle

**Same governing law, applied at a stronger/earlier pipeline stage.** `research_deep_chain_reasoning_bounded_
compounding_error_brain_first_2026-07-08.md`'s headline: chains compound when the correcting signal is drawn
from the SAME noisy estimator that produced the error (self-referential); they stay bounded when the
correcting signal is informationally INDEPENDENT (grid-cell boundary reset, bidirectional replay-then-select).
That principle, applied to generation's PROPOSAL/SCORING stage (mechanism 2, replay-propose-score-commit),
says: score candidates using a signal (the certified content-vs-recency `combinedgate`, or here the goal-reach
+ content-toward-goal `coherence` score) that is INDEPENDENT of any single partial commit — this is present in
REPLAY's design (`coherence = reach_goal*10 + w_score`, computed over WHOLE candidate routes before any commit).

This note's contribution is the READOUT stage specifically (mechanism 1, competitive-queuing peel/SIC), which
is a STRONGER, more literal instance of the SAME law: it does not merely use an independent signal to CORRECT
a running estimate — it removes the running estimate ENTIRELY once the plan is committed, so there is nothing
left TO correct. "Independent-correction" (chain-reasoning) and "no self-reference at all" (bounded-plan
readout) are the same principle at two different points on a spectrum: (1) you can correct a recursive process
with an independent signal (chain-reasoning's fix), or (2) you can eliminate the recursion altogether and read
a fixed object multiple times (generation's readout stage). Both are instances of "never correct a noisy
process using more of the same noisy process" — (2) is just the limiting case where there is no process left
to be noisy about, only a fixed target with a known, flat capacity ceiling. This is a genuine, not manufactured,
structural convergence: three independent same-week/same-day drills (chain-reasoning rescue, generation
mechanism inventory, this reframe) each separately arrived at recognizable instances of one law from three
different empirical starting points (a HARD_FAIL waypoint cell, a brain-mechanism lit-scan, and a hand-recompute
of existing generation-cell JSON).

---

## Cross-thread synthesis

- Directly resolves the open question left at the end of `research_native_glassbox_generation_brain_first_
  2026-07-08.md` (mechanism 2's cheap decisive test) and explains, retroactively, why v9/v10/v11 iterated
  through three INCONCLUSIVE verdicts without landing: v9/v10 had genuine confounds (goal-attractor rescue,
  multiple-valid-path ambiguity) that were correctly diagnosed and fixed by exp_dev across iterations; v11
  fixed the GRAPH confound (unique-path construction) correctly, but the METRIC WIRING was left one step
  behind its own docstring's diagnosis — this note closes that last gap.
- Extends `research_deep_chain_reasoning_bounded_compounding_error_brain_first_2026-07-08.md`'s governing
  principle (informational independence beats self-reference) from the DECISION/SCORING layer to the READOUT
  layer, and supplies a THIRD independent empirical regime (after the chain-reasoning HARD_FAIL and the v5-v8
  gate family) where the same law is directly, quantitatively visible in already-collected data.
- Directly reuses `research_bundling_capacity_beyond_fixed_N_theta_gamma_chunking_sparse_2026-07-08.md`'s
  capacity literature (Lisman-Idiart clock-division, Tsodyks-Feigelman sparse-Hopfield) as the closed-form
  account of what SHOULD limit a bounded-plan readout if the "capacity is the only limit" claim is correct —
  turning a qualitative brain-first intuition into a numerically falsifiable collapse test.
- Cross-domain grounding (generic terms, no substrate-specific framing exposed off-platform): ribosome
  translation processivity is the cleanest cross-domain analog — drop-off (processivity failure) is reported
  as largely SEQUENCE/POSITION-INDEPENDENT ("dependent on the inner machinery of the ribosome more than the
  specific sequence"), and per-codon miscoding error is commonly modeled as UNIFORM across position (~1e-4),
  i.e. a FIXED per-step rate against a fixed external template (charged-tRNA pool matched to the mRNA), not a
  quantity that grows with how many codons have already been read — structurally the same "fixed external
  reference, read repeatedly, no recursive carry" class as the peel/SIC readout. Successive-refinement
  source coding is a weaker but directionally consistent analog: optimal successive refinement requires a
  Markov/independent-target structure across stages rather than each stage correcting the residual of the
  PREVIOUS stage's own noisy reconstruction; this is suggestive, not decisive (no direct "error does not
  compound" result was found in this session's search). Systolic-array literature returned no directly
  on-point citation this session (searched, came back generic — flagged as a genuine gap, not asserted).

## Substrate-product implications

- **If Test 0 confirms:** the product-facing claim upgrades from "three inconclusive generation-mechanism
  probes" to "the substrate has a certified, brain-grounded, glass-box generative primitive (replay-propose-
  score-commit + competitive-queuing readout) that is measurably depth-invariant on a structural synthetic
  regime, and the earlier ambiguity was a metric-selection bug, not a mechanism failure" — a materially
  stronger and more honest position than either "it works" (overclaim) or "compounding is untestable here"
  (the prior framing).
- **If Test 1 (capacity-collapse) clears HARD-PASS:** the substrate gains something more valuable than "beats
  a baseline" — a PREDICTIVE, closed-form account of when bounded-plan generation will degrade (bundle
  load/N ratio) that composes directly with the existing capacity literature (sparse coding, DG pattern
  separation, theta-gamma clock-division) already banked for other capability lines — i.e. generation
  degradation would no longer need its OWN separate theory, it would be an INSTANCE of the substrate's general
  capacity law.
- **If Test 1's collapse test fails:** still valuable — it would isolate a genuine, previously-unknown
  position/order-dependent residual in the peel/SIC readout specifically (not in the propose/score/commit
  stage, which v9-v11 already independently certify via `goal_reach`), narrowing future readout-hardening work
  to a specific, falsifiable target rather than a vague "generation might drift" worry.
- No overclaim: this note does not promote any cap_map row. It identifies one small, disk-verifiable code fix
  (metric wiring) with a fully worked hand-computation predicting its outcome, plus one new, sharper positive-
  cert design (capacity-collapse) that goes beyond what v9-v11 attempted to test.

## Citations (verified count)

**Fresh external sources, verified via WebSearch this cycle (generic terms only, no substrate-specific framing
exposed off-platform per `[[feedback-query-privacy-decomposition]]`), 4 searches:**
1. Successive refinement of sources / rate-distortion region (Markov-chain necessary-and-sufficient condition
   for optimal successive refinement) — multiple arXiv/IEEE sources cross-checked; no direct "error does not
   compound" claim found, logged as a weak/suggestive analog only, not asserted as decisive.
2. Systolic array fixed-latency pipeline error propagation — searched, no directly on-point citation surfaced;
   logged as a genuine gap (do not cite a specific paper for this analogy).
3. Ribosome translation processivity / drop-off-rate literature (PMC11025885 / NAR Genomics and Bioinformatics
   2024; PMC5697424 translational fidelity review; bionumbers.org error-rate compilation) — processivity
   (drop-off) errors reported as machinery-dependent rather than sequence/position-dependent; per-codon
   miscoding error commonly modeled as uniform (~1e-4) across position.
4. Competitive queuing model (Bullock & Rhodes, "Competitive queuing for planning and serial performance";
   Kornysheva et al. 2019, *Neuron*/bioRxiv 383364, "Neural competitive queuing of ordinal structure underlies
   skilled sequential action") — re-confirms winner-take-all-and-delete dynamics over a static primacy-gradient
   plan, independently of the same-day sibling drill's citation of the same paper.

**Carried, re-verified against fresh on-disk reads this cycle (not re-fetched externally, per 2x-drill
discipline):** Grossberg 1978; Houghton 1990; Pfeiffer & Foster 2013; Mattar & Daw 2018; Foster & Wilson 2006;
Hardcastle, Chen & Giocomo 2015 (grid-cell boundary reset); Sreenivasan & Fiete 2011 (modular error-correcting
code); Duttweiler-Mazo-Messerschmitt 1974 (regenerative repeater / decision-feedback-equalizer error-
propagation law); Ross & Bagnell 2010/2011 (all from the two same-day sibling notes read in full this cycle);
Lisman & Idiart 1995, *Science* (theta-gamma clock-division capacity); Tsodyks & Feigel'man 1988 (sparse
Hopfield capacity) (from `research_bundling_capacity_beyond_fixed_N_theta_gamma_chunking_sparse_2026-07-08.md`).

**Internal artifacts freshly re-read/recomputed off-disk this cycle (load-bearing, not carried from memory):**
`data/exp_substrate_gen_lm_replay_propose_score_commit_v9_n8192_gpu_smoke/metrics.json`,
`..._v10_unforgiving_..._smoke/metrics.json`, `..._v11_unique_path_..._smoke/metrics.json` (all `per_seed[0].
per_unit[*]` rows, including `per_position_acc` arrays used for the by-hand `intra_decline` recomputation);
`experiments/exp_substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu.py` (full 869 lines,
including the `_acc_curve`/`_selftest`/`compute_verdict` functions specifically diffed against each other to
locate the wiring gap).

**Total: 4 fresh external searches + 11 carried/re-verified external citations (from same-day/prior sibling
drills, not re-fetched, per 2x-drill discipline) + 4 internal artifacts hand-recomputed off-disk = 19 verified
sources/checks.**
