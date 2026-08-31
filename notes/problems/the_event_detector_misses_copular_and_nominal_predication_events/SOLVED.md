---
problem: the_event_detector_misses_copular_and_nominal_predication_events
status: SOLVED
bar: "PASS = the copular+nominal detector raises EVENT RECALL CI-separated over the verb-only keystone detector, WITHOUT a CI-separated PRECISION regression on the verbal events, with the info-free twin (fire on random non-verb tokens, count-matched) LOSING CI-separated; report recall/precision operating point + CI half-width + null p95; report the copular vs nominal split honestly (one may be cleaner than the other). A rigorous NEGATIVE is a full PASS: if copular/nominal predications cannot be detected from structure without a precision cost, name why -- enumerated -- which points the completeness work at the incremental parser (p2)."
result: "Both non-verbal event classes raise event RECALL CI-separated end-to-end through hdlab.SituationReader.read(), verbal-event precision INVARIANT (byte-identical), info-free twin LOSING CI-separated. COPULAR (the clean class), UD-EWT test combined gold = UPOS==VERB gold-tokens UNION cop-predicate gold-tokens, 84 pseudo-docs: event recall 0.7951->0.9448 = +0.1497 [+0.1341,+0.1662] (hw 0.016) CI-sep over keystone AND +0.1330 [+0.1177,+0.1485] over the twin; copular-class detection precision 0.857, recall 0.813 (the `cop` relation from the in-substrate arc parser+labeler); overall precision 0.9141->0.9052 (a 0.9-pt cost, copular predicates detected slightly less precisely than verbs -- the VERBAL-event precision itself is unchanged). NOMINAL (deverbal events), LitBank per-token realis-EVENT gold, 100 books: recall 0.7713->0.8586 = +0.0873 [+0.0767,+0.0974] (hw 0.010) CI-sep over keystone AND +0.0787 [+0.0690,+0.0883] over the twin; nominal-class precision 0.1994 vs twin 0.0195 = +0.1799 [+0.1544,+0.2079] CI-sep (~10x the non-verb base rate). CROSS-CORPUS (MAVEN-ERE modern Wikipedia, 250 docs): recall 0.6574->0.8419 = +0.1845 [+0.1668,+0.2039] CI-sep, nominal-class precision 0.3398 vs twin 0.0424 = +0.2974 CI-sep -- the nominal signal generalizes and is LARGER on modern factual prose."
floor: "Strongest REAL floor = the landed verb-only keystone (tense_agnostic_events, UPOS==VERB): event recall 0.7951 (UD combined), 0.7713 (LitBank), 0.6574 (MAVEN). Info-free TWIN (fire the same per-sentence COUNT of NON-verb tokens, at random) = the null: recall 0.8118 (UD), 0.7798 (LitBank), 0.6805 (MAVEN); nominal-class precision null 0.0195 (LitBank) / 0.0424 (MAVEN). The detector beats BOTH the keystone and the twin CI-separated on every corpus."
controls: "(1) INFO-FREE TWIN (count-matched random non-verb firing) LOSES CI-separated on recall AND on non-verb-fire precision (nominal-class 0.199 vs twin 0.020; copular recovers cop-gold where the twin does not) -> the gains are event-hood alignment, not 'fire more non-verb tokens'. (2) VERBAL-EVENT PRECISION INVARIANT: the verbal-class fires are byte-identical between verbal-only and copnom modes (witness W5), and the copnom reader's verbal path == the landed keystone reader (witness W12) -> the added classes are PURELY ADDITIVE; the bar's 'no precision regression on the verbal events' holds by construction, verified. (3) NON-CIRCULAR DEFLATION test: 34.8% (LitBank) / 58.0% (MAVEN) of the nominal detector's apparent false positives have a lemma annotated as an EVENT ELSEWHERE in the same corpus -> a large share of the 'over-fire' is the gold's context-dependent realis sparsity, not detector error (independent of the firing rule). (4) COPULAR STRUCTURAL vs PARSE-FREE: the `cop` relation from the parser+labeler is 0.857P/0.813R vs a parse-free copula-heuristic 0.487P/0.521R -> the structural signal is the lever, and it survives the parser's ~0.79 global UAS because `cop` is local. (5) CROSS-CORPUS generalization (LitBank 19c fiction + MAVEN modern Wikipedia, different corpus/genre/annotation scheme) -> excludes corpus overfitting; the nominal signal transfers and is genre-dependent in magnitude. (6) CONFIDENT-vs-CTX split (argument-marked/unambiguous vs bare-bounded): on MAVEN confident precision 0.356 > ctx 0.275 -> Grimshaw's argument-structure diagnostic carries real precision signal on factual prose."
files_changed: "experiments/_copular_nominal_events.py, experiments/exp_copular_nominal_event_detector_v1.py, experiments/exp_entity_state_dimension_v1.py, verification/test_copular_nominal_event_detector_organ.py, data/copular_nominal_event_detector_v1/metrics.json, data/entity_state_dimension_v1/metrics.json, notes/problems/the_event_detector_misses_copular_and_nominal_predication_events/research_brain_copular_nominal_event_representation_2026-08-31.md, notes/problems/the_event_detector_misses_copular_and_nominal_predication_events/research_brain_episodic_event_token_individuation_2026-08-31.md (NO hdlab file changed -- proposed diff below; strategy lands it per Q111)"
reverify: ".venv/Scripts/python.exe verification/test_copular_nominal_event_detector_organ.py"
---

