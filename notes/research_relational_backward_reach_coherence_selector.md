# Relational backward-reach / coherence-based binding selector: design drill

### 2026-08-04, Director (research role). Design-only, no cell authored/dispatched.

**MID-DRILL REDIRECT INCORPORATED.** The task brief as issued presumed decodability is dead for
relational binding (goal-outcome aggregate = 0.0) and asked only for the backward-reach spec. A
coordinator redirect arrived mid-drill challenging that premise as resting on a non-apples-to-apples
test. I disk-verified the redirect's claim before accepting it (see Section 1) — it is correct. This
note therefore **leads with a fair-decodability re-test design (new primary deliverable)** and
**demotes the backward-reach spec to a conditional fallback**, per the redirect's explicit
instruction. Everything else in the original brief (biology-first, WIRE-don't-island, anti-recency +
load-artifact guards, P_deflated discipline, local-only git commit) stands.

---

## HEADLINE

The claim "decodability is dead for relational binding, therefore build a new SR-backward organ" is
**not yet earned** — the cell that produced `aggregate_decodability_extends_to_goal_outcome=n`
confounded relation-KIND with three other variables (data-realness, role-vocab richness, register
slot-count) simultaneously, and its own internal sub-arms (`foilheavy`/`ownerheavy`/`matched`)
already show the "signal" is register-LOAD-tracking, not relation-kind-tracking, on BOTH sides of
the comparison — this needs to be checked for coref too before either verdict can be trusted. **The
correct next step is a fair, load-controlled, single-register apples-to-apples test that embeds
goal-owner binding in the SAME full situation model coref uses** (Section 2), not a new backward-SR
build. Only if that fair test *also* fails does the relational-reach organ from the original brief
(Section 5, already spec'd in the 2026-08-03/2026-08-04 prior drills, disk-verified sound but its
biology-to-text bridge unbuilt) become the next thing to build.

---

## 1. Disk-verifying the redirect: the confound is real

Read `data/exp_coherence_aggregate_discriminates_goal_outcome_v1/metrics.json` `config` block
directly (not from memory):

```
coref_role_vocab = [agent, experiencer, theme, patient, recipient, possessor, addressee, goal, instrument]  (9 roles)
coref_max_event_slots = 16
n_coref_passages = 18   (real McGuffey text, per experiments/exp_coherence_aggregate_discriminates_goal_outcome_v1.py line 15: "g5g6_reviewed McGuffey passages")
go_role_vocab = [GOAL, ACTION_AGAINST, OUTCOME_UNMET, OUTCOME_MET]  (4 roles)
go_max_event_slots = 8
n_go_matched = n_go_foilheavy = n_go_ownerheavy = n_go_shuffled = 4   (synthetic hand-built role_seq items, per line 17: "synthetic multi-position items")
```

Confirmed exactly as the redirect states: coref arm = 18 real passages / 9-role vocab / 16 slots;
goal-outcome arm = 4 synthetic items / 4-role vocab / 8 slots. Four variables move at once
(relation-kind, realness, vocab richness, N) between the arm that scored 1.0 and the arm that scored
0.0. Grepping `hdlab/situation_model_accumulate.py` for `GOAL`/`goal_owner`/`GoalOutcome` returns
**no hits** — the goal-outcome register is a standalone construction in the experiment file, never
integrated into the same full multi-role situation model coref uses. The verdict
`aggregate_decodability_extends_to_goal_outcome=n` is real as a *statement about this specific
under-matched comparison*; it is not yet evidence about relation-kind per se.

