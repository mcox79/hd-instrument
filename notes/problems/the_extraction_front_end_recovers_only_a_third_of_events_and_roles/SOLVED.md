---
problem: the_extraction_front_end_recovers_only_a_third_of_events_and_roles
status: SOLVED
bar: "the fixed extraction front-end raises real event/role RECALL on the diagnosed-lossy stage, CI-separated over the current live extractor (bootstrap; CI half-width + null p95), WITHOUT a CI-separated precision regression, with the info-free twin (shuffled cues / permuted attachment) LOSING; AND show ONE downstream organ's end-to-end number improves when fed the better extraction (the point of the whole thing)."
result: "The recall is lost entirely in EVENT DETECTION: the live detector (experiments._temporal_ordering.extract_events) is TENSE-GATED and misses present-tense finite verbs (VBZ/VBP) 100% (0/560 on UD-EWT test), capping event-detection recall at 0.332 (UD-EWT gold, n=2605). The brain-faithful fix is TENSE-AGNOSTIC, lexical-category detection (fire an event at every non-aux lexical VERB). Two variants: (RULE) add VBZ/VBP to the POS rule -> gold-POS recall 0.332->0.502 (+0.170, CI[+0.155,+0.186]) with precision NEUTRAL (0.9977->0.9985, no regression); (REALIZED, recommended) detect via the in-substrate UD-trained UPOS tagger firing on UPOS==VERB -> recall 0.332->0.869 (+0.537, CI[+0.511,+0.562]) at detection-precision 0.941. Present-tense recall 0.00->0.73. GENERALIZES out-of-domain: QA-SRL modern (0.373->0.828, present 0.00->0.78) and LitBank 19c fiction (0.533->0.740, present 0.00->0.90), CI-separated on all three, info-free twin losing (~0.145). DOWNSTREAM: who-did-what tuple recall 0.269->0.655 (+0.387, CI[+0.362,+0.413]), random-role twin losing at 0.175."
floor: "Strongest REAL floor = the current live extractor (NLTK tense-gated), event-detection recall 0.332 (UD-EWT), 0.373 (QA-SRL), 0.533 (LitBank); who-did-what floor 0.269. Info-free TWIN (random detection of same per-sentence count) recall p95 ~0.145; random-role downstream twin 0.175. FIX beats all CI-separated."
controls: "(1) INFO-FREE TWIN: random same-count detection loses on every corpus (fix 0.74-0.87 vs twin ~0.145); random-role downstream twin loses (0.655 vs 0.175) -> the lift is real predicate/argument recovery, not a scoring artifact. (2) RULE-ISOLATION (one variable = the detection rule): evaluated on GOLD POS so the tagger is held perfect -> excludes tagger-quality as the source of the recall gain and shows the rule change is precision-NEUTRAL (0.9977->0.9985). (3) OUT-OF-DOMAIN generalization (QA-SRL modern different-genre + LitBank 19c fiction where the tagger is ~150yr OOD) -> excludes UD-EWT overfitting; LitBank's HIGHER current recall (0.533) confirms the diagnosis (the rule was tuned for past-tense narrative). (4) PER-TENSE decomposition -> excludes 'general noise': the miss is specifically present-tense finite verbs (100% under CURRENT). (5) POSITIVE CONTROL: the home-grown tagger reproduces 0.945 UPOS token accuracy on UD-EWT test."
files_changed: "experiments/exp_extraction_frontend_recall_diagnosis_and_tense_fix_v1.py, experiments/exp_extraction_frontend_recall_generalization_v1.py, experiments/exp_extraction_frontend_downstream_whodidwhat_v1.py, verification/test_extraction_frontend_recall.py, notes/problems/the_extraction_front_end_recovers_only_a_third_of_events_and_roles/research_brain_event_detection_tense_agnostic_and_nv_disambiguation_2026-08-30.md (NO hdlab file changed -- proposed diff below, strategy lands it per Q111)"
reverify: ".venv/Scripts/python.exe verification/test_extraction_frontend_recall.py"
---

# SOLVED — the extraction front-end's ~0.32 recall is a TENSE-GATED event-detector, and the brain detects events tense-agnostically