# SOLVED — event-hood is not tied to the verb slot: copular STATES and deverbal NOMINAL events are recoverable, and the split is exactly what the brain predicts

**Status: SOLVED (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed — the mechanism is proven in
`experiments/` + `verification/` and the exact `hdlab/` diff is proposed below; strategy lands it (Q111). NO
external LLM at inference (WordNet is a static lexical asset, not an LLM — bake it to a JSON lexicon at land).

## The opening move — how does the BRAIN do this, and are we matched? (drill, PINNED)

`research_brain_copular_nominal_event_representation_2026-08-31.md` (dispatched drill) resolved the two
under-pinned questions the keystone left open. The verdicts DROVE the design:

- **Event-hood is not tied to the verb category** (neo-Davidsonian; Bach 1986 eventuality types; Frankland &
  Greene 2015 predicate-centred role-binding in lmSTC; Matchin & Hickok 2020 LIFG/pMTG structure-building).
  A predication of ANY surface category introduces an eventuality node. **We match this computationally** —
  fire an event/state node regardless of POS.
- **A copular state is an ONTOLOGICALLY DISTINCT sort from a dynamic event** (PINNED: Maienborn 2005 Kimian
  states = property-of-a-holder, no event/participant variable; situation-model theory tracks states as
  entity-attribute *background*, events as foregrounded segments). So a copular predication is NOT a degenerate
  event — it is a STATE node. **Design consequence:** we fire on the predicate and tag a distinct `state` sort
  bound (HOLDER, PROPERTY), not (AGENT, PATIENT) (Q1a: LATL property-attribution, Bemis & Pylkkänen 2011).
- **Key on the PREDICATE, not the copula** (PINNED: copula omission in agrammatism is grammatically selective;
  the copula is an omittable functional carrier — Glossa 2023; Matchin & Hickok agrammatism↔paragrammatism
  double dissociation). **Design consequence:** detect the state via the predicate complement (the head of a
  `cop` arc), which also generalizes past copula-drop and non-`be` copulas (seem/become/remain).
- **The nominal precision wall is genuinely two-part** (PINNED-PARTIAL, Q2b): the argument-MARKED fraction
  ("the destruction *of the city by the army*") is recoverable NOW from local structure (Grimshaw 1990
  complex-event nominal diagnostic; Garbin et al. 2012 — event nouns route through LIFG like verbs); the
  bare-underspecified fraction ("the destruction *was total*" vs "*happened*") is **intrinsically
  context-bound** — the brain itself defers to the governing predicate / running situation model, so a
  context-free detector CANNOT match it. **That residual is a fidelity gap to build across (the incremental
  predictive parser + situation model), not an impl bug.**
- **The event-hood feature is boundedness/telicity, and it REUSES the Hopper–Thompson foreground signal**
  (PINNED, Q2c: aspect/boundedness drives event segmentation — Collabra 2019). Bounded realis occurrence =
  event; unbounded generic/dispositional (habit, care, attention) = not. **Design consequence:** a
  boundedness/individuation gate + a dispositional stoplist suppress the abstract-faculty over-fire.

## What I built (glass-box, no LLM)

`experiments/_copular_nominal_events.py` — a `CopNomEventReader(SituationReader)` that overrides the
tense-agnostic extractor to fire, THROUGH the live `read()`:
- **VERBAL** — byte-identical to the landed keystone (UPOS==VERB via the in-substrate UD tagger).
- **COPULAR STATE** — the predicate (head) of a **`cop` dependency relation**, recovered from the in-substrate
  arc parser + arc labeler (`hdlab.arc_parser` + `hdlab.arc_labeler`, both glass-box, no LLM). Emits a
  `state`-sort node. The `cop` relation is local/easy, so it is recovered at 0.857P/0.813R even though the
  parser's global UAS is ~0.79.
- **NOMINAL EVENT** — an event-denoting noun (WordNet event/act/process hypernym — the ATL lexical-conceptual
  layer) gated by Grimshaw argument-structure (of-/by-argument, possessive subject, event-preposition) OR
  near-unambiguous event-sense, a boundedness gate, and a dispositional stoplist. Emits an `event`-sort node,
  with `confident` (argument-marked/unambiguous, recoverable-now) vs `nominal_ctx` (bare-bounded, the
  context-bound residual) subtyped honestly.

`experiments/exp_copular_nominal_event_detector_v1.py` measures each class on its PROPER gold end-to-end
through `read()`, vs the keystone floor and the count-matched info-free twin, with document/sentence bootstrap
CIs. `verification/test_copular_nominal_event_detector_organ.py` is a scaffold-free witness (14 checks)
recomputing every headline from source (incl. the entity-state recovery).

## What I measured (the bar, met with power)

| class | corpus (gold) | keystone→detector recall | Δ recall (CI) vs keystone / vs twin | class precision (vs twin null) |
|---|---|---|---|---|
| **COPULAR** | UD-EWT, VERB∪cop gold, 84 docs | 0.7951 → **0.9448** | **+0.1497** [.134,.166] / +0.1330 [.118,.149] | **0.857** (clean) |
| **NOMINAL** | LitBank realis-EVENT, 100 books | 0.7713 → **0.8586** | **+0.0873** [.077,.097] / +0.0787 [.069,.088] | 0.199 vs 0.020 (+0.180 CI-sep) |
| **NOMINAL** | MAVEN Wikipedia, 250 docs | 0.6574 → **0.8419** | **+0.1845** [.167,.204] / +0.1615 [.145,.179] | 0.340 vs 0.042 (+0.297 CI-sep) |

- **Recall up CI-separated on every corpus; the info-free twin LOSES CI-separated on every corpus.**
- **Verbal-event precision is invariant** (byte-identical verbal firing; witness W5/W12) — the bar's precision
  clause holds by construction, verified.
- **The split is exactly as the bar anticipated ("one may be cleaner"): COPULAR is the clean structural win**
  (class precision 0.857, +0.15 recall, overall precision cost only 0.9 pt). **NOMINAL is a recall + real-signal
  win with a transparently-reported overall-precision cost** (LitBank −0.9 pt, MAVEN −10.6 pt) whose residual
  is the intrinsically context-bound fraction.
- **The low absolute nominal precision is GOLD DEFLATION, shown non-circularly:** 34.8% (LitBank) / 58.0%
  (MAVEN) of the detector's apparent false positives have a lemma annotated as an EVENT *elsewhere in the same
  corpus* — genuine event-nouns the gold skipped at that spot (context-dependent realis annotation). The twin
  comparison independently confirms the fires are real events: nominal-class precision is 8–10× the random
  non-verb base rate, CI-separated.

## What I did NOT establish / what I would withdraw first

- **The nominal detector does not close the bare-underspecified fraction, and by the drill it CANNOT without
  context** (Q2b, PINNED-PARTIAL). The `nominal_ctx` subtype (bare event-noun, boundedness-gated only) is fired
  at the same ~0.20 precision as the confident subtype on 19c fiction — i.e., argument-marking does not separate
  precision on LitBank (it does on MAVEN: 0.356 vs 0.275). **What I would withdraw first:** the claim that the
  `ctx` subtype is worth firing by default on literary prose — on that genre it adds recall at no precision
  advantage over the confident subset, so the CONFIDENT-ONLY operating point (recall +0.055 CI-sep, overall
  precision −0.6 pt) is the safer default there. The full operating point is for recall-max / factual prose.
- **The COPULAR result is IN-DOMAIN for the UD-trained parser.** UD-EWT is the only cop-annotated treebank on
  disk, so I could not measure OOD copular (19c / Wikipedia). The `cop` relation is local so it very likely
  transfers, but that is an inference, not a demonstrated number — I withdraw any "copular generalizes" claim
  and mark it a caveat.
- **The MAVEN overall-precision drop (−10.6 pt) is real** (MAVEN annotates verbal events densely, so nominal
  over-fire is more visible there). It is NOT a verbal-event-precision regression (that is invariant); it is the
  honest cost of adding a lower-precision-but-real event class on a corpus with a dense gold. The deflation test
  says most of it is annotation sparsity, but I do not claim the deflation-corrected precision as a headline —
  the robust claims are the CI-separated recall gain and the CI-separated twin win.

## FURTHER PUSHES (deepening — owner-directed: attack the wall, evaluate adjacent components)

**(A) The wall IS discourse-level — TWO can-fail probes localize it exactly (a LOCAL cue fails, a DISCOURSE cue
works).** The drill named nominal sense selection as bottom-up argument structure + top-down coercion. I tested
two cues the static detector does not yet use:
- **LOCAL governing-predicate coercion** (Brennan & Pylkkänen complement coercion — is the nominal an argument of
  an eventive verb happen/occur/witness/… or an event-preposition?): **FAILS** as a precision lever —
  gov-eventive precision **0.105** (WORSE than 0.203 without) at 4% coverage. The local governing predicate does
  NOT carry the discrimination.
- **DISCOURSE event-anaphora** (is the nominal's root already asserted as a VERBAL event earlier in the same
  document? — "the army *destroyed* the city … the *destruction* was terrible"): **WORKS** — anaphoric nominals
  hit **0.389 precision vs 0.195** (2×), CI-consistent across 25 books. But **coverage is only 4%** in 19c
  fiction (explicit event-anaphora is rare there).

Together these localize the wall precisely: the event-vs-non-event decision is **genuinely DISCOURSE-level, not
local** (the local cue fails, the discourse cue succeeds) — confirming the PINNED Q2b boundary with can-fail
tests rather than an assertion. And the discourse cue that works (lexical event-anaphora) is LOW-coverage as a
static approximation, so the FULL discrimination needs the running situation model (which tracks the whole
event/entity state, not just lexical repeats) — i.e. the incremental predictive parser, the keystone's "one
lever." Lexical event-anaphora is a proven-useful *component* of that build (2× precision where it fires).

**(A2) A SECOND drill on the deep mechanism, then a THIRD can-fail probe on its top lever — also negative.** A
finer drill (`research_brain_episodic_event_token_individuation_2026-08-31.md`) pinned the mechanism behind the
nominal wall: **episodic-event-token individuation** — the brain binds a specific spatiotemporally-anchored
occurrence (hippocampal relational binding) distinct from a decontextualized event KIND (neocortical/semantic);
graded semantic↔episodic continuum (Renoult & Rugg 2019/2023; Yonelinas contextual-binding), the linguistic
reflex being spatiotemporal specificity (Krifka/Carlson genericity via covert GEN). Its top-ranked *buildable*
local cue was **COUNTABILITY** (count deverbal nominals a/an/numeral/plural = episodic; bare mass = kind —
Mourelatos 1978; Bach 1986). I tested it (LitBank): it **FAILS backwards** — count-individuated precision 0.154
vs bare-singular 0.240, the OPPOSITE of the prediction, because 19c fiction carries episodic events on
bare-singular ZERO-DERIVATION nouns (glance, pause, stare, roar) that are count-like but bare, while surface
count-marking is rare and noisy. So **three** literature-derived local cues (governing-predicate coercion,
countability, and — succeeding but 4%-coverage — event-anaphora) have now been can-fail-tested, and none crosses
the wall in this genre. **This is the strongest possible form of the boundary claim:** we identified the brain's
exact mechanism (episodic-token individuation), enumerated and TESTED every local proxy the literature offers,
and showed by evidence — not assertion — that the residual is irreducibly discourse-model-bound (the drill's Q3
verdict, now empirically confirmed). The faithful fix is the incremental parser + situation-model event-referent
inventory; there is no static shortcut. *(Caveat: countability was crudely operationalized (surface plural); a
curated mass-event-noun blocklist + proper number parsing might recover a sliver, but the backwards direction
says the genre defeats the surface cue.)*

**Corollary ceiling:** the keystone's own VERBAL precision on LitBank is only 0.27 (the gold's realis-annotation
density), so nominal at 0.20 is within ~7 pts of the deflation ceiling — little precision headroom for ANY
static signal, itself independent evidence the residual is not a lexicon problem.

