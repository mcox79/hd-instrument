---
problem: the_boards_seven_rows_never_run_the_reader_each_rebuilds_its_own_copy_from_annotated_cased_files_so_a_reader_repair_worth_0_41_propn_f1_is_board_invisible_rebuild_the_rows_on_the_live_reader
status: PARTIAL
bar: "All seven rows scored from the live reader's output on the document text (one read per document), provenance fields published, the old rebuilt numbers retired in notes/reference_retired_claims_never_requote.md with the new honest baseline stated, the three landings' effects visible -- OR a numbered reason a row cannot be reader-driven (with the rebuilt form kept and labelled)."
result: "ALL SEVEN ROWS ARE NOW SCORED OFF `SituationReader.read`, AND THE BOARD OVERSTATES THE READER ON RAW TEXT BY +0.70 ON THE ROW THAT MATTERS MOST. (1) THE COUNTED WITNESS, one process: while the board's own six functions produced all seven headline rows, `SituationReader.read` was called 0 times and the reader's only sentence source 0 times -- an EXACT zero from the call graph, now counted for read() itself and not only for the sentence source (pri 116 counted the latter). 28 `board_*_dimension` arms exist in the board file; 9 can reach the reader at all by static call-graph reachability, and none of the 7 headline producers is among them. (2) WHO-DID-WHAT AGENT, the whole UD-EWT test split (2,077 sentences, 104 pseudo-documents of 20, chunk-paired bootstrap 2,000), the reader's OWN read of annotation-free text: 0.1510 (n=1,424, answered 0.9831) against its OWN recomputed positional floor 0.8371 -- CI-separated BELOW it. The published rebuilt row is 0.8552 against 0.8468. THE LOSS IS FULLY ATTRIBUTED, BY COUNT: 948 of the 1,424 gold agents (66.6%) are headed by a PRONOUN and the reader scores 0 of 948 on them (504 of those 948 have the agent slot literally unbound, `?`); on the 476 non-pronoun agents it scores 0.4517. On annotation-free text the reader has NO pronoun mentions at all, so a pronoun agent is unreachable by construction. (3) THE PROTOTYPE THAT LOCATES IT: give the reader a singleton mention on every token ITS OWN category organ tags PRON (no gold read) and the agent row goes 0.1510 -> 0.7114, +0.5604 CI[+0.5038,+0.6193] CI-SEPARATED, the pronoun slice 0.0000 -> 0.9726 (922 of 948) -- and the NON-pronoun slice REGRESSES 0.4517 -> 0.1912, which is the number pri 125's landed form has to beat (adding pronouns as bare candidates is not the same as weighting them by the Competition Model's own cue validities). (4) A SECOND, INDEPENDENT GOLD GATE FOUND IN hdlab: `coref.build_pronoun_targets` opens a target only when an EARLIER mention carries the SAME cluster id -- and that id is the treebank's coref column. So the reader's anaphora POPULATION is itself gated on the answer key: with the annotation supplied it is 381 targets over 40 GUM documents; with the pronouns discovered from text but no cluster column it is 0, because no two mentions can share a cluster. The coref row therefore has ZERO decisions on annotation-free text for two separate reasons, and only one of them is pri 125's. (5) THE ROWS THAT SURVIVE THE LIVE READ, with their floors recomputed in place: STATE 0.7937 (n=378) vs most-recent-noun 0.5767, CI-separated, answered 0.8413 -- within 0.0027 of the published rebuilt 0.7910, so the instrument is not systematically pessimistic; PATIENT 0.6869 (n=1,255) vs nearest-post-verbal 0.6303, CI-separated ABOVE (published rebuilt 0.8143 / 0.7259 -- the board overstates it by +0.1274); WiC through the READ-BOUND closure `sm.select_sense` 0.7583 (n=120, coverage 1.000) vs the majority floor 0.5500, +0.2083 CI[+0.0583,+0.3500] CI-separated, foreign-context twin 0.5917 beaten +0.1667 CI[+0.0750,+0.2667]; SALIENCE reader-driven 0.2750 (n=40 documents) vs the reader's own first-introduced entity 0.1250, +0.1500 CI[+0.0500,+0.2750] CI-SEPARATED -- the rebuilt row (0.2656 vs 0.2031) does NOT separate, so this row is BETTER measured on the reader. (6) THE TWO ROWS THAT LOSE TO A SIMPLE FLOOR ON THE READER'S OWN POPULATION, which the rebuilt rows hide: PRONOUN COREF 0.4961 (n=381) vs same-surface string identity 0.7323, -0.2362 CI[-0.4487,-0.0463] CI-separated BELOW, and the info-free twin (0.3150) NOT beaten CI-separated (+0.1811 CI[-0.0073,+0.3378]); COMMON-NOUN COREF 0.5156 (n=898) vs same-head string identity 0.6158, -0.1002 CI[-0.1256,-0.0782] CI-separated BELOW (twin 0.0935 beaten CI-sep). (7) COMMON-NOUN COREF IS ALREADY ANNOTATION-INVARIANT -- 0.5156 with the coref column supplied vs 0.5167 without it, one item of 898 -- so that row needs no annotation and can be promoted as-is. (8) PHASE 7 -- THE HEADLINE IS SWAPPED AND THE TWO REMAINING GAPS ARE ATTRIBUTED TO A RUNG EACH. The board diff now makes `aggregate_19c_free` THE READER'S OWN READ OF THE RAW TEXT (the product number) and keeps the old figure in full as `aggregate_component_rebuilt`; both go into notes/BOARD_TREND.jsonl from the first run, every reader row publishes its DOCUMENT cap, and `trend_regressions` REFUSES to compare reader rows measured at different caps (both directions exercised). THE NEW HEADLINE, from the rows measured here (GUM 40 documents + the FULL UD-EWT test split + 120 WiC pairs): 0.4717 model / 0.6868 floor / 0.2513 twin, n=4,115, 3 of 6 rows CI-separated -- against the COMPONENT number 0.6200 / 0.5266 (n=11,291). The reader with the mentions supplied is 0.4740 (n=4,496); with the pronoun prototype 0.6656; and substituting pri 125's published landed agent value into the same aggregate PROJECTS 0.6802 (an arithmetic projection on a different agent population, NOT a measurement). THE AGENT MECHANISM, COUNTED: my prototype writes ONLY pronoun singletons into the mention column, and `_cm_agent_candidates` reads exactly that column -- so on 600 UD-EWT sentences the candidate set holds 692 mentions of which NONE is a content noun (176 flagged pronoun + 516 first/second-person pronouns that `PRONOUN_SCOPE` does not flag, hence admitted as 'nominals'), and 302 of 600 sentences have no non-pronoun candidate at all; the shipped text-only arm holds 0 mentions on all 600 sentences (600 of 600 sentences with no candidate), which is why the Competition Model never runs. That is a CANDIDATE-SET composition fact, not a cue-weighting one, and it is exactly why pri 125's ONE-STREAM form (content heads AND discovered pronouns in the same stream) does not pay the -0.2605 non-pronoun cost my injection does. THE PATIENT GAP IS ATTRIBUTED TO ONE RUNG: on 401 items over 600 UD-EWT sentences, the reader's read scores 0.6808, the SAME landed organ (`predicate_argument_frontend.structural_patient_pick`) called on the READER'S OWN tags and parse scores 0.7980, and on the frontend tagger+parser 0.8030 -- so the READ's event/candidate layer costs +0.1172 CI[+0.0784,+0.1566] CI-SEPARATED while the reader's own categories and parse cost +0.0050 CI[-0.0047,+0.0150] NOT separated (cross-tab: 63 items the organ gets right and the read gets wrong, 15 the other way). The 0.13 is inside read(), not in the parse. (9) THE THREE LANDINGS, A/B'd ON THE READER-DRIVEN ROWS (8 GUM documents + 200 UD sentences): pri 117 (the predicate-slot cue) is VISIBLE -- patient +0.0158 CI[+0.0049,+0.0293] CI-SEPARATED, the first landing ever shown CI-separated on a board-shaped row through the live reader; pri 116 (the case) MOVES four reader-driven rows (salience +0.1250, patient +0.0158, agent +0.0129, common-noun -0.0705) where it left all seven rebuilt rows byte-identical, but none separates at this document cap; pri 113 (non-verbal predication) is EXACTLY 0.0000 on every row in both arms, and the reason is arithmetic -- all three UD rows iterate gold VERBs or copular clauses, which is precisely why pri 121 built a separate non-verbal row."
floor: "EVERY floor is RECOMPUTED IN PLACE on the arm's OWN population, never pasted from the board. GUM rows (doc-paired bootstrap 2,000): coref -- the strongest of same-surface string identity 0.7323 / agreement-compatible recency 0.4829 / plain recency 0.4199, taken on the reader's own target list; salience -- the reader's OWN first-introduced entity 0.1250; common-noun -- same-head string identity 0.6158 / recency 0.2049 over the reader's own prior mentions. UD-EWT rows (chunk-paired bootstrap 2,000): agent -- nearest PRE-verbal nominal computed on the READER'S OWN categories 0.8371; patient -- nearest POST-verbal nominal on the reader's own categories 0.6303; state -- the most-recent-noun positional binding (exp_copular_is_a_binding_readout_v1.positional_floor) on the reader's own categories 0.5767. WiC -- the majority label on the scored population 0.5500. The published REBUILT reference is the board's own last full run (notes/BOARD_TREND.jsonl, 2026-09-15, commit 0108f0086): AGG 0.6200 / coref 0.4217 / salience 0.2656 / common-noun 0.5383 / agent 0.8552 / patient 0.8143 / state 0.7910 / wic 0.7493."
controls: "(1) AN INFO-FREE TWIN ON EVERY ROW, recomputed on the row's own items: coref/common-noun -- a uniformly random PRIOR mention (0.3150 / 0.0935); salience -- a random reader entity (0.0250); agent/patient -- a random sentence nominal (0.2458 / 0.2112); state -- the gold holders shuffled within the sentence (0.7302); WiC -- the SAME read-bound closure fed a FOREIGN pair's context (0.5917). Every twin loses CI-separated except on the coref row, where it does not (reported, not hidden). (2) THE COUNTED CALL-GRAPH WITNESS (ReaderCallCounter): 0 read() calls and 0 sentence-source calls during the rebuilt seven rows; the reader-driven rows make exactly one read() per document per provenance mode. Monkeypatching is per-module and restored on exit; no hdlab file is edited. (3) THE PROVENANCE CONTROL, three columns on the SAME reader and the SAME documents: annotated / text-only / text-only-with-the-organ's-own-pronouns. The text-only file is asserted byte-identical to the annotated one except the mention column, and the pron-discovered file byte-identical to the text-only one except singleton spans, and its spans are asserted DIFFERENT from the gold spans -- so no gold column can leak in. (4) COVERAGE BEFORE QUALITY, on every row: answered-rate agent 0.9831 / patient 0.9912 / state 0.8413, WiC coverage 1.000 (0 abstentions), common-noun 2,398 of 10,793 reader referents coincide with a gold mention head. The FIRST WiC measurement read coverage 0.000 and was MY bug (WiC ships pos as 'N'/'V', WordNet wants 'n'/'v'), caught by the coverage check and fixed before any claim. (5) AN INSTRUMENT UPPER BOUND on what the bare head-string match costs: credit any token of the gold ARGUMENT's dependency subtree and agent goes 0.1510 -> 0.2072, patient 0.6869 -> 0.7745 -- so string matching accounts for at most 0.056 / 0.088 of the gaps, not the +0.70. (6) HARNESS IDENTITY: the role-mention snapshot wrapper is asserted to leave the read byte-identical (entities 195/195, events 116/116, every predicate/agent/patient tuple equal), and the reader's own pronoun targets are asserted 1:1 with sm.coref_resolutions so the floors run on the identical decision list. (7) THE PATCHED BOARD WAS EXECUTED END-TO-END before the diff was proposed (a meta-loader compiles the patched source with __file__ set to its real repo path, write_metrics=False): 7/7 checks PASS -- every headline row stamped, all three provenance columns populated, the reader-driven rows keeping their own provenance, rebuilt_vs_reader naming all seven rows, and trend_row carrying dims_reader so a reader-driven regression is caught by trend_regressions. (8) MODERN gold only (GUM / UD-EWT / WiC); the gold columns are the answer key in every arm, and no arm's DECISION reads one (HDLAB_GUM_DECISION=organ, the live default). (9) PHASE 7: the 4-FILE patched change was EXECUTED end-to-end again -- 14/14 checks PASS, including the PATCHED verification witness W1 run for real (green: HEADLINE = reader_textonly, COMPONENT rebuilt kept), the matched-cap trend rule exercised in BOTH directions (same caps -> compared; different caps -> skipped WITH the reason), and the patched tools/substrate_health selector shown to read the board's own `capped` flag instead of the n<10000 heuristic that would otherwise have silently dropped the (document-capped) reader headline. (10) THE PATIENT ATTRIBUTION IS A THREE-ARM DECOMPOSITION ON THE SAME ITEMS (R read / O organ-on-reader-parse / B organ-on-frontend-parse) with a paired chunk bootstrap per contrast and a full cross-tabulation, so the rung is isolated rather than inferred."
files_changed: "experiments/exp_board_rows_on_the_reader_v1.py (NEW -- the reader-driven seven rows in three provenance columns, the counted reader-call witness, the static provenance table for all 28 board arms, the three-landing A/B, the pronoun-discovery prototype, the AGENT candidate-set composition count, the PATIENT three-arm rung attribution, the per-row cap fields, a forward-compatible pronoun-question builder, --self-test 15/15); notes/problems/<slug>/SOLVED.md; notes/problems/<slug>/board_rows_on_the_reader_patch.diff (PROPOSED, NOT applied -- FOUR files: experiments/exp_situation_model_qa_modern_v1.py +219/-10, tools/substrate_health.py +8/-1, verification/test_modern_board_landing.py +22/-7, experiments/exp_copular_subject_attachment_learned_v1.py +7/-3; `git apply --check` CLEAN, and all four patched sources EXECUTED end-to-end before proposal, 14/14); data/exp_board_rows_on_the_reader_v1/{gum_d40,ud_full,wic_c120,rebuilt_cap,landings_l8,attrib_p7}.json. NO hdlab/ or tools/ file was edited; no landed record was rewritten (every run is routed by HDLAB_EXP_NAME into this cell's own directory)."
reverify: ".venv/Scripts/python.exe experiments/exp_board_rows_on_the_reader_v1.py --self-test   # ~4 min, writes only to its own selftest dir; expect SELF-TEST PASS (15 checks): the text-only file differs from the annotated one ONLY in the mention column, the pron-discovered file carries only singleton spans the category organ opened and they are NOT the gold spans, the snapshot wrapper leaves the read byte-identical, the reader's pronoun targets are 1:1 with sm.coref_resolutions, every arm of every row scores the SAME items, and the agent row publishes the pronoun/not-pronoun slice.   THEN THE HEADLINE (the whole UD-EWT test split, both arms, ~48 min):  OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 HDLAB_EXP_NAME=board_rows_on_the_reader_v1 .venv/Scripts/python.exe experiments/exp_board_rows_on_the_reader_v1.py --ud --ud-cap 0 --n-boot 2000 --tag _reverify   # expect agent 0.1510 vs floor 0.8371 (n=1424, pronoun slice 0/948), patient 0.6869 vs 0.6303 CI-sep, state 0.7937 vs 0.5767 CI-sep, and the pron-discovery contrast on agent +0.5604 CI[+0.5038,+0.6193] sep=True.   AND THE COUNTED WITNESS (~4 min):  ... --rebuilt --docs 40 --ud-cap 600 --n-boot 1000 --tag _reverify   # expect SituationReader_read_calls 0 and sentence_source_calls 0, and 28 board arms of which 9 statically reach the reader.   AND THE GUM ROWS (40 documents x 3 provenance modes, ~67 min):  ... --gum --docs 40 --n-boot 2000 --tag _reverify   # expect coref annotated 0.4961 (n=381) vs string-identity 0.7323, textonly n=0; salience 0.2750 vs 0.1250 CI-sep; common-noun 0.5156 vs 0.6158 and 0.5167 text-only.   AND WiC (~23 min):  ... --wic --wic-cap 120 --n-boot 2000 --tag _reverify   # expect 0.7583 vs 0.5500 CI-sep, coverage 1.000, rebuilt-style on the same items 0.7833.   AND THE LANDINGS A/B (~52 min):  ... --landings --docs 8 --ud-cap 200 --n-boot 1000 --tag _reverify   # expect pri117_off patient +0.0158 CI[+0.0049,+0.0293] sep=True, pri113_off exactly 0.0000 everywhere.   AND THE PHASE-7 ATTRIBUTION (~3 min):  ... --attrib --ud-cap 600 --n-boot 2000 --tag _reverify   # expect candidate_composition reader_textonly mentions 0 / 600 of 600 sentences with no candidate, pron_discovered 692 mentions with 0 content nouns and 302 of 600 sentences still with none; patient_attribution R 0.6808 / O 0.7980 / B 0.8030 with read_layer +0.1172 CI[+0.0784,+0.1566] sep=True and tags_and_heads_layer +0.0050 NOT sep.   AND THE PATCHED 4-FILE CHANGE, executed without touching the repo: see section 9."
---

