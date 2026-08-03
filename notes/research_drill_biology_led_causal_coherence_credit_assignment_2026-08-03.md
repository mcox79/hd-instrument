# Research drill (2x/operational-depth): causal-COHERENCE credit assignment — the SELECTION signal that beats recency
### 2026-08-03, Director (research role)

Design-only. No cell authored/dispatched. Target: the piece flagged SYNTHESIS P~0.45 in
`notes/research_drill_biology_led_learning_mechanism_earned_grounding_simulation_appraisal_action_causal_credit_2026-08-03.md`
Part B (same-day note, KB-checked, NOT re-derived) — this drill is a level-2 operational drill on
that note's Part B: it disk-verifies every claimed reuse organ line-by-line, finds one load-bearing
correction, and turns the spec into a concrete can-fail cell design against the real 4-item gold
eval. Per 2x discipline this is depth, not a repeat lit-scan.

---

## HEADLINE

Disk-reading the three claimed reuse organs turns up **one real correction and one confirmed
reuse**: `CausalLinkRegister`'s 0.9722 is **pure GIVEN-link retrieval-under-capacity-load**
(697-event vocabulary, write-then-read fidelity) — it is a **storage/query organ, not a selector**,
and cannot discriminate a true causal antecedent from a plausible distractor because both would
decode perfectly once *either* is written as the link. The actual coherence-selection signal has to
come from somewhere that scores candidates **before** any link is written — that is
`train_sr_transport`'s TD(0) delta-rule (Foster-Wilson reverse-replay / Mattar-Daw need-x-gain
biology), but re-pointed to the **predecessor** direction requires **retraining a new M_backward
via the same code path on reversed transitions** — it is NOT a free transpose of the certified
forward M (M is not symmetric; nothing in `exp_pfc_gate_cfrpe_trained_v2.py` learns a backward
map). `self_improving_loop.route_passage`/`decide_keep_or_revert` IS a genuine coherence-gated
candidate-selection **pattern** (abstain-band adoption of whichever candidate raises decode
confidence) but its literal `decode_coherence_margins` function is hard-wired to
`AccumulateRegister` entity-role decode, not causal reach — reusable as **architecture** (the
abstain-band gate), not as a drop-in function call.

**Net:** two of three organs need genuine new training/wiring, not a re-point; only the
control-flow SHAPE and the storage tail are free. P deflated further from Part B's 0.45 to
**0.35** for this drill's specific selector claim (SR-backward reach as the discriminator),
reflecting: (a) no backward-direction training data pipeline exists yet (named gap below), (b) the
anti-tautology guard must be re-earned for backward reach, unverified.

---

## 1. Disk-verified reuse map (per organ, corrected)

