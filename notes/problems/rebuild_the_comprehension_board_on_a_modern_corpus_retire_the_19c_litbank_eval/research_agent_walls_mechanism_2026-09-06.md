# Research drill — the MECHANISM of the modern who-did-what AGENT walls (2026-09-06)

Solver: rebuild_the_comprehension_board_on_a_modern_corpus_retire_the_19c_litbank_eval. Glass-box, NO LLM.
Instrument: `experiments/_drill_agent_walls.py` + `experiments/_diagnose_agent_upstream.py` (UD-EWT train+test).
This drills, to mechanism, WHY the upstream PP-government fix failed and WHY the competition's value on modern is
passive-only — the two under-understood walls, plus the pp-suspect wash and the tracked-set sign-reversal.

## The unifying mechanism (the one finding that explains most of the others)

**The Competition-Model AGENT cue set is PREVERBAL-DOMINATED, so on canonical clauses the competition is
CORRELATED with the positional heuristic — and therefore cannot recover the clauses where position fails.**

Measured P(cm picks the SAME candidate as position) by clause class (UD-EWT train+test):

| class | P(cm == positional pick) | n |
|---|---|---|
| active canonical | **0.841** | 12597 |
| pp-suspect active | 0.362 | 643 |
| passive | **0.159** | 182 |

The preverbal cue (weight 3.0, vs animacy/core-arg/salience at 2.0) dominates the additive activation on an active
clause, so the argmax is the nearest-preverbal nominal **84% of the time on canonical clauses** — i.e. cm ≈
position there. The competition DIVERGES from position only when a non-preverbal cue decisively overrides: the
VOICE cue on passives (divergence 84%) and the core-argument cue on pp-suspect (64%).

**Consequence — the competition does WORSE THAN RANDOM on position's failures.** On the clauses where position is
wrong (n=1980, mean 6.1 candidates):

| arm | recovers the gold agent |
|---|---|
| **cm (real competition)** | **0.137** |
| scrambled-supports twin | 0.169 |
| random-over-candidates expectation | 0.155 |

cm recovers only 0.137 — **below the random 0.155 and below the decorrelated twin 0.169** — because on 54.8% of
position's failures cm makes the SAME wrong pick as position (P(cm==floor | floor≠gold) = 0.548), and on the rest
its preverbal-biased cues resemble the same mistake. The scrambled twin, being decorrelated, reverts to ~random
and thus BEATS the real mechanism on this subset. **This is the precise reason the assigner's value is
passive-only:** the voice cue is the one cue that is NOT correlated with position, so it is the only place the
mechanism recovers a failure. It also proves cue-reweighting CANNOT fix the residual: preverbal is RIGHT on
canonical (84% — needs a high weight) and WRONG on failures (needs a low weight), and nothing but a PARSE tells
you which regime a clause is in. The "needs a register-general parse, not a cue" conclusion is validated at the
mechanism level, not asserted.

## Wall A — WHY the sharper PP-government detector (v3) over-fired (74% false positives)

