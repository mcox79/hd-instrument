---
problem: the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses
status: SOLVED
bar: "PASS = a coverage recovery (attempt every finite verb + parser-robust candidate building, glass-box, NO LLM) that raises the LIVE reader's EFFECTIVE end-to-end who-did-what (abstention counted as wrong) CI-separated over the current 0.629, WITHOUT regressing the picked-clause NP-head precision (an explicit no-regression check on the accuracy the parent landed), with an info-free twin (recover random clauses) LOSING. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — the dropped clauses are genuinely un-recoverable glass-box, with the named cause + number — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed)."
result: "RECOMPUTED against the CURRENT live reader (the stored 0.6293 floor went STALE -- upstream modules landed DURING this work and lifted the live wired reader to 0.7877; predict_revise = +0.0643 of it). On the 669 clean-19c direct-object clauses, scorer pick==gold_head, effective end-to-end (abstention=wrong): CURRENT live wired 0.7877 -> STRUCTURAL recovery 0.9851, marginal +0.1973 CI[+0.1689,+0.2272] CI-separated. The recovery's contribution is now primarily ACCURACY (it fixes 65 of the reader's 75 remaining wrong picks) plus the 47 verb_subcat + 20 no-event abstentions. Modern QA-SRL (n=1261) 0.5678 -> 0.9025, +0.3347 CI-sep (modern floor not yet re-run against current substrate)."
floor: "Strongest floor actually run = the CURRENT live wired reader 0.7877 (predict_revise ON; recomputed first-hand, NOT the stale stored 0.6293). predict_revise OFF = 0.7235. The RECOVERED path beats the current floor +0.1973 CI[+0.1689,+0.2272]. best-available-parser wired floor (updated arc-eager UAS 0.842) 0.6308 at the time it was run -- also now superseded by the upstream lift. RETIRED as stale: the stored wired_pick 0.6293."
controls: "(1) info-free twin = full coverage + UNIFORM-RANDOM post-verbal pick 0.4185, LOSES CI-sep. (2) NO-REGRESSION: present-accuracy 0.807->0.981; 5 individual flips (hard ditransitive/copula/distant-noun). (3) INTRANSITIVE precision control (constructed, can-fail): naive soft rule over-generates on 100% of intransitives; STRUCTURAL-DO abstains correctly 0.975 AND recovers the 47 AND does not regress the main gold. (4) CURRENT-FLOOR recompute (first-hand): the recovery marginal is measured over the CURRENT 0.7877 reader, not the stale 0.6293; predict_revise attributed (+0.064). (5) fair-floor: the updated arc-eager parser recovers only 1/669 -> abstention was not parse-quality. (6) per-cause ablation is exhaustive."
files_changed: "experiments/exp_whodidwhat_coverage_diagnosis_v1.py, experiments/exp_whodidwhat_coverage_recover_v1.py, experiments/exp_whodidwhat_coverage_parser_floor_v1.py, experiments/exp_whodidwhat_coverage_transitivity_control_v1.py, experiments/exp_whodidwhat_verb_id_recoverable_v1.py, experiments/exp_whodidwhat_mention_source_transfer_v1.py, experiments/exp_whodidwhat_meaning_prediction_completeness_v1.py, experiments/exp_whodidwhat_live_wire_end_to_end_v1.py, experiments/exp_whodidwhat_current_floor_rediagnosis_v1.py, experiments/exp_whodidwhat_referent_per_np_prototype_v1.py, experiments/exp_whodidwhat_verbid_override_prototype_v1.py, experiments/exp_whodidwhat_ideal_brain_foundational_v1.py, experiments/exp_whodidwhat_noncanonical_upstream_v1.py, experiments/exp_whodidwhat_fillergap_fix_v1.py, experiments/exp_whodidwhat_composed_pipeline_v1.py, experiments/exp_whodidwhat_verbid_learned_combiner_v1.py, experiments/exp_whodidwhat_competent_reader_benchmark_v1.py, experiments/exp_whodidwhat_verbid_joint_pos_parse_v1.py, experiments/exp_whodidwhat_noncanonical_gold_rebuild_v1.py, experiments/exp_whodidwhat_fillergap_parse_v1.py, verification/test_whodidwhat_coverage.py, notes/problems/the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_whodidwhat_coverage.py"
---

# SOLVED — the who-did-what front end silently abstains on a fifth of answerable clauses

## What this problem asked, and the answer in one line
The live reader picks the patient right ~98% of the time WHEN it answers, but stays silent on 22% of answerable
clean-19c clauses, so its EFFECTIVE end-to-end who-did-what (silence counted as wrong) is only **0.629**. I diagnosed
the 22% first-hand into three exact causes, recovered them with a brain-faithful robust role path, and lifted the
effective end-to-end to **0.981** (+0.3513 CI-separated, info-free twin loses, no precision regression, generalizes
to modern text). The abstention was **never** a "the parser could not find the noun" problem — it is three
OUR-INVENTION precision gates mis-firing on 19c prose.

## 0. ⚠️ THE FLOOR MOVED DURING THIS WORK — recomputed honestly (cell: exp_whodidwhat_current_floor_rediagnosis_v1)
The substrate was being improved by the strategy session WHILE this problem was worked, so the numbers below that are
stated against the stored `wired_pick` (0.6293) are STALE. Recomputed first-hand against the CURRENT live reader:

| floor | effective (669 clean-19c DOs) | note |
|---|---|---|
| stored `wired_pick` (gold-build time) | 0.6293 | **STALE — retired** |
| current live wired, predict_revise OFF | 0.7235 | other landings lifted it +0.094 |
| **current live wired (the honest floor)** | **0.7877** | predict_revise adds +0.0643 |
| STRUCTURAL recovery (this work) | 0.9851 | **marginal +0.1973 CI[+0.1689,+0.2272] CI-sep** |

