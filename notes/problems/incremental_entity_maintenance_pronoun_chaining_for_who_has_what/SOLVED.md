---
problem: incremental_entity_maintenance_pronoun_chaining_for_who_has_what
status: SOLVED
bar: "PASS = an incremental entity-maintenance mechanism (resolved pronouns chained into recurrently-maintained, accumulating entity-activation histories) that: (1) raises he/she who-has-what CI-separated toward the ~0.72 gold-grouping ceiling, over the realistic glass-box floor (~0.46, the landed graded pick over glass-box grouping -- recompute on the held-out population, gate on its UPPER bound), on HELD-OUT LitBank gold coref (doc-split; do not grade on the tuning split); (2) the lift is ATTRIBUTED to entity-maintenance, not the pick -- via the grouping decomposition (the gain must appear in the grouping term, with the pick held at its near-optimal setting); (3) a shuffled-chain twin LOSES CI-separated (same resolved mentions, wrong chaining order/assignment -> the maintained history, not the machinery, does the work); (4) reports the long-distance re-instatement effect (does pattern completion fix the ~2x-distance failure bucket the parent localised). Report CI half-width + null p95 on every margin. A rigorous located NEGATIVE is a FULL PASS if faithfully-built entity maintenance does not close toward the gold ceiling AND it names why (the chaining signal, the completion dynamics, or a genuine long-distance ambiguity floor) with the number."
result: "PRIMARY (LitBank coref-CoNLL, 25 gold-coref docs, he/she who-has-what pick accuracy on gold-nominal grouping, the pick HELD at hdlab.graded_coref_pick's near-optimal setting; scored anti-circularly = picked entity's gold cluster == target's gold cluster). Recurrent incremental entity-maintenance (chain each resolved he/she pronoun back into the PICKED entity's ACT-R activation history) raises who-has-what over the NO-chaining floor: HELD-OUT (12 test docs, n=977) coref-blind-to-chaining floor 0.4637 [0.4330,0.4954] -> CHAIN 0.5210 [0.4893,0.5527], PAIRED +0.0573 [0.0328,0.0809] (half-width 0.024, excludes 0). ALL 25 docs (n=1700): floor 0.4735 [0.4512,0.4982] -> CHAIN 0.5382 [0.5141,0.5612], PAIRED +0.0647 [0.0465,0.0841] (unpaired CI-separated too: chain lo 0.514 > floor hi 0.498). Fully-glass-box grouping (aliaser, no gold nominal grouping): ALL 0.4512 -> 0.5494 +0.0982 [0.0712,0.1689]; TEST 0.4432 -> 0.5107 +0.0676 CI-sep. The lift is a TARGETED long-distance re-instatement: bucketed by distance to the nearest prior NOMINAL, the entire gain is FAR-from-nominal -- FAR (nominal >=2 sentences back, n=717) 0.261 -> 0.471 toward the per-bucket gold ceiling 0.750 = 43%% of that bucket's gap recovered (long bucket, nominal >=3 back, n=492: 0.185 -> 0.423 toward gold 0.754); NEAR (nominal <=1 back, n=962) 0.642 -> 0.600 (-0.043, nochain already near its gold ceiling 0.703). Deterministic across PYTHONHASHSEED 0/1/42."
floor: "Strongest floor actually run = the NO-chaining arm = the identical graded pick (hdlab.graded_coref_pick, near-optimal by the MAP-optimality theorem) + landed keep_after_pool_cleanup + is_discourse_participant (phi-agreement), over the SAME gold-nominal-grouped entities, with pronouns NOT chained into histories: HELD-OUT 0.4637 [0.4330,0.4954] (gate on upper bound 0.4954; the paired chain-minus-floor delta +0.0573 excludes 0). Fully-glass-box floor (aliaser grouping) 0.4432. CEILING = gold pronoun-chaining (the parent's `gold`): gold_anchored 0.714 (ALL) / 0.732 (TEST), reproducing the parent's grouping decomposition (gold_anchored-nochain +0.241 ALL / +0.284 TEST ~ the parent's gold_nom->gold +0.260)."
controls: "(1) SHUFFLED-CHAIN TWIN (same resolved mentions, chain to a RANDOM gender-compatible entity; K=300 passes): mean 0.270, p95 0.283; CHAIN 0.538 >> p95 (the maintained IDENTITY does the work, not the chaining machinery/recency-shape). (2) SOFT vs HARD maintenance: SOFT (accrue each pronoun across candidates by the posterior, 'hold both') LOSES to HARD (commit to the argmax): soft-hard -0.0235 [-0.0312,-0.0165] ALL / -0.0358 [-0.0481,-0.0246] TEST, CI-sep -- distributed maintenance keeps distractors alive; the attractor must SETTLE (CA3/Hopfield). (3) ORACLE-gated chain (propagate ONLY correct picks) 0.629 isolates the residual: propagation-damage (chain->oracle) +0.091, missed-reinforcement (oracle->gold) +0.085 -- both are the pick's structural ceiling. (4) STRUCTURAL-DOMINATION: 29.4%% of chain errors are strictly structurally-dominated (gold reachable by NO recency/subject/freq cue), chain acc there 0.481 (n=445) vs 0.684 non-dominated (n=1025) -- the residual IS the missing coherence PRIOR (Kehler-Rohde), the coref-cap's ~19%% residual. (5) ENTROPY diagnostic: 99.5%% of wrong picks are low-entropy (confident) -> the confidence gate is a located NEGATIVE (flat 0.3->1.0), because the errors are confident structural mistakes, not gate-able uncertainty. (6) CHAINED-WEIGHT sweep (Wall D, OUR-INVENTION param): best on train w=0.25 but weighted-chain -0.010 NOT CI-sep held-out = located negative; default weight-1 retained. (7) PER-BUCKET GOLD ceiling (honest recovery framing). (8) local_graded_pick BIT-EQUAL to hdlab.graded_antecedent_pick at weight=1 (the pick is held fixed; only histories differ -> attribution is surgical). (9) NO-HARM per-doc: 11 improve / 8 flat / 6 regress of 25 (net +0.065; the 6 regressions are the near-nominal propagation cost). (10) GENERALIZATION: object-'it' chaining (same accrual, number not gender) reproduces the mechanism -- ALL +0.0226 [0.0028,0.0424] CI-sep, twin loses (0.234 vs p95 0.209), same long-distance signature (long +0.115); underpowered held-out. (11) PICK x MAINTENANCE coupling: the loop over the GRADED pick +0.0647 CI-sep, but over the INCUMBENT rigid hard-tier pick it HURTS -0.0253 [-0.0335,-0.0176] CI-sep -- the recurrence needs a pick that integrates accrued ACT-R activation; a rigid tier cannot consume the maintained history. (12) DECAY-d robustness: the gain is CI-sep across the brain-plausible range d=2(+0.036)/3(+0.065)/4(+0.055) but flips negative at d=1(-0.104) -- the lever exists BECAUSE memory decays (ACT-R d>0)."
files_changed: "experiments/exp_entity_maintenance_chaining_v1.py (the recurrent entity-maintenance mechanism + local_graded_pick bit-equal to hdlab + hard/soft/oracle/twin arms + confidence-gate + chained-weight sweep + per-bucket-gold long-distance + structural-domination + no-harm + pick-x-maintenance coupling + decay-d robustness); experiments/exp_entity_maintenance_object_chaining_v1.py (object-'it' generalization probe); verification/test_entity_maintenance_chaining.py (10/10 scaffold-free witness); data/exp_entity_maintenance_chaining_v1/metrics.json + data/exp_entity_maintenance_object_chaining_v1/metrics.json. NO hdlab/ written (Q111 -- the proposed wire is in FOR STRATEGY below)."
reverify: ".venv/Scripts/python.exe verification/test_entity_maintenance_chaining.py   # 12/12 FROM SOURCE -- local pick bit-equal to hdlab + accrual mechanism + reproduces grouping decomposition + chain-beats-nochain CI-sep + shuffled twin loses + long-distance re-instatement + soft-loses-to-hard + residual-is-pick-reliability + object generalization + pick-x-maintenance-coupling + decay-d-robustness"
---

