---
priority: 138
slug: the_introduction_organ_opens_one_referent_per_content_noun_token_with_a_bare_head_span_and_no_global_index_rebuild_it_as_one_referent_per_np_with_the_attachment_arms_span_and_real_token_positions
status: OPEN
review:
review_text:
---

# PROBLEM: the introduction organ (`hdlab/referent_per_np.py`) opens one discourse referent per content-noun TOKEN, stores the bare head as the mention's span, and writes no global token position. So 'the old baker' is three referents, no mention has a readable determiner, and every consumer that needs a position abstains. Rebuild it as ONE referent per noun phrase (the attachment arm's head plus its pre-head dependents, determiner included, post-modifiers excluded) with real token positions. Measured worth on its own: entity partition +0.0621 CI-separated on 28 modern documents, with no other change.

**slug:** `the_introduction_organ_opens_one_referent_per_content_noun_token_with_a_bare_head_span_and_no_global_index_rebuild_it_as_one_referent_per_np_with_the_attachment_arms_span_and_real_token_positions`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A noun phrase is ONE object file (Kahneman, Treisman & Gibbs 1992): the reader opens one discourse referent per NP (Heim 1982's file card; Karttunen 1976's discourse referent), not per noun; the phrase's boundary comes from the parse (the head and what depends on it before it), and the determiner is read ON that card (Heim's Novelty-Familiarity Condition). The mention's POSITION in the discourse is part of the card (where it was said; recency and distance cues need it).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy, GLUCOSE, MAVEN and ANY off-the-shelf parser/dataset/model are NOT brain-foundational; an external tool AT INFERENCE is a DEFECT THAT BLOCKS. The NP boundary comes from the reader's OWN attachment arm (`hdlab/attachment_arm.py`); no chunker trained elsewhere, no fitted boundary table.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS (owner 2026-09-11):** the introduction organ is `referent_per_np`; the pronoun arm (pri 125) and the nominal arm are its two arms and hand ONE stream to every consumer (the agent competition, anaphora, entities, space, the crosstype bridge, the common-noun binder). Do not build a second mention stream anywhere.
> **DOWNSTREAM REGRESSION AFTER A BF UPSTREAM IS NOT FAILURE:** fewer, larger mentions change every consumer's population; name each flip and repair the consumer (never keep the per-token stream for a consumer that liked it).
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED** (with your diff applied), not on the tree you started from.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Reproduce pri 136's measurement first-hand: `experiments/exp_object_file_competition_v1.py --npspan 28` (its NP-span arm is a prototype INSIDE the cell, not shipped). Then check whether pri 134's phase 7 has already shipped `referent_per_np_span_patch.diff` in its folder (`notes/problems/the_fine_non_argument_relations_*/`): if it has, START FROM IT (apply, measure, extend) rather than rebuilding.
> 2. **REUSE.** `hdlab/referent_per_np.py` (`_content_head_positions` :111-115 -- one referent per token; `_mk_referent` :192 `gtok_start = -1`, :194 `span_toks = [head]`; the pronoun arm :107), `hdlab/attachment_arm.py` (heads and dependents of the reader's own parse; `predicate_sites`), `hdlab/coref.py` (`span_caps_symbol`, the readers of `gtok_start` at :452), `hdlab/situation_reader.py` (:260 reads `gtok_start`; the mention hand-offs at :4939 and :4994), `hdlab/crosstype_live_adapter.py` (`_can_build` rejects `gtok_start = -1`), `hdlab/entity_resolver.py` (Heim's criterion shift since pri 136 reads the determiner), the common-noun binder's modifier-split cue.
> 3. **GENERALIZE.** Every consumer reads the ONE new stream: enumerate the readers of `span_toks`, `gtok_start`, `gtok_end`, `wtok_start` on disk (grep, count) and measure each before/after.
> 4. **WALL -> DEEPER.** Where the arm's parse gives the wrong boundary (a post-head modifier swallowed, a compound split), the fix is a cue on the attachment arm (pri 134's name-run cue; the compound relation), not a boundary heuristic here.
> 5. **OPTIMIZE BY EXACT REPLICATION;** nothing to sweep: the boundary is the parse; the Right-Hand Head Rule (Williams 1981) picks the head.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Mention count, determiner readability, same-gold-mention cross-file pairs, B-cubed, the pronoun row (both scorers), the bridge's docs-reaching-the-detector, the raw-text agents row -- all on the 28 GUM test docs through the FULL live read.
> 7. **ADJACENT.** pri 136 (the object-file competition; lands first), pri 134 (fine relations; the bridge's other gate), pri 131 (the pick's contract), pri 132 (the analysis object: sentence/entity ids), LOCATED item 11 (the space hand-off's movers).
> 8. **COMPLETION BAR.** Below.

**(PHASE DIAGRAM.)** No fitted parameter in this rung. If a graded boundary is needed (a dependent attached with low confidence), read the attachment arm's graded head belief rather than thresholding it here.

## 1. THE PROBLEM IN PLAIN LANGUAGE

When the reader meets 'the old baker', it should open ONE file for one person. Today it opens three: one for 'old' is not opened (not a noun) but 'baker' gets a file whose whole content is the word 'baker' -- and for 'the New York Times' it opens a file per noun. The file does not record the word 'the' (so the reader cannot tell a first mention from a repeat), and it does not record WHERE in the text the mention was (so every step that needs a position gives up silently: the name-linking bridge, the distance cues). Two solvers found this from two sides on the same day: the clustering solver measured that just fixing the span, with nothing else changed, lifts how well the reader groups mentions into people and things by six points in a hundred, clearly separated; the relations solver found the missing position is why its link-finding step had never run on real text.

## 2. WHY THIS ONE

It sits at the top of the entity chain (the introduction organ hands the stream to every entity consumer), and it is measured: +0.0621 CI[+0.0481,+0.0770] B-cubed on its own, stacking with pri 136's competition to +0.0845; the determiner becomes readable on 46% of mentions (from 0%), same-gold-mention cross-file pairs fall 46%, and it is the precondition for the crosstype bridge (pri 134) and the common-noun binder's modifier cue. A located root cause becomes a brief the same day (LOCATED item 14 in `notes/STATUS.md`).

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)

