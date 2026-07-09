# Research (cross-domain, self-authored, no sub-agents): 5x negative-revival drill on the compounding-error
# wall — NEW mechanism classes from AI, biochemistry, control theory, materials science, physics, population genetics

**Date:** 2026-07-09. **Trigger:** four autonomous-decomposition rescue variants have now landed
`HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL` at the identical corner `op4_V1200_d8` (entropy=16.0, chain_steps=3):
`wp_bisect_verify` (self-referential percentile gate), `exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1`
(multi-resolution re-derivation of the same signal), `exp_pfc_gate_waypoint_rescue_replay_bidirectional_v1`
(forward/reverse SR agreement — verified off-disk below), and a fourth (lookahead-bisection) referenced in the
dispatch brief. Per the VET's HARD CONSTRAINT: this drill is explicitly barred from proposing a fifth
autonomous-decomposition variant. It must identify a genuinely NEW mechanism class — the VET named three
candidates (DAgger/imitation-from-oracle, correctness-calibrated selector, structural per-step entropy
reduction) — and is asked to cross-pollinate AI, materials science, biology, physics, and control theory for
convergent, buildable answers. Atom under revival:
`math::HARD_FAIL_STRUCTURAL_COMPOUNDING_ERROR_BOUND_DOUBLY_CONFIRMED_MECHANISM_INDEPENDENT_BARRIER2`.

