# pri 113 head-to-head: owner-run vs agent-run (2026-09-14)

Same brief (one in five asserted clauses has a non-verbal predicate no VERB-gated consumer sees), same base
(`comparison_pri113_base` = 816efb22a + the working tree), blind to each other. The agent saw the first 90 lines of
the owner's cell (docstring + the start of the copula-scan extension) before the folder ruling; it had derived the
locative / clause-final constructions ~10 minutes earlier on its own, and declared the contamination. Strategy read
neither folder until both were in. Both verdicts: PARTIAL.

## 1. The bar, with CIs (same instrument design on both sides: argument-structure scoring, gold tag column never read)

| | OWNER (`SOLVED.md`) | AGENT (`SOLVED_agent.md`) |
|---|---|---|
| Floor on the 167 non-verbal clauses (UD-EWT test 700) | 0.1856 | 0.1856 (same) |
| Recall on the 167, shipped mechanism | **0.7365** (+0.5509 CI[+0.4789,+0.6228] sep) | **0.8084** at phase 5 -> **0.8802** after phase 7 (15 constructions + graded arc cue; +0.1522 pooled-recall CI-sep) |
| Pooled precision | 0.8358 -> 0.8244 (held; verbal untouched 0.9950) | 0.8358 -> 0.8370 (phase 5) / 0.8305 (phase 7); -0.0052 CI[-0.0136,+0.0030], not down |
| Twin | 0.2635 (random clause token, matched rate) | 0.2275-0.2934 (three seeds); every twin beaten CI-sep on recall AND precision |
| Oracle | gold slot 1.0000 (instrument well-formed) | not run as an arm; the residual attributed item by item instead |
| Out of supply (GUM / GENTLE) | floor 0.0784 -> **0.5705** (+0.4922 sep), precision held, 319 clauses, cap 1000 | floor 0.1230 -> **0.6120** (0.6257 with the arc cue), 366 clauses; precision **-0.0083 CI-sep DOWN**, attributed to the closed-class word lists (not the governor read) |
| Role competition on the 167 | "largely already receives the predicate"; subject 0.84; obliques 0.53 -> ~0.83 LOCATED (PRED keyed on predicate-hood; needs a table rebuild; prototyped, must be selective) | cue coverage FIXED (slot 2->52, rank 5->136, frame 3->27) but accuracy **-0.0260 CI[-0.0558,+0.0037]** vs a matched control; four rebuilt tables; the repair its own diagnosis named was built and REFUTED (-0.0297); Higgins cue +0.0037 n.s. |
| One structure per clause | `is_state` co-indexed with the state reader (proposed diff) | measured consolidation: **state 0.7487 -> 0.7857, +0.0370 CI[+0.0186,+0.0571] CI-SEP at full n**, 14 docs gained / 0 lost; disagreements 30 -> 20 -> 11 (cause located: `robust_cop`'s HOLDER rule) |
| The 65 seen by nobody | counted residual: 123 hit / 15 blocked / 14 clausal-complement / 10 inverted / 5 verbless | 65 -> 39 -> 32, all 32 attributed to 9 mechanisms; 10 provably outside the rung; 4 are treebank head conventions |
| Board | CAPPED A/B byte-identical on 7/7 (aggregate 0.5958 -> 0.5958) -- an underpowered instrument by today's rule (capped zeros are the instrument's floor) | CAPPED 7/7 zeros, THEN the FULL board on the phase-5 arm: coref -6 items, patient -6, state -1, aggregate -0.0006 -> the arc cue default reverted; the shipped configuration (with the state consolidation) not yet full-boarded |

Read: on the instrument the agent got further in supply (0.88 vs 0.74) and about the same out of supply (0.61 vs 0.57
on different populations), and it paid for the extra in-supply recall with a measured out-of-supply precision cost
that it attributed to its own word lists. The owner's mechanism is the smaller, safer core (42 added lines vs 596).
The agent's state consolidation is the only CI-separated BOARD win either side produced.

## 2. Depth of the chain trace and of the explained negatives

**Owner** went UP the chain and OUT to the representation: the heads rung's non-verbal attachment (0.54 vs 0.85 on
verbal) traced as the single biggest upstream loss and PROTOTYPED (predicate-slot-biased re-attachment as a graded
arc feature + held/reshape decode: 0.5385 -> 0.6509, propagating to the event stream 0.60 -> 0.72 and entity binding
0.71 -> 0.89); the reframe that a non-verbal predication is a TYPED ATTRIBUTE on the entity (a Kimian state), not an
eventive record (typed-attribute capture 0.35 -> 0.56, holder 0.85); the five named hand-offs where the signal drops;
a literature scan; two cues (agreement, discourse-givenness) prototyped and refuted; a false-negative audit of the
cited negatives; the contextual-HRR lever measured positive (+0.049 / +0.089) after first being called unprototypable;
walls A/B/C mechanised; and an honest "wiring is necessary, not sufficient" section. Broad, architectural, and it
corrects itself in the record (sections 18, 28, 31/32).

