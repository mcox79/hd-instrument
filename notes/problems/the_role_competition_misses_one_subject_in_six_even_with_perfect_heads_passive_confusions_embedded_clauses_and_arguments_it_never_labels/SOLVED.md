---
problem: the_role_competition_misses_one_subject_in_six_even_with_perfect_heads_passive_confusions_embedded_clauses_and_arguments_it_never_labels
status: PARTIAL
bar: "Under GOLD heads: nsubj recall up CI-separated in matrix AND embedded clauses, obj not down, the nsubj:pass confusions at least halved net of verified annotation noise, and the <none> population labelled with recall >= the NOUN population's. Under LIVE heads: embedded nsubj up CI-separated. Board patient not down. Knowledge as counts with an online observe path. OR a numbered located negative naming the missing input."
result: "FIRST RESULT IS AN INSTRUMENT CORRECTION: all 41 'the labeler calls active subjects PASSIVE' cases are an artifact of the diagnostic, not of the organ. experiments/_diag_roles_by_clause_type.py reads its gold through tools/build_attachment_validities.sentences, which does rels.append(c[7].split(':')[0]) -- it STRIPS UD subtypes, so gold nsubj:pass arrives as nsubj and every CORRECTLY labelled passive subject was scored as a miss. On the true gold the labeler's PASS_SUBJ recall is 1.000 (embedded, n=16) and 0.750 (matrix, n=32) and it makes ZERO false passive calls under gold heads. The true floor is matrix nsubj 0.9079 / embedded nsubj 0.8655 / copular nsubj 0.8239 (not 0.830 / 0.812 / 0.832), i.e. the miss rate on subjects is one in nine, not one in six. THE BUILD: cue set v3 for the Competition-Model role labeler -- (1) ARGUMENT RANK over the verb's own dependents on BOTH sides (an NP-internal compound is not a second argument slot; the pre-verbal side had no rank cue at all, so the active-filler configuration was invisible), PRECISION-GATED on the heads rung's own posterior; (2) the there-BE CONSTRUCTION as a CONFIGURATION plus an EXPLETIVE value for the pre-verbal slot; (3) LEXICAL case (the preposition FORM is the cue value) with the surface scan STOPPED at a relativizer; (4) the COPULA cue read in BOTH orders and ADV/ADP/SYM/INTJ predicates given their own head classes; (5) the ARGUMENT-HEAD population -- a quantifier / numeral / nominalised-adjective phrase head is labelled too (Right-hand Head Rule + DP-head, the landed np_head_reduce criterion); plus a RELIABILITY GATE on learning (a comprehension outcome teaches only when the governor believed its own attachment, P >= 0.5, swept). MEASURED, UD-EWT test 700, weighted-perceived accrual, paired item bootstrap: GOLD heads (the labeler's own rung) matrix nsubj 0.9079 -> 0.9460 (+0.0381 CI95[+0.0159,+0.0635] CI-SEP), embedded nsubj 0.8655 -> 0.9496 (+0.0840 CI[+0.0504,+0.1218] CI-SEP), matrix obj 0.8254 -> 0.9418 (+0.1164 CI-SEP), embedded obj 0.8768 -> 0.9242 (+0.0474 CI-SEP), copular nsubj 0.8239 -> 0.8176 (-0.0063 n.s.), nsubj:pass unchanged (0.750 / 1.000); ALL core arguments 0.8655 -> 0.9198 (+0.0543 CI[+0.0397,+0.0707] CI-SEP); the NEVER-LABELLED population (37 core arguments whose category is ADJ/NUM/DET/SYM/ADV) 0.0000 -> 0.8378 (+0.8378 CI[+0.7027,+0.9459] CI-SEP); held-out role accuracy over all 3224 nominals 0.8734 -> 0.8834 (+0.0099 CI-SEP). LIVE heads (attachment arm): NEUTRAL everywhere, no CI-separated regression on any population (core +0.0026 CI[-0.0078,+0.0129]; matrix nsubj +0.0127; embedded nsubj +0.0000; copular -0.0314 CI incl 0), never-labelled population 0.1351 -> 0.2973 (+0.1622 CI-SEP). Info-free twin CI-separated below in every population and both arms (gold core: twin 0.4517 vs 0.9198). Board who_did_what PATIENT no-regress by in-process A/B on the same entry point: 0.7920 -> 0.7936 (UP), still CI-separated over its own floor and twin. Board who_did_what AGENT on the live chain (1424 gold items, strategy's probe): positional floor 0.8399, chain naive-first-nsubj 0.8371, chain with the SUBJECT-SLOT COMPETITION pick 0.8434 (+0.0035 CI[-0.0063,+0.0140]) -- a tie with the floor, not a win, but the competition pick alone is worth +0.0443 over the naive pick on the incumbent table (0.7879 -> 0.8322) and precision-when-decided rises 0.859 -> 0.9316. TWO BAR CLAUSES NOT MET, both located: (a) under LIVE heads embedded nsubj is +0.0000, and (b) the previously-unlabelled population reaches 0.8378 against the nominal population's 0.9225. THE NUMBERED LOCATED NEGATIVE: the heads rung. Chain decomposition (core role recall, n=1160): gold tags + gold heads floor 0.8655 -> v3 0.9095; ORGAN tags + gold heads 0.8207 -> 0.8474 (the win SURVIVES the tagger rung); gold tags + ARM heads 0.7543 -> 0.7491; organ tags + arm heads 0.7250 -> 0.7224. Split by whether the governor attached the argument at all: on head-correct items the floor is already 0.878-0.907 and v3 adds +0.011/-0.004 (no headroom left); on head-wrong items nothing recovers the label. The heads rung costs the floor 0.111 and the better labeler 0.160 -- a sharper cue set on a wrong structure is worse, which is why the arc-dependent rank cue had to be precision-gated to make the live arm neutral instead of -0.049."
floor: "The shipped Competition-Model coarse role labeler (hdlab.graded_role_assigner.coarse_roles) with its cue validities re-accrued by the same weighted-perceived pipeline, measured on UD-EWT test 700 with the TRUE (subtype-preserving) gold. GOLD heads: matrix nsubj 0.9079 (n=315), embedded nsubj 0.8655 (n=238), copular nsubj 0.8239 (n=159), matrix obj 0.8254 (n=189), embedded obj 0.8768 (n=211), matrix nsubj:pass 0.7500 (n=32), embedded nsubj:pass 1.0000 (n=16), ALL core 0.8655 (n=1160), never-labelled population 0.0000 (n=37), held-out accuracy 0.8734 (n=3224). LIVE heads: 0.8444 / 0.7227 / 0.6667 / 0.6667 / 0.6967 / 0.4062 / 0.6875, ALL core 0.7250. The two SHIPPED assets measured alongside as external references (gold heads, held-out accuracy): coarse_role_validities_ud_ewt.json 0.8620, coarse_role_validities_ud_ewt_perceived_w.json 0.8638 -- the cell's re-accrued floor at 0.8734 is the STRONGER floor and is the one every delta is quoted against."
controls: "(1) INFO-FREE TWIN = the learned strength VECTORS permuted across the cue VALUES of every cue, configuration included; the whole competition machinery runs on a destroyed value->role mapping. CI-separated below v3 in every population and both arms (gold: core 0.4517 vs 0.9198 (+0.4681 CI[+0.4371,+0.4983]), subjects 0.7360 vs 0.9185, objects 0.0000 vs 0.9325, held-out accuracy 0.4032 vs 0.8834; live: core 0.4164 vs 0.7276). (2) PAIRED ITEM BOOTSTRAP (4000 resamples) over the SAME items for every population; each population is the item's own (clause type x gold relation). (3) FLOOR FIDELITY: the cell's v2-repro floor reproduces the shipped organ's per-population recalls (matrix nsubj 0.9079 vs shipped 0.9079, embedded nsubj 0.8655 vs 0.8655, matrix obj 0.8254 vs 0.8254) and is slightly STRONGER overall (0.8734 vs 0.8638) -- deltas are quoted against the stronger. (4) PATCH FIDELITY: the proposed hdlab change reproduces the cell EXACTLY -- 3716/3716 identical labels under gold heads and 3698/3698 under live heads -- and is BYTE-IDENTICAL to the shipped organ on a pre-v3 validity table (3224 labels, 0 differences), because every addition is self-gated on the asset's cue_set key. (5) UPSTREAM ORACLE ABLATION (locates the loss; NOT a shippable arm -- it reads the gold tree at learning time): training the same cue set on gold heads takes gold-head core recall to 0.9629 and subject recall to 0.9817, i.e. the perceived-heads training itself costs ~0.05. (6) FOUR-WAY CHAIN DECOMPOSITION (tagger rung x heads rung) isolating which upstream rung erases the gain (numbers in `result`). (7) HEAD-CORRECTNESS SPLIT of the live arm (head-ok vs head-wrong sub-populations). (8) HEAD-POSTERIOR CALIBRATION: AUC 0.678 for discriminating a correct attachment, but precision only 0.740 even at P >= 0.95 -- which is why marginalising the role read over the posterior LOSES (live core 0.7224 -> 0.6952; it also loses for the pre-v3 cue set, 0.7250 -> 0.6970) while using the same posterior as a PRECISION GATE wins. (9) WITNESS on real UD-EWT test trees (12 cases the shipped organ gets wrong, one per mechanism): 11/12; the 12th is the existential residual, documented below with its count. (10) NO-REGRESS on the board's who_did_what PATIENT dimension by in-process A/B (0.7920 -> 0.7936) and on the board's who_did_what AGENT items (0.8371/0.8434 vs 0.8399 floor)."
files_changed: "experiments/exp_role_competition_voice_embedding_arguments_v1.py, data/hook_state/coarse_role_validities_pri103_v3.json, notes/problems/the_role_competition_misses_one_subject_in_six_even_with_perfect_heads_passive_confusions_embedded_clauses_and_arguments_it_never_labels/SOLVED.md. NOT PRODUCED: graded_role_assigner_patch.diff -- the tool call that generated the unified diff was DENIED by the harness and, per the session's hard rules, was not retried by any other route. The two patched files themselves are complete, syntax-checked and behaviour-verified in the session scratchpad at C:/Users/marsh/AppData/Local/Temp/claude/c--AI/95c182ee-4222-401b-92f4-de5c381c5ab4/scratchpad/patch/{hdlab/graded_role_assigner.py, tools/build_coarse_role_validities.py}; strategy can diff them against the repo copies itself. The MEASURED asset is already on disk (data/hook_state/coarse_role_validities_pri103_v3.json), so the organ change can be landed asset-first: copy it into data/frontend_assets/ and point HDLAB_ROLE_VALIDITIES at it -- it carries cue_set: v3, which is the switch."
reverify: ".venv/Scripts/python.exe experiments/exp_role_competition_voice_embedding_arguments_v1.py --self-test   (then --cache once, then --run --ablate, --agent, --board-patient)"
---