# SOLVED. Recurrent entity-maintenance (pronoun-chaining over the near-optimal graded pick) lifts he/she who-has-what CI-separated, and the lift is a TARGETED long-distance re-instatement -- exactly the bucket the parent localised.

## Status in one line
Chaining each resolved he/she pronoun back into its entity's ACT-R activation history -- the brain's incremental
entity-maintenance loop -- raises who-has-what over the no-chaining floor CI-separated (held-out +0.057 [0.033,0.081];
glass-box +0.068), attributed SURGICALLY to maintenance (identical pick + identical candidate entities; only the
histories differ), with the shuffled-chain twin LOSING and the entire gain living in the LONG-DISTANCE-from-nominal
bucket (0.261 -> 0.471 toward a 0.750 gold ceiling = 43%% recovered). Every wall is drilled to a brain mechanism and a
number: the residual is the missing coherence PRIOR (not a chaining defect); SOFT maintenance loses to HARD (attractors
SETTLE, they do not hold a superposition); cold re-instatement needs episodic retrieval, a different system.

## THE OPENING MOVE -- how does the brain do this? (PINNED vs OUR-INVENTION)
Comprehension maintains INCREMENTAL discourse-entity representations in working memory, updated mention-by-mention
(Centering, Grosz-Joshi-Weinstein 1995; structure-building, Gernsbacher 1990). An entity's retrievability GROWS with
its accrued mentions (ACT-R base-level activation `A_i = ln(sum_k w_role*dt^-d)`; Anderson; Lewis & Vasishth 2005).
Re-instating an entity from a bare pronoun (a partial cue) is pattern COMPLETION -- a recurrent settling onto the
stored entity (CA3 hippocampal completion; Nakazawa 2002; the substrate's own `hdlab.ca3_completer` /
`iterative_attractor`). The chaining is RECURRENT: each resolved pronoun feeds the NEXT mention's salience -- a loop,
not a feed-forward pick, which is precisely why single-pick optimization plateaus (the parent proved the pick
near-optimal: graded TIES ACT-R by the MAP-optimality theorem).
- **PINNED-BY-EVIDENCE:** incremental entity maintenance + activation accrual + partial-cue re-instatement; and (the
  data corrected me, see KEY REALIZATION 1) that maintenance COMMITS to a settled attractor rather than holding a
  distribution.
