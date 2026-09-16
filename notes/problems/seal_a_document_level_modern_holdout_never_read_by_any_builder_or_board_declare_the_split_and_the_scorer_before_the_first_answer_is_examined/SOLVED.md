---
problem: seal_a_document_level_modern_holdout_never_read_by_any_builder_or_board_declare_the_split_and_the_scorer_before_the_first_answer_is_examined
status: SOLVED
bar: "A committed sealed list with hashes, a committed rule and seed dated before the draw, an enumeration proving no builder/witness/board read those ids, a fixed scorer and configuration manifest, and the per-dimension held-out table with document-level CIs -- OR a numbered reason no unread modern document exists and the proposed next corpus."
result: "SEALED AND MEASURED ONCE. The seal (manifest + draw rule + seed + per-document SHA-256 + fixed scorer + configuration manifest + overlap audit + the enumeration) was committed at 66f5b1948 BEFORE the reader was run on a single sealed document; the first held-out answers were produced by the next command. HOLDOUT_V1 = 279 documents / 719 sentences / 15,294 tokens of UD_English-PUD (pinned commit f16eba4a; modern 2016-17 newswire + Wikipedia), stratified by genre (151 news / 128 wiki), seed 20260916; RESERVE_V2 = 118 documents / 281 sentences, never read. THE PRODUCT'S OWN READ OF RAW TEXT (279 SituationReader.read calls, 15,294 tokens written, 0 non-FORM CoNLL columns populated -- counted, not asserted), abstentions counted wrong, every eligible gold question in the denominator, DOCUMENT-paired bootstrap (n_boot=2000): who_did_what_agent n=806 model 0.6328 vs floor 0.7171 (nearest pre-verbal nominal) = -0.0844 [-0.1109,-0.0596] CI-SEPARATED **BELOW ITS FLOOR**, twin 0.1402 (+0.4926 [+0.4527,+0.5328] SEP), coverage 781/806=0.969; who_did_what_patient n=788 model 0.6980 vs floor 0.5698 = +0.1282 [+0.0864,+0.1698] SEP, twin 0.1396 (+0.5584 SEP), coverage 777/788=0.986; state n=139 model 0.7410 vs floor 0.4892 = +0.2518 [+0.1786,+0.3309] SEP, twin 0.6906 (+0.0504 [+0.0142,+0.0981] SEP), coverage 111/139=0.799. CI half-widths vs floor: 0.0256 / 0.0417 / 0.0762. THE SEAL COVERS 3 OF THE BOARD'S 7 ROWS; the other four (coref, salience, common_noun_coref, wic) have a NUMBERED reason and a named next sealed corpus below -- the 'OR' branch of the bar."
floor: "Recomputed in place on the sealed population, never pasted. agent = nearest PRE-verbal nominal on the READER'S OWN categories, 0.7171 (it BEATS the reader, CI-separated); patient = nearest POST-verbal nominal on the reader's own categories, 0.5698; state = most-recent-noun positional binding on the reader's own categories, 0.4892. Strongest-floor selection is the scorer's own argmax over the declared floor list."
controls: "(1) INFORMATION-FREE TWIN per row (a random sentence nominal / the gold holders shuffled) -- LOSES on all three rows, CI-separated, so the rows are not shape artifacts; the state twin at 0.6906 against a model of 0.7410 is honestly WEAK and is reported as such, NOT as a passed control -- the chunk-matched control REFUTED my first explanation (short documents) by reproducing 0.6906 exactly at 8x the unit length, and the real cause is a sentence-scoped shuffle in the imported scorer (exp_board_rows_on_the_reader_v1.py:730-741), filed as sealed_holdout_patch.diff. (1b) CHUNK-MATCHED control (8 sealed documents concatenated to the board's ~20-sentence unit): agent 0.6340 vs 0.6328, patient and state BIT-IDENTICAL -- document length explains nothing here. (1c) SCRAMBLED-DOCUMENT control (sentences reassigned ACROSS sealed documents, discourse destroyed): agent 0.6439 (+0.0111, inside the 0.021 half-width), patient and state unchanged to 4dp -- so these three rows are sentence-local and this instrument CANNOT detect a discourse-scale change, a limitation published rather than hidden. (1d) COMPARISON arm, same scorer and reader in the same process on the board's own read UD-EWT test split: agent 0.7558 vs floor 0.8093 (-0.0535), patient 0.6791 vs 0.6308 (+0.0484), state 0.7522 vs 0.5044 (+0.2478) -- the agent row is below its floor on BOTH populations, so the seal re-measured a standing defect rather than discovering a generalisation gap. (2) COUNTED ANNOTATION-FREE WITNESS: 15,294 tokens written, 0 non-FORM CoNLL columns populated -- the reader received no gold tag, head, deprel or coref column; the same counter is shown CAN-FAIL in the self-test by planting a gold UPOS column (310 populated). (3) OVERLAP AUDIT: 0 of 998 sealed sentences (SHA-256 of the lowercased FORM sequence) appear in UD-EWT train/dev/test in EITHER on-disk copy, or in any of the 301 GUM+GENTLE documents. (4) ENUMERATION, not search: all 10,006 .py files under hdlab/ tools/ experiments/ verification/ walked; exactly 2 files name the sealed corpus (the instrument and its witness); the same walk FINDS 234 files naming GUM/GENTLE and 208 naming UD-EWT, so it can see a reader when one exists. (5) SEAL WITNESS verification/test_sealed_holdout_is_unread.py 23/23 PASS, including W7 which demonstrates the check FAILING on a deliberately planted leaking builder in a scratch directory. (6) DRAW controls: deterministic under the declared seed, holdout/reserve disjoint and exhaustive, stratified 70% per genre, and a different seed gives a different draw."
files_changed: experiments/exp_sealed_modern_holdout_v1.py, verification/test_sealed_holdout_is_unread.py, data/corpora/holdout/SEALED_modern_v1.json, data/corpora/holdout/ud_pud_sealed_v1/PROVENANCE.json
reverify: .venv/Scripts/python.exe verification/test_sealed_holdout_is_unread.py
---