**What upstream already recovered, and where signal is NOW lost:** `predict_revise`'s drop-fill (landed 2026-09-01)
plus other landings recovered the **80 speech-quotative** event-no-patient drops entirely. The CURRENT reader's
remaining loss is: **75 WRONG picks (accuracy)** — of which the structural NP-head/DO recovery fixes **65** — plus
**47 verb_subcat** + **20 no-event** abstentions. So the bottleneck RE-LOCATED from coverage to ACCURACY: the
recovery is still worth +0.1973 CI-separated, but now chiefly as an accuracy fix (65 wrong picks) on top of the
coverage upstream recovered. The rest of this document's diagnosis (80/47/20) describes the state AT THE TIME it was
run and remains a correct account of the mechanism; only the headline floor is superseded by §0.

## 0b. THE CURRENT LOSSES, PINPOINTED + PROTOTYPED FIXES (the renewed optimization opportunity)
After the floor moved to 0.7877, I pinpointed every remaining loss first-hand and prototyped a fix for each. Ranked
by leverage:

**(1) REFERENT-PER-NP mention source — the biggest lever, prototyped and WORKING** (cell:
`exp_whodidwhat_referent_per_np_prototype_v1`). This is a DEPLOYMENT loss, not visible in the eval (which supplies
every noun): the live `read()` sources candidates from the coref column, so on the 25 real LitBank docs the gold
patient is a candidate only **0.8183** of the time (entity-type coref only). The brain opens a referent for EVERY NP
(Kamp 1981; Heim 1982). Prototype `referent_per_np_mentions` (a mention per content-noun head, coref demoted to a
downstream linking pass) lifts patient candidate-coverage to **0.9705, +0.1521** across 1354 clauses. Tractable,
brain-foundational, and it dwarfs the in-eval losses — the recommended next problem.

**(2) 20 NO-EVENT (verb mis-tagged) — prototyped, LOCATED PARTIAL** (cell: `exp_whodidwhat_verbid_override_prototype_v1`).
The tokens ARE verbs (18/20 WordNet). A combined glass-box override (WordNet verbhood AND (arc-eager parser attaches
it as a predicate head/root OR a Mintz subject-[verb]-object frame)) recovers **10/20** — but at **3.72 false-verbs
per sentence** (2417 spurious promotions on 649 clauses). Unusable as a heuristic: the recovery/precision tradeoff is
bad because content nouns routinely have verb readings and sit in noun-flanked frames. Clean recovery needs a
register-robust TRAINED predicate model — this is the honest scope of follow-on 1c (a heuristic will not do it).

**(3) 75 WRONG picks — 65 fixed by the structural-DO recovery (this work); the 10 residual pinpointed as follow-on 1d.**
Of the 10 the structural recovery still misses: **1** is a candidate-quality bug (it picked the pronoun "our" over
"people" — a drop-PRON-candidate fix), and **9 are genuine NON-CANONICAL constructions** outside this problem's
canonical-DO scope — object-complement/naming ("call her bungalow **a place**" → gold=place; "called _**hell**_" →
gold=regions), ditransitive ("gave the **man** godspeed" → gold=man/recipient; "paint you the dreamiest **bit**"),
and copula ("seemed odd **people**"). These are the VerbNet-double-object + animacy fix (Goldberg; Bresnan 2007) the
research called the cheapest win — they belong to the filed non-canonical-argument problem (1d), and the structural-DO
rule is correct-by-design to not claim them.

## 0c. THE IDEAL, FULLY BRAIN-FOUNDATIONAL PIPELINE — prototyped end-to-end (cell: exp_whodidwhat_ideal_brain_foundational_v1)
Composing every validated stage into one glass-box pipeline, each stage PINNED to a brain mechanism:
1. **Referent-per-NP** candidate source (Kamp 1981 DRT; Heim 1982) — a referent for every NP, coref downstream.
2. **Davidsonian** per-verb coverage (Davidson 1967).
3. **NP-head** identification (Williams 1981 RHR; Abney 1987 DP-head).
4. **Structural direct-object** filter (patient = bare post-verbal DO; obliques never — the patient-role definition).
5. **Competition-Model** role assignment (Bates & MacWhinney 1989) — the landed 8-cue graded competition.
6. **Animacy** for ditransitive (Bresnan et al. 2007) — recipient animate, theme inanimate.
7. **Predictive confidence** (Van Herten 2005 semantic P600) — surprisal as a conflict/abstain flag, NEVER auto-revise.

Measured on both regimes of the 5999-clause gold:

| regime | current live floor | IDEAL (routed) | vs floor | info-free twins | confidence AUC |
|---|---|---|---|---|---|
| CANONICAL (n=669) | 0.6293 | **0.9851** | +0.3558 CI[+0.321,+0.393] | shuf-reduce 0.954 / shuf-cue 0.924 (both lose) | 0.840 |
| NON-CANONICAL (n=729) | 0.0274 | **0.1385** | +0.1111 CI[+0.086,+0.136] | shuf-cue 0.074 (loses) | 0.701 |

**THE ARCHITECTURE FINDING — routing beats flat composition (more machinery is NOT better).** Piling every stage on
every clause (the "flat" ideal) scores only 0.8984 on canonical — the ditransitive/animacy machinery MIS-FIRES where
it does not belong. ROUTING it (the focused structural rule on canonical; the full multi-cue competition only on the
non-canonical residual) restores 0.9851 (+0.0867 CI-sep). This is the brain's own architecture — good-enough default
+ targeted reanalysis (Ferreira; Christiansen & Chater) — and it reproduces the substrate's landed "routing > flat"
result first-hand.