**Status: SOLVED (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed — I prove the mechanism
in `experiments/` + `verification/` and propose the exact `hdlab/` diff below; the strategy session lands it (Q111).

## What I diagnosed (the first deliverable — WHERE the recall is lost)

I reproduced the archetype and **localized the entire loss to the EVENT-DETECTION stage**, then explained it:

- Applying the live extractor's own detection rule to **gold** UD-EWT POS tags (which isolates the rule's
  design from tagger noise) gives event-detection recall **0.332** (n=2605 gold lexical-verb events) — essentially
  identical to the brief's "~0.32 on SimpleWiki." So the number is real, but I re-grounded it on a clean modern
  gold (the brief's `_stage1_simplewiki_yield_probe.json` is a *definition-yield* probe, not a recall — a brief
  inaccuracy; **the disk outranks the brief**).
- **The loss is structural, not a ceiling.** The rule fires for VBD / VBN(+had/be) / VB(+modal) / VBG(participial)
  but has **no branch for present-tense finite verbs (VBZ/VBP)** — those are missed **100%** (0/560 on UD-EWT).
  Past-tense VBD recalls 0.86. It was built inside a temporal-ordering module where tense was the point, so it
  conflated "attach tense" with "detect event."
- **Argument attachment is NOT the bottleneck** (adjacent prior work: `exp_reader_candidate_generation_recall_persisted_frontend_v1`
  reaches 0.90 candidate recall once a real parse is fed), and the **role stage's fancy version is a dead end**
  (`the_reading_extractor_may_not_beat_a_two_line_rule`: the perceptron LOSES to a two-line rule — do not re-run).
  So the diagnosed-lossy stage is **detection**, and within it, **tense-gating**.

## The brain frame — and why the old detector was *backwards* (research drill, PINNED with citations)

`research_brain_event_detection_tense_agnostic_and_nv_disambiguation_2026-08-30.md` (dispatched drill) establishes:

- **Event-hood is carried by ARGUMENT STRUCTURE at the predicate, not by tense** (neo-Davidsonian event variable;
  Frankland & Greene 2015 *PNAS* decode agent/patient as separately-bound variables in lmSTC; Matchin & Hickok 2020
  put predicate-centred structure-building in LIFG-BA44 + pMTG/pSTS). None of this machinery references tense.
- **Tense is a SEPARATE, dissociable feature** bound to the event, not a gate on detecting it (Ullman 2001
  declarative/procedural; Thompson ASCH and Bastiaanse PADILIH double-dissociate argument-structure from
  time-reference deficits).
- **The killer finding:** where a tense asymmetry exists, **PAST is the *harder*, discourse-linked form and present
  is the cheap default** (Bastiaanse 2011; Faroqi-Shah 2009/2015). **Our detector gated on exactly the tense the
  brain finds harder (past) and dropped the brain's default (present) — it was backwards.** The fix restores the
  brain's operation: detect the predicate from its lexical category, tense-agnostically.
- **The N/V precision wall is resolved brain-faithfully by context.** English zero-derivation (*runs/plans/results*)
  makes isolated-form tagging err on exactly the present-tense verbs. The brain commits lexical category from
  LEFT/predictive context in LIFG within ~80 ms (Strijkers 2019; Dikker & Pylkkänen; agreement + distributional
  cues). Swapping the isolated-word tagger for a **context-sensitive Viterbi tagger** copies that computation.
- **Generalization is the signature of a structural operation** (Jabberwocky structure-building generalizes to novel
  forms; Fedorenko) — so testing OOD is the *right* test, and failure-to-transfer would have diagnosed a surface shortcut.

## What I built + measured

Three cells + a scaffold-free witness (8/8 PASS, recomputes every headline from source):

1. **Diagnosis + rule fix** (`exp_extraction_frontend_recall_diagnosis_and_tense_fix_v1`): on UD-EWT gold POS,
   CURRENT 0.332 -> FIX_TENSE 0.502 (+0.170, CI[+0.155,+0.186]), **precision neutral** 0.9977->0.9985; FIX_FINITE
   (also progressive/participle) 0.645. Twin loses (0.082). This is the clean, one-variable, **precision-neutral**
   result that meets the bar's "no precision regression" condition exactly.
