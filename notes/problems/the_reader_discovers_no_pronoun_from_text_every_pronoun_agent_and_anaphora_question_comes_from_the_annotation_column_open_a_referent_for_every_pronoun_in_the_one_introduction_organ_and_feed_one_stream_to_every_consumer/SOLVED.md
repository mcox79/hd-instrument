---
problem: the_reader_discovers_no_pronoun_from_text_every_pronoun_agent_and_anaphora_question_comes_from_the_annotation_column_open_a_referent_for_every_pronoun_in_the_one_introduction_organ_and_feed_one_stream_to_every_consumer
status: PARTIAL
bar: "PASS = annotation invariance proven byte-for-byte (text-only vs blank column vs permuted cluster ids -> identical events/agents/patients/states/pronoun picks); text-only agents on the five evaluation documents within 5 of the component scorer's 44/52 AND CI-separated over the word-order floor on a 40-document seeded sample; the text-only pronoun instrument on MODERN GUM CI-separated over its floors with the phi twin at floor; the no-regress populations (patient, state) hold; the full board not down; ONE discovered stream feeds every consumer (grep witness) -- or a numbered located negative naming the consumer that cannot read it and why."
result: "FOUR OF THE FIVE BAR LEGS MET ON THE LANDED DIFF; THE FIFTH IS PARITY WITH ITS FLOOR AND ITS RESIDUAL IS RELOCATED BY ARITHMETIC. Every number is through the LIVE SituationReader().read() on TEXT ONLY with the PATCHED SOURCE loaded and all arms in ONE process. (1) ANNOTATION INVARIANCE PROVEN BYTE-FOR-BYTE on 3/3 documents across text-only / blank column / permuted cluster ids / correctly-linked gold ids, while the shipped reader FAILS the same test (permuted ids change its decisions) -- the test can fire. (2) AGENT, the five evaluation documents, the evaluation's own scorer, all 52 counted: 9/52 -> 43/52 (component scorer 44/52, within 1); pronoun agents 0/33 -> 31/33; missing answers 15 -> 1. On a 40-document seeded UD-EWT test sample (211 items, documents the bootstrap unit): 0.1896 -> 0.7536, +0.5640 CI[+0.4085,+0.7262] half=0.1589 CI-sep; pronoun-agent subpopulation 0.0000 -> 0.9194, +0.9194 CI[+0.8559,+0.9775] CI-sep; with the already-built agent_hybrid+agent_hybrid_construction 0.8057 / 0.9435. (3) THE PRONOUN INSTRUMENT IS THE PASS: 28 MODERN GUM test documents, 795 fixed questions from the gold, ABSTENTION=WRONG, floor recomputed on the same population -- shipped reader 0.0000 (0 questions answered), landed 0.2717 (783 answered) vs a nearest-prior-compatible-referent floor of 0.1849, +0.0868 CI[+0.0166,+0.1665] half=0.0749 CI-SEPARATED, and the info-free phi twin sits AT FLOOR (0.1799, -0.0050 CI[-0.0455,+0.0314] n.s.) while the landed pick beats it +0.0918 CI[+0.0052,+0.1904] CI-sep. (4) NO-REGRESS EXACT: patient 0.7081 -> 0.7081 and state 0.6667 -> 0.6667, delta EXACTLY 0.0000 with CI [0,0], every arm. (5) ONE STREAM: three of the four inference-path readers of the annotation column are fixed by the diff; the fourth (hdlab/space_reader.py:248, 0 mentions on text-only) is outside the three files this brief may diff and ships as space_reader_column_hunk.diff. THE LEG NOT MET: against the word-order agent floor 0.7962 the landed organ is BELOW (-0.0427 CI[-0.0802,-0.0087]) and the hybrid reaches PARITY (+0.0095 CI[-0.0128,+0.0372], separated in neither direction); a weight sweep RELOCATES that residual off the cue validity and onto the candidate set (preverbal 6/9/14 all 0.7204, worse than the shipped 3.0 at 0.7725, and that degenerate always-positional limit is itself below the floor, so 0.0758 is attributable to the competition's CANDIDATE SET alone). THE ROOT CAUSE THE PHASE-7 PUSH FOUND: the introduction organ wrote gender/number/name_gender = None on every referent, so a graded agreement cue weighted 4.0 and weighted 0.0 scored BYTE-IDENTICALLY (0.1791 both); with the file card filled the cue becomes load-bearing, and on the landed instrument a blank-card ablation sits AT FLOOR (0.1887, +0.0038 n.s.) against the filled card's +0.0868 CI-sep -- the fill is worth +0.0830 and the entire anaphora win rests on it."
floor: "Strongest floors actually run, each recomputed on its arm's own population. AGENT: the WORD-ORDER agent (nearest preverbal NOUN/PROPN/PRON by position, from the category organ's own tags, no mention stream and no retrieval) 0.7962, pronoun-agent 0.9516, same 40 documents, 211 and 124 items. ANAPHORA: nearest-prior-compatible-referent 0.1849 and nearest-prior-any 0.1849 on the same 795 questions. DEPLOYMENT floor being replaced = the shipped reader on text-only: agent 0.1896, pronoun agent 0.0000, pronoun instrument 0.0000 with 0 of 795 questions answered. ALSO RUN: the shipped six-form pick over the discovered stream scores 0.0667 (207 of 795 answered), -0.1182 CI[-0.1755,-0.0427] CI-separated BELOW the floor."
controls: "(1) INFORMATION-FREE POSITION TWIN (the same NUMBER of pronoun referents per sentence, opened at RANDOM token positions -- same counts, same forms, same machinery): agent 0.5829 vs 0.7441, true discovery +0.1611 CI[+0.1033,+0.2227] CI-sep, pronoun-agent +0.2823 CI[+0.2157,+0.3500] CI-sep, and the twin also COSTS patient accuracy (-0.0373 CI-sep) -- the gain is WHERE the pronouns are, not the extra machinery. (2) INFORMATION-FREE PHI TWIN, valid only after a CONTROL DEFECT was found and fixed: the pick re-derives features from state_of_mind.PRONOUN_SCOPE (event_centrality_coref.py:358), NOT from the mention, so permuting only referent_per_np.PRONOUN_PHI left the pick untouched and the twin could not lose -- an INVALID control, not evidence. With both tables permuted within person class (question-set size preserved) the twin LOSES: 0.1799 vs 0.2717, -0.0918 CI-sep, and sits AT FLOOR. (3) FILE-CARD ABLATION: the same pick over BLANK cards is AT FLOOR (0.1887, +0.0038 n.s.) -- the upstream fill carries +0.0830. (4) ANNOTATION-INVARIANCE TRIPLE as a can-fail control: the shipped reader FAILS on 3/3 documents, the patch passes on 3/3. (5) A/B SWITCHES: discover_pronouns=False reproduces the pre-patch organ exactly (0 pronoun records, 9/52 agents); graded_anaphora=False gives the shipped six-form pick (0.0667); fill_card=False gives the blank card. (6) LEVER ABLATIONS: the case cue as an accusative EXCLUSION +2 agents / +3 pronoun agents; the Centering-count repair the brief predicted HURTS (28/33 -> 27/33) and its stronger form was built too; dropping possessives is NULL; cm_agent OFF collapses to 10/52. (7) EXHAUSTED WITH NUMBERS: the strict person-evidence pool HURTS (ACT-R 0.2425 -> 0.1677, overlay 0.1617 -> 0.0449); the positional-weight sweep is -0.0758 CI-sep BELOW the floor at 6/9/14; a rank-based Principle-B proxy costs -0.104 (the PROXY refuted, not the constraint); window=2 beat unbounded on 67 questions and LOST on 334 (0.2545 vs 0.2784), so the small-sample result is withdrawn. (8) DERAILMENT-vs-SCORING DIAGNOSIS: of 38 annotated targets, 6 had no gold mention at the target position and 32 bound a NON-coreferent entity -- genuine derailment, not a scoring artifact."
files_changed: "experiments/exp_pronoun_referent_discovery_v1.py (NEW -- the cell). notes/problems/<slug>/pronoun_discovery_patch.diff (NEW -- the proposed hdlab change: 21 hunks, +455/-25, `git apply --check` clean against the current tree). notes/problems/<slug>/space_reader_column_hunk.diff (NEW -- the fourth consumer, both halves included; its apply-check was DENIED to me, so it ships UNVERIFIED). NO hdlab/ file written: every arm is installed by rebinding module attributes inside the cell's process, and the diff is verified by loading the PATCHED SOURCE into the live modules and re-running (43/52 agents, 31/33 pronoun agents, 0.2717 on the pronoun instrument, annotation-invariant, pre-patch organ reproduced by the A/B switches). REUSED read-only: hdlab/{referent_per_np,coref,situation_reader,state_of_mind,affected_entity_resolver,salience_binder,graded_role_assigner,graded_competition,animacy_lexicon,event_centrality_coref,morphology,space_reader}.py, experiments/{gum_coref,exp_board_agent_slot_ud_v1,exp_crosstype_gum_conll_fullread_v1}.py."
reverify: ".venv/Scripts/python.exe experiments/exp_pronoun_referent_discovery_v1.py --self-test   # 8/8, including the LIVE check that the shipped organ schedules ZERO pronoun questions on text-only while the discovery arm schedules one, plus a can-fail twin test and a window-bounds test.  Regenerate the patched copies by applying pronoun_discovery_patch.diff into a scratch copy of hdlab/, then: --verify-patch <dir>  (asserts 43/52 agents, 31/33 pronoun agents, patient 30 / state 7 unchanged, annotation invariance, and that discover_pronouns=False reproduces the pre-patch organ); --landed 40 --patched <dir>  (the agent rows, both arms in ONE process); --landed-pron 28 --patched <dir>  (the pronoun instrument with its floor, the valid twin and the blank-card ablation, all in ONE process)."
---