**THE NON-CANONICAL FRONTIER, TRACED TO ITS UPSTREAM SOURCE** (cell: exp_whodidwhat_noncanonical_upstream_v1) — it is
NOT primarily a parser gap; it is a LAYERED upstream problem, biggest layer first:
1. **~61% of the non-canonical gold is NOISE**, not a modeling frontier: 352/729 (48%) have an intransitive/low-
   transitivity verb so the preverbal "patient" is a mislabeled SUBJECT ("the bridges PEEPING", "SITS the lord"); 93
   (13%) are cross-clause segmentation mismatches (the gold belongs to a different clause of a long run-on). You
   cannot improve against a majority-noisy target — this is the PARENT problem's exact lesson (the who-did-what lever
   lives on a CLEANED gold), never applied to this slice. Cleaning is the first, biggest, most tractable lever.
2. On the CLEANED 39% (gold reachable 99.7%), the genuine issue is FILLER-GAP parsing (the active-filler strategy,
   Frazier & Clifton 1989): the clean cases are object-relatives/fronting ("the book [that I] read") where the patient
   is the relativized FILLER held across the embedded subject. A clause-window + object-gap->filler rule lifts the
   ideal 0.1385 (full) / 0.1620 (cleaned) -> **0.2254** (1.6x); the landed `resolve_patient` underperforms (0.1056 —
   it is tuned to a narrower relcl pattern).
3. The residual (0.23 -> 1.0) needs a joint generative event/VALENCE model — which candidate is a plausible theme of
   this verb, resolved jointly with the parse — the successor problem the prior work already named.
So "vastly improve non-canonical" = (1) CLEAN THE GOLD, (2) proper FILLER-GAP resolution, (3) a joint valence parser —
in that order. It is partly a parser gap (layer 2) but the dominant immediate blocker is gold noise (layer 1).

**ALL THREE LAYERS PROTOTYPED as a cumulative ladder (cell: exp_whodidwhat_fillergap_fix_v1) — honestly, 2 of 3 work:**
| layer | non-canonical acc | verdict |
|---|---|---|
| L0 ideal (full noisy) | 0.1385 | baseline |
| L1 + clean the gold | 0.1620 | ✓ works (+0.024) |
| **L2 + object-gap routing** (gap -> nearest-preverbal theme; unaccusative/fronting) | **0.2465** | ✓ **works, biggest lever (+0.085 CI-sep) — roughly DOUBLES L0** |
| L3 + joint valence re-rank (grounded fit + animacy) | 0.2113 | ✗ **REFUTED (−0.035)** — the meaning cue is too weak; the real valence parser needs the meaning channel fixed first |

Two honest NEGATIVES inside the prototype: (a) the SOPHISTICATED filler-gap (skip the embedded subject, take the noun
before the relativizer as the relative HEAD) is REFUTED — on the object-gap slice the SIMPLE nearest-preverbal rule
scores 0.741 vs the sophisticated rule's 0.345 (most clean non-canonical are unaccusative/fronting where the nearest
preverbal IS the patient, not object-relatives needing subject-skipping); (b) L3 grounded-valence re-ranking hurts,
re-confirming first-hand that who-did-what selection is not fit-quality-bound. Net: the tractable brain-foundational
fix (clean gold + route object-gaps to the preverbal theme) roughly doubles non-canonical (0.139 -> 0.247); the true
frontier remains the joint generative valence parser, which is gated on the (separately-filed) meaning channel.

**What this says about completeness (honest):** on CANONICAL who-did-what the ideal is at the parse ceiling (0.985),
fully brain-foundational, every info-free twin loses, and the predictive-confidence layer flags its own errors
(AUC 0.84). NON-CANONICAL (preverbal/fronted patients) is the genuine FRONTIER: the full Competition Model lifts it
5x off a near-zero floor (0.027 -> 0.139) — real and CI-separated — but it is far from solved, consistent with the
prior-work verdict that the non-canonical blowout is gated on a joint-generative valence parser (a named successor),
not on more cues here. So the ideal is COMPLETE and brain-foundational for the canonical regime; the honest remaining
depth is (a) the non-canonical frontier and (b) the referent-per-NP deployment source (§0b).

## 0d. THE IMPLEMENTATION — composed drop-in + per-stage SIGNAL-LOSS LEDGER (cell: exp_whodidwhat_composed_pipeline_v1)
All CONFIRMED brain-foundational STRUCTURAL fixes composed into one glass-box drop-in (`composed_who_did_what`):
referent-per-NP candidates → Davidsonian coverage → NP-head → route (canonical: structural-DO + competition;
non-canonical: nearest-preverbal theme) → predictive confidence. **L3 grounded-valence is EXCLUDED** — the
meaning-channel research (2026-09-03) CONFIRMED who-did-what selection is parse/structure-bound, not fit-bound
(structural roles ~0.996; the fit-gate tradeoff is irreducible), so a valence cue on selection is a fenced negative;
its real home is forward prediction, and the generative situation model is a separately-filed deep successor (priority
1, under the learner-on north star) — CITED, not opened here.

**Per-stage SIGNAL-LOSS LEDGER (where signal is lost, measured):**
| regime | ORACLE (gold reachable) | current floor | **COMPOSED** | residual loss to oracle | twin |
|---|---|---|---|---|---|
| CANONICAL (n=669) | 0.9895 | 0.6293 | **0.9596** | **0.0299 (near-saturated)** | 0.833 (loses) |
| NON-CANONICAL cleaned (n=284) | 0.9965 | 0.0704 | **0.2923** (4× floor) | **0.7042 (the frontier)** | — |