**The load-redistribution mechanism, read directly from the code** (`hdlab/self_improving_loop.py`
lines 56-89, `decode_coherence_margins`): `reg.add_event(cid, role, slot)` binds every position's
`(role, slot)` into the register keyed by whichever `cluster_id` that position is assigned to under
a given candidate resolution. When two candidates disagree on a position's `cluster_id`, they are
disagreeing about *which entity's register absorbs that event's storage load*. Decode margin at a
given `(cid, slot)` is `top1_score - runner_up_score` — a quantity that is well known to shrink as an
`AccumulateRegister`'s per-entity bundle gets busier (this codebase's own capacity certs, e.g. atom
29609, establish decode fidelity degrades with load). So **a coref candidate that is "more coherent"
also, by construction, changes how many events pile into each entity's register** — the margin signal
may be measuring "does this resolution redistribute load more favorably," not "is this resolution
semantically more coherent." These are only the same thing by accident in the current coref item set.

**This is directly confirmed as the mechanism on the goal-outcome side, in the SAME already-run cell**:
`go_foilheavy_adopt_rate=1.0` (foil/distractor carries MORE events -> selector adopts at ceiling),
`go_ownerheavy_adopt_rate=0.0` (true owner carries more events, load direction reversed -> selector
adopts at floor), `go_matched_adopt_rate=0.0` (load exactly equalized -> no signal at all). This is
the textbook signature of a pure load-tracking detector, not a truth-tracking one: adoption rate
flips with which side is heavier, independent of which side is correct, and collapses to zero the
instant load is equalized. `bands.load_artifact_ruled_out=false` in that same file already says this
in the machine-readable verdict. **What has NOT yet been tested is whether coref's own 1.0 win is the
identical artifact** — the 18 real passages were never load-matched between candidates, so the
possibility that coref's "coherence win" is ALSO pure load-redistribution, just accidentally
correlated with truth in this item set, is open and unaudited.

**Conclusion, matching the redirect exactly:** the 0.0-for-goal-outcome result is confounded on (at
least) two independent axes — vocab/slot/realness mismatch, AND an explicit load-matching
manipulation that was never applied symmetrically to the coref arm. Before building a new organ, the
honest next step is a fair test that removes both confounds at once.

---

## 2. Biology grounding for what "fair" means here

This section answers the brief's "which brain structure, on what signal" question for BOTH
questions this drill now carries (fair decodability re-test AND, conditionally, backward-reach).
Two independent Sonnet lit-scans were dispatched this session (generic-term queries only, per
query-privacy discipline); findings synthesized below, citations in Section 8.

**Kintsch's Construction-Integration (CI) model** (Kintsch 1988, 1998) is explicitly two-staged:
*construction* generates a loose, context-insensitive candidate net (including wrong/irrelevant
associations, no early pruning); *integration* is iterative spreading-activation relaxation over that
net to a stable fixed point, where jointly-reinforcing (globally coherent) propositions survive and
locally-plausible-but-globally-isolated ones decay. The textbook argument for why this beats a
single best-local-candidate pick: a candidate can be maximal on its OWN local association strength
yet incoherent once checked against everything ELSE the model currently holds about the same entity —
exactly the property this drill's fair-test design needs to engineer into the goal-outcome item set.
This is the direct theoretical warrant for the redirect's instruction: don't test the GOAL slot in
isolation; embed it so a wrong choice has to survive contact with the rest of the entity's bindings.

**Landscape model / causal network models** (van den Broek et al. 1999; Trabasso & van den Broek
1985) give this a concrete, already-implemented-in-the-literature mechanism: candidate antecedents
carry a per-cycle activation value that is a function of (a) current co-occurrence, (b) prior
activation, and (c) causal/coherence relatedness accumulated in the network so far — a genuinely
relational, whole-network property (an event's importance is predicted by its number of causal
connections in the network, not by recency of mention). This is the model-level analog of "does
binding X here conflict with X's other established roles," independent of any load-count artifact.

**CA3 as a recurrent autoassociative attractor** (Rolls and others, standard hippocampal-systems
account): CA3 relaxes over multiple internal recurrent iterations from a partial/noisy cue to a
previously-stored stable pattern — genuine multi-step settling, not a single feedforward evaluation.
The lit-scan found that ML work approximating CA3 with a single feedforward pass explicitly frames
this as an efficiency-motivated simplification that discards completion dynamics, not as a claim of
equivalence — single-pass margin scoring (`decode_coherence_margins`, one shot, no relaxation) is a
*brain-compatible approximation*, not a fully brain-faithful one. This matters for how much weight to
put on a HARD-PASS from the one-shot fair test below: a pass licenses "the cheap approximation
suffices here," not "this is how CA3 does it."