# The board grades a component and reports it as the reader: on annotation-free text the live reader names the doer of a sentence 15 times in 100, and the board's row for that says 86

**STATUS: PARTIAL** (solver scope; WIP until the owner marks DONE). Glass-box; no external LLM, no spaCy, no nltk
tagger, no supervised parser at inference. MODERN gold only (GUM / UD-EWT / WiC). **No `hdlab/` or `tools/` file
was written** -- the board change is proposed as `board_rows_on_the_reader_patch.diff` and was EXECUTED end to end
before being proposed.

---

## 1. THE OPENING MOVE -- what may an INSTRUMENT read, and what does a reader actually receive?

This is an instrument brief, so the opening question is pri 109's, sharpened: **what does the live system know at
decision time, and may the instrument read only that?** The brain-foundational content of the answer is specific,
and the measurement turned on it.

- **A comprehender is handed a TOKEN STREAM and nothing else.** There is no channel into the language system that
  supplies "here are the referring expressions, and which of them co-refer". Detecting the referring expression IS
  the first half of the job (Kamp 1981 DRT; Heim 1982 File Change Semantics: an indefinite OPENS a file card, a
  pronoun issues a RETRIEVAL DEMAND against the accessible cards). It is not an input to comprehension.
- **So an instrument that supplies the annotated mention spans measures a COMPONENT.** That is a legitimate thing to
  measure. It is not the product's number, and the two must not be quoted as one thing.
- **The reader's own sentence source is the only place the percept enters** (`hdlab.scene_segment.parse_conll_sentences`
  -- the visual word-form route, left occipito-temporal; Cohen & Dehaene 2002). pri 116 counted the calls the seven
  rows make to it: zero. A row that never touches the percept cannot see a repair to the percept.

The cell therefore has one rule: **the model's answer comes out of the SituationModel the live reader returned, and
nothing else.** Where the reader's input contract still requires an annotation column, that fact is published as a
PROVENANCE field on the row instead of being hidden inside a number.

---

## 2. THE COUNTED WITNESS -- the zero, for `read()` itself and not only for the sentence source

`ReaderCallCounter` wraps `SituationReader.read` and `hdlab.scene_segment.parse_conll_sentences` (per module, restored
on exit; no hdlab file edited) and counts calls while the board's own six row functions produce all seven headline
rows, in ONE process:

| | count |
|---|---|
| `SituationReader.read` calls during the seven rebuilt rows | **0** |
| reader sentence-source calls during the seven rebuilt rows | **0** |
| `board_*_dimension` functions in the board file | **28** |
| of those, arms that can reach the live reader AT ALL (static call-graph reachability) | **9** -- `affect_harm_help`, `causal_multihop`, `causal_sign`, `coref_via_reader`, `negation_quantifier`, `nonverbal_predication`, `occ_appraisal`, `selective_reliability`, `state_closure` |
| of those 9, producers of a HEADLINE row | **0** |