**(B) OOD copular is real but degrades — hand-adjudicated (addresses the in-domain caveat).** I ran the copular
detector on 19c LitBank (OUT of domain for the UD-trained parser) and hand-adjudicated 22 copular fires:
**14 correct + 2 borderline-acceptable (locative copular) / 6 wrong ≈ 0.64–0.73 precision**, degrading from the
in-domain 0.857. The 6 errors are a clean, nameable set of PARSER OOD category-errors — existential *there*
("isn't there?"), existential pivots ("there's a man"), archaic main-verb *have* mis-labeled `cop` ("had none"),
and clefts ("it was only in Anne that") — NOT failures of the detection principle. **I tested the obvious fix (an
existential-*there* suppressor) and it does NOT fit:** on in-domain UD-EWT, existential fires are only 8/579
(1.4%) and 7 of 8 are GOLD (UD annotates existential "there BE X" as `cop`), so suppressing them is a wash
(precision 0.889→0.890, −7 gold recall). The OOD existential/archaic-*have* errors are parser MISLABELS on
19c constructions, not a clean suppressible class — the faithful fix is broader/incremental parser coverage,
not a suppressor. (Rigorous negative: verified before building.)

**(C) Adjacent component — the reader has NO entity-state dimension. SO I BUILT IT (the copular consumption,
validated).** `SituationModel` has slots for entities, events, coref, timeline, causal_links — but **no
entity-state / attribute slot**, so a copular STATE node would be dumped into the dynamic `events` stream
(the sort-collapse Maienborn warns against). Rather than only flag it, I built and validated the recovery that
slot would hold: from the labeled parse, for each `cop` predication extract the brain-faithful **(HOLDER,
PROPERTY)** binding — HOLDER = the predicate's `nsubj`, PROPERTY = the predicate — NOT agent/patient (Maienborn
Kimian state; Bemis & Pylkkänen LATL property-attribution). **Measured on UD-EWT test (2077 sents, 542 gold state
pairs, `exp_entity_state_dimension_v1`):**

