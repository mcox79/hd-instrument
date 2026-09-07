---
owner_verdict: DONE
---

SUBMISSION — represent_negation_and_quantifier_scope_for_truth_conditional_reading_modern_gold
STATUS: SOLVED (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM at inference, NO training.
NO hdlab/ written (Q111 — a PROPOSED additive diff, not landed). Ledger: malformed/incomplete 0.
Reverify: .venv/Scripts/python.exe verification/test_polarity_operator_ewt.py && ...test_quantifier_operator.py
  && ...test_polarity_operator_upgrades.py   (full suite: 8 witnesses / 28 checks + operator self-test 26/26)

WHAT I BUILT. A glass-box truth-conditional POLARITY + QUANTITY operator (experiments/_polarity_operator.py)
attached to the reader's already-extracted sm.events / argument set — it does NOT re-extract. It REUSES
hdlab/state_register.py verbatim (the +1/-1 polarity primitive, antonym/contradiction guards, the ATL-hub
WordNet entailment matcher) and EXTENDS the copular-state polarity onto EVENT propositions + a quantifier layer.
PINNED brain computation copied (Kaup-Zwaan two-step negation = toggle the ACTUAL state; Johnson-Laird
cardinality: none/no = ZERO tokens = ¬∃; scope = clause-local c-command, complement factuality from the matrix
verb's implicative/factive signature); parameters swept.

THE BAR IS MET on all counts — negation AND quantifier, reader-native headline + well-powered naturalistic
companion, CI-separated over a polarity/quantity-blind floor that LOSES (and INVERTS) and an info-free
shuffled-token twin, on MODERN gold:
 - NEGATION reader-native (UD-EWT sm.events, n=131): net factuality 0.9313 vs polarity-blind 0.5038
   (+0.4275 CI[0.344,0.512]); negated-recall 0.8769 vs blind 0.0000; over-negation 0.0000 clean —
   BEATS the prior negation_factuality_gate (MIDDLE_BAND, 0.0303 over-negation), and reader-native not gold-fixed.
 - NEGATION well-powered (MoNLI NMoNLI n=1202): operator 0.9965 vs blind 0.0035 (+0.9929 CI[0.988,0.997]);
   PMoNLI op==blind 1.0 (no positive regression); polarity detection 1.0. Ignoring one "not" doesn't just miss —
   it INVERTS the answer.
 - QUANTIFIER reader-native (constructed modern QA, n=585, verb-extraction 1.0): 1.0000 vs quantity-blind 0.5385
   (+0.4615 CI[0.421,0.503]); specific-exception ("everyone but Mary -> did Mary?") 1.0 vs blind 0.0.
 - QUANTIFIER well-powered (MED, naturalistic): downward-monotone n=563 operator 0.8259 vs monotone-blind 0.1741
   (+0.6519 CI[0.588,0.712]); the FULL unified operator over ALL decidable (n=3791) is 0.8225 vs blind 0.2849
   (+0.5376 CI[0.517,0.558]) and CI-sep over the twin (+0.2464).

CONTROLS: blind floor INVERTS on the monotonicity golds (positive control = polarity-respecting answer OPPOSITE
the blind one); info-free shuffled-token twin loses CI-sep on all four; ADDITIVE isolation (operator leaves
sm.events predicate/agent/patient/tense byte-identical — no downstream regress); ablation direct-only vs full
scope drives over-negation 0.0303 -> 0.0000.

UPGRADES IMPLEMENTED (each MEASURED for generality — the standing lesson):
 A implicative/factive lexicon -> 141 curated Karttunen/de Marneffe verbs (EWT no-regress).
 B NPI / negation-licensing UNIFICATION (biggest win): sentential negation IS a downward context (Ladusaw) —
   the same none=¬∃ unification. MED NPI subset 0.266->0.741; full operator coverage 0.490->0.704, acc 0.511->0.822.
 C restrictor-vs-scope monotonicity for universals (every/all restrictor is downward): universal subset 0.375->0.428.
 D PRECISE predominant-verb signal for the parser fix (replaces the permissive WordNet "any verb sense"):
   retag precision 0.037->0.208, general POS damage -165 -> -14 tokens.
 Plus P1 wired-reader landing prototype (downstream QA aware 1.00 vs blind 0.40), P2 unified state_match query,
   P4 scanner-consolidation proof (operator subsumes >=5 scattered hdlab negation scanners).

WALLS RESEARCHED TO MECHANISM (a rigorous negative is a full pass):
 - EWT residual: of 8 misses, ~6 are GOLD NOISE — the gold's own auto-propagation over-negates across
   contrastive "but" (the exact v1 bug: "can't help but trot it out" = trot DOES happen). My brain-faithful
   operator is MORE correct than its evaluation gold on these; noise-cleaned recall ~0.95.
 - Parser-attachment wall: the brain resolves scope structurally; our parse (UAS~0.79) injects errors. I built a
   parse-aware resolver + a brain-foundational repair (WordNet category + Frazier parallelism + subcategorization
   + shared-subject) that reaches the surface operator EXACTLY (0.9318) on the negation gold — NO training. BUT
   measured on general UD-EWT gold the blanket repair is net-negative (overfit); the SURFACE operator is the
   deployable primary; the general fix = precise VerbNet frames + tagger-confidence gating (foundation, no training).
 - Drilled a wall I had HAND-WAVED (MED "upward 0.43"): it was 43% negation-CONTAMINATION, not edit-noise —
   upgrade B recovers it (0.110->0.890). Corrected a wrong conclusion.
 - Out-of-brief adjacents named (not silently skipped): quantifier-QUANTIFIER scope ambiguity (∀∃), double negation.

KEY REALIZATIONS: (1) "none" IS negation (cardinality 0 == ¬∃) — one operator answers both golds, and unifying
negation with quantifier monotonicity was the single biggest lift (B). (2) Read the DETERMINER, not the reader's
noisy binding. (3) The complement gate (matrix verb's implicative signature), NOT negation propagation, is the
brain's mechanism — and it beats the prior wall. (4) The blind floor INVERTS, not just loses. (5) MEASURE every
"fix" for GENERALITY before deploying — a heuristic that won on the enriched gold was overfit on general text;
measuring it prevented a regression. (6) The parser residual is closed by KNOWLEDGE, not training — stored verb
argument structure corrected a parse attachment-level error with zero training.

FOR STRATEGY (Q111 — I propose, do NOT land): add default-None additive fields polarity/quantity(+exception)/
polarity_provenance to EventRecord; a default-off read_polarity flag on SituationReader running the operator over
each event + the coref-resolved subject NP (following the _read_state / predict_surprisal additive-wire template);
promote _polarity_operator.py as hdlab/polarity_operator.py; route event polarity through state_register.state_match.
AUDIT UPDATE: EventRecord carries no truth-polarity/quantity (now demonstrated CI-sep, and blind INVERTS); ≥5
scattered clause-local negation scanners are consolidatable under this one operator.

PRIORITY NEXT STEPS:
 P1 (HIGH, strategy-owned, ready now): LAND the operator + additive default-off read_polarity field + WIRE the QA
    capstone to answer polarity/quantity questions — the step that makes the gain board-visible (all downstream
    organs read propositions polarity-blind today).
 P2 (HIGH): UNIFY state_register copular polarity with event polarity under one state_match representation; folds
    in the scattered negation scanners (consolidation proof shows the operator subsumes them).
 P3 (lower): the parse-aware resolver + parser fix are prototyped + measured — do NOT deploy the repair (overfit);
    the general fix is precise VerbNet frames + tagger-confidence gating (foundation, no training). Follow-on problem.
 P4 (optional): extend the natural-logic engine to conditionals + phrase-level edits (conjunction already handled).

TLDR (plain English): the reader used to file every fact as true and about one thing — so "she didn't take the
key" became "she took it", "none of the guards moved" became "someone moved", "everyone but Mary agreed" filed
Mary as agreeing. I built the step that carries the little words — not, no, never, none, some, all, each — through
to the stored fact, reusing the machinery the reader already had for "she is / is not ill". On modern tests it gets
these right where a reader ignoring those words gets them exactly backwards (99.6% vs 0.4%; ignoring one "not"
flips the answer), correctly flags 88% of real-web negations the old reader flagged none of without ever wrongly
denying a plain positive, and is perfect on quantifiers where the old reading is a coin-flip. It beats an earlier
in-house attempt that got stuck, using the brain's actual rule for tricky cases ("she didn't remember him leaving"
still means he left). Transparent add-on, changes none of the reader's existing output.

QUESTIONS: none blocking. One judgement call: the reader-native quantifier headline is a constructed (templated)
modern set — I lead with it per the brief's "reader-native as HEADLINE" and back it with the naturalistic MED
companion; if you prefer, treat MED + the EWT negation headline as load-bearing and the constructed set as illustrative.