## 1. What the problem turned out to be

The brief's headline -- *"it calls active subjects PASSIVE (41 cases)"* -- **is not a defect of the organ.**
`experiments/_diag_roles_by_clause_type.py` gets its gold from
`tools/build_attachment_validities.sentences`, whose last line is

    toks.append(c[1]); pos.append(c[3]); heads.append(int(c[6])); rels.append(c[7].split(":")[0])

`c[7].split(":")[0]` **strips the UD subtype**. Gold `nsubj:pass` therefore arrives as `nsubj`, the
`nsubj:pass` population is never measured at all, and every passive subject the organ labels *correctly*
is scored as a miss. All 41 cases are that: I re-read the same 700 sentences with the subtype preserved
and the organ's PASS_SUBJ recall is **1.000** (embedded, n=16) and **0.750** (matrix, n=32), with **zero**
active subjects called passive under gold heads. Checklist item 4 anticipated exactly this ("verify the 41
cases against the gold deprel"); the answer is 41/41 instrument, 0/41 organ, 0/41 annotation noise.

Corrected floor (UD-EWT test 700, gold heads, weighted table): matrix nsubj **0.9079** (not 0.830),
embedded nsubj **0.8655** (not 0.812), copular nsubj **0.8239**. The subject miss rate is **one in nine**,
not one in six.

The **real** residual, with counts, from the anatomy dump:

| bucket (gold heads) | n | what it is |
|---|---|---|
| copular nsubj -> dep | 21 | the predicate is an ADV/INTJ/SYM/NUM ("Here **is** a draft", "the economy is **down**") collapsed into one OTHERH head class, and the copula cue only fired for a pre-verbal subject |
| matrix/embedded nsubj -> obj | 20 | **14 are the existential construction** ("there is no **proof**"): `there` counted as filling the pre-verbal subject slot |
| matrix obj -> dep | 12 | an NP-internal compound counted as an argument slot ("criticized President **Bush**" read as the *second* post-verbal nominal) |
| embedded nsubj -> obl | 8 | "in which KENNEDY joined": the surface case scan crossed the relativizer and read `in` as KENNEDY's preposition |
| embedded obj -> nsubj | 10 | filler-gap ("the aid **that** Darfur needs"): no rank cue existed on the pre-verbal side |
| matrix obj -> obl | 7 | verb PARTICLES ("worked **out** a deal", "checking **out** my options") read as case markers |
| any -> `<none>` | 37 | ADJ 14 / NUM 14 / SYM 5 / DET 2 / ADV 3 core arguments the organ never labels at all |

## 2. The brain computation, and what changed

Nothing about the **operation** changed: it is still the Competition Model (Bates & MacWhinney 1982/1989),
additive cue activation read *within* the configuration, softmax = the posterior, strengths a pure function
of accrued counts. Five things the cues **read** changed, each one a place where a surface proxy stood in
for a structure the brain reads:

1. **Argument RANK is over the verb's arguments, not over tokens** (Competition Model first-noun/second-noun),
   and it exists on the **pre-verbal** side too -- the active-filler configuration (Frazier & Clifton 1989),
   the same structure the organ's PATIENT arm already reads as `gap_config`.
2. **An expletive does not fill the subject slot**, and `there`-BE is a stored **construction**
   (Goldberg 1995; MacWhinney's item-based constructions) -- so it belongs in the **configuration key**, not
   as one additive contrast fighting the general post-verbal-object configuration.
3. **Case is lexical**: the preposition *form* is the cue value (case marking is a top Competition-Model cue);
   the scan stops at a relativizer, which is a clause boundary.
4. **The copula links in both orders** (inverted "Here is a draft"), and ADV/ADP/SYM/INTJ predicates get their
   own head classes.
5. **An argument is whatever fills the slot**: a quantifier / numeral / nominalised-adjective **phrase head**
   is labelled, gated by the Right-hand Head Rule (Williams 1981) + DP-head rule (Abney 1987) -- i.e. the
   criterion the landed `hdlab/np_head_reduce.py` already implements. **One structure, one organ**: no new
   organ, no new lexicon.

Plus a **reliability gate on learning**: a comprehension outcome teaches the validities only when the governor
believed its own attachment (P >= 0.5, swept 0.0/0.5/0.8). The brain consolidates what it *understood*.

Knowledge stays counts; `observe_role_outcome` works unchanged (the patch passes the same `cue_set` flag into
it, so online accrual and offline accrual compute identical cue values).

## 3. Cumulative build order (gold heads, deltas vs the floor, all CI-separated unless marked)

| step | ALL nsubj | ALL obj | ALL core | held-out acc | never-labelled |
|---|---|---|---|---|---|
| + argument RANK | +0.0183 | +0.0200 | +0.0181 | +0.0071 | 0 |
| + relativizer-stopped case scan | +0.0295 | +0.0200 | +0.0250 | +0.0099 | 0 |
| + existential CONFIGURATION + expletive slot | +0.0407 | +0.0200 | +0.0319 | +0.0155 | 0 |
| + head classes + two-order copula | +0.0463 | +0.0200 | +0.0353 | +0.0121 | 0 |
| + rank PRECISION GATE | +0.0365 | +0.0350 | +0.0345 | +0.0065 (n.s.) | 0 |
| + ARGUMENT-HEAD population | +0.0435 | +0.0525 | +0.0448 | +0.0059 (n.s.) | **+0.8108** |
| + LEXICAL case values (the landed set) | **+0.0435** | **+0.0800** | **+0.0543** | **+0.0099** | **+0.8378** |

The lexical preposition value is **null on its own** (+0.0025 obj) and worth **+0.028 obj / +0.010 core** once
the relativizer stop and the argument rank are in place -- the chain had to be cracked above it before it paid.

## 4. Understood negatives (each one built faithfully, measured, and NOT shipped)

- **VOICE from the predicate's AUX DEPENDENTS** (the brief's lever (a)). Built: be/get + V-en = passive,
  have + V-en = perfect ACTIVE, be + V-ing = progressive, aux found as the predicate's AUX dependents so
  inversion ("Attached **is** a spreadsheet") is recovered. **-0.0323 subject recall CI-sep, -0.0630 on
  embedded subjects.** *Mechanism, with numbers:* the cue becomes arc-dependent, so at LEARNING time it
  inherits the governor's attachment noise -- the be+participle bucket's reliability for PASS_SUBJ falls
  **0.719 -> 0.549** and 2339 weighted decisions leak into a "bare participle" bucket. English auxiliary order
  is fixed, so the shipped **surface** window is the higher-validity read; the only real defects in it are the
  sentence-wide fallback (`is_passive_clause(toks, pos, h)` passes the head index as the *window* argument, so
  the test runs over the whole sentence) and the missing inversion case -- and with those fixed on the surface
  the cue is still net-negative in the full stack (-0.073 core). **The passive rung was already right; the
  instrument was wrong.**
- **The filler's own CATEGORY as a full 8-value cue.** **-0.10 CI-sep** (77 canonical subjects flipped to
  OTHER). *Mechanism:* it double-counts the animacy and case cues (a pronoun is already marked animate and
  nominative), so every common-noun subject pays a negative contrast. Collapsed to one value over
  NOUN/PROPN/PRON it is harmless but buys nothing, so it is not shipped.