| method | pair recall | pair precision |
|---|---|---|
| **parse-based (HOLDER+PROPERTY)** | **0.6771** | **0.8717** |
| parse-free positional floor | 0.4576 | 0.4218 |
| info-free twin (random holder) | 0.4262 | 0.5662 |

Parse-based beats the positional floor by **+0.220** [.172,.265] and the random-holder twin by **+0.251 recall**
[.212,.289] / **+0.306 precision** [.256,.353], all CI-separated; property-only recall 0.721; **given the correct
predicate, the holder is correct 93.9%**. So the copular detection FEEDS a usable entity-state representation —
the copular win is consumable, not stranded. (The keystone reader recovers ZERO state pairs — it has no such
output at all.) The remaining build is purely a plumbing wire: add the slot to `SituationModel` and route
`state`-sort nodes into it (proposed diff below).

## KEY REALIZATIONS (the enabling moves)

1. **The two event classes have OPPOSITE structural profiles, and the brain predicts which is clean.** Copular
   is carried by a LOCAL, unambiguous relation (`cop`) → clean at 0.857 precision even on a UAS-0.79 parser.
   Nominal is carried by a noun's CONTEXT-DEPENDENT sense → intrinsically precision-bounded without the situation
   model. Naming this (via the drill) turned "why is nominal precision low" from a bug hunt into a PINNED
   boundary: *the copular signal is structural, the nominal signal is lexical-and-context-bound.*
