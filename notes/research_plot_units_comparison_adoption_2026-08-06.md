# Comparison + adoption-plan drill: Lehnert Plot Units vs our goal/outcome/ownership organs

**Filed:** 2026-08-06 by research. Read-only comparison + can-fail empirical test against our own
production code; **no organ was modified**. `hdlab/goal_typing.py` was read but not touched (a
sibling agent is actively editing it -- read-only respected throughout).

**Trigger:** Director-directed COMPARISON + ADOPTION-PLAN drill following USER's greenlight to adopt
prior-art recommendations under a hard discipline: "be clear on EXACTLY what we're pulling in, TEST
it against what we have, in particular verify it's doing things the way WE think they should be done
(brain-foundational, glass-box)." This is the gate before any production-code change.

**Construct under comparison:** Lehnert (1981) Plot Units -- closed M/+/- affect-state alphabet, four
typed causal links (MOTIVATION, ACTUALIZATION, TERMINATION, EQUIVALENCE), structural per-character
ownership, cross-character link types (REQUEST, vicarious ENABLEMENT, vicarious MOTIVATION, SHARED,
MIXED->COMPETITION), 15 primitive units composing into named complex units. Sibling constructs:
TALE-SPIN's per-character goal-list with stored failure-reasons; BORIS's affect-as-goal-status-signal.
Full landscape context (same-day sibling note, not re-derived here): `notes/prior_art_classical_
symbolic_story_understanding_2026-08-06.md`.

