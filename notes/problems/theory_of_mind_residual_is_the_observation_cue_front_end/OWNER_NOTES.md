---
owner_verdict: DONE
---

SUBMISSION — SOLVER RESULT: theory_of_mind_residual_is_the_observation_cue_front_end
STATUS: SOLVED | 5 witnesses green (main 6/6, occlusion 6/6, sequential 4/4, testimony 3/3, self-test 5/5)
        | problem_ledger --check clean (malformed/incomplete: 0) | hdlab UNTOUCHED (Q111 — you land)
INTEGRATE ONLY on owner_verdict: DONE in notes/problems/<slug>/OWNER_NOTES.md.
REVERIFY (4 scaffold-free witnesses, live recompute):
  .venv/Scripts/python.exe verification/test_perceptual_access_ledger.py &&
  .venv/Scripts/python.exe verification/test_perceptual_field_occlusion.py &&
  .venv/Scripts/python.exe verification/test_sequential_registration.py &&
  .venv/Scripts/python.exe verification/test_testimony_reliability.py

ONE-LINE: The landed ToM belief organ is perfect with clean observation (1.000) but the residual was reading
"did agent A witness the change?" from prose with a keyword list (0.808 → 50% on real novel language). Replaced
it with the brain's actual mechanism — a per-agent PERCEPTUAL-ACCESS REGISTRATION LEDGER — validated CI-separated
on corpus prose, lifting end-to-end 0.50→0.99 past the 0.82 residual. Two research drills then closed the
occlusion wall, the distance/windowing question, sequences, and deceptive/discounted testimony.

THE BAR (PROBLEM.md §7): (1) cue acc beats the 0.808 lexical baseline CI-sep on a CORPUS-mined false-belief gold,
info-free twin LOSES; (2) lifts END-TO-END belief acc CI-sep over the lexical-cue 0.821 toward oracle 1.000;
(3) brain-faithful mechanism (perceptual-access read from event/entity/situation structure, NOT a keyword list);
(4) a corpus-mined gold exists + verified. A rigorous NEGATIVE is a full pass.

MECHANISM (copy the operation; Butterfill&Apperly 2013 registration; Zwaan situation model; Talmy PATH; Harris&
Koenig testimony): a STICKY per-agent registration ledger, NOT a query-time boolean. observed(A,E) =
  RULE 0 explicit narrator epistemic statement ("unbeknownst to her" / "he watched"), EVENT-LOCAL; else
  RULE 1 co-present (presence as temporal INTERVAL; motion read off the realized PATH satellite not a verb list)
         AND in the PER-MODALITY perceptual FIELD (vision needs light+line-of-sight+not-closed-opaque-container+
         attending+awake; audition penetrates dark/thin-barrier but needs a non-silent event; touch needs contact);
  OR RULE 2 informed (testimony writes the ASSERTED location — honest→true, a believed LIE→false, distrusted→
         discounted). FALSE BELIEF = the ledger being STALE vs reality — no separate computation. Folding this per
         change over a CHAIN gives sequential registration + motion-persistence + ignorance(None); glass-box over a
         spaCy parse, NO external LLM at inference.

RESULT (numbers, scorer = extractor observed-bit == ground-truth observation state):
  * CUE, corpus-grounded gold (real LitBank cue-clauses in canonical frames, n=246 balanced): LEDGER 0.988
    [0.972,1.000] dev / 0.985 [0.978,0.992] HELD-OUT (5 unseen phrasing draws, n=1230) vs LEXICAL 0.500
    [0.439,0.557]; TWIN 0.488 (loses). Authored gold: LEDGER 1.000 vs LEXICAL 0.808.
  * CUE, INTACT natural LitBank passages (n=86): LEDGER 0.930 [0.872,0.977] vs LEXICAL 0.581 (CI-sep, twin loses).
  * END-TO-END via LANDED belief_partition: LEDGER 0.988 [0.972,1.000] vs LEXICAL 0.500 vs ORACLE 1.000 (> 0.821).
  * DISTANCE invariance: spatial route 0.99 at K=0..20 filler sentences over full text; a 3-sentence WINDOW
    collapses 0.99(K=0)→0.00(K≥2) — proves the intact-window spatial chance score is a WINDOWING artifact.
  * OCCLUSION discriminators 6/6 (transparent-vs-opaque container, silent-vs-loud-in-dark, behind-screen,
    not-attending); a coarse single-gate baseline fails 2/6. SEQUENTIAL 4/4 (A→B→C→believes B; watched-into-box→
    destination-frozen; already-hidden→IGNORANT; two-agent→divergent). TESTIMONY 3/3 (truth→true, lie→false-
    matching-the-lie, distrusted→discounted).
  FLOOR = the LANDED lexical extractor recomputed per gold (0.500 corpus / 0.808 authored) + majority 0.500.

HONEST SCOPE (read before quoting):
  * The corpus gold is corpus-GROUNDED, not intact-natural-SCENE: its observation-cue CLAUSE is real LitBank prose
    (mined from 100 novels by a broad net) with a ground-truth-by-construction label, in a canonical frame. Finding
    (bar #4's honest gap): intact false-belief-about-an-object SCENES are TOO SPARSE to mine at scale (991 marker
    windows, mostly idiom/dialogue/unfamiliar-person), and clean presence/absence mining is bounded by verb
    POLYSEMY. Label precision ~90% after metaphor/transitive/speech-tag filters; the 0.99-vs-0.50 gap dwarfs it.
  * On intact WINDOWS the win is RULE 0 (broad explicit-marker coverage); the SPATIAL route (RULE 1) needs the FULL
    incremental situation model — proven at 0.99 over full text (distance item), chance under a window. Do NOT quote
    the intact 0.930 as a spatial-inference result. First-order belief only. Coref is a simple proxy (single-
    protagonist ok; multi-character prose is coref-bound).

