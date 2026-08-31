---
owner_verdict: DONE
---

Problem: the_tense_agnostic_detector_drops_tense_needed_by_the_time_dimension — SOLVED
(brain-foundational; witness 12/12; ledger-accepted, 0 malformed). WIP until owner_verdict: DONE.
No hdlab/ touched (Q111 — proposed diff + validated ref impl in SOLVED.md). Glass-box, NO LLM.

REVERIFY: .venv/Scripts/python.exe verification/test_tense_preserving_event_detector.py   # 12/12

WHAT IT IS: the landed keystone detector fires an event at every verb (recall ~0.95) but stamps a
PLACEHOLDER "simple past" on all of them, and that flows into every event's tense field — so the
TIME dimension can't use one shared event set and runs its own separate extraction. Root cause
(on disk): the in-substrate tagger emits only coarse UPOS (VERB/AUX), so the keystone has NO tense
signal to keep. Built the tense-PRESERVING variant: keep every detection, and compute each event's
real tense/aspect.

THE MECHANISM (how the brain does it): detection stays tense-agnostic (event-hood = lexical
predication — the tenseless neo-Davidsonian event variable, PINNED). Temporal LOCATION is a
SEPARATE, compositional parse of the verb group (main verb + its auxiliary chain) into a Reichenbach
triple — tense x aspect x voice — reading the same morphosyntax the language network reads
(Reichenbach 1947; Zwaan & Radvansky TIME dimension; LAN->P600 / LIFG composition). Read from the
in-substrate UPOS + closed-class auxiliary forms + suffix morphology (fully in-substrate); an
optional fine PTB tag (NLTK, already in the stock reader) is a separable morphology PARAMETER.
Two literature drills confirmed every choice is PINNED (research notes committed).

MEASURED (UD-EWT test, in-substrate, n=2605; CI + null-p95 reported):
- RECALL PRESERVED EXACTLY — identical event-index set through the live SituationReader.read()
  (219 events), tense goes from one constant label to 9 real ones. Strongest possible "no regression".
- word-tense 0.770 [0.755,0.786] vs placeholder 0.296 / majority 0.397 / shuffled-twin 0.336 (CI-sep).
- clausal ASPECT 0.987, VOICE 0.933 — the compositional win no word-tense label carries.
- FINITE clausal-tense (the temporal anchors) 0.860; every-event temporal placement 0.712
  [0.695,0.731] vs placeholder 0.244 / majority 0.486 / twin 0.385.
- GENERALIZES to the train split (finite tense 0.912); the fixed composition is not fit to any corpus.
- finetag parameter lifts word-tense to 0.909 (separable, English-morphology).

THE BRIEF'S NEGATIVE HINT IS REFUTED + THE WALL IS UNDERSTOOD (research-driven): the extra
present-tense verbs are highly recoverable (VBZ 1.00, VBP 0.87). The real weak spot is bare
infinitives/gerunds — and a drill showed this is a CATEGORY ERROR, not a bug: non-finite forms carry
no independent tense, they INHERIT it from the controlling finite verb (Ogihara/Abusch;
sequence-of-tense). Implementing MARK-AND-INHERIT: non-finite standalone tense 0.335 (the enumerated
NEGATIVE) -> inherited 0.674 -> with the gold syntactic controller (oracle) 0.876, matching the finite
ceiling. So the frame is correct and the entire residual is anchor-finding.

PAYOFF (the two extractions can be UNIFIED): fed to the timeline reconstructor the unified detector
reproduces the flashback (past-perfect) signal (is_pp agreement 0.988), recovers 300+ extra events the
narrow timeline extractor drops, and BEATS the stock path on a flashback gold (1.00 vs 0.88 — its
verb-group parse tolerates intervening adverbs the stock 3-token window breaks on).

DEEPENING (post-solve, the bar was already met):
- A. Closing the non-finite wall with syntax: a real dependency parse (in-substrate ArcParser 0.734;
  spaCy 0.743) modestly closes the surface->oracle residual, but a competent parser barely beats our
  own — so parser fidelity is NOT the dominant lever; the remainder to the ~0.87 oracle is bounded by
  our own finite-tense accuracy. Incremental, not a blocker.
- B. Adjacent TIME organ evaluated + next problem mapped (2nd research drill): the reader's
  `_read_timeline` is brain-UNfaithful in a SPECIFIC way — it fires only on "had" (pluperfect), the
  MARKED exception, and drops the DEFAULT rule that eventive simple-past clauses advance narrative time
  (Partee/Kamp&Reyle DRT reference-time update; Dowty aspectual advancement). Its readout shape
  (edge-graph -> toposort = hippocampal relational order) is faithful; the fix is the EDGE SET.

BE CLEAR — HONEST BOUNDS: (1) the finetag headline (0.909) uses NLTK; the fully in-substrate surface
mode is 0.770 — the fine tag is an admissible separable parameter, not the core. (2) The clausal
aspect/voice gold is DERIVED from the UD tree (UD-EWT has no Aspect feature), not hand-annotated. (3)
The non-finite surface anchor-finder is a proxy; the inheritance FRAME (oracle 0.88) is the robust
claim, not the surface number. (4) Genre generalization is within-standard (UD train vs test);
LitBank/QA-SRL have no tense gold. (5) The payoff rests on is_pp fidelity + an 8-item constructed
flashback gold — no large temporal-ordering benchmark is on disk.

KEY REALIZATIONS: recall preservation is FREE and EXACT (tense is a label on already-detected tokens);
the keystone had NO tense signal (a BUILD, not a recovery); the "wall" was a category error dissolved
by asking whether a per-token absolute-tense gold is even the right instrument for a non-finite form;
copy the computation (Reichenbach), sweep the parameter (English aux/suffix lexicon), and do NOT
hardcode telic/atelic aspectual class — the brain learns it.

FILES: experiments/exp_tense_preserving_event_detector_v1.py (mechanism + mark-and-inherit + effective
temporal location); exp_tense_preserving_live_reader_and_timeline_v1.py (landing form + recall
preservation + timeline payoff); exp_tense_preserving_parse_inheritance_v1.py (deepening A);
verification/test_tense_preserving_event_detector.py (12/12); 2 research notes; SOLVED.md.

FOR STRATEGY (Q111 — you land it): replace the placeholder-tense line in
hdlab/situation_reader.py::_tense_agnostic_extract with the composed tense/is_pp (validated ref impl
assign_sentence + _stock_tense), behind the same default-off flag (byte-identical off). Then the TIME
dimension can consume the unified detector (is_pp-faithful) and EventRecord.tense becomes real content
for every dimension. Fold the AUDIT UPDATE into BRAIN_FOUNDATIONAL_AUDIT.md §2b. Ranked follow-on
problems (in SOLVED.md): (1) rebuild TIME as a DRT reference-time event-ordering graph consuming this
detector — needs a temporal-ordering gold ACQUIRED (MATRES free on GitHub; none on disk); (2) a
learned telic/atelic signal; (3) the incremental parser-into-inheritance wiring.