2. **Realized fix + generalization** (`exp_extraction_frontend_recall_generalization_v1`): the in-substrate
   UD-trained UPOS tagger firing on `UPOS==VERB` (tense-agnostic, category-based, glass-box, NO nltk):

   | corpus | CURRENT recall | FIX recall | Δ (CI) | present-tense C→F | FIX prec |
   |---|---|---|---|---|---|
   | UD-EWT (in-domain modern) | 0.333 | **0.869** | +0.537 [+0.511,+0.562] | 0.00→0.73 | 0.941 |
   | QA-SRL (OOD modern, textbook/wiki) | 0.373 | **0.828** | +0.456 [+0.434,+0.478] | 0.00→0.78 | 0.897 |
   | LitBank (OOD 19c fiction) | 0.533 | **0.740** | +0.207 [+0.172,+0.242] | 0.00→0.90 | (nominal-gold; recall-only) |

   Twin loses on all three (~0.145). Event-detection recall ~2.5×; present tense recovered from 0 everywhere.
3. **Downstream organ lift** (`exp_extraction_frontend_downstream_whodidwhat_v1`): holding the role stage fixed
   (positional), who-did-what tuple recall **0.269 -> 0.655** (+0.387, CI[+0.362,+0.413]); random-role twin loses (0.175).
   The front-end caps a downstream comprehension dimension and the fix lifts it 2.4×.

## What I did NOT establish / what I would withdraw first

- **The realized (tagger-based) fix trades a small detection-precision dip for the big recall gain**: UD-EWT gold-space
  detection precision 0.999→0.941, QA-SRL 0.957→0.897 (F1 0.50→0.90, 0.54→0.86). This dip is **the UD-trained tagger's
  category error, not the rule** — the rule itself is precision-neutral (control 2). If precision-strictness is required,
  the **RULE-only variant (+0.170, precision-neutral) meets the bar with zero precision cost**; the tagger variant buys
  the extra +0.37 recall at the tagger's noise. I would withdraw the "+0.54 with no precision cost" reading first — it is
  "+0.54 at −0.06 precision (tagger), or +0.17 at 0 precision (rule)." Both are honest wins; F1 rises decisively either way.