# SOLVED (PARTIAL) — the reader now discovers its own pronouns, and the anaphora PICK is the rung that is still open

## Status in one line
On annotation-free text the shipped reader had **no pronoun mentions at all** — the introduction organ lifted
them from the input's coref column — so the Competition-Model agent had **no candidates** (agent 9/52, pronoun
agents **0/33**) and **no anaphora question was ever scheduled**. Opening a discourse referent for every PRON
the category organ tags, and feeding **one discovered stream** to every consumer, takes agents to **43/52** on
the evaluation's five documents and **0.1896 → 0.7536** (hybrid **0.8057**) on a 40-document sample, with
patient and state **exactly unchanged** and **byte-identical predictions** whether the answer key is present,
blank, permuted or correct. The anaphora half **now passes too, after phase 7**: on 795 fixed GUM questions the landed
pick scores **0.2717 against a 0.1849 floor, +0.0868 CI[+0.0166,+0.1665] CI-separated, with the
information-free twin at floor** — a result that only became possible once the **file card was filled at
introduction** (a blank-card ablation sits at floor). The one leg still short is the **agent** row against a
strong word-order floor: **parity**, with the residual relocated by arithmetic to the competition's candidate
set (§6b).

## 0. THE OPENING MOVE — how does the brain do this (PINNED vs OUR-INVENTION)
A pronoun is a **referent-introducing expression like any other NP**. In DRT/FCS (Kamp 1981; Heim 1982) it
opens a discourse referent whose file card is nearly empty except for a **retrieval demand**: it must be
identified with an accessible prior referent. The identification is **content-addressable, cue-based
retrieval** (Lewis & Vasishth 2005 ACT-R; McElree direct access) with the **form's own phi-features** as the
cues (person/gender/number), plus the **animacy** constraint on pronoun interpretation (Garnham 2001), over
the **salient forward-looking centers** (Grosz, Joshi & Weinstein 1995 Centering). When nothing accessible
matches, the referent **stays open** — an explicit abstention, not a missing question.

| piece | status |
|---|---|
| introduction of a referent per NP, pronouns included | **PINNED** (Kamp/Heim) |
| the retrieval demand + phi/animacy retrieval cues | **PINNED** (Lewis & Vasishth; Garnham) |
| accessibility / Cf salience bounding the candidate set | **PINNED** (Centering) |
| ACT-R base-level activation `B = ln Σ_k w(role_k)·(t_now−t_k)^(−d)` | **PINNED** (Anderson & Schooler) — already in `salience_binder.actr_activation` |
| the discrete file-card record, the exact accessibility window, the exact person-evidence test | **OUR-INVENTION** (the window is SWEPT, never adopted) |
| closed-class membership decided by the category organ, features by the form | **PINNED** (the closed class is lexical; function-word bootstrapping, Abney 1991) |

**The decisive consequence, and it is the whole architecture of the fix:** the two consumers of the referent
set draw on it through **different cue filters**. Thematic role binding needs *every* NP referent (a letter, a
door — inanimate patients). Pronoun anaphora retrieves over the *tracked person* referents. The 2026-09-04
DECOUPLE implemented that separation by giving the two consumers **two different mention STREAMS**, one of
them the annotation column — which is why the column ended up on the inference path. The separation is right;
the implementation put it in the wrong place. It belongs **inside the retrieval organ as a cue filter**, not
in the stream.