These zeros are properties of the call graph, not underpowered estimates. The static table is a LOCATOR (it is an
upper bound -- a module can mention `SituationReader` without calling `read`); the counted zero is the proof.

---

## 3. THE SEVEN ROWS, SCORED OFF `sm` -- and what each one says

**GUM, 40 documents drawn EVENLY SPACED across the board's own 128-document test split** (a prefix cap would have
handed the reader two genres, since GUM files sort by genre), 41,485 tokens, one `read()` per document per provenance
column, document-paired bootstrap 2,000.

| row | provenance | n | model | strongest floor | twin | model - floor | verdict |
|---|---|---|---|---|---|---|---|
| coref (pronoun) | annotation supplied | 381 | **0.4961** | **0.7323** same-surface string identity | 0.3150 | **-0.2362 CI[-0.4487,-0.0463]** | ❌ CI-sep BELOW the floor; twin NOT beaten (+0.1811 CI[-0.0073,+0.3378]) |
| coref (pronoun) | text only | **0** | -- | -- | -- | -- | **no decisions** (section 5) |
| coref (pronoun) | text only + the organ's own pronouns | **0** | -- | -- | -- | -- | **no decisions** (section 5) |
| salience | annotation supplied | 40 | **0.2750** | 0.1250 first-introduced entity | 0.0250 | **+0.1500 CI[+0.0500,+0.2750]** | ✅ CI-sep, twin beaten |
| salience | text only | 40 | 0.2250 | 0.1250 | 0.0500 | +0.1000 CI[0.0000,+0.2250] | ~ not separated |
| common_noun_coref | annotation supplied | 898 | **0.5156** | **0.6158** same-head string identity | 0.0935 | **-0.1002 CI[-0.1256,-0.0782]** | ❌ CI-sep BELOW the floor; twin beaten CI-sep |
| common_noun_coref | text only | 898 | 0.5167 | 0.6169 | 0.0780 | -0.1002 CI[-0.1256,-0.0782] | **annotation-INVARIANT (one item of 898)** |

**UD-EWT, the WHOLE test split** -- 2,077 sentences written as 104 reader-native pseudo-documents of 20 (UD-EWT
carries no coref annotation, so these rows are annotation-free BY CONSTRUCTION), chunk-paired bootstrap 2,000.

| row | arm | n | model | strongest floor | twin | model - floor | answered |
|---|---|---|---|---|---|---|---|
| who_did_what_agent | text only | 1,424 | **0.1510** | **0.8371** nearest pre-verbal nominal | 0.2458 | **-0.6861** ❌ | 0.9831 |
| who_did_what_agent | + the organ's own pronouns (PROTOTYPE) | 1,424 | **0.7114** | 0.8371 | 0.2458 | -0.1257 ❌ | 0.9831 |
| who_did_what_patient | text only | 1,255 | **0.6869** | 0.6303 nearest post-verbal nominal | 0.2112 | **+0.0566 CI-sep** ✅ | 0.9912 |
| who_did_what_patient | + prototype | 1,255 | 0.6869 | 0.6303 | 0.2112 | identical (delta 0.0000) | 0.9912 |
| state | text only | 378 | **0.7937** | 0.5767 most-recent-noun | 0.7302 | **+0.2170 CI-sep** ✅ | 0.8413 |
| state | + prototype | 378 | 0.7937 | 0.5767 | 0.7302 | identical | 0.8413 |