PROPOSED hdlab (you land — Q111; validated in experiments/, NOT written to hdlab/):
  1. Promote experiments/perceptual_access_ledger.py → hdlab/perceptual_access.py (default-off island, like
     belief_partition). Wire: for each (agent, object-move) the situation model surfaces, observed() → belief_
     partition.form_belief(...). RUN OVER THE FULL running situation model, NOT windows (the spatial route needs the
     history). Consume the coref / situation-model organs for mention + event localisation (currently a spaCy proxy).
  2. Extend belief_partition from the binary believed_location(observed, initial, final) to a SEQUENCE registration
     ledger + an IGNORANCE (None) state + testimony that writes the ASSERTED location with a trust flag — the shape
     is validated in perceptual_access_ledger.sequential_registration() + belief_of/is_false_belief/is_ignorant.
  3. Do NOT touch the belief mechanism/controls/dissociations (DONE + LANDED). Witnesses above are the landed-VET gates.

ADJACENT GAPS = candidate focused-solver briefs (grounded on disk; ranked):
  1. NO SPACE dimension in the situation model [highest] — situation organs track (entity,role,event), NOT
     location-over-time; my ledger is a stopgap. A per-entity location register is a shared, missing organ.
  2. COREFERENCE ~0.65 on real narrative (coreference_resolver.py) — caps the cue on multi-character prose.
  3. VERB POLYSEMY / word-sense — cross-cutting wall (bit both extractor and gold labels); no glass-box WSD.
  4. OBJECT-STATE-CHANGE / SEQUENCE event extraction — the missing input stage that supplies "what changed, where".
  5. belief_partition is a default-off island with NO live belief-question task — the gating adjacency for VALUE.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md §2b ToM): the residual now has a brain-faithful mechanism (spatial-
  presence registration ledger). Add OCCLUSION (per-modality field) + verb POLYSEMY as first-class walls (NOT
  coref-specific). Record the two-route dissociation (explicit-marker RULE 0 local vs spatial RULE 1 needs the full
  incremental model) and SEQUENTIAL registration + IGNORANCE + motion-persistence. The lexical extractor is an
  OUR-INVENTION stand-in that does NOT generalise (0.808 → 0.500 on real prose).

KEY REALIZATIONS: false belief = the ledger being STALE (no separate computation); PATH lives in the SATELLITE not
  the verb (a verb-whitelist is the implementation trap the brain doesn't have); the REAL walls are occlusion +
  polysemy, not coref; the "ledger" formalism only earns its name over a SEQUENCE — and the sequence exposed two
  bugs a single move hides (occlusion window read one sentence PAST the event; RULE 0 leaked a move-1 marker onto
  move 2 — markers are event-local).

DO NOT QUOTE: the intact 0.930 as spatial inference; the corpus gold as intact-natural scenes; coref/SPACE-organ as
  mine to fix (adjacent, filed above); the lexical 0.808 as its real-prose accuracy (it's 0.500 on corpus prose).

FILES (all in my lane; NO hdlab/): experiments/perceptual_access_ledger.py; exp_perceptual_access_{corpus,intact,
  distance}_v1.py; mine_{presence_phrasings,false_belief_corpus}_v1.py; verification/test_perceptual_access_ledger.py
  + test_perceptual_field_occlusion.py + test_sequential_registration.py + test_testimony_reliability.py;
  notes/problems/<slug>/{BRAIN_MECHANISM_SPEC.md, SOLVED.md}; data/exp_perceptual_access_*/ + data/mine_*/.

TLDR (plain language): We had a reader that correctly tracks what a story character believes — but only when
  handed the answer to "did this character actually see the thing change?" Reading that one fact from ordinary prose
  was the last weak link, done with a phrase list that works on tidy examples (81%) and falls to a coin flip (50%)
  on real novel language. I rebuilt it the brain's way: keep a running note of where each character is, whether
  anything blocks their view (a wall, sleep, darkness, a closed box vs a glass one), and whether they were told —
  and mark them as knowing only when they were actually there and able to perceive it, or were told by someone they
  trust. On a test built from real sentences pulled from 100 novels it gets it right 98–99% versus 50%, never wins
  by luck (a scrambled version is a coin flip), and lifts the whole ability from 82% to 99%. It also now handles
  chains of moves (sees the first, misses the second → believes the middle spot), keeps tracking a thing it watched
  go into a box, tells ignorance apart from a wrong belief, tracks two characters who saw different things, and
  handles being lied to (believes the lie) versus being lied to by someone it distrusts (ignores it). Two honest
  limits: whole intact false-belief SCENES are rare in real books, so the main test frames real absence/presence
  SENTENCES; and word ambiguity ("left the room" vs "left a letter") is a wall the brain crosses with full
  understanding and we only partly can.

QUESTIONS: none blocking. NEXT STEPS (you): (1) re-verify with the 4 witnesses; (2) fold the AUDIT UPDATE into
  BRAIN_FOUNDATIONAL_AUDIT.md §2b; (3) land hdlab/perceptual_access.py + the belief_partition sequence/ignorance/
  testimony extension, run over the full situation model; (4) file the 5 adjacency briefs as focused-solver
  problems. The 30-min deepening cron keeps probing in the background — CronDelete it once integrated.