# THE SEAL: a document-level modern holdout, declared before the first answer was examined

## 0. What this is, in plain words (for the scorecard line)

We set aside a batch of modern passages that nobody on this project had ever read — they were not on this
machine at all until this work started, so no tool could have learned from them and no setting could have been
tuned on them. Before looking at a single answer we wrote down, and committed to the record: which passages
they are (with a fingerprint of each one so they cannot be swapped), how they were chosen and with which
random seed, exactly how the reader would be graded, and the exact settings the reader would run at. Then the
reader read them once, as raw text with no answer key attached, and we graded it once. **On these unseen
passages the reader gets *who was done to* right 698 times in 1,000 and beats the dumb word-order rule that
guesses the nearest noun after the verb; it gets *what something is like* right 741 times in 1,000 and beats
its rule; and it gets *who did it* right 633 times in 1,000, which is WORSE than the dumb rule that just
picks the nearest noun before the verb — by 84 in 1,000, and that gap is wider than the measurement error.**
Nothing was adjusted after seeing those numbers.

## 1. THE ENUMERATION — why the sealed corpus is what it is

The brief required the seal be proved by enumeration. `--enumerate` walks **10,006 `.py` files** under
`hdlab/`, `tools/`, `experiments/`, `verification/` and records every `file:line` that names each modern gold.

| corpus | lines | files | code lines (not comments) |
|---|---|---|---|
| UD-EWT via `data/corpora/ud_english_ewt` | 387 | 208 | 292 |
| UD-EWT via a **second on-disk copy**, `experiments/data/ud_english_ewt` | 39 | 27 | 38 |
| GUM + GENTLE (`data/corpora/gum/conllu`) | 587 | 234 | 567 |
| **the sealed holdout** | 20 | **2** (the instrument + its witness) | 20 |

**Three findings the enumeration produced that a grep for the expected files would have missed:**

1. **GUM is exhausted, including GENTLE.** `experiments/gum_coref.load_docs` (`experiments/gum_coref.py:609`)
   globs *every* `GUM_*.conllu`; the board's split (`[i % 2 == 1]`) is applied **after** the load, so the
   loader has read all 275. GENTLE — the obvious "unread" candidate — is read by
   `experiments/exp_commonnoun_binder_live_report_v1.py:646`,
   `experiments/exp_crosstype_live_wire_gum_v1.py:279`,
   `experiments/exp_namebridge_fidelity_landing_v1.py:138`,
   `experiments/exp_entity_to_category_prior_v1.py:902`,
   `experiments/exp_passage_register_in_order_v1.py:1010`, and two witnesses
   (`verification/test_commonnoun_binder_live_report.py:212`,
   `verification/test_online_cue_cluster.py:167`). Worse for sealing purposes, GENTLE numbers are quoted as
   **calibration evidence inside the live organ**: `hdlab/lexical_categories.py:227-241` records the theta=100
   choice against GENTLE repeat-mention accuracy. A GENTLE holdout would have been a holdout the category
   organ's threshold was chosen on.
   *And there is no newer GUM to take:* `amir-zeldes/gum` `master` is at `22fdf87f9c71c96bcc771461d06e689b1f90020d`
   — **the exact commit `data/corpora/gum/PROVENANCE.json` already pins**, 301/301 files.