**Reverse replay / need-x-gain** (Foster & Wilson 2006; Ambrose, Pfeiffer & Foster 2016; Mattar & Daw
2018) is well-established in the SPATIAL domain as backward, outcome-triggered credit assignment:
reverse-ordered place-cell reactivation at reward arrival, with "gain" (expected value-improvement
from updating a state) driving propagation backward through predecessor states from a newly-updated
outcome. Critically, per this session's lit-scan: **no literature was found that formally defines a
"Predecessor Representation" as a clean backward counterpart to the Successor Representation, and no
paper shows the backward map is a transpose of the forward one** — this independently confirms and
strengthens the 2026-08-03 drill's disk-finding that `M_backward` requires its own training pass, not
a free transpose of the certified forward `M`. More important for THIS drill: **no literature was
found bridging spatial hippocampal replay/need-x-gain models to narrative/text credit assignment at
all** — narrative-comprehension neuroscience (event segmentation, hippocampal reinstatement during
discourse) and the replay-credit-assignment literature are separately well-studied but not yet
connected by any shared formal model. This is the honest state of the sim-to-text bridge the
conditional Section 5 spec depends on: it is a plausible, brain-motivated extrapolation, not an
established transfer.

**Narrative event-chain learnability from real text IS established**, separately: Chambers &
Jurafsky (2008, "Unsupervised Learning of Narrative Event Chains") show verb-argument co-occurrence
statistics keyed on shared coreferring protagonists yield ordered (predecessor/successor) narrative
chains directly from raw text, no synthetic domain needed. This is relevant only to the CONDITIONAL
Section 5 (it says real-text event-transition structure with learnable order DOES exist, addressing
part of Gap 1) — it does not bear on the fair-decodability question in Section 3, which is the
primary deliverable.

---

## 3. THE FAIR TEST (primary deliverable)

**Goal:** determine whether relational-role decodability (the SAME `decode_coherence_margins` /
`route_passage` organ already validated for coref) can discriminate a coherent goal-owner/causal
antecedent from a plausible-but-wrong one, when relation-kind is the ONLY thing that varies —
removing realness, vocab-richness, slot-count, and load-symmetry as confounds simultaneously.

### 3a. Design principle: ONE register, not two

Do not build a separate `go_role_vocab`/`go_max_event_slots` register at all. Extend the SAME
9-role, 16-slot register coref already uses (`coref_role_vocab` in
`experiments/exp_coherence_aggregate_discriminates_goal_outcome_v1.py`) with two new roles, `GOAL`
and `ACTION_AGAINST` (or reuse existing `experiencer`/`patient`/`agent` roles compositionally if a
genuinely new role type is judged unnecessary — a design call for whoever authors the cell, not
pre-baked here). This single change removes the vocab-richness and slot-count confounds by
construction, and is a near-zero-code change per the build-spec note's own Section 3 table ("genuine
build = a harness that supplies goal/outcome role_vocab ... in place of coref cluster ids" — this
just means: same register class, same call site, additional role labels).

### 3b. Design principle: real passages, not synthetic hand-built items

Source both coref AND goal-outcome test items from the SAME 18 (or more) real, `g5g6_reviewed`
McGuffey passages already used for the coref arm — i.e., find or construct passages in that corpus
where a goal/desire is stated (e.g. "X wanted the toy," "X's plan was blocked by Y") and score
goal-owner attribution on THOSE passages' natural events, not on hand-built 4-item synthetic role
sequences. This removes the realness and N confound (both arms then draw from the same population).
If the existing McGuffey passage set does not contain enough naturally-occurring goal/blocked-goal
constructions at N>=10, that shortfall should be reported honestly as a data-availability gap, not
patched by reverting to synthetic items with a wider excuse.