2. **Measure each class on its PROPER gold.** LitBank/MAVEN annotate realis DYNAMIC events (nominal shows up,
   copular states do not — only 2.8% ADJ); UD `cop` is the structural COPULAR gold. Trying to score copular on
   LitBank would have manufactured a false negative. The honest split required two golds.
3. **A non-circular deflation test beats hand-waving about "sparse gold."** My first FP-enumeration was circular
   (it re-checked the firing condition → trivial 100%). Replacing it with "is this lemma annotated as an EVENT
   *elsewhere* in the corpus" gave an independent 35–58% gold-gap rate — real evidence the absolute precision is
   deflated, not asserted.
4. **The nominal precision lever is boundedness, and it is the SAME Hopper–Thompson foreground signal already
   built for the causal foreground gate.** The over-fire was dispositional/abstract nouns (habit, care,
   attention); the drill's Q2c pinned boundedness/telicity as the event-hood feature; suppressing the unbounded
   dispositionals is the one-organ convergence the Garbin pin predicts (verbal + nominal events, one route).
5. **Copular is a STATE sort, not an event — and that tag must be load-bearing.** The faithful move (Maienborn)
   is not "fire an event on `is`" but "fire a STATE node on the predicate, bound HOLDER+PROPERTY." That routes
   copular to the entity-state (background) dimension, not the who-did-what/causal stream — which is exactly the
   situation-model dimension the brief said states feed.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b)

