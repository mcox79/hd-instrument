# Build spec: ONE coherence-based relational binding/selector organ (design drill, no cell authored)
### 2026-08-04, Director (research role)

Design-only per task brief. All prior-art numbers below are disk-verified (file paths + fields
cited), not asserted from memory. KB-checked: field advisor run (irrelevant here — it indexes the
substrate-physics track, not the comprehension/coherence-selector track; this drill instead
disk-read the actual experiment/hdlab files, which is the correct KB for this question).

---

## HEADLINE

**The SELECT operation (abstain-gated argmax-of-coherence-delta) already exists as ONE reusable
organ (`hdlab/self_improving_loop.py::decide_keep_or_revert`) and genuinely unifies all 3
instances. The COHERENCE-SCORE computation does NOT unify — it must be instance-specific**:
an accumulate-register decode-margin (`decode_coherence_margins`, already built) correctly serves
coref and (with new role-vocab wiring, no new hdlab code) goal-outcome, but is proven the WRONG
quantity for causal antecedent selection (`CausalLinkRegister` write-then-read is symmetric — it
decodes a wrong link with the same ~0.97 fidelity as a right one, so an accumulate-margin cannot
discriminate candidates; disk-verified in `notes/research_drill_biology_led_causal_coherence_
credit_assignment_2026-08-03.md`). Causal needs a genuinely different, not-yet-trained scalar:
`reach_value` from a TD-trained **backward** successor map (`M_backward`), which has code
(`train_sr_transport`/`reach_value`/`reach_control_targetcos` in
`experiments/exp_pfc_gate_cfrpe_trained_v2.py`) but no training data pipeline yet (named Gap 1,
2026-08-03, still open — verified not built by this drill's search for `M_backward`/`sr_backward`).
Net: **one organ (SELECT) reused whole across 3 instances; one organ (accumulate-margin SCORE)
reused across 2 of 3; one scalar (SR-backward reach) still needs its first training run for the
3rd.** This is an honest 2/3-built, 1/3-designed-not-built spec, not a fully landed capability.

---

## 1. The COHERENCE SCORE: adjudication among the 3 candidate signals

**(a) `predictive_coding` residual (rejected for now).** Read `hdlab/predictive_coding.py` in
full: `residual = observed - predicted` over **bipolar {-1,+1} HRR** vectors, gating a Hebbian
`W += value (x) key` write. Two problems: (i) representation-basis mismatch — every organ used
elsewhere in this spec (`AccumulateRegister`, coreference, situation-model) is **FHRR
complex64**, not bipolar HRR; using this residual would require a translation layer that does not
exist. (ii) direction mismatch — it scores "was this outcome predicted from a stored association,"
a *forward* prediction-error, not "which of K prior candidates *explains* this outcome," a
*backward* attribution query. Not reusable without new representation-bridge work; parked as a
future unification target, not on the critical path.

**(b) Situation-model coherence via `AccumulateRegister` decode-margin — CONFIRMED for 2/3
instances, DISPROVEN for the 3rd.** `hdlab/self_improving_loop.py::decode_coherence_margins`
(promoted 2026-08-02 from `exp_coref_autonomous_fix_router_v1`, atom 29609 lineage) already does
exactly this: bind a candidate assignment into a fresh `AccumulateRegister`/
`MultiBankAccumulateRegister`, decode each position's own (entity, event-slot), and return the
top1-vs-runner-up role-decode margin. This is a genuine Kintsch-style "does integrating this
binding produce a more internally self-consistent representation" signal — validated (per the
module's own scope note) on dense McGuffey content: recovers ~67% of oracle gain, 100% rejection
of a confirmed-bad "decay-window" trap lever, using ONLY its own gold-free margin. It is explicitly
flagged content-density-gated (ties on sparse content).

For **causal** candidate scoring this signal is proven the wrong quantity, not merely untested:
the 2026-08-03 drill disk-read `CausalLinkRegister.add_causal_link` and found it writes
`(cause_idx, effect_idx)` **given already-known indices**, with no scoring/ranking/competition
anywhere in the class. The certified 0.9722 result
(`data/exp_causal_link_comprehension_fuller_v3_cleaned/metrics.json`) is a write-then-read
capacity/fidelity test over 697 event slots — if the distractor had been written as the link
instead of the true cause, decode would return the distractor at the same ~0.97 fidelity. An
accumulate-register margin computed over "bind candidate X as the effect's cause" cannot
distinguish plausible-wrong from true, because both bindings are stored with equal fidelity; the
margin only measures storage-load, not candidate plausibility. **This is included as a built-in
negative-control arm in the unified test below** (run `decode_coherence_margins`-style scoring
on the causal instance anyway, predict it ties recency/random) — an honest way to empirically
confirm rather than merely assert the mechanism boundary.

**(c) Kintsch-style iterative constraint-satisfaction settling — not built, not attempted now.**
Searched the tree for an iterative spreading-activation / relaxation loop; none exists.
`route_passage`'s one-shot "compute margin under each candidate, pick best, gate by abstain-band"
is a **discrete, single-pass approximation** of Kintsch construction-integration (construction =
candidate generation, upstream and unsolved per Gap 2 below; integration = the one-shot margin
comparison), not true iterative settling to a fixed point. Adjudication: ship the one-shot
approximation now (cheap, already built for 2 of 3 instances); iterative settling is a stretch
goal, not blocking.

**Decision:** the coherence score is **instance-specific**, not one formula:
- coref, goal-outcome: `decode_coherence_margins` (accumulate-register decode-margin) — reuse
  verbatim / near-verbatim.
- causal: `reach_value(candidate_E @ M_backward, outcome_E)` — SR-backward reachability, needs
  `M_backward` trained (not built; Gap 1).
- predictive-coding residual and full Kintsch settling: explicitly out of scope for this spec.

---

## 2. The SELECT operation

`hdlab/self_improving_loop.py::decide_keep_or_revert(agg_deltas, abstain_band=0.02)` — pure,
data-agnostic: `argmax` over a `{candidate_name: score}` dict, adopted **iff** it strictly clears
`abstain_band` above zero, else `None` (abstain / keep baseline). This is reused **verbatim,
unmodified, across all 3 instances** — it is the one genuine cross-instance unification point in
this spec. Concretely: compute `delta = coherence_score(true_candidate) -
coherence_score(runner_up_candidate)` (or, for >2 candidates, `route_passage`'s per-candidate
delta-vs-baseline framing); call `decide_keep_or_revert({name: delta, ...})`.

**Anti-recency by construction, not by tuning:** the abstain-band gate and the underlying score
never read text position / clause order / `last_pos` at all — recency cannot enter the tie-break
because the function signature has no positional argument. This directly replaces
`hdlab/coreference_resolver.py::_pick_strict_cb` (disk-read, lines 227-236: literal
`argmax(most_recent_subject_clause)` tie-broken by `last_pos` — confirmed a recency operator by
source, not just by the 0/4 falsification cited in the task brief) for the coref instance's
tie-break path specifically. On ties / insufficient evidence the new selector returns **abstain**,
not a recency fallback — a deliberate behavior change from `_pick_strict_cb`'s current
recency-fallback design.

---

## 3. Per-component reuse map

| Piece | Organ | Status / build delta |
|---|---|---|
| Accumulate register substrate | `hdlab/situation_model_accumulate.py::AccumulateRegister` / `make_situation_register` | Reuse verbatim (atom 29609 validated: accumulate=1.0000 vs overwrite=0.4600 vs floor=0.2100) |
| Coref coherence score | `hdlab/self_improving_loop.py::decode_coherence_margins` | Reuse verbatim — already coref-native |
| Goal-outcome coherence score | same `decode_coherence_margins` | Reuse verbatim; genuine build = a harness that supplies goal/outcome `role_vocab` + candidate-owner `cluster_ids` in place of coref cluster ids (~1 new eval script, zero new `hdlab` code) |
| Causal coherence score | `experiments/exp_pfc_gate_cfrpe_trained_v2.py::train_sr_transport` / `reach_value` / `reach_control_targetcos` | Reuse the LEARNING RULE + anti-tautology-guard function verbatim; genuine build = Gap 1 (exploration-graph random-walk over the 697-slot event vocabulary + reversed-transition TD training to produce a NEW `M_backward` — **not built anywhere on disk**, confirmed by search) |
| SELECT / abstain gate | `hdlab/self_improving_loop.py::decide_keep_or_revert` | Reuse verbatim across all 3 instances — the actual unification point |
| Persistence of the chosen link | `hdlab/situation_model_accumulate.py::CausalLinkRegister` | Reuse verbatim, write-ONLY after selection (per the 2026-08-03 correction: never the selector itself) |
| Predictive-coding residual | `hdlab/predictive_coding.py` | NOT reused — representation-basis (bipolar HRR) and direction (forward-prediction, not backward-attribution) mismatch; future work |
| Kintsch iterative settling | none exists | NOT built; one-shot margin comparison + abstain-gate is the shipped approximation |
| Dispatcher (route instance-type to its score fn, then through the shared gate) | none exists | NEW, small (~50-100 lines): the one piece of genuinely new code that makes this "ONE organ" at the API level despite 2 different scoring backends |

---

## 4. Unified 3-instance test (pre-registered)

**Instance A — coref recency-trap.** Items: the recency-trap set that falsified `_pick_strict_cb`
0/4 (WHERE-banner, commit `e34d54701` — cited, not re-derived; this drill did not re-read that
specific commit's item list, flagged as a verify-before-cell-authoring step). Score:
`decode_coherence_margins` margin-delta between the baseline (recency) resolution and the
coherent-alternative resolution. Gate: `decide_keep_or_revert`.

**Instance B — causal multi-candidate.** Items: the 4 real, director-spot-verified items in
`data/eval_gold_mention_role_mcguffey_v1/gold_grounded_appraisal_richer_v1.jsonl`
(`grapp_mcca_001/003/004/005` — the "gold_grounded_causal_crossspan" family referenced in the task
brief; disk-verified this is the same 4-item set the 2026-08-03 drill pre-registered against, each
with `true_blocker_span`/`distractor_span`/`recency_baseline_prediction` wrong by construction).
Score: `reach_value(candidate_E @ M_backward, outcome_E)`, requires Gap 1 (not built). Includes the
negative-control arm from Section 1(b): the SAME 4 items scored by `decode_coherence_margins`
(accumulate-margin), predicted to tie recency/random per the write-then-read-is-symmetric argument
— this is a planned FAIL, included to empirically confirm the instance-specificity claim rather
than merely assert it.

**Instance C — goal-outcome discourse binding.** Items: `exp_situation_model_goal_outcome_
dimension_v1`'s eval where a recency-shaped binding baseline scored `recency_binding_accuracy=
0.3333` (disk-verified, `data/exp_situation_model_goal_outcome_dimension_v1/metrics.json`,
verdict `MIDDLE_BAND_FIRES_BUT_RECENCY_CONFOUND_ROUTES_BINDING_SELECTOR`). **Caveat, stated
honestly**: 0.3333 is not the clean 0.0/wrong-by-construction recency-trap the other two instances
have (coref = 0/4 by construction; causal = wrong-by-construction per gold file) — this instance's
existing item set is weaker evidence that recency is the specific failure mode, only that SOME
non-recency-informed binding scheme is needed. Recommend hardening this item set into an explicit
recency-trap (goal-owner is NOT the most-recently-mentioned entity, by construction) as a
prerequisite for Instance C, not just reusing the existing items as-is.

**Pre-registered bands (unified across all 3 instances):**
- **HARD-PASS:** selector beats recency on all 3 instances, non-overlapping (strictly above, not
  tied) AND each instance's own anti-tautology/anti-memorization control clears (coref:
  shuffled-structure ceiling per the v2/v3 pattern below; causal: `reach_control_targetcos` <=1/4
  correct, per the 2026-08-03 pre-reg; goal-outcome: a shuffled-owner control collapses to chance).
- **MIDDLE-BAND:** beats recency on 2/3 instances, OR beats on all 3 but one instance's control is
  inconclusive/underpowered (n=4 for causal has essentially no statistical power at any accuracy,
  per the 2026-08-03 drill's own honest caveat — a HARD-PASS read there is "mechanism-class
  license," not a landed statistical result). Read as right-mechanism-class/underpowered, not
  refutation — triggers the named gap's investment (e.g. Gap 1 data pipeline), not abandonment.
- **HARD-FAIL:** beats recency on <=1/3 instances, or any instance's control ALSO clears the bar
  (signal is a relabelled recency/positional cue in disguise, not real coherence).

**The mandatory anti-recency control** is already satisfied by construction for Instances A and B
(items are gold-labeled such that the recent candidate is never the correct one); Instance C needs
this property added (see caveat above) before it can honestly participate in the HARD-PASS band.

---

## 5. Honest what-transfers-from-v2/v3/v4 vs what's-new

Disk-verified prior numbers (correcting the task brief's loose recollection):

- `exp_coherence_selector_insim_v2` (`data/exp_coherence_selector_insim_v2/metrics.json`):
  **HARD_PASS** — `COHERENCE_REVERSE_REPLAY` on known types, novel-entity eval, acc=1.0000 vs
  recency=0.0000, random=0.5067, no-replay-local=0.4600; shuffled-structure control collapses to
  0.2700 (structural_lift=0.73) confirming the win is structural, not entity-memorized.
- `exp_coherence_selector_novel_types_v3` (`data/exp_coherence_selector_novel_types_v3/
  metrics.json`): **MIDDLE_BAND**, not the HARD_PASS the task brief implied — `acc=0.8733,
  min_lift=0.3667`, below the HARD-PASS accuracy floor; `shuffled_ok=True`
  (`structural_lift_minus_shuffled=0.6233`, so the anti-memorization control DOES pass) but the
  raw accuracy gate does not clear. Read as right-mechanism-class/underpowered on novel types, per
  the metrics file's own `verdict_msg`.
- `exp_coherence_selector_bidirectional_v4`: **HARD_FAIL_NO_MULTIHOP_LIFT** at 2-hop/3-hop — a
  genuine negative for multi-hop composition, not a "3-way pass" as loosely stated in the brief.
  Scope-relevant: this build spec targets **1-hop direct-candidate selection only** (2 candidates,
  the shape of all 3 target instances); multi-hop causal chains remain an open, separately-negative
  problem (also see `exp_multihop_reverse_replay_backward_sweep_v1`, MIDDLE_BAND, D_bidir best arm
  but below HARD-PASS).
- `exp_coherence_selector_insim_v1`: **HARD_FAIL** (does not beat floors), not simple
  "memorization" as the brief characterized it — `verdict_msg` reports it failed the coherence
  floor outright (0.2633 vs 0.75 threshold), a different failure mode than a memorization
  diagnosis.
- `exp_coherence_selector_text_transfer_v1`: **CANNOT_BRIDGE_REPRESENTATION_GAP** — the v2/v3
  sim-earned coherence rule is INTACT in-sim (0.8367) but ~chance on real text (0.4286, tiny n=7).
  Root cause per the metrics file: `M_backward` there learned the inverse of a fixed synthetic
  **coordinate-axis permutation**, and real text has no such T-orbit structure — the encoding, not
  the selection LOGIC, is what breaks.
- `exp_grounded_coherence_selector_v1`: **GROUNDED_PARTIAL_LEXICAL_PROXY** — sim FULL=1.000 clean,
  text (n=7, tiny) full=0.714 with `lift_carried_by_eff=true, valence_dim_transfers=false` —
  effort/effect-shaped features transfer to text better than valence-lexicon features. Weak
  evidence but directionally useful for feature choice on the goal-outcome instance (prefer
  structural/effort features over a valence lexicon when building Instance C's role vocab).

**What genuinely transfers to this spec:** the MECHANISM CLASS — "a TD-trained backward/reverse
signal beats recency and survives a shuffled-structure anti-memorization control" — is real and
structurally confirmed (v2, and v3's structural-lift-passes-even-though-accuracy-doesn't). **What
does NOT transfer:** the specific v1-v4 CODE, because it was built and validated entirely on a
synthetic in-sim permutation-orbit representation that `text_transfer_v1` proved has no path to
real narrative HD content. The causal instance's `M_backward` (via `train_sr_transport` on real
narrative event embeddings, per Gap 1) is a **different, real-text-native construction** that
inherits the validated mechanism-class claim without inheriting the broken sim-to-text bridge —
this is the load-bearing distinction this spec is built on, not a restatement of v2/v3's numbers.

---

## 6. First buildable step

Cheapest-to-falsify first, most-expensive last:

1. **Instance C (goal-outcome)** — zero new `hdlab` code, only a harness wiring
   `decode_coherence_margins` to the goal-outcome role vocab + candidate-owner cluster_ids. Fastest
   test of whether the shared margin-organ beats recency outside its native coref domain. Also:
   first harden the item set into a true recency-trap (see caveat, Section 4) before scoring it, or
   the result cannot honestly enter the HARD-PASS band.
2. **Instance A (coref)** — also zero new `hdlab` code (the organ is already coref-native); the
   work is locating/re-verifying the exact recency-trap item set behind the 0/4 falsification
   (commit `e34d54701`) and running `route_passage` against it directly.
3. **Instance B (causal)** — the real remaining build: Gap 1's exploration-graph + reversed-
   transition TD training pipeline for `M_backward`. Biggest lift (new data plumbing, new training
   run, re-earning the anti-tautology `reach_control_targetcos` guard for the backward direction
   per Gap 3), do last, and only after 1-2 confirm the SELECT-side architecture is sound so Gap 1's
   investment isn't wasted on a broken gate.

---

## 7. Confidence and biggest risk

**P_deflated = 0.35**, carried forward unchanged from the 2026-08-03 causal-coherence drill's own
calibration (same organs, same open Gap 1) — this spec adds the goal-outcome and coref
generalization claims on top, which are LOWER-risk (near-zero new code) but have not been run, so
they do not raise the number; capped per novel-synthesis-P<=0.50 discipline regardless.

**Biggest risk:** the unifying claim "one SELECT organ, instance-specific SCORE" could still be
wrong in the other direction — `decode_coherence_margins` might ALSO fail to discriminate on
Instance C the way it's proven to fail on causal, if goal/outcome role-binding turns out to be
symmetric write-then-read the same way `CausalLinkRegister` is (no one has checked whether binding
a wrong goal-owner into the register decodes with equal fidelity to binding the right one — this is
exactly the failure mode that sank the causal case and has NOT been ruled out for goal-outcome).
If Instance C also HARD-FAILs for the same structural reason, the honest read would be: the
accumulate-margin signal only works when the role vocabulary itself encodes competing, mutually
exclusive information at decode time (coref: two candidate entities cannot both "own" the same
pronoun slot) — a property that may not hold for goal/outcome binding the same way. This should be
the FIRST thing checked when Instance C is run (step 1 above), before treating a goal-outcome
HARD-FAIL as underpowered rather than structural.

---

## Cross-thread synthesis

Builds directly on and does not re-derive: `notes/research_drill_biology_led_causal_coherence_
credit_assignment_2026-08-03.md` (the disk-verified organ-by-organ correction this spec's causal
instance is entirely inherited from — CausalLinkRegister=storage-not-selector,
`decode_coherence_margins`=architecture-not-drop-in-quantity, Gap 1/2/3 named there and still open);
the coherence-selector v1-v4 + text-transfer + grounded arc (Section 5, disk-verified numbers,
correcting several loosely-stated figures from the task brief); `exp_situation_model_goal_outcome_
dimension_v1` (the goal-outcome recency-confound instance); `exp_cross_span_causal_binding_v1`
(`CROSS_SPAN_BINDING_LIFTS_RECALL_AND_SELECTION` — a DIFFERENT, already-landed piece of the causal
puzzle: it fixes candidate-**reachability** across spans via the accumulate register, but explicitly
reuses `bridge_causal_antecedent` UNCHANGED as "the existing unchanged bridge/selector" — i.e. it
solves binding-vs-selection's binding half, not the selection half this spec targets; the two are
complementary, not overlapping). The `research_coherence_over_recency_selection_biology_2026-08-04`
note the task brief expected to fold in was **not found on disk** (searched by filename) — either
not yet landed or filed under a different name; this spec proceeds without it and should be
reconciled if/when it lands.

## Substrate-product implications

A shipped version of this organ answers, glass-box and auditable: "why did the system attribute
this pronoun / this blame / this goal to entity X" via a durable, queryable trail (candidate
scores + the abstain-gate's margin, logged per decision) — not a black-box pick. The instance-
specific-score finding (Section 1) is itself product-relevant: it means the substrate cannot ship
ONE "coherence" API and expect it to silently work everywhere; each new relational-binding surface
needs its own coherence-quantity validated against its own write-then-read symmetry properties
before being trusted, which is a real, non-trivial integration cost the product roadmap should
carry explicitly rather than assume away.

## Citations (verified count: 0 new external citations — disk-only verification pass, no web
search per design-drill scope; biology citations underlying the causal mechanism carried forward
unchanged from the cited 2026-08-03 note, not re-verified this session). Source files read in full
or in relevant part this session: `hdlab/self_improving_loop.py`, `hdlab/situation_model_
accumulate.py`, `hdlab/coreference_resolver.py` (grep-located sections), `hdlab/predictive_coding.py`
(grep-located sections), `experiments/exp_cross_span_causal_binding_v1.py` (header),
`notes/research_drill_biology_led_causal_coherence_credit_assignment_2026-08-03.md` (in full);
metrics.json disk-read for `exp_coherence_selector_{insim_v1,insim_v2,novel_types_v3,
bidirectional_v4,text_transfer_v1}`, `exp_grounded_coherence_selector_v1`, `exp_situation_model_
goal_outcome_dimension_v1`, `exp_cross_span_causal_binding_v1`, `exp_multihop_reverse_replay_
backward_sweep_v1{,_self_contained}`.