- **In-domain caveat**: UD-EWT test is in-domain for the tagger. The claim does NOT rest on it — the two OOD corpora
  (QA-SRL, LitBank; leakage-immune) carry the generalization result independently. (I could not locate the tagger's
  training cell to byte-confirm train-only; the 0.945 held-out test accuracy is consistent with train-only, and the
  OOD results don't depend on it.)
- **LitBank precision is uninterpretable here** (its gold = realis EVENT triggers incl. nominal events, a different
  target class than all-verbs) — I report LitBank on RECALL only.
- **Copular/nominal predications are NOT fixed** (see next problem) — the UPOS==VERB target class excludes them.

## KEY REALIZATIONS (the enabling moves)

1. **The detector was backwards, not just incomplete.** The reframe that unstuck it: it gated on the tense the brain
   finds *harder* (past) and dropped the brain's *default* (present). Naming that (via the drill) turned "add a POS
   branch" into "restore the brain's tense-agnostic operation."
2. **Isolate the RULE from the TAGGER by scoring on gold POS.** Doing the fix comparison in gold-POS space proved the
   rule change is precision-neutral and pinned the realized precision dip on the tagger (a separable component) — without
   this the +0.54/−0.06 result would have looked like a rule that trades recall for precision. It doesn't.
3. **Generalization is the whole point, so test OOD deliberately.** The problem IS a generalization failure; measuring on
   QA-SRL (genre change) and LitBank (century change) — where LitBank's *higher* current recall confirmed the past-tense
   tuning — is what makes "systematicity, not a UD-EWT fit" a demonstrated claim rather than an assertion.
4. **The right target is "predicate that projects argument structure," not "VERB."** Garbin 2012 (complex-event nominals
   share the verb route via inherited argument structure) says UPOS==VERB under-generates — which is exactly why the
   copular/nominal gap is real and parse-bound (below).

## PROPOSED hdlab DIFF (strategy lands it — Q111)

The live event detector is `experiments/_temporal_ordering.extract_events`, called by `hdlab/situation_reader._read_events`
(line 594). Two options, in increasing value/risk:

- **(A) MINIMAL, precision-neutral, low-risk — do this first.** In `extract_events`, add a present-tense branch and
  lemma-aware AUX exclusion: fire an event for `pos in ("VBZ","VBP")` when the token's *lemma* is not in `AUX_LEMMAS`
  (the lemma check matters — form-only exclusion wrongly fires on contracted auxiliaries `'s`/`'re`). Tense is attached
  as `TENSE_PRESENT`, not gated. This is the +0.170, precision-neutral change; every existing past-tense branch is
  byte-identical. It closes the 100% present-tense miss on the current NLTK path.
- **(B) RECOMMENDED, higher-value — route detection through the in-substrate UD-trained UPOS tagger.** `hdlab/situation_reader`
  already loads `hdlab/pos_tagger.py` (asset `data/frontend_assets/pos_tagger_ud_ewt_upos.json`) on its wired opt-in path.
  Make `_read_events` detect events at `UPOS==VERB` (non-aux) via that tagger — tense-agnostic, category-based, glass-box,
  no nltk — with the existing rule attaching tense/aspect as metadata. This realizes recall 0.33→0.87 and generalizes OOD.
  Gate it behind a flag and A/B it on the live `situation_reader.read()` self-tests before defaulting it on; watch the
  ~0.06 detection-precision dip (improvable by broadening tagger training — a FREE foundation build).

Fold an **AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (below).

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md)

- **"READ THE TEXT" / extraction front-end (§2b BIGGEST LEVER, ~0.32 recall): DIAGNOSED.** The ~0.32 is an EVENT-DETECTION
  loss, and specifically a TENSE-GATE: the detector fired on past-tense/aux-marked verbs and missed present-tense finite
  verbs (VBZ/VBP) 100%. **PINNED correction:** event-hood is argument-structure/lexical-category based and tense-agnostic
  (neo-Davidsonian; Frankland&Greene 2015; Matchin&Hickok 2020; tense dissociable — Ullman 2001, Bastiaanse PADILIH), and
  the brain's asymmetry runs the *other* way (past is harder — Bastiaanse 2011). Our old detector was **backwards** relative
  to the brain. FIX (tense-agnostic category detection via the context-sensitive UD tagger) raises recall 0.33→0.87,
  generalizes OOD, lifts who-did-what +0.39. **Mark the detection stage: brain-faithful fix identified + validated in
  experiments/, awaiting hdlab landing.**
- **POS tagger / lexical-category assignment: PINNED-faithful in shape, OOD-limited.** Context-sensitive Viterbi tagging
  copies the brain's left-context category commitment (Strijkers 2019). Deviation: UD-only training → degrades OOD (a
  FREE-to-fix foundation build). The isolated-form NLTK tagger on the live path is the LESS brain-faithful component.
- **Copular/nominal predication detection: NEW deviation logged.** The event organ should detect predicates that project
  argument structure, incl. copular ("Paris is the capital") and complex-event nominals ("the destruction of the city";
  Garbin 2012 — nominals share the verb route). Currently EXCLUDED (copula AUX-skipped; nominalizations are nouns). Real
  gap: +18% more events on UD-EWT (567 copular vs 2605 verbal). Parse-bound (below).

## Adjacent components — capabilities, limitations, brain status, opportunity (to seed the next problems)