Reading the ledger: the structural pipeline **nearly saturates** canonical (only 0.030 of the reachable signal lost),
while non-canonical still loses **0.70** — recovered 4× off the floor by structure but the residual is gated on the
meaning channel (structural cues cannot close it; the generative situation model is the successor). Combined effective
0.7607. The confidence layer still flags the composed pipeline's own errors (surprisal wrong 2.60 > correct 1.66).
This is the reference drop-in the strategy session lands (Q111, default-off, witnessed).

## 0e. BRAIN-COMPARISON (performance-level) + the verb-ID located negative + scoped successors
**Verb-ID learned combiner — the research-confirmed fix, IMPLEMENTED and located as a HARD_FAIL** (cell:
`exp_whodidwhat_verbid_learned_combiner_v1`). Per the 2026-09-03 drill this is a "combiner not capability" problem: a
learned logistic weighting (WordNet + dependency-attachment + morphology + closed-class) over the same signals,
trained on UD gold. Result: UD verb recall +4pp, but on 19c at FP<=1.0/sentence recovery is only **0.05** (HARD_FAIL
vs the pre-registered recall+>=20pp @ FP<=1.0 bar). Mechanistic reason: the discriminative signal (dependency
attachment, learned weight 3.86) is **corrupted on the exact tokens** — the arc-eager parser inherits the POS
mis-tag, so the mis-tagged verb is not attached as a head. => the real fix is a **JOINT POS+parse retrain** (so the
parser does not inherit the mis-tag), not a combiner. Scoped as follow-on 1c with this evidence.

**COMPETENT-READER BENCHMARK — the brain-comparison, made performance-level** (cell:
`exp_whodidwhat_competent_reader_benchmark_v1`; spaCy REFERENCE-ONLY, never at inference — the diagnostic-oracle
exception): our glass-box pipeline vs a competent statistical parser (spaCy structural roles) vs the oracle ceiling.

| regime | OUR pipeline | competent reader (spaCy) | oracle |
|---|---|---|---|
| CANONICAL (n=669) | **0.9596** | 0.8520 | 0.9895 |
| NON-CANONICAL cleaned (n=284) | 0.2923 | **0.0211** | 0.9965 |

TWO findings: (1) **on CANONICAL we are AT competent-reader level** (0.96 vs spaCy 0.85, near oracle 0.99) — a
trustworthy quantitative brain-comparison. (2) **On NON-CANONICAL a COMPETENT reference parser ALSO fails (0.021)** —
so the non-canonical gold is BROKEN; its "0.70 signal loss" was measuring against an unreliable target, **NOT a
modeling/meaning gap**. This CORRECTS the earlier framing (§0c/§0d) that non-canonical was gated on the meaning
channel: it is gated on GOLD QUALITY first. Our 0.29 > spaCy 0.021 is NOT "better than a competent reader" — our
positional rule accidentally matches the gold's noisy preverbal-labeling; neither number is trustworthy on this gold.

**HONEST STATUS — are we 100% brain-foundational?** No. The role-assignment CORE is brain-foundational and verified;
THREE surrounding organs are not, each a named successor:
- **verb/predicate identification** — static tagger; brain-faithful combiner HARD_FAILED; needs joint POS+parse retrain (1c).
- **meaning channel** — 12-d grounded space measurably weak/dead; the generative situation model is partial/unbuilt, priority-1 under the learner-on north star (CITED, not opened — a fenced re-tread for selection).
- **deployment mention builder** — coref-based, not referent-per-NP (quantified deviation; fix prototyped, not landed).
And a data prerequisite: the **non-canonical gold must be rebuilt** before non-canonical can be measured at all.
Where signal is lost = MEASURED at each stage (§0d ledger). Brain-comparison = performance-level on canonical (at
competent-reader), un-measurable on non-canonical (broken gold).