## 1. THE DEFECT, REPRODUCED FIRST-HAND (the brief's phase-1 gate)
Five complete UD-EWT test documents in file order, text only (only FORM plus token/sentence boundaries cross
the reader's input boundary), the evaluation's own scorer, **all 52 eligible agent questions counted**:

| arm | agent | pronoun agent | patient | state | missing answers | pronoun records |
|---|---|---|---|---|---|---|
| shipped reader | **9/52** | **0/33** | 30/43 | 7/9 | 15 | **0** |
| discovery, role stream only | 10/52 | 0/33 | 30/43 | 7/9 | 15 | 0 |
| discovery + ONE stream | 40/52 | 28/33 | 30/43 | 7/9 | 1 | 8 |
| + the case cue as an accusative exclusion | 42/52 | 31/33 | 30/43 | 7/9 | 1 | 8 |
| **the LANDED diff** | **43/52** | **31/33** | 30/43 | 7/9 | 1 | 8 |
| component scorer (the evaluation's) | 44/52 | — | — | — | — | — |

`9/52`, `30/43`, `7/9` and `0` pronoun records reproduce the evaluation exactly. **The `disc_role` row is the
load-bearing ablation:** putting pronouns in the role stream alone buys **+1 answer**. The recovery is the
**ONE-STREAM** flip — `_coref_mentions` is what the Competition-Model agent reads.

## 2. THE SIGNAL-LOSS TRACE, CHAIN BY CHAIN, WITH COUNTS
For the signal the end read needs — *who did it, when the doer is a pronoun* — on the five documents:

| rung | hand-off produces | next rung reads | LOST |
|---|---|---|---|
| tokens → **categories** (`lexical_categories`) | PRON on 68 of 69 gold PRON tokens (0.9855); on the **33 gold agent pronouns, 33/33** | the introduction organ's per-sentence tags | **0** — the top of the chain is already at brain level |
| categories → **introduction** (`referent_per_np`) | shipped: **0** pronoun referents (PRON is in `NEVER_HEAD`; pronouns came from the column) | the role/entity stream | **33 of 33 — the entire loss is this one rung** |
| introduction → **agent candidate set** (`_cm_agent_candidates`) | after discovery 33/33 referents present | `_nominals_keep_pron` + the CASE filter | **4 of 33** to the 8-form NOMINATIVE allow-list |
| candidates → **pick** (`agent_supports` competition) | 29/33 in the set | the event's agent slot | **1 of 33** |
| introduction → **anaphora question** (`build_pronoun_targets`) | shipped: a target needs a prior mention with the **same GOLD CLUSTER ID** | the retrieval organ | **all of them** — 0 questions, and no record that any were missed |

**Brain-foundational status of each rung as it relates to THIS signal** (item 3b): categories hands down a
**graded posterior** and the introduction arm reads its argmax for a closed-class decision the organ makes at
~0.99 — adequate, and the graded row is preserved on the mention (`span_post`). The introduction rung was
**not brain-foundational at all** for pronouns: it had no pronoun operation, it had a *data feed from the
answer key*. The case rung was a **conflated value**: an allow-list of 8 nominative forms, where the brain's
cue is the **marked member** of the opposition (English marks the oblique forms; everything else is
case-neutral and can be a subject). The anaphora rung read **gold equivalence classes** as its trigger.

## 3. WHAT I BUILT (four rungs, each measured)
1. **The pronoun arm of the introduction organ** (`referent_per_np.PRONOUN_PHI`, `_mk_pronoun_referent`, the
   per-sentence PRON loop). A referent for every PRON the category organ tags, **in reading order**, with the
   form's phi-features and a fresh singleton cluster. The phi table is **composed from the tables the
   substrate already holds** — `state_of_mind.PRONOUN_SCOPE` (3rd person), `affected_entity_resolver.
   REFLEXIVE_GN` (Principle A), `state_of_mind.FIRST/SECOND_PERSON_PRONOUNS` (deixis) — plus demonstratives
   used as an NP. A PRON the lexicon does not know (an indefinite, a relative) still **opens a referent**
   with phi unknown: the organ decides pronoun-hood, the lexicon supplies features, and absence of features
   is the honest state rather than a reason to drop the referent.
2. **ONE discovered stream** (`read()`): `coref_mentions = role_mentions`. The column is still parsed, but
   only into `self._gold_align`, consulted **after** a pick to say whether it was right.
3. **The discovered question set with explicit abstentions** (`coref.discovered_pronoun_targets`): every
   third-person pronoun with an accessible phi-compatible prior referent becomes a question; every one
   without becomes a **`sm.pronoun_abstentions` record carrying the target's token position**. A zero-answer
   read now scores zero recall on a non-empty question set instead of vanishing from the denominator.
4. **The retrieval-cue pool inside the retrieval organ** (`coref.retrievable_referents`, applied in
   `_read_entities`): the 2026-09-03 flood repair, kept as the brain's own cue filter rather than as a second
   stream sourced from the answer key.

**Plus the case cue as the marked member** (`coref.ACCUSATIVE_MARKED`, used by `_cm_agent_candidates` behind
`case_cue_marked`), which is the rung that carries the last 3 pronoun agents.

## 4. THE HEADLINE, ON THE LANDED DIFF, BOTH ARMS IN ONE PROCESS
40 seeded random UD-EWT test documents (documents are the resampling unit, 2,000 bootstrap resamples), text
only. `pre` = `SituationReader(discover_pronouns=False, case_cue_marked=False)`, i.e. the pre-patch organ.

| row | pre | landed | landed + hybrid | word-order floor |
|---|---|---|---|---|
| agent (n=211) | 0.1896 | **0.7536** | **0.8057** | 0.7962 |
| pronoun agent (n=124) | 0.0000 | **0.9194** | **0.9435** | 0.9516 |
| patient (n=161) | 0.7081 | 0.7081 | 0.7081 | — |
| state (n=72) | 0.6667 | 0.6667 | 0.6667 | — |

- agent **+0.5640 CI[+0.4085,+0.7262]** half=0.1589 CI-sep; hybrid **+0.6161 CI[+0.4709,+0.7634]** CI-sep
- pronoun agent **+0.9194 CI[+0.8559,+0.9775]** half=0.0608 CI-sep; hybrid **+0.9435 CI[+0.9035,+0.9787]**
- patient and state: **delta exactly 0.0000, CI [0,0]** — the no-regress populations hold by construction
- vs the word-order floor: landed **−0.0427 CI[−0.0802,−0.0087]** (below); hybrid **+0.0095
  CI[−0.0128,+0.0372]** (**parity**, not separated in either direction)

## 5. ANNOTATION INVARIANCE — PROVEN, AND THE TEST CAN FIRE
Decisions fingerprinted as (events with agent/patient/polarity, entity states, entities with mention counts,
pronoun picks). Three conditions on the same tokens: text-only, blank column, and **mention brackets present
with PERMUTED cluster ids**.

| arm | blank == text-only | permuted == text-only |
|---|---|---|
| shipped reader | True 3/3 | **False 3/3** |
| the patch | True 3/3 | **True 3/3** |

The patched source is also invariant against a **correctly linked** column (the condition that flipped the
shipped reader's `she → alice` in the evaluation's ablation). Gold now enters correctness only.

## 6. THE ANAPHORA HALF — THE NUMBERED PARTIAL, AND WHY
The reader's own pronoun instrument, 12 MODERN GUM test documents, **text only**, a fixed set of **334**
questions taken from the gold (every third-person pronoun with a prior non-pronoun mention of its gold
entity), the reader's pick vs the gold antecedent head, **ABSTENTION = WRONG**:

| arm | accuracy | questions answered | floor |
|---|---|---|---|
| shipped reader | **0.0000** | **0 of 334** | 0.2036 |
| landed discovery (overlay pick) | 0.1617 | 98 of 334 | 0.2036 |
| discovery routed through the ACT-R object-file organ | **0.2425** | **327 of 334** | 0.2036 |
| phi twin | 0.1617 | 98 | — |

- ACT-R arm vs the nearest-prior-compatible floor: **+0.0389 CI[−0.0577,+0.1345] NOT CI-separated**
- the **phi twin does not lose** — per-item vectors identical to the true arm

**That negative is understood, with the mechanism and the number.** On 8 GUM documents read *with* their gold
column, the landed pool scores coref **0.0000 over 38 targets** against the shipped 0.7714 over 35, and the
decomposition says why: **6** targets have no gold mention at the target position and **32 bind a
NON-COREFERENT entity**. The failure is visible in the transcript — `she` bound **`youtube`** in eleven
consecutive sentences. `youtube` is a PROPN, my pool admitted every PROPN as a person candidate, the
gazetteer abstains on it so its gender is unknown, and I had deliberately made unknown gender
**non-blocking** — so nothing stopped it, and being frequent and salient it won every retrieval. This is the
**2026-09-03 pool flood recurring in a milder form**, and it is exactly the failure mode the brief's item 4
names, with exactly the repair the brief names: strengthen the **retrieval cue filter**, never return to the
column. The strict-pool build (positive person evidence required: a gender cue, a gazetteer name-gender, or
an animacy-lexicon animate reading) and the accessibility-window sweep are in the cell as
`disc_*_strict` / `--window-sweep`; their measurement is reported in §6b.

**Why the phi twin failing to fail is diagnostic, not decoration:** it proves the agreement cue is currently
**inert** in the overlay pick — the pick is recency-driven. So the anaphora rung's problem is not that the
cues are absent from the stream (the discovery arm puts them there) but that the **retrieval arithmetic does
not weight them**. The organ that *does* hold the pinned arithmetic (ACT-R activation, Centering role
prominence, the foreground window, Principle A, the impletion accrual) is
`hdlab/affected_entity_resolver.EntityTokens`, and routing the question there moved coverage from 98/334 to
**327/334** and accuracy from 0.1617 to 0.2425 — the right direction, from the right organ, and still not
separated from the floor.

## 6b. PHASE 7 — THE NEGATIVES RESEARCHED TO THE CODE, AND WHAT THAT BUILT
### (1a) WHERE THE PICK GETS ITS FEATURES — and my "the cue is inert" claim was WRONG
`hdlab/event_centrality_coref.py:355` enters the retrieval branch **only** when
`m["head"] in TARGET_PRONOUNS` — and `TARGET_PRONOUNS` (`hdlab/state_of_mind.py:86`) is
**six forms**: `{he, him, his, she, her, hers}`. Line **358** then reads the probe's features as
`sc = PRONOUN_SCOPE[m["head"]]` — the **surface-form table** at `hdlab/state_of_mind.py:72` — and lines
**359/369** use them (`_compatible_entities(sc["gender"], sc["number"])`, `_agreement_narrow(pool, ...)`).

**So two corrections to what I wrote before:**
1. **The pick does NOT discard gender/number — it uses them.** My §6 sentence "the agreement cue is inert in
   the pick" was wrong about the mechanism.
2. **My phi twin was an INVALID CONTROL.** It permuted `referent_per_np.PRONOUN_PHI` (which drives discovery
   and question scheduling) while the pick re-derives features from the **untouched** `PRONOUN_SCOPE`. That
   is why it could not lose. Fixed: `install_twin_phi` now permutes `PRONOUN_SCOPE` too, and the twin then
   **does** lose (below).
3. **The 6-form gate is the coverage number.** 236 of 334 questions are `it`/`they`/`them`/`their`/`this`/
   `that`: scheduled, then never attempted. That, not my pool, is why the overlay arm answered 98 of 334.

**Is this pri 118's organ?** **No.** pri 118's typer is `coref.name_content_tokens` (the name-vs-common route
on a mention's span). This is the antecedent **retrieval** branch in `event_centrality_coref`. Different organ,
different decision.

### THE ROOT CAUSE, FOUND BY IDENTITY: THE FILE CARD WAS BLANK
Building a graded phi cue exposed it. With a graded agreement term weighted **4.0** the pick scored **0.1791**;
with the same term weighted **0.0** it scored **0.1791** — byte-identical on 67 GUM questions. A cue cannot be
load-bearing when what it matches against is always `None`, and `referent_per_np._mk_referent` wrote
`gender=None, number=None, name_gender=None` on **every** referent, while the column source it replaced
(`parse_litbank_conll`) computed `infer_nominal_gender(span_toks)` and the gazetteer gender for each of its
mentions. **This is the same blank-card diagnosis the 2026-09-03 SOLVED recorded for the coref collapse
(0.4693 → 0.1019), still unfixed at the introduction organ.**

**BUILT (now in the diff):** `referent_per_np._file_card_features` fills the card at introduction — gender from
`state_of_mind.infer_nominal_gender`, number from the substrate's own glass-box morphology, `name_gender` from
the offline given-name gazetteer **gated on the category organ calling the head a PROPN** (without the gate it
fired on a mis-tagged `saw` → masc, observed). Introduction and feature-binding are one act, which is the
brain's form. Verified through the patched source: `mother` → fem/singular, `alice` → name_gender fem,
`brothers` → plural, and the agent rows are unchanged (43/52, patient 30/43, state 7/9).

### (2a) THE PICK AS ACT-R CUE-BASED RETRIEVAL WITH A GRADED CUE SUM — and the twin now LOSES
`graded_resolve` implements `A(cand) = ln Σ_k w(role_k)·(t_now−t_k)^(−d) + w_g·gender_match + w_n·number_match
+ w_focus·1[cand is the previous utterance's Cb]`, over every third-person pronoun, with the accessibility
bound applied at **retrieval**, Principle A for reflexives, and impletion accrual. 12 GUM test documents,
**334** fixed questions, text only, ABSTENTION = WRONG, floor recomputed on the same population:

| arm | accuracy | answered | vs floor 0.2036 |
|---|---|---|---|
| shipped reader | 0.0000 | 0 of 334 | −0.2036 CI[−0.2635,−0.1547] CI-sep BELOW |
| overlay pick (the 6-form gate) | 0.1617 | 98 | −0.0419 CI[−0.1885,+0.1418] |
| **graded ACT-R, window 2** | **0.2545** | 309 | +0.0509 CI[−0.0486,+0.1815] |
| **graded ACT-R, unbounded window** | **0.2784** | 329 | +0.0749 CI[−0.0284,+0.1943] |
| graded, gender cue OFF | 0.2246 | 309 | +0.0210 CI[−0.0523,+0.1095] |
| **graded, PHI TWIN (PRONOUN_SCOPE permuted too)** | **0.1617** | 303 | **−0.0419 CI[−0.1241,+0.0354]** |

- **The twin LOSES**: 0.2545 → 0.1617, i.e. −0.0928 against its own arm, and it falls **below** the floor while
  the true arm is above it. The agreement cue is now load-bearing, which it provably was not before the card
  was filled.
- **The gender cue is worth +0.0299** (0.2545 vs 0.2246 with it off).
- **NOT CI-SEPARATED from the floor** — the best arm is +0.0749 with a CI half-width of **0.111** at 12
  documents. That is an **UNDERPOWERED instrument**, not a closed question; §6c reports a larger population.

**Two ablations that reversed at scale, reported rather than cherry-picked.** On a 4-document probe (67
questions) the window helped (+0.045) and dropping my Principle-B proxy helped (+0.104). On the full 334
questions the **unbounded** window is better (0.2784 vs 0.2545), so the 4-document window result was
small-sample noise and **window=2 is not supported**. The Principle-B finding held in direction: my proxy
excluded every same-sentence core-ranked mention, which is **not** the clause-mate co-argument relation —
**what is refuted is MY PROXY, not Principle B**, which stays a live lead (§9 lead 4).

**The strict person-evidence pool is EXHAUSTED, with the number:** requiring a gender cue, a gazetteer name or
an animacy-lexicon animate reading **hurts** — ACT-R arm 0.2425 → 0.1677, overlay arm 0.1617 → 0.0449 — because
the gazetteer and animacy lexicon do not cover most person names, so it deletes more true antecedents than
distractors. The `youtube` derailment is therefore an **entity-TYPE knowledge** gap (§9 lead 6), not a
filter that was missing.

### (1b) WHERE THE POSITIONAL CUE'S VALIDITY COMES FROM — nowhere; and (2c) is EXHAUSTED
`hdlab/graded_role_assigner.py:265-267`:
`AGENT_VALIDITIES = {"preverbal": 3.0, "core_arg": 2.0, "animacy": 2.0, "salience": 2.0, "adjacency": 1.0,
"byagent": 6.0, ...}`, and the comment immediately above it (lines 259-261) says it is **"a STATIC asset …
hand-set from cue validity, NOT trained"**; the module's `__bf_note__` repeats **"agent weights hand-set"**.
**So the word-order cue's validity was never accrued from any register — not 19c, not gold heads, not the
organ's own decisions. It is a hand-set constant of 3.0, against a non-positional sum of 6.0**
(`core_arg` 2.0 + `animacy` 2.0 + `salience` 2.0), and `net_activation` is a plain additive sum
(`hdlab/graded_competition.py:57`). That is the arithmetic by which a correct word-order pick gets outvoted.

**I then swept it rather than proposing a re-accrual, and the hypothesis is REFUTED** (40 documents, 211 items,
text only, same population and floor as §4):

| `preverbal` weight | agent | vs word-order floor 0.7962 |
|---|---|---|
| 3.0 (shipped) | **0.7725** | −0.0237 CI[−0.0632,+0.0000] not sep |
| 6.0 | 0.7204 | −0.0758 CI[−0.1191,−0.0305] CI-sep BELOW |
| 9.0 | 0.7204 | −0.0758 CI[−0.1191,−0.0305] CI-sep BELOW |
| 14.0 | 0.7204 | −0.0758 CI[−0.1191,−0.0305] CI-sep BELOW |

Raising the positional weight makes it **worse**, and 6/9/14 are **identical** — the cue saturates the argmax
immediately, so the competition degenerates to "always the nearest preverbal candidate". **That degenerate
limit scores 0.7204, itself below the 0.7962 floor.** Therefore the residual is **not the cue's validity and
cannot be fixed by re-accruing it**: it is the competition's **CANDIDATE SET** (clause bounds, the case
filter, mention granularity), which admits a different set of tokens than the floor's raw preverbal scan.
**EXHAUSTED at −0.0758 across a 2×–4.7× weight sweep, with the residual relocated to the candidate set.**

### (2b) THE `agent_hybrid` FLIP ON THE FULL BOARD — BOARD-INVISIBLE BY CONSTRUCTION, with the proof
I did not spend 70-90 minutes producing exact zeros, and here is why, from the code rather than from
recollection. `experiments/exp_board_agent_slot_ud_v1.py` contains **zero** references to `SituationReader`;
its line **154** calls `GRA.hybrid_agent_pick(...)` **directly**, and line **262** makes `hybrid − floor` the
row's **headline** (`mt` at 263 is `hybrid − twin`). **The board's agent row already IS the hybrid, computed
without the reader.** `agent_hybrid` is a *reader* flag, so flipping it cannot move that row — or any other:
the only board row that builds a reader is `exp_situation_model_state_qa_v1:119` via
`all_capabilities_off(bind_entity_states=True)`, which sets `referent_per_np=False`, and the diff adds
`discover_pronouns` / `fill_card` / `case_cue_marked` to `CAPABILITY_FLAGS` so that row turns them off too and
stays byte-identical. A full-board A/B would be **exact zeros by construction**, which is a control, not a
flip decision (memory: capped-board exact zeros are underpowered). **The flip IS measured where it lands** —
the reader's own text-only read: agent **0.7536 → 0.8057**, pronoun agent **0.9194 → 0.9435**, patient and
state exactly unchanged (§4). **I have NOT put the `agent_hybrid` default flip in the diff**: it is a
different organ's default, its own docstring records a 19c regression, and the evidence I have is
reader-level only — it goes to strategy as next step 1 rather than riding in on this brief's patch.

## 6c. THE LANDED ANAPHORA RESULT — the diff's own pick, its floor, a valid twin and the card ablation
28 MODERN GUM test documents, **795** fixed questions taken from the gold (every third-person pronoun with a
prior non-pronoun mention of its gold entity), **text-only input**, ABSTENTION = WRONG, floor recomputed on
this population, documents the bootstrap unit, **all four arms in ONE process**:

| arm | accuracy | answered | vs floor 0.1849 |
|---|---|---|---|
| shipped reader (text-only) | 0.0000 | 0 of 795 | — (it has no pronoun mentions at all) |
| **the LANDED diff** | **0.2717** | **783** | **+0.0868 CI[+0.0166,+0.1665] half=0.0749 CI-SEP** |
| `fill_card=False` (blank cards) | 0.1887 | 783 | +0.0038 CI[−0.0261,+0.0345] **AT FLOOR** |
| `graded_anaphora=False` (the shipped six-form pick) | 0.0667 | 207 | −0.1182 CI[−0.1755,−0.0427] **BELOW** |
| **info-free PHI TWIN** (both tables permuted) | **0.1799** | 783 | −0.0050 CI[−0.0455,+0.0314] **AT FLOOR** |

- **landed − twin = +0.0918 CI[+0.0052,+0.1904] CI-separated.** The twin is valid now (§6b-1a) and it loses.
- **landed − blank card = +0.0830.** With blank cards the pick is statistically indistinguishable from the
  floor. **The upstream file-card fill is what makes the whole anaphora capability exist**; no amount of work
  on the pick could have substituted for it.
- The shipped pick over the same discovered stream is **CI-separated BELOW the floor** — its six-form gate
  answers 207 of 795, and under ABSTENTION=WRONG that coverage loss is fatal.
- A larger population was needed to see this: at 12 documents the margin was +0.0749 with a **0.111**
  half-width (not separated); at 28 documents it is +0.0868 with a **0.0749** half-width (separated). The
  earlier n.s. result was **underpowered, not negative** — reported that way at the time, and now resolved.

### THE ANNOTATED-PATH "REGRESSION", RESOLVED — it was a DENOMINATOR, not a loss
§6 reported the reader's annotated read falling from 0.7714 to 0.0000, and I flagged it as the one measured
regression. Re-measured on the landed diff (8 annotated GUM documents, gold coref column present):

| arm | `coref_acc` | targets attempted | **pronouns actually got right** |
|---|---|---|---|
| pre-patch organ | 0.7714 | **35** | **27** |
| the LANDED diff | 0.1858 | **253** | **47** |

**The two rates are not comparable and the paired bootstrap over them is meaningless** (it returns
CI[−0.19,+13.33] precisely because the per-document populations differ 7-fold). `pre` schedules a question
only where the gold column already links a `he`/`she` to a prior mention — a **gold-selected, easy,
self-chosen denominator** — while the landed organ schedules every third-person pronoun it discovers and
never abstains into a smaller denominator. On the same 8 documents the landed form gets **47 pronouns right
against 27**, a **+74% absolute gain**, while its *rate* falls because it attempts 7× more.

**So `sm.coref_acc` is a conditional-on-attempted rate whose denominator the model itself chooses, and it is
therefore not a no-regress instrument** — which is finding E03 of the evaluation, arriving here empirically. A
fixed question set is the instrument, and on the fixed 795 it is the landed form that wins CI-separated
(§6c). **I am not claiming the annotated rate is fine: I am saying the comparison it invites is invalid, and
giving the count that is valid.** The board's coref row inherits this defect and that is worth strategy's
attention (next step 7).

## 7. THE CONSUMER AUDIT (item 3, GENERALIZE) — enumerated on disk, then counted
| inference-path consumer of the coref column | status |
|---|---|
| `referent_per_np.referent_per_np_source` (the pronoun source) | **FIXED** — the category organ's PRON tags |
| `situation_reader.read` → `_coref_mentions` (the AGENT competition) | **FIXED** — one discovered stream |
| `situation_reader.read` → `build_pronoun_targets` (the questions) | **FIXED** — `discovered_pronoun_targets` |
| `situation_reader._read_entities` correctness | **FIXED** — scorer-side alignment, after the pick |
| **`hdlab/space_reader.py:248`** (the SPACE dimension, `track_space` default ON) | **NOT FIXED** — it **re-parses the file itself** and gets **0 mentions / 0 pronouns** on text-only input, in BOTH arms. Outside the three files this brief may diff. |
| `bundle_focus_coref`, `coref_distractor_suppress`, `event_centrality_coref` `build_pronoun_targets` | **not on the inference path** — every use is inside a `_selftest_*` function |

Counts on 3 text-only documents: shipped coref stream **0** mentions / 0 pronouns / 0 questions; landed
**97** mentions, **30** pronouns, 2 scheduled questions; `space_reader` **0** mentions in both arms.

## 8. THE FULL BOARD — IT CANNOT SEE THIS, AND THAT IS pri 122's FINDING, NOT A SILENCE I CHOSE
I enumerated the board's row modules rather than asserting it. `exp_board_agent_slot_ud_v1`,
`exp_board_coref_gum_v1`, `exp_board_patient_slot_v1`, `exp_hybrid_unified_incumbent_coref_gum_v1`,
`exp_route_unified_to_consumers_gum_v1` and `exp_affected_entity_binding_parallelism_gum_v1` contain **zero**
references to `SituationReader`. The only row that builds a reader is `exp_situation_model_state_qa_v1:119`,
via `SituationReader.all_capabilities_off(bind_entity_states=True)`, which sets `referent_per_np=False` — and
the diff adds `discover_pronouns` and `case_cue_marked` to `CAPABILITY_FLAGS`, so `all_capabilities_off` turns
them off too and that row is **byte-identical**. **The board is structurally invariant to this change**, which
is finding E01 / priority 122. Running it twice would produce exact zeros that measure nothing, and
capped-board exact zeros are a control, not a flip decision. The honest board-reachable equivalent is §6's
annotated-path A/B on the reader itself, and **that one currently regresses** — reported above, not hidden.

## 9. WHAT WOULD TAKE THIS TO A FULL PASS (every lead, researched, with what I could build)
| # | lead | research / prior work on this rung | status here |
|---|---|---|---|
| 1 | **The gendered-pronoun pool needs positive person evidence** | Garnham 2001 animacy constraint (PINNED); the 2026-09-03 flood (coref 0.4693→0.1019, 514/539 derailment) is the same shape | **BUILT → EXHAUSTED**: it HURTS (ACT-R 0.2425→0.1677; overlay 0.1617→0.0449) because the gazetteer/animacy lexicon miss most person names. The derailment is a knowledge gap (lead 6), not a missing filter |
| 1b | **FILL THE FILE CARD AT INTRODUCTION** — the measured root cause: a graded agreement cue at weight 4.0 and weight 0.0 scored byte-identically, because every referent's gender/number/name_gender was `None` | Kamp/Heim file cards carry the entity's conceptual features; the 2026-09-03 SOLVED recorded exactly this blank card | **BUILT AND IN THE DIFF** (`_file_card_features`): the agreement cue becomes load-bearing (+0.0299) and the phi twin now LOSES (−0.0928) |
| 2 | **Sweep the accessibility window** — the brief's one free parameter | Centering Cf recency; `affected_entity_resolver.FOREGROUND_WINDOW = 2` (swept 1/2/3/5, flat on its own population) | **BUILT AND SWEPT (0/1/2/3/5)**: window 2 beat unbounded on a 4-document probe (+0.045) and LOST on the full 334 questions (0.2545 vs 0.2784) → **window=2 NOT supported; unbounded reported** |
| 3 | **Route the pick through the organ that holds the pinned retrieval arithmetic** | `salience_binder.actr_activation` + `ROLE_PROMINENCE` (Centering Cf) + `foreground` + Principle A/B + impletion accrual, all already measured wins on this rung (salience prior +0.27 CI-sep on GUM pronoun undergoers; Principle B +0.048; Principle A +0.0151; accrual +0.020) | **BUILT** (`disc_actr`, then `graded_resolve` with a graded cue sum): coverage 98→329 of 334, 0.1617→**0.2784**. Best arm; still not CI-sep from the floor at 12 docs (half-width 0.111) |
| 4 | **Binding Principle B on the discovered stream** — my ACT-R arm passes `coarg_key=None`, so the clause-mate co-argument is never excluded | Chomsky 1981 / Reinhart 1983, `P(plain pronoun \| clause-mate co-argument) = 0`, PINNED and **already built** as `affected_entity_resolver.coarg_head_gidx` (+0.048 gold / +0.049 predicted) | **PROXY BUILT AND REFUTED, CONSTRAINT STILL LIVE**: a rank-based same-sentence proxy cost −0.104, because "any other core-ranked mention in the sentence" is not the clause-mate CO-ARGUMENT. Needs the real clause-mate map from the reader's own parse |
| 5 | **Kehler–Rohde next-mention prior** `P(r \| pron) ∝ P(r next-mentioned)·P(pron \| r)` | PINNED; the prior alone saturates ~0.45, the grammar likelihood added +0.093 | **NOT BUILT** — the natural successor once 4 lands |
| 6 | **Entity TYPE knowledge, so `youtube` is not a person candidate** | brief already filed: `acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref`; the gazetteer covers given names only | **NOT BUILT** — a knowledge gap, not a mechanism gap, with an owner |
| 7 | **The agent floor gap: word-order vs the competition on modern prose** | `situation_reader.py:1714-1729` already measures it (UD-EWT positional 0.855 vs always-compete 0.758) and `agent_hybrid`/`agent_hybrid_construction` are the built repair, **default-OFF because the reader's live who-did-what board is 19c LitBank** — and 19c is banned from requirements (owner 2026-09-06) | **MEASURED**: hybrid takes agent 0.7536→0.8057 and reaches parity with the floor. Recommend flipping both ON — **not put in this diff** (another organ's default, its own docstring records a 19c regression, and my evidence is reader-level only) |
| 7b | **The competition's positional cue WEIGHT** | `AGENT_VALIDITIES["preverbal"] = 3.0`, hand-set and never trained (§6b-1b) | **BUILT, SWEPT, EXHAUSTED**: 6/9/14 all give 0.7204 (worse than 3.0's 0.7725), −0.0758 CI-sep BELOW the floor; the degenerate always-positional limit is itself below the floor, so the residual is the **candidate set**, not the weight |
| 7c | **The competition's CANDIDATE SET** (where 7b relocated the residual): clause bounds + the case filter + mention granularity admit a different token set than the floor's raw preverbal scan | Competition Model: the candidate set is the competition's population, and clause-bounding is PINNED — but the bound's EXTENT is ours | **NOT BUILT** — the sharpest remaining agent lead, and it is now numbered: 0.7204 degenerate-positional vs 0.7962 floor = **0.0758 attributable to candidates alone** |
| 8 | **`space_reader` re-parses the column** | §7 | **NOT BUILT** — outside my three files; hand-off with the number |
| 9 | **The animacy lexicon reads WordNet through nltk at inference** (`animacy_lexicon.py:52`) | pre-existing: `graded_role_assigner.py:1575` already calls `lookup_animacy` on every read, so my pool adds no new dependency — but it is a real BF exposure | **NOT BUILT** — ship it as a count asset; named for strategy |

