---
problem: the_tense_agnostic_detector_drops_tense_needed_by_the_time_dimension
status: SOLVED
bar: "PASS = the tense-preserving detector holds the keystone event RECALL (no CI-separated regression vs the placeholder-tense detector) AND its assigned tense/aspect beats the placeholder-constant floor CI-separated on the tense gold, with the info-free shuffled-tense twin LOSING; AND (the payoff) the unified detector, fed to the timeline, does not regress the TIME/flashback read vs the timeline's own separate extraction. Report CI half-width + null p95."
result: "Recall preserved EXACTLY (identical event-index set through live SituationReader.read(), 219 events, placeholder tense constant -> 9 varied tense labels). Tense/aspect on UD-EWT test (n=2605 VERB tokens, in-substrate tagger+surface morphology): word-tense acc 0.770 [0.755,0.786] (CI half-width 0.015) vs placeholder-constant 0.296 / majority 0.397 / shuffled-twin null-p95 0.336, CI-separated; clausal aspect 0.987, voice 0.933; FINITE clausal-tense 0.860; EFFECTIVE temporal location (every event placed, mark-and-inherit) 0.712 [0.695,0.731] vs placeholder 0.244 / majority 0.486 / twin 0.385. Payoff: is_pp agreement with the timeline's own extractor 0.988 on shared flashback events + 300+ extra events recovered; flashback-gold reconstruction unified 1.00 vs stock 0.88 (no regression -- unified is higher)."
floor: "STRONGEST constant floor = majority-class (word-tense 0.397 'NONE'; effective-location 0.486 'PRESENT'); also the literal placeholder-constant (all SIMPLE_PAST: word-tense 0.296, effective 0.244). Gated on the floor; twin (shuffled tense labels) null-p95 reported beside every margin."
controls: "info-free shuffled-tense twin (same marginal) LOSES CI-separated on every headline; placeholder-constant + majority-class floors both cleared CI-separated; ORACLE-ANCHOR ablation isolates the non-finite residual (frame vs anchor-finding); STANDALONE-tense-on-non-finite enumerated as the NEGATIVE (0.335) it must not be scored as; generalization arm on the train split (different sentences) holds; recall preservation is EXACT (identical event set), not merely non-regressed."
files_changed: "experiments/exp_tense_preserving_event_detector_v1.py, experiments/exp_tense_preserving_live_reader_and_timeline_v1.py, experiments/exp_tense_preserving_parse_inheritance_v1.py, verification/test_tense_preserving_event_detector.py, notes/problems/the_tense_agnostic_detector_drops_tense_needed_by_the_time_dimension/research_brain_temporal_location_tense_aspect_2026-08-31.md, notes/problems/the_tense_agnostic_detector_drops_tense_needed_by_the_time_dimension/research_discourse_reference_time_and_temporal_order_2026-08-31.md"
reverify: ".venv/Scripts/python.exe verification/test_tense_preserving_event_detector.py"
---

# SOLVED — the tense-preserving high-recall event detector

## What the problem was (verified on disk, not the brief)
The landed keystone `hdlab/situation_reader.py::_tense_agnostic_extract` fires an event at every
`UPOS==VERB` (recall ~0.95) but stamps a PLACEHOLDER `T.TENSE_SIMPLE_PAST` on all of them, and that
tense flows straight into `sm.events[i].tense` (`EventRecord.tense`). **The root cause is structural:
the in-substrate UD tagger (`hdlab.pos_tagger`) emits only COARSE UPOS (VERB/AUX) — `tag()->list[str]`,
no tense/morphology — so the keystone has no tense signal to keep.** The stock `T.extract_events` DID
compute tense but is tense-GATED (fires only on VBD / had+VBN / be+VBN / modal+VB / VBG-participial),
missing present-tense finite verbs (VBZ/VBP) 100% and capping detection recall ~0.33. So the two
extractions were split: the high-recall keystone (tense dropped) and the timeline's own narrow
`M.extract_events_punct` (keeps tense, fires only on past-perfect "had" flashbacks).