**Our organs read end-to-end this cycle** (all read-only, no edits):
`hdlab/goal_owner_select.py` (GoalOutcomeRegister, `directed_goal_outcome_score`,
`select_outcome_owner`, the Tier-3 evaluative/affect bridges), `hdlab/goal_typing.py`
(`congruence_decision`, `CLASS_REGISTRY`/`OPPOSED_PAIRS`, `find_desired_state`, the did-it-happen
occurrence-gate, `goal_congruence_appraisal_type`/Channel B force-dynamics), `hdlab/situation_model_
accumulate.py` (`AccumulateRegister`, `CausalLinkRegister`). Grepped `hdlab/` for any existing
TERMINATION/EQUIVALENCE/vicarious/cross-character construct -- **none found** (the apparent grep hits
were coincidental unrelated tokens: `NO_COMPETITION_MARGIN` in `coreference_resolver.py`, `SUPERSEDES`
in `director_kb.py`'s KB-versioning relation -- verified by reading context, not a Plot-Units analog).

## HEADLINE

**Our goal/outcome/ownership organs are a clean structural match for the CORE of Lehnert's schema
(M-state, per-owner track, ACTUALIZATION->success/failure) -- in fact more mechanized than her
hand-annotated original on that core. The real gap is her CROSS-CHARACTER link vocabulary (vicarious
MOTIVATION/ENABLEMENT, REQUEST, SHARED, MIXED->COMPETITION), which we have zero of; our
`select_outcome_owner` is architected as single-winner-take-all argmax over roster candidates, not a
multi-edge graph-construction step, and this exact gap is what a real cross-character rescue passage
in our own eval set exposed as a can-fail case. A full-44-item empirical translation test found the
REPRESENTATION is not the bottleneck -- COVERAGE is: on `experiments/data/goal_bearing_modern_eval_v1.
jsonl` our polarity organ gets 11/44 (25%) genuinely correct, abstains conservatively on 31/44 (70.5%,
NA/none/ambiguous -- the mechanism declines rather than guesses), and is confidently WRONG on only
2/44 (4.5%) -- a high-precision/low-recall profile whose failure mode is the same
construction/extraction bottleneck the sibling prior-art note already identified as the dominant
50-year failure class in this literature, not a Plot-Units-representation mismatch.**

Per-element verdict counts (12 rows, detailed table below): **ADOPT=2, ADAPT=2, KEEP-OURS=4,
REJECT=2**, plus 2 rows (SUCCESS/FAILURE formula, BORIS affect-signal) folded into KEEP-OURS as
already-equivalent. Plot Units is **not** a wholesale unifying target we're missing -- most of its
primitive vocabulary we already have, independently arrived at and in some respects more rigorously
built (referent-linking tiers, occurrence-gate negation handling, MDL-induced construction typing).
The one part worth pulling in is real and specific: cross-character causal links, which not
coincidentally is also the user's own already-planned next build (ToM/illocutionary force).

P_deflated (confidence this comparison table + empirical numbers correctly characterize our organs'
compatibility with Lehnert's schema): **0.65** -- deflated from a raw ~0.85: the code-read and the
44-item run are both DIRECT, disk-verified evidence (not lit-scan secondary sourcing), but (a) the
can-fail deep-dive (root-causing WHY each polarity/owner mismatch happens) was done by hand on N=3 of
the 44 items, not all of them -- the "goal-clause self-contamination" and "sentence-boundary" bug
classes are diagnosed confidently on those 3, generalized to the aggregate 44-item numbers by
inference, not individually re-verified on every item; (b) Lehnert's own link-type taxonomy detail
(exact MOTIVATION/ACTUALIZATION/TERMINATION/EQUIVALENCE formal definitions) is MED-confidence per the
sibling prior-art note's own citation caveat (original 1981 PDF unreadable this session). Novel-
synthesis P (the "cross-character links should be the next build, and TALE-SPIN/BORIS-style stored
failure-reasons are a cheap wire-in" strategic recommendation) is capped at **0.50** per mandatory
ceiling -- a plausibility read, not a tested claim.

## Per-element comparison table

| # | Plot-Units element | What it is | What WE have | Aligned/Divergent | Brain-mechanism or symbolic convenience? | VERDICT |
|---|---|---|---|---|---|---|
| 1 | **M (mental/goal state)** | Neutral affect-state: character X holds a goal/desire | `R_GOAL` role in `GoalOutcomeRegister`; `type_goal_events`'s union of 3 signals (EXPERIENCER-frame via `frame_primary_role`, purpose-infinitival construction, desiderative/conative/intention partition with negation-scope guard) | ALIGNED -- and richer: Lehnert's M is an undifferentiated single symbol; ours distinguishes bouletic desire / conative attempt / intention-decision (Bratman 1987 three-way split) as sub-signals feeding one role | Brain: PFC prospective-goal representation (rostral PFC held-intention state) | **KEEP-OURS** |
| 2 | **+ / - (positive/negative event, on ONE character's track)** | Any event's raw affect valence to the character it happens to, independent of whether that character has an antecedent goal -- this is what FEEDS MOTIVATION | `R_MET`/`R_UNMET` roles, but ours are **goal-congruence-scoped**: `congruence_decision` only assigns MET/UNMET relative to an already-typed antecedent GOAL (or a flat OOV-lexicon fallback); there is no general "this event is bad for X" appraisal independent of an existing goal -- EXCEPT: `goal_congruence_appraisal_type`'s branch-2 (Talmy force-dynamics agonist-realized/blocked reading of a bare clause) is exactly this, but it lives in the Channel-B word-acquisition pathway (`hdlab/word_acquisition_loop`), not wired into `GoalOutcomeRegister`/`select_outcome_owner` | DIVERGENT -- Lehnert's +/- is more general-purpose than ours (it's what GENERATES M states via MOTIVATION); we have the raw-valence primitive already built, just unwired to this pathway | Brain: amygdala/OFC continuous valence appraisal of perceived events, prior to and independent of explicit goal-state -- this is the appraisal step that would ground the user's own reward-PE grounding pivot (pfc_gate_cfrpe) | **ADAPT** (wire `goal_congruence_appraisal_type`'s force-dynamics branch as the general event-valence generator for the narrative pipeline, not build a new one) |
| 3 | **MOTIVATION link (- -> M)** | A negative event on one track CAUSES a new goal-state (on the same or another character's track) | Nothing -- every GOAL we type comes directly from explicit desiderative/purposive/experiencer-frame lexis in the goal-holder's own clause; we never DERIVE a new goal from a preceding negative event | DIVERGENT (real gap) | Brain: negative-outcome PE -> approach/avoidance goal formation (amygdala/OFC -> PFC) -- directly on the user's own reward-PE grounding roadmap | **ADOPT** (half-built: item 2's force-dynamics primitive is the "-" detector; missing piece is a goal-FORMATION rule consuming it) |
| 4 | **ACTUALIZATION link (M -> + or M -> -) / SUCCESS = M-act->+ / FAILURE = M-act->-** | A goal-state is satisfied or blocked by a later event, via a typed causal link | `directed_goal_outcome_score` (does THIS candidate's own antecedent GOAL connect to the outcome event) + `congruence_decision` (referent-linking tiers: literal/pronoun-coref/shared-feature, class-registry same/opposed-pole comparison, negation occurrence-gate, verb-recurrence channel) | ALIGNED -- and more rigorous: Lehnert hand-annotated this per passage; ours computes referent identity, verb-class relatedness, and negation-scope programmatically | Brain: OFC/vmPFC expected-vs-obtained outcome evaluation (reward-prediction-error sign) -- matches the user's own audit language ("outcome-VALUATION, OFC content-blind") | **KEEP-OURS** |
| 5 | **TERMINATION link (a later event supersedes/negates an earlier state's affect, backward)** | Fortuitous resolution or loss WITHOUT the character's own actualization -- order-sensitive supersession of an already-resolved state | `GoalOutcomeRegister.appraise()` only TALLIES `n_unmet` vs `n_met` counts (`goal_blocked = n_unmet > n_met`) -- a majority-vote over all recorded events, NOT order-sensitive "does event_k+1 supersede event_k's affect" | DIVERGENT (real gap, distinct from #3 and #4) | Brain: situation-model belief-revision / event-segmentation update (a new event can override the affective interpretation of a prior state) -- well-established, brain-plausible | **ADOPT** |
| 6 | **EQUIVALENCE link (redundant-description merge)** | Two surface descriptions of the SAME event get merged so a symbolic graph doesn't double-count a node | No direct analog; our register is a superpositional (FHRR bundle) accumulate, not an explicit symbolic node/edge graph -- a repeated mention re-binds and bundles rather than needing "de-duplication of a node" | Not directly comparable -- this is a housekeeping artifact of Lehnert's explicit-graph representation, not a gap in ours | Symbolic convenience (graph-construction bookkeeping), not a brain mechanism in its own right | **REJECT** (as a distinct link-type; if repeated-mention dilution of bundle-cleanup margins ever becomes measurable, that's a de-duplication fix to the existing register, not a new link type) |
| 7 | **Ownership = structural (which character's track a node sits on)** | Every affect-state lives on ONE character's own timeline by construction | `GoalOutcomeRegister` is keyed per-entity; `select_outcome_owner` explicitly ENUMERATES every roster entity as a candidate, scores each with a fresh per-candidate register, argmaxes, tie-breaks by goal/outcome theme overlap | ALIGNED -- and more mechanized: Lehnert assigned ownership at annotation time; ours is a live candidate-enumeration + selection procedure | Brain: this is the entity-indexing dimension of Zwaan's event-indexing model (protagonist tracking) | **KEEP-OURS** |
| 8 | **Cross-character links: REQUEST (M/M), vicarious ENABLEMENT (+/M), vicarious MOTIVATION (-/M), SHARED (same-polarity both tracks), MIXED (opposite-polarity -> COMPETITION)** | A typed edge connecting TWO characters' tracks for the same underlying event | **Nothing.** `select_outcome_owner` is single-winner-take-all: it treats "who owns this outcome" as ONE argmax over competing candidates, never as a graph where several characters can simultaneously hold genuinely-linked (not competing) nodes for the same event | DIVERGENT -- largest structural gap found this cycle | Brain: multi-agent Theory-of-Mind (mentalizing network, TPJ/mPFC) -- one agent's action changing/being caused by another's goal-state | **ADOPT (highest priority)** -- see can-fail case below; this is also the user's own already-planned next build (ToM/illocutionary force) |
| 9 | **15 primitive units -> named complex units (COMPETITION, RETALIATION, DOUBLE-CROSS, HONORED/DENIED/BUNGLED REQUEST, SACRIFICE, FLEETING SUCCESS...)** | A catalog of recognizable subgraph SHAPES over the primitive M/+/- + 4-link vocabulary | Nothing, and nothing SHOULD be hand-built here | Once #3 (MOTIVATION), #5 (TERMINATION), and #8 (cross-character links) exist, these named units are pattern-matchable subgraphs, not a new mechanism -- exactly the TAU-style abstract-pattern-matching the sibling prior-art note flagged as adoptable via VSA similarity search rather than hand-coded rules | Purely symbolic-convenience catalog once the primitives exist | **REJECT** (do not hand-build a "COMPETITION detector"; it should fall out of #3+#5+#8 via similarity search once those land) |
| 10 | **TALE-SPIN's per-character goal-list with STORED FAILURE-REASONS** | Each goal object carries not just SUCCEEDED/FAILED but WHY | `congruence_decision`'s `detail` dict already computes a reason (`opposed_class_same_referent`, `referent_mismatch`, `verb_class_unrelated`, occurrence-gate fired/not) PER CALL, but this is computed-then-discarded -- never accumulated into the entity's persistent `GoalOutcomeRegister` state as a durable blocking-cause | Partially aligned -- the reasoning already exists, it's just not promoted into persistent per-entity state | This is a wire-don't-island opportunity, not a new mechanism | **ADAPT** (thread `congruence_decision`'s detail dict into `appraise()`'s return as a stored blocking-cause) |
| 11 | **BORIS's affect-as-goal-status-signal** | A tally of a character's accumulated affect events serves as a readout of their goal status | `appraise()`'s `has_goal`/`n_unmet`/`n_met`/`goal_blocked` tally IS this, already | ALIGNED | Same as #4/#7 -- readout of the same accumulated register | **KEEP-OURS** (no action; this row exists to confirm the sibling construct isn't a separate gap) |
| 12 | **QUALM's "goal orientation" as a first-class QA target (context, not a build target this cycle)** | 1970s convergent confirmation that goal-outcome tracking is its own QA category, not incidental to general causal QA | Out of scope for this drill (QA-layer, not representation) -- noted for completeness per the sibling prior-art note's own Focus-Question-3 ranking (QUEST's arc-search is priority #4, secondary to representation-building) | N/A | N/A | **N/A (no action)** |

## THE CAN-FAIL TEST -- our organs' actual output run against `goal_bearing_modern_eval_v1.jsonl`

**Full 44-item run** (not a hand-picked N=3 -- the deep dives below explain the mechanism behind the
aggregate numbers):

- **Owner selection** (`select_outcome_owner`): 22/44 correct overall (50%); but 18/44 (41%) raise
  `OUTCOME_NEVER_TYPED` (`select_outcome_owner` cannot even attempt a pick -- the outcome slot never
  gets typed for ANY roster candidate). Of the 26 items that could be scored at all, **22/26 = 84.6%
  correct** -- when the mechanism has SOMETHING to work with, owner selection is strong.
- **Outcome polarity** (`congruence_with_lexicon_fallback`): **11/44 correct (25%)**, **31/44 abstain
  (70.5%** -- NA/none/ambiguous, i.e. the mechanism conservatively DECLINES rather than guesses**)**,
  **2/44 confidently WRONG (4.5%)**. High-precision/low-recall profile.

This is the compatibility finding: **the REPRESENTATION is not what's bottlenecking these numbers.**
Every item's role_seq/cluster_ids output IS already shaped exactly like Lehnert's per-owner M/+/-
track with an actualization link (a temporally-ordered list of `(role, owner)` pairs, directly
re-expressible as her notation with zero new slots needed for the 22/26-scoreable owner cases). What's
low is COVERAGE (41% of items never get an outcome typed at all -- a lexical/construction gap, the
exact class-1 knowledge-acquisition-bottleneck failure mode the sibling prior-art note already
identified as this literature's dominant terminal failure) and, on the items that DO get scored, two
distinct concrete bug classes surfaced by hand-tracing 3 representative items:

**Case A -- `lw_ice_rescue_amy` (gold owner=amy, gold polarity=met; a genuine cross-character rescue
passage: Jo attempts and fails to help; Amy falls through ice; Laurie and Jo together rescue "the
child"):** `select_outcome_owner` returns `amy` -- matching gold -- but for the WRONG reason.
Instrumented trace: `type_goal_events` on the outcome sentence ("Jo dragged a rail... got the child
out...") returns `[]` for **every** roster candidate (jo/laurie/amy) -- "the child" never resolves to
Amy (no coreference beyond gender-marked pronouns). Because the outcome sentence types nothing, all
three candidates' `role_seq`/`cluster_ids` collapse to the IDENTICAL sequence drawn entirely from the
GOAL-clause sentences ("her voice was gone", "her feet had no strength" -- Jo's own failed
micro-attempts), and a Tier-2 open-vocab scan on one of those goal-clause tokens spuriously types an
`OUTCOME_UNMET` bound to **jo** (not the hypothesized candidate at all). `directed_goal_outcome_score`
then scores all three candidates identically at 1.0 (jo genuinely has an earlier GOAL, and that
mid-passage `OUTCOME_UNMET` -- itself a misfire -- is what `_outcome_pos` latches onto). The
content-coherence tie-break finds no theme overlap for any candidate and falls through to
**alphabetical sorted-order** (amy < jo < laurie), which is how "amy" wins. **This is the exact
manifestation of table-row #8's gap**: this passage needs a vicarious-MOTIVATION link (Amy's fall
motivates Jo's rescue attempt) and a vicarious-ENABLEMENT link (Jo+Laurie's joint action enables Amy's
positive resolution) -- a genuine 2-character causal structure our single-winner-argmax cannot
represent even in principle. The correct-looking answer is an artifact, not a capability.
- **CAN-FAIL, not a rescue for our confidence**: swap the roster so the alphabetically-first name is
  NOT the correct answer (e.g. relabel Amy as "Zara") and this passage should flip to a WRONG answer
  for the same reason -- a decisive discriminator to run before trusting this class of item.

**Case B -- `lw_jo_laurie_snowball` (gold owner=jo [correct], gold polarity=met, our polarity=UNMET
[a genuine flip]):** owner selection is correct and clean (jo has the only typed GOAL, laurie scores
0.0). The polarity flip traces to the sentence-splitter's dialogue-quote handling: the true resolving
clause ("the head turned at once. Laurie opened the window...") types nothing under Tier-1/Tier-2, so
the primary `congruence_outcome_valence_windowed` abstains and the fallback lexicon path reads the
FINAL trailing dialogue fragment ("I've had a bad cold, and been shut up a week") -- Laurie describing
his own illness, unrelated to whether Jo's overture succeeded -- and a Tier-2 similarity hit on
"shut"-like vocabulary types it UNMET. This is an extraction/segmentation bug (which clause counts as
"the outcome"), not a representation mismatch; Lehnert's schema doesn't force this failure, her
hand-annotation simply never had to solve it automatically.

**Case C -- `lw_jo_wanted_forgive_amy` (gold owner=jo, gold polarity=unmet, negation-sensitive):**
owner selection ties jo/amy/march at 1.0 (a milder version of Case A's contamination -- goal-clause
vocabulary like "grief and anger" plausibly trips outcome-polarity scans); polarity abstains (NA) --
conservative, not wrong, consistent with the aggregate 70.5% abstain rate.

**Verdict on the can-fail test:** clean translation at the STRUCTURAL/representation level (owner and
polarity, when typed, are already Lehnert-shaped); genuine mismatches are (1) a coverage/construction
bottleneck (41% of items never get an outcome typed -- matches the historical literature-wide failure
mode) and (2) the missing cross-character link vocabulary (table row #8), vividly exposed by Case A
rather than merely inferred. Reported honestly per instruction, not glossed: Case A's "correct" answer
should NOT be read as evidence the mechanism handles rescue/indirection passages -- it doesn't yet.

## Adoption plan -- ADOPT + ADAPT elements only

**1. ADOPT -- cross-character causal links (table row #8, highest priority).**
- Organ change: extend `select_outcome_owner`'s single-argmax selection into a small typed-edge
  layer: when `directed_goal_outcome_score` ties across >1 candidate AND the outcome sentence's
  structural subject differs from the tied goal-holder(s), emit a typed cross-character edge (vicarious
  MOTIVATION if the goal-holder's antecedent trigger was another character's negative event; vicarious
  ENABLEMENT if the tied candidates jointly co-occur as agents in the outcome clause) INSTEAD OF
  falling through to the alphabetical tie-break. This reuses `GoalOutcomeRegister` per-entity registers
  unmodified -- it's a new EDGE-typing function reading two already-built registers, not a new binding
  primitive.
- Can-fail acceptance test: construct a roster-relabeling probe on `lw_ice_rescue_amy`-shaped items
  (swap which entity is alphabetically first) -- HARD-PASS iff owner selection stays correct across
  relabelings (proves the edge-typing, not alphabetical luck, drives the pick); HARD-FAIL if accuracy
  drops to roster-order-dependent chance on the relabeled set.

**2. ADOPT -- TERMINATION link / order-sensitive supersession (table row #5).**
- Organ change: extend `GoalOutcomeRegister.appraise()` beyond the current `n_unmet > n_met` tally to
  an order-aware readout: if the LAST-recorded MET/UNMET event for an entity is a different polarity
  than an earlier one, report the later event's polarity as authoritative (with the earlier one
  demoted to `superseded=True` in the returned dict), rather than a symmetric count comparison.
- Can-fail acceptance test: hand-author 6-8 items where an early resolution is explicitly reversed by
  a later event ("she won the race, but was later disqualified") vs. matched controls with no reversal
  -- HARD-PASS iff order-aware readout beats the current tally-based readout on the reversal subset
  without regressing the non-reversal subset; HARD-FAIL if the two readouts never diverge on any
  constructed item (would mean the reversal pattern doesn't actually occur in the tally-collision
  cases this fix targets, i.e. the fix is solving a non-problem).

**3. ADAPT -- wire `goal_congruence_appraisal_type`'s force-dynamics branch as the general event-valence
generator, then use it to drive MOTIVATION-link goal formation (table rows #2 + #3 combined).**
- Organ change: (a) expose `goal_congruence_appraisal_type`'s branch-2 (implicit force-dynamics
  agonist-realized/blocked reading, currently reachable only via Channel B / `word_acquisition_loop`)
  as a standalone `raw_event_valence(clause) -> POS/NEG/None` call usable from the narrative
  goal/outcome pipeline; (b) when `raw_event_valence` returns NEG for a clause with an animate agent
  who has NO already-typed GOAL, hypothesize a new GOAL event for that agent (the MOTIVATION link).
- Can-fail acceptance test: on a held-out probe of clauses where a character suffers harm with no
  antecedent lexical desiderative marker (the exact TALE-SPIN "Henry Ant drowns" class), HARD-PASS iff
  the induced-goal-holder matches the gold goal-holder at a rate clearly above the base rate of the
  roster size (e.g. >1/|roster| by a wide margin, pre-registered per envelope-fail-bands); HARD-FAIL if
  performance is at chance -- would refute the "half the primitive already exists, just needs wiring"
  claim in row #2/#3 and mean a genuinely new detector is needed, not a wire-in.

**4. ADAPT -- thread `congruence_decision`'s reason/detail into a persistent per-entity blocking-cause
(table row #10, TALE-SPIN-style stored failure-reasons).**
- Organ change: `GoalOutcomeRegister.appraise()` gains an optional `blocking_cause` field populated
  from the `detail` dict already computed by `congruence_decision` at the call site that typed the
  UNMET event (opposed-class verb + referent, or occurrence-gate-negated recurrence) -- pure
  plumbing, no new inference.
- Can-fail acceptance test: on the subset of the 44-item eval where our polarity organ already gets
  UNMET correct, HARD-PASS iff the stored `blocking_cause` names a verb/referent a human annotator
  would independently point to as "why it failed" for >=80% of that subset (spot-checked by hand, small
  N is fine -- this is a plumbing correctness check, not a discovery claim); HARD-FAIL if the stored
  cause is uninformative/generic on the majority (would mean `congruence_decision`'s detail dict isn't
  actually rich enough to serve as a failure-reason, a scoping correction to make before wiring further).

## KEEP-OURS / REJECT -- explicit, with reasons

- **KEEP-OURS:** M/goal-state typing (row #1) -- ours is a richer 3-signal union (experiencer-frame +
  purpose-infinitival + desiderative/conative/intention triad with a negation-scope guard) than
  Lehnert's flat symbol. **Do not adopt her undifferentiated M.**
- **KEEP-OURS:** ACTUALIZATION / SUCCESS-FAILURE (row #4) -- ours computes referent-linking tiers,
  verb-class same/opposed-pole comparison, and a negation occurrence-gate programmatically; Lehnert's
  was hand-annotated per passage with no such machinery. **Do not adopt her actualization test; ours is
  already more mechanized on the identical formal shape (M -> +/- via a legality check).**
- **KEEP-OURS:** Ownership-by-track (row #7) -- `GoalOutcomeRegister` keyed per-entity plus explicit
  candidate enumeration + argmax + content-coherence tie-break is structurally identical to, and more
  mechanized than, Lehnert's per-annotation-time track assignment.
- **KEEP-OURS:** BORIS's affect-as-goal-status-signal (row #11) -- already exactly what
  `appraise()`'s `has_goal`/`n_unmet`/`n_met`/`goal_blocked` tally computes; no separate construct to
  pull in.
- **REJECT:** EQUIVALENCE link (row #6) -- a symbolic-graph node-deduplication artifact specific to
  Lehnert's explicit node/edge representation; our FHRR accumulate-register doesn't have "duplicate
  nodes" in the same sense, and if repeated-mention bundle-dilution ever becomes a measured problem,
  the fix belongs to the existing register (a de-duplication guard on repeated same-slot writes), not a
  new link-type import.
- **REJECT:** the 15-primitive -> named-complex-unit catalog (row #9, COMPETITION/RETALIATION/
  DOUBLE-CROSS/etc.) -- not a brain mechanism in its own right; once rows #3 (MOTIVATION), #5
  (TERMINATION), and #8 (cross-character links) are built, these are pattern-matchable subgraph SHAPES
  over primitives we'll already have, recognizable via similarity search rather than hand-coded
  detectors (consistent with the sibling prior-art note's own TAU-style-pattern-matching
  recommendation). **Do not hand-build a COMPETITION/RETALIATION detector as a standalone unit.**

**Does Plot Units add anything we don't already have?** Mostly no on the core primitive vocabulary
(rows #1, #4, #7, #11 are KEEP-OURS -- we independently arrived at an equal-or-more-mechanized version
of Lehnert's M/actualization/ownership/affect-signal core). It adds exactly one thing of real,
specific value: the cross-character link vocabulary (row #8), which is both a genuine gap (proven by
Case A, not merely asserted) and independently the user's own next-planned build (ToM/illocutionary
force) -- external validation from a 45-year-old, independently-arrived-at symbolic design that this
is the right next brain-mechanism to build, not a redirection.

## Cheap decisive test

The roster-relabeling probe described in Adoption-plan item 1 (swap the alphabetically-first entity in
`lw_ice_rescue_amy`-shaped rescue/indirection items and re-run `select_outcome_owner`) is the single
cheapest test that would separate "our organ genuinely handles cross-character indirection" from "it
got lucky on alphabetical tie-break fallback" -- costs ~30 minutes (roster dict edit + re-run, no new
mechanism needed to RUN the test, only to fix what it will very likely expose).

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS (representation compatibility, generalization of the N=3 deep-dive):** on a full
  re-run of all 44 items with per-item mechanism tracing (not just the aggregate pass/fail counted
  above), the role_seq/cluster_ids output for every item that DOES get an outcome typed (the 26/44
  owner-scoreable, 13/44 polarity-scoreable-or-flip subset) is losslessly re-expressible as Lehnert
  M/+/- per-owner tracks with a legal ACTUALIZATION link, with zero items requiring a new slot/link
  type beyond MOTIVATION/TERMINATION/cross-character (i.e. the three ADOPT/ADAPT gaps already named
  above are exhaustive, not a partial list).
- **HARD-FAIL (representation compatibility):** if that full re-run finds an item requiring a
  genuinely new slot/link type NOT among {MOTIVATION, TERMINATION, cross-character (REQUEST/vicarious
  ENABLEMENT/vicarious MOTIVATION/SHARED/MIXED)}, that would mean this comparison's per-element table
  is incomplete and should be re-opened, not patched ad hoc.
- **HARD-PASS (Case A generalizes):** the roster-relabeling probe (cheap decisive test above), run on
  Case A plus at least 2 more hand-authored rescue/indirection items, finds owner selection flips to
  WRONG on a majority of relabelings -- confirms the alphabetical-tie-break-as-lucky-artifact diagnosis
  is real and not a one-off misreading of a single trace.
- **HARD-FAIL (Case A does NOT generalize):** if owner selection stays correct across relabelings on
  all 3 items, that would mean some OTHER signal (not alphabetical order) is actually doing the work in
  Case A, and the "correct answer for the wrong reason" diagnosis above should be retracted and
  re-traced, not assumed.
- **HARD-PASS (adaptation #3, force-dynamics MOTIVATION wire):** on a held-out no-antecedent-goal
  harm-clause probe (TALE-SPIN-class items), the induced-goal-holder accuracy clears
  1/|roster|-by-a-wide-margin (pre-registered envelope-fail-band, per standing experiment-design
  discipline) -- validates "half the MOTIVATION primitive already exists, just needs wiring."
- **HARD-FAIL (adaptation #3):** induced-goal-holder accuracy is statistically indistinguishable from
  1/|roster| chance -- refutes the wire-in claim; MOTIVATION-link goal-formation would need a genuinely
  new detector, reclassifying row #2/#3 from ADAPT to full ADOPT (higher cost than currently
  estimated).

## Cross-thread synthesis

Sits directly downstream of the same-day sibling `notes/prior_art_classical_symbolic_story_
understanding_2026-08-06.md`, which surveyed the broader classical-symbolic + cognitive-comprehension
lineage and concluded (a) the goal/outcome/ownership REPRESENTATION shape is well-precedented and
close to right across three independently-converging designs (Yale AI, Lehnert, Trabasso/van den
Broek), and (b) the historically dominant failure mode across the ENTIRE 50-year lineage is automatic
CONSTRUCTION of that representation from raw text, never the representation's design. This drill's
empirical can-fail numbers (41% owner-untypeable, 70.5% polarity-abstain, only 4.5% confidently wrong)
are a direct, concrete confirmation of exactly that historical pattern IN OUR OWN SYSTEM: precision is
fine, coverage is the wall, matching a 50-year-old, independently-repeated finding rather than being a
novel problem specific to this substrate. The one place this drill goes BEYOND the sibling landscape
survey is identifying that our single biggest STRUCTURAL (not coverage) gap -- cross-character links
-- is both real (Case A) and already the user's own next-planned build, giving two independent lines
of evidence (this drill's can-fail test, and the user's own standing brain-mechanism-audit priority)
converging on the same next step.

## Substrate-product implications

No organ was changed this cycle (read-only comparison per the OPS instruction). The product-relevant
takeaway: continued investment in the goal/outcome/ownership representation's CORE (M-typing,
actualization, ownership) is validated as near-ceiling relative to a 45-year-old independently-derived
prior design -- not a place to spend more redesign effort. The two genuine near-term opportunities are
(1) a cheap wire-don't-island move (adaptation #3, exposing the already-built force-dynamics primitive
to the narrative pipeline) and (2) the higher-value, higher-cost cross-character link layer (adoption
#1), which the can-fail test shows is not a nice-to-have -- it is why a real rescue passage got the
right owner for an artifactual (alphabetical) reason rather than a principled one, meaning our current
confidence on any passage resembling Case A's shape is currently miscalibrated (looks like a pass,
isn't structurally one). The coverage bottleneck (31/44 abstain) is NOT something this comparison
recommends chasing via Plot-Units adoption -- Lehnert's own system solved coverage only via
hand-annotation, so her design offers no lever on it; that remains a separate, already-tracked
extraction/grounding problem per the sibling prior-art note.

## Citations (verified count)

**0 new external citations fetched this cycle** -- this drill is an internal code-comparison + an
empirical run against our own eval data, not a literature scan. All Lehnert/TALE-SPIN/BORIS/Trabasso
citation verification was done in the same-day sibling note (`notes/prior_art_classical_symbolic_
story_understanding_2026-08-06.md`: 9 HIGH-confidence WebSearch-verified + 12 MED-confidence
training-memory citations) and is reused by reference here, not re-verified independently this cycle
(a real, acknowledged limitation folded into the P_deflated figure above).

**Internal primary sources read end-to-end this cycle (disk-verified, not summarized from memory):**
`hdlab/goal_owner_select.py` (890 lines), `hdlab/goal_typing.py` (1691 lines, full read across 2
pages), `hdlab/situation_model_accumulate.py` (234 lines), plus a live interactive run of
`select_outcome_owner` / `build_candidate_role_seq` / `congruence_with_lexicon_fallback` against all
44 items of `experiments/data/goal_bearing_modern_eval_v1.jsonl` and a hand-instrumented trace of 3
representative items (Cases A/B/C above).

## Bottom line

Plot Units does not turn out to be a wholesale unifying target we're missing -- most of its primitive
vocabulary (M-typing, actualization/success-failure, structural ownership, affect-as-status-signal) we
already have, independently arrived at, and in several respects more mechanized than Lehnert's
hand-annotated 1981 original. It adds exactly one real, specific, well-evidenced thing: cross-character
causal links (vicarious MOTIVATION/ENABLEMENT and friends), proven necessary (not merely plausible) by
a real rescue passage in our own eval set where the mechanism got the right owner for an artifactual
reason. Two cheaper wire-don't-island adaptations (exposing the already-built force-dynamics
raw-event-valence primitive to the narrative pipeline; threading the already-computed
congruence-decision reason into persistent per-entity state) round out the actionable list. Everything
else in Lehnert's schema is either already equivalent to what we have (KEEP-OURS) or a symbolic-graph
housekeeping convenience with no brain-mechanism content of its own (REJECT).