**WiC, 120 pairs (the board's own smoke population), scored through the closure the READ binds (`sm.select_sense`),
coverage 1.000, 0 abstentions:** model **0.7583**, majority floor 0.5500, **+0.2083 CI[+0.0583,+0.3500] CI-separated**;
the info-free twin (the same closure fed a FOREIGN pair's context) 0.5917, beaten **+0.1667 CI[+0.0750,+0.2667]**.
The read-time contract costs almost nothing: the rebuilt arm's exact call (a pre-built `candidate_synsets` list and a
hand-filtered content-word context with the target removed) on the SAME items scores 0.7833, i.e. **-0.0250**.

### THE REBUILT-vs-READER TABLE, with the provenance in words

The rebuilt column is the board's own last FULL run (`notes/BOARD_TREND.jsonl`, 2026-09-15, commit `0108f0086`).
**The populations are NOT the same -- that IS the finding** -- so each cell carries its own n.

| row | rebuilt: "a rebuilt read from the annotated file" | reader: "the reader's own read of the text, annotation supplied" | reader: "the reader's own read of the raw text alone" |
|---|---|---|---|
| coref (pronoun) | 0.4217 / floor 0.3192 ✅ (n 3,130) | 0.4961 / floor 0.7323 ❌ (n 381) | **no decisions (n 0)** |
| salience | 0.2656 / 0.2031 ~ (n 128) | **0.2750 / 0.1250 ✅ (n 40)** | 0.2250 / 0.1250 ~ (n 40) |
| common_noun_coref | 0.5383 / 0.5342 ~ (n 2,939) | 0.5156 / 0.6158 ❌ (n 898) | 0.5167 / 0.6169 ❌ (n 898) |
| who_did_what_agent | 0.8552 / 0.8468 ✅ (n 1,423) | -- (UD has no coref column) | **0.1510 / 0.8371 ❌ (n 1,424)** |
| who_did_what_patient | 0.8143 / 0.7259 ✅ (n 1,255) | -- | 0.6869 / 0.6303 ✅ (n 1,255) |
| state | 0.7910 / 0.5714 ✅ (n 378) | -- | **0.7937 / 0.5767 ✅ (n 378)** |
| wic | 0.7493 / 0.5000 ✅ (n 2,038) | -- | 0.7583 / 0.5500 ✅ (n 120) |
| **cross-population summary (informational only)** | **0.6200 / 0.5266, 5/7 CI-sep (n 11,291)** | **0.4740 / 0.6904 (n 4,496)** | **0.4717 / 0.6867, 3/6 CI-sep (n 4,115)**; with the pronoun prototype **0.6654 / 0.6867** |

**THE SINGLE SENTENCE THE OWNER ASKED FOR.** *The scoreboard says the system names the doer of a sentence 86 times
in 100. When the same reading system is handed the same sentences as plain text, it names the doer 15 times in 100,
and two thirds of the misses are sentences where the doer is a word like "he", "they" or "I" -- which the reader
never even registers as a thing being talked about.*

---

## 4. THE STATUS PROBE -- where the signal is lost, chain by chain, with counts

**Each row's signal requirement in one sentence, then every hand-off up the chain.**

| # | hand-off | what it PRODUCES | what the next rung READS | what is LOST on annotation-free text | BF status of this hand-off |
|---|---|---|---|---|---|
| 0 | a board row -> the reader | nothing; the row rebuilds the read from the annotated file | the aggregate | **THE WHOLE READER** (0 `read()` calls, 0 sentence-source calls, counted) | NOT_BF **as an instrument claim**: a COMPONENT score published as the reader's |
| 1 | `read(conll_path)`'s input contract | a CoNLL carrying a MENTION column | `parse_litbank_conll` | -- | **NOT_BF**: a comprehender receives words; detecting the referring expression is the first half of the job (Kamp/Heim) |
| 2 | `referent_per_np.referent_per_np_source` | content-head NP referents from TEXT **+ pronoun mentions lifted from the coref column** | `role_mentions` -> roles, entities, common-noun resolution | **every pronoun referent.** GUM 40 docs: reader entities 6,962 with the column vs 6,524 without; 5,358 coref-column mentions vs 0 | **NOT_BF on the pronoun half** -- this is pri 125's rung |
| 3 | `parse_litbank_conll` -> `self._coref_mentions` | the coref-column mention stream | `_cm_agent_candidates` (the AGENT candidate set) **and** `build_pronoun_targets` (the anaphora population) | **the entire AGENT candidate set** -> `(None, None)` -> the Competition Model never competes; **the entire anaphora population** -> 0 targets | the COMPUTATION is PINNED (Bates & MacWhinney graded cue competition); the CANDIDATE SET is handed in from outside |
| 4 | `coref.build_pronoun_targets` | a target only where an EARLIER mention shares the **same cluster id** -- and that id is the treebank's coref column | `sm.coref_resolutions` | **the population itself is gold-gated** (381 targets with the column, 0 without, even with the pronouns discovered) | **NOT_BF**: whether an antecedent exists is the reader's problem, not an admission gate |
| 4b | `state_of_mind.TARGET_PRONOUNS` | the he/she family only (6 forms) | the same | `it`/`they`/`them`/`their`/`themselves` anaphora is never attempted **even with the annotation**: 1,237 targets against 3,187 third-person pronoun mentions on the full GUM test split -- **1,950 of 3,187 (61.2%) never decided** | narrower than the board's population by construction |
| 5 | `sm.events[].agent` | a head STRING | the agent row | a pronoun agent cannot be named when no pronoun referent exists: **0 of 948**, 504 of them unbound (`?`) | -- |
| 6 | `sm.events[].patient` | a head STRING off the structural arc | the patient row | nothing from the mention stream (delta 0.0000 under the prototype); the residual is the arc + the pronoun UNDERGOER (pronoun-headed patients 0.3521 of 284 vs 0.7848 of 971) | BF_SPIRIT |
| 7 | `sm.entity_states` | (holder, property) surface strings | the state row | **nothing** -- 0.7937 text-only vs the published rebuilt 0.7910 | BF_SPIRIT (Kimian states; Maienborn 2005) |
| 8 | `sm.select_sense` (the closure the read installs) | a committed coarse supersense | the WiC row | **nothing measurable** -- coverage 1.000, and the read-time contract costs -0.0250 vs the rebuilt call | BF_SPIRIT (Frisson good-enough; Rodd shared-core) |

**THE LOSS IS CONCENTRATED AT ONE RUNG AND IT IS UPSTREAM OF FOUR OF THE SEVEN ROWS: the mention stream is an INPUT
to the reader rather than a product of it.** Two independent gates implement that, and they must BOTH be opened:
`referent_per_np_source` (pronouns lifted from the column -- pri 125) and `build_pronoun_targets` (the target
population admitted only on a shared GOLD cluster id -- not yet filed anywhere).

### How the brain does THIS signal, mathematically, along the chain

- **Introduction.** DRT/FCS is explicit and compositional: the discourse referent is opened by the NP itself
  (Kamp 1981; Heim 1982). A pronoun is not a different KIND of object -- it opens a card whose content is an
  unsatisfied retrieval demand. Nothing in the theory lets the referent set be supplied from outside the text.
- **Retrieval.** Cue-based content-addressable retrieval over the open cards, activation
  `A_i = B_i + sum_j W_j S_ji` with a recency/decay term (Lewis & Vasishth 2005 ACT-R; McElree 2003 direct access).
  The retrieval CUES are the pronoun form's own phi-features -- gender, number, person, case -- which is why the
  substrate's `TARGET_PRONOUNS` restriction to the he/she family is a real agreement axis but the wrong POPULATION:
  `it` and `they` carry number and animacy cues, so they are retrievable, just with different cue validities.
- **Role assignment.** Graded parallel cue competition, `A_i = sum_c w_c * support_c(i)` with validity
  = availability x reliability (MacWhinney & Bates 1989), which is a Bayesian posterior over the candidate set
  (McClelland 2013). **The competition is only as good as the candidate set, and a candidate set that omits every
  pronoun cannot assign a pronoun agent at any weight.** That is the arithmetic behind 0 of 948.
- **What this predicts and the measurement confirms:** opening the pronoun referents should recover almost all of
  the pronoun slice (0.9726 measured) and should NOT help the patient slot (delta 0.0000 measured, because the
  patient is read off the structural arc, not off the candidate competition).

---

## 5. THE NUMBERED REASONS A ROW IS NOT FULLY READER-DRIVEN (bar clause 8's escape hatch, used twice)

1. **`coref` has ZERO decisions on annotation-free text, for TWO separate reasons.** (a) The reader has no pronoun
   mentions at all without the coref column (`referent_per_np_source`); (b) even when the pronouns ARE discovered,
   `build_pronoun_targets` admits a target only if an earlier mention carries the SAME cluster id, and cluster ids
   come from the coref column -- so with text-derived singletons the population is still 0. **The rebuilt form is
   kept and labelled**; the reader-driven form is published with `n: 0` and a provenance line saying so, because a
   zero-decision row must be visible as a zero, not absent.
2. **`who_did_what_agent`, `who_did_what_patient` and `state` have no "annotation supplied" column at all**, because
   UD-EWT ships no coref annotation. Their single column is annotation-free, which is the honest product number; the
   published rebuilt numbers for those rows come from the same gold via a different (non-reader) path.
3. **`wic` has no document to read** -- a WiC item is a sentence pair. It is made reader-driven by reading each
   sentence as its own one-sentence passage and committing through `sm.select_sense`, which is the closure the read
   installs. The residual difference from the rebuilt arm (-0.0250) is the read-time contract, measured.

---

## 6. THE PROTOTYPE THAT LOCATES THE BIG LOSS -- and the number its landed form must beat

**What it is:** the reader's input keeps the same tokens and no gold column, and carries a SINGLETON mention span on
every token **the reader's own category organ tags PRON** (`hdlab.frontend.tagger()` -> `lexical_categories`). No
gold is read; the self-test asserts the spans differ from the gold spans. It is a PROTOTYPE, and the landed form
must be the organ opening the referent itself inside `referent_per_np_source`, with the phi-features read off the
form's own lexical entry -- which is exactly pri 125's build.

| | agent, all 1,424 UD-EWT items | pronoun-headed gold agents (948) | non-pronoun gold agents (476) |
|---|---|---|---|
| text only | 0.1510 | **0.0000** (504 unbound) | 0.4517 |
| + the organ's own pronouns | **0.7114** | **0.9726** (922 of 948) | **0.1912** |
| paired contrast | **+0.5604 CI[+0.5038,+0.6193] CI-sep** | +0.9726 | **-0.2605** |

**THE REGRESSION IS THE USEFUL PART AND IT IS THE HAND-OFF TO pri 125.** Adding pronouns as BARE candidates makes
the competition prefer them almost unconditionally: the non-pronoun agent slice falls 0.4517 -> 0.1912 (215 -> 91
hits of 476). The Competition Model's own answer is that a candidate enters with a WEIGHT -- case (nominative),
animacy, givenness/Centering frequency -- not as an equal member of the set. So the landed form's acceptance test is
not "does the pronoun slice rise" (it does, to 0.97) but **"does it rise without costing the non-pronoun slice
0.26"**. That is a specific, numbered target for the organ that lands this rung.

---

## 7. THE THREE LANDINGS, A/B'd ON THE READER-DRIVEN ROWS (checklist item 6)

Each landing turned OFF on the SAME capped population (8 GUM documents + 200 UD sentences), everything else
identical, paired per cluster. `default - off` > 0 with CI-separation means the landing is finally VISIBLE.

| landing turned off | salience[ann] | common-noun[ann] | agent[text] | patient[text] | state[text] | coref[ann] |
|---|---|---|---|---|---|---|
| **pri 116** -- the sentence source lowercases again | **+0.1250** [0.0000,+0.3750] | **-0.0717** [-0.1539,+0.0143] | +0.0129 [-0.0041,+0.0324] | +0.0158 [-0.0100,+0.0377] | 0.0000 | 0.0000 |
| **pri 113** -- non-verbal predication off | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| **pri 117** -- the predicate-slot cue off | 0.0000 | 0.0000 | +0.0043 [0.0000,+0.0132] | **+0.0158 CI[+0.0049,+0.0293] ✅ VISIBLE** | 0.0000 | 0.0000 |

**Three different verdicts, each with its reason.**
- **pri 117 is VISIBLE** -- `who_did_what_patient` +0.0158 CI-separated through the live reader. This is the first
  time one of the last three landings has been shown CI-separated on a board-shaped row that actually runs the
  reader. On the rebuilt board it was a -0.0008 population artefact.
- **pri 116 MOVES four reader-driven rows** where it left all seven rebuilt rows byte-identical (pri 116 counted
  that). At this document cap none of the moves separates -- 8 documents / 200 sentences is a control-sized run, not
  a decision-sized one, and the honest statement is "the case flip is now VISIBLE IN KIND on the reader-driven rows
  and needs the full split to be visible in degree". **The common-noun point estimate is NEGATIVE (-0.0705), and
  that comparison is population-confounded in the way pri 109 documented**: lowercasing collapses the name
  population, so more referents are typed common and fall into the row, where they resolve easily by repeated
  surface string. It is not evidence against the case flip; it is the same artefact, reproduced.
- **pri 113 is EXACTLY 0.0000 on every row in both arms, and the reason is arithmetic, not power**: the three UD
  rows iterate gold VERBs (agent/patient) or copular clauses (state), so a non-verbal predicate is outside all three
  populations by construction. That is precisely why pri 121 built a separate non-verbal row, and it stays the right
  answer.

---

## 8. THE NEGATIVES, EACH UNDERSTOOD WITH A NUMBER

**(N1) The WiC row first measured coverage 0.000 -- the organ abstained on 100% of pairs -- and it was MY bug.**
WiC ships `pos` as `"N"`/`"V"`; WordNet wants `"n"`/`"v"`; the rebuilt arm maps it through `E._WNPOS` before
enumerating candidates and my first version did not, so `wn.synsets(lemma, pos="N")` returned `[]` and
`select_sense` returned `None` every time. Fixed; coverage 1.000; the row then CI-separates over its floor. Recorded
because this is exactly the failure the "check coverage before reading chance as a finding" discipline exists to
catch, and the fix changed the conclusion completely.

**(N2) The pronoun-coref row loses to same-surface string identity by -0.2362, and its twin is NOT beaten
CI-separated.** Understood, with the mechanism: the reader's own population is the he/she family with a prior
same-cluster mention, and on a gendered pronoun chain "the most recent earlier mention with the SAME surface form"
is an unusually strong rule -- it scores 0.7323 here against 0.3005 on the board's wider third-person population.
So this is not the same question the board's coref row asks, and it is not evidence that the resolver is worse than
previously thought; it is the first measurement of the resolver against a floor recomputed on ITS OWN decisions, and
on that population the floor wins. The forward lever is the population, not the pick: `TARGET_PRONOUNS` admits 6
forms and leaves 1,950 of 3,187 third-person anaphors undecided.

**(N3) The common-noun row is CI-separated BELOW same-head string identity (-0.1002) and ANNOTATION-INVARIANT.**
Both halves matter. The invariance (0.5156 vs 0.5167, one item of 898) means this row needs no annotation and can be
promoted to the reader immediately. The negative margin is consistent with pri 109's gold-free result (margin
+0.0015, not separated) and sharper, because the floor is recomputed on the reader's own prior mentions rather than
on the gold mention stream.

**(N4) The non-pronoun agent slice REGRESSES under the prototype (-0.2605).** Fully understood and mechanistic:
bare candidates with no cue weighting. Section 6 turns it into the acceptance test for the landed form.