### 3c. Design principle: downstream-embedded error, not isolated-slot error (the core fix)

This is the redirect's central instruction and the one that actually tests Kintsch-CI-style
coherence rather than a register-load artifact. Construct each item so the WRONG goal-owner
candidate is not a free-floating alternative but an entity that **already has other established role
bindings elsewhere in the SAME passage register** (e.g., the foil is independently bound as
`agent` in an earlier clause, or `possessor` of an unrelated object) — so that binding it ALSO as
`GOAL`-owner requires its register to reconcile a role assignment against everything else already
known about it, exactly the "does this configuration cohere with the rest of the model" test CI and
the Landscape model formalize. Symmetrically, the TRUE owner should also carry other established
role bindings, so that BOTH candidates have non-trivial context to be checked against — the
discriminating variable must be relational fit, not "does the foil have any other bindings at all."

### 3d. Design principle: directly test the load-redistribution hypothesis on BOTH arms

Add a fourth condition, symmetric across coref and goal-outcome: an explicit **load-matched control**
where both candidates' total register load (event count bound to that `cluster_id` across the whole
passage) is held numerically equal, exactly as `_go_matched_items()` already does for goal-outcome
(reuse that construction pattern) — but NOW ALSO applied to a matched subset of the coref items
(construct or select coref recency-trap items where the two candidate antecedents have equal
downstream mention/role counts). **Prediction to be pre-registered, not assumed:** if coref's own win
is load-redistribution-in-disguise, the load-matched coref subset should ALSO collapse toward 0
adopt-rate, mirroring `go_matched_adopt_rate=0.0`. If coref's win survives load-matching (stays
meaningfully above the abstain band) while an equivalently load-matched, downstream-embedded
goal-outcome item ALSO survives, that is the first honest evidence that decodability discriminates
relation-kind-independent coherence, not just load.

### 3e. Pre-registered bands

- **HARD-PASS (decodability survives, ship it, no new organ needed):** on the fair,
  downstream-embedded, load-matched, same-register, same-corpus item set, BOTH coref and goal-outcome
  adopt-rates clear the abstain band (>0.02, non-trivially, not a single-item fluke) AND a
  shuffled-role-sequence control (reuse `_shuffle_role_seq`, already built) collapses toward 0 for
  BOTH arms (rules out positional/structural memorization) AND the load-matched subsets (3d) do NOT
  collapse to 0 for either arm (rules out load-redistribution as the sole driver). This licenses
  extending `decode_coherence_margins`/`route_passage` to goal-outcome and causal directly — no
  backward-SR organ needed; Section 5 stands down as unnecessary for THIS gap (may still be relevant
  to genuinely multi-hop causal chains, which stay out of scope here per the 2026-08-04 build spec's
  own scoping note).
- **MIDDLE-BAND:** coref survives load-matching but goal-outcome (even downstream-embedded, real,
  matched-vocab) still collapses to 0, OR vice versa. Read as: the mechanism-class question is now
  cleanly separated from the confounds, and a genuine relation-kind asymmetry may exist — but this
  is now evidence, not an artifact of test construction. Triggers Section 5 (conditional spec) for
  the arm(s) that failed, not for both.
- **HARD-FAIL:** BOTH arms collapse to 0 once load-matched (i.e., load-redistribution was ALSO
  carrying coref's apparent 1.0, and once removed, no genuine coherence signal remains for either
  relation kind at the one-shot decodability grain). This would be the strongest finding of the three
  bands: it would mean `decode_coherence_margins`'s prior "coref works" result (atom 29609, the
  build-spec note's Section 1b) needs re-auditing for the same load-artifact this drill is chasing —
  a materially bigger finding than either 0.0-for-goal-outcome result alone, and should be escalated
  (not just logged) if it occurs, since it would revise a previously-"confirmed reuse" claim.