2. **The UD-EWT dev split is a trap.** `data/corpora/ud_english_ewt/` holds only `train` and `test`, so "use
   EWT dev" looks like a free sealed split. It is not: a **second copy of EWT lives at
   `experiments/data/ud_english_ewt/` and it contains `en_ewt-ud-dev.conllu`**, and two *asset builders* read
   it — `tools/build_construction_gold.py:485` and `tools/build_negation_factuality_gold.py:125,275` both
   build their gold from `train + dev + test` concatenated. `hdlab/uds_time_duration.py:120` reads it too.
   Across the tree, **dev is named at 32 code sites**. A holdout drawn from EWT dev would have been
   contaminated by two builders before the first read.
3. **Therefore no unread modern document existed on this disk.** That is the brief's checklist item 4
   condition, so the seal was built on a corpus *absent from the machine*: a corpus that is not on disk
   cannot have been read by a builder, and that is the strongest form the absence proof can take.

## 2. THE SEALED CORPUS AND THE DRAW

**UD_English-PUD**, pinned commit `f16eba4ae7f3d161870ed320676c5088b8fa476c`, file `en_pud-ud-test.conllu`,
SHA-256 `c80584f2bc2b31d5bada78a1136f9feec7ac49e5e18898db02dea434b5b8f0aa`, CC BY-SA 3.0. 397 documents /
1,000 sentences / 21,180 tokens of **2016-17 newswire and Wikipedia** — modern, not 19c. It is a treebank
that exists only as a blind test set; the project has never named it. It is parked at
`data/corpora/holdout/ud_pud_sealed_v1/` — a directory **no existing loader globs** (witness W2a), so no
builder can reach it by a path it already walks. `data/` is gitignored; the corpus is re-acquirable from the
pinned commit by `--fetch`, and the manifest carries the file hash and a hash of every document.

**The draw, declared and committed before it was executed** (`DRAW_RULE` in the cell, copied into the
manifest): unit = the document (`# newdoc id`); stratified by the genre prefix (`n` = newswire, `w` =
Wikipedia); within each stratum, sort ids, shuffle with `random.Random(20260916)`, take `ceil(0.70 * n)`.

| | docs | sentences | tokens | genres |
|---|---|---|---|---|
| **HOLDOUT_V1** (read once per landing) | 279 | 719 | 15,294 | 151 news / 128 wiki |
| **RESERVE_V2** (never read, by anything, including this cell) | 118 | 281 | 5,886 | 64 news / 54 wiki |

**The overlap audit** (SHA-256 of each lowercased space-joined FORM sequence, sentences ≥ 5 tokens; 998 sealed
sentences hashed): **0 shared sentences** with UD-EWT train (10,259 sentences), UD-EWT test (1,516), UD-EWT
dev (1,528), the `experiments/data` duplicates of all three, or the 301 GUM+GENTLE documents (14,115
sentences). A shared word is not leakage; a shared sentence is, and there are none.

## 3. THE SCORER AND CONFIGURATION, FIXED BEFORE THE FIRST ANSWER

The scorer is fixed **by import, not by copy**: every row, floor and twin comes from the landed pri-122 cell
`experiments/exp_board_rows_on_the_reader_v1.py` (`score_ud_chunk`, `_ud_write_chunk`, `_gold_agent_items`,
`_row`, `provenance`, `_paired`), whose SHA-256 (`f44e8f8b54bb208f4b1781527ef2bebf99f23439ac6a54b72144d234b9effada`)
is recorded in the manifest and re-checked on every score — a scorer that moves is surfaced with both hashes,
never silently accepted. Declared with it: abstentions counted **wrong**; every eligible gold question in the
denominator; the **document** as the unit of uncertainty; `n_boot = 2000`, bootstrap seed `20260916`; and the
gate (beat the strongest in-place floor CI-separated *and* the information-free twin).

The configuration manifest pins the run: **138** `HDLAB_*` flags discovered across `hdlab/` with their
resolved environment values (**all 138 unset — the run is at module defaults**, and the module SHA-256s
recorded alongside pin what those defaults are), SHA-256 of ten `hdlab/` + `experiments/` sources, and name,
size and SHA-256 of all **66** files in `data/frontend_assets` (files over 20 MB recorded by size only).

**The order is the point, and it is in the git history:** commit `66f5b1948` contains the manifest, the draw,
the scorer declaration and the witness. The reader had not been run on one sealed document at that point.

## 4. THE MEASUREMENT — the product's own read of raw text, reported once

279 `SituationReader.read` calls, one per sealed document, **15,294 tokens written and 0 non-FORM CoNLL
columns populated** — the reader received the FORM column and nothing else. Gold columns were read only by
the answer key, after the reader had answered.