**(N5) The reader-driven agent row stays BELOW its own positional floor even after the prototype (0.7114 vs
0.8371).** Not a wall: the floor is "nearest pre-verbal nominal on the reader's own categories", and modern UD-EWT
prose is canonical, so word order is near-ceiling (the board's own note records this for the rebuilt row too). The
brain's answer is that word order is the highest-validity English cue and the Competition Model should DEFAULT to
it and override only on marked cues -- which is what the board's rebuilt `hybrid` arm does and what the live
reader's agent route does not. **Naming it as a specific lever: the live agent route should be the hybrid
(word-order default + marked-cue override), the same one the board arm scores at 0.8552.** That single alignment is
the largest remaining reader-driven gap on this board and it is an `hdlab` change, so it is filed, not built here.

---

## 8b. PHASE 7 (a) -- WHY MY PROTOTYPE REGRESSED THE NON-PRONOUN AGENTS AND pri 125's LANDED FORM DOES NOT

**The mechanism is a CANDIDATE-SET composition difference, not a cue-weighting difference, and it is counted.**
`situation_reader._cm_agent_candidates` builds the Competition-Model AGENT candidate set from
`self._coref_mentions` -- the stream parsed out of the input file's MENTION column, and nothing else. My
prototype writes **only pronoun singletons** into that column, so that is the whole candidate set:

| arm (600 UD-EWT test sentences) | mentions the AGENT competition sees | flagged pronoun | flagged "nominal" | content nouns | sentences with NO non-pronoun candidate |
|---|---|---|---|---|---|
| text only (as it ships) | **0** | 0 | 0 | 0 | **600 of 600** |
| text only + my prototype | **692** | 176 | 516 | **0 by construction** | **302 of 600** |

Two things follow, and both are arithmetic. (1) With 0 mentions, `_cm_agent_candidates` returns
`(None, None)` and **the Competition Model never runs at all** -- which is why the shipped text-only agent row
is 0.1510 rather than merely degraded. (2) With a pronoun-only candidate set, a non-pronoun agent has **no
correct candidate to win**, so the competition must answer with a pronoun: the non-pronoun slice falls
0.4517 -> 0.1912. The 516 "nominals" are the sting in the tail -- they are first- and second-person pronouns
(`I`, `you`, `we`, `me`), which `state_of_mind.PRONOUN_SCOPE` does not list, so `parse_litbank_conll` does not
flag them `is_pronoun` and the `case_filter` that keeps only nominative pronoun agents never looks at them.

**pri 125's landed form does not pay that cost because it does not inject into the column at all: it sets
`coref_mentions = role_mentions`, i.e. ONE stream carrying the content-noun referents AND the discovered
pronouns together, plus `coref.ACCUSATIVE_MARKED` as the marked case cue.** Its published numbers on its own
40-document UD-EWT sample are agent 0.1896 -> 0.7536 with patient and state deltas **exactly 0.0000**, and no
non-pronoun regression. My prototype and their organ therefore agree on the pronoun half (0.9726 vs 0.9194
pronoun-agent accuracy on different samples) and differ exactly where the candidate-set composition differs.

> ⚠️ **THE CONFIRMING RUN THE PHASE-7 REQUEST ASKED FOR WAS NOT PERFORMED, BECAUSE THE TOOL CALL WAS DENIED.**
> Building a private patched copy of pri 125's three `hdlab` files (to run MY agent row through their modules)
> was refused: *"Permission to use Bash with command ... `git apply` ... `patch -p1` ... has been denied."* Per
> the standing rule I did not retry it or achieve it another way, so **there is no measurement of my rows
> through pri 125's code in this submission**. The mechanism above is instead established from MY OWN arms
> (the candidate-composition count) plus THEIR published numbers, which is sufficient to name the mechanism
> and insufficient to claim the combined figure -- and I do not claim it.

## 8c. PHASE 7 (b) -- THE PATIENT ROW'S 0.13 IS INSIDE `read()`, NOT IN THE PARSE

Three arms, the SAME 401 gold patient items over 600 UD-EWT test sentences, chunk-paired bootstrap 2,000:

| arm | what it is | acc |
|---|---|---|
| **R** | the reader's own read -- `sm.events[].patient` through `read()` | **0.6808** |
| **O** | the SAME landed organ (`predicate_argument_frontend.structural_patient_pick`) called directly on the **reader's OWN** tags and parse heads | **0.7980** |
| **B** | the same organ on the **frontend** tagger + frontend parser (the rebuilt board arm's route) | **0.8030** |

| contrast | delta | CI | separated? |
|---|---|---|---|
| **the READ layer** (O - R): read()'s event/candidate layer | **+0.1172** | [+0.0784,+0.1566] | ✅ |
| **the TAGS+HEADS layer** (B - O): the reader's categories and parse vs the frontend's | +0.0050 | [-0.0047,+0.0150] | ❌ |
| total (B - R) | +0.1222 | [+0.0839,+0.1622] | ✅ |

Cross-tabulation (upper case = correct): `rOB` **63** items the organ gets right on BOTH parses and the read
gets wrong; `Rob` **15** the read gets right and the organ wrong; `ROB` 256 all three right; `rob` 63 all three
wrong. Net −48 of 401 = −0.120, all of it attributable to the read layer.

**So the answer to "which rung loses the 0.13" is: neither the loader's organ layer nor the heads rung -- the
reader's own tagger and parser are worth +0.005 (not separated) against the frontend's. The loss is the
event/candidate layer inside `read()`** (`_read_events_wired`'s nominal candidate list, the `verb_subcat`
gate, `np_head_reduce`, and the joint-nominal-event pass), which re-derives the patient from its own candidate
set instead of taking the organ's pick. That is a specific, bounded `hdlab` item: **call the landed organ on
the reader's own parse and keep its answer.**

## 8d. PHASE 7 (c) -- WHY STATE AND WiC SURVIVE THE LIVE READ AND AGENT/COREF/COMMON-NOUN DO NOT

| row | what the answer needs | does the rebuilt path hand it something the reader does not make for itself? |
|---|---|---|
| **state** 0.7937 vs rebuilt 0.7910 (Δ 0.0027) | a SENTENCE-LEVEL relation: which token is the copular subject and which the complement, from tokens + categories + heads | **No.** `copular_binding.robust_cop` reads only `(toks, upos, heads)`. The reader makes all three itself, so there is nothing to lose |
| **wic** 0.7583 vs rebuilt 0.7493 (Δ +0.0090, and −0.0250 against the rebuilt call on the SAME 120 items) | a LEXICAL decision: a lemma plus a bag of context words | **Almost nothing.** The read-bound closure supplies the passage's own context and lets the organ enumerate candidates from the lemma; the rebuilt arm hands in a pre-built candidate list and a target-removed context. Worth −0.0250 |
| **patient** 0.6869 vs 0.8143 | a SENTENCE-LEVEL relation, but read through `read()`'s own event/candidate layer | **No** -- and §8c shows the loss is that extra layer, not the inputs |
| **agent** 0.1510 vs 0.8552 | a DISCOURSE-LEVEL object: a set of tracked referents to compete over | **YES -- the mention stream.** The rebuilt arm builds its own candidate nominals from the sentence; the reader's competition reads `_coref_mentions`, which is empty on text |
| **coref** n=0 vs 0.4217 | a DISCOURSE-LEVEL object twice over: the referring expressions AND the accessibility relation between them | **YES -- the mention spans AND the cluster ids.** Both come from the column |
| **common-noun** 0.5156 vs 0.5383 | a DISCOURSE-LEVEL object, but one the reader already builds from text | **No** -- and the row is annotation-INVARIANT (one item of 898), which is why it is promotable today |

**The generalisation, stated once: a row whose answer is a SENTENCE-LEVEL structural relation survives the
live read; a row whose answer is a DISCOURSE-LEVEL object breaks, and it breaks by exactly as much as the
mention stream it was handed.** That is not a fact about scoring, it is the Kamp/Heim point -- introducing the
discourse referent is the half of comprehension the reader is currently not being asked to do.

## 8e. PHASE 7 (a-c) -- THE NEW HEADLINE, WITH ITS CAP

The board diff makes `aggregate_19c_free` the reader's own read of the raw text. From the rows measured in
this submission (**GUM 40 whole documents, the FULL UD-EWT test split, 120 WiC pairs** -- the caps travel on
every row and on the aggregate):

| aggregate (cross-population summary, informational; the per-row numbers are load-bearing) | n | model | floor | twin | CI-sep rows |
|---|---|---|---|---|---|
| **HEADLINE -- the reader's own read of the raw text** | 4,115 | **0.4717** | 0.6868 | 0.2513 | 3 of 6 |
| the reader, mentions supplied | 4,496 | 0.4740 | 0.6904 | 0.2596 | 4 of 7 |
| the reader + its own pronouns (my prototype) | 4,115 | **0.6656** | 0.6868 | 0.2474 | 3 of 6 |
| COMPONENT -- every row rebuilt from the annotated file (the previous headline, kept in full) | 11,291 | 0.6200 | 0.5266 | 0.4240 | 5 of 7 |
| *PROJECTION with pri 125's landed agent value substituted* | *4,115* | *0.6802* | *0.6868* | -- | -- |

**The projection is arithmetic, not a measurement**: it substitutes pri 125's published agent accuracy
(0.7536, measured on their own 211-item 40-document sample) into my 1,424-item agent row and leaves the coref
row out entirely, because I could not run their question builder here (the denial in §8b). Quote it as a
projection or not at all.

---

## 9. THE PROPOSED BOARD CHANGE -- executed before it was proposed

`board_rows_on_the_reader_patch.diff` -- **FOUR files, 414 lines, `git apply --check` CLEAN at HEAD
`29c384139`** (`+219/-10` the board, `+8/-1` `tools/substrate_health.py`, `+22/-7`
`verification/test_modern_board_landing.py`, `+7/-3` `experiments/exp_copular_subject_attachment_learned_v1.py`):

1. **`_REBUILT_PROVENANCE` + `_stamp_provenance()`**: every headline row and every `new_board_arms` row gets a
   `provenance` field -- `token_stream`, `read_by`, `case`, `annotation_supplied`, and the one phrase the scorecard
   prints (`"a rebuilt read from the annotated file"`). It never overwrites a row that brought its own.
2. **THE HEADLINE SWAP (phase 7a).** `aggregate_19c_free` is now **the reader's own read of the raw text** --
   the product number -- and the previous figure is kept IN FULL as `aggregate_component_rebuilt`, with
   `aggregate_reader_given_mentions` and `aggregate_reader_pron_discovered` beside them. Every aggregate carries
   `provenance`, `plain`, `reader_caps` and `capped`, so none of them can be quoted without its provenance and
   its cap. **No default-off switch**: the reader block runs on every full board run; if it cannot be built the
   headline falls back to the component number and SAYS SO in its own `provenance`
   (`rebuilt_component_FALLBACK`), so the fallback is never silent.
3. **`run(..., reader_driven=True)`** calls this cell and publishes `per_dimension_reader_driven` (three
   provenance columns), `aggregate_reader_driven`, `reader_driven_detail`, `reader_caps` and `rebuilt_vs_reader`.
   **Capped by WHOLE DOCUMENTS** -- `--reader-docs` on the board's own command line (default 24, `0` = the full
   split), because a full-split pass is ~2.5 h; the witness/self-test path uses a witness-sized cap so W1 stays
   a witness.
4. **BOTH aggregates enter `notes/BOARD_TREND.jsonl` from the first run** (`agg` = the reader headline,
   `agg_component` = the old number), together with `reader_caps` and `dims_reader`; **`trend_regressions`
   refuses to compare reader-driven rows measured at different caps** and reports the skip with both caps
   instead of comparing them silently.
5. **`tools/substrate_health.py`**: its `n < 10000` "capped/smoke board" heuristic would have silently dropped
   the new headline (a document-capped reader aggregate is ~4k items, not ~11k). The patch makes it believe the
   board's own `capped` flag when the board states one, and keeps the n-heuristic as the fallback for older
   dumps. **This is the consumer the headline swap would otherwise have broken, and it is in the diff.**
6. **`verification/test_modern_board_landing.py` W1**: passes a witness-sized reader cap and now asserts BOTH
   aggregates, the provenance of each, the stamp on every rebuilt row, and that `rebuilt_vs_reader` names seven
   rows. **Run for real against the patched sources: green.**
7. **`experiments/exp_copular_subject_attachment_learned_v1.py`**: its two-arm board A/B has always compared the
   REBUILT rows, so it now reads `aggregate_component_rebuilt` and passes `reader_driven=False` -- otherwise
   re-pointing the key would silently change what that landed A/B measures and make it cost ~5 hours.

**EXECUTED END TO END BEFORE PROPOSAL** (a meta-loader compiles each patched source with `__file__` set to its
real repo path and `write_metrics=False`, so no landed record is touched): **14/14 checks PASS** -- the headline
aggregate is `reader_textonly` and carries its cap; the component aggregate is still published in full; the
"mentions supplied" aggregate sits beside it; every rebuilt row is stamped `loader` and every `new_board_arms`
row too; all three provenance columns are populated and keep their own provenance; every reader GUM row
publishes its document cap; `rebuilt_vs_reader` names all seven rows; `trend_row` carries both aggregates, the
caps and 21 reader rows; **`trend_regressions` compares reader rows at a matched cap and REFUSES at a mismatched
one, with the reason** (both directions exercised); the patched `substrate_health` selector reads the `capped`
flag; and **the patched witness W1 was run for real and is green** (`HEADLINE = reader_textonly (model=0.4949),
COMPONENT rebuilt kept (model=0.6044 over 7 modern dims)`, at the witness cap).
`notes/problems/<slug>/board_rows_on_the_reader_patch.diff` onto a scratch copy of the board, load it with
`__file__` set to the real repo path, and call `run(caps={"gum":8,"ud":200,"state":200,"wic_mode":"smoke",
"reader_docs":2,"reader_ud":40,"reader_wic":6}, n_boot=300, run_new_arms=False, write_metrics=False)`.

**WHAT THE DIFF DELIBERATELY DOES NOT DO: it does not silently replace the seven rows.** Three of the seven
reader-driven rows do not clear their floors, one has zero decisions on text, and the choice of which aggregate is
the HEADLINE is a strategy/owner decision, not a solver's. The diff publishes both, stamped, so the decision can be
made on numbers.

**THE RETIREMENT BLOCK** (bar clause 3 -- a solver may not write `notes/reference_retired_claims_never_requote.md`;
strategy pastes this):

```
- **RE-LABELLED 2026-09-15 (pri 122): the modern board's AGGREGATE 0.6200 and all seven of its rows are COMPONENT
  scores measured on a REBUILT read of the annotated corpus file -- not the reader's own read.** Counted in one
  process: the six functions that produce the seven rows call `SituationReader.read` 0 times and the reader's only
  sentence source 0 times. Quote them as "<row>, with the answer key's mentions supplied", NEVER as what the reader
  understands from text. The reader's OWN numbers on the same questions (data/exp_board_rows_on_the_reader_v1/):
  who-did-what AGENT 0.1510 vs its own positional floor 0.8371 (n=1424, UD-EWT full test, annotation-free; 0 of the
  948 pronoun-headed gold agents); PATIENT 0.6869 vs 0.6303 CI-sep; STATE 0.7937 vs 0.5767 CI-sep; WiC 0.7583 vs
  0.5500 CI-sep; salience 0.2750 vs 0.1250 CI-sep (annotation supplied, n=40 docs); common-noun 0.5156 vs 0.6158
  CI-sep BELOW; pronoun coref 0.4961 vs 0.7323 CI-sep BELOW with the annotation supplied and ZERO DECISIONS without
  it. Cross-population summary, informational: 0.4717 annotation-free (n=4115, GUM 40 documents + the FULL
  UD-EWT test split + 120 WiC pairs) vs the COMPONENT 0.6200 (n=11291). With the reader's own pronouns opened
  (pri 122's prototype) 0.6656; PROJECTED 0.6802 once pri 125's landed agent value is substituted (arithmetic,
  on a different agent population -- a projection, not a measurement).
  Do NOT compare a reader-driven row with a rebuilt row without naming the provenance AND the document cap of
  both; `trend_regressions` now refuses to compare reader rows across different caps.
```

---

## 9b. THE OWNER'S PUSH SCRIPT, RUN ON WHAT PHASE 7 BUILT

**(i) How do we perform against the brain at each rung, and where exactly is signal lost?** Two rungs now carry
the whole remaining loss, each with a number: **mention introduction** (agent 0.1510 with a 0-mention candidate
set; 0 of 948 pronoun-headed gold agents) and **`read()`'s own event/candidate layer** (patient −0.1172
CI-separated against the identical organ on the identical parse). Everything else is within noise of the
rebuilt path: the reader's own categories and parse cost +0.0050 (not separated), state agrees to 0.0027, WiC's
read-time contract costs −0.0250.