## The mechanism (brain-foundational — how the brain does this)
DETECTION stays tense-agnostic (event-hood = lexical predication; the tenseless neo-Davidsonian event
variable; PINNED, keystone). Temporal LOCATION is a SEPARATE computation: a **COMPOSITIONAL parse of
the verb group** (main verb + its auxiliary chain) into a **Reichenbach triple** — tense (reference vs
speech time), aspect (event vs reference: simple / perfect / progressive), voice (active / passive) —
reading the same morphosyntax the language network reads (Reichenbach 1947; Bach eventualities; Zwaan &
Radvansky TIME dimension; LAN→P600 / LIFG morphosyntactic composition, Kielar 2016). This is NOT the
stock flat 6-way label; it FACTORS tense × aspect × voice, which is what a proper TIME dimension needs.
Glass-box, NO LLM. The verb-group is read from the in-substrate UPOS (VERB/AUX split) + closed-class
auxiliary surface forms + suffix morphology (`surface` mode, fully in-substrate); an optional fine PTB
tag (NLTK perceptron — the stock reader already uses it) is a separable English-morphology PARAMETER
(`finetag` mode) that lifts accuracy. See the research drill (cited) confirming every choice is PINNED.

### The research-driven reframe of the one wall: MARK-AND-INHERIT
The brief's negative hint ("the extra present-tense verbs are the ambiguous ones") is **REFUTED**: on
UD gold the extra present-tense verbs are highly recoverable (VBZ 1.00, VBP 0.87). The real weak spot
is bare **VB** (infinitive) and **VBG** (gerund/participle) — and a literature drill (see the research
note) shows this is a **category error, not a morphology bug**: non-finite forms carry NO independent
absolute tense; they INHERIT the reference time from the controlling finite verb (Ogihara/Abusch;
sequence-of-tense). So the faithful target is `finite=False` + an inheritance pointer to the matrix
finite verb, NOT a guessed standalone tense. Implementing that:
- **non-finite STANDALONE absolute tense = 0.335** (the enumerated NEGATIVE — the wrong instrument);
- **non-finite INHERITED (surface anchor) = 0.674** (inheritance is the right frame — ~doubles it);
- **non-finite INHERITED (ORACLE anchor = the gold syntactic controller) = 0.876** — matching the
  finite ceiling, so the *entire* residual is surface anchor-finding, which the reader's existing
  opt-in dependency parser (`role_route != "positional"`) closes. The wall is fully decomposed.

## What was measured (headline, in-substrate surface mode, UD-EWT test, n=2605)
| quantity | value | strongest floor | twin null-p95 |
|---|---|---|---|
| word-tense acc | **0.770** [0.755, 0.786] (±0.015) | majority 0.397 / placeholder 0.296 | 0.336 |
| clausal ASPECT acc | **0.987** | (majority 0.375) | — |
| clausal VOICE acc | **0.933** | — | — |
| FINITE clausal-tense (temporal anchors, n=1517) | **0.860** | majority 0.566 / placeholder 0.281 | — |
| EFFECTIVE temporal location (ALL events, mark+inherit, n=2491) | **0.712** [0.695, 0.731] | majority 0.486 / placeholder 0.244 | 0.385 |

- `finetag` optimization (separable parameter): word-tense **0.909**, FINITE clausal-tense 0.884.
- GENERALIZATION (train split, different sentences, fixed rule): FINITE clausal-tense **0.912**,
  word-tense 0.805 — holds; the composition is not fit to any corpus.
- RECALL PRESERVED EXACTLY: through the live `SituationReader.read()` the tense-preserving detector
  produces an IDENTICAL event-index set to the placeholder detector (same detections; only the tense
  label changes), while `sm.events[i].tense` goes from a single constant to a varied set. This is the
  strongest possible "no CI-separated recall regression" — it is byte-identical detection.
- PAYOFF (the two extractions can be UNIFIED): feeding the unified detector to
  `M.reconstruct_order_timeline` reproduces the timeline's own past-perfect (is_pp) flashback signal
  (agreement **0.988** on shared events, after fixing an adverb-in-verb-group bug the payoff test
  surfaced — "had long devastated", "had never before seen"), recovers 300+ extra events the narrow
  timeline extractor drops (superset, not regression), and on a constructed flashback gold recovers the
  correct chronological order **unified 1.00 vs stock 0.88** (no regression — unified is actually
  higher, because its verb-group parse tolerates intervening adverbs the stock 3-token lookback breaks
  on).