- **OUR-INVENTION-UNDER-TEST (swept):** the confidence-gate `tau` and the chained-pronoun evidence weight -- both
  located NEGATIVES held-out (the default hard, commit-all, weight-1 chain is near-optimal).

## WHAT WAS BUILT
A RECURRENT WRAPPER around the PINNED, near-optimal graded pick (`hdlab.graded_coref_pick`, held FIXED --
`local_graded_pick` copies its formula verbatim and is self-tested BIT-EQUAL at weight=1). Process he/she pronouns in
reading order over the entity-activation histories; after each pick, CHAIN that pronoun's mention `(sent_idx, role)`
back into the PICKED entity's history, so later pronouns see the accrued recency + frequency. Glass-box, NO gold in the
chaining decision, NO LLM. **The reader ALREADY has this primitive** -- `event_centrality_coref.resolve_stream` with
`chain_pronouns=True` appends the resolved pronoun to `resolved_ent.mention_midxs` -- but wired to its WEAKER centrality
pick and surface-head grouping; this contribution runs the loop over the near-optimal graded pick with clean grouping.

**Attribution is surgical.** The floor (`nochain`) and the arm (`chain`) call the IDENTICAL `graded_antecedent_pick`
over the IDENTICAL candidate entities (gold-nominal grouping + the landed `keep_after_pool_cleanup` +
`is_discourse_participant` phi-agreement filter). The ONLY difference is whether resolved pronouns enter the histories.
So any lift is 100%% entity-maintenance, not the pick -- the grouping term of the parent's decomposition, by construction.

## WHAT WAS MEASURED