- **Relative-pronoun FORM as a case value** and **the relative clause as its own configuration**: both trade
  subjects for objects (obj +0.072 / +0.058 CI-sep, nsubj -0.025 / -0.018, core *down*). *Mechanism:* relative
  **subjects** far outnumber extracted relative **objects**, so the split halves the count mass of the dominant
  subject configuration without buying the object contrast. The stronger form needs more construction exposures
  than 12.5k sentences provide -- a data lever, not a ceiling.
- **Marginalising the role read over the head posterior** (the organ's own graded hand-off). **live core
  0.7224 -> 0.6952**, and it also costs the *pre-v3* cue set (0.7250 -> 0.6970). *Mechanism:* the attachment
  arm's posterior is **broad and mis-centred**, not narrow and uncertain -- AUC 0.678 for a correct attachment,
  but even at P >= 0.95 the head is only 74% correct, so the alternative mass is not the right head and the
  mixture dilutes the correct MAP reads without rescuing the wrong ones. This sharpens the pri-93 finding
  ("peaked") into a calibration statement. The same posterior used as a **precision gate** is a win.
- **Verb PARTICLE detection** ("worked out a deal") as a cue value: exactly null. *Mechanism:* the test is
  arc-dependent (an ADP whose head is a verb), so under perceived heads the bucket fills with mis-attached
  real prepositions -- 37 weighted decisions, 47% OBL / 49% OTHER. A phrasal verb is a **stored lexical item**;
  the brain-faithful form is a learned (verb-lemma, particle) association, which is the queued alternate path.
- **Widening the argument class WITHOUT the argument-rank cue**: -0.072 subject recall. *Mechanism:* the
  pre-v3 `post_slot` counts nominal **tokens**, so determiners and adjectives then count as argument slots and
  almost every object becomes the "second" post-verbal nominal. The widening is only safe once rank is over
  siblings -- an ordering constraint, discovered by measurement.

## 5. The residual, and where the signal is lost (the status probe, answered with numbers)

**Chain, rung by rung, for the signal the who-did-what readers need (core role recall, n=1160):**

| tags | heads | floor | v3 | delta |
|---|---|---|---|---|
| gold | gold | 0.8655 | **0.9095** | +0.0440 |
| **organ (`lexical_categories`)** | gold | 0.8207 | **0.8474** | +0.0267 |
| gold | **arm (`attachment_arm`)** | 0.7543 | 0.7491 | -0.0052 |
| organ | arm | 0.7250 | 0.7224 | -0.0026 |

The labels rung's own share is now largely recovered and **the recovery survives the tagger rung** (+0.027 with
the organ's own categories). It is **erased by the heads rung**. Splitting the live arm by whether the governor
attached the argument at all:

- **head-correct items** (66% of core arguments): floor is already 0.878-0.907 and v3 adds +0.011 / -0.004.
  There is essentially **no labeler headroom left on the arguments the live chain perceives correctly** --
  the floor there is already at the gold-heads level.
- **head-wrong items** (34%): floor 0.22, v3 0.22. Nothing at this rung can recover them.
- The heads rung costs the floor 0.111 and the *better* labeler 0.160 -- a sharper cue set over a wrong
  structure is worse. That is why the one arc-dependent addition had to be precision-gated: ungated it took
  the live arm to **-0.049 core CI-sep**; gated at P >= 0.5 the live arm is neutral (+0.0026).

**Brain-foundational status of each rung as it relates to THIS signal** (as the disk shows it):

| rung | organ | status | what it hands down for this signal |
|---|---|---|---|
| tokens | -- | n/a | surface forms |
| categories | `hdlab/lexical_categories.py` (+ Penn arm) | BF_SPIRIT, count-based, no supervised tagger at inference | a HARD tag; a graded posterior exists (`coarse_role_posterior_tagmarg`) but the live chain hands a point estimate. Costs the labeler 0.0621 (gold-heads arm: 0.9095 -> 0.8474) |
| lemma | `hdlab/morphology` | BF_SPIRIT | verb lemma for the frame cue |
| heads | `hdlab/attachment_arm.py` | BF_SPIRIT, cue competition + Matrix-Tree marginals, self-supervised | a hard head + a posterior. The posterior is **informative about reliability** (AUC 0.678) but **not about the alternative** (74% precision at P>=0.95). Costs the labeler 0.160 |
| roles | `hdlab/graded_role_assigner.coarse_roles` | BF_SPIRIT; this cell | a hard label; the graded posterior exists and is unused by the consumers |
| consumers | `exp_board_patient_slot_v1`, `affected_entity_resolver`, state register | -- | the patient read moved 0.7920 -> 0.7936; the agent board read is an ISLAND (see below) |

## 6. The board's AGENT dimension (strategy's request, answered)

Scored on the same 1,424 gold agent items, live chain (organ tags -> attachment arm heads -> `coarse_roles`):

| arm | decision rate | precision when decided | with positional fallback |
|---|---|---|---|
| positional floor | -- | -- | **0.8399** |
| incumbent table, naive first-`nsubj` pick | 0.7971 | 0.8590 | 0.7879 |
| incumbent table, **subject-slot competition** pick | 0.7971 | 0.9145 | 0.8322 |
| **v3 table, subject-slot competition pick** | **0.8013** | **0.9316** | **0.8434** (+0.0035 vs floor, CI[-0.0063,+0.0140]) |

Two findings for strategy: (1) the naive "take the first nominal labelled nsubj" step in the probe was costing
**0.0443** -- the brain's read is a competition for the one subject slot (highest SUBJ activation among the
verb's `nsubj`-labelled dependents), and it removes 23 of the 44 `wrong|active|nsubj|head_ok` items; (2) with
that fixed and the v3 labels, the chain **ties** the positional floor (0.8434 vs 0.8399, CI includes 0) rather
than beating it -- so re-pointing the board's agent dimension at the chain is defensible on
one-structure-no-islands grounds but is **not** a scored win yet. The residual is 182 abstentions in which the
true agent's head is wrong under the live governor -- the heads rung again.

## 7. What it would take to make this FULLY solved, and the cheapest path (tried)

Two clauses are unmet.

- **"live-heads embedded nsubj up CI-separated."** It would take the governor's **core-argument** arcs. The
  labeler has no headroom left on the arguments the governor gets right (0.878-0.907, at the gold-heads level);
  every remaining live-arm point is behind an attachment. **Path A (cheapest), TRIED and re-measured:** use the
  heads rung's graded hand-off. Two forms: marginalising the role read over the posterior **loses** (0.7224 ->
  0.6952, and it loses for the incumbent cue set too), because the posterior is broad and mis-centred; using the
  same posterior as a **precision gate** on the arc-dependent cue **works** and is what took the live arm from
  -0.049 to neutral. That is the whole of what this rung can extract from the current hand-off.