**(ii) Research every wall again and PROTOTYPE past it.** Both walls are now prototyped or located, not asserted.
The mention wall: prototyped here (+0.5604), landed form pri 125's (which removes my prototype's regression by
construction — §8b). The `read()`-layer wall: located by the three-arm decomposition, and its landed form is a
one-line specification — **call the landed organ on the reader's own parse and keep its answer**, instead of
re-deriving the patient from `read()`'s own candidate list. Neither is a heuristic; both name the learned/graded
form they must become.

**(iii) Is the wiring alone sufficient to reach brain level?** No, and now I can say by how much. With the
instrument fixed and the mention rung opened (prototype), the headline goes 0.4717 → 0.6656 against a floor mean
of 0.6868 — i.e. **the wiring closes most of the visible gap and still leaves the aggregate at its own floor**.
The residual is capability, concentrated in three rows: agent (0.7114 vs a 0.8371 word-order floor — the live
route needs the hybrid override-only form the board arm already uses), pronoun coref (0.4961 vs 0.7323 —
`TARGET_PRONOUNS` admits 6 of 17 third-person forms and leaves 1,950 of 3,187 anaphors undecided), and
common-noun coref (0.5156 vs 0.6158).

**(iv) The brain never does anything frozen.** The instrument adds no table of its own. The tables the two
located rungs need an observe path for are named: the pronoun-form phi table (pri 125 composes it from tables
the substrate already holds — static today), and the Competition Model's cue validities, which are a lifetime
statistic that should be learned online from decoded outcomes rather than hand-set (the existing
`cue_validities_are_a_lifetime_statistic...` brief owns that).

**(v) Compare each rung with the state of the art on its own metric.** A supervised end-to-end coreference
system on GUM reports CoNLL-F1 in the 0.70s **including mention detection**; every row here is scored with the
mentions supplied or with the mention stream missing entirely, so those numbers are not comparable and I do not
quote them against ours. The glass-box lever that makes the comparison legitimate is the same one (ii) names:
detect mentions from text, then report detection × linking (alternate path 2).

**(vi) Audit the negatives for FALSE negatives.** Three audited this session, two of which changed a conclusion:
the WiC row's 100% abstention was my own pos-mapping bug (§N1); the salience row's 0/10 was my own
surface-overlap mapping, repaired to the board's majority-eid rule over the reader's own mention positions, after
which the row CI-separates where the rebuilt row does not; and my prototype's non-pronoun regression looked like
a cue-weighting problem and is a candidate-set composition fact (§8b). **The one negative I could NOT audit is
named: the confirming run through pri 125's modules was denied (§8b), so that check is undone.**

**(vii) Prior work on the same rung already on disk.** pri 116 (the counted zero + the board question), pri 109
(the five gold columns and the loader's organ layer), pri 121 (the first reader-driven row), and pri 125 (the
landed pronoun arm, read in full before answering phase 7). All four are reused rather than re-derived.

---

## 10. KEY REALIZATIONS

1. **The zero was already known; what was missing was the SECOND zero.** pri 116 counted sentence-source calls. I
   counted `read()` itself and got the same zero -- which closes the loophole "maybe a row reads the reader some
   other way".
2. **The provenance axis that mattered was not case, it was ANNOTATION.** I went in expecting the case flip to be
   the thing the rows could not see. The bigger fact is that four of the seven rows cannot be asked the question at
   all on raw text, because the reader's mention stream is an input.
3. **A GOLD GATE CAN HIDE INSIDE A POPULATION BUILDER.** `build_pronoun_targets` looks like a target list; it is a
   filter keyed on the treebank's cluster id. No amount of pronoun discovery opens a target while that gate stands.
   The generalizable form: *when a row reports zero decisions, check whether the POPULATION builder reads the answer
   key* -- not only whether the decision does.
4. **Recompute the floor on the reader's OWN decisions and some rows invert.** The coref row's floor goes 0.3005 ->
   0.7323 purely by moving from the board's third-person population to the reader's he/she population. A margin over
   a floor is only meaningful with the population attached.
5. **A prototype's REGRESSION is the deliverable.** The pronoun prototype's +0.56 is the headline, but the -0.26 on
   the non-pronoun slice is what turns "add pronouns" into a specification (weight them by cue validity).
6. **Check coverage before believing a zero.** The WiC row's first reading was 100% abstention and it was a
   two-character bug in my own pos mapping.