| row | n | model | strongest floor | model − floor [95% CI] | twin | model − twin | CI half-width (floor) | coverage |
|---|---|---|---|---|---|---|---|---|
| who_did_what_agent | 806 | **0.6328** | 0.7171 (nearest pre-verbal nominal) | **−0.0844 [−0.1109, −0.0596] CI-SEP BELOW** | 0.1402 | +0.4926 [+0.4527,+0.5328] SEP | 0.0256 | 781/806 = 0.969 |
| who_did_what_patient | 788 | **0.6980** | 0.5698 (nearest post-verbal nominal) | **+0.1282 [+0.0864, +0.1698] SEP** | 0.1396 | +0.5584 [+0.5208,+0.5933] SEP | 0.0417 | 777/788 = 0.986 |
| state | 139 | **0.7410** | 0.4892 (most-recent-noun binding) | **+0.2518 [+0.1786, +0.3309] SEP** | 0.6906 | +0.0504 [+0.0142,+0.0981] SEP | 0.0762 | 111/139 = 0.799 |

**Read once. Not iterated on.** The landing record is appended to
`data/exp_sealed_modern_holdout_v1/board_landings.jsonl` with the corpus hash, both scorer hashes, the
provenance block and the resolved configuration; the file's line count is the number of times the seal has
been spent.

### What this says, stated carefully

- **The agent row loses to its own positional floor on sealed text — and §4b shows it loses on the board's own
  read split too.** So this is *not* a generalisation gap the seal discovered; it is a standing property of
  the agent rung that the sealed population makes worse but did not create. That distinction is exactly what
  a holdout is for, and getting it wrong would have been the expensive mistake here.
- **The state twin is weak, and §4c locates exactly why — it is a defect in the scorer, not in the corpus.**
  The twin sits at 0.6906 against a model of 0.7410, i.e. only ~5% of items ever receive a different holder.
  My first guess was that PUD's short documents were the cause; the chunk-matched control **refuted that** —
  concatenating 8 sealed documents reproduces the twin at 0.6906 *exactly*. The real cause is that
  `score_ud_chunk` shuffles the gold holders **within one sentence**
  (`experiments/exp_board_rows_on_the_reader_v1.py:730-741`), so a sentence with a single predicational
  clause hands the holder back to itself. A proposed fix is filed as `sealed_holdout_patch.diff`; until it
  lands, **the state row's "the twin loses" check is close to vacuous and the state margin should not be
  quoted as twin-controlled.**
- **Power, honestly:** agent and patient carry ~800 items across 279 document clusters, with CI half-widths
  of 0.026 and 0.042 — enough to see the margins reported. **State carries 139 items and a half-width of
  0.076; it cannot resolve a margin smaller than about 8 points**, so it is the row that will need the
  reserve, a larger seal, or both.

## 4b. THE GENERALISATION GAP — the same scorer, the same reader, the same process, on the read split

`--compare` runs the identical scorer and the identical reader over **UD-EWT test**, the board's own,
repeatedly-read split, capped to the sealed sentence count (719) and chunked the board's own way (20
sentences per pseudo-document), inside the **same process** as the sealed read.

| row | sealed model | read-split model | Δ model | sealed margin over floor | read-split margin over floor | Δ margin |
|---|---|---|---|---|---|---|
| who_did_what_agent | 0.6328 (n=806) | 0.7558 (n=561) | **−0.1230** | −0.0844 [−0.1109,−0.0596] | −0.0535 [−0.0757,−0.0305] | −0.0309 |
| who_did_what_patient | 0.6980 (n=788) | 0.6791 (n=455) | **+0.0189** | +0.1282 [+0.0864,+0.1698] SEP | +0.0484 [+0.0018,+0.1002] SEP | **+0.0798** |
| state | 0.7410 (n=139) | 0.7522 (n=113) | −0.0112 | +0.2518 [+0.1786,+0.3309] SEP | +0.2478 [+0.1308,+0.3637] SEP | +0.0040 |

Read-split floors: agent 0.8093, patient 0.6308, state 0.5044. Read-split twins: 0.2121 / 0.2088 / 0.6991.
Read-split coverage: 558/561, 452/455, 90/113. Read-split CI half-widths vs floor: 0.0226 / 0.0492 / 0.1164.

**What it says, and the caveat first: these two populations are different corpora, so this is an UNPAIRED
comparison between populations and no paired CI exists for the Δ column.** With that stated:

1. **There is no general collapse on sealed data.** Patient is *better* on the sealed population, by +0.0189
   absolute and +0.0798 in margin over its own floor. State is unchanged within noise (Δ margin +0.0040
   against half-widths of 0.076 and 0.116).