## 10. THE OWNER'S PUSH SCRIPT, RUN ON MYSELF
**(i) Performance against the brain at each rung, and where signal is lost.** Categories 0.9855 PRON / 33-of-33
on agent pronouns — at brain level. Introduction: was 0 of 33, now 33 of 33 — at brain level. Case cue: 29/33
→ 33/33 with the marked-member form. Agent pick: 31/33 on the five documents, 0.9435 on 124 items — a
competent reader is ~1.00, so ~0.06 remains and it is the competition's weighting, not the input. Anaphora
pick: 0.2425 vs a human's near-ceiling on these 334 questions — **this is the big remaining gap in the chain**,
and it is now measurable for the first time because the questions exist.
**(ii) Prototype past every wall; a heuristic is not the landed form.** The case cue is a **closed-class
lexical fact** (the marked oblique forms), not a heuristic. The person-evidence pool is a **cue filter over
three existing graded/lexical sources** — the landed form should read the animacy lexicon as a shipped count
asset (lead 9) rather than WordNet at read time. The accessibility window is **swept, never adopted**.
**(iii) Is the wiring alone sufficient to reach brain level?** No. The wiring gets agents to parity with a
positional floor and gets anaphora from *no questions at all* to *questions asked and 24% right*. The
remaining gaps are **representational and upstream**: Principle B is unwired on this stream (lead 4), the
next-mention prior is unbuilt (lead 5), and entity type is unknown (lead 6).
**(iv) Nothing frozen.** The phi table and the accusative set are **closed-class lexicons** (finite, lexical
facts a reader acquires once), not fitted parameters — I state that plainly rather than claim an observe path
I did not build. The things that *should* move do: the Competition-Model cue validities are already fit from
counts and have a brief filed (`cue_validities_are_a_lifetime_statistic...`), and the accessibility window is
swept. **The honest gap:** PRON membership itself could be induced distributionally by the category organ
instead of read from a table — a brief-ready lead.
**(v) State of the art on each rung's own metric.** Subject/agent identification: a supervised parser labels
`nsubj` far above our 0.9435 on pronoun subjects, but the **glass-box lever that closes it is the hybrid
(lead 7), already built**. Pronoun coreference on GUM: the board's own gold-mention pronoun row is 0.4681
with a 0.3621 floor; our text-only 0.2425 against a 0.2036 floor is a *harder population* (no gold mentions
at all) and the gap to 0.4681 is leads 4–6.
**(vi) False-negative audit of my own negatives.** The Centering-count lever lost (28/33 → 27/33). I did not
leave it there: the mechanism is that **counting by head string makes every `he` in the passage one
referent**, so the count measures the FORM, not the referent. I built the stronger form (count non-pronoun
mentions only, `freq2`) — so the negative is understood and the stronger version was tested rather than
assumed.
**(vii) Prior work on this rung, already banked.** The two SOLVED.md files this brief names (the +0.336
referent-per-NP source and the DECOUPLE that made it safe), pri 116's case flip, pri 118's mention typer,
and `notes/BRAIN_MATH_REFERENCE.md` §A — which is where leads 3–5 come from.