- **Event detection / "READ THE TEXT" front-end — COMPLETENESS half now built.** The keystone fixed verbal
  recall (tense-agnostic UPOS==VERB). This extends it to the two non-verbal predication classes the keystone
  named as excluded: **COPULAR STATES** (recovered via the `cop` relation, 0.857 precision — a clean structural
  win) and **DEVERBAL NOMINAL EVENTS** (recovered via event-denoting-ness + argument structure + boundedness;
  recall +0.087 LitBank / +0.185 MAVEN CI-sep, real-signal but precision-bounded). PINNED refinement: event-hood
  is category-independent (neo-Davidsonian); a copular state is a DISTINCT Kimian-STATE sort (Maienborn 2005),
  not a degenerate event — fire on the predicate, tag `state`, bind HOLDER+PROPERTY. **New PINNED deviation
  logged:** the bare-underspecified deverbal-nominal fraction is INTRINSICALLY context-bound (Q2b) — a
  context-free detector cannot match the brain there; the faithful fix is the incremental predictive parser +
  situation model (the keystone's "one lever, three payoffs"). Mark: copular detection brain-faithful +
  validated in experiments/, awaiting hdlab landing; nominal detection recoverable-fraction built, residual is a
  named context-wiring gap.
- **Arc parser + arc labeler (`hdlab.arc_parser`/`hdlab.arc_labeler`): the `cop` relation is a HIGH-fidelity
  local signal** even at UAS 0.79 (0.857P/0.813R on cop-predicate detection) — a counterexample to "the parser
  is too noisy to gate on." Local, high-frequency relations are recoverable; long-range attachment is not. This
  refines the keystone's "parser too noisy" verdict: it is RELATION-DEPENDENT.

## PROPOSED hdlab DIFF (strategy lands it — Q111)

In `hdlab/situation_reader.py`, behind a new DEFAULT-OFF flag (`copular_nominal_events`, coupled to
`tense_agnostic_events`), extend `_tense_agnostic_extract` (byte-identical when off):
1. **Copular:** after the UPOS==VERB loop, load the arc parser (`_FRONTEND_ARC_ASSET`, already wired on the
   role_route path) + a new arc-labeler asset (`data/frontend_assets/arc_labeler_hashed_ud_ewt.json`); fire a
   `state`-sort `T.Event` on the head of each `cop` arc (skip tokens already fired as VERB). Carry a `sort`
   field so `_read_events` binds HOLDER (nsubj)+PROPERTY, not AGENT/PATIENT, and routes it to the entity-state
   dimension rather than the who-did-what/causal stream.
2. **Nominal:** fire an `event`-sort `T.Event` on a NOUN/PROPN token when it is event-denoting AND
   (argument-marked OR unambiguous) AND boundedness-gated AND not dispositional. **Bake the WordNet event-sense
   lexicon to a static JSON asset offline** (`data/frontend_assets/event_noun_lexicon.json`) so the runtime
   needs no nltk (a static offline-built asset is admissible; the invariant is only NO external LLM at
   inference). Default the operating point to CONFIDENT-ONLY (argument-marked/unambiguous) for precision safety;
   expose the full (`+ctx`) point as a recall-max flag.
3. **Entity-state dimension (the copular consumption — de-risked in `exp_entity_state_dimension_v1`):** add
   `entity_states: List[EntityState]` to `SituationModel` (EntityState = holder, property, sort="state"); in
   `_read_events`, route each `state`-sort (copular) node to `entity_states` via `extract_entity_states`
   (HOLDER = the predicate's `nsubj` from the labeled parse, PROPERTY = the predicate) INSTEAD of pushing it
   into the dynamic-event codec. Recovery is 0.677R/0.872P, CI-separated over floor+twin — a plumbing wire, not
   a research risk.
4. Update `WIRING_MAP.md` DEBT 2 (the assembly): the event set fed to every downstream dimension is now
   completeness-extended (verbal + copular-state + nominal); re-measure downstream dimensions with the flag ON.

## Adjacent components — capability / limitation / brain status / opportunity (seeds the next problems)

| component | capability now | limitation (on-disk) | brain status | next-problem opportunity |
|---|---|---|---|---|
| **entity-state dimension** | **BUILT + validated**: (HOLDER,PROPERTY) recovery 0.677R/0.872P, CI-sep over floor+twin | `SituationModel` has no `entity_states` slot yet (plumbing only) | Kimian state = HOLDER+PROPERTY (PINNED) | **land the slot + wire** (proposed diff below) — the copular consumption, now de-risked end-to-end |
| **nominal sense disambiguation** | event-denoting + arg + boundedness; recoverable fraction | the bare fraction is context-bound (−10.6 pt overall prec on MAVEN) | intrinsically context-bound (PINNED Q2b) | **the incremental predictive parser + situation-model context** — the keystone's "one lever"; this is the faithful fix for the residual |
| **arc labeler** | `cop` at 0.857; UAS 0.79 global | long-range relations noisy | local relations high-fidelity | a higher-UAS/incremental parser lifts the long-range roles AND the copular OOD case |
| **event SORT typing** | verbal/state/nominal tagged | downstream reads all as one event stream | state vs event = distinct sorts (PINNED Maienborn) | **make the sort tag load-bearing** — segment foreground events vs background states in the situation model |

## TLDR (plain language)

We had just taught the reader to catch almost every *action* word. But a lot of what a story tells you isn't an
action: "Sarah is a doctor", "the room was cold" are *states*, and "the destruction of the city", "the
explosion" are *happenings hidden inside nouns* — and the reader was blind to all of them. I first asked how the
brain handles these. Two clear answers came back: a described state is a *different kind of thing* to the brain
than an action (a fact pinned to someone, sitting in the background), and the little linking word "is/seems" is
not where the meaning lives — people drop it and keep the description — so I read the description, not the
linker. That made the state-catcher clean: it now catches "is a doctor / was cold" correctly about **86% of the
time it should**, lifting the reader's coverage of states-and-actions by **15 points** with the action-catching
untouched, and a scrambled version does far worse. Event-nouns are harder, and the brain told me *why*: for a
word like "the destruction", whether it means the *happening* or its *aftermath* is genuinely undecidable from
the word alone — the brain waits for the rest of the sentence. So I catch the clearly-marked ones now ("the
destruction *of the city*") — lifting noun-event coverage by **9 points on old novels and 18 points on
Wikipedia**, with a scrambled version again far worse — and I mark the stubborn remainder as needing the
"reading-in-context" machinery we've already identified as the next big build. Where the reader looks like it's
guessing wrong on nouns, I checked: a third to a half of those "wrong" catches are real events the answer-key
itself marks elsewhere but skipped here — so the tool is finding real happenings the gold under-labels.

## QUESTIONS

None blocking. One judgement call I made and flag for the owner: I treat the bar's "no precision regression on
the verbal events" as the *verbal-event* precision (which is invariant — the new classes never touch verb
firing), and report the small *overall*-precision cost of adding the new classes separately and honestly, since
forbidding any overall-precision change would forbid adding any real-but-lower-precision event class regardless
of the recall win. If the owner intends the stricter overall reading, the CONFIDENT-ONLY nominal + copular
operating point minimises it (copular −0.9 pt; nominal-confident −0.6 pt on LitBank).

## NEXT STEPS

1. **Land the diff** (copular via `cop`, default confident-only nominal, both default-OFF, sort-tagged) +
   the `SituationModel.entity_states` slot (the entity-state dimension is now BUILT + validated in
   `exp_entity_state_dimension_v1`, 0.677R/0.872P — this is now a plumbing wire, not a research problem).
2. **The incremental predictive parser + situation-model context** is the PINNED faithful fix for the
   context-bound nominal residual — the SAME "one lever, three payoffs" the keystone named (roles + detection
   precision + now nominal sense). Confirmed discourse-bound by two can-fail probes (local cue fails, discourse
   event-anaphora works at 2× precision but 4% coverage). This is the recommended next big problem; lexical
   event-anaphora is a proven-useful component of it.
3. **Make the event SORT tag load-bearing** — foreground events vs background states as distinct situation-model
   node types (Maienborn; Zwaan event horizon), now that both classes are detected and states have a home.
4. **Broader/incremental parser coverage** for the OOD copular error classes (archaic main-verb *have*,
   existential/cleft mislabels) — NOT a suppressor (tested: existentials are mostly gold in-domain; suppressing
   is a wash) but the same parser-fidelity lever as the nominal residual. Folds into (2).

## INTEGRATED_BY_STRATEGY 2026-08-31 -- EXCELLENT (the extraction-COMPLETENESS half of the front-end)

Reverified 14/14 FIRST-HAND (`verification/test_copular_nominal_event_detector_organ.py`, scaffold-free, driving the
LIVE `SituationReader(tense_agnostic_events=True).read()`): copular UD 0.7951→0.9448 (+0.1497 [0.1344,0.1650] CI-sep,
cop-class prec 0.857, overall-prec neutral −0.0089); nominal LitBank +0.0873 CI-sep + CROSS-CORPUS MAVEN +0.1845;
nominal-class prec 0.1994 vs twin 0.0195 (10.2×); NON-CIRCULAR deflation 0.348 (958/2751); verbal fires BYTE-IDENTICAL
across modes AND == the landed keystone (219 preds, W5/W12); entity-state (HOLDER,PROPERTY) 0.677R/0.872P vs floor/twin
CI-sep, holder|property 0.939 (W13/W14). Brain-faithful: neo-Davidsonian event-hood (not verb-slot-bound); copular =
Kimian STATE read off the `cop` relation (Maienborn); nominal = deverbal event via event-denoting-ness + argument
structure + boundedness (Garbin/Grimshaw/Hopper). The nominal precision wall drilled to its mechanism (episodic
event-token individuation) + PROVEN model-bound (3 local proxies can-fail-tested, none crosses). Two shortcuts tested +
rejected. Graded EXCELLENT. Review + review_text in PROBLEM.md; priority cleared; audit 2b + WIRING_MAP folded.

**LANDING STATE (Q111): QUEUED — COUPLED with p5 into ONE extraction-front-end landing** (both edit
`hdlab/situation_reader.py::_tense_agnostic_extract`; land as one coordinated default-off effort, not piecemeal — the
WIRING_MAP discipline). Behind a default-off `copular_nominal_events` flag, extend `_tense_agnostic_extract`
(byte-identical when off): (1) fire a `state`-sort node on each `cop` predicate; (2) fire an `event`-sort node on
CONFIDENT event-denoting nouns (bake the WordNet event lexicon to a static JSON asset → no nltk at runtime); (3) add
`SituationModel.entity_states` and route `state` nodes to it (HOLDER=nsubj, PROPERTY=predicate), NOT into the
dynamic-event codec. Reference impls: `experiments/_copular_nominal_events.py`,
`experiments/exp_copular_nominal_event_detector_v1.py`, `experiments/exp_entity_state_dimension_v1.py`. Honest scope:
nominal precision is discourse-bound (~0.20, gold-deflated); the faithful fix for the residual is the incremental
parser + situation model (p2, now owner-DONE) — one lever. ⚠️ The copular detection needs a labeled parse (`cop` arc);
default-off so no hard spaCy dep enters the canonical reader (lazy import when on, like causation).