2. **The agent rung is below its floor on BOTH populations** — −0.0535 on the read split, −0.0844 sealed;
   both CIs exclude zero on the negative side. The seal did not reveal a new agent defect, it re-measured a
   standing one on a population nobody chose. The *worsening* (Δ margin −0.0309) is inside the sum of the two
   half-widths (0.0226 + 0.0256 = 0.048), so **"the agent gap is worse on unseen text" is NOT established**
   and must not be quoted as if it were.
3. **The reader's absolute agent accuracy is 12.3 points lower on sealed newswire/Wikipedia — but so is the
   floor, by 9.2 points.** Most of the absolute drop is the population being harder for both arms, which is
   precisely why a holdout must recompute its floors in place rather than paste the board's.
4. **Item density differs and it matters for power:** the same 719 sentences yield 806 agent items in PUD
   against 561 in UD-EWT (PUD sentences average 21 tokens of edited prose; EWT web text is shorter and
   fragment-heavy). The sealed population is therefore the better-powered of the two at equal sentence cost.

## 4c. THE CONTROLS — what the instrument can and cannot move

Two further reads of the sealed documents in the same process, both with the counted annotation-free witness
green (15,294 tokens, 0 non-FORM columns each). **Both are controls on the INSTRUMENT, not extra chances for
the model; neither changed a reported model number and nothing was tuned against them.**