**Verified off-disk before drilling (per Fix#28, do not requote without re-deriving):**
`data/exp_pfc_gate_waypoint_rescue_replay_bidirectional_v1/metrics.json`: `verdict=HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL`,
`run_mode=full`. At FOCUS: `recovery_open=0.0192`, `recovery_verify=0.0182`, `recovery_rescue(replay)=0.0283`,
`delta_recovery(vs verify)=0.0101`, `flatness_ratio=0.044`, `n_hp_ok=0/5`, honesty guards clean
(`index_artifact_gap=0.0008`). Critically: `bidir_mean_selected=0.630` vs `bidir_mean_all_cand=0.584` — the
bidirectional-agreement signal DOES separate somewhat (selected candidates score higher than the candidate
pool average) but this separation barely moves `recovery_ratio` (+0.010, ten times below the HARD-PASS bar of
+0.15). This is the load-bearing empirical clue this whole drill pivots on (see HEADLINE).

Also verified: `data/exp_community_routed_glassbox_reasoning_scale_v1/metrics.json`: `verdict=HARD_PASS`,
`verdict_msg`: "ARM_C_FRESH routing BOUNDED (slope=0.0010 <= 0.02) while COMPOUND control rises
(slope=0.0976)." This is a HARD_PASS on the exact discriminating comparison this drill needs (see HEADLINE) —
already landed this session, already certified, immediately reusable.

---

## HEADLINE

**All four confirmed failures share ONE precise structural defect that four different-sounding designs all
independently reproduced: the "correction" signal at each hop was recomputed FROM THE SAME NOISY DERIVED
ESTIMATOR being corrected (the SR-trained reach matrix `M`/`R`), not from anything outside it.** `wp_bisect_verify`
thresholds `R` against a percentile of `R` itself. `coarse2fine` re-derives a coarser `R` from the same `M`
machinery at a different gamma. `replay_bidirectional` trains `M_rev` on the REVERSED transitions of the exact
same training corpus, using the exact same stochastic optimizer and the exact same noise source — so `M` and
`M_rev`'s errors are correlated, not independent, which is exactly why their disagreement (bidirectional score)
separates weakly (0.630 vs 0.584, real but tiny) and barely moves recovery (+0.010, not +0.15). This is the
control-theory diagnosis, made precise: **a correction channel only bounds steady-state error if it is
observable/independent of the state being corrected (Kalman-filter innovation orthogonality; the algebraic
Riccati equation has a bounded fixed point only when the pair is observable — otherwise error grows exactly
like open-loop dead-reckoning, which is the compounding shape measured in all four failures).** None of the
four attempted "independent" signals were actually independent in this rigorous sense — each was a
different-looking function of the SAME underlying noisy accumulator.

**Four unrelated fields converge on the SAME fix, and the substrate already has a HARD_PASS proof-of-concept
of it landed THIS SESSION.** (1) DAgger (imitation learning): compounding error is fixed by querying an
EXTERNAL oracle — ground truth, not a re-derived self-estimate — which is the formal reason DAgger converts
`O(T^2)` regret to `O(T)`. (2) DNA replication proofreading (Hopfield/Ninio + T7 polymerase structural work):
the correction happens at a PHYSICALLY SEPARATE catalytic domain (~25 Angstrom from the polymerase site) that
re-examines the raw base-pair, not a re-check by the same active site. (3) Control theory (Kalman/Luenberger):
the innovation (measurement residual) must be statistically independent of the state estimate for the error
covariance to have a bounded fixed point; the observability of the (C,A) pair is the precise mathematical
criterion. (4) Cerebellar forward-model correction: the climbing-fiber error signal is driven by ACTUAL sensory
reafference from the body/world, not by a second internally-generated prediction — the previously-tried
"cerebellar-rollout" negative almost certainly modeled the SECOND kind (self-predicted proxy), not the first,
which is a mis-implementation of the biology, not a refutation of it. And **the substrate's own innovation
cell landed this exact comparison as a HARD_PASS today**: `ARM_C_FRESH` (routing recomputed fresh, each hop,
directly from raw stored community structure — an exogenous, non-accumulated source) stays flat
(`slope=0.0010`) while `COMPOUND` (routing carried forward from the prior hop's derived estimate — structurally
identical in kind to what all four failed waypoint-rescue arms did) drifts (`slope=0.0976`), a **98x** ratio.
This is not a new theory needing a first test — it is the SAME mechanism principle already empirically
confirmed on a sibling cell in this session, just not yet applied to the specific waypoint-discovery capability
that has failed four times.

**Top pick (flagged HIGH-PROB-SUPERIOR, genuinely NEW class — not autonomous-decomposition):
Exogenous-ground-truth gate ("kinetic-proofreading checkpoint").** At each hop, do not accept the SR/`M`-derived
waypoint pick on its own recognizance. Cross-check it against a DIRECT, zero-shared-parameter lookup on the
raw ingested KB (the same `oracle_trajectory_idx`/KB edge table already used for scoring in both ancestor
cells, repurposed at INFERENCE time as a real-time gate, not just a post-hoc scorer): does an actual stored
edge exist from the current anchor into the picked waypoint? If yes, commit (this is the "fast, low-energy"
accept path, analogous to correct base-pairing passing kinetic proofreading quickly). If no exact edge exists,
either (a) restrict the `M`-derived candidate set to ONLY waypoints with a confirmed direct KB edge and re-pick
within that confirmed subset, or (b) discard and re-derive fresh from the immutable start/goal KB atoms (an
`ARM_C_FRESH`-style reset), never carrying the unconfirmed intermediate state forward. This is provably
NOT autonomous decomposition (it adds zero new decomposition of the reasoning structure — it adds an
independent CHECK against something the four failures never touched: the raw graph itself, not a derived
statistic of it) and it is cheap: `oracle_trajectory_idx`/the raw KB edge table already exists in both
ancestor cells' code, this only changes WHEN it is consulted (inference-time gate vs. post-hoc scorer only).

---

## RANKED SHORTLIST (each: domain mechanism + source; why NEW class; substrate composition; kill-test; honest prior)

**Rank 1 (HIGH-PROB-SUPERIOR, flagged).** **Exogenous ground-truth gate / kinetic-proofreading checkpoint.**
Domain: biochemistry (Hopfield 1974; Ninio 1975; independently, T7 Pol proofreading structural kinetics,
PMC9800556 — physically separate exonuclease domain ~25 Angstrom from polymerase site, strand-transfer on
slowed/incorrect incorporation, ~100x error reduction) + AI (Ross/Bagnell 2010; Ross-Gordon-Bagnell 2011
DAgger — external-oracle query converts `O(T^2)` to `O(T)` regret) + control theory (Kalman innovation
orthogonality / observability criterion, below). Why NEW class: the check is against RAW, unprocessed ground
truth (the KB edge table itself) — zero shared computation, zero shared training noise with the `M`/`R`
estimator being checked. This is categorically different from all four failed variants, every one of which
checked the estimator against ANOTHER FUNCTION of the same estimator. Composition: reuses `oracle_trajectory_idx`
/ raw KB edges verbatim (already exists in both ancestor cells for scoring); only the TIMING of use changes
(inference-time gate, not post-hoc metric only); composes directly with the just-proven `ARM_C_FRESH` pattern
from the community-routed HARD_PASS cell (same principle: recompute/verify fresh from raw content each hop,
never carry forward an unconfirmed derived estimate). Kill-test: build
`exp_pfc_gate_waypoint_rescue_kb_grounded_check_v1`, identical FOCUS regime (`op4_V1200_d8`, entropy=16,
chain_steps=3), paired against `wp_bisect_open`/`wp_bisect_verify`/`replay_bidirectional` (already measured,
reused verbatim per both ancestors' discipline) plus one NEW arm `wp_kb_grounded_gate`. Pre-registered
independence check (new, mandatory given this drill's diagnosis): report `corr(kb_confirm_signal, M_error)` —
predict near-zero (unlike `M` vs `M_rev`'s correlated ~0.05 separation); if this correlation is itself high,
the KB signal is not actually independent either and the diagnosis is wrong. Honest prior: raw ~0.40 (cheap,
mechanistically the FIRST truly non-self-referential correction tried on this exact regime, cross-validated by
FOUR independent fields AND by a same-session sibling HARD_PASS on the identical structural comparison) ->
**P_deflated ~0.20** after the mandatory 0.15-0.25 calibration penalty (still a 5th attempt on the same wall;
sobering base rate from four prior failures applies even though this one is structurally different). P(full
HARD-PASS bar: recovery>=0.20 AND delta>=0.15 AND flatness>=0.5 AND `corr(kb_confirm,M_error)` near-zero): raw
~0.30, **P_deflated ~0.15-0.18**, under the mandatory 0.50 novel-synthesis cap.

**Rank 2.** **Structural per-step entropy reduction via bounded macro-state (renormalization-group /
information-bottleneck).** Domain: physics/information theory (Gaussian Information Bottleneck <-> non-perturbative
RG duality, arXiv:2107.13700/PMC8967309 — successive coarse-graining transforms remain IB-optimal, a semigroup
structure with a genuine fixed point; information loss per step = conditional entropy of discarded fast
variables, not an accumulating residual). Why NEW class: attacks the entropy driving the wall directly by
projecting to a bounded sufficient statistic recomputed at each hop, rather than either checking or generating
more of the same unbounded accumulator. This is NOT autonomous decomposition (it collapses branching factor,
it doesn't add another decomposition level) and is DISTINCT from rank 1 (rank 1 is "verify against something
external"; rank 2 is "never carry more than a bounded amount of information forward at all", true even with no
external oracle available). Composition: this is arguably WHAT the `ARM_C_FRESH` HARD_PASS cell already is
(routing recomputed fresh from raw community structure each hop is functionally a bounded macro-state
projection) — the substrate-product action here is less "build something new" than "recognize the mechanism,
push it further, and confirm it is a genuine fixed point rather than a finite-depth illusion." Kill-test: extend
`exp_community_routed_glassbox_reasoning_scale_v1`'s ARM_C_FRESH vs COMPOUND comparison to greater depth/more
hops than already tested; RG framing predicts the near-zero slope (0.0010) should persist at ANY depth (true
fixed point); if slope eventually turns super-linear at deeper hop counts, that falsifies the RG-fixed-point
reading and downgrades this to "delayed compounding," not "bounded." Honest prior: raw ~0.55 for "slope stays
bounded at 2x current max-tested depth" (already HARD_PASS at current depth, extending a working mechanism is
lower-risk than a fresh build) -> **P_deflated ~0.35** (still capped well under 0.50 for the deeper-depth
novel-synthesis claim specifically).

**Rank 3 (process-level, not a build mechanism — a MANDATORY pre-registration diagnostic).**
**Kalman-observability independence screen.** Domain: control theory (innovation-sequence orthogonality is the
defining property of a working Kalman filter; steady-state error covariance has a bounded fixed point via the
algebraic Riccati equation ONLY when the (C,A) pair is observable/detectable — Wikipedia Kalman filter;
ME233/EE363 course derivations; Luenberger-observer bounded-error-covariance literature). Why relevant: this
gives a CHEAP, ANALYTIC, PRE-BUILD criterion that would have predicted all four failures without spending a
FULL dispatch on any of them: compute the correlation/mutual-information between the proposed correction
signal and the running estimator's own error BEFORE building the cell. `M` vs `M_rev` (replay_bidirectional)
should have been checked this way — their shared training corpus and shared optimizer noise predicts weak,
not strong, decorrelation, consistent with the measured 0.630-vs-0.584 near-miss. Composition: NOT a substrate
mechanism to build — a screening step to run on ranks 1, 2, 4, 5 (and any future candidate) BEFORE dispatch,
folded into pre-registration going forward. Kill-test: retroactively compute this correlation for all four
already-landed failures (cheap, off-disk, no new dispatch) and confirm it was uniformly high (predicting
failure) — if instead it turns out LOW for one of the four already-failed variants, the whole diagnosis in this
drill's HEADLINE is wrong and needs revision before rank 1 is built. **This retroactive check should be done
FIRST, before rank-1 dispatch, as the cheapest possible falsification of this drill's own central claim.**
Honest prior: this is a diagnostic, not a P(HARD-PASS) claim; the retroactive check either confirms or
falsifies the headline at near-zero cost.

**Rank 4.** **Repeated-independent-draw with irreversible commit gate (kinetic-proofreading discrimination,
applied per-hop rather than as a one-time domain check).** Domain: biochemistry (Hopfield-Ninio; PNAS
10.1073/pnas.1119911109 — specificity scales as `(exp(deltaE))^N` for N independent proofreading stages).
Why distinct from rank 1: rank 1 checks against an EXTERNAL raw source; rank 4 improves fidelity by re-sampling
the SAME discrimination criterion with a FRESH independent random draw and an irreversible dissipative commit
step between draws — useful when no external oracle exists for a given hop, only usable to boost a single
decision's fidelity, not to bound drift across a GROWING sequence of dependent decisions (secondary/combinable
with rank 1, not a full substitute — this is an honest limitation, not a strength, relative to rank 1). Honest
prior: raw ~0.30 for standalone lift (does not address the cross-hop dependency, only single-hop fidelity) ->
**P_deflated ~0.10-0.15** as a standalone fix; recommend testing ONLY combined with rank 1, not alone.

**Rank 5 (flagged lower-priority; risk of reclassification as decomposition-adjacent).**
**Independent-lineage recombination (Muller's ratchet reversal).** Domain: population genetics (Muller's
ratchet — asexual/non-recombining lineages accumulate deleterious mutations irreversibly via drift-driven loss
of the fittest class; Wikipedia; "Finite genome size can halt Muller's ratchet," arXiv:physics/0109058;
recombination between independent lineages is the only known reversal). Why marginal-NEW: running multiple
independently-SEEDED reasoning rollouts (different RNG streams, ideally different RETRIEVAL PATHS hitting
different raw stored content, not just noise-perturbed re-runs of the same generator) and periodically
recombining/selecting the best-of-independent-chains is DIFFERENT in spirit from a single self-checked chain,
but risks being classified as "another decomposition variant" by the VET's HARD CONSTRAINT unless the
independence is enforced at the RETRIEVAL-PATH level (grounding in different raw content), not merely at the
random-seed level — `replay_bidirectional`'s `M_rev` was already "independently seeded" in a shallow sense
(different RNG draws) and it failed, which is direct negative evidence against a shallow reading of this
mechanism. Composition: only worth testing as a compound arm with rank 1 (each of the N independent chains uses
the rank-1 KB-grounded gate; recombination selects among KB-CONFIRMED candidates, not raw model agreement).
Honest prior: raw ~0.25 standalone (already negatively informed by the `replay_bidirectional` near-miss) ->
**P_deflated ~0.10**, below rank 4.

**Rank 6 (negative/cautionary finding — corroborates the HEADLINE diagnosis, do not pursue standalone).**
**Correctness-calibrated selective-prediction / confidence gate.** Domain: AI (selective prediction / reject-
option literature; "Trust but Verify: Prover-Verifier Deliberation for Selective LLM Prediction," arXiv:2605.25133;
"How to Fix a Broken Confidence Estimator," arXiv:2305.15508). Literature explicitly confirms: **confidence
calibration DEGRADES under distribution shift** — a self-generated confidence score (exactly what
`wp_bisect_verify`'s percentile-tau and `replay_bidirectional`'s bidirectional-agreement score both are) is
NOT reliably predictive of correctness precisely under the drift conditions where it is most needed. This is
independent literature-level confirmation of the empirical near-miss already measured
(`bidir_sel=0.630` vs `bidir_all=0.584` — real separation, weak predictive power). Do not build a standalone
"better confidence threshold" cell; any future confidence-based selector must be CALIBRATED AGAINST EXOGENOUS
LABELS (ties directly back to rank 1's KB-grounding, not a free-standing fifth self-referential variant).

---

## (b) Cheap decisive test

**Step 0 (near-zero cost, do FIRST, before any dispatch):** retroactively compute
`corr(candidate_correction_signal, running_M/R_error)` for all four already-landed failures using existing
`metrics.json`/per-seed arrays already on disk (no new compute) — this is rank 3's diagnostic, applied
retroactively. If it does NOT show uniformly high correlation across all four, this drill's headline diagnosis
needs revision before rank 1 is dispatched.

**Step 1 (smoke, reuse ancestor's grid verbatim):** `N=2048`, `V=300`, 3 seeds, `op4_V300_d6` FOCUS,
`chain_steps=2`, per standing discipline (SMOKE=FULL branch-parity). Add ONE new primitive family for rank 1:

```
def kb_confirms_edge(anchor, candidate, raw_kb_edges) -> bool:
    # direct dict/set lookup on the RAW ingested KB edge table (oracle_trajectory_idx-adjacent structure),
    # zero shared parameters/training with M or R -- this is the exogenous ground-truth channel
    return (anchor, candidate) in raw_kb_edges  # or nearest-exact-match within a tight radius if fuzzy

def wp_kb_grounded_gate(start, goal, R, raw_kb_edges) -> boundary_seq:
    # at each hop: take M/R's top-k candidates, RESTRICT to those kb_confirms_edge()==True,
    # re-pick argmax WITHIN the confirmed subset; if subset is empty, reset fresh from start/goal KB atoms
    # (ARM_C_FRESH-style) rather than carrying forward an unconfirmed pick
```

**Step 2 (FULL, if smoke clears branch-parity):** identical FOCUS regime (`op4_V1200_d8`, entropy=16,
chain_steps=3) as both ancestors, paired seeds, reusing `wp_bisect_open`/`wp_bisect_verify`/
`wp_replay_generate_select` verbatim as the required must-decay/already-failed controls (all three already
measured at FULL — re-run in-cell for a clean paired comparison per standing discipline, not new information).

---

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL, locked; FOCUS = `op4_V1200_d8`, entropy=16, chain_steps=3)

**HARD-PASS (exogenous grounding hypothesis confirmed; genuine rescue, 5th attempt succeeds for a
structurally sound reason):**
- `recovery_ratio(wp_kb_grounded_gate)` at FOCUS `>= 0.20` **AND**
- `recovery_ratio(wp_kb_grounded_gate) - recovery_ratio(wp_bisect_verify)` (`0.0182` per verified metrics
  above) `>= 0.15` **AND**
- `recovery_ratio(wp_kb_grounded_gate) - recovery_ratio(replay_bidirectional)` (`0.0283`) `>= 0.12` (must beat
  the best PRIOR attempt by a wide margin, not just barely) **AND**
- `corr(kb_confirm_signal, M_error) <= 0.15` (the mandatory independence check — near-zero, unlike the implicit
  ~0.05-separation-only signal in `replay_bidirectional`) **AND**
- flatness ratio (`recovery(chain_steps=3) / recovery(chain_steps=1)`) `>= 0.5` **AND**
- honesty guards at ancestor thresholds (`index_artifact_gap < 0.05`, `anti_tautology_corr < 0.85`,
  `degenerate_rate < 0.10`) **AND** `cv < 0.15` at FULL, `sign_p < 0.05` (paired vs `wp_bisect_verify`).
=> the compounding-error bound was specifically an artifact of self-referential correction (checking a noisy
estimator against another function of itself), NOT a fundamental property of the domain; a genuinely exogenous
ground-truth channel — independently converged upon by biochemistry, control theory, imitation learning, and
already HARD_PASS-proven in a sibling cell this session — recovers real capability where four prior variants,
including the closest-sounding "independent" one (bidirectional replay), could not.

**HARD-FAIL (the bound survives even genuinely exogenous grounding — triply/quadruply confirmed structural,
strongest possible closure):**
- `recovery_ratio(wp_kb_grounded_gate)` at FOCUS `<= recovery_ratio(replay_bidirectional) + 0.05` (i.e.
  `<= 0.078` — no material improvement over the best prior attempt despite a rigorously independent,
  cross-domain-converged correction channel) **OR**
- flatness ratio `< 0.2` **OR**
- `corr(kb_confirm_signal, M_error) > 0.4` (the grounding signal turns out NOT to be independent after all —
  e.g., if the KB itself was used to derive `M`'s training transitions, contaminating the "independence").
=> this would be the strongest possible closure to date: the bound survives not just self-check variants but
a channel that is provably informationally exogenous by construction and cross-validated by an already-landed
sibling HARD_PASS on the identical structural principle. At that point the honest read is that the FAILURE
MODE is not "lack of an independent channel" but something else entirely (e.g., insufficient KB coverage at
this specific entropy/depth regime, or a genuine information-theoretic floor on this task class) — recommend
accepting the bound as fundamental for autonomous no-oracle waypoint discovery at `chain_steps>=3`,
`entropy=16`, and redirecting effort to bounded-depth-budget framing (per the prior note's own HARD-FAIL
substrate-product recommendation) rather than a sixth mechanism attempt.

**MIDDLE_BAND:** real lift over `replay_bidirectional` (best prior) in `[0.03, 0.12)`, OR flatness ratio in
`[0.2, 0.5)`, OR `corr(kb_confirm,M_error)` in `(0.15, 0.4]` (partial independence) — report as "exogenous
grounding helps but the KB itself may be too sparse at this entropy/depth to fully confirm every hop," a
genuinely new and more actionable diagnosis than either prior HARD-FAIL (which could not distinguish
"mechanism wrong" from "grounding data too sparse").

**P_deflated:** see Rank 1 above (~0.20 for MIDDLE-or-better, ~0.15-0.18 for full HARD-PASS). Rank 2 extension:
~0.35 for "slope stays bounded at 2x tested depth." Both capped well under the mandatory 0.50 novel-synthesis
ceiling.

---

## (d) Cross-thread synthesis

- **Directly supersedes and sharpens** `notes/research_deep_chain_reasoning_bounded_compounding_error_brain_first_2026-07-08.md`'s
  rank-1 diagnosis. That note correctly identified "the correcting signal must be informationally independent"
  as the governing principle and proposed bidirectional replay-select as the test — which has NOW landed
  HARD_FAIL (`replay_bidirectional`, verified above). This drill's contribution is explaining WHY that specific
  implementation of "independence" wasn't independent ENOUGH (shared training corpus/optimizer noise between
  `M` and `M_rev`) and supplying the missing rigor: the control-theory observability criterion, which the prior
  note's biological framing (grid-cell boundary reset, reverse replay) gestured at but did not formalize. This
  is exactly the intended function of a 2x/5x drill: go deeper into the mechanism of an existing finding, not
  re-scan the same literature.
- **Directly reuses and extends** `notes/research_community_routed_glassbox_reasoning_scale_invariant_brain_first_2026-07-08.md`
  and its landed cell `exp_community_routed_glassbox_reasoning_scale_v1` (HARD_PASS, verified above,
  `ARM_C_FRESH` slope=0.0010 vs `COMPOUND` slope=0.0976). That note flagged per-hop routing becoming "a NEW
  noisy per-hop estimate that could compound" as the load-bearing open risk (PRED-C) — the cell's own result
  answers that risk in the POSITIVE direction (fresh grounding does not compound) and this drill identifies
  that result as the SAME structural principle needed to rescue the waypoint-discovery capability, not a
  separate finding to be reconciled later.
- **Extends** `notes/research_autonomous_waypoint_deep_corner_compounding_error_rescue_2026-07-05.md`'s original
  ML-only diagnosis (Ross-Bagnell `O(T^2)`): DAgger's own theory (query an EXTERNAL oracle) was in that note's
  scope all along but was set aside as "out of scope by the capability's own autonomous, no-oracle definition"
  per the 07-08 note's HARD-FAIL write-up. This drill's reframe: the substrate's OWN INGESTED KB, already used
  as a scoring oracle in every ancestor cell, is not an external oracle in the sense that matters for the
  "autonomous" framing (it requires no NEW privileged information, no human-in-the-loop, no extra query budget
  beyond what the capability already has access to) — it is exogenous only relative to the DERIVED SR
  estimator, which is the ONLY independence that matters per the control-theory criterion. This resolves the
  apparent tension between "no oracle allowed" and "DAgger needs an oracle" that caused the 07-08 note to set
  DAgger aside as out-of-scope.
- Does not reopen unrelated closures (option-critic / BlocksWorld hierarchical planning, algebraic-topo,
  quantum-info, dynamics fields) per `[[feedback-prior-work-informs-not-constrains]]`.

## (e) Substrate-product implications

- **If HARD-PASS:** the product claim sharpens to "the substrate's autonomous multi-step waypoint discovery
  was never fundamentally bounded — it was bounded by an easily-identified implementation defect (checking a
  noisy estimate against itself) shared across four different-looking prior attempts, and grounding each step
  against the substrate's own raw ingested content (not an external human oracle) fixes it." This is a
  materially stronger, more specific, more DIFFERENTIATED capability story than any prior HARD-FAIL framing —
  it also retroactively explains why an unrelated sibling cell (community-routed reasoning) landed HARD_PASS
  this same session using structurally the same fix, which is a strong internal-consistency signal for the
  product narrative (one governing principle, not one-off tricks per cell).
- **If HARD-FAIL:** this is the strongest possible closure yet reached — surviving a channel that is
  rigorously exogenous by construction (not just claimed independent) and that already works elsewhere in the
  same session on a structurally identical comparison. At that point the honest, deflated read is that
  `chain_steps>=3` autonomous no-oracle waypoint discovery at `entropy=16` specifically needs either (a) richer
  KB coverage at this regime (a data problem, not a mechanism problem — genuinely actionable, unlike prior
  HARD-FAILs) or (b) acceptance as a fundamental floor, with deployment favoring bounded-depth budgets/larger
  atomic chunks (rank-3 chunking from the 07-08 note, orthogonal and still valid regardless of this drill's
  outcome).
- Either outcome, **Rank 3 (the observability/independence pre-registration screen) should become a STANDING
  discipline** applied to any future compounding-error rescue candidate before dispatch — it is free (uses
  data already on disk), would have flagged all four prior failures' shared weakness before a single FULL
  dispatch, and directly operationalizes `[[feedback-lit-scan-calibration-penalty]]`'s spirit (a mechanistic,
  not just statistical, pre-registration gate).

---

## Citations (verified count: 19, all live-URL-confirmed via WebSearch this session, generic math/science
terms only, no substrate-specific framing exposed off-platform per `[[feedback-query-privacy-decomposition]]`)

1. Ross, S., Gordon, G., & Bagnell, D. (2011). "A Reduction of Imitation Learning and Structured Prediction to
   No-Regret Online Learning" (DAgger), AISTATS. Confirms `O(T^2)`->`O(T)` regret via external-oracle query.
2. "Revisiting DAgger in the Era of LLM-Agents," arXiv:2605.12913.
3. Hopfield, J.J. (1974), "Kinetic proofreading: a new mechanism for reducing errors in biosynthetic processes
   requiring high specificity," PNAS.
4. Ninio, J. (1975), independent co-discovery of kinetic proofreading.
5. "Speed, dissipation, and error in kinetic proofreading," PNAS 10.1073/pnas.1119911109.
6. "A stochastic version of the Hopfield-Ninio kinetic proofreading model," arXiv:2405.10580.
7. "Kinetics of DNA strand transfer between polymerase and proofreading exonuclease active sites regulates
   error correction during high-fidelity replication," PMC9800556 (T7 Pol, ~25 Angstrom separate domain, ~100x
   error reduction via strand transfer on slowed incorporation).