PINNED (computational level): one object file per perceived object (Kahneman, Treisman & Gibbs 1992); one discourse referent per NP (Karttunen 1976; Heim 1982); the determiner is read on the card (Heim's condition); the head of an English compound/nominal is its rightmost member (Williams 1981). OUR-INVENTION: using the attachment arm's arcs to delimit the phrase (pre-head dependents join; post-head dependents do not); the representation of the position (global token index). The boundary decision reads the arm's graded head belief where it is uncertain.

## 4. MEASURED vs INFERRED

MEASURED (pri 136 phase 7, 28 GUM test docs, 795 pronoun questions, `exp_object_file_competition_v1.py --npspan 28`): shipped 7,168 mentions, determiner readable 0/7,168, bridge binds 3, same-gold-span cross-file pairs 3,431, B-cubed 0.5532 (P 0.780 / R 0.428), pronoun span row 0.3283. Shipped + NP span: 5,625 mentions, determiner readable 2,584, binds 5, pairs 1,853, B-cubed 0.6152 (0.783 / 0.507) = +0.0621 CI[+0.0481,+0.0770]; pronoun span row 0.3094 (-0.0189 CI[-0.0602,+0.0190], not separated). Competition + NP span: 0.6377 (0.854 / 0.509). MEASURED (pri 134): `_can_build` rejects 292/292 mentions on a raw-text read because `gtok_start = -1`; 0/6 docs reach the predication detector. The lines: `referent_per_np.py:111-115`, `:192`, `:194`, `:107`.

INFERRED (verify): that the pronoun row moves once the span and the readout agree (pri 136's identity scorer says the pick is up +0.0780 by entity; the span row reports the token); that the space hand-off's mover defect (LOCATED item 11) shares this cause (gendered common nouns as movers may be a per-token-mention artefact).

## 4b. THE STARTING DIFF EXISTS (pri 134 phase 7, 2026-09-16 01:36)

`notes/problems/the_fine_non_argument_relations_*/referent_per_np_span_patch.diff` (that file only) is measured on 6 GUM docs through the real reader: `_can_build` 0 -> 6 docs, global index in range 0 -> 1,846, definiteness 580 definite + 204 indefinite (42.5% of mentions get a determiner for the first time), modifiers 0 -> 708, extent 0 -> 1,234, name-typed 312 -> 320, the mention COUNT identical (2,010 / 1,846: it completes mentions, adds none); pri 131's pronoun row span-scored 0.3182 -> 0.3523 (floor 0.2443 unchanged; the info-free twin also rose +0.0568, so part is instrument). It was NOT landed by strategy because it changes the POSITION CONTRACT: `coref.parse_litbank_conll` puts `wtok_start` at the SPAN START with the head last, while `referent_per_np` put it at the HEAD with a one-token span -- every extent consumer was accidentally right only while the span was degenerate. The diff ships `mention_head_wpos()` and repairs a MASKED defect (`graded_role_assigner:2069` / `:2154` read `wtok_start` as the head index -- wrong on every multi-token gold mention since written). YOUR JOB is therefore: apply it on the landed tree (after pri 134 + 136 land), enumerate EVERY consumer of `wtok_start` / `span_toks` / `gtok_*` (pri 136's Heim read of the token BEFORE `wtok_start` in `entity_resolver.py`; coref's `ent_at_pos` keyed by `wtok_start` and the QA alignment by position; the 7 `span_toks` organs pri 134 names; the space hand-off), decide per consumer whether it wants the head or the span start, repair each, and measure the bar below on the full 28-doc instrument.

## 5. ALREADY TRIED / DO NOT RE-RUN

- pri 136's `--npspan` prototype (the measurement above) exists inside its cell; it is not shipped and not a landed form. Reuse its boundary logic, do not re-derive the numbers.
- The `boundary_nphead` prior work (cited by pri 136): post-head dependents swallowed into the span HURT; keep post-modifiers out.
- Do not re-open the pronoun arm (pri 125) or the identity contract (pri 131); the pronoun referent's span (:107) becomes the pronoun token with a real position, nothing more.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

1. `sed -n 100,200p hdlab/referent_per_np.py` -- confirm the three lines (per-token positions, `gtok_start = -1`, `span_toks = [head]`); line numbers drift.
2. `ls notes/problems/the_fine_non_argument_relations_*/` -- if `referent_per_np_span_patch.diff` exists (pri 134 phase 7), read its SOLVED.md section on it and start from that diff.
3. `grep -rn "gtok_start\|span_toks\|wtok_start" hdlab/ | wc -l` -- your consumer enumeration (expect dozens).
4. Run `experiments/exp_object_file_competition_v1.py --npspan 28` once to reproduce the table (one cell at a time; the product board may be running).
5. Confirm pri 136's diff state: if `object_file_competition_patch.diff` has landed (look for `HDLAB_OBJECT_FILE_ONLINE` in `hdlab/entity_resolver.py`), measure on the landed competition as well as on the old clustering.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)

1. **One referent per NP with real positions, from the reader's own parse.** `span_toks` is the phrase (determiner in, post-modifiers out), `gtok_start/gtok_end` are true global indices, for the nominal AND the pronoun arm; no chunker, no fitted table.
2. **Entity partition up CI-separated** on the 28 GUM test documents (B-cubed over the reader's files, all mentions counted) against the shipped per-token stream, with the OLD clustering and with pri 136's competition if landed; report P and R. The floor is the shipped stream; the twin is a RANDOM-BOUNDARY stream (each mention's left boundary drawn at random within the same sentence, the same mention count) and it must lose CI-separated.
3. **The three joins move:** determiner readable fraction (report; expect ~46%), same-gold-mention cross-file pairs (report; expect ~-46%), and the crosstype bridge's `_can_build` accepting the reader's mentions (docs reaching the detector 6/6 on pri 134's probe).
4. **The pronoun row, both scorers** (span and identity, pri 136's instrument): reported with CI; not down CI-separated on either.
5. **Every consumer of the stream enumerated and measured** before/after on the reader-driven rows (raw-text agents, common noun, state, space where-is) -- a flip is named and repaired downstream, never by keeping the per-token stream for that consumer.
6. **Witness**: a landing witness that pins the CLAIMS (one mention per NP on a fixture; positions valid; determiner readable) and the pri 125 source witness (`test_referent_per_np_source_landing_organ`) re-pinned to the NP population if its counts move.

## 8. FILES AND ENTRY POINTS

- `hdlab/referent_per_np.py` -- the organ: `_content_head_positions` (:111-115), `_mk_referent` (:192, :194), the pronoun referent (:107), `discovered_pronoun_targets` consumers.
- `hdlab/attachment_arm.py` -- heads and dependents; graded head belief.
- `hdlab/crosstype_live_adapter.py` -- `_can_build` (the `gtok_start` gate); `hdlab/coref.py:452`, `hdlab/situation_reader.py:260` -- other `gtok_start` readers.
- `hdlab/entity_resolver.py` -- Heim's criterion (reads the determiner since pri 136); `hdlab/commonnoun_binder.py` -- the modifier-split cue.
- `hdlab/crosstype_bridge.py:55` (`_ART`) -- the bridge's definiteness test reads the FIRST TOKEN of the mention text; with the bare-head span every definite fails it, so the bridge licensed 0 binds even with the global index repaired (pri 136 measured: indices alone 0 binds; indices + determiner 1 bind on 28 docs, the residual being pri 134's relations). Your span must make that read true for 'the baker'; measure the bridge's binds before/after.
- `experiments/exp_object_file_competition_v1.py` (`--npspan`) -- the prototype and the instrument; `experiments/exp_pronoun_pick_identity_contract_v1.py` -- the pronoun instrument; `experiments/exp_board_rows_on_the_reader_v1.py` -- the reader-driven rows.

Also known: the bridge's precise-constructs sieve scores HIGHER with the retired perceptron's labels than with gold deprels (pri 134 E) -- it may be shaped to perceptron-style labels; report it if your binds are capped by it, do not tune the sieve here.

Write ONLY: `experiments/exp_np_span_introduction_v1.py` (NEW cell; `get_output_dir` per Q115; `--self-test`), `verification/test_referent_per_np_span_landing.py` (NEW witness), `notes/problems/<slug>/{SOLVED.md, np_span_patch.diff}` (unified diffs against `hdlab/referent_per_np.py` and any consumer you repair; never edit hdlab/ or tracked verification files directly). Cap cores: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time.

## DO NOT QUOTE / DO NOT REDO

- Do not quote '+0.1168' for the clustering oracle (retired 2026-09-16; it is +0.0390).
- Do not quote the bridge's '+0.0838' (retired 2026-09-16; never a raw-text number).
- Do not re-measure the per-token stream's numbers above; reproduce once, then build.
- 19c corpora are informational only (owner 2026-09-06); grade on the 28 GUM test documents and the reader-driven rows.

## 9. EVIDENCE ADDED AT THE pri 136 LANDING (strategy, 2026-09-16 11:05) -- YOUR FIRST ACCEPTANCE BAR

With pri 136 landed (the object-file competition, tau=0, the flat adjacency cue `np` = gap1_nom/gap2_nom, learned on ONE-TOKEN mentions: gap1_nom counts 490 same-file vs 16 different), two measurements show the missing spans as the live defect: (a) the board's NEW entity-set row (GUM test, 24 docs, n=874 non-pronoun re-mentions): the reader's own partition 0.5046 vs SAME-HEAD-STRING IDENTITY 0.738, -0.2334 CI[-0.3248,-0.1553] BELOW the simplest rule (B-cubed F1 0.6401 vs 0.8451); (b) the inferred-emotion board arm (occ_appraisal, 50 constructed modern items, two sentences each): 0.90 on 22 consecutive boards -> 0.64 with the competition ON (0.90 with HDLAB_OBJECT_FILE_COMPETITION=0, same process, 13 items flip to 'no goal found'), MECHANISM probed on the items: the character's file absorbs its neighbouring nominal run ('maya' + 'championship'; 'leo' + 'last','train','home','pulled'), the goal register then names the owner by the wrong head ('championship', 'pulled'), and the appraisal finds no goal for the character. The nominal-run cue is the stand-in for the NP span this brief builds; once mentions carry real spans (one referent per NP with positions) the cue's job is done by the span and its validities must be RE-ACCRUED without the NP-internal 'same' observations (pri 136's phase-7 lead: the configuration-conditioned cue set, entity_resolver.NP_VALUES v2, is already coded and unshipped). BARS ADDED: (1) the entity-set row at or above same-head-string identity (0.738) on the same 874 items, CI reported; (2) occ_appraisal back to >= 0.90 on its 50 items with the competition ON; (3) the goal register names a file by its PROPER NAME when it holds one (a file card's label is its name; today `_cluster_name` can return a common-noun head of a merged file) -- measured on the 13 flipped items. Reproduce (a) from data/exp_situation_model_qa_modern_v1_pri136a/metrics.json (per_dimension_reader_driven.reader_textonly.entity_set) and (b) with the scratch probe in the ledger row of 11:05 (two runs of experiments/exp_occ_appraisal_emotion_v1.extract_all under the switch).