| arm | reads | agent model / margin | patient model / margin | state model / margin | state twin |
|---|---|---|---|---|---|
| **headline** (native sealed documents) | 279 | 0.6328 / −0.0844 [−0.1109,−0.0596] | 0.6980 / +0.1282 [+0.0864,+0.1698] | 0.7410 / +0.2518 [+0.1786,+0.3309] | 0.6906 |
| **chunk-matched** (8 sealed docs concatenated, so the unit is ~20 sentences like the board's) | 35 | 0.6340 / −0.0831 [−0.1046,−0.0612] | 0.6980 / +0.1282 [+0.0825,+0.1694] | 0.7410 / +0.2518 [+0.1759,+0.3284] | 0.6906 |
| **scrambled** (sentences reassigned ACROSS sealed documents — discourse destroyed, sentences intact) | 279 | 0.6439 / −0.0732 [−0.0939,−0.0519] | 0.6980 / +0.1294 [+0.0910,+0.1695] | 0.7410 / +0.2518 [+0.1726,+0.3381] | 0.6763 |

**Three things this establishes, one of which cost me a wrong hypothesis:**

1. **Document length is not the explanation for anything here.** Concatenating the sealed documents into
   board-sized units moves the agent model by **+0.0012** and leaves patient and state **bit-identical**. So
   the sealed-vs-read-split difference in §4b is a property of the *population*, not of PUD's short
   documents — which was the obvious confound and is now excluded by measurement rather than by argument.
2. **These three rows are sentence-local, and the scrambled control proves it.** Destroying the discourse
   entirely — every sentence read in a document it does not belong to — moves the agent model by **+0.0111**
   (*upward*, and inside the CI half-width of 0.021) and leaves patient and state unchanged to four decimals.
   **The honest consequence: this instrument, on these three rows, cannot detect a change that only helps
   across sentences.** Sealing at the document level buys an unread *population*; it does not yet buy a
   discourse-scale measurement. That is an argument for the WikiCoref-style long-document seal in §5, and it
   is a limitation of the instrument I am publishing, not a caveat I was asked for.
3. **My first explanation of the weak state twin was wrong, and the control is what caught it.** I attributed
   twin 0.6906 to PUD's 2.5-sentence documents. The chunk-matched arm reproduces 0.6906 *exactly* at 8× the
   unit length, which rules that out; reading the scorer then located the real cause at
   `exp_board_rows_on_the_reader_v1.py:730-741` — the shuffle is scoped to one sentence's gold states.
   Filed as `sealed_holdout_patch.diff`, not applied.

## 5. THE FOUR ROWS THE SEAL DOES NOT COVER, AND THE NEXT SEALED SOURCE

This is the brief's "OR" branch, with numbers.

| board row | why it has no sealed counterpart |
|---|---|
| coref (pronoun), salience, common_noun_coref | They need a **coreference layer**. The only modern coref gold on disk is GUM/OntoGUM, and the enumeration shows **all 301 of its documents are read** by 234 files, with GENTLE additionally quoted as calibration evidence inside `hdlab/lexical_categories.py`. UD_English-PUD has no coref annotation. |
| wic | A lexical-sense pair benchmark, not a document corpus. Sealing it is a different draw (by sense pair, not by document) and it also needs the E03/E13 dev-vs-test unpooling, which is pri 126-adjacent but not this instrument. |

**Proposed next sealed source, checked live (HTTP 206 on both files at the time of writing):**
`google-research-datasets/gap-coreference` — **GAP**, 8,908 modern Wikipedia pronoun instances, free licence,
and the property that makes it the right next seal: **it ships as raw text with no annotation column at all**,
so the "is any gold column readable on the measured path?" question is answered by construction rather than by
a counter. It is the natural sealed instrument for pri 125 (pronoun discovery from text), because the reader
must find the pronoun *and* choose between two named candidates with nothing supplied. A document-level
companion for the salience row would be **WikiCoref** (30 fully coref-annotated modern Wikipedia documents,
freely available) — small, but documents are long, which is exactly the property PUD lacks. Neither was
acquired here: acquiring them is a build, and this brief's write list is four files.

## 6. WHAT THE INSTRUMENT CAN AND CANNOT DETECT

**Can:** a reader change that helps on the read splits and not on fresh modern prose (that is its whole
purpose); a floor that is stronger than the reader on a population nobody chose; a builder or board row that
starts reading the sealed ids (witness W1, on every certification run); a swapped or edited sealed document
(per-document SHA-256, W4b); a scorer edited after the seal (W6, both hashes printed); a gold column leaking
onto the measured path (the counted non-FORM column witness, shown can-fail).

**Cannot:** (a) anything about the four uncovered rows; (b) *erosion of its own seal* beyond counting — the
holdout is read once **per landing**, and after enough landings it becomes a dev set by ordinary selection
pressure. The mitigation is structural, not procedural: RESERVE_V2 is committed, hashed and unread, and the
board arm prints the running read count so the moment a decision is steered by V1 is visible. (c) It cannot
certify that the *corpus publisher's* text never influenced anything upstream of this repository — there is
no pretrained model here, so the only contamination channel is our own disk, which is what the overlap audit
measures. (d) Document-level discourse: PUD documents average 2.5 sentences, so a change that only helps
across long spans will look flat here. That is a property to fix with WikiCoref-style long documents, not a
property to hide.

## 7. ALTERNATE DESIGNS CONSIDERED, AND WHAT EACH WOULD TAKE

- **A rolling holdout** — already half-built: RESERVE_V2 (118 docs / 281 sentences) is drawn, hashed and
  committed by the same rule and seed. Promoting it is a one-line change of `which=` plus a manifest version
  bump; what it would take to be *complete* is a declared retirement trigger (e.g. "V1 retires the first time
  a landing decision cites it") written into the manifest rather than into prose.
- **A second seal per genre** — the draw is already stratified, and the manifest records each document's
  genre, so per-genre rows are a grouping change in `_rows_from_per`, not new data. The blocker is **power**:
  split 279 documents into news (151) and wiki (128) and the state row falls to ~70 items per genre, where a
  0.076 half-width becomes ~0.11. It is worth doing for agent and patient now and not for state.
- **Seal all 397 documents instead of 70%** — rejected deliberately: it buys ~40% more items on one
  measurement and gives up the reserve, which is the only defence against the holdout decaying into a dev set.
- **Draw a holdout from UD-EWT dev** — rejected on evidence, see §1 finding 2.

## 8. THE AUDIT QUESTIONS, ANSWERED WITH NUMBERS

**(i) Does it measure the PRODUCT or a component?** The product. `SituationReader.read` is called once per
sealed document — 279 calls — on a file containing the FORM column and nothing else. It is *not* the full
product: the reader is handed the corpus's sentence and token boundaries, so tokenisation and sentence
segmentation are not measured. That boundary is stated, not papered over.

**(ii) Is any gold column readable on the measured path? Prove not.** Proved by counting, not asserting:
15,294 tokens written, **0 non-FORM CoNLL columns populated**, in each of the three sealed arms. The counter
is shown able to fail — the self-test plants a gold UPOS column into the same writer's output and the counter
reports 310 populated. The gold UPOS/head/deprel columns are touched only by `_gold_agent_items` and
`COP.typed_gold`, both of which run *after* `sm` exists.

**(iii) Honest power per row.** agent n=806 over 279 document clusters, CI half-width 0.0256; patient n=788,
half-width 0.0417; **state n=139, half-width 0.0762 — it cannot resolve a margin below ~8 points and is the
row that needs the reserve or a bigger seal.** For orientation: the same 719 sentences drawn from UD-EWT
yield only 561 / 455 / 113 items, so the sealed population is better-powered per sentence than the split it
is compared against.

**(iv) Which board rows have no holdout counterpart, and why.** Four of seven: coref, salience and
common_noun_coref need a coref layer that PUD does not have and that GUM cannot supply (all 301 GUM+GENTLE
documents are read by 234 files, and GENTLE additionally appears as calibration evidence inside
`hdlab/lexical_categories.py:227-241`); wic is a sense-pair benchmark, not a document corpus, and needs its
own draw plus the E03/E13 dev-vs-test unpooling. Named next sources in §5.

**(v) Against the literature, and the gap.** The practice this imitates is the blind test set with a
pre-registered analysis plan — CoNLL/SemEval shared-task hidden test sets, the Netflix Prize held-back quiz
split, and clinical-trial pre-registration, where the primary endpoint and its analysis are filed before
unblinding. This instrument matches the mechanics (declared split, declared scorer, declared configuration,
hashes, read once) and beats the usual practice on two points: the split rule and seed are in version control
*before* the scoring commit, and the scorer is pinned by file hash rather than by prose. **The gap is real and
structural: a shared-task test set is scored once, ever, by an organiser who holds the labels; ours is scored
once *per landing* by the same team that builds the reader.** Nothing prevents selection pressure accumulating
across landings except the read counter and RESERVE_V2. An organiser-held seal would need a party outside this
session to hold the labels, which is not available here — so the honest statement is that this is a
pre-registered holdout, not a blind benchmark.

**(vi) My own negatives, audited.** (a) The agent row losing to its floor is *not* a finding about
generalisation — §4b shows it loses on the read split too, and the worsening (Δ margin −0.0309) is inside the
summed half-widths (0.048), so it is **not established** and I do not claim it. (b) The state twin result is
*not* a passed control; I first explained it wrongly (short documents), the chunk-matched arm refuted that
exactly, and the true cause is a scorer defect I am proposing a patch for. (c) The scrambled control produced
a *null*, and the null is the finding: these rows are sentence-local, so the document-level seal buys
population independence and not discourse sensitivity. (d) The sealed-vs-read comparison is **unpaired**
across two different corpora; no paired CI exists for it and none is quoted.

**(vii) Prior work on disk, checked.** `preregs/**` holds 3,833 files, of which three mention a holdout and
all three are 2026-05 compositional-holdout cells about vector-store generalisation, unrelated to a corpus
seal — nothing to re-tread, and I edited nothing there. The 19c ban (owner 2026-09-06) is satisfied by
construction: UD_English-PUD is 2016-17 newswire and Wikipedia, and no 19c number appears here. The board's
existing caps are the reason the comparison arm caps UD-EWT at the sealed sentence count rather than quoting
a differently-capped historical board number — the two arms were run in one process precisely so that no
number travels without its population. `notes/reference_retired_claims_never_requote.md` was checked; nothing
retired is quoted.

## 9. PRIORITY NEXT STEPS

1. **Trace the agent rung, not the holdout.** The reader is below the nearest-pre-verbal-nominal floor on both
   populations (−0.0535 read, −0.0844 sealed) at 0.969 coverage, so this is not abstention and not
   population: it is the agent selection itself. This is the highest-value thing the instrument pointed at.
2. **Land `sealed_holdout_patch.diff`** (strategy owns the file) so the state row has a real twin, and mark
   the landing record with a scorer version so state twin numbers stay comparable.
3. **Seal a modern coref source** — GAP first (raw text, no annotation column at all, the natural sealed
   instrument for pri 125's pronoun discovery), WikiCoref second (30 long modern documents, which is also the
   fix for the discourse-blindness §4c measured).
4. **Wire the board arm into the landing routine** — `--board` is one command, ~4 CPU-minutes, and appends
   one line with full provenance; it is only useful if it runs every landing rather than once.
5. **Do not promote RESERVE_V2 yet.** It is worth more unread. Promote it the first time a landing decision
   cites HOLDOUT_V1.

## SUBMISSION PROMPT

```
Problem: seal_a_document_level_modern_holdout_never_read_by_any_builder_or_board_declare_the_split_and_the_
scorer_before_the_first_answer_is_examined  (priority 126)

SOLVED. A document-level modern holdout is sealed, declared and measured once.

The enumeration (10,006 .py files walked, not grepped) found NO unread modern document on this disk: all 301
GUM+GENTLE documents are read by 234 files -- GENTLE included, and GENTLE numbers are quoted as calibration
evidence inside hdlab/lexical_categories.py -- and amir-zeldes/gum master is the exact commit we already pin.
UD-EWT is read in all three splits; the dev split is a trap, reachable via a SECOND on-disk copy at
experiments/data/ud_english_ewt/ from which two gold builders (build_construction_gold.py,
build_negation_factuality_gold.py) build assets. So the seal was built on a corpus that was not on the machine
at all: UD_English-PUD, pinned commit f16eba4a, 397 modern documents, parked in a directory no loader globs.

The manifest -- sealed ids + per-document SHA-256, the seeded stratified draw rule, the scorer (fixed by
IMPORT from pri 122 and by its file hash), the configuration (138 flags resolved, 66 asset hashes) and a
0-overlap audit -- was committed at 66f5b1948 BEFORE the reader saw one sealed document.

FIRST AND ONLY MEASUREMENT, the reader's own read of raw text (279 read() calls, 15,294 tokens, 0 non-FORM
CoNLL columns populated, abstentions counted wrong, document-paired bootstrap):
  who_did_what_agent    n=806  0.6328 vs floor 0.7171  -0.0844 [-0.1109,-0.0596]  BELOW ITS FLOOR
  who_did_what_patient  n=788  0.6980 vs floor 0.5698  +0.1282 [+0.0864,+0.1698]  CI-sep
  state                 n=139  0.7410 vs floor 0.4892  +0.2518 [+0.1786,+0.3309]  CI-sep
The comparison arm (same scorer, same reader, same process, UD-EWT test) shows the agent row is below its
floor there too (-0.0535), so the seal re-measured a STANDING defect rather than finding a generalisation gap
-- and patient is BETTER on sealed text (+0.0798 in margin). Controls: chunk-matched (document length explains
nothing: agent +0.0012, patient/state bit-identical) and scrambled-document (discourse destroyed: agent
+0.0111, inside the half-width) -- so these three rows are sentence-local and the instrument cannot yet detect
a discourse-scale change. The state twin is reported as WEAK, not as a passed control; its cause is located at
exp_board_rows_on_the_reader_v1.py:730-741 and a patch is filed, not applied.

The seal covers 3 of the board's 7 rows; the other four have a numbered reason and a named next corpus (GAP,
then WikiCoref). verification/test_sealed_holdout_is_unread.py: 23/23 PASS standalone and 1 passed under
pytest -m corpus, including a can-fail demonstration on a planted leak.

Files: experiments/exp_sealed_modern_holdout_v1.py, verification/test_sealed_holdout_is_unread.py,
data/corpora/holdout/SEALED_modern_v1.json, data/corpora/holdout/ud_pud_sealed_v1/PROVENANCE.json,
notes/problems/<slug>/SOLVED.md, notes/problems/<slug>/sealed_holdout_patch.diff.
Reverify: .venv/Scripts/python.exe verification/test_sealed_holdout_is_unread.py
```

## KEY REALIZATIONS

1. **"Unread" is a claim about *every* path, and the second copy is where it dies.** The natural move was
   "EWT dev isn't in `data/corpora/ud_english_ewt/`, so it's free". The enumeration found a *second* EWT tree
   under `experiments/data/` where two gold builders concatenate `train + dev + test`. The lesson generalises:
   **enumerate directories, not just the one the loader you know about uses.**
2. **The strongest seal is a corpus that is not on the machine.** Every on-disk candidate required proving a
   negative across 10,006 files. An absent corpus makes the absence proof trivial and auditable, and the
   standing authorisation to acquire an offline modern gold makes it cheap.
3. **Fix the scorer by importing it and hashing the file, not by copying it.** A copied scorer drifts silently;
   an imported one whose SHA-256 sits in the manifest cannot change without the next run printing both hashes.
4. **Commit the manifest as its own commit, before the scoring command.** "Declared before the first answer"
   is otherwise a sentence in a document rather than a fact in the history.
5. **A sealed population re-ranks the floors, not just the model.** The agent floor is stronger in newswire
   than in web text, so the first thing a fresh population changed was *what the reader has to beat*. A
   holdout that reports the model without recomputing the floor in place would have shown a rosier number and
   said nothing true.

## ADJACENT COMPONENTS / CONSUMED INPUTS (for the cross-solution map)

**Consumed inputs:** `experiments/exp_board_rows_on_the_reader_v1.py` (pri 122 — the scorer, the floors, the
twin, the annotation-free chunk writer); `hdlab/situation_reader.SituationReader.read`;
`experiments/exp_name_entity_clustering_v1.load_given_gazetteer`;
`experiments/exp_copular_is_a_binding_readout_v1` (the copular answer key); `experiments/_seed_checkpoint`.

**Flagged upstream needs (my walls, in order):** (1) **the agent rung** — the reader is below its positional
floor on sealed newswire; whichever of {population, genre, the floor itself} explains it, the agent row is the
one to trace. (2) **a modern coref gold nobody has read** — this blocks sealing 3 of 7 board rows and is a
data-acquisition job, not a mechanism job. (3) **document length** — every sealed document here is ~2.5
sentences, so the discourse-scale organs are untested on sealed data.

**AUDIT UPDATE (`notes/BRAIN_FOUNDATIONAL_AUDIT.md`):** nothing in this brief changes an organ, and nothing on
the measured path uses an external tool at inference — no spaCy, no nltk tagger, no supervised parser, no LLM.
The one item worth recording is not a fidelity verdict but a **measurement** one: the audit's fidelity claims
for the who-did-what rungs have, until now, only ever been checked on splits the project chose against, and
the first sealed check disagrees with the read-split picture on the agent rung.
