# DIAGNOSTIC (not a banked experiment): why 56/100 gold patients are never generated as reader candidates

Filed: 2026-07-23. Read-only analysis + light local instrumentation. No atoms banked, no push, no cell modified.

## HEADLINE

Of the 56 recall-miss gold patients in `exp_pivot_rich_knowledge_full_reader_integration_v1`
(recall_ceiling=0.44 over 100 gold-pos items, FULL_SLICE = L04/L05/L07/L08/L09/L10/L12), **54/56 (96%) are
EXTRACTION misses and only 2/56 (4%) are FILTER drops.** The prior VET's flagged "extraction-not-filter"
attribution is CONFIRMED, and the dominant mechanism is now identified precisely: it is **not** a window/
distance cutoff and **not** mainly a POS/stopword filter -- it is that the underlying hand-rule reader
(`exp_read_argstruct_goal_role_third_reader_v1` via `ORC.assign_roles_learned`) selects **exactly ONE
main verb per sentence** (`find_main_verb`: first non-auxiliary VB* token) and runs its single
AGENT/PATIENT/RECIPIENT/LOCATION role-assignment pass relative to that ONE verb only. Any other predicate
in the same sentence (coordinate VP, subordinate clause, complement clause) gets **zero candidates and zero
svo emission**, full stop -- unless it happens to be caught by the narrow explicit-relativizer nest module
(that/who/which/whom only).

## Method