## What I did NOT establish / would withdraw first
- The tense gold is UD-EWT FEATS **word-tense** (morphological) + a **clausal triple DERIVED from the
  UD gold tree** (aux dependency children + Voice feature). UD-EWT has NO Aspect FEATS, so the aspect
  gold is tree-derived, not hand-annotated — if that derivation is wrong the 0.987 aspect number moves.
  (It is a deterministic, standard read of aspect off the tree; independent of our rule.)
- The mark-and-inherit **surface anchor-finder** (nearest finite verb by token distance) is a cheap
  proxy for the true syntactic controller; the oracle-anchor ablation shows the residual 0.67→0.88 is
  entirely this proxy. If I had to withdraw one claim it is the *surface* non-finite number, not the
  inheritance frame.
- Genre generalization is within-standard (UD-EWT train vs test). LitBank/QA-SRL have no tense FEATS
  gold, so the OOD-genre tense number is not established (only the keystone's OOD *recall* was).
- The payoff is validated at the level of is_pp fidelity + reconstruction on a constructed gold; a
  large annotated timeline-order gold was not available, so the reconstruction correctness rests on the
  8-item constructed set + agreement with the stock path on real flashback sentences.

## KEY REALIZATIONS
- **The keystone has NO tense signal at all** — not "drops it late": the in-substrate tagger is
  UPOS-only. So this is a BUILD (compose tense from the verb group), not a recovery of a dropped field.
- **Recall preservation is FREE and EXACT** — tense is a LABEL on already-detected tokens; the
  detection set is untouched, so recall cannot regress by construction. The interesting question was
  never recall, it was tense ACCURACY on the extra present-tense verbs (which is high).
- **The wall was a category error.** Asking "what tense is `to walk`?" measures against a gold that
  itself must inherit. Reframing non-finite events as mark-and-inherit turned a 0.335 "failure" into a
  0.876 (oracle) success and made the residual a known, fixable anchor-finding gap. *Ask whether the
  experiment could have succeeded before asking why it did not — a per-token absolute-tense gold is the
  wrong instrument for a non-finite form.*
- **Copy the computation, sweep the parameter.** The Reichenbach composition is the shared computation
  (hardcode it); the English aux/suffix lexicon is a supplied closed-class PARAMETER (dual-route
  words-and-rules is brain-faithful); telic/atelic aspectual class was NOT hardcoded (the brain learns
  it — flagged as the thing to keep learned).

## DEEPENING (post-solve, driven by the two research drills — the bar was already met)

### A. Closing the non-finite wall with SYNTAX (exp_tense_preserving_parse_inheritance_v1.py)
The research said the brain finds the inheritance controller from the syntactic parse, not token
proximity. Tested directly on UD-EWT test non-finite events (n=567), inheriting our composed tense at
the controller found by four methods:

| controller found by | non-finite effective-tense acc |
|---|---|
| none (STANDALONE absolute tense — the NEGATIVE) | 0.337 |
| surface token-proximity (our default) | 0.674 |
| **in-substrate ArcParser dependency heads** (glass-box, reader's own) | **0.734** |
| spaCy dependency heads (competent glass-box parser) | 0.743 |
| gold UD tree (oracle ceiling) | 0.877 |

**Finding (honest, nuanced):** a real dependency parse DOES help (full test set n=567: 0.674 → 0.734;
the gain is MODEST and sample-variable — ~8-30% of the residual across sub-samples) — confirming the
residual is syntactic — but a *competent* parser (spaCy 0.743) barely beats our in-substrate one, so
**parser fidelity is not the dominant remaining lever**. The gap from 0.74 to the ~0.87 oracle is
bounded by our own finite-tense prediction at the controller (~0.86, i.e. the oracle ceiling IS roughly
the finite accuracy). So the wall is now fully attributed: FRAME correct (oracle ~0.87), anchor-finding
partially and variably closed by any real parse, remainder = finite-tense accuracy — an incremental
optimization (wire the parser into the inheritance step in the assembly path), not a blocker. *A mid-analysis hypothesis ("the in-substrate parser is too weak") was a 150-sentence
small-sample artifact; the full corpus showed it helps as much as spaCy — recorded so it is not requoted.*

### B. Adjacent-component evaluation + the next problem (research_discourse_reference_time_...md)
Evaluated the adjacent TIME dimension for brain-foundational fidelity (owner directive):
- **`_read_timeline` is brain-UNfaithful in a SPECIFIC way:** the situation-model timeline is built by
  an anaphoric, incrementally-updated Reference time (PINNED: Partee temporal focus; Kamp & Reyle DRT;
  Dowty aspectual advancement), where simple-past EVENTIVE clauses *advance* the narrative-now and the
  pluperfect is the *marked anteriority exception*. Our `_read_timeline` fires ONLY on "had"
  (pluperfect) — it models the exception and DROPS the default advance rule, an inversion of the brain's
  model. The **readout shape is faithful** (a before/after edge graph → toposort = hippocampal
  relational order reconstruction; DuBrow & Davachi), so the fix is the EDGE SET, not the readout.
- **Missing edges:** default narrative-now advancement (simple past), aspectual advancement
  (telic advances / atelic overlaps — needs a LEARNED telicity signal, not a hardcoded list),
  adverbial/connective R-setting beyond the few handled, and reference-time anaphora.
- **Opportunity unblocked by THIS solution:** the tense-preserving detector supplies exactly the
  per-verb tense/aspect FEATURES that a DRT reference-time update consumes — so a general temporal-order
  dimension is now buildable on one unified event set.
- **DATA GAP (blocks scoring the next problem):** NO temporal-ordering gold is on disk (only UD-EWT +
  LitBank + reading corpora). MATRES (free, GitHub, over TempEval-3/TimeBank) is the primary
  can-fail ordering gold; CaTeRS (ROCStories) a short-narrative sanity set; TRACIE a stretch. Acquiring
  them is admissible (FOUNDATION-is-free-to-build).

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b)
The TIME-dimension entry (2026-08-31 component scan) called the tense-preserving detector a QUEUED p1
follow-on. It is now BUILT + VALIDATED in `experiments/` (not landed — hdlab is strategy's, Q111).
Add: (a) the detection/location split is PINNED-faithful (tenseless event variable + separate
Reichenbach location operator); (b) temporal LOCATION is a compositional verb-group parse (tense ×
aspect × voice), aspect/voice CI-clear over floors; (c) non-finite events are MARK-AND-INHERIT, not
standalone-tense (research-pinned); (d) the research correction stands — situation-model TIME
*placement* is tense+aspect+**discourse context** (Bastiaanse/PADILIH), so the timeline's discourse
reference-time step must stay DOWNSTREAM of this per-verb feature parse. The unified detector is is_pp-
faithful to the timeline's own extractor, so the SHARED-EVENT-SET architecture is unblocked.

## FOR STRATEGY — the proposed hdlab change (Q111; you land it)
Replace the placeholder-tense line in `hdlab/situation_reader.py::_tense_agnostic_extract` with the
composed tense/is_pp, behind the SAME `tense_agnostic_events` flag (default-off = byte-identical). The
validated reference impl is `experiments/exp_tense_preserving_event_detector_v1.assign_sentence` +
`_stock_tense`. Concretely, inside `_tense_agnostic_extract`, after `up = self._ta_tagger.tag(toks)`:

```python
# compose real tense/aspect/is_pp per the verb group (Reichenbach), replacing the constant
sent = assign_sentence(toks, up, mode="surface")           # from the validated ref impl
for i, tk in enumerate(toks):
    if up[i] == "VERB":
        a = sent[i]
        events.append(T.Event(lemma=tk.lower(), idx=i, pos=up[i],
                              tense=_stock_tense(a), is_pp=bool(a["is_pp"])))
```

Then the TIME dimension (`_read_timeline`) can consume the unified detector (it is is_pp-faithful);
and `EventRecord.tense` becomes real content for every dimension.

### Candidate follow-on problems this seeds (ranked; map, not silent gaps)
1. **PRIMARY — `the_timeline_dimension_reorders_only_around_pluperfect_and_drops_default_reference_time_advancement`.**
   Rebuild the reader's TIME dimension as a general event-ordering graph via DRT-style Reference-time
   update (default advance on eventive/telic simple-past, overlap on states, anteriority on perfect,
   adverbial/connective R-resets), CONSUMING this tense-preserving detector. Replicates Partee temporal
   focus + Kamp & Reyle DRT + Dowty aspectual advancement (computational) + hippocampal relational order
   binding (implementation). Gold: pairwise event ordering (before/after/equal/vague) from MATRES /
   TempEval-3 / TCR; can-fail control = text-order baseline + shuffled-tense twin LOSES. Judgement call
   from the research: extend the whole-passage `_read_timeline_register` (already the faithful
   graph→toposort readout), NOT the per-sentence `_read_timeline`, and widen its edge set.
2. **SECONDARY (a component of #1) — `aspectual_advancement_needs_a_learned_telic_atelic_signal`.**
   Dowty's default advancement is aspect-gated but we have no telicity signal; LEARN telic/atelic
   distributionally (Aspect Hypothesis) rather than hardcoding a list (the one shortcut the first
   research drill flagged as brain-UNfaithful).
3. **INCREMENTAL — close the non-finite anchor-finding residual** by wiring the reader's dependency
   parser into the inheritance step (Deepening A: 0.674 → 0.734 with a real parse; oracle 0.877).
   Small; do it inside the assembly path where the parser is already loaded.

### DATA-ACQUISITION ACTION (blocks problem #1)
No temporal-ordering gold is on disk. Acquire MATRES (free, GitHub — over TempEval-3/TimeBank) as the
primary ordering gold, CaTeRS (ROCStories) as a short-narrative sanity set, TRACIE as a stretch
inference test. Admissible as a static offline FOUNDATION asset.

## INTEGRATED_BY_STRATEGY 2026-08-31 -- STRONG (tense-preserving front-end; unblocks the landed TIME dimension)

Reverified 12/12 FIRST-HAND (`verification/test_tense_preserving_event_detector.py`, scaffold-free, recomputed from
UD-EWT gold + the live reader): in-substrate word-tense 0.77 [0.7551,0.7856] CI-sep over placeholder 0.2955 / majority
0.3974 / twin 0.3356; aspect 0.987 / voice 0.933; finite clausal-tense 0.860; effective temporal location 0.712 CI-sep,
twin losing; RECALL PRESERVED EXACTLY (219 events identical through live read(), tense 1→9 real labels, W9); mark-and-
inherit NF standalone 0.337→inherit 0.674→oracle 0.876 (the "wall" dissolved as a sequence-of-tense category error, W5);
generalizes to train split (finite 0.912, W7); PAYOFF is_pp agreement 0.988 + 303 extra events (W10) + flashback
reconstruction 1.00 vs stock 0.875 (W11). Brain-faithful + PINNED (neo-Davidsonian tenseless detection; compositional
Reichenbach tense×aspect×voice parse of the verb group). Graded STRONG (bar fully cleared; held below EXCELLENT because
the 0.909 headline uses a separable NLTK fine-tag — the pure-substrate core is 0.770, itself CI-sep — and the payoff
gold is a small 8-item constructed flashback set; both flagged). Review + review_text in PROBLEM.md; priority cleared;
audit 2b + WIRING_MAP folded.

**LANDING STATE (Q111): QUEUED — COUPLED with p3 into ONE extraction-front-end landing** (both edit
`hdlab/situation_reader.py::_tense_agnostic_extract`; land as one coordinated default-off effort). Replace the
placeholder `tense=T.TENSE_SIMPLE_PAST` line with the composed tense/is_pp (validated ref impl `assign_sentence` +
`_stock_tense` in `experiments/exp_tense_preserving_live_reader_and_timeline_v1.py`), behind the same default-off flag
(byte-identical off). Then the landed TIME dimension (`timeline_register`) consumes the unified is_pp-faithful detector
and `EventRecord.tense` becomes real content for every dimension. Follow-on (solver-mapped, NOT owed here): rebuild the
narrow `_read_timeline` (fires only on the marked "had") into a DRT reference-time ordering graph that also advances on
eventive simple-past clauses — needs a temporal-ordering gold ACQUIRED (MATRES; none on disk).