7. **WHEN A PROTOTYPE REGRESSES, COUNT THE CANDIDATE SET BEFORE BLAMING THE WEIGHTS.** My pronoun injection cost
   0.26 on the non-pronoun agents and it read like a cue-weighting failure. It was a composition fact: the
   candidate set the competition sees held **0 content nouns**. The generalizable move — *when a competition
   picks the wrong KIND of thing, enumerate what was in its candidate set* — is one count, and it distinguishes
   "the arithmetic is wrong" from "the right answer was never on the ballot".
8. **A HEADLINE SWAP IS A CONSUMER CHANGE.** Re-pointing `aggregate_19c_free` at the reader would have silently
   blanked `tools/substrate_health` (its `n < 10000` "capped board" heuristic drops a document-capped aggregate)
   and silently changed what a landed two-arm A/B cell measures. Both are in the diff. *A key whose meaning
   changes is a signature change, and the completeness rule applies to it.*

---

## 11. EVERY COMPONENT I INTERACTED WITH OR CREATED, AND ITS BRAIN-FOUNDATIONAL STATUS

| component | what it did here | BF status |
|---|---|---|
| `experiments/exp_board_rows_on_the_reader_v1.py` (NEW) | the reader-driven seven rows, three provenance columns, the counted witness, the 28-arm static provenance table, the landings A/B, the pronoun prototype | **AN INSTRUMENT, NOT AN ORGAN** -- the BF gate applies to the mechanism under test. Its own discipline: the answer is `sm`, floors in place, a twin per row, cluster-paired CIs, modern gold, provenance on every row |
| `hdlab.situation_reader.SituationReader.read` | the thing finally being scored; one call per document shared by every row on that document | BF_SPIRIT (one in-order pass, 25 consumers; Heim/DRT cards, Zwaan-Radvansky indexing) -- **its INPUT CONTRACT is the defect** |
| `hdlab.scene_segment.parse_conll_sentences` | the reader's one sentence source, cased since pri 116 | BF (word-form route hands down an abstract letter identity AND the surface shape; Cohen & Dehaene 2002). Counted: 0 calls from any headline row |
| `hdlab.referent_per_np.referent_per_np_source` | content-head NP referents from text **+ pronouns lifted from the coref column** | **NOT_BF on the pronoun half** (pri 125's rung) |
| `hdlab.situation_reader._cm_agent_candidates` | the Competition-Model AGENT candidate set = `self._coref_mentions` | **NOT_BF as wired** -- PINNED computation, externally supplied candidate set; `(None, None)` on text |
| `hdlab.coref.build_pronoun_targets` + `state_of_mind.TARGET_PRONOUNS` | the anaphora population: he/she family AND a shared GOLD cluster id | **NOT_BF (new finding)** -- the population is gated on the answer key, and 1,950 of 3,187 third-person anaphors are never decided |
| `hdlab.entity_resolver.resolve_commonnouns` (via `sm.commonnoun_resolution`) | the common-noun row's model answer | BF_SPIRIT (same-head recency + non-writing ACT-R bridge; Nieuwland) -- **annotation-invariant, promotable today** |
| `hdlab.copular_binding` / `sm.entity_states` | the state row's model answer | BF_SPIRIT (Kimian states; Bemis & Pylkkanen LATL) -- **survives the live read intact** |
| `hdlab.underspecified_sense_reader` via `sm.select_sense` | the WiC row's model answer, through the closure the read installs | BF_SPIRIT (Frisson; Rodd) -- read-time contract costs -0.0250 |
| `hdlab.lexical_categories` (`PREDICATE_SLOT`) / `nonverbal_predication` | the two landing switches A/B'd here | BF_SPIRIT; pri 117 now CI-sep VISIBLE on a reader-driven row |
| `experiments/gum_coref.py`, `exp_whodidwhat_ud_structural_v1.load_ud`, `exp_copular_is_a_binding_readout_v1.typed_gold`, `tools/load_wsd_benchmarks.load_wic` | ANSWER KEYS only | admissible: static offline MODERN golds |
| `experiments/exp_crosstype_gum_conll_fullread_v1.gum_to_conll` | GUM -> the reader's native CoNLL (round-trip gated) | admissible (a format converter) |
| `hdlab.predicate_argument_frontend.structural_patient_pick` | the PATIENT organ, called directly in the phase-7 attribution on the reader's own parse and on the frontend's | BF_SPIRIT and **NOT the loss**: 0.7980 on the reader's own parse vs 0.8030 on the frontend's (+0.0050, not separated) -- the 0.13 is `read()`'s event/candidate layer around it |
| `hdlab.situation_reader._read_events_wired` (the event/candidate layer) | located as the patient row's losing rung | **NOT_BF as wired (new finding)**: it re-derives the patient from its own candidate list instead of keeping the landed organ's pick on the same parse -- worth −0.1172 CI[−0.1566,−0.0784] |
| `tools/substrate_health.py`, `verification/test_modern_board_landing.py`, `experiments/exp_copular_subject_attachment_learned_v1.py` | PROPOSED changes only -- the three consumers the headline swap would otherwise have broken silently | instrument plumbing; each is in the diff and was executed |
| `experiments/exp_situation_model_qa_modern_v1.py` | PROPOSED change only (provenance + the headline swap + the reader-driven block + both aggregates in the trend + the matched-cap regression rule) | the board is an instrument; the change makes it SAY what it measured and LEAD with the reader it runs |

**AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`), three entries:**
1. **`hdlab.coref.build_pronoun_targets` -> NOT_BF (new).** The anaphora POPULATION is admitted only on a shared
   treebank cluster id. Counted: 381 targets with the coref column on 40 GUM documents, 0 without it even when the
   pronouns are discovered from text.
2. **`situation_reader._cm_agent_candidates` -> NOT_BF as wired (sharpen the existing entry).** The candidate set is
   the coref-column mention stream; on annotation-free text the Competition Model does not run at all, and the agent
   row reads 0.1510 against its own 0.8371 positional floor (n=1,424, UD-EWT full test).
3. **The modern board (`exp_situation_model_qa_modern_v1`) -> the seven headline rows are COMPONENT instruments.**
   0 `read()` calls and 0 sentence-source calls, counted in one process; 28 arms, 9 statically able to reach the
   reader, 0 of them headline producers.
4. **`situation_reader._read_events_wired`'s event/candidate layer -> NOT_BF as wired (new).** On 401 UD-EWT
   patient items the landed organ scores 0.7980 on the reader's OWN parse and the reader's read of the same
   sentences scores 0.6808: the layer around the organ costs −0.1172 CI[−0.1566,−0.0784] CI-separated, while the
   reader's categories+parse cost +0.0050 (not separated). The organ's pick should survive the read.

---

## 12. WHY THE BIG ONE WON -- the chain, rung by rung, and the rungs NOT cracked

The thing cracked here is not an organ, it is **the definition of the question**: stop scoring the answer the
instrument can most cheaply recompute, and score the answer the reader actually produced. Every number above comes
out of `sm`.

| rung | already the brain's? | what this session did |
|---|---|---|
| **the question** ("what did the reader understand?") | ❌ the board asked "what can be recomputed from the annotated file?" | **CRACKED** -- the row reads `sm` and nothing else, and says so on its face |
| **the percept** (the sentence source) | ✅ cased since pri 116 | reached by a board-shaped row for the first time (the rebuilt rows call it 0 times) |
| **mention detection** | ❌ an INPUT, not a product of the read | **NOT cracked -- LOCATED with counts**, prototyped (+0.5604), and handed to pri 125 with its acceptance test |
| **the anaphora population** | ❌ gated on the gold cluster id | **NOT cracked -- FOUND.** A new `hdlab` item, not previously filed |
| **the AGENT candidate set** | ❌ supplied from the annotation column | **NOT cracked** -- 0 of 948 pronoun agents, counted |
| **role assignment given candidates** | ✅ PINNED Competition Model | inherits the candidate set; the live route needs the hybrid word-order default (N5) |
| **copular state binding** | ✅ BF_SPIRIT | **survives the live read** (0.7937 vs the rebuilt 0.7910) -- the proof the instrument is not pessimistic |
| **the sense commit** | ✅ BF_SPIRIT | **survives** (0.7583, coverage 1.000, contract cost -0.0250) |
| **the provenance of a number** | ❌ absent | **CRACKED** -- every arm on the board now says what it read, in the owner's words |

---

## 13. WHAT WOULD TAKE THIS TO A FULL PASS

| bar clause | state | what is missing |
|---|---|---|
| all seven rows scored from the live reader's output, one read per document | **MET**, with two numbered exceptions (section 5) | -- |
| provenance fields published | **MET** -- three columns per row, plus the static table for all 28 board arms | -- |
| the old rebuilt numbers retired with the new honest baseline | **BLOCKED BY REMIT** -- a solver may not write `notes/reference_retired_claims_never_requote.md` | strategy pastes the block in section 9 |
| the three landings' effects visible | **1 of 3 VISIBLE CI-sep (pri 117), 1 visible-in-kind but underpowered (pri 116), 1 exact zero with an arithmetic reason (pri 113)** | pri 116 needs the landings A/B at the full document cap (~4 h at 4 arms); I ran 8 documents + 200 sentences |
| reader-driven rows clearing their floors | **4 of 7** (salience, patient, state, wic) | agent, coref and common-noun do not -- **that is the TRUE live number**, and the repair is in the reader (sections 5, 6, 8) |
| the headline is the reader the owner runs | **MET (phase 7)** -- `aggregate_19c_free` = the reader's own read of the raw text, 0.4717 (n=4,115), the component number kept in full at 0.6200, both in the trend file, every reader row carrying its document cap | -- |
| the two remaining gaps attributed to a rung each | **MET (phase 7)** -- agent = the candidate set (counted: 0 content nouns); patient = `read()`'s event/candidate layer (+0.1172 CI-sep, the parse exonerated at +0.0050 n.s.) | -- |
| the confirming run through pri 125's modules | **NOT DONE -- THE TOOL CALL WAS DENIED** (§8b, verbatim) | strategy can run it in one command after pri 125 lands: `--ud --ud-cap 0` on this cell |

**Chased here, within remit:** the pronoun prototype (built, +0.5604 CI-sep, with its regression quantified); the
salience mapping repaired to the board's own majority-eid rule over the reader's own mention positions (which is
what made that row separate); the span-credit bound on the instrument's own string matching; the WiC coverage bug;
the landings A/B. **Handed on with numbers:** the two gold gates, the hybrid agent route, and the full-cap pri 116
A/B.

---

## 14. PRIORITY NEXT STEPS (for strategy)

1. **Apply the diff and publish BOTH boards, every row stamped.** Nothing is replaced; the rebuilt rows keep their
   numbers and gain the phrase "a rebuilt read from the annotated file".
2. **Paste the retirement block** (section 9) so `0.6200` stops travelling as the reader's comprehension.
3. **Open an `hdlab` item for `build_pronoun_targets`' gold gate** -- it is NOT covered by pri 125 and it alone
   keeps the coref row at zero decisions on text. One-line shape: admit every third-person pronoun as a target and
   let "no antecedent found" be an answer.
4. **Land pri 125 and re-run `--ud --ud-cap 0`.** The prototype's +0.5604 with a -0.2605 non-pronoun cost is the
   acceptance test.
5. **Align the live agent route with the board's hybrid** (word-order default + marked-cue override). On the
   reader-driven row that is the largest remaining gap (0.7114 against a 0.8371 floor).
6. **Widen `TARGET_PRONOUNS`** -- 1,950 of 3,187 third-person anaphors on GUM test are never decided.
7. **Add a `mention_detection` row in front of the four affected rows**, so "the reader has no pronouns" is a
   number on its own row instead of a population artifact.
8. **KEEP THE LANDED PATIENT ORGAN'S PICK THROUGH `read()`** -- the single largest bounded reader-driven gain
   located here: +0.1172 CI[+0.0784,+0.1566] on the patient row, with the parse and the categories already
   exonerated. It is an `hdlab` change inside `_read_events_wired`, so it is filed, not built.
9. **RUN THIS CELL'S `--ud --ud-cap 0` AND `--gum --docs 40` ONCE pri 125 LANDS** -- that is the confirming
   measurement the denial prevented here, and it is one command each.

---

## 15. ALTERNATE PATHS -- other ways to do this read, similarly or MORE brain-foundational

1. **🥇 MAKE `read()`'s INPUT A TOKEN STREAM AND DELETE THE MENTION COLUMN FROM ITS CONTRACT.** More
   brain-foundational than anything shipped here: the comprehender receives words. Then there is ONE provenance
   column and the question "did we supply the answer?" cannot arise. *What it takes:* an `hdlab` signature change
   across every consumer and witness that passes a CoNLL path, after pri 125 and the `build_pronoun_targets` fix.
   *Why not now:* it is squarely a substrate change and my remit is the instrument.
2. **🥈 DECOMPOSE EVERY ENTITY ROW INTO DETECTION x LINKING.** A coreference score is detection x linking
   (CoNLL-2012's own lesson). A `mention_detection` row (the reader's referents against the gold spans, P/R/F1 on
   the reader's own positions) in front of linking-on-the-detected-subpopulation removes the cross-arm population
   comparison that pri 109 caught itself in and that reappears in section 7's common-noun contrast.
3. **🥉 ONE READ PER DOCUMENT FOR THE WHOLE BOARD.** A comprehender builds one situation model and answers many
   questions from it (Zwaan & Radvansky 1998). This cell does that within a corpus; a board that did it globally
   would cost one read per document instead of one per arm and would force every row onto one provenance by
   construction.
4. **A HUMAN-COMPETENCE ANSWER KEY INSTEAD OF A TREEBANK COLUMN.** QA-SRL for who-did-what, ARRAU/PDP for anaphora:
   these measure the ability rather than the annotation manual. *What it takes:* acquisition plus a fresh floor per
   gold; a separate brief.
5. **KEEP TWO BOARDS DELIBERATELY** (the weakest, recorded because it is the default if nobody acts): a COMPONENT
   board and a PRODUCT board. Honest only if both are always published together with provenance -- which is what
   the diff enforces.

---

## 16. GAPS -- steps not performed, and not worked around

1. **The GUM reader-driven rows are capped at 40 of 128 test documents** (evenly spaced, 41,485 of 127,919 tokens),
   because a full-split pass in three provenance columns is ~3.3 h. The UD-EWT rows are the FULL test split.
2. **The landings A/B is capped at 8 GUM documents + 200 UD sentences** (4 arms x 2 corpora). pri 117's win
   separates at that cap; pri 116's moves do not, and I say so rather than quoting them as effects.
3. **The rebuilt reference is the board's own last published full run**, not a re-run inside this cell. The capped
   rebuilt run I did make (`rebuilt_cap.json`, 40 GUM documents / 600 UD sentences) exists for the COUNTED WITNESS
   and the schema check only; its GUM rows sit on a genre-prefix subsample (the board arm's own `limit=` semantics)
   and are NOT comparable to the reader-driven rows.
4. **No `metrics.json` was written for this cell.** The five component artifacts are the landed records; the board's
   patched arm calls `run(..., write_metrics=False)`, so the canonical artifact is not required and nothing of the
   board's was at risk of being re-dated.
5. **I did not touch `notes/reference_retired_claims_never_requote.md`, `notes/STATUS.md`, the plan, or any other
   problem folder.**
6. **THE PHASE-7 CONFIRMING RUN THROUGH pri 125's PATCHED MODULES WAS NOT PERFORMED: THE TOOL CALL WAS DENIED**
   (the text is quoted verbatim in §8b). Per the standing rule I did not retry it and did not achieve it by
   another route, so this submission contains **no measurement of my rows through pri 125's code**, and the
   combined figure in §8e is labelled a PROJECTION wherever it appears. The same denial blocks the phase-7
   request to measure the coref row text-only with `discovered_pronoun_targets` loaded. **What I did instead,
   inside my own remit:** my cell's pronoun-question builder is now forward-compatible
   (`_reader_pronoun_targets` prefers `coref.discovered_pronoun_targets` when the substrate has it and falls
   back to `build_pronoun_targets`), so the coref row starts reporting a population the moment pri 125 lands,
   with no edit here — and the 15-check self-test still passes.
7. **The phase-7 attribution runs are capped at 600 UD-EWT sentences** (401 patient items / 692 candidate
   mentions), not the full split, because each arm re-reads the corpus; the headline UD rows ARE the full split.

---

## SUBMISSION PROMPT

```
SOLVED (PARTIAL): none of the board's seven headline rows runs `SituationReader.read` -- each rebuilds its own copy
of the read from the annotated CoNLL-U files, so a reader repair worth +0.41 PROPN F1 is board-invisible; rebuild
the rows on the live reader.

Problem: the_boards_seven_rows_never_run_the_reader_each_rebuilds_its_own_copy_from_annotated_cased_files_so_a_reader_repair_worth_0_41_propn_f1_is_board_invisible_rebuild_the_rows_on_the_live_reader   (priority 122)

Headline: all seven rows are now scored off `sm`. Counted in one process, 0 `read()` calls and 0 sentence-source
calls while the board's own functions produced all seven rows. On the FULL UD-EWT test split, annotation-free, the
reader names the doer 0.1510 (n=1424) against its own positional floor 0.8371 -- the board's row for that question
reads 0.8552 -- and 0 of the 948 pronoun-headed gold agents are named, because the reader has no pronoun mentions
without the annotation column. Opening the pronouns the reader's OWN category organ already tags takes it to
0.7114 (+0.5604 CI[+0.5038,+0.6193], pronoun slice 0.9726) at the cost of -0.2605 on the non-pronoun slice -- the
acceptance test for pri 125's landed form. State (0.7937 vs 0.5767), patient (0.6869 vs 0.6303), WiC (0.7583 vs
0.5500) and salience (0.2750 vs 0.1250) clear their floors CI-separated on the reader; pronoun coref, common-noun
coref and agent do not. A SECOND gold gate found in hdlab: `coref.build_pronoun_targets` admits a target only on a
shared treebank cluster id, so the coref row has zero decisions on text even with the pronouns discovered. pri 117
is the first landing shown CI-separated through the live reader (patient +0.0158 CI[+0.0049,+0.0293]).