### 1. HEADLINE -- chaining lifts who-has-what CI-separated, held-out
| population | floor (no chaining) | CHAIN | paired delta |
|---|---|---|---|
| HELD-OUT (12 test docs, n=977) | 0.4637 [0.4330,0.4954] | 0.5210 [0.4893,0.5527] | **+0.0573 [0.0328,0.0809]** (hw 0.024) |
| ALL (25 docs, n=1700) | 0.4735 [0.4512,0.4982] | 0.5382 [0.5141,0.5612] | **+0.0647 [0.0465,0.0841]** (unpaired-sep too) |
| glass-box grouping (aliaser), ALL | 0.4512 | 0.5494 | **+0.0982 [0.0712,0.1689]** |
| glass-box grouping (aliaser), TEST | 0.4432 | 0.5107 | **+0.0676** CI-sep |

Ceiling (gold pronoun-chaining, the parent's `gold`): 0.714 (ALL) / 0.732 (TEST). Reproduces the parent's grouping
decomposition: `gold_anchored - nochain = +0.241` (ALL) / `+0.284` (TEST), matching the parent's `gold_nom -> gold` +0.260.

### 2. THE LIFT IS A TARGETED LONG-DISTANCE RE-INSTATEMENT (bar item 4, CONFIRMED with per-bucket gold ceilings)
Bucketed by distance to the nearest prior NOMINAL of the true entity -- the axis `nochain` actually sees, and the axis
of the parent's "wrong picks are ~2x the antecedent distance" finding:
| bucket (nominal distance) | n | nochain | chain | gold ceiling | recovered of bucket gap |
|---|---|---|---|---|---|
| **FAR (>=2 back)** | 717 | 0.261 | **0.471** | 0.750 | **43%%** |
| &nbsp;&nbsp;`long` (>=3 back) | 492 | 0.185 | 0.423 | 0.754 | ~38%% |
| &nbsp;&nbsp;`plus2` | 225 | 0.427 | 0.578 | 0.742 | ~48%% |
| NEAR (<=1 back) | 962 | 0.642 | 0.600 | 0.703 | -0.043 (already near gold) |

So chaining does EXACTLY what the brief's re-instatement hypothesis predicts -- it bridges the long-distance-from-nominal
gap with the intervening chained pronouns -- and it is (correctly) inert-to-slightly-costly where the nominal is right
there. The "27%% of the TOTAL gap" headline UNDERSTATES the mechanism: ~57%% of holders are near-from-nominal where
`nochain` already sits near its own ceiling; where the mechanism APPLIES it recovers 43%% of the gold gap.

### 3. CONTROLS
- **Shuffled-chain TWIN LOSES (bar item 3):** chain to a RANDOM gender-compatible entity (K=300 passes) -> mean 0.270,
  p95 0.283; CHAIN 0.538 >> p95. The maintained IDENTITY does the work, not the chaining machinery or the recency-shape.
- **SOFT maintenance LOSES to HARD:** accruing each pronoun across candidates by the posterior ("hold both") scores
  BELOW committing to the argmax: soft-hard -0.0235 [-0.0312,-0.0165] (ALL) / -0.0358 (TEST), CI-sep. (KEY REALIZATION 1.)
- **ORACLE-gated ceiling:** chaining ONLY correct picks -> 0.629; splits the residual into propagation-damage
  (chain->oracle +0.091) + missed-reinforcement (oracle->gold +0.085), both the pick's structural ceiling.
- **local pick BIT-EQUAL to hdlab** at weight=1 (300 random cases) -- the pick is genuinely held fixed.

### 4. GENERALIZATION -- object-'it' chaining (same accrual, number not gender)
The accrual is pronoun-class-agnostic. Running the identical mechanism on resolvable object pronouns (it/its/they/them,
number-compatible, recency-dominant per the parent's object finding): ALL nochain 0.212 -> chain 0.234, **+0.0226
[0.0028,0.0424] CI-sep**, twin LOSES (0.234 vs p95 0.209), and the SAME long-distance signature reproduces (`long`
+0.115, `plus2` +0.091). Held-out is underpowered (TEST flat -- objects are sparser and harder). So the mechanism is a
GENERAL working-memory operation, not a he/she trick; the object held-out effect is not established (small n).

### 5. PICK x MAINTENANCE coupling + DECAY robustness (deepening drills -- they PROVE the mechanism)
- **The maintenance loop is COUPLED to the graded ACT-R pick.** Running the IDENTICAL chaining loop over the incumbent
  rigid hard-tier pick (`hard_tier_pick`: most-recent grammatical-subject, the pick the coref-cap showed is worse than
  recency) does NOT help -- it HURTS: graded 0.473 -> 0.538 (+0.0647 CI-sep) vs hard-tier 0.404 -> 0.378 (**-0.0253
  [-0.0335,-0.0176] CI-sep**). A rigid tier cannot consume the accrued activation the loop deposits (it reads only
  "most-recent-subject", not the graded recency x frequency), and the chained pronoun-subject mentions actively mislead
  it. So the recurrence pays off ONLY with a pick that integrates ACT-R base-level activation -- which is exactly why
  the wire is "run the loop over the graded pick", not incidental. The maintenance lever and the brain's retrieval
  currency are one coupled system.
- **The gain is robust across the brain-plausible decay range, and exists BECAUSE memory decays.** Sweeping the ACT-R
  decay exponent d: chain-minus-nochain is CI-sep at d=2 (+0.036), d=3 (+0.065), d=4 (+0.055) -- the range the coref-cap
  sweep found plausible (d peaks ~2) -- but at d=1 (near-no-decay) it FLIPS negative (-0.104, not CI-sep): with no
  decay, distant entities persist on their own (nochain rises to 0.520) so chaining is redundant and over-boosts. The
  lever is not a d=3 artifact; it is the signature of a memory that fades (ACT-R d>0), which is the brain's regime.

## WALLS -- fully drilled to the brain mechanism and how we differ (owner directive)
- **WALL A -- the residual (chain 0.52 vs gold-chaining 0.73):** the oracle splits it into propagation-damage (+0.091)
  and missed-reinforcement (+0.085), and BOTH trace to one root -- the pick's STRUCTURAL ceiling. **Brain:** reference is
  a TWO-term Bayes (Kehler & Rohde 2013): a Centering LIKELIHOOD (role/recency/topichood -- what we compute) x a
  coherence-driven next-mention PRIOR (verb-semantics/discourse relations -- what we do NOT). **How we differ:** we have
  no prior, so on the structurally-dominated cases we err CONFIDENTLY -- 99.5%% of wrong picks are low-entropy, and 29.4%%
  of errors are strictly structurally-dominated (chain acc 0.481 there vs 0.684 elsewhere). That is why the confidence
  gate is a null and why chaining cannot fix them: a confident wrong pick cannot correctly reinforce the true entity.
  This residual IS the coref-cap solution's ~19%% coherence-prior residual -- a SEPARATE situation-model build, not a
  chaining defect. Chaining is doing its job; it is capped by the pick's structural ceiling.
- **WALL B -- cold re-instatement (the truly-cold sliver, no mention for 2+ sentences):** chaining keeps ACTIVE entities
  hot but cannot retrieve a dropped one. **Brain:** the sharp WM-focus vs episodic-retrieval discontinuity (McElree 2006:
  ~1 item in the focus, everything else by content-addressable cue-based access; Ericsson-Kintsch long-term WM);
  re-instating a cold entity from a bare pronoun is CA3 partial-cue completion (Nakazawa 2002) -- a DIFFERENT system.
  **How we differ:** my mechanism is pure WM maintenance; the substrate HAS the episodic organs (`ca3_completer`,
  `hippocampal_encoder`, `cortical_recall`) but they are not wired to entity tracking. Named adjacency, not this lever.
- **WALL C -- SOFT ("hold both") loses to HARD commit (-0.024 to -0.036 CI-sep):** my a-priori "soft is more faithful"
  was WRONG, and the correction is itself brain-foundational. **Brain:** attractor networks (CA3/Hopfield) SETTLE to ONE
  stored pattern -- they do not maintain a superposition (the `graded_competition` organ literally counts cycles-to-
  settle; Spivey-Knowlton). The Nref "hold both" is a transient READOUT/decision signal, not the MAINTAINED state. A
  distributed maintenance keeps distractors alive and prevents the entity attractor from consolidating -- which is why it
  loses. So hard-commit IS the faithful maintenance; we do NOT differ -- my soft hypothesis was the deviation, rejected.
- **WALL D -- near-nominal regression + 6/25 docs regress:** where the direct nominal is recent, `nochain` already wins
  and chaining only adds distractor noise. **Brain:** recency/locality dominates for near antecedents, and a NOMINAL
  mention is stronger entity evidence than a pronoun. **How we differ:** I chain pronouns at EQUAL weight to nominals.
  The faithful fix (down-weight pronoun evidence) is best on TRAIN (w=0.25) but NOT CI-sep held-out -> a located negative;
  the real fix is the same coherence-prior / finer clause-locality gating (the focus-stack solution's flagged #2 open
  problem). Default weight-1 retained.

## WHAT I DID NOT ESTABLISH / would withdraw first
- **The object-'it' held-out generalization** is NOT established (TEST flat; the +0.023 is ALL-set only, small n, hard
  population). First thing I would withdraw: any claim that object chaining generalizes HELD-OUT. What holds: the
  mechanism reproduces the long-distance signature and beats its twin on the full object set.
- **The near-nominal regression is real** (net across all holders is still +0.065 CI-sep, but 6/25 docs regress, worst
  -0.159). Chaining is net-positive but NOT uniformly harmless; the honest recall-safe signature is "helps far, costs
  near", not "harmless everywhere".
- **Absolute recall has an OOD question** (shared with the parent): LitBank is the reader coref's home corpus. The
  blind-vs-chain DELTA holds regardless (both arms same corpus); the absolute levels may be optimistic OOD.
- **The gold ceiling (0.73) is the gold-CHAINING ceiling, not 1.0** -- even perfect chaining leaves ~0.27 unresolved
  (the coherence-prior residual). Do NOT quote 0.73 as "solvable by chaining"; ~0.63 (oracle-gated) is the
  chaining-reachable ceiling, and the rest needs the prior.

## KEY REALIZATIONS (the enabling moves)
1. **SOFT maintenance LOSES to HARD, and that inverts the a-priori faithful design.** I built soft-chaining expecting
   the "hold both" distribution to be MORE brain-faithful and to dampen error propagation. It lost CI-separated. The
   reason is the deeper brain fact: pattern-completion attractors SETTLE onto one stored pattern; a maintained
   superposition keeps distractors alive and never consolidates. "Hold both" is a readout/abstain transient, not the
   stored state. The data corrected the design toward the more faithful mechanism -- committed maintenance.
2. **Bucket by distance-to-NOMINAL, not distance-to-any-mention.** My first long-distance axis (distance to any prior
   mention, incl. pronouns) HID the mechanism -- it showed chaining helping "near", because a chained pronoun makes
   every entity trivially near-by-any-mention. The correct axis (distance to the nearest NOMINAL, what the no-chaining
   floor actually sees) revealed the mechanism cleanly: the entire gain is FAR-from-nominal (+0.216), and it recovers
   43%% of that bucket's gold gap. Measuring the RIGHT distance was the move.
3. **The residual is the pick's structural ceiling, proven two ways.** The oracle-gated chain (0.629) and the
   structural-domination split (29.4%% of errors reachable by no structural cue, at 0.481 acc) together show chaining is
   capped by self-pick reliability -- the missing coherence PRIOR -- not by the maintenance mechanism. This points the
   next problem at the prior (a situation-model build), not at "make chaining safer".
4. **Two silent measurement bugs, both caught by disk-verification, both changed the numbers.** (a) Keying paired
   bootstrap on `midx` alone COLLAPSED the population across documents (midx is only unique within a doc) -> the composite
   `(doc, midx)` key. (b) `max(set(...), key=count)` in the entity-gender tie-break was PYTHONHASHSEED-dependent -> a
   ~0.013 cross-process drift (0.4735 vs 0.486); `Counter.most_common` makes it deterministic (verified identical across
   seeds 0/1/42). The `sorted(set())` discipline exists for exactly this; I violated it and the re-verify caught it.
5. **Attribution had to be surgical, so the pick is held byte-identical.** `local_graded_pick` copies the pinned formula
   and is self-tested BIT-EQUAL to `hdlab.graded_antecedent_pick` at weight=1; floor and arm share it AND the candidate
   entities. Without that, a chaining "gain" could hide a pick change. The gain lives entirely in the histories.
6. **The maintenance lever is COUPLED to the ACT-R pick -- proven by feeding the loop a rigid pick, where it HURTS.**
   Chaining over the incumbent hard-tier pick is -0.025 CI-sep (vs +0.065 over the graded pick). This inverts the naive
   view that chaining is a pick-agnostic preprocessing trick: the recurrence only helps a pick that INTEGRATES accrued
   activation, so "incremental maintenance" and "graded ACT-R retrieval" are not two separable improvements -- they are
   one brain mechanism (activation accrual feeding graded retrieval), and the wire must deliver both together.

## ADJACENT COMPONENTS (brain-fidelity + optimization -> next problems)
- **`hdlab.graded_coref_pick` (WIRED as the pick core; brain-foundational -- ACT-R graded retrieval).** Near-optimal
  (MAP theorem); held fixed here. Its landed `chain_pronouns` primitive lives in the reader but on the WEAKER centrality
  pick -- the wire below moves it onto the graded pick.
- **The coherence next-mention PRIOR (`hdlab.predictive_reader`; the residual's real fix; brain-foundational -- forward
  pre-activation).** The coref-cap solution's adjacency 1: multiply the graded retrieval posterior by the predictive
  reader's next-entity expectation before argmax. MEASURED here to own 29.4%% of the errors (struct-dominated) at 0.481
  acc. **-> The single highest-value follow-on for who-has-what accuracy.**
- **Episodic re-instatement (`ca3_completer` / `hippocampal_encoder` / `cortical_recall`; brain-foundational but UNWIRED
  to entity tracking).** Wall B: cold entity re-instatement is a partial-cue completion these organs implement. **->
  Next problem: cue a cold discourse entity from the pronoun's phi-features via CA3 completion (the WM->episodic
  handoff).**
- **The name-branch grouping (`the_name_branch_shatters...`, a CONCURRENT solver's problem).** Upstream of this: cleaner
  nominal grouping raises the whole stack. NOT my lane; the aliaser glass-box grouping here is used as-is.
- **The reader's `event_centrality_coref` chaining primitive (WIRED; brain-foundational).** Already chains pronouns; the
  wire below composes this result with it by running the loop over the graded pick.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md 2b -- strategy folds in)
The he/she who-has-what ceiling is INCREMENTAL ENTITY MAINTENANCE (a recurrent working-memory loop: chain each resolved
pronoun into the entity's ACT-R activation history), NOT the per-pick resolver (near-optimal, MAP theorem). Built
glass-box over the pinned graded pick, it lifts who-has-what CI-separated (held-out +0.057; glass-box +0.068; twin
loses), and the lift is a TARGETED long-distance re-instatement (far-from-nominal 0.261->0.471 toward gold 0.750, 43%%
recovered). NEW brain-foundational findings: (i) maintenance is a COMMITTED attractor, not a held distribution -- SOFT
"hold both" maintenance LOSES to HARD commit CI-sep (attractors settle; the Nref is a readout transient, not the stored
state). (ii) The chaining-reachable ceiling is ~0.63 (oracle-gated), NOT the 0.73 gold ceiling; the remaining ~0.10 is
the missing coherence PRIOR (Kehler-Rohde) -- 29.4%% of errors are structurally-dominated (0.481 acc) and 99.5%% of wrong
picks are confident, so the residual is confident structural error the entropy gate cannot catch. (iii) Cold-entity
re-instatement (no mention for 2+ sentences) is OUT of scope for WM maintenance -- it needs episodic CA3 completion (a
different system). Citations to add: Gernsbacher 1990 (structure-building); Lewis & Vasishth 2005 (ACT-R retrieval);
McElree 2006 (focus-of-attention vs cue-based access); Nakazawa 2002 / Marr 1971 (CA3 partial-cue completion);
Kehler & Rohde 2013 (two-term Bayes); Nieuwland & Van Berkum 2008 (Nref = readout transient).

## TO REALIZE THE GAINS -- ORDERED (strategy lands hdlab; Q111 -- I did not write hdlab/)
**STEP 1 -- WIRE the graded-pick chaining loop into the reader (default-off).** The reader already chains pronouns
(`event_centrality_coref.resolve_stream`, `chain_pronouns=True`) but onto its centrality pick. Add a default-off
`graded_chain` path that runs the recurrent loop over `graded_coref_pick.graded_antecedent_pick` with the landed
`keep_after_pool_cleanup` + `is_discourse_participant` filters, HARD-committing each resolved he/she pronoun into the
picked entity's mention history (weight 1). ACCEPTANCE: flag OFF -> byte-identical; flag ON -> who-has-what beats the
no-chaining path CI-separated (demonstrated +0.057 held-out), the lift concentrated far-from-nominal.
**STEP 2 -- carry it into the world-state densifier** (the parent's `densify_world_state`): the holder binding should
use the chained (maintained) entity histories, so long-distance he/she holders resolve. ACCEPTANCE: densified
who-has-what with chaining > without, CI-sep, on the far-from-nominal population.
**STEP 3 (the big remaining lever) -- BUILD the coherence next-mention PRIOR** (multiply the graded posterior by the
predictive reader's next-entity expectation before argmax) and re-measure on the 29.4%% structurally-dominated errors.
This is the residual's real fix and it lifts BOTH the pick AND (through the loop) the maintenance. ACCEPTANCE: chain acc
on the struct-dominated bucket rises from 0.481 CI-sep.
**STEP 4 -- episodic cold re-instatement:** wire `ca3_completer` partial-cue completion to re-instate a cold entity from
the pronoun's phi-features (Wall B). ACCEPTANCE: the truly-cold bucket (no prior mention) rises above 0.

## TLDR
As you read a story you keep a running memory of each character, and every time you meet "she" you not only work out who
it is, you also refresh that person in memory so the next "she" is easier. Our tracker resolved each "she" from scratch
against the last time the character was named -- so when the name was many sentences back it lost the trail. I added the
running memory: each time a "she" is resolved, that mention is folded back into the character's memory, keeping her
"warm" for the next pronoun. On real 19th-century novels this made the tracker meaningfully better at "who has what" (a
clean, statistically separated gain that held on books it was not tuned on), and -- the important part -- the whole
improvement is on exactly the hard cases where the character had not been named for a while (there it recovers about
four in ten of the gap to a perfect-memory oracle), while it is neutral where the name was just mentioned. Scrambled and
"spread the memory around" versions both fail, which tells us it is the CORRECT running memory doing the work. Two honest
limits I nailed down: (1) the leftover mistakes are cases where the grammar genuinely points at the wrong person and only
world-knowledge/meaning could fix it (a separate piece we have not built), and (2) a character who has dropped out of the
story entirely can't be kept warm -- retrieving them needs a different, memory-recall system. I also caught and fixed two
of my own measurement bugs before trusting the numbers (one made the result depend on a random seed).

## QUESTIONS
None.

## NEXT STEPS
1. (Strategy) Wire the default-off graded-pick chaining loop into the reader + carry it into `densify_world_state`
   (STEPS 1-2 above); re-verify the witness first.
2. (Follow-on problem) The coherence next-mention PRIOR channel -- the residual's real fix (owns 29.4%% of the errors);
   multiply the graded posterior by the predictive reader's next-entity expectation. The single highest-value accuracy
   lever left.
3. (Follow-on problem) Episodic cold-entity re-instatement via `ca3_completer` (the WM->episodic handoff, Wall B).
4. (Fold) The AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` 2b.