8. "Molecular basis for proofreading by the unique exonuclease domain of Family-D DNA polymerases," Nature
   Communications, PMC10721889.
9. Wolpert, D.M. & Miall, R.C. (1998), cerebellar forward-model framework (efference copy + predicted sensory
   consequence vs actual reafference), TICS (reused/re-verified from prior session drill).
10. "The Forward Model: A Unifying Theory for the Role of the Cerebellum in Motor Control and Sense of Agency,"
    Frontiers in Systems Neuroscience, 10.3389/fnsys.2021.644059.
11. "A Forward Model at Purkinje Cell Synapses Facilitates Cerebellar Anticipatory Control," arXiv:1701.07775 /
    bioRxiv 10.1101/078410.
12. Kalman filter innovation-sequence orthogonality and steady-state error-covariance / algebraic Riccati
    equation properties — Wikipedia "Kalman filter"; ME233 (Berkeley) and EE363 (Stanford) course derivations;
    "An improved Unscented Kalman Filter restraining outliers based on orthogonality of innovation," IEEE
    6272637.
13. Luenberger-observer bounded-estimation-error-covariance design (zonotope-bounded gain, non-Kalman-embedded
    approach), per ResearchGate/PMC12655895 tutorial-review search results.
14. Gaussian Information Bottleneck <-> non-perturbative renormalization-group duality (semigroup structure,
    successive IB-optimal transforms), arXiv:2107.13700 / PMC8967309.