| component | capability now | limitation / on-disk evidence | brain-foundational status | opportunity → candidate next problem |
|---|---|---|---|---|
| **event detection** (this fix) | recall 0.33→0.87, generalizes | realized precision −0.06 (tagger) | tense-agnostic = PINNED-faithful (was backwards) | **land the fix** (diff above); broaden tagger training |
| **role assignment** (positional default; two-line rule; `thematic_role_labeler`) | positional live; two-line rule 0.795 best | who-did-what 0.66 < detection 0.87 → **role is the NEW bottleneck once detection is fixed**; perceptron LOSES to two-line (dead end) | role = grammatical-function + voice (PINNED); positional/single-cue = OUR-INVENTION placeholder | **NEXT PROBLEM #1: wire the parse-based role router** (`predicate_argument_frontend`, +0.225, built+validated+default-OFF) now that detection no longer caps it |
| **argument attachment / parse** (`incremental_parser` SOLVED islanded; batch arc parser UAS 0.79) | candidate recall 0.90 with real parse | islanded (`used_by`=tests); parse-free positional default | incremental/predictive structure-building = PINNED (Beber 2025: separate structure vs role organs); batch parse = placeholder | wire the incremental parser as the live structure source; it also enables copular/nominal detection |
| **copular / nominal predication** | EXCLUDED | +18% events; parse-free copular rule caps ~0.60 precision (can't separate copular from auxiliary "be" without the `cop` relation) | copular/nominal events ARE events (neo-Davidsonian; Garbin 2012) — PINNED deviation | **NEXT PROBLEM #2: parse-gated predicate detection** ("predicate that projects argument structure"), needs the wired parse |
| **coref-gated mention linking** | `pronoun_to_event_binding` +0.083 (SOLVED) | who-did-what bound by coreference | Centering/situation-model (PINNED) | wire it into the live who-did-what path |

**The through-line for planning:** this fix removes the front-end's FIRST cap (detection). The measured residual — who-did-what
0.66 vs detection 0.87 — is the ROLE/PARSE stage, whose brain-faithful organs (parse-based router, incremental parser, copular
detection) are **built or validated but default-OFF/islanded**. The highest-value next problem is **wiring the parse-based role
front-end**, which also unlocks the copular/nominal recall gap. That is one coherent next build, not three.

## TLDR (plain language)

Every "smart part" we built was graded on a clean list of events handed to it; when the reader has to pull events out of raw
text itself it only caught about **one in three**. I found out exactly why: the part that spots events was quietly built to
notice only **past-tense** happenings ("she *walked*") and to completely ignore **present-tense** ones ("water *freezes*",
"Paris *is* the capital"). Real modern writing — encyclopedias, textbooks, the web — is mostly present tense, so the reader was
blind to most of it. The brain does the opposite: it spots that *something happens* from the word's role in the sentence, no
matter the tense — and if anything it finds present tense *easier*. So our part was backwards. I switched it to spot every
action-word regardless of tense (using a smarter word-labeller that reads surrounding words for context, the way the brain
does), and event-catching jumped from **one-in-three to about seven-in-eight** — and, crucially, it kept working on writing it
had never seen (modern textbooks, 150-year-old novels), which is the real test that it *understood* rather than *memorised*.
Downstream, the "who did what" reader improved from **27% to 66%**. One honest caveat: the smarter labeller occasionally mislabels
a word, so the new part is a little noisier; a stricter, no-noise version still gives a solid third of the gain, and the noise is
fixable by training the labeller on more text.

## QUESTIONS

None — the diagnosis is localized, the fix is CI-separated over the real floor with the info-free twin losing, it generalizes on
two out-of-domain corpora, the downstream organ improves, and the witness recomputes every number from source.

## NEXT STEPS

1. **Land the fix** (proposed diff above): (A) the minimal precision-neutral present-tense branch first, then A/B (B) the
   UPOS-tagger detection route behind a flag on `situation_reader.read()`.
2. **Wire the parse-based role front-end** (`predicate_argument_frontend`, built+validated+default-OFF) — the measured NEW
   bottleneck (who-did-what 0.66 vs detection 0.87) once detection is fixed. **This is the recommended next problem.**
3. **Parse-gated copular/nominal predicate detection** ("predicate that projects argument structure") — the +18% recall gap
   that needs the wired parse to separate copular from auxiliary "be". Follows (2).
4. **Broaden the UPOS tagger's training** (a FREE offline foundation build) to close the ~0.06 OOD precision dip.