Reused the cell's own `build_candidates(FULL_SLICE)` (from `exp_pivot_rich_knowledge_full_reader_integration_v1`,
which itself reuses `exp_learned_argstruct_parser_lccp_independent_gold_v1.load_slice_and_reader` /
`load_gold` VERBATIM -- no cell code modified). Reproduced the exact 56-miss set with the cell's own
`recall_miss` logic (`gold patient not in candidate patients for (sid, verb_lemma)`). For each miss, traced:
literal token presence in the tokenized sentence; whether the verb ever produced ANY svo tuple in that
sentence (pre- and post- the pivot script's own funcword filter); whether the sentence's single
`ORC.find_main_verb` pick equals the gold verb; whether the gold-patient token is a member of
`ORC.candidate_indices` (the POS/grounding gate); and structural context (preposition / complementizer
between verb and patient). Diagnostic script: `diag_recall_miss.py` (scratchpad, not committed to
`experiments/`).

## Per-category counts (sum = 56)

| Category | n | % |
|---|---|---|
| (d) NON-LOCAL / multi-predicate sentence (gold verb is not the sentence's single processed main verb) | 38 | 68% |
| (a) PARSE/ATTACHMENT miss (verb WAS processed, wrong patient attached or emission suppressed) | 16 | 29% |
| (c) POS/quantifier-pronoun candidate-gate drop | 2 | 4% |
| (b) window/distance cutoff | 0 | 0% |
| (e) tokenization/multiword | 0 | 0% |

Sub-split of (a) (16 total): 11 wrong-patient-attached (of which several are a coref-surface artifact, see
below); 4 zero-subject/imperative agent-gate failures (`if agents and patients` guard drops a perfectly
good patient candidate when no pre-verbal subject exists, e.g. imperatives "Build it up again", "Watch her");
1 other emission-suppression case.

**EXTRACTION-vs-FILTER split (the VET's headline question): 54/56 extraction (96%), 2/56 filter (4%).**
Verb-patient token distance among the resolvable misses: mean 2.07, median 2.0, max 6 -- i.e. these are NOT
distant candidates being cut off by a window; the code has no distance cutoff at all (confirmed by reading
`candidate_indices` / `assign_roles_learned` -- distance is only ever a soft classifier feature, never a
hard gate), so category (b) is genuinely zero, not just unobserved.

## Concrete examples (sourced, sid / sentence / mechanism)

- **d (dominant, 38x)**: `L04_03` "Herbert took up one of the blocks **and threw** it fiercely at pussy."
  main verb picked = `take`; `throw`/`it` never gets a role-assignment pass at all (verb_ever_emitted=False).
  `L04_07` "She did n't mean **to do** it!" main verb = `mean`; `do`/`it` never processed (infinitival
  complement of a clause-taking verb).
- **a - zero-subject/imperative (4x)**: `L04_10` `Build it up again." ` -- imperative, no agent candidate
  precedes the verb -> the reader's own emission guard (`if verb is not None and agents and patients`, in
  `exp_read_argstruct_goal_role_third_reader_v1.py:459`) drops the patient even though "it" IS a valid
  PATIENT-role candidate at distance 1 with `in_cand_gate=True`.
- **a - oblique/phrasal-verb (1x)**: `L04_12` "Pussy just rubbed **against** Herbert's castle" -- gold
  scores "castle" as `rub`'s patient, but "castle" is preposition-governed (`against`) so the reader's
  structural cues class it as oblique/LOCATION-like, not PATIENT -- a valency mismatch (phrasal-verb
  argument realized via PP not licensed as core-object).
- **a - coref-surface-vs-gold-surface mismatch (observed in >=3 of the 11 "wrong-patient" cases)**:
  `L07_01` "James Brown was ten years old when his parents **sent** him to school." reader_svo =
  `('sent','parents','james')` -- the reader's coreference resolver correctly resolved "him" -> "james"
  and substituted the resolved head into the emitted tuple; gold records the surface pronoun "him". The
  attachment is semantically RIGHT, but literal-string scoring (`g["patient"] == p`) counts it a miss. This
  is a **scoring-protocol artifact, not a knowledge gap** -- confirmed by direct inspection of `reader_svo`
  for `L07_01`/`L07_02`/`L10_09`/`L10_26`/`L12_10` (see raw dump in the diagnostic script output).
  `L07_02` and `L10_09` additionally show apparent parse/tagging-edge-case artifacts (patient = the verb's
  own lemma, e.g. `('sent','they','sent')`) -- flagged as a possible POS-tag or clause-boundary bug, not
  characterized further here (out of scope for this diagnostic).
- **c (2x)**: `L05_13` "the **one** pussy knocked down" -- "one" tagged `CD` (cardinal number), excluded by
  the POS/grounding candidate gate (not NN*, not in `PRONOUNS_SUBJ_OBJ`). `L10_14` "**Those** I saw upon a
  sign" -- fronted demonstrative pronoun "those" tagged `DT`, same gate miss.

## What structural knowledge would recover the biggest categories

1. **(d), 68% of misses -- the single highest-leverage fix.** The reader needs to stop being "one main verb
   per sentence" and become "one argument-structure pass per PREDICATE." Two concrete paths, both
   ingestible per the foundation-pivot (build-time tool, glass-box at runtime):
   - A real dependency parse (Universal Dependencies-style) that gives every finite/nonfinite verb its own
     nsubj/dobj/xcomp/ccomp slot directly -- this subsumes `find_main_verb` + single-pass role assignment
     entirely; multi-predicate sentences stop being a special case.
   - Short of a full reparse: VerbNet subcategorization frames PER VERB TOKEN (not per sentence) would at
     minimum tell the reader "this verb licenses/needs an object -- go find one in its own local span"
     for EVERY content verb encountered, not just the sentence's first one. This is the natural next rung
     above the already-built explicit-relativizer nest module (which does exactly this re-parse-a-span
     trick, but is gated on an explicit relativizer cue instead of on "any additional content verb").
2. **(a), 29% of misses, three distinct sub-fixes, none of them large single-resource ingests:**
   - Imperative / null-subject licensing (4/16): a cheap rule fix -- relax the `agents and patients` emission
     guard when the clause has no candidate before the verb AND the verb is sentence-initial (imperative
     mood), not a knowledge-ingestion item.
   - Phrasal-verb / oblique-as-core-argument valency (>=1/16): VerbNet subcat frames that mark specific
     verb+preposition pairs (rub-against, look-at, tread-on -- note the LCCP doc already treats look-at/
     tread-on as NOPAT-class verbs, so "rub against" being POS-class in this gold is an annotation-internal
     inconsistency worth flagging back to the gold, not just a reader gap).
   - Coref-surface-vs-gold-surface (>=3/16): NOT a knowledge gap -- an evaluation-harness fix (score against
     the coref-resolved head on both sides, or resolve gold pronouns through the same chain before matching).
3. **(c), 4% of misses**: extend the candidate POS-gate to admit partitive/demonstrative pro-forms ("one",
   "those", "these" used headlessly) as pronoun-like candidates -- a small, cheap POS-gate patch, not a
   resource ingest.

## Cross-thread synthesis

This directly answers the open question left by the pivot cell's VET (`exp_pivot_rich_knowledge_full_reader_
integration_v1`, HARD_FAIL_DOESNT_INTEGRATE_EXTRACTION_BOUND band): the rich selectional-knowledge lever
(29471/29472) cannot move the full reader's real accuracy because 96% of the ceiling loss is a genuine
extraction bound, and the extraction bound is dominated by a **single architectural limit** (one-verb-per-
sentence role assignment), not by the funcword/POS filter layer the selectional-knowledge cell shares
candidates through. Selectional/plausibility knowledge (the FIRST leg of the foundation, already built and
isolated-validated) is the wrong lever for this ceiling; it operates entirely downstream of where 68% of the
loss occurs.

## Substrate-product implications

The SECOND leg of the knowledge foundation (per the gating question) should be **structural/valency
knowledge that extends argument-structure processing to every predicate in a sentence**, not more
plausibility ratings. Two build-time-ingestible, glass-box-at-runtime candidates, ranked:
1. Per-verb-token subcategorization frames (VerbNet SELECT frames, or a build-time LLM-authored
   verb-frame table analogous to the rich_selectional_table.json pattern already proven safe) that let the
   reader open a NEW local argument-search scope at every content verb, not just the sentence's first.
2. A real dependency-parse upgrade (replacing `find_main_verb` + single global role pass) -- higher payoff,
   higher engineering cost; the multi-predicate wall is a parser-architecture ceiling, and VerbNet frames are
   the cheaper lever that could plausibly recover a large fraction of the 68% without a full reparse.
Separately and cheaply: fix the imperative-agent-gate rule (4/56) and the coref-vs-surface scoring mismatch
(>=3/56, likely 5-8/56 once fully audited) -- both are near-zero-cost, non-knowledge, code-level fixes that
would independently raise recall_ceiling by several points before any new resource is ingested.

## Cheap decisive test (if this diagnosis is acted on)

Build a small VerbNet-subcat-frame lookup (build-time, glass-box dict-lookup at runtime, same invariant as
rich_selectional_table.json) that, for the SAME FULL_SLICE + gold, allows a SECOND argument-structure pass
per sentence at the sentence's second content verb (only where the first pass's verb != gold verb for a
gold-pos item). HARD-PASS: recall_ceiling rises from 0.44 to >= 0.65 (recovers >= 60% of the 38 category-d
misses) with zero regression on the previously-recovered 44 items. HARD-FAIL: recall_ceiling rises by
< 0.05 (the second-verb re-parse does not generalize / the multipredicate cases need a real parse, not a
frame lookup).

## Citations

None (internal code-archaeology diagnostic; no external literature scan performed for this task).