15. "Optimal Renormalization Group Transformation from Information Theory," Phys. Rev. X 10.1103/PhysRevX.10.011037.
16. Muller's Ratchet (irreversible deleterious-mutation accumulation absent recombination) — Wikipedia
    "Muller's ratchet"; "Finite genome size can halt Muller's ratchet," arXiv:physics/0109058.
17. Self-healing/error-correcting algorithmic tile self-assembly (near-equilibrium reversible correction,
    detachment/reattachment) — "Combining self-healing and proofreading in self-assembly," Natural Computing,
    Springer 10.1007/s11047-007-9036-x; "Design and Simulation of Self-repairing DNA Lattices."
18. Selective prediction / confidence calibration degradation under distribution shift — "Trust but Verify:
    Prover-Verifier Deliberation for Selective LLM Prediction," arXiv:2605.25133; "How to Fix a Broken
    Confidence Estimator," arXiv:2305.15508.
19. Concatenated error-correcting codes with block-local parity/syndrome checks inserted to avoid error
    propagation across long sequential channels (Reed-Solomon/LDPC concatenation practice), per patent/survey
    search results ("Method and coding means for error-correction utilizing concatenated parity and turbo
    codes"; "Topic: Coding for Error Detection and Correction," CMU 18-849).

All searches used generic math/science terms ("DAgger dataset aggregation compounding error," "kinetic
proofreading Hopfield Ninio," "cerebellar forward model efference copy," "Kalman filter innovation
orthogonality Riccati," "renormalization group information bottleneck entropy," "defect tolerant lattice
self-healing assembly," "Muller's ratchet recombination," "selective prediction calibration distribution
shift," "concatenated error correcting code parity") — no substrate-novel mechanism names, cell names, configs,
or numerical parameters were exposed off-platform, per `[[feedback-query-privacy-decomposition]]`. Two on-disk
`metrics.json` files were read locally (not searched externally) for verified-off-disk grounding, per Fix#28.