### 1a. `hdlab/situation_model_accumulate.py::AccumulateRegister` / `make_situation_register` — CONFIRMED reuse, as buffer only
Read in full. FHRR `bind(role_vec, idx_vec)` accumulated via `bundle` per entity; validated
accumulate-vs-overwrite organ (atom 29609, accumulate=1.0000 vs overwrite=0.4600 vs floor=0.2100).
`make_situation_register(backend="multibank")` is the wired default
(`MultiBankAccumulateRegister`, n_banks=8, decode >=0.999 at n_events=256/entity vs flat's 0.6547).
**Confirmed**: this is exactly the entity/event accumulate buffer Part B claimed — reusable
verbatim as the register holding the narrative's event sequence to iterate/replay over. No
correction needed here.

### 1b. `hdlab/situation_model_accumulate.py::CausalLinkRegister` — CORRECTED: storage, not selector
Read in full. `CausalLinkRegister` extends `AccumulateRegister` with `role_vocab=[CAUSE, EFFECT]`.
`add_causal_link(cause_idx, effect_idx)` **writes both directions given already-known indices** —
there is no scoring, ranking, or competition anywhere in the class; `query_cause_of` /
`query_effect_of` unbind-then-cleanup-argmax over the fixed `idx_vecs` vocabulary and return
`(None, {})` honestly if the role was never bound.

Disk-verified the 0.9722 result itself (`data/exp_causal_link_comprehension_fuller_v3_cleaned/
metrics.json`, HARD_PASS): 25 GOLD (cause, effect) pairs, written into a register spanning
**697 event slots** (46 real gold events + 651 mined raw-text distractor events used purely as
capacity-load fillers, not as competing causal candidates), then queried back —
`organ_accuracy_integration=0.9722`, `most_recent_accuracy_integration=0.0000` (a
text-position-nearest baseline collapses because true links span up to 4170 lines,
`supporting_event_line_distance_distribution.max=4170`). **This is a write-then-read capacity/
fidelity test, structurally identical to the AccumulateRegister capacity cert it inherits from —
it is never asked to choose between two SEMANTICALLY PLAUSIBLE candidate causes for the same
effect.** If you wrote `add_causal_link(distractor_idx, effect_idx)` instead of the true cause,
decode would return the distractor with the same ~0.97 fidelity — the register has no opinion on
which link is correct, only on whether a written link survives bundling load.

**Correction to Part B**: `CausalLinkRegister` is confirmed reusable **only as the persistence
tail** (write the SELECTED link once chosen, for later query) — not as any part of the
selection/coherence-scoring step. This is the single load-bearing finding of this drill: the
0.9722 number does not transfer to "solves credit assignment," and treating it as if it does was
Part B's overclaim.

### 1c. `experiments/exp_pfc_gate_cfrpe_trained_v2.py::train_sr_transport` / `reach_value` — CONFIRMED as the right discriminator, CORRECTED on "for-free" transpose
Read in full (`train_sr_transport`, `reach_value`, `reach_control_targetcos`,
`collect_rollout_transitions`). `M[n,n]` is learned by TD(0) delta-rule:
`E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M)` over `(cur, nxt)` transitions collected by random-walk
exploration of a forward operator-adjacency graph. `reach_value(cand_E, goal_E, M) =
cos(cand_E@M, goal_E)` is explicitly **directional** (forward reachability from candidate to
goal); `reach_control_targetcos` (M:=identity) is the certified anti-tautology guard proving the
HARD_PASS win (`reach_tcos_corr=-0.079`) is dynamics-carried, not raw-cosine-in-disguise.

**There is no backward/predecessor variant anywhere in this file.** `M` is not claimed or shown to
be symmetric (a general TD-learned linear map over a directed transition graph has no reason to
be), so **`M^T` is not a valid predecessor operator without independent verification** — using it
without retraining would be an unverified assumption, not a re-point. The mathematically clean
reuse is: **call `train_sr_transport` again, same function, same delta-rule, on REVERSED
transitions** (`(effect_idx, cause_idx)` pairs fed as `(cur, nxt)`) to learn a genuinely new
`M_backward`. This is a correct, cheap reuse of the LEARNING RULE and CODE PATH (same TD(0)
delta-rule, same anti-tautology control available for free by calling
`reach_control_targetcos` again) — but it is a **new learned object**, not a transpose trick, and
it needs its own training DATA (named as Gap 1 below).

### 1d. `hdlab/self_improving_loop.py::route_passage` / `decide_keep_or_revert` — CONFIRMED as architecture, CORRECTED on literal reuse
Read in full. `decode_coherence_margins` builds a fresh `AccumulateRegister`/`MultiBankAccumulateRegister`
from `(role, cid, event_slot)` triples and returns, per position, the top1-vs-runner-up
**role-decode margin**. `route_passage` computes this margin for a baseline resolution and each
candidate resolution, takes the **mean margin DELTA over positions the candidate actually changed
and flagged**, and `decide_keep_or_revert` adopts the best candidate only if its aggregate delta
**strictly clears an abstain band (default 0.02) above zero** — otherwise keeps baseline. Validated
on coreference cluster candidates only (dense McGuffey content: recovers ~67% of oracle gain,
100% rejection of a confirmed-negative "decay-window" trap lever, per the module's own docstring
scope note); explicitly flagged CONTENT-DENSITY-GATED (ties on sparser content).

**This is architecturally exactly the right shape for the causal-selection problem**: an
abstain-gated adopt-best-candidate-if-it-clears-a-margin-band rule, using a gold-free internal
signal, is precisely "coherence beats a floor, or abstain" — the Kintsch integration-stage pattern.
**Correction**: `decode_coherence_margins` itself is NOT swappable to causal reach without new
code — it is hard-wired to `AccumulateRegister.decode()`'s role-vocab margin, which is the wrong
quantity for scoring *which candidate event* is the cause (that margin measures how confidently
one entity's accumulated register resolves a role at a slot, not how plausible a candidate
antecedent is). **Reuse call: adopt the CONTROL-FLOW (`decide_keep_or_revert`'s abstain-band gate)
over a NEW margin quantity — the SR_backward `reach_value` delta between the leading candidate and
the runner-up — rather than reusing `decode_coherence_margins` itself.** This is architecture
reuse (the gate), not a drop-in function call, and should be named as such rather than folded into
"REUSE X" without distinction.

### 1e. Explicit non-reuse (confirmed, unchanged from Part B)
`hdlab/coreference_resolver.py::_pick_strict_cb` (read, lines 227-236): `argmax(most_recent_subject_clause)`
tie-broken by `last_pos` — literally a recency operator, confirmed by source, not just by the
falsification. **Do not reuse for causal selection**; this is the mechanism that already failed
0/4 on the recency-trap items per tonight's WHERE banner (commit e34d54701) — cited, not re-derived.

---

## 2. Discriminating claim, sharpened

Part B's biology (Foster & Wilson 2006 reverse replay; Ambrose-Pfeiffer-Foster 2016 reward-scaled;
Mattar & Daw 2018 need x gain, explicitly NOT recency; Trabasso & van den Broek 1985
causal-network coherence; Kintsch construction-integration) is carried forward unchanged — it was
verified in that same-day note and this drill's disk-reading does not contradict it, only the
IMPLEMENTATION-layer reuse claims. The sharpened computational claim, now grounded in what the
code actually does:

**The discriminator is a LEARNED SCALAR (SR_backward reach-cosine), not a MEMORY LOOKUP.**
Credit assignment requires scoring K candidate antecedents by "how much does a TD-trained backward
map say this candidate causally leads to the outcome" — a quantity that must be computed BEFORE any
write to a link register, from a map trained on many OTHER (cause, effect) pairs across the corpus
(so it generalizes/generalizes-plausibility rather than reproducing what's written). This is the
Mattar-Daw "need x gain" prioritization made concrete: `reach_value` IS a value/utility-shaped
score over the transition structure, not a proximity score — exactly what should NOT tie on the
recency-trap items the way `_pick_strict_cb` did.

---

## 3. Named gaps (honest, not glossed over)

**Gap 1 — no training data pipeline for M_backward.** `train_sr_transport` needs many `(cur, nxt)`
transitions (`exp_pfc_gate_cfrpe_trained_v2` uses `collect_rollout_transitions`, a random walk over
an abstract operator-adjacency graph with hundreds of steps). For the real narrative domain, the
only existing GIVEN-link corpus is the 25 pairs behind the `CausalLinkRegister` 0.9722 cert
(`gold_anne_comprehension_v3.jsonl`) — sparse for TD training as literal (effect, cause) pairs
alone. The buildable fix (not yet built): use the 651 mined distractor events already extracted for
that cert as an EXPLORATION graph (co-occurrence / narrative-adjacency edges over all 697 event
slots), random-walk over it exactly as `collect_rollout_transitions` does, and use the 25 GOLD
links as the reward/consistency anchors, not the sole transition set. This is a real design task,
not a re-point — name it explicitly rather than assume the existing 25 pairs are "enough data,"
which they are not for TD bootstrap convergence at this codebase's usual `steps`/`batch` scale
(`exp_pfc_gate_cfrpe_trained_v2` trains on far more rollout transitions than 25).

**Gap 2 — candidate generation (Kintsch "construction") is not addressed by any organ read here.**
Every organ above SCORES or STORES a candidate; none GENERATES the candidate set. For the pilot
cell (below) this is sidestepped because the 4 gold items already supply exactly 2 named
candidates each (true blocker + distractor) — but a general-purpose credit-assignment mechanism
needs a construction stage (e.g., "every agent-performed action-event within N clauses of the
goal-owner, referencing the same goal-object") that does not exist yet. Flag for a follow-up
design, not solved here.

**Gap 3 — the anti-tautology guard for the backward direction is unverified.** The forward organ's
`reach_tcos_corr=-0.079` (independent of raw cosine) does not transfer automatically; `reach_control_
targetcos` must be re-run against `M_backward` and must show the analogous near-zero-or-negative
correlation before the backward reach score can be trusted as dynamics-carried rather than a
relabelled cosine/adjacency cue.

---

## 4. Can-fail cell DESIGN (design only — not authored/dispatched)

**Data**: the 4 real, director-spot-verified `multi_candidate_causal_attribution` items in
`data/eval_gold_mention_role_mcguffey_v1/gold_grounded_appraisal_richer_v1.jsonl`
(`grapp_mcca_001/003/004/005`) — each supplies `true_blocker_agent`, `true_blocker_span`,
`distractor_agent`, `distractor_span`, `query_span`, and a `recency_baseline_prediction` that is
WRONG on all 4 by construction (that is the recency-trap structure this cell needs).

**One variable**: the SELECTOR used to pick between `true_blocker_span`'s event and
`distractor_span`'s event as "what explains the query outcome." Everything else (event encoding,
FHRR dim, seed) held fixed across arms.

**Real baselines (must all be present, per fair-test discipline)**:
1. **Recency** — `argmax(line_position)` over the two candidate spans (reproduces
   `recency_baseline_prediction`; pre-registered to score 0/4, since the gold file already states
   this).
2. **Random** — uniform coin-flip over {true, distractor}, seeded; expected ~2/4, reported with a
   binomial-p against n=4 (acknowledged: n=4 gives essentially no power to reject random at
   standard alpha — see honest caveat below).
3. **The falsified selector** — `hdlab.coreference_resolver._pick_strict_cb` structurally applied
   to a synthetic candidate stream built from each item's two spans' clause order (same
   recency-under-a-different-name mechanism that scored 0/4 tonight per the WHERE banner; included
   here to show the NEW selector must beat, not just resemble, what already failed).
4. **The organ under test** — `reach_value(candidate_action_E @ M_backward, query_outcome_E)` for
   each of the two candidate action-events, computed from an `M_backward` trained per Gap 1's
   pipeline; pick `argmax`.

**Pre-registered PASS/FAIL bands**:
- **HARD-PASS**: organ correct on >=3/4 items (recency 0/4, random ~2/4 expected, falsified
  selector 0/4) AND `reach_control_targetcos` on the SAME candidate pairs (M_backward := identity)
  is correct on <=1/4 (i.e., the win is not raw-cosine-in-disguise — the backward anti-tautology
  guard from Gap 3, re-earned, not assumed) AND the per-item glass-box margin (below) is positive
  on every item the organ gets right.
- **MIDDLE-BAND / PARTIAL**: organ correct 2/4 (ties random, beats recency and the falsified
  selector) — read as "right mechanism-class, underpowered training data (Gap 1)," triggers
  Gap-1 pipeline investment before re-test, not a mechanism refutation.
- **HARD-FAIL**: organ correct <=1/4 (no better than the falsified recency selector) OR the
  anti-tautology control also passes at >=3/4 (win is cosine-in-disguise, not dynamics). A
  HARD-FAIL here would sharpen, not close, the direction: per Part B's own fidelity-gate framing,
  it would mean the CONTENT the backward map is trained over needs to be richer (event structure
  or exploration-graph density), not that coherence-over-recency credit assignment is impossible —
  the brain's own reverse-replay is reward/need-x-gain-SCALED, so a flat/near-floor result should
  first be diagnosed as a replay-lesion-shaped (undertrained M) signature per the standing
  flat-result discipline, before treating it as a ceiling.

**Glass-box witness**: per item, report the scalar margin
`reach_value(true_candidate_E @ M_backward, outcome_E) - reach_value(distractor_candidate_E @
M_backward, outcome_E)` — directly analogous to the sim cell's `Q(coherent)-Q(recent)=+1.146`
margin cited in the task brief. Require this margin to be strictly positive on every item counted
correct (not just argmax-correct by a hair) and log the full 4-item margin vector in the cell's
metrics.json for audit, exactly as `reach_tcos_corr` and `per_item_records` are logged in the
disk-verified cert cells above.

**Honest caveat on power**: n=4 is a smoke/pilot scale (consistent with this codebase's other
pilot cells, e.g. the CausalLinkRegister cert's own N_integration=18), not a statistically
powered eval — a binomial test at n=4 cannot reject random at conventional alpha even at 4/4
correct (p=0.0625, two-sided vs 0.5). Treat a HARD-PASS on this pilot as "mechanism-class
license to build the eval out to real n" (per the earlier drills' own eval-densification pattern:
the richer eval itself started as this kind of small hand-verified batch), not as a landed result.

---

## 5. Substrate-product implications

The corrected reuse map changes the BUILD ORDER, not the target: (1) Gap 1 (exploration-graph +
reversed-transition TD training for M_backward) is now the actual next artifact, cheaper than it
looked in Part B because `train_sr_transport`/`reach_value`/`reach_control_targetcos` are already
generic, dimension-agnostic functions requiring only new `(cur, nxt)` index pairs and an event
embedding table — no new learning RULE, only new DATA plumbing. (2) `CausalLinkRegister` still
ships as the persistence layer once a link is selected (product-visible: "why did the system
attribute blame to X" queries against a durable, glass-box, 0.9722-fidelity store), it is just not
on the critical path for getting the attribution right in the first place. (3)
`self_improving_loop`'s abstain-band pattern generalizes cleanly as a reusable "adopt only if it
clears a coherence-margin floor, else abstain" primitive across BOTH coreference and causal
domains — this is a genuinely reusable substrate primitive worth naming in the capability registry
once the causal-margin version lands, distinct from the coref-specific `decode_coherence_margins`
implementation.

---

## Cross-thread synthesis

Builds on, cites (does not re-derive): Part B of
`research_drill_biology_led_learning_mechanism_earned_grounding_simulation_appraisal_action_causal_credit_2026-08-03.md`
(biology + first-pass reuse map), the SR/TD drill
`research_drill_biology_led_predictive_learning_mechanism_successor_representation_2026-08-03.md`
(Dayan 1993, Stachenfeld 2017, general SR framing), and the WHERE-banner falsification of
`_pick_strict_cb` as a causal selector (commit e34d54701). This drill's contribution is disk-level:
it separated "confirmed reusable" from "claimed reusable," found `CausalLinkRegister` is a storage
organ misread as a selector, and turned the abstract spec into a concrete 4-item can-fail design
with pre-registered bands.

## Citations (verified count: carried forward from Part B, 13 sources, not re-verified this
session — Schultz 1997, Montague-Dayan-Sejnowski 1996, O'Doherty 2004, Holroyd & Coles 2002,
Shenhav 2013, Frank & O'Reilly 2004/2006, Rangel 2008, Balleine & Killcross 2006, Foster & Wilson
2006, Ambrose-Pfeiffer-Foster 2016, Mattar & Daw 2018, Dayan 1993, Stachenfeld 2017, Trabasso &
van den Broek 1985, Kintsch 1988/1998, Baker-Saxe-Tenenbaum 2009/2017, van Kesteren 2012). This
drill's own verified count: 0 new external citations (disk-only verification pass); 6 source files
read in full (`hdlab/situation_model_accumulate.py`, `hdlab/self_improving_loop.py`,
`experiments/exp_pfc_gate_cfrpe_trained_v2.py` [selected functions], `hdlab/coreference_resolver.py`
[selected functions], `data/exp_causal_link_comprehension_fuller_v3_cleaned/metrics.json`,
`data/eval_gold_mention_role_mcguffey_v1/gold_grounded_appraisal_richer_v1.jsonl`).

## Confidence / biggest risk

**P_deflated = 0.35** (novel-synthesis cap per calibration discipline, further deflated from Part
B's 0.45 given the two corrections above). **Biggest risk**: Gap 1 (training-data pipeline for
M_backward) is the actual bottleneck, not the learning rule or the selection architecture — if the
25-pair GIVEN-link corpus plus mined-distractor exploration graph turns out too sparse/noisy for
TD(0) to converge to a non-degenerate M_backward, the pilot can-fail cell will HARD-FAIL for a
data-volume reason indistinguishable at n=4 from a mechanism-class refutation; the design above
tries to pre-empt this by requiring the MIDDLE-BAND read ("underpowered training, not refuted") be
checked before any HARD-FAIL is treated as closing the direction.