**Agent** went DEEP inside the remit with controls at every step: every construction ablated one at a time (two worth
exactly zero, reported as zero; one narrowed because it cost more than it bought); every negative researched to a
mechanism with a matched control (the PRED split's -0.026 is a measured cue-by-cue contribution table, not a guess;
the repair its own diagnosis named was built and refuted it); the graded arc cue's bimodal gate explained (kept sites
median P=1.0000 vs dropped median 0.0001); the tense reader from 0 to 117 of 167; the event/state disagreements
adjudicated against gold (20 slot-right, 9 state-right); three labelling errors and one wrong default caught by its
own controls and left in the record; a full-size board it ran even though it went against it.

Read: the owner's trace reaches rungs the agent did not touch (the heads rung, the entity-state representation, the
SOTA gap); the agent's negatives are better controlled and every number it reports has a twin or a matched
control beside it. The owner's role-competition claim (obliques 0.53 -> ~0.83, located) and the agent's (the PRED
split loses, matched control) DISAGREE and neither was run under the other's control -- see section 5.

## 3. Follow-up briefs produced

**Owner (ranked):** (1) the heads rung's non-verbal-predicate attachment with an ONLINE-learned copular-subject
validity (prototyped 0.65, must be plastic); (2) land the complement firing as a typed STATE(entity, property,
polarity, time) with a symmetric EQUATE fallback; (2b) two cheap coverage subtypes (interrogatives; locative
inversion via agreement); (3) the role table rebuilt with PRED keyed on predicate-hood; (4) extend the board's
who-did-what dimensions to score non-verbal predications (the gain is board-invisible); (5) the inverted copular in
`cop_predicates`; plus the cross-cutting representational lever (a learned contextual encoder on all arcs).

**Agent (ranked):** (1) learn the construction memberships from counts with an observe() on confirmed predications
(the 0.8383 -> 0.6120 out-of-supply gap is the measure of what is treebank); (2) the Higgins cue in its
argument-population form; (3) `robust_cop`'s HOLDER rule (the last 11 one-structure clauses); (4) the role asset's
drift (22% fewer instances clear the reliability gate on today's frontend); (5) route the fragment branch into
`predicate_sites` (6 clauses); plus two findings outside remit: rebuilding the role table on today's frontend LOSES
0.0100 / 0.0447, and the copular state reader is a second predicate finder.

Read: the owner's leads are larger and further up the chain (two are brief-ready for other organs); the agent's are
smaller, each with a number and a bound. Both name the board's blindness to this gain; only the owner proposes the
board fix.

## 4. Wall-clock and tokens

| | OWNER | AGENT |
|---|---|---|
| Wall-clock | ~5 h 30 min (cell first written 13:52, result pasted 19:25) | 2 h 26 min to the phase-7 end, ~2 h 50 min including the last board (13:46 -> ~16:35) |
| Tool calls / experiment runs | not recorded (owner to supply) | ~215 tool calls, 56 experiment runs |
| Tokens | not recorded (owner to supply) | ~750k subagent tokens (opus) |
| Report | 1,036 lines, 33 sections | 1,478 lines, 13 sections + phase 7 |
| Diff | 3 files, 42 added lines | 3 files, 596 added lines |
| Self-test | `--self-test` (PATCH == CELL) | 14/14 incl. PATCH == CELL and an execution of the diff's own code |

## 5. What strategy integrates, and what is unresolved

1. **Land the shared core once**: fire the clause event/state on the copular complement, co-indexed with the state
   reader (both diffs; the owner's is the minimal form). Land the agent's **state consolidation** (the one CI-separated
   board win, +0.0370 at full n) and the owner's `is_state` typing together as ONE structure per clause.
2. **Constructions**: ship the constructions BOTH sides found (locative / clause-final) plus the agent's ablation-
   positive ones, but the agent's own out-of-supply finding says the word lists overfit UD-EWT: the landing must be
   full-boarded (one process, full size) and the owner's typed-STATE reframe is the form that avoids committing an
   order the inverse cases do not determine.
3. **Arc cue**: off (the agent reverted it after the full board); revisit with the owner's graded heads-rung feature,
   which is the same idea one rung up and measured larger (0.5385 -> 0.6509).
4. **The role competition disagreement** (owner: obliques 0.53 -> ~0.83 located; agent: PRED split -0.026 with a
   matched control): unresolved. Run the owner's SELECTIVE form under the agent's matched control before any role
   change lands.
5. **Board**: the owner's capped byte-identical board is not evidence of no effect (today's rule); the agent's full
   board shows a 6+6+1-item cost on its phase-5 arm. The merged landing gets one full-size, one-process A/B.

## 6. Verdict on the comparison itself

Complementary, not redundant. The agent produced the better-controlled measurement of the brief as posed and the
only board-visible win; the owner produced the deeper diagnosis of WHY the bar is bounded (the heads rung and the
representation) and the architectural reframe that changes what should be built next. The agent was about twice as
fast and recorded its own errors; the owner reached rungs no agent brief would have reached because the brief did
not name them. The program should keep both: agents for the bounded measurement with controls, the owner for the
cross-rung diagnosis -- and briefs should ask for the upstream trace explicitly, since the agent stayed inside the
remit it was given.
