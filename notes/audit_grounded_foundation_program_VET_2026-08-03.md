# ADVERSARIAL VET — grounded-foundation program design (commit f4c42f226)

Auditor: Skunkworks (cert-owner). Audit-only, no cells authored/dispatched. Target doc:
`notes/foundational_grounded_knowledge_layer_program_2026-08-03.md` @ f4c42f226.

## Method
Every load-bearing claim disk-verified independently (not read from the doc's own citations):
`data/corpora/binder/binder2016_ratings.csv` (row/column contents), `hdlab/animacy_lexicon.py`
(full read), `hdlab/self_improving_loop.py` (full read, 178 lines), `data/capability_registry.jsonl`
(wiring status), `data/exp_theory_of_mind_sally_anne_nested_hrr_v1/metrics.json`,
`data/exp_mcguffey_whoaffected_verb_affectedness_gate_v2_heldout/metrics.json`,
`data/substrate_index/meta/atoms.jsonl` (atoms 29613-29624), grep across the repo for
"false-consolidation"/"consolidation ledger".

## Director's 6 findings — CONFIRM/REFUTE

**1. SUPPLIED != UNDERSTOOD (assignment-vs-understanding tension).** CONFIRM, and this is the
correct central tension — not overstated. Disk-verified: Binder rows FOUND =
`angry, happy, joy, love, awe, animosity, apology`; rows ABSENT = `anger, fear, afraid, sad,
sadness, hate, hatred, revenge, punish, hurt, harm, help, kind, cruel` (verified via direct grep
of column 2 of the 536-line CSV — exact match to the doc's own 1.5-A claim, no discrepancy). The
doc's fix (compose abstract concepts over Binder axes rather than look them up) is real and not
hand-waved as theory, but as of TODAY nothing on disk actually performs that composition — it is
100% proposed, 0% built. Severity: not fatal under the already-locked meaning=assignment
definition, but the fork with the USER's "can't learn from a book" bar is real and unresolved —
see Fork below.

**2. `retaliate(blocker)` is a supplied action primitive.** CONFIRM, severity raised to
HIGH when combined with #4. The world's action set is `{pursue, block, help, retaliate,
withdraw}` — five named, hand-designed actions, one of which is pre-labeled with the exact
semantic content ("act against a specific other agent who has PREVIOUSLY blocked own goal") that
the sim is supposed to be discovering. What's earned is a policy over this closed, pre-built menu,
not the concept of targeted retaliation itself.

**3. Appraisal schema (Scherer CPM, 4 dimensions) supplied by hand.** CONFIRM — directly stated
in the doc itself (2a: "SUPPLY BY HAND (genuinely not on disk yet)"), not hidden. The doc is
honest about this, but "what anger computationally IS" (the mapping from event+goal+cause to an
emotion CATEGORY) is architected by the human designer citing one specific theory (Scherer's CPM)
among several competing appraisal theories (OCC, Smith-Lazarus) — see new hole (a) below for why
this is worse than the doc frames it.

**4. Construction-determination in the discrete grid-world.** CONFIRM, HIGH severity — the
strongest of the six. With 5 actions and a reward defined as "own-goal eventually achieved,"
and only `retaliate(blocker)` capable of targeting the specific causal agent, the "hard" part of
the learning problem may collapse to fitting a decision boundary over ~4 boolean/scalar appraisal
features onto ~5 labeled actions — a shallow classification/bandit problem that a linear
classifier could plausibly solve regardless of whether anything resembling "grounded meaning" is
happening. The 2c three-floor can-fail test partially guards this (a no-appraisal floor) but does
not rule out that ALL floors including the earned one are solving an engineered, over-determined
task.

**5. Sim-to-reading transfer asserted, not shown.** CONFIRM, and this is the single largest
unaddressed engineering gap in the whole doc (co-equal with #6, arguably the most consequential
finding of the six). Section 3 describes the mapping (text -> situated-structure tuple -> query
the grounded function) entirely in prose; there is no specified encoding bridge from
TEXT-EXTRACTED (agent, target, action, goal-context) into the simulation's internal feature space
(discrete world positions, Binder Harm/Benefit scalars, animacy booleans). Worse: the specific
verbs the reading stage will need to score ("punish," "avenge," "retaliate") are THEMSELVES not
Binder rows (per 1.5-A's own disk-verified finding) — so grounding those exact words for the
reading stage still requires some word->grounded-feature mapping step that isn't specified
anywhere, and risks re-importing the distributional-guessing failure the whole program exists to
eliminate, just one level removed (word->Binder-axis instead of word->co-occurrence-vector).

**6. Grounding-transfer compositions must be derived, not hand-authored.** CONFIRM, HIGH
severity, tied with #5 as the biggest open mechanism gap. Section 3.5's worked example
("revenge = Harm-toward-other-after-being-harmed-by-that-other") is prose written by the doc's
author. No algorithm is specified for the substrate to DISCOVER which composition of primitives
corresponds to a novel lexical item; only the THEORY that composition is possible (Harnad) is
cited. As specified, the "growth operator" would have to be implemented as a human enumerating
`if word == 'revenge': compose(...)` rules — exactly the "hand-curated dictionary with a
provenance field" the finding warns about. This is not resolved anywhere in the doc; it is the
biggest single missing mechanism.

## New holes found (beyond the Director's 6)

**(e) A load-bearing dependency that DOES NOT disk-verify — Section 3.5's reuse of
`hdlab/self_improving_loop.py`.** The doc claims: "Its consolidation ledger + FALSE-CONSOLIDATION
detection ... is exactly the mechanism that must guard the store from poison" and lists this as
REUSED (not new) in the summary table. Disk-verified FALSE: I read the full 178-line
`hdlab/self_improving_loop.py` — it contains `decode_coherence_margins`, `decide_keep_or_revert`,
`route_passage`. There is no ledger (no persistence at all — every function is pure/stateless) and
no mechanism or term "false-consolidation" anywhere in that file. `grep -rl "false.consolidation"`
across the whole repo returns exactly ONE file besides this design doc:
`hdlab/coreference_resolver.py`, where "false-consolidation" refers to a DIFFERENT thing entirely
(a pronoun over-attaching and merging two distinct coref entities into one cluster) — not a
store write-back safety mechanism. The capability_registry entry for this module
(`self_improving_loop_coherence_gated_keep_revert_controller`) states explicitly: "NOT a general
autonomy result; do not deploy on sparse/low-density content without re-validating" and scopes it
to "DENSE McGuffey content only." The registry-certified atom this claim rests on (29624,
`MM_STANDARD_SYNTHESIS`, 3 cycles / 4 fix-levers / 2 falsified — this numeric tally itself DOES
disk-verify against the atom) carries an explicit `honest_scope` clause: "NOT verdict-bearing as a
general-purpose or domain-independent self-improvement guarantee." Repurposing this exact,
narrowly-scoped-by-its-own-certification module as the write-back gate for an entirely different
data type (symbolic grounding-composition candidates, not coref cluster-id candidates over
role/event-slot sequences) is a genuine domain generalization with ZERO supporting evidence, and
directly contradicts the atom's own stated scope limit. `decode_coherence_margins` requires
`role_seq/event_slots/cluster_ids/role_vocab` — there is no code path from a candidate grounding
like "revenge = Harm-toward-other-after-harm" into those types. Calling this "REUSED (compose 3
existing pieces)" in the doc's architecture section is not accurate; at most the PATTERN
(coherence-margin gated keep/revert) is reusable, and a new coherence signal + a new persisted
ledger + false-consolidation logic for the grounding-store domain would all have to be built from
scratch. Severity: HIGH — this materially changes the "small buildable surface" framing in
section 7 (recommends 3.5's living-store gate as ready-to-wire when it is not built at all).

**(f) The verb-affectedness lexicon (1.5-D) is presented as "REUSED AS-IS" but its own held-out
cell shows a catastrophic out-of-domain regression, undisclosed in the doc.**
`data/exp_mcguffey_whoaffected_verb_affectedness_gate_v2_heldout/metrics.json` (verdict
`GATE_GENERALIZES_BUT_OVERFIRES_UD`): on held-out McGuffey it reaches combined_acc=0.8158 (not
the 0.912 the doc cites, which the CELL ITSELF documents was "co-defined," i.e. circular with its
own gold-labeling — the doc does flag this caveat, credit where due). But the SAME cell reports
`UD-EWT no-reg N=1095: base=0.6329 comb=0.2374 (d=-0.3955), no_regression=False` — on a broader,
out-of-domain corpus the gate's accuracy COLLAPSES by 40 points when applied broadly (it
"overfires"). This is the exact lexicon the design proposes wiring in as the harm/help
"who-is-affected" signal feeding the appraisal congruence dimension for ALL future reading, not
just McGuffey. If deployed as specified, the appraisal computation inherits this brittleness
silently for any content outside the McGuffey-shaped register. Additionally, this lexicon is not
an importable `hdlab/` module (unlike animacy_lexicon.py) — it lives embedded in two experiment
scripts (`exp_mcguffey_whoaffected_verb_affectedness_gate_v1.py`/`_v2_heldout.py`), so "REUSE
AS-IS" understates real integration work needed. Severity: MODERATE.

**(g) The appraisal SCHEMA is locked-in, not revisable, and represents one specific psychological
theory as ground truth.** Scherer's Component Process Model is one of several competing appraisal
theories (vs. OCC, Smith-Lazarus). The design supplies Scherer's four dimensions
(goal-relevance/congruence/causal-attribution/coping-potential) as THE fixed architecture with no
mechanism proposed anywhere for the schema itself to be revised if it proves wrong or
incomplete for narrative content (e.g., OCC separately tracks blameworthiness/desirability in a
way Scherer's model collapses into "causal-attribution"). Only the MAPPING from dimensions to
actions is earned; the dimension set itself is permanently fixed by fiat. This compounds finding
#3 — not just "supplied," but non-falsifiable within this design.

**(h) The 2c can-fail plan tests the simulation in isolation and never tests the actual payoff
claim (sim-to-text transfer).** All three can-fail floors (random / memorized-lookup /
no-appraisal) and both envelope bands operate entirely within the simulation's own world-state.
Nowhere in 2c is there a proposed discriminator that feeds the earned function TEXT-DERIVED
situated structures and checks the output is sensible — i.e. the can-fail test cannot fail on the
central promise of the whole program (that grounding earned in simulation transfers to reading).
This means the design's own falsification plan would PASS even if finding #5 (sim-to-reading
transfer) turns out to be completely broken. Severity: HIGH — this is a real gap in the
can-fail design, not just an implementation TODO.

**(i) Minor: `a7a370e2` is cited in the summary table as "REUSED, in-flight test ... becomes the
reading-side FEEDER" — disk-verified this test is genuinely IN-FLIGHT / undecided
(`notes/WHERE_WE_ARE_NOW.md`: "TEST IN FLIGHT (a7a370e2): ... STRUCTURE_HELPS -> ...;
STRUCTURE_INSUFFICIENT -> ..."), not a settled, reusable result. Listing it under "REUSED" in a
table meant to distinguish reused-vs-new slightly overstates its maturity; it should be listed as
PENDING/in-flight, one more dependency this program needs to land before section 3's reading-side
claims are actionable.

## Answers to the USER's two framing questions

**Q1 — Does our existing grounding actually include emotions like anger/revenge?**
NO, disk-verified. Binder2016 (535 rows) contains `angry` (adjective) plus `happy, joy, love, awe,
animosity, apology` — it does NOT contain `anger` (noun), `revenge`, `fear`, `sad`, `sadness`,
`hate`, `punish`, `hurt`, `harm`, `help`, `kind`, or `cruel` as rated rows. What exists today is
the DIMENSION SPACE (columns: `Angry, Fearful, Happy, Sad, ... Benefit, Harm, ... Drive, Needs,
Arousal`) that a FUTURE composition step could use to construct grounded vectors for those
concepts — but that composition step is 0% built (see finding 1 and hole (f)). The design's own
1.5-A section is honest about this on close reading, but section 0's rhetorical framing ("we have
already done SUBSTANTIAL STATIC grounding work") risks giving a skimming reader the impression
more is already grounded than actually is. As of today: the substrate does not ground anger or
revenge at all.

**Q2 — Does the substrate UNDERSTAND the things in the foundation, or just hold supplied
numbers?**
Mixed, and this is the real fork (see below), not a yes/no. The STATIC core (Binder ratings,
animacy lexicon, appraisal schema) is supplied numbers/rules — no understanding claim is credible
there, and the doc does not overclaim otherwise for this part. The DYNAMIC piece (2b) is
genuinely more than lookup IF built as specified: it is a real error-driven function fit against
simulated consequence, which is a legitimate glass-box "earning" step, not mere number-holding.
But per finding #4/(h), the specific closed-action, engineered-reward design of 2b makes it
plausible that even the "earned" part reduces to fitting a shallow decision boundary over ~4
features and ~5 labeled actions — which is closer to sophisticated pattern-matching than to
"discovering what revenge is." Verdict: the design, if built exactly as specified, produces a
system that computes a real function (not a static table), but whether that function constitutes
"understanding" anger/revenge or merely "correctly classifies appraisal-vectors into a
pre-supplied action taxonomy" is exactly the open philosophical question the USER is asking, and
the design does not resolve it — it makes a defensible glass-box engineering choice, not a proof
of understanding either way.

## The assignment-vs-understanding fork, stated crisply for the USER

- Under the project's ALREADY-LOCKED **meaning=assignment** definition (a symbol's meaning is a
  non-arbitrary computational assignment to grounded structure, not a distributional guess), this
  design QUALIFIES: Binder ratings are grounded axioms (human neural-correlate data, not
  co-occurrence), and the appraisal function is a computed assignment, not a table lookup for
  abstract concepts. On this reading, BUILD-2b-AS-IS is consistent with prior USER-authorized
  locks.
- Under the STRONGER reading implied by "you can't learn revenge and anger from a book" — that the
  substrate should arrive at what anger/revenge ARE through its own experience, not have the
  definitional content (which 4 dimensions define an emotion, which named action IS "retaliation,"
  which lexical compositions ARE valid) placed there by the human designer — this design
  undershoots: too much of the definitional content of "what anger is" is supplied (schema +
  named actions + hand-worked composition examples), leaving only a thin, possibly-shallow
  classification layer to be earned.
This is a genuine unresolved fork and a values/definition call, not something this audit can
close unilaterally — it should go to the USER explicitly before build, because it determines
whether findings #2/#3/(g) are acceptable design tradeoffs or disqualifying.

## Verdict

**REDESIGN-FIRST, not BUILD-2b-AS-IS**, for two independent reasons that are each individually
sufficient:
1. Section 3.5 (the living self-extending store, the USER's explicit first-class requirement) is
   NOT actually built from 3 reused pieces as claimed — new hole (e) shows the "consolidation
   ledger + false-consolidation detection" does not exist anywhere on disk and the module it's
   attributed to is certified, by its own registry entry and its own certifying atom's honest_scope
   clause, ONLY for a narrow, different domain (dense-McGuffey coref candidates). Building 3.5 as
   specified means building an entirely new coherence/ledger/false-consolidation mechanism for
   grounding-composition candidates from scratch — this is real, unscoped, un-estimated work, not
   the "small, already-certified" surface section 7 claims.
2. The can-fail plan (2c) never tests the program's actual payoff claim — sim-to-reading transfer
   (finding #5 / new hole (h)) — so even a full PASS on 2c would leave the central promise of the
   whole program unverified.

**Single most important change if proceeding:** add an explicit, disk-checkable Phase 0
discriminator BEFORE the 2b simulation is built: take the CURRENT grounded lexicons (Binder +
animacy + verb-affectedness) and hand-write (openly, as a throwaway probe, not as the production
growth operator) ONE concrete composition — e.g. ground "revenge"/"punish" as
Harm-toward-other-after-harmed-by-that-other over the existing Binder/animacy/affectedness
features on a handful of REAL McGuffey/reading-corpus sentences containing those words — and check
whether that composed grounding actually discriminates REVENGE_PUNISH from SELF_DISCIPLINE better
than the current text-only methods did, on real text, before any grid-world simulation is
built. This directly tests finding #5/#6 (the real payoff and the real mechanism gap) cheaply,
BEFORE investing in the RL-shaped 2b simulation whose main risk (finding #4) is that it may
"pass" its own can-fail bands for reasons unrelated to grounding meaning, and BEFORE committing to
building 3.5's store-gate mechanism from scratch on an unproven foundation.

## Where the Director's findings were right vs. where I'd push back

All 6 of the Director's findings CONFIRM on independent disk/text re-derivation — none were
refuted or found to be an over-read. If anything the Director UNDER-called severity on #5/#6 (I
rate both HIGH, tied for the single biggest gap, not "hand-waved" as a minor caveat) and missed
the single most consequential NEW hole: Section 3.5's core "reused, already-certified" claim about
`self_improving_loop.py` does not survive a full read of that file plus its own capability-registry
scope statement plus its own certifying atom's honest_scope clause. This is not a case of the
Director over-reading; if anything this design doc under-disclosed how unbuilt the 3.5 mechanism
actually is relative to how it is framed in the doc's own section 7 ("the buildable surface is
SMALL because the static grounded core already exists").

Files verified: `data/corpora/binder/binder2016_ratings.csv`, `hdlab/animacy_lexicon.py`,
`hdlab/self_improving_loop.py`, `data/capability_registry.jsonl`,
`data/exp_theory_of_mind_sally_anne_nested_hrr_v1/metrics.json`,
`data/exp_mcguffey_whoaffected_verb_affectedness_gate_v1.py`,
`data/exp_mcguffey_whoaffected_verb_affectedness_gate_v2_heldout/metrics.json`,
`data/substrate_index/meta/atoms.jsonl` (seq 29613-29624), `notes/WHERE_WE_ARE_NOW.md`.