## 11. EVALUATION OF THE MOST SUCCESSFUL IMPROVEMENT — why the signal maximised
The agent recovery (+0.564, and +0.9194 on the pronoun subpopulation) is large because **the real,
mathematical brain-foundational chain was cracked all the way to the top for that one signal**:

| rung | cracked? |
|---|---|
| tokens → categories (`lexical_categories`, count-based, live) | **yes** — already at 0.9855 PRON / 33-of-33 on the agent pronouns; nothing to fix |
| categories → **introduction of a pronoun referent** | **yes** — the missing operation, supplied (DRT introduction, PINNED) |
| introduction → **one stream to every consumer** | **yes** — the gold leak removed, the same stream to agents, entities, states, anaphora |
| stream → **agent candidate set** (the CASE cue) | **yes** — the cue re-expressed as the marked member of the opposition |
| candidates → **agent pick** (the Competition Model) | **partly** — the competition under-weights word order on modern prose; the built hybrid reaches parity |
| **file card** (the referent's conceptual features) | **yes, in phase 7** — was blank on every referent, now filled at introduction; this is what made the agreement cue load-bearing at all |
| **anaphora pick** (cue-based retrieval) | **partly** — the pinned activation equation is now the pick, the twin loses, and coverage went 0 → 329 of 334, but it is not CI-separated from a nearest-prior floor at 12 documents |
| **space dimension** | **no** — it re-parses the column and is blind to the stream (hunk written, §7) |

The rungs that did **not** crack are exactly the rows that fall short of the bar. That is the pattern the
owner predicts, and it held here twice: the agent row fell short while the candidate set was uncracked, and
the anaphora row could not move at all while the **file card** was blank — the cue had nothing to match
against, which no amount of work on the *pick* could have fixed. **Phase 7's lesson, concretely: I diagnosed
"the cue is inert in the pick" and was wrong about the location. The cue was inert because the UPSTREAM
hand-off carried no features.** Reading the pick's actual lines (`event_centrality_coref.py:355-369`) is what
relocated it, and filling the card upstream is what made every downstream retrieval experiment meaningful.

## 12. ALTERNATE PATHS — equally or MORE brain-foundational than what I shipped
1. **Make the pronoun a PREDICTION rather than a discovery.** Structure: the predictive-coding hierarchy
   (Levy 2008 surprisal; Lewis & Vasishth held expectations). Maths: at each word the reader already carries a
   next-category distribution; a pronoun would be *expected* at a subject slot whose referent is highly
   accessible, and the referent could be bound **before** the form is fully identified. What it would take:
   the incremental parser's hold-expectation table already exists (`attachment_arm.hold_expectation`) and
   would need a referent-accessibility term. Why not now: it changes the reader's control flow, and the
   discovery arm is a strict prerequisite (you cannot predict a referent for a token class you never open).
   **Arguably more brain-foundational than what I shipped.**
2. **Induce the closed class instead of tabling it.** Structure: distributional category induction
   (Gleitman's closed-class scaffold; the substrate's own `reading_learned_pos_category_induction...` brief).
   Maths: PRON membership from the paradigmatic distribution; gender/number from **agreement co-occurrence**
   (a form that co-occurs with `himself` is masc). What it would take: an agreement-count asset over the
   reading corpus. Why not now: the closed class is small and stable, and the table I compose is already the
   substrate's own; this would remove the last hand-authored lexicon on the rung.
3. **One retrieval organ for every anaphor, with the anaphor type as an arm.** Structure: one cue-based
   retrieval structure (the consolidation audit's principle). The substrate currently has the reader's
   overlay pick *and* `EntityTokens` *and* the unified referent resolver computing overlapping things; §6
   shows the overlay pick is the weakest of them. What it would take: making `EntityTokens` the reader's sole
   anaphora path, with Principle A/B and the next-mention prior as arms. Why not now: it is a larger
   consolidation than this brief's remit, and my `disc_actr` arm is the measured down-payment on it.
4. **Score coreference by POSITION, not by head string, everywhere.** The `resolved_head` → cluster map is
   head-level on both sides (it always was: `resolve_stream`'s own `head_to_cluster` is a head-string map), so
   two distinct referents sharing a head are indistinguishable to the scorer. The diff carries
   `target_wpos`; extending it to the *picked* mention's position would make the instrument exact. Cheap,
   and it would sharpen every number on this rung.

## 12b. THE OWNER'S PUSH SCRIPT, RUN A SECOND TIME ON WHAT PHASE 7 BUILT
**(i) Where is signal lost NOW?** Not at categories (0.9855 / 33-of-33), not at introduction (33/33), not at
the case cue (33/33), and no longer at the file card (filled). It is lost in exactly two places, both
numbered: the agent **candidate set** (0.7204 degenerate-positional vs 0.7962 floor = 0.0758) and the
anaphora **pick quality** (0.2784 vs a 0.2036 floor, +0.0749 with a 0.111 half-width = underpowered).
**(ii) Prototyped past every wall?** Five levers built and measured this phase: the file-card fill (kept, in
the diff), the graded ACT-R cue sum (kept), the strict pool (EXHAUSTED, hurts), the Principle-B proxy
(REFUTED as a proxy), the positional weight sweep (EXHAUSTED, relocates the residual). None is a heuristic
standing in for a learned form: the card's sources are three existing organs, and the activation equation is
the pinned one.
**(iii) Is wiring alone enough?** **No, and phase 7 says why more precisely than phase 6 could:** the wiring
is now complete on this rung and the two residuals are a *candidate-set* question and an *entity-type
knowledge* question. Neither is wiring.
**(iv) Nothing frozen.** The file card's features are computed per read from the form and the lexicon, not
stored — so the card is not a frozen table. The phi and accusative lexicons remain closed-class lexical facts,
stated as such. The one genuinely fitted constant I touched, `AGENT_VALIDITIES["preverbal"]`, I swept rather
than adopted, and the sweep **refuted** re-accrual as the fix — so there is no table here awaiting an observe
path that I have quietly left frozen.
**(v) vs the state of the art.** Agent: parity with a strong positional floor; the glass-box lever that
exceeds it is built (`agent_hybrid`, 0.8057) and the remaining 0.0758 is the candidate set. Anaphora: the
board's gold-mention GUM pronoun row is 0.4681 over a 0.3621 floor; our 0.2784 over 0.2036 is on a strictly
harder population (no gold mentions, ABSTENTION=WRONG, every third-person form) and the named levers to close
it are Principle B (real clause-mates), the Kehler-Rohde next-mention prior, and entity type.
**(vi) False negatives audited.** Three of my own negatives were wrong or mislocated and I say so with the
evidence: "the agreement cue is inert in the pick" (wrong location — the card was blank), the phi twin's
failure to fail (an invalid control — I permuted the wrong table), and the window's apparent benefit (a
4-document artefact that reversed at 334 questions).
**(vii) Prior work reused.** `salience_binder.actr_activation`, `ROLE_PROMINENCE`, `foreground`,
`REFLEXIVE_GN`, `infer_nominal_gender`, `name_gender_for_span`, the glass-box morphology, and
`notes/BRAIN_MATH_REFERENCE.md` §A — every piece of the new pick is an organ that already existed.

## 13. PRIORITY NEXT STEPS (for strategy)
1. **The agent competition's CANDIDATE SET** (lead 7c) — the residual is now isolated to it by arithmetic:
   the competition's own degenerate-positional limit is 0.7204 against a 0.7962 raw-token floor, so 0.0758 is
   attributable to candidates alone, independent of any cue weight.
2. **Flip `agent_hybrid` + `agent_hybrid_construction` ON** (lead 7): +0.0521 agent on the landed organ,
   parity with the positional floor. Deliberately **not** in this diff — another organ's default, and the
   evidence is reader-level only.
3. **Wire the REAL clause-mate co-argument for Principle B** (lead 4) — PINNED, already built in
   `affected_entity_resolver`, and my rank-based proxy is measured at −0.104, so the proxy must not be shipped.
4. **Apply `space_reader_column_hunk.diff`** (lead 8) — written this phase, both halves included; its
   apply-check was DENIED to me, so strategy must run it.
5. **Power the pronoun instrument** — at 12 documents the half-width is 0.111 on a +0.0749 margin; the leg is
   underpowered, not closed.
6. **Entity TYPE knowledge** (lead 6) — `acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref` is the
   filed owner of the `she → youtube` class of error, now shown to be unfixable by filtering.
7. **Rebuild the board rows on the live reader** (pri 122) — until then every result on this rung, including
   this one, is board-invisible **by construction** (§6b-2b).

INTEGRATED_BY_STRATEGY 2026-09-15 18:18 local -- DONE by strategy after first-hand reverify: the 21-hunk diff + space_reader_column_hunk.diff APPLIED (referent_per_np: PRON referents from the category organ + _file_card_features; coref: discovered_pronoun_targets + graded_pronoun_resolve; situation_reader: one discovered stream to _cm_agent_candidates / the anaphora questions / entities, the space hand-off; space_reader: mentions=) plus strategy's D02 guard (resolved_cluster=None in the graded branch). Reverify: cell --self-test 8/8 on the landed tree; the 21-file witness batch (data/hook_state/pri125_witnesses.log) green except three attributed reds (situation_model_qa alignment -> pri 131; referent_per_np_organ SUPERSEDED exit 3; space W4 pre-existing on HEAD); three witnesses re-pinned from numbers to claims. PRODUCT BOARD pri125a (capped 24/600/60): text-only agent 0.7363 (answered 0.994), patient 0.6808 > 0.6384, state 0.7455 sep, wic 0.85 sep, coref n=0 (row alignment predates discovered targets -> pri 131), headline 0.6425; three provenance columns identical; component rows byte-identical to pri118a. Status PARTIAL stands (agent at parity with the word-order floor, not above; the anaphora pick's identity contract is pri 131). The agent's DENIED apply-check of the space hunk was not retried by it; strategy applied the hunk through the normal integration path and measured it (-0.043 on the 6-passage space witness, both arms; recorded).