PHASE 7: the diff now makes the HEADLINE the reader own read of the raw text -- 0.4717 (n=4115, GUM 40 whole
documents + the FULL UD-EWT test split + 120 WiC pairs) against the COMPONENT number 0.6200 (n=11291), which is
kept in full; both go into BOARD_TREND from the first run, every reader row publishes its DOCUMENT cap, and
trend_regressions refuses to compare reader rows across caps. Two rungs carry the rest, each attributed by
count: the AGENT candidate set (the shipped text-only arm hands the Competition Model 0 mentions on 600 of 600
sentences; my prototype hands it 692 of which 0 are content nouns -- a composition fact, which is exactly why
pri 125 ONE-STREAM form does not pay my -0.2605 non-pronoun cost), and the PATIENT row 0.13, which is INSIDE
read(): the same landed organ scores 0.7980 on the reader OWN parse and 0.8030 on the frontend one (+0.0050
n.s.) while read() event/candidate layer costs +0.1172 CI[+0.0784,+0.1566] CI-sep.

Read notes/problems/<slug>/SOLVED.md. Deliverables: experiments/exp_board_rows_on_the_reader_v1.py (--self-test
15/15) and board_rows_on_the_reader_patch.diff (proposed; FOUR files, 414 lines, git apply --check clean; all
four patched sources EXECUTED end-to-end, 14/14, including the patched verification witness W1 run green). The
three extra files are the consumers the headline swap would otherwise have broken silently
(tools/substrate_health.py, verification/test_modern_board_landing.py, the copular A/B cell). No hdlab/ or
tools/ file was written on disk. The retirement block for notes/reference_retired_claims_never_requote.md is in
section 9 -- a solver may not write that file. ONE STEP IS UNDONE AND SAID SO: the confirming run through pri
125 patched modules was DENIED (the denial text is quoted verbatim in section 8b), so no number here is measured
through pri 125 code and the combined figure is labelled a PROJECTION.
```
