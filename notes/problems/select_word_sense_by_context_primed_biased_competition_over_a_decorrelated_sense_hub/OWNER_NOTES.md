---
owner_verdict: DONE
---

SUBMISSION — select_word_sense_by_context_primed_biased_competition_over_a_decorrelated_sense_hub
status: REFUTED (full-pass located negative) + 3 banked positives + a promotion-ready reader. WIP until owner_verdict: DONE.

WHAT THE BRIEF ASKED: decorrelate the near-collinear sense hub AND select by discourse-primed biased competition, to
crack the ~0.33 fine-sense ceiling — glass-box, no trained encoder.

CORE RESULT — the brief's mechanism is REFUTED, three ways, and the standing no-encoder-invariant is SETTLED:
  • The within-word collinearity is REAL (0.923 on the actual meaning_foundation asset) — but it's the brain's
    graded shared-core POLYSEMY structure, not a bug. Decorrelating the hub is (1) provably accuracy-NEUTRAL for the
    cosine-argmax readout (common-mode removal changes 0 of 50,386 picks — the argmax already reads only the
    distinctive residual), (2) empirically NEGATIVE when it reweights (global whitening −0.015 a_s / −0.013 WiC,
    CI-sep below), and (3) brain-UNFAITHFUL: the ATL DISTILLS (Patterson-Nestor-Rogers 2007), decorrelation is a
    HIPPOCAMPAL job (CLS 1995), polysemy shares a core (Rodd 2002). The unverified prior-art +0.0176 whitening lift
    is RETRACTED (small-sample noise; CI-sep negative at full n). Modern WiC + SemCor both agree.

REFUTING WAS THE HALFWAY POINT — I built the brain's ACTUAL mechanisms (4 research drills) and drilled every wall:
  • Context de-blur (Kintsch construction-integration): −0.04 to −0.06 — resolving context words to gloss senses
    loses the rich distributional signal.
  • Distinctive-feature IDF resupply: right op for meaning-IDENTITY (SimLex) but WRONG for context-SELECTION (−0.17).
  • Thematic-fit selectional preference (Erk-distributional, parsed gov-predicate+role): REAL (beats role/verb twins
    CI-sep) but topical-context-DOMINATED — a fair multi-cue integrator gives it weight w*=0.00 (replicates Lee&Ng
    2002 −0.6pp + this project's own +0.007 + 5 external studies). Coarse-only by construction.
  • Joint-role bind (Lenci ECU): BIND (multiplicative) > BUNDLE (additive) CI-sep — but still bag-dominated.
  • Metusalem discourse-event prior: REAL (beats scrambled-discourse +0.020 CI-sep, COLLAPSES in isolation per its
    own Exp-2 control) but bag-subsumed.
  CONVERGENCE (witness 9/9): every brain-faithful cue is real but subsumed by the LOCAL sentence. The ceiling is the
  CONTEXT-INPUT REPRESENTATION (sense-conflated word vectors), reachable only by the recurrent predictive-comprehension
  loop (Phase-1) — a glass-box program, NOT a barred encoder. HOLD the invariant, for the right reason.

CORRECTION I OWN: my first pass said "the ceiling needs a trained encoder." That was too strong — the brain uses none;
it uses glass-box structured predictive comprehension. Withdrawn and corrected in the doc.

BANKED POSITIVES (CI-separated, glass-box):
  • SHARED-CORE GRANULARITY: 37% of fine "errors" are near-misses inside the correct coarse sense. The reader's
    committed COARSE sense beats the coarse-MFS floor +0.1377 CI[+0.133,+0.143] AND a context-shuffle twin +0.1104
    CI-sep (n=50,386, context-driven — not a lenient metric). Right form = compete FINE, deliver COARSE (beats
    merge-then-compete +0.043); underspecify the OUTPUT, not the COMPUTATION.
  • BIND > BUNDLE for joint-role composition (reusable substrate principle, CI-sep).
  • Metusalem discourse mechanism confirmed real (with its own falsification intact).

IMPLEMENTED — a PROMOTION-READY reference reader (I did NOT write hdlab/; Q111 reserves it for strategy):
  experiments/exp_underspecified_sense_reader_v1.py (witness verification/test_underspecified_sense_reader.py, 5/5)
  wires all four upgrades in one hdlab-promotable module: (1) underspecification-by-default (commit shared-core,
  retain fine); (2) cluster-first compute mode (56% fewer candidates); (3) bind joint composition; (4) the curated-hub
  wire + landed precision/Bayesian knobs. VERIFIED SAFE: mode="fine" at default knobs is a BYTE-IDENTICAL passthrough
  of the landed diagnostic readout (400/400) — promotion changes no existing behaviour.

hdlab LANDING (strategy, Q111 — exact spec in SOLVED.md §10e): promote the module to hdlab/underspecified_sense_reader.py;
wire situation_reader's read-time meaning stage to call it with the sglite-w2v lookup (curated hub default source),
emit the shared-core cluster as the committed sense, retain fine for on-demand elaboration, turn on the landed
gamma/topk/sense_prior knobs at go-live. Also the standing meaning WIRE (curated stack beats live PPR select_sense
+0.0633 on WiC). Coarse grain = WordNet supersense (CI-sep); a finer OntoNotes/CoarseWSD grouping is a 1-function drop-in.

NO OTHER DOWNSTREAM REGRESSION: I propose NO hub change (decorrelation refuted), so the hub's only read-time consumer
(the diagnostic readout) is untouched. AUDIT UPDATE folded (BRAIN_FOUNDATIONAL_AUDIT.md meaning §2b): remove hub
decorrelation from the lever list; add bind>bundle as a cross-cutting composition principle.

FILES: 11 experiments + 2 witnesses + SOLVED.md (all in files_changed). NO hdlab/ written. Glass-box, no LLM.
REVERIFY: .venv/Scripts/python.exe verification/test_sense_hub_separation_and_selection_organ.py   (9/9)
       && .venv/Scripts/python.exe verification/test_underspecified_sense_reader.py                (5/5)