- **"the never-labelled population at >= the NOUN population's recall."** 0.8378 vs 0.9225. The residual 6 of 37
  are partitive and measure heads whose configuration is starved: the existential configuration carries only
  **48 weighted training decisions** and the inverted-locative copular head class (`ADV_pre`) only **17**,
  because the governor removes the instances before they can be counted (its mis-attachment moves them into a
  different configuration entirely -- my attempt to un-gate construction instances at accrual changed **exactly
  zero** decisions for that reason). This is a **count** problem with a known fix: accrue the constructions over
  more text than UD-EWT train's 12.5k sentences.

## 8. Alternate paths (as brain-foundational or more), for strategy to queue

1. **Learn the cue validities from more text, not more cues.** Everything starved above is a construction with
   fewer than 50 exposures. The Competition Model's validities are *lifetime* statistics; the organ's
   `observe_role_outcome` already accrues online. Feeding it the reading corpus (simplewiki) with
   self-supervised outcomes would fill `VERB_post_ex`, `ADV_pre` and the lexical preposition values. **More
   brain-foundational than what I shipped** (it removes the treebank from the learning loop entirely). Cost:
   an outcome signal for unlabelled text -- the parser's own confident reads, which is the same
   propose-and-verify loop the learner line already uses.
2. **The filler-gap construction as a configuration, with enough exposures.** Refuted here at 12.5k sentences
   (it halves the dominant subject configuration's mass), but the mechanism is right and the failure was
   sample size. Pairs naturally with (1).
3. **Phrasal verbs as stored lexical items.** A learned (verb-lemma, particle) association would separate
   "worked **out** a deal" from "worked **on** a deal" -- the brain stores phrasal verbs as units. The organ
   already has per-lemma frame counts (`lemma_frames`); this is the same table with one more field.
4. **A graded hand-off the role rung can actually use.** The blocker is not that the heads rung hands down a
   point estimate -- it hands down a posterior, and that posterior is *mis-centred*. The lever is the
   attachment arm's **calibration** on core-argument arcs (make P(head) mean what it says), after which
   marginalisation flips from -0.027 to positive. This is a heads-rung brief, not a labels-rung one.
5. **Hand the consumers the graded role posterior instead of the MAP label.** `coarse_role_posterior` exists and
   nothing reads it; the patient/agent readers take a hard string. Precision-weighting *their* decision by the
   role competition's own margin is the same move that worked for the agent arm's `agent_competition_pick_conf`.

## 9. Priority next steps

1. Land the asset (it is measured and on disk): copy `data/hook_state/coarse_role_validities_pri103_v3.json`
   into `data/frontend_assets/` and point `HDLAB_ROLE_VALIDITIES` at it. It carries `cue_set: "v3"`, which is
   the switch; without the organ patch the key is ignored and nothing changes.
2. **Fix the instrument** (`experiments/_diag_roles_by_clause_type.py` / the `sentences` loader it borrows):
   the subtype strip has been mis-scoring every passive subject in this rung's diagnostics, and the brief that
   opened this problem was written from those numbers. Any other consumer of
   `tools.build_attachment_validities.sentences` that cares about `nsubj:pass`, `obl:agent` or `acl:relcl` has
   the same bug.
3. Re-point the board's `who_did_what_agent` dimension at the live chain **with the subject-slot competition
   pick** (one structure, no islanded copy) -- currently a tie with the positional floor, so land it for
   architecture, not for the number.
4. Queue alternate path 1 (grow the construction counts from reading) -- it is the single lever that unblocks
   both unmet bar clauses at this rung.
5. Everything else at this rung is behind the **heads rung's core-argument arcs**. That is the brief to write.