v3 skipped compound noun modifiers (PROPN/NOUN) to catch compound-modified PP objects ('the commander **of**
Ninevah **Province**') and guarded with "a preposition governs an object only if a nominal precedes it". It passed
all 6 hand-probes and REGRESSED at scale. Mechanism (measured): v3 newly-flagged 390 clauses as PP-governed;
**position was actually RIGHT on 290 of them (false-positive rate 0.744)**. The false positives are a systematic
class the guard cannot exclude:

- **relative-pronoun subjects** — 'the officers **who** were secretly working' → 'who' flagged (scan left over
  'officers' finds no prep in-NP, but the guard's nominal-before-prep test matches an earlier clause's noun).
- **clause-initial pronouns after a FRONTED adjunct** — 'As a child in the 50's **I** had…' → 'I' flagged
  because 'child … in' precedes it, and the guard sees a nominal ('child') before the preposition ('in').

The guard "a nominal precedes the preposition" does NOT distinguish (a) a PP that attaches to a HEAD inside the
same NP (a real PP-object: 'commander of Province') from (b) a FRONTED PP-adjunct whose own object precedes an
UNRELATED following subject ('[As a child in the 50's] I …'). Distinguishing them needs the attachment structure
— a parse. So the aggressive detector cannot be made precise with a linear left-scan; the conservative
comma-stopped detector (no compound skip) is the deployable one (full-set +0.0029 vs v3's −0.0068).

## Wall C — WHY the pp-suspect slice is a WASH

On genuine pp-suspect clauses (position's pick is PP-governed, n=643): reachability (gold subject IS a candidate)
= 0.823; floor==gold 0.350; **cm==gold 0.355** (marginal); cm==floor 0.362. So the core-argument cue correctly
REJECTS the PP-object pick and diverges from position 64% of the time — but when it diverges it lands on the true
subject only marginally more often (0.350→0.355), because among the ~6 remaining candidates the preverbal/animacy
cues cannot identify WHICH nominal is the subject, and 18% of true subjects are not candidates at all (reachability
0.82). Rejecting the distractor is not the same as finding the subject; the latter needs structure.

## Wall D — WHY the tracked-set decouple REVERSES sign on modern (the 19c lever hurts)

On GUM (modern discourse) the reachable ceiling of the tracked/given candidate set = 0.719 (only 72% of gold
agents are tracked coref entities, vs 79% in 19c fiction and rising toward ~100% for the dense set). Restricting
the AGENT competition to the tracked set therefore CAPS recovery at 0.72 by construction, and on modern
expository/news prose the dense set + word-order (cm_dense 0.719) already beats the capped tracked set
(cm_tracked 0.634). In 19c character-driven fiction the tracked set both had high reachability AND removed the
dense multi-clause distractor flood, so it helped (cm_dense 0.082 << cm_tracked 0.252); on modern edited prose the
distractor flood is smaller and the reachability cost dominates, so the SAME restriction hurts. The lever's sign
is set by (reachability of tracked agents) × (distractor density) — both register-dependent.

## PINNED vs OUR-INVENTION (labelled)
- PINNED: the Competition-Model additive cue integration; the cue identities (preverbal/animacy/voice/core-arg/
  case). The FINDING that preverbal dominance makes cm correlated with position is a measured property of the
  PINNED English word-order cue, not an invention.
- OUR-INVENTION-UNDER-TEST (tested, reported): the v3 aggressive PP-government detector (LOCATED NEGATIVE); the
  validity-seeded weights (register-specific, not adopted).

## What this closes, and what it opens
CLOSES (measured NO): more glass-box cue-tuning of the agent assigner on modern — the residual is structurally
un-recoverable by cues (cm < random on position's failures). OPENS (measured YES): a register-general incremental
PARSE that supplies subject-attachment as the one cue that is decorrelated from position on ACTIVE clauses (today
only the voice cue is) — already filed as `the_agent_tie_wall_is_embedded_clauses_needs_a_register_general_
incremental_parse_cue`. A cheap named sub-slice: an existential-'there' detector (part of the 78% bucket).

## Wall E — the COORDINATION cue was NEUTRAL because CLAUSE-coordination looks like NP-coordination
The construction upgrade added a 'NP1 and NP2 V -> agent = NP1' rule. Naive, it was a located NEUTRAL. Drill: it
fired on 388 clauses and **position was already RIGHT on 216 (56%)** — because the naive rule cannot tell
NP-coordination ('the IP **and** ICDC have…', agent = IP) from CLAUSE-coordination ('a clan , **and** some
observers have…' / 'on the street **and** they have…', where 'and' joins two clauses and the preceding nominal is
in the OTHER clause). Three guards fix it (all measured necessary): the coordinator must IMMEDIATELY join the two
NPs (only NP-internal modifiers between); NO ', and' (a comma before 'and' = clause/list coordination); and NP1
must NOT be PP-governed ('on the street' -> street is an object, not a subject conjunct). Guarded, the cue lifts
genuine NP-coordination **0.307→0.5817 (+0.275 CI-sep)** with the false-positive clause-coordinations removed
(n 380→153) and zero canonical regress. Same lesson as the v3 PP wall: a linear surface rule needs explicit
constituent-boundary guards to stand in for the parse it lacks.

## The construction-cue outcome (the upgrade the drill predicted, BUILT)
Two DECORRELATED construction cues (existential + guarded NP-coordination) lift the FULL modern who-did-what AGENT
set 0.855→0.873 (+0.018 CI-sep), zero canonical regress, twin loses — the first clear full-set margin over
position, exactly as the "add a cue decorrelated from position" mechanism predicted. CLEFT was checked and is NOT
an agent-dimension lever (the embedded nsubj is the relativizer, already correct — 'X = who' is coref). SALIENCE
(ACT-R/Centering) is ALREADY the deployed pronoun-pick mechanism in the coref dimension; the standalone
protagonist arm is frequency-dominated only because its gold IS frequency. So the glass-box AGENT frontier after
this round is genuinely the register-general parser + Phase-1 (filed); the construction inventory has diminishing
per-construction value beyond existential + coordination.

## Citations
Bates & MacWhinney 1989 (Competition Model; word-order as the dominant English cue); MacWhinney 1987 (cue
validity is environment-specific); McClelland 2013 (additive cue → posterior); Lewis & Vasishth 2005 (cue-based
retrieval); DuBois 1987 (Preferred Argument Structure — the tracked-agent prior); Bornkessel-Schlesewsky &
Schlesewsky 2006 (eADM — a parse enters as a precision-weighted cue).