- **Positive control (must fire in all bands, sanity gate):** the ORIGINAL, non-load-matched, natural
  McGuffey coref items (18 passages, as already run) must continue to score `net_auto=1.0`
  when re-run through the same harness unmodified — if re-running the exact prior config on the exact
  prior data does not reproduce 1.0, the fair-test harness itself has a bug, stop and fix before
  trusting any band above.

### 3f. What this test does NOT resolve

Per Section 2's CA3 caveat: even a clean HARD-PASS here only licenses the one-shot
`decode_coherence_margins` approximation as *sufficient for this item set's difficulty*, not as fully
brain-faithful relative to CA3's genuine iterative settling. If a later, harder eval (multi-candidate,
>2-way competition, weaker lexical cues) shows the one-shot signal degrading where a human reader
would not, iterative settling (Kintsch CI implemented as literal multi-pass relaxation over the
register, not yet built anywhere on disk — confirmed by search) becomes the next brain-fidelity
upgrade, orthogonal to the fair-vs-confounded question this section resolves.

---

## 4. Unification check for the fair-test path

If Section 3 reaches HARD-PASS or MIDDLE-BAND-favoring-decodability, the SAME organ
(`decode_coherence_margins` + `route_passage`/`decide_keep_or_revert`) serves coref, goal-outcome,
AND (by identical construction — embed the causal `CAUSE`/`EFFECT` roles into the same full register
with downstream-linked foils) causal antecedent selection, through the literal same function calls,
not merely "the same organ class." This would be a materially stronger unification than the
2026-08-04 build spec's "one SELECT, instance-specific SCORE" finding — it would mean the SCORE also
unifies, once tested fairly, and the earlier causal-specific finding (`CausalLinkRegister` write/read
is symmetric, decode-margin can't discriminate) should be re-checked under the SAME downstream-
embedding fix before being treated as a settled negative — the 2026-08-03 causal drill's negative was
diagnosed from the register's write-then-read symmetry (a real, different problem: no scoring occurs
at all in `CausalLinkRegister.add_causal_link`), which this fair-test redesign does not by itself fix
for causal (causal's problem is architectural — no competition mechanism exists in that class at
all — not a confound in how goal-outcome's test was built). **Scoped conclusion: Section 3's fair
test directly re-opens the goal-outcome question and, by identical construction, extends to any
FUTURE relational-binding instance that (like coref) already flows through
`decode_coherence_margins`; it does NOT by itself resolve causal, whose gap is that no candidate ever
competes for a slot in `CausalLinkRegister` in the first place (a construction/generation gap, named
Gap 2 in the 2026-08-03 drill, not a scoring-fairness gap).**

---

## 5. CONDITIONAL fallback: the backward-reach organ (only if Section 3 fails for a given instance)

Carried forward, not re-derived, from the 2026-08-03/2026-08-04 drills (both disk-verified again this
session, see Section 8) — do not build this unless Section 3's fair test HARD-FAILs or MIDDLE-BANDs
against decodability for the relevant instance(s):

- **Reusable code**: `train_sr_transport`/`reach_value`/`reach_control_targetcos` in
  `experiments/exp_pfc_gate_cfrpe_trained_v2.py` — a TD(0) delta-rule learning `M[n,n]` over
  `(cur, nxt)` transitions, with `reach_value(cand@M, goal) = cos(cand@M, goal)` and a certified
  anti-tautology guard (`reach_tcos_corr=-0.079` on the forward direction). No backward/predecessor
  variant exists on disk; the literature scan in Section 2 confirms this is not a free transpose in
  neuroscience either — a `M_backward` must be trained fresh on reversed transitions.
- **Gap 1 (unchanged, still open)**: no training-data pipeline for `M_backward` exists. The lit-scan
  this session adds one new, genuinely useful fact: Chambers & Jurafsky (2008)-style narrative
  event-chain induction over real text (verb-argument co-occurrence keyed on shared protagonists) is
  an established, real-text-native way to build the exploration graph Gap 1 needs — a firmer citation
  than the 2026-08-03 drill had for "mined-distractor co-occurrence edges are a reasonable
  exploration graph," but still not built.
- **Gap 2 (causal construction, unchanged, still open)**: no organ generates competing causal
  candidates; `CausalLinkRegister` only stores an already-chosen link. This gap is independent of the
  fair-decodability question and must be solved regardless of Section 3's outcome for causal to work
  at all.
- **Settling vs trained-SR, adjudicated by this session's lit-scan**: the literature favors iterative
  CA3-style settling as more brain-faithful (Section 2), but no comparison exists in the literature of
  single-pass-trained-scoring vs settling specifically for this task, and settling is unbuilt on this
  codebase (confirmed by search, no relaxation loop anywhere). **Recommendation: ship the cheaper
  one-shot `reach_value` (or, if Section 3 passes, one-shot `decode_coherence_margins`) organ first;
  treat iterative settling as the brain-fidelity upgrade path if/when a harder eval shows the one-shot
  signal under-performing** — consistent with the 2026-08-04 build spec's own adjudication, now with
  literature backing rather than just an engineering-cost argument.

This section is intentionally NOT expanded further in this note — expanding it would violate the
redirect's explicit instruction to lead with, not presume past, the fairness question. See the
2026-08-04 build spec and 2026-08-03 causal-coherence drill for the full spec if Section 3 triggers
this path.

---

## 6. First buildable step (revised order)

1. **Fair-test harness (Section 3), coref-only load-matched subset first** — cheapest possible probe
   of the load-redistribution hypothesis: select/construct a small (n>=4) subset of already-known
   coref recency-trap items with matched downstream mention-count between candidates, re-run through
   the EXISTING `route_passage` unmodified. This alone answers "is coref's 1.0 also a load artifact"
   without touching goal-outcome at all — cheapest, most information-dense first move.
2. **Goal-outcome downstream-embedded real-passage items (Section 3b/3c)** — the genuine new
   construction work; needs real McGuffey passages with goal/blocked-goal content, which may not
   exist at N>=10 in the current corpus (flag as a possible data-availability finding, not assumed
   available).
3. **Only if 1-2 HARD-FAIL**: Gap 1's exploration-graph + reversed-TD training pipeline for
   `M_backward` (Section 5), now with the Chambers-Jurafsky citation to ground the exploration-graph
   construction choice.
4. **Causal instance**: regardless of 1-2's outcome, Gap 2 (candidate-generation/construction stage)
   remains a separate, unaddressed prerequisite — causal cannot be fairly tested via Section 3's
   design until something generates competing causal candidates in the first place.

---

## 7. Falsifiable predictions (HARD-PASS / HARD-FAIL, consolidated)

**HARD-PASS (fair test, primary):** load-matched coref subset adopt-rate > abstain_band (0.02) AND
downstream-embedded goal-outcome adopt-rate > abstain_band AND both shuffled controls collapse
toward 0 AND the original 18-passage coref positive control still reproduces net_auto=1.0.

**HARD-FAIL (fair test, primary):** load-matched coref subset collapses to ~0 (i.e., the ORIGINAL
coref win was itself a load-redistribution artifact) — this is the single most consequential possible
outcome of this drill, since it would revise a previously-"confirmed" reuse claim (build-spec note
Section 1b), not just fail to extend it.

**HARD-PASS (conditional backward-reach, only if triggered):** unchanged from the 2026-08-03 drill —
organ correct on >=3/4 real causal items, `reach_control_targetcos` correct on <=1/4 (anti-tautology
holds), positive margin on every correct item.

**HARD-FAIL (conditional backward-reach, only if triggered):** unchanged — organ correct <=1/4, or
anti-tautology control also passes >=3/4 (cosine-in-disguise).

---

## 8. Cross-thread synthesis

Builds on, corrects the presumption of, and does not re-derive the mechanism content of:
`notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md` (organ reuse map,
SELECT-unifies/SCORE-is-instance-specific finding — this drill's Section 4 sharpens that finding by
showing the "instance-specific" conclusion was itself drawn from a confounded comparison for the
goal-outcome instance specifically, not for causal) and
`notes/research_drill_biology_led_causal_coherence_credit_assignment_2026-08-03.md` (Gap 1/2/3,
`CausalLinkRegister` storage-not-selector finding, carried forward unchanged — that finding is
architectural, not a confound, and is unaffected by this drill's redirect). New disk-reads this
session: `experiments/exp_coherence_aggregate_discriminates_goal_outcome_v1.py` (full config +
`_go_asym_items`/`_go_matched_items`/`_shuffle_role_seq` construction, confirming the confound and
the load-artifact sub-arm design already exists and already flags `load_artifact_ruled_out=false`),
`hdlab/self_improving_loop.py` (`decode_coherence_margins`/`route_passage`/`decide_keep_or_revert`
read in full, confirming the load-binds-to-register mechanism), `hdlab/situation_model_accumulate.py`
(grepped, confirming no `GOAL` role exists there — the goal-outcome register was never integrated
into the shared situation model).

## Substrate-product implications

If Section 3 HARD-FAILs on the coref load-matched subset, this is a product-relevant finding beyond
this specific gap: it would mean the substrate's one currently-"validated" coherence-selection
capability (coref, atom 29609 lineage, already promoted) needs an integrity re-audit before further
product claims lean on it — "why did the system pick this antecedent" would currently answer
"because it redistributed register load favorably," which is not the same auditable, semantically-
grounded explanation the product roadmap implicitly promises. Conversely, a clean HARD-PASS is a
strictly better product outcome than the original brief's ask: it would mean ONE already-built, cheap,
already-partially-promoted organ covers coref AND goal-outcome without any new training pipeline,
directly reducing the integration cost flagged as a real cost in the build spec's own "Substrate-
product implications" section.

## Citations (verified count: 8 sources newly surfaced this session via 2 parallel Sonnet lit-scans,
generic-term queries only per query-privacy discipline; carried-forward biology citations from the
2026-08-03 drill not re-verified here). New this session: Foster & Wilson 2006 (reverse replay);
Ambrose, Pfeiffer & Foster 2016, Neuron (reward-scaled reverse replay); Mattar & Daw 2018 (need x gain
prioritized replay); Dayan 1993 and Stachenfeld, Botvinick & Gershman 2017, Nature Neuroscience
(forward SR formalization, confirming no established backward/predecessor transpose result);
Kintsch 1988/1998 (Construction-Integration, two-stage account); van den Broek et al. 1999 (Landscape
model) and Trabasso & van den Broek 1985 (causal network, carried forward, now with the
per-cycle-activation mechanism detail added); Chambers & Jurafsky 2008, ACL (narrative event-chain
induction from real text, new citation strengthening Gap 1's exploration-graph construction option).
Disk sources read this session (paths above): 3 experiment/hdlab files read in full or in relevant
part, 3 metrics.json files read in full, 2 prior research notes read in full.

## Confidence and biggest risk

**P_deflated = 0.35** for the fair-test design being the correct next move (novel-synthesis cap,
consistent with the two prior drills this builds on) — deflated specifically because the fair test's
own outcome is genuinely unknown in either direction (could resolve favorably, cheaply, with no new
organ; could instead surface a bigger problem, the load-artifact-in-coref finding, than either
starting hypothesis anticipated). **Biggest risk, stated plainly**: if the HARD-FAIL band in Section 7
fires (load-matched coref ALSO collapses), the honest read is that `decode_coherence_margins` has
never actually demonstrated relation-kind-independent coherence-tracking on ANY instance including
the one treated as "confirmed reuse" — this would be a bigger and more consequential finding than
either of the two negatives that motivated this drill, and should be treated as the priority
escalation if the fair-test cell is ever run, not folded quietly into a routine MIDDLE-BAND read.