## 0f. THE TWO NEXT-STEPS DONE + THE BRAIN STRUCTURE FOR EACH NON-BRAIN-FOUNDATIONAL ORGAN
**Step 2 — verb-ID JOINT POS+parse** (cell: `exp_whodidwhat_verbid_joint_pos_parse_v1`). Brain: lexical category and
syntax settle JOINTLY (left posterior temporal lexical access + left IFG/BA44-45 combinatorial syntax; MacDonald 1994)
— there is no static tag to mis-propagate, which is exactly why the sequential combiner failed. The heuristic joint
version (re-categorise a verb-less clause's predicate, then re-parse) ALSO HARD_FAILS (recovery 0.05) — most no-event
clauses are NOT verb-less (they contain other verbs), so the trigger rarely fires. THREE approaches now refuted
(heuristic combined cue; learned sequential combiner; heuristic joint re-tag) → 19c verb-ID genuinely needs a **fully
JOINTLY-TRAINED POS+dependency model** (Bohnet & Nivre 2012 joint parsing), a substantial adjacent build — thoroughly
located as follow-on 1c, not a heuristic.

**Step 1 — REBUILD the non-canonical gold** (cell: `exp_whodidwhat_noncanonical_gold_rebuild_v1`; spaCy reference-only,
offline eval-gold build). The original LitBank non-canonical gold agrees with a competent reader only **0.0426** (96%
broken — the "0.70 signal loss" was mostly measuring noise). But against the REBUILT competent-reader gold (282
clauses where spaCy gives a confident patient), our positional pipeline scores **0.4752** — a REAL modeling gap. So
non-canonical is BOTH: broken gold masked a genuine gap. A competent parser handles relative clauses / fronting; our
positional rule reaches 48%. This is now honestly measurable (it was not, on the broken gold), and the lever is a
real filler-gap parse, not more cues.

**The brain structure for each non-brain-foundational organ (the answer to "what does it in the actual brain"):**
- **verb/predicate identification** → left posterior temporal (lexical) + left IFG/BA44-45 (combinatorial syntax),
  settling category + structure JOINTLY (no static tagger). Our fix = joint POS+parse (1c).
- **meaning** → the anterior temporal lobe HUB binding sensorimotor spokes (Lambon Ralph hub-and-spoke); the ~200-d
  amodal hub the project already filed as its successor (the 12-d grounded space is one crude spoke).
- **referent/mention** → the discourse/situation model (default-mode network + hippocampus/entorhinal); every NP opens
  a referent (Kamp/Heim at the computational level). Our fix = referent-per-NP (prototyped).
Each organ HAS a brain-foundational answer AND a filed/prototyped successor; none is a fidelity wall, but two
(meaning hub, joint parser) are substantial builds and one (referent-per-NP) is ready to land.

## 0g. READY-TO-LAND WIRE SPEC (step 3 — for the strategy session, Q111, default-off, witnessed)
The CONFIRMED structural fixes, ready to land into `hdlab` (reference impl:
`experiments/exp_whodidwhat_composed_pipeline_v1.composed_who_did_what`). Ordered by leverage:
1. **`np_head_reduce`** — already landed (`hdlab/np_head_reduce.py`); keep on the role path.
2. **STRUCTURAL-DO candidate filter** — restrict the patient candidate set to BARE post-verbal nominals (no
   intervening preposition) before the pick; subsumes the `verb_subcat` hard veto (recovers the 47, +intransitive
   precision 0.975, +0.0045 on the main gold). Wire into `_read_events_wired` / the `_cands` primitive.
3. **QUOTATIVE-on-evidence** — apply the speaker-inversion `patient='?'` branch only with real quote structure, not on
   `is_speech_verb` lexical class alone; else keep the positional patient (recovers the 80 speech-verb drops — though
   `predict_revise` already covers most of these on the current substrate; re-measure at land).
4. **OBJECT-GAP routing** — non-canonical object-gap clauses route to the nearest-preverbal theme (unaccusative/
   fronting). NOTE: measured value on this eval is small because the non-canonical gold is broken (§0f); land as
   additive, re-validate on a REBUILT gold.
5. **REFERENT-PER-NP mention builder** (deployment) — the biggest real-world lever (+0.15 candidate coverage); land as
   a mention source with coref demoted to a downstream linking pass. (Own problem — see §0b.)
DO NOT land: the grounded-VALENCE cue on selection (fenced negative); a verb-ID heuristic (all refuted — 1c needs the
joint trained model). Every step is default-off + witnessed; strategy re-verifies against the CURRENT substrate (the
floor moves — §0).

## 1. The diagnosis — first-hand, exhaustive (cell: exp_whodidwhat_coverage_diagnosis_v1) [floor superseded by §0]
I re-ran the actual `hdlab.situation_reader.SituationReader` (the "strong" reader the gold was built with:
`role_route=wired`, `tense_agnostic_events=True`, `verb_subcat_gate=True`) first-hand on the 669 clean-19c
direct-object clauses. It reproduces the gold's stored `wired_pick`/`wired_no_event` fields **100%**. Every content
noun is handed to the reader as a candidate mention, so abstention is NOT a missing-candidate problem. The 147/669
(22%) abstentions decompose **exactly** (0 residual "other"):

| cause | n | what it is | brain verdict |
|---|---|---|---|
| **speech-verb quotative over-fire** | **80** | `role_route=wired` treats EVERY speech verb (call/tell/ask/show/reply/warn/…) as a quotative inversion ("said John") and FORCES patient=`?`, discarding the real direct object ("call **me**", "tell my **wife**"). The `positional` route recovers **all 80** (strict subset). | OUR-INVENTION over-fire |
| **verb_subcat hard-threshold suppression** | **47** | `verb_subcat_gate` deletes the patient when a modern-corpus transitivity propensity < 0.35, vetoing genuinely-transitive 19c verbs. Hits both routes. | OUR-INVENTION hard veto |
| **no-event (POS mis-tag)** | **20** | the in-substrate UD tagger mis-tags the 19c verb as ADJ/ADP/ADV/NOUN ("the lake **presents**…", "**obey**", "**spoil**", "**round**"), so the (Davidsonian, every-UPOS==VERB) tense-agnostic detector never fires. | upstream tagger recall |

The decisive number: **the wired parse-routing is NET-NEGATIVE for patient coverage** — effective 0.629 (wired) vs
0.729 (positional), a −0.100 cost, entirely the 80 speech-verb quotative vetoes. All 80 are speech verbs; 0 are
non-speech parse-attachment failures. So a "better parser" is the wrong lever.

## 2. Fair floor — I opted into the updated parser (cell: exp_whodidwhat_coverage_parser_floor_v1)
Per the standing instruction to test against the best available parser, I re-ran the wired reader with the promoted
**arc-eager parser** (`parser_arceager=True`, UD-EWT UAS 0.775 → 0.842). It recovers **1 of 669** clauses (effective
0.6293 → 0.6308; event-no-patient stays 127, no-event stays 20). The abstention is **parser-independent** — it lives
in the three gates ABOVE the parser, so the floor I beat is not a strawman weak parser.

## 3. The recovery — brain-faithful robust role path (cell: exp_whodidwhat_coverage_recover_v1)
The RECOVERED path is the Competition-Model robust role assignment (word-order-primary competition over parser-free
NP-head candidates, attempting EVERY finite verb, transitivity a SOFT cue, no quotative veto) — exactly the parent's
validated `role_patient_full_fix`, REUSED. Effective end-to-end on the 669:

| arm | effective | note |
|---|---|---|
| A0 LIVE wired | **0.6293** | the deployed floor |
| A1 LIVE positional | 0.7294 | the reader's OWN better route (recovers the 80 speech) |
| **RECOVERED** | **0.9806** | attempt-every-verb + parser-free NP-head competition + soft cues |
| info-free twin (random post-verbal pick) | 0.4185 | LOSES |

- **REC vs A0 (wired):** +0.3513 CI[+0.3154, +0.3886] half=0.0366 **null_p95=0.0375** → CI-separated AND over null.
- **REC vs A1 (positional, the strongest floor):** +0.2511 CI[+0.2167, +0.2840] → CI-separated.
- **REC vs info-free twin:** +0.5620 CI[+0.5247, +0.6009] → CI-separated (the recovery's accuracy is structural, not luck).

**Per-cause ablation (0.629 → 0.981 decomposed, sums exactly):** already-picked-correct 421→416 kept (+0.622),
already-picked-wrong 101→99 fixed (+0.148), speech-quotative 80→74 recovered (+0.111), verb_subcat 47→47 (+0.070),
no-event 20→20 (+0.030).

**NO-REGRESSION:** present-accuracy (on the clauses it answers) rises **0.807 → 0.981**; of the 421 clauses the live
reader already got right, RECOVERED keeps 416. The **5 individual flips** are genuinely hard multi-candidate cases:
one ditransitive ("gave [master] [errand]" — the parse router correctly gets the recipient, positional doesn't model
it), one copula/raising ("seemed … people"), three where grounded competition chose a distant noun. Net precision is
up, not down — the 5 are the residual value of the parse router, which the proposed wire deliberately keeps as an
ADDITIVE override (below).

**Generalization (modern QA-SRL, n=1261):** effective 0.5678 → 0.9025, +0.3347 CI-separated; present-accuracy 0.9025.
The same mechanism recovers coverage on modern text — the gates cost coverage in both registers, and the robust path
is register-independent.

## 4. Is the wall brain-faithful? (the opening move, and the user's standing question)
The three gates are each LESS brain-faithful than the recovery — confirmed by a literature drill converging across
five independent literatures:
- **Parse-dependence (the 80):** the brain does NOT require a complete syntactic parse to assign the patient; it
  assigns roles incrementally from robust cues (word order, animacy, morphology) that survive parse failure —
  Competition Model (Bates & MacWhinney 1989), good-enough/shallow processing (Ferreira 2002; Ferreira & Patson
  2007), Now-or-Never bottleneck (Christiansen & Chater 2016), constraint-satisfaction (MacDonald et al. 1994),
  noisy-channel (Gibson et al. 2013). Principled abstention-on-parse-failure has **no** empirical analog — garden
  paths yield a degraded/hybrid reading, never silence. → the parser-free positional recovery is MORE faithful.
- **Transitivity (the 47):** no literature has verb bias fully BLOCK bottom-up argument evidence; strong local
  plausibility OVERRIDES verb bias when they conflict (Garnsey et al. 1997; Trueswell et al. 1993; Altmann & Kamide
  1999). → a soft, overridable transitivity cue is MORE faithful than a hard threshold veto. (Honest caveat from the
  drill: the brain still DISCOUNTS an overridden reading rather than forgetting the prior — a graded confidence, not
  a binary flip; our recovery treats it as a present-object override, a small simplification worth noting.)
- **Verb identification (the 20):** the brain identifies the predicate from clausal position + agreement/tense
  morphology + closed-class scaffolding, not a static category lookup (MacDonald 1993; Mintz 2003 frequent-frames;
  Christophe/Morgan & Demuth function-word bootstrapping). → the 19c mis-tagging is an adjacent-component
  (tagger-recall) limitation, not a fundamental wall.
- **Register-independence (honest caveat):** consistent with the general adaptive-parser literature (Fine et al.
  2013), but **no direct archaic-register study was located** — I do not claim this as settled; the modern+19c
  generalization result is the evidence I actually have.

Not a single one of these is a fidelity wall we cannot cross — each fix moves the substrate TOWARD the brain's
mechanism, not toward a convenient tool.

## 5. PROPOSED hdlab WIRE (strategy lands it — Q111, default-off, witnessed; I do NOT edit hdlab)
A surgical, precision-preserving change to `hdlab/situation_reader.py::_read_events_wired`, not a wholesale
replacement — each step recovers one cause while keeping the router's genuine passive/ditransitive value:
1. **Quotative-on-evidence (recovers 80):** apply the speaker-inversion `patient='?'` branch (line ~1031) ONLY when
   the clause actually has quote structure, not on `is_speech_verb` lexical class alone; otherwise assign the patient
   normally. Equivalent minimal form: never let the quotative branch leave `patient='?'` when a post-verbal nominal
   candidate exists — fall back to the positional patient.
2. **Positional fallback in the router (backstop):** the wired path must never emit `patient='?'` when the positional
   `_assign_roles` found one; the router `theme` is an ADDITIVE override (keep it — it is what correctly handles the 5
   ditransitive/passive cases), never a delete.
3. **STRUCTURAL direct-object filter (recovers 47, replaces the verb_subcat veto — REFINED by the deepening below):**
   restrict the patient candidate set to BARE post-verbal nominals (no intervening preposition) before the pick — a
   patient is structurally a DIRECT object; a preposition-governed oblique is never the patient. This recovers the 47
   the hard gate false-suppressed AND correctly abstains on genuine intransitives (measured 0.975), AND slightly
   IMPROVES the main gold (0.9806 -> 0.9851). It subsumes the `verb_subcat_gate`'s protective purpose without its
   false-suppression, and needs no transitivity threshold at all.
4. **NP-head reduction** is already landed (`hdlab/np_head_reduce.py`) and should stay on this path (the accuracy half).
5. The **20 no-event** is a LOCATED sub-negative: it is upstream POS-tagger recall on 19c verbs, not a role-assignment
   defect — recovered here only because the who-did-what task supplies the verb index. It is filed as follow-on
   problem 1c below, not silently folded in.

Reference implementation of the full recovered path: `experiments/exp_whodidwhat_full_fix_v1.role_patient_full_fix`.

## 6. DEEPENING — two pushes that made the fix more brain-faithful and closed my own gaps
A second research drill (verb/noun category ambiguity, ditransitive linking, singleton referents) plus two new cells:

**(a) STRUCTURAL direct-object rule beats "soft transitivity" — a cleaner mechanism, discovered by pushing.**
(cell: `exp_whodidwhat_coverage_transitivity_control_v1`.) My first recovery softened the transitivity veto, and I had
flagged its no-regression as *argued, not measured*. I measured it on a constructed can-fail INTRANSITIVE control ("the
man arrived at noon", "she sat by the fire", …; correct answer = no patient): the naive soft rule OVER-GENERATES on
**100%** of them (assigns the oblique as patient) — a real regression. The brain-faithful fix is not a softer
transitivity threshold at all: **the patient is structurally a direct object, so restrict candidates to BARE
post-verbal nominals (no intervening preposition); a preposition-governed oblique is never the patient** (grounded in
the definition of the patient role + structural DO evidence — Goldberg construction linking; Bresnan 2007). This
STRUCTURAL-DO rule: recovers the 47 hard-suppressed clauses (1.00), abstains correctly on **0.975** of the
intransitive control (vs the hard gate's 1.00), and *improves* the main gold **0.9806 → 0.9851**. It subsumes the
`verb_subcat_gate` entirely — no transitivity number needed. This is the recommended form of wire-step 3.

**(b) The 20 no-event is SOLVABLE-in-principle, not a wall — but not trivially (honest located sub-result).**
(cell: `exp_whodidwhat_verb_id_recoverable_v1`.) The mis-tagged 19c verbs ARE lexically verbs (WordNet verb-reading on
**18/20**), confirming the research verdict that verbhood is recoverable from lexicon+structure, not a static tag. But
a cheap glass-box heuristic does NOT cleanly recover them: "verb-reading + any preceding subject" gets 75% at an
unusable 5.0 false-verbs/sentence; a Mintz frequent-frame cue (N-[verb]-N, no verb in the predicate slot) gets only
30% at 0.8 FP/sentence. So a clean recovery needs REAL clause-level predicate identification (the research's
parser-attachment-as-verbhood-override), which is the adjacent component — filed as follow-on 1c with this evidence,
NOT claimed as solved here. "If the brain can do it we can too" holds; the honest scope is that it needs a mechanism,
not a heuristic.

## 7. ADJACENT-COMPONENT MAP — brain-fidelity, capability, limitation, opportunity (to seed the next problems)
Evaluated while solving this, per the standing instruction to map adjacent components:

| component (hdlab) | brain status | capability now | limitation found | opportunity / next problem |
|---|---|---|---|---|
| **event detection** (`_extract_events` / `tense_agnostic`) | Davidsonian per-verb = PINNED ✓; verb-IDENTIFICATION by static UD tag = OUR-INVENTION deviation | fires at every UPOS==VERB (recall 0.97 through the reader) | capped by UD-tagger 19c verb recall — the 20 no-event; verb-ID should be position+morphology, not a tag | **1c: register-robust predicate identification** (parser-attachment/frame verbhood override; evidence in cell (b)) |
| **role routing** (`_read_events_wired`, parse route) | Competition-Model incremental role assignment = PINNED; full-parse-gated routing = deviation | richer passive/ditransitive roles when the parse succeeds | net-NEGATIVE for patient coverage on 19c (−0.10); quotative veto + no positional fallback | **this problem's wire** (demote router to additive override; positional/structural-DO primary) |
| **transitivity gate** (`verb_subcat`) | verb bias = graded overridable cue (PINNED); hard threshold = deviation | suppresses spurious intransitive patients | false-suppresses genuinely-transitive 19c verbs (47) | **subsumed** by the STRUCTURAL-DO rule (push (a)) — candidate for retirement on this path |
| **quotative inversion** (`is_speech_verb` branch) | speaker-inversion is real; lexical-class trigger = deviation | handles "'…,' said John" | over-fires on every speech verb with a real object (80) | fold into the wire: gate on actual quote structure |
| **mention / candidate builder** (`parse_litbank_conll`) | referent-per-NP incl. singletons = PINNED (Kamp/Heim) | eval marks every content noun a mention | DEPLOYED `read()` derives mentions from COREF chains — can drop singleton referents | **next problem: referent-per-NP first, coref as a downstream LINKING pass** (Q3 confirms our design premise) |
| **ditransitive linking** (positional/NP-head) | double-object construction obj1=recipient/obj2=theme = PINNED (Goldberg; VerbNet) | word-order patient works for mono-transitives | mis-assigns recipient vs theme (1 of the 5 regressions) | **1d / the filed non-canonical-argument problem**: VerbNet ditransitive frame + animacy backoff (research: cheapest win) |

## KEY REALIZATIONS
- **The abstention was disguised as a parser problem and was actually three lexical/threshold gates.** The enabling
  move was running the reader FIRST-HAND and splitting the 147 by CAUSE instead of trusting "the parse is weak on
  19c" — the moment I compared the wired and positional routes and saw positional recover all 80, the story flipped
  from "build a better parser" to "stop three gates from vetoing real patients".
- **A more accurate component made the whole system less accurate.** The `wired` parse route was added for
  richer/passive roles and it is net-NEGATIVE (−0.10) for patient coverage — a concrete instance of "the convenient
  fancy mechanism loses; the robust brain-faithful cue wins".
- **The updated parser recovering 1/669 is the proof, not a footnote.** Opting into the best parser and watching the
  gap NOT move is what licenses "parser-free is the right lever".
- **Coverage, not accuracy, was the larger loss** — and it hid behind a 0.98 present-accuracy number. Counting
  silence as wrong is the measurement that made the real bottleneck visible.
- **Pushing on "soft transitivity" replaced it with a better mechanism entirely.** Building the can-fail intransitive
  control showed the naive soft rule regresses (over-generates on 100% of intransitives); the fix was not a softer
  threshold but a structural principle — *the patient is a direct object, obliques never are* — which needs no
  transitivity number, recovers the 47, abstains 0.975 on intransitives, and even improves the main gold. The lesson:
  when a gate mis-fires, the brain-faithful move is often to delete the gate and use the structural definition of the
  role, not to re-tune the gate's threshold.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
`situation_reader` role assignment: the `role_route=wired` patient path carries two OUR-INVENTION precision gates
(speech-verb quotative veto; verb_subcat hard threshold) that are register-brittle and cost 127/669 patients on 19c
prose, plus 20 upstream POS-tagger no-events. The brain-faithful operation is word-order-primary Competition-Model
role assignment with transitivity/quotative as SOFT overridable cues (PINNED by Bates & MacWhinney / Ferreira /
Garnsey). Current fidelity: the robust positional+NP-head competition path is the faithful one and reaches 0.981
end-to-end; the parse router should be demoted to an additive passive/ditransitive override. The tense-agnostic
Davidsonian event detector is correct but capped by UD-tagger 19c verb recall (adjacent component).

## What I did NOT establish (would withdraw first if wrong)
- I did NOT edit hdlab or measure the wire landed in-place — I proved the mechanism in experiments/ and the strategy
  session lands it (Q111). The 0.981 is the reference-path measurement, first-hand-reproduced against the live reader.
- The intransitive precision control is a CONSTRUCTED (glass-box, hand-built) set of 40 clauses, not mined 19c
  intransitives; it can-fail and the STRUCTURAL-DO rule passes it (0.975), but a corpus-mined intransitive population
  would be a stronger control. First thing to withdraw if mined intransitives over-generate. (This SUPERSEDES the
  earlier "argued not measured" caveat — the gap is now measured.)
- The 20 no-event are recovered here only because the task supplies the verb index; in free-text deployment they
  depend on POS-tagger 19c recall (follow-on 1c). I do NOT claim end-to-end event DETECTION is solved.
- Register-independence is an extrapolation (no direct archaic-register study); the evidence is the modern+19c
  generalization, not a brain finding.

---

### TLDR (plain language) — UPDATED after the floor moved (see §0)
IMPORTANT HONESTY UPDATE: while I was working this, the shared system was being improved by the other session, and
the reader's "who did what" score quietly climbed on its own — from the ~63% the brief cites to about **79%** now.
The biggest thing I had diagnosed (it throws away the object of "saying" verbs like "call **me**") was fixed upstream
by that work. So counting silence as a miss, the honest starting point is now ~79%, not 63%. My fix still helps — it
takes it to ~98.5%, a **+20-point CI-separated gain that is now mostly about ACCURACY** (picking the right word inside
a phrase) rather than the silence, plus recovering two smaller silent buckets. Original diagnosis, still a correct
account of the mechanism: the silence had three causes, none of them "couldn't find the noun": (1) it threw away the
object of every "saying" verb — "call **me**", "tell my **wife**"; (2) it deleted the object whenever a word-frequency
table thought the verb was rarely transitive, which misfires on old verbs; (3) it never starts because its
part-of-speech tool mislabels old verbs like "the lake **presents**" as nouns. Fixing all three
with a robust, brain-style rule (nearest sensible noun after the verb, always try, treat those two vetoes as soft
hints not hard blocks) takes it from 63% to 98%, holds up on modern text too, and a scrambled version collapses to
42% — proving the fix is real, not luck. I also turned on the newest, most accurate grammar parser to be fair: it
fixed only 1 sentence out of 669, confirming the problem was never the parser.

### QUESTIONS
None blocking. One judgement call for the strategy session at landing: whether to keep the parse router as an
additive passive/ditransitive override (recommended — it correctly handles the 5 hard cases the pure positional rule
misses) or drop it entirely for simplicity.

### NEXT STEPS
1. **Land the wire** (strategy, Q111, default-off, witnessed): quotative-on-evidence + positional fallback +
   **STRUCTURAL-DO candidate filter** (patient = bare post-verbal nominal; the refined form that subsumes verb_subcat)
   in `_read_events_wired`; re-measure through the live reader; then re-validate the ~20 role-output organs (they
   inherit the fix — re-validate, don't re-code).
2. **Follow-on 1c — register-robust predicate identification** (the 20 no-event; adjacent component, SOLVABLE not a
   wall): the mis-tagged tokens ARE lexically verbs (18/20 WordNet), but a heuristic can't cleanly recover them (cell
   (b)) — the fix is the research-indicated parser-attachment / clause-structure verbhood override, not a better
   static tagger. High-value for free-text event detection; verdict-independent.
3. **Follow-on 1d — ditransitive recipient-vs-theme** (1 of the 5 regressions): the double-object construction assigns
   obj1=recipient/obj2=theme (Goldberg; VerbNet) with animacy backoff (Bresnan 2007) — the research calls this the
   cheapest win (a wiring fix against resources already held). Its home is the filed non-canonical-argument problem.
4. **Referent-per-NP mention sourcing** (adjacent, brain-fidelity): the deployed `read()` derives mentions from coref
   chains, which can drop singleton referents; the brain-faithful order is referent-per-NP first (Kamp/Heim), coref as
   a downstream LINKING pass. Verify the deployed mention source annotates singletons; if not, it is a coverage
   ceiling this recovery's eval harness hides. Candidate next problem.
