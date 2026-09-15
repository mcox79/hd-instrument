---
problem: the_reader_lowercases_every_token_at_its_one_sentence_source_so_the_category_organ_misses_70_percent_of_proper_nouns_on_the_live_path_flip_the_case_through_with_a_board_ab
status: SOLVED
bar: "The category organ's PROPN F1 through the live reader up CI-separated on GUM test (toward the 0.8622 measured at the organ), all-tag accuracy up; the entity layer's name typing live (>= 150 names typed on the reader's stream); the board's seven rows reported with CIs (up, down or flat -- a down row is repaired at its consumer, not by reverting the case); every string-keyed consumer classified; twin (random case per token) at floor -- OR a numbered located negative naming the consumer that cannot receive cased tokens and why."
result: "THE FLIP IS MEASURED WHERE IT LANDS AND IT IS THE LARGEST SINGLE HAND-OFF GAIN AT THE TOP OF THE CHAIN. (1) ON THE READER'S OWN CALL SEQUENCE over the whole 127,919-token MODERN GUM test split (128 documents, doc-paired bootstrap 2,000): the categories the reader's 25 downstream organs ACTUALLY READ go PROPN P/R/F1 0.9413/0.2996/0.4545 -> 0.9065/0.8273/0.8651, +0.4106 F1 CI[+0.3835,+0.4399] CI-SEPARATED, all-tag 0.9049 -> 0.9328, +0.0280 CI[+0.0235,+0.0327] CI-SEPARATED; PROPN misses 5,024 -> 1,239 of 7,173. (2) THROUGH THE WHOLE LIVE READER on 16 modern GUM test documents (GUM -> the reader's own CoNLL via the landed gum_to_conll; the reader UNPATCHED, the case forced at the harness): PROPN F1 0.4923 -> 0.8544 (+0.3621 CI[+0.3109,+0.4138]), all-tag 0.9096 -> 0.9300 (+0.0203 CI[+0.0096,+0.0335]), entity files 2459 -> 2563 (+4.2%), NAME-typed referent mentions 242 -> 599 (2.48x, bar asked for >= 150), who-did-what PATIENT 0.6687 -> 0.6779, pronoun coref 0.7722 -> 0.7722 IDENTICAL TO FOUR DECIMALS (the 7th independent confirmation that its inputs are closed-class). (3) THE SECOND DEFECT, NOT PREVIOUSLY RECORDED: pri 112's ONE IN-ORDER FEED already reads the passage CASED (lower=False at situation_reader:4498) and caches the settled posterior under ('tag', tuple(CASED sentence)), while every consumer asked `_cached_tag(sents[i])` with the LOWERCASED tuple -- a DIFFERENT dict key. MEASURED: 823 of 823 sentences tagged TWICE per read, 823 of 16,127 tag calls missing the cache and re-running forward-backward on case-stripped text; under the flip 0 duplicates and 0 misses out of 16,094 calls. The reader computed the right answer, cached it, and read the worse copy. (4) THE BOARD CANNOT SEE THIS AND HERE IS WHY: experiments/gum_coref.organ_tags -- the loader behind the board's coref / common-noun / salience rows -- feeds the category organ the RAW-CASED GUM forms, so the board has been grading the organ at 0.8651 while the live reader ran it at 0.4545; and none of the seven headline rows calls SituationReader.read at all (enumerated, section 7). (5) TWO CONSUMER REPAIRS THE FLIP EXPOSES, FOUND BY A STATIC SCAN AND CONFIRMED BY COUNT: `_read_causation` gates on `_CAUSAL_CONNECTIVES & set(toks)` and `_read_timeline` on `'had' not in toks` -- raw-token tests against lowercase literals. 49 of the 112 causal-connective sentences in the 16 documents open with a capitalised connective (43.8%) and stop matching the instant the case arrives. Both are repaired IN THE DIFF by folding case at the lookup, which is what the ~110 other case-folds on this path already do, and the `cased_repair` arm (the repairs re-compiled from the methods' OWN source) restores causal_links 298 -> 301 of the shipped 303 with every other row unchanged. (6) THE ONLY OTHER ROW THAT MOVES IS AN IMPROVEMENT, NOT A REGRESSION: the reader fires 30 fewer events (2,137 -> 2,107), and scored against GUM's own gold VERB tokens that is event-detection F1 0.8296 -> 0.8358, +0.0062 CI[+0.0017,+0.0132] CI-SEPARATED UP with recall flat (-0.0006 CI[-0.0039,+0.0027]) -- false positives 581 -> 552, of which those on gold PROPN tokens fall 46 -> 20. The reader has stopped treating names as verbs. (7) THE BOARD A/B, RUN, BOTH ARMS IN ONE PROCESS over the six functions that produce the seven headline rows: every row BYTE-IDENTICAL on every field, and the sentence-source call count is 0 on every row in both arms -- an EXACT zero from the call graph, not an underpowered estimate. (8) A MEASURED NO-OP I DID NOT SHIP: passing the CASED token into referent_per_np._mk_referent's span_toks changes nothing on any row, because coref.name_content_tokens defers to span_upos whenever the forward wire supplies it and lowercases its output regardless."
floor: "THE SHIPPED READER (`lower=True` at the three consumer call sites), recomputed in place on each arm's own population -- never pasted. Category rung: low all-tag 0.9049 / PROPN F1 0.4545 (128 GUM test documents, 127,919 tokens) and 0.9096 / 0.4923 (the 16-document full-read population). Who-did-what: the board's own POSITIONAL floor recomputed per arm on the 16-document population (agent 0.9172, patient 0.7178). Entity layer: the shipped reader's own counts (2,459 files, 242 name-typed referent mentions)."
controls: "(1) THE INFO-FREE TWIN -- each sentence's capital BUDGET permuted onto random capitalisable tokens (same number of capitals per sentence, positions destroyed): PROPN F1 0.6292 on the full test split and 0.6390 through the reader; the flip beats it +0.2358 CI[+0.2173,+0.2557] (organ path) and +0.2154 CI[+0.1871,+0.2707] (full read), both CI-SEPARATED, so the gain is the case being on the RIGHT words and not a train/read distribution match. AND THE TWIN BEATS THE SHIPPED READER by +0.1747 F1 -- the shipped input is worse than scrambling the capitals at random. (2) THE STREAM-ISOLATION CONTROL: coref.parse_litbank_conll reads the CoNLL FORM column directly, so its mention-stream tags are IDENTICAL in both arms (0.9300 all-tag / 0.8544 PROPN F1) -- every point of movement is the `sents` stream and nothing else in the reader changed. (3) HARNESS IDENTITY (--self-test): install(None) reproduces the shipped sentence source byte-for-byte, the forced arm reproduces `lower=False` byte-for-byte, and the two consumer repairs are installed by RE-COMPILING THE METHODS' OWN SOURCE with the one-line edit applied (so the A/B runs exactly the code the diff describes) and restore to the original objects. (4) NO-REGRESS, every situation-model dimension counted in both arms (section 4) plus an EVENT-DETECTION row scored against GUM's own gold VERB tokens, so a raw count change cannot be mistaken for a regression -- and it was not (F1 +0.0062 CI-separated UP). (4b) THE BOARD ROWS, BOTH ARMS IN ONE PROCESS, with the sentence source itself instrumented: seven rows byte-identical, 0 calls each. (5) PHASE-4 LEVERS EACH WITH THEIR OWN INFO-FREE TWIN (section 6): the per-string case card vs a random-string twin; the register-on-known-words arm vs a wrong-symbol twin; plus an ORACLE arm (read EVERY forced-position capital as mid-sentence) which is CI-separated NEGATIVE (0.8521 vs 0.8651) and confirms the organ's forced/non-forced split is already doing the right thing. (6) The gold is read with decision_source='gold' so the GUM UPOS/head/deprel columns are the ANSWER KEY only -- no arm's decision reads them."
files_changed: "experiments/exp_case_through_the_reader_v1.py (the cell: the case harness, the tag-stream logger, the four/five arms, the consumer-repair installer, the GUM->reader-CoNLL A/B, the organ-path replica on the full test split, the phase-4 levers, the seven-row board A/B, --self-test); notes/problems/<slug>/case_through_patch.diff (PROPOSED, NOT applied -- hdlab/situation_reader.py, hdlab/referent_per_np.py, hdlab/space_reader.py, hdlab/causation_typing.py, hdlab/scene_segment.py, hdlab/crosstype_live_adapter.py; `git apply --check` CLEAN at HEAD 0b89591f8); notes/problems/<slug>/SOLVED.md; data/exp_case_through_the_reader_v1/*.json + *.log (metrics). NO hdlab/ or tools/ file was edited; no landed record was rewritten (the board probe refuses to run unless HDLAB_EXP_NAME routes it to its own directory)."
reverify: ".venv/Scripts/python.exe experiments/exp_case_through_the_reader_v1.py --self-test   # ~30s, writes only to its own selftest dir; expect PASS -- the harness restores the shipped default byte-for-byte, the twin preserves each sentence's capital budget, `_mk_referent` is byte-identical on lowercase input, and the two consumer repairs install from their own source and restore.   THEN THE HEADLINE (the category rung on the whole modern test split, ~8 min):  OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe experiments/exp_case_through_the_reader_v1.py --organ --docs 0 --thetas 100   # expect n=127919, low all-tag 0.9049 / PROPN (0.9413, 0.2996, 0.4545), cased 0.9328 / (0.9065, 0.8273, 0.8651), twin 0.9108 / (0.8087, 0.5150, 0.6292); cased-low PROPN F1 +0.4106 CI[+0.3835,+0.4399] sep=True; cased-twin +0.2358 CI[+0.2173,+0.2557] sep=True.   AND THE FULL-READER A/B (~45 min, writes only to data/exp_case_through_the_reader_v1/):  ... --run --docs 16 --arms low,cased,twin,cased_repair   # expect the `sents` stream 0.9096/0.4923 -> 0.9300/0.8544, the COREF-stream control identical in both arms, entities 2459 -> 2563, name-typed 242 -> 599, coref 0.7722 in every arm, 823 -> 0 sentences tagged under both casings, causal_links 303/298/301 (low/cased/cased_repair) and event-detection F1 0.8296 -> 0.8358 (+0.0062 CI[+0.0017,+0.0132]).   AND THE BOARD (the six functions that produce the seven headline rows, both arms in ONE process; ~60 min; HDLAB_EXP_NAME is MANDATORY -- the cell refuses to run without one, so no landed board record can be rewritten):  HDLAB_EXP_NAME=case_board_rows_v1 ... --board-probe   # expect all seven rows byte-identical between the arms and `sentence_source_calls` 0 on every row in both arms.   AND THE PHASE-4 LEVERS (~25 min):  ... --capcard --docs 0   # expect capcard - cased PROPN F1 +0.0023 CI[+0.0009,+0.0039] sep, capcard - its twin +0.0028 CI[+0.0014,+0.0044] sep, oracle_mid - cased -0.0130 CI[-0.0182,-0.0089] sep (a clean negative), regknown - cased all-tag -0.0014 CI[-0.0019,-0.0009] sep (a clean negative)."
---

# The reader computed the right answer and threw it away: the sentence source lowercased the tokens AFTER the in-order feed had already read them cased, so every organ below re-tagged case-stripped text -- and the board has been grading a category organ the reader does not have

**STATUS: SOLVED** (solver scope; WIP until the owner marks DONE). Glass-box; no external LLM, no spaCy, no nltk, no supervised parser at inference. MODERN gold only (GUM; the 19c ban respected). **No `hdlab/` or `tools/` file was written** -- the flip and the two consumer repairs are proposed as `case_through_patch.diff`, and every one of them was EXECUTED end-to-end in the A/B before being proposed: the repairs are installed by re-compiling the methods' **own source** with the one-line edit applied, so the experiment runs exactly the code the diff describes.

---

## 1. THE OPENING MOVE -- how does the BRAIN do this, and what operation do we copy?

**Orthographic case is a PERCEIVED CUE, and the comprehender never discards it before deciding a word's category. It discards it for exactly one thing: the lexical lookup.**

- The **visual word-form system** (left occipito-temporal; Cohen & Dehaene 2002; Dehaene et al. 2005) computes an **abstract letter identity** that is case-invariant -- cross-case priming (`RADIO` -> `radio`) is as strong as same-case. *That* is the warrant for a case-folded LEXICAL key, and the organ already does exactly that (`lexical_categories.posterior` builds `_sent_lows` for the emission table).
- The surface graphemic code is **not** thrown away. It is read as a cue with **position-relative validity** -- the Competition Model in its cleanest form (MacWhinney & Bates 1989: validity = availability x **reliability**): a capital at a sentence's first word is *forced*, so its reliability is ~0, while a capital mid-sentence is a highly reliable proper-name cue. The organ already encodes precisely this: `word_shape_rich(w_raw)` x `position_class(words, i)` makes `Cap@i` and `Cap@m` DIFFERENT learned rows.
- Above the word-form level the **proper-name route** (left anterior temporal lobe / temporal pole -- Semenza 2006/2009 proper-name anomia; Damasio et al. 1996) decides that a form picks out an INDIVIDUAL (Kripke 1980, rigid designation). It is **fed by** the word-form level, not a substitute for it.

**So the brain's architecture is TWO ROUTES OUT OF ONE PERCEPT: a case-folded key for the lexicon, and the surface shape kept for the categorisation.** Our organ implements both. **The defect was purely upstream -- the reader severed the second route before the organ could see it.**

Nothing here is an invention of ours to sweep; the brief said so and the measurement agrees. The fix is one argument at four call sites plus two consumers that were reading a raw string where they should have folded case at their own lookup.

---

## 2. THE STATUS PROBE -- where the signal is lost, chain by chain, with counts

**The chain:** text -> **the sentence source** (`scene_segment.parse_conll_sentences`) -> **the category organ** (`lexical_categories`) -> **lemma** (`morphology`) -> **heads** (`attachment_arm`) -> **roles** (`graded_role_assigner`) -> **the 25 `sents` consumers** in `situation_reader.read`.

| rung | what the hand-off PRODUCES | what the next rung READS | what is LOST | BF status as the disk shows it |
|---|---|---|---|---|
| **sentence source** | `[[token]]`, **lowercased** (`cols[3].lower()`) | everything below | **the whole orthographic route**: the cased test text realizes 35 shape x position symbols of which 13 are case symbols; the SAME text lowercased realizes 24, of which **1** | registry `BF_SPIRIT`, but **NOT_BF on this hand-off** -- the word-form system does not delete the percept |
| **the in-order feed** (pri 112) | `feed_passage(CASED sentences)` -> the settled posterior, cached under `("tag", tuple(CASED sentence))` | **nobody**, on the shipped path | **the entire feed**: consumers ask `_cached_tag(sents[i])` with the LOWERCASED tuple, a different dict key | BF (Heim/DRT in-order file cards) **whose output was unreachable** |
| **category organ** | the tags AND the graded posterior every rung below consumes | heads, roles, events, entities, ... | **PROPN recall 0.8273 -> 0.2996** (5,024 of 7,173 proper nouns); all-tag 0.9328 -> 0.9049 | BF_SPIRIT -- the organ is right and was being fed a mutilated percept |
| **lemma / heads / roles** | a graded hand-off keyed on the category | the consumers | inherits the category error; the heads rung reads the category POSTERIOR, so it inherits the GRADED error too | BF_SPIRIT |
| **25 `sents` consumers** (24 default-ON) | events / entities / causal links / timeline / goals / affect / state / space / bridges / senses / ... | the board and the reader's instruments | two of them additionally gate on a RAW token equal to a lowercase literal (section 5) | mixed |

**THE THREE COUNTS THAT MATTER, all measured.**

**(a) The reader tags every sentence TWICE and reads the worse copy.** Instrumenting `SituationReader._cached_tag` over 16 modern GUM documents: **823 of 823 sentences** sit in the per-read cache under BOTH casings; **823 of 16,127 tag calls MISS** and re-run forward-backward on case-stripped text. Under the flip: **0 sentences under two casings, 0 misses, 16,094 hits of 16,094 calls.** *pri 112's SOLVED says of this feed "the consumer that re-asks for a sentence is served THIS pass instead of re-running forward-backward: the feed costs no extra passes." On the shipped path that is not true, and the reason is the case one level up -- the same shape as pri 109's finding (4) about `_mk_referent`.*

**(b) The board grades an organ the reader does not have.** `experiments/gum_coref.organ_tags` -- the loader behind the board's coref / common-noun / salience rows -- calls `lc.feed_passage([[x.form for x in row] ...])`, i.e. the **RAW-CASED** GUM forms. The board has been measuring the category organ at PROPN F1 **0.8651** while the live reader's organs read it at **0.4545**.

**(c) The cue alphabet is not degraded, it is absent.** 13 case symbols realizable on cased text, **1** on the same text lowercased.

---

## 3. THE CATEGORY RUNG, ON THE READER'S OWN CALL SEQUENCE, ON THE WHOLE MODERN TEST SPLIT

`--organ` replicates the reader's category path exactly and cheaply -- `new_document()` -> `feed_passage(CASED sentences)` (the pri-112 in-order feed, unchanged in every arm) -> one `posterior(sents[i])` READ per sentence, `sents` lowercased under the shipped default and cased under the flip -- so it runs on **all 128 GUM test documents, 127,919 tokens** instead of the 16 a full read affords. It reproduces pri 109's organ numbers to four decimals, which is what licenses every comparison.

| arm (128 GUM test docs, 127,919 tokens) | all-tag | PROPN P | PROPN R | **PROPN F1** | TP/FP/FN |
|---|---|---|---|---|---|
| **`low`** -- as it ships | 0.9049 | 0.9413 | 0.2996 | **0.4545** | 2149 / 134 / 5024 |
| **`cased`** -- the flip | **0.9328** | 0.9065 | **0.8273** | **0.8651** | 5934 / 612 / 1239 |
| **`twin`** -- info-free (capital budget permuted onto random tokens) | 0.9108 | 0.8087 | 0.5150 | **0.6292** | -- |

- **`cased` - `low`:** all-tag **+0.0280 CI[+0.0235,+0.0327]** ✅ ; PROPN F1 **+0.4106 CI[+0.3835,+0.4399]** ✅
- **`cased` - `twin`:** all-tag **+0.0220 CI[+0.0191,+0.0253]** ✅ ; PROPN F1 **+0.2358 CI[+0.2173,+0.2557]** ✅

> **THE TWIN IS THE CONTROL THAT MATTERS AND IT SAYS SOMETHING UNCOMFORTABLE ABOUT THE SHIPPED PATH.** The twin has exactly as many capitals as the real text, in the same per-sentence budget, on the wrong words. It scores PROPN F1 **0.6292 -- 0.1747 ABOVE the reader as it ships.** So the gain is not "the offline table was built on cased text and lowercase is out of distribution" (the twin is in distribution and still loses by +0.2358 CI-separated); it is that the case is **on the right words**. And the reader's current input is **worse than scrambling the capitals at random.**

**A SIGN FLIP IN A LANDED ARM, worth its own line.** pri 104's passage SHAPE register (`ENT_THETA_DOC=100`, the passage's own capitalisation convention) is **CI-separated NEGATIVE on the shipped lowercased path** -- PROPN F1 -0.0152 CI[-0.0183,-0.0120], all-tag -0.0008 CI[-0.0011,-0.0006] -- and **CI-separated POSITIVE once the case reaches it**: PROPN F1 +0.0012 CI[+0.0002,+0.0023]. *A convention arm cannot learn a convention from text that has none; it was paying a cost for a signal it could not receive.*

---

## 4. THROUGH THE WHOLE LIVE READER, ON MODERN GOLD

`--run` converts GUM documents to the reader's own OntoNotes-style coref CoNLL (the landed `exp_crosstype_gum_conll_fullread_v1.gum_to_conll`, mention round-trip gated) and runs the **entire `SituationReader.read`** on them -- 16 test documents spread across GUM's genres, doc-paired bootstrap 2,000. The reader is UNPATCHED; the case is forced at the harness level.

| arm | tokens | all-tag | PROPN P/R/F1 | entity files | NAME-typed referent mentions | pronoun coref | wdw agent | wdw patient |
|---|---|---|---|---|---|---|---|---|
| **`low`** (ships) | 15,748 | 0.9096 | 0.9560 / 0.3315 / **0.4923** | 2,459 | 242 | **0.7722** | 0.6748 | 0.6687 |
| **`cased`** | 15,748 | **0.9300** | 0.9200 / 0.7975 / **0.8544** | **2,563** | **599** | **0.7722** | 0.6748 | **0.6779** |
| **`twin`** | 15,748 | 0.9129 | 0.8214 / 0.5229 / **0.6390** | 2,794 | 438 | **0.7722** | 0.6748 | 0.6564 |
| **`cased_span`** (cased + cased `span_toks`) | 15,748 | 0.9300 | **identical to `cased` on every row** | 2,563 | 599 | 0.7722 | 0.6748 | 0.6779 |
| *floor (positional)* | | | | | | | *0.9172* | *0.7178* |

| contrast | all-tag | PROPN F1 | coref | agent | patient |
|---|---|---|---|---|---|
| **cased - low** | **+0.0203 [+0.0096,+0.0335]** ✅ | **+0.3621 [+0.3109,+0.4138]** ✅ | 0.0000 | 0.0000 | +0.0092 [0.0000,+0.0227] ns |
| **cased - twin** | **+0.0170 [+0.0099,+0.0256]** ✅ | **+0.2154 [+0.1871,+0.2707]** ✅ | 0.0000 | 0.0000 | **+0.0215 [+0.0085,+0.0381]** ✅ |
| twin - low | +0.0033 ns | **+0.1467 [+0.0872,+0.1785]** ✅ | 0.0000 | 0.0000 | -0.0123 ns |

**THE CONTROL THAT ISOLATES THE EFFECT.** `coref.parse_litbank_conll` reads the CoNLL FORM column directly, so its mention stream is raw-cased in BOTH arms, and its tags are **identical** in `low` and `cased` (all-tag 0.9300, PROPN F1 0.8544 in both). **Every point of movement above is the `sents` stream and nothing else in the reader changed.**

**THE WIRING COUNTS.** `low`: 16,127 tag calls, 15,304 hits, **823 misses**; 1,649 cached tag entries (823 cased, 826 lowercase); **823 sentences present under BOTH casings**. `cased`: 16,094 calls, **16,094 hits, 0 misses**; 826 entries (823 cased, 3 lowercase -- three genuinely all-lowercase sentences); **0 under both casings**.

**NO-REGRESS: every situation-model dimension the reader built (sum over the 16 documents).**

| dimension | low | cased | twin |
|---|---|---|---|
| coref_resolutions | 79 | 79 | 79 |
| entities | 2,459 | **2,563** | 2,794 |
| events / event_tokens | 2,137 | 2,107 | 2,114 |
| events_with_agent | 2,088 | 2,061 | 2,077 |
| events_with_patient | 1,755 | 1,729 | 1,739 |
| events_with_affect | 1,238 | 1,194 | 1,195 |
| events_with_subj_role | 1,526 | 1,524 | 1,653 |
| causal_links | 303 | 298 | 288 |
| timeline_frames / timeline_order | 12 / 301 | 12 / 301 | 11 / 294 |
| typed_causal / coherence / locations / senses / bridges / suppressed | 0 | 0 | 0 |

**TWO ROWS GO DOWN AND BOTH ARE CONSUMERS TO REPAIR, NOT REASONS TO REVERT (owner 09-12).** `causal_links` 303 -> 298 and `events` 2,137 -> 2,107 (-1.4%). The causal drop is fully explained and repaired (section 5): 49 of the 112 causal-connective sentences in these documents open with a **capitalised** connective and stop matching the raw-token gate. The event drop is the category organ doing its job differently -- a capitalised word that used to be read VERB is now read PROPN -- and scored against gold it is a PRECISION GAIN, not a loss (below).

**THE `cased_repair` ARM -- the flip PLUS the two case-folded consumer gates, run as a fourth arm through the whole reader** (the repairs installed by re-compiling the two methods' own source with the one-line edit applied, so the arm runs exactly the code the diff describes):

| | causal_links | events | entity files | name-typed | coref | agent | patient | all-tag | PROPN F1 |
|---|---|---|---|---|---|---|---|---|---|
| `low` (ships) | 303 | 2,137 | 2,459 | 242 | 0.7722 | 0.6748 | 0.6687 | 0.9096 | 0.4923 |
| `cased` | 298 | 2,107 | 2,563 | 599 | 0.7722 | 0.6748 | 0.6779 | 0.9300 | 0.8544 |
| **`cased_repair`** | **301** | 2,107 | 2,563 | 599 | 0.7722 | 0.6748 | 0.6779 | 0.9300 | 0.8544 |

**The causal row is repaired at its consumer, exactly as the owner's rule says (298 -> 301 of the shipped 303), and nothing else moves.** The residual 2 links are sentences whose only connective is capitalised AND which yield fewer than two events, so the gate was never the binding constraint there.

**AND THE EVENT COUNT IS NOT A REGRESSION -- scored against GUM's own gold VERB tokens it is a PRECISION GAIN:**

| arm | TP | FP | FN | P / R / **F1** | false positives on gold **PROPN** tokens |
|---|---|---|---|---|---|
| `low` | 1,556 | 581 | 58 | 0.7281 / 0.9641 / **0.8296** | **46** |
| `cased` / `cased_repair` | 1,555 | 552 | 59 | 0.7380 / 0.9634 / **0.8358** | **20** |
| `twin` | 1,551 | 563 | 63 | 0.7337 / 0.9610 / **0.8321** | 38 |

**Event-detection F1 +0.0062 CI[+0.0017,+0.0132] CI-SEPARATED UP; recall -0.0006 CI[-0.0039,+0.0027] NOT separated.** The 30 events the reader stops firing are 26 fewer predicates fired on tokens GUM calls PROPN plus a handful of other function-word mis-fires -- **the reader has stopped treating names as verbs.** *A raw count went down and the capability went up; this is exactly why the row is scored rather than counted.*

---

## 5. GENERALIZE (checklist item 3) -- every consumer downstream of the sentence source, classified

`sents` is read by **25 organs** inside `situation_reader.read` (`_read_events`/`_read_events_wired`, `_read_timeline`, `_read_causation`, `_read_timeline_register`, `_read_belief`, `_read_predict_revise`, `_read_surprisal`, `_read_world_state`, `_read_entity_states`, `_read_goals`, `_read_affect`, `_read_tom_action`, `_read_infer_emotion`, `_read_bridges`, `_read_senses`, `_read_affected_entity`, `_read_prediction`, `_read_causal_reasoning`, `_read_predictive_causal`, `_read_spatial_reasoning`, `_read_temporal_reasoning`, `_read_natural_logic`, `_read_coherence`, `_read_polarity`) -- **24 default-ON** (only `track_coherence` ships off). Plus the three other call sites of the source: `referent_per_np_source`, `space_reader`, `causation_typing`.

**How each was classified:** (i) a static scan of every token-string test on the read path across all of `hdlab/` (`"<lower literal>" in toks`, `set(toks) & <lowercase set>`, `toks[i] == "<lower literal>"`); (ii) the empirical A/B, with every situation-model dimension counted in both arms.

| class | count | what they do | verdict |
|---|---|---|---|
| **case-insensitive AT THEIR OWN LOOKUP already** | the great majority -- `situation_reader` folds case 49 times on this path, `causation_typing` 38, `space_reader` 21, `referent_per_np` 6 | `low = [t.lower() for t in toks]` before any lexicon/dict/gazetteer touch (`_read_senses`' passage context, `_read_causation`'s inner `low`, `goal_register.extract_goals_sentence`, `space_reader.canon_node`, `gender_organ.infer`, `coref.name_content_tokens`) | ✅ **unaffected -- and they are RIGHT to fold**: a closed-class cue word is the same word capitalised |
| **case-SENSITIVE by accident -- REPAIRED in the diff** | **2 gates, 3 lines** | `_read_timeline`: `if "had" not in toks` ; `_read_causation`: `_CAUSAL_CONNECTIVES & set(toks)` (twice) | 🔧 **repaired.** Counted: **49 of 112** causal-connective sentences (43.8%) open with a capitalised `So/Because/Since/Therefore/Thus/Hence`; `had` 0 of 23 on this sample but the same latent defect (`Had he known ...`) |
| **reads the ORGAN, not the string** | the name decision in 10 organs | `coref.name_content_tokens(span, upos=span_upos)` defers to the category organ whenever the forward wire supplies `span_upos`, and lowercases its output either way | ✅ unaffected -- and this is WHY `cased_span` is a measured no-op |
| **reads raw-cased ALREADY** | `coref.parse_litbank_conll` (the coref mention stream), `gum_coref.organ_tags` (the board loader) | they read the CoNLL FORM column directly, never through the sentence source | ✅ unaffected -- and this is the CONTROL in section 4 |
| **⚠️ the OTHER direction: 19 bare call sites in `verification/`** | 19 files | they call `parse_conll_sentences(path)` with the default and therefore keep the OLD lowercased input | they still PASS after the flip, but they stop mirroring the live reader. **Named for strategy in section 13; I am scope-barred from `verification/`** |

---

## 6. THE QUALITY PUSH (phase 4) -- the residual located, two more levers built and measured

**WHERE THE RESIDUAL IS, counted first so the levers are aimed rather than guessed.** After the flip the category rung leaves **1,239 PROPN false negatives and 612 false positives** on 127,919 tokens. The anatomy:

- **Only 65 of the 1,239 misses (5.2%) are at a FORCED sentence-initial position** (36 known, 29 novel); **1,174 are mid-sentence** (699 known, 475 novel).
- **948 of the misses are called NOUN**, 143 ADJ, 38 PRON.
- The false positives come from **NOUN 226, ADJ 165, X 65, INTJ 58, VERB 35** -- the signature of **title case and headings**, where every content word is capitalised and `Cap@m` loses its reliability.
- **Per document** (`cased` PROPN F1, 16-document full read): court_property 0.9801, voyage_fortlee 0.9538, bio_marbles 0.9098, interview_mckenzie 0.8913, letter_marcie3 0.8800, academic_census 0.8696, textbook_chemistry 0.8214, speech_data 0.8056, academic_thrones 0.7568 -- then **vlog_hair 0.6486, podcast_addiction 0.6364, news_hackers 0.6154, whow_cactus 0.5000, conversation_scientist 0.4000** (n=3). **The bottom of that list is the spoken and informal registers: passages whose orthographic convention is not the one the offline table learned.**

**LEVER A -- the passage's per-STRING orthographic FILE CARD (a small CI-separated WIN).** *Brain structure:* Heim (1982) file-change semantics; the organ already keeps a card per lowercased string (`DiscourseRegister.h`), written by the ONE in-order feed and read as-of the sentence (pri 112). What the card does not record is the ORTHOGRAPHIC fact. A reader who has met `Marcie` capitalised MID-sentence has established that the string names an individual; at the start of the next sentence, where the capital is forced and tells them nothing, that established fact is the cue they use instead. *Prototype (a LOCATOR, not the landed form):* when a token at a forced position is capital-initial and the passage's own record, as of sentences strictly before this one, has met that exact string capitalised at a non-forced position, read its shape emission against the `Cap@m` row it established. **Measured on 128 documents: PROPN F1 0.8651 -> 0.8673 (+0.0022), all-tag 0.9328 -> 0.9331; 957 of 7,060 forced-position capitals read as established.** Its info-free twin (the same number of strings drawn at random from the passage's own vocabulary) scores 0.8645. **The contrast: `capcard` - `cased` PROPN F1 +0.0023 CI[+0.0009,+0.0039] CI-SEPARATED, all-tag +0.0003 CI[+0.0001,+0.0004] CI-SEPARATED; `capcard` - its own twin +0.0028 CI[+0.0014,+0.0044] CI-SEPARATED, while the twin itself is null against `cased` (-0.0005 CI[-0.0012,+0.0001], not separated).** So it is a REAL, twin-beating, brain-faithful gain -- and a tiny one.
**AND THE ARITHMETIC BOUND WAS AVAILABLE BEFORE THE RUN: only 65 of 7,173 gold proper nouns are missed at a forced position, so NO implementation of this idea could be worth more than ~0.005 F1.** *The landed form would have to be a GRADED card (counts of forced/non-forced observations, shrunk `a = n/(n+theta)`, written by the feed and read as-of); I used the hard bit deliberately, to locate the signal, and the signal is small.*

**THE ORACLE THAT BOUNDS IT FROM THE OTHER SIDE, and it is a clean negative:** reading **every** forced-position capital against the `Cap@m` row scores **0.8521**, CI-separated BELOW `cased`'s 0.8651. **The organ's forced/non-forced split is already doing the right thing**, which is exactly what the Competition Model's reliability argument predicts; the only value in Lever A is its SELECTIVITY, and the selective population is 957 tokens.

**LEVER B -- read the passage's convention for KNOWN words too (a CI-separated NEGATIVE, understood).** The organ WRITES its shape register from known tokens (`ENT_REG_KNOWN`) but READS it only for novel forms (`_log_shape_factor` returns the whole-vocabulary row whenever `known`). Most of the residual is on KNOWN forms (699 of the 1,174 mid-sentence misses). *Prototype:* apply the organ's OWN shrinkage (`a = n/(n+theta)`, with the `ENT_REG_OFFSET` correction) to the whole-vocabulary row as well. **Measured on 128 documents: PROPN F1 0.8651 -> 0.8644 (-0.0007 CI[-0.0022,+0.0007], NOT separated) and all-tag 0.9328 -> 0.9314, -0.0014 CI[-0.0019,-0.0009] -- CI-separated NEGATIVE.** Its info-free twin (the same local records attached to the WRONG shape symbols) scores 0.8575, so the arm beats its twin +0.0069 CI[+0.0015,+0.0124] CI-separated. **The register's content IS informative; it is just less informative than the whole-vocabulary row it would displace** -- see N4.

---

## 7. THE BOARD (bar item: "the board's seven rows reported with CIs")

**The seven rows of the 19c-free modern board CANNOT MOVE UNDER THIS FLIP, and that is an arithmetic fact about the board, not a claim about the flip.**

The flip changes exactly one thing: what `hdlab/scene_segment.parse_conll_sentences` returns. **No board arm that feeds a headline dimension ever calls it** -- I enumerated every `board_*_dimension` in `experiments/exp_situation_model_qa_modern_v1.py` and traced the four that name the reader at all:

| board arm | reaches `SituationReader.read` / `parse_conll_sentences`? | in the seven-row aggregate? |
|---|---|---|
| `coref`, `salience`, `common_noun_coref` | ❌ -- built from `gum_coref.load_docs` / `gum_to_live` mention streams; the pronoun pick runs on `EventCentralityReader`, not on `read()` | yes |
| `who_did_what_agent`, `who_did_what_patient`, `state` | ❌ -- UD-EWT deprels, own loaders | yes |
| `wic` | ❌ | yes |
| `board_coref_via_reader_dimension` | ❌ despite the name -- `EventCentralityReader` on GUM mentions | no (own row) |
| `board_spatial_extraction_precision_dimension`, `_reader_commonnoun_resolution` | ❌ -- docstring references to the reader's configuration only | no / yes (common-noun) |
| **`board_affect_harm_help_dimension`'s LIVE-READER cross-check** | ✅ **the only one** -- it writes one-sentence synthetic CoNLL files and calls `SituationReader.read` on them | no (own row) |

**So the honest statement is: the board is the wrong instrument for this defect, for the same structural reason pri 109 found -- and worse, `experiments/gum_coref.organ_tags` feeds the category organ the RAW-CASED GUM forms, so the board has been grading the organ at the flipped value (0.8651) all along while the reader ran at 0.4545.** A board A/B measures the difference between two things that are already identical on six of seven rows and on the seventh (`common_noun_coref`) as well.

**The board probe, run as a witness** (`--board-probe`, output routed away from the landed record by `HDLAB_EXP_NAME`): it counts every call to the sentence source made during one full board run. **THE BOARD A/B, RUN: the six functions that produce the seven headline rows, BOTH ARMS, IN ONE PROCESS** (`--board-probe`, output routed away from any landed record by `HDLAB_EXP_NAME=case_board_rows_v1`; the cell REFUSES to run without that). The counter wraps the sentence source itself.

| board row | n | shipped | cased | strongest floor | byte-identical? | **sentence-source calls** |
|---|---|---|---|---|---|---|
| coref (pronoun) | 3145 | 0.4178 | 0.4178 | 0.3199 | ✅ | **0** |
| salience | 128 | 0.2656 | 0.2656 | 0.2188 | ✅ | **0** |
| common_noun_coref | 2994 | 0.5461 | 0.5461 | 0.5344 | ✅ | **0** |
| who_did_what_agent | 1423 | 0.8552 | 0.8552 | 0.8468 | ✅ | **0** |
| who_did_what_patient | 1255 | 0.8151 | 0.8151 | 0.7243 | ✅ | **0** |
| state | 378 | 0.7910 | 0.7910 | 0.5714 | ✅ | **0** |
| wic | 120 | 0.7833 | 0.7833 | 0.5500 | ✅ | **0** |

**Every row is BYTE-IDENTICAL between the arms on every field (not just `model_acc`), and every row makes ZERO calls to the function the flip changes, in BOTH arms.** These zeros are EXACT -- a property of the call graph -- not an underpowered estimate, so no amount of extra bootstrap would change them. *(These are the rows as this probe's own invocation computes them; they are not interchangeable with the published board's numbers, which run with the board's own caps and seeds. The comparison that matters here is arm-vs-arm within this one process.)*

**The one board arm that IS on the flip's path** is `board_affect_harm_help_dimension`'s LIVE-READER cross-check, which writes one-sentence synthetic CoNLL files and calls `SituationReader.read` on them. It is not one of the seven and it carries its own row; strategy should expect it -- and only it -- to move.

**THE SPECIFIC BOARD QUESTION FOR STRATEGY, in plain language:**

> *The programme grades the word-type reader on text that still has its capital letters, but the reading system itself was handed text with the capitals stripped out. Those are two different machines and they differ by a lot -- on capitalised names, one gets 87 in 100 right and the other 45 in 100. Fixing the reading system does not change any of the seven scores on the scoreboard, because not one of those seven scores actually runs the reading system; they each rebuild their own copy of it from the annotated files. So the scoreboard cannot tell us whether this fix helped. Two things follow, and they are both decisions above my level: (1) should the scoreboard's rows be rebuilt to run the actual reading system, so that a repair like this one is visible where we look? and (2) until they are, which instrument do we accept as the evidence for a change of this kind -- the direct measurement of what the reading system's own parts receive, which is what I used?*

---

---


## 8. THE NEGATIVES, EACH UNDERSTOOD WITH A NUMBER

**(N1) `cased_span` -- passing the CASED token into `referent_per_np._mk_referent`'s `span_toks` -- is a measured NO-OP.** Every row of the 16-document A/B is identical to `cased` (all-tag 0.9300, PROPN F1 0.8544, entities 2,563, name-typed 599, coref 0.7722, agent 0.6748, patient 0.6779). *Mechanism, from the source:* `coref.name_content_tokens(span, upos=span_upos)` takes the `_span_head_is_name(span, upos)` route whenever `span_upos` is present and `NAME_SOURCE != "caps"` -- and pri 109's forward wire puts `span_upos` on every referent mention -- so the capitalisation route is never consulted; and when it IS consulted it returns `t.lower()`, so no consumer downstream can see the case either. **Consequence: I did NOT ship it.** The diff stays surgical and nobody has to re-derive this. *(It would matter again only under the `HDLAB_NAME_SOURCE=caps` baseline switch.)*

**(N2) The `twin` beats the SHIPPED reader by +0.1747 PROPN F1.** Not a defect in the twin -- a fact about the shipped path. A capital in the wrong place still tells the organ "some word here is a name"; no capital at all tells it "no word here is a name", and on GUM test that is wrong 7,173 times. The twin is still CI-separated BELOW the flip, which is the control doing its job.

**(N3) Lever A is near-null and it was bounded by arithmetic before it was built** (65 of 7,173). Understood, not mysterious: the organ's `position_class` already withholds credit from a forced capital, and the oracle arm shows that withholding is CORRECT.

**(N4) Lever B (read the passage's convention for KNOWN words too) is a CI-separated NEGATIVE on all-tag (-0.0014) and null on PROPN F1 -- and the twin says why.** If the register were noise, the arm would score like its scrambled-symbol twin; instead it beats that twin by +0.0069 PROPN F1 CI-separated. So the passage's convention genuinely carries signal for known words -- and the whole-vocabulary shape row it replaces carries MORE, because a known word already has lexical evidence and a stable, corpus-sized estimate of its shape emission, while the passage-local estimate is accumulated from the organ's own (sometimes wrong) posteriors over a few hundred tokens. **This is the READ-side twin of pri 104's version-1 finding ("it calibrated on its own errors"), and it says the same thing from the other direction: the register belongs where there is nothing better, i.e. on novel forms, which is exactly where the shipped organ already reads it.** The stronger form I did not build -- and would file rather than guess -- re-estimates the known-word offset per passage instead of reusing the offline `ENT_REG_OFFSET`; that is the version worth one more day, in the category organ's lane.

**(N5) The who-did-what AGENT row does not move at all (0.6748 in every arm) and sits far BELOW its positional floor (0.9172).** Not this flip's doing and not new: the modern board's own note records that agent selection on canonical modern prose is near-ceiling for word order, so the Competition-Model agent pick is a register-specific win modern text does not reward. The flip changes the categories, not the word order, and the agent pick is decided by order. **The PATIENT row -- where the decision has to know which token is a nominal at all -- is the one that moves, and it is CI-separated over the twin.**

---

## 9. WHY THE BIG ONE WON -- the chain, rung by rung, and the rungs NOT cracked

The owner's reading is the right one here and unusually literal: **the win is large because the mathematically brain-foundational chain was cracked ALL THE WAY TO THE TOP -- and the top is the PERCEPT, not the first organ.**

| rung | was it already the brain's computation? | what this session did |
|---|---|---|
| **the percept (orthography)** | ❌ the reader deleted half of it before anything read it | **CRACKED**: the surface form reaches the organ; the case-folded key is taken at each lookup, which is where the brain takes it |
| **word-form -> category** (`lexical_categories`) | ✅ already two-route: `_sent_lows` for the lexical emission, `word_shape_rich` x `position_class` for the orthographic factor | nothing needed -- it was correct and starved |
| **the in-order feed** (`feed_passage`, pri 112) | ✅ Heim/DRT: read once, in order, answer as of the sentence | **CRACKED**: its output is now what consumers read (0 duplicate passes, 0 cache misses) |
| **category -> the 25 consumers** | ⚠️ two of them gated on a raw string | **CRACKED**: fold case at the lookup, as the ~110 other case-folds on this path already do |
| **the name decision** (`name_content_tokens` + pri 109's forward wire) | ✅ reads the organ's category, not capitalisation | inherits the whole gain -- name-typed referent mentions x2.5 |
| **heads / roles** (`attachment_arm`, `graded_role_assigner`) | ✅ BF rungs, and they read the category POSTERIOR | inherit a better graded hand-off; the patient row moves, the agent row does not |
| **the pronoun-coref pick** | ✅ BF, and structurally indifferent: its load-bearing cues are CLOSED-CLASS | **NOT cracked, and it does not need to be** -- identical to four decimals, the seventh independent confirmation of pri 109's structural point |
| **the passage's orthographic CONVENTION** (a forced-position capital read against what the passage established) | ❌ the file cards record mention history, not orthography | **NOT cracked** -- prototyped and bounded by arithmetic in §6 |
| **register-conditioned cue reliability** (a transcript that capitalises nothing; a title that capitalises everything) | ❌ the Cap cue's reliability is estimated globally | **NOT cracked** -- §6 and §10; the per-document numbers say this is where the residual lives |

**The single enabling move, stated plainly: I stopped measuring the organ and started measuring THE TAGS THE CONSUMERS ACTUALLY RECEIVE.** pri 109 had the organ-level number (-0.4076 PROPN F1), could not move any board row with it, and concluded -- correctly for its instrument -- that the lever "is nearly invisible". Logging `_cached_tag` showed why: **there are TWO tag streams inside one read** -- the coref mention stream (cased, 0.8651) and the `sents` stream (lowercased, 0.4545) -- and every instrument pointed at this problem was pointed at the first one. The board's own loader feeds the organ cased forms. **The defect lived exactly in the gap between what we measure and what we run.**

---

## 10. ALTERNATE PATHS -- other ways to do this read, similarly or MORE brain-foundational

1. **🥇 HAND DOWN A CODE, NOT A STRING (more brain-foundational than what I shipped).** The brain does not pass "the word" to the next area; it passes a code. The sentence source could return, per token, `(lexical_key, shape_symbol, position_class)` -- the two routes made EXPLICIT -- so no consumer can key a dictionary on the surface form by accident and the two gates I repaired could not have existed. *Why not now:* a signature change across 25 consumers and four call sites, an order of magnitude more edit than the flip; and the flip is a prerequisite either way (there is no shape symbol to hand down while the source lowercases). **Queue as the successor.**
2. **🥈 A PER-PASSAGE, REGISTER-CONDITIONED RELIABILITY FOR THE CAPITAL CUE.** Cue validity in the Competition Model is LEARNED, and it differs by register: GUM's conversation and vlog transcripts capitalise almost nothing and a title capitalises everything -- exactly the documents where the cased arm's PROPN precision is worst, and where the residual sits (§6). The brain-faithful form is the organ's own reliability shrinkage `a = n/(n+theta)` applied to the Cap cue and estimated from the passage so far. **The naive version of this -- simply READING the existing register for known words as well as novel ones -- I built and it is a CI-separated NEGATIVE (-0.0014 all-tag), and N4 says exactly why: the passage-local estimate carries real signal (it beats its scrambled twin by +0.0069 PROPN F1) but less than the corpus-sized whole-vocabulary row it would displace.** So the lead is the STRONGER form, not that one: re-estimate the known-word offset PER PASSAGE (the shipped `ENT_REG_OFFSET` is a single offline constant) so the blend is weighted by how reliable the capital cue is *in this register*, which is what separates a court transcript (PROPN F1 0.98) from a vlog transcript (0.65). *Why not now:* it is a change inside `lexical_categories` (pri 104/112's organ), it needs its own floor and twin on the organ's own instrument, and my remit is the sentence source.
3. **🥉 THE PER-STRING ORTHOGRAPHIC FILE CARD.** Heim's file card extended with what the passage has established about the string's ORTHOGRAPHY, so a forced-position capital is read against the convention the passage itself set. Same organ, same reason to defer -- and §6 bounds it by arithmetic before anyone spends a day on it.
4. **DO NOT READ CASE AT ALL -- decide name-hood in the referent route.** Kripke/Semenza: a name is what picks out an individual, and the ATL decides that, not the word-form area. This is pri 104's entity-feedback prior and pri 109's forward wire, both landed. *Measured verdict: not an alternative, a complement.* The entity prior is worth ~0.01 on repeat mentions (pri 112's numbers); the orthographic cue is worth +0.4106 PROPN F1. A cue with that much availability is not one the brain declines to use.

---

## 11. EVERY COMPONENT I TOUCHED OR INTERACTED WITH, AND ITS BRAIN-FOUNDATIONAL STATUS

| component | role here | BF status | note |
|---|---|---|---|
| `hdlab/scene_segment.parse_conll_sentences` | **the organ under repair** -- the reader's ONE sentence source | registry `BF_SPIRIT`; **this hand-off was NOT_BF**, the diff makes it BF | the word-form system abstracts case for the LEXICAL key only; deleting the percept has no brain analogue |
| `hdlab/situation_reader.read` (`sents`) | the distribution point for 25 organs | BF_SPIRIT | one argument |
| `hdlab/situation_reader._cached_tag` / `_cached_tag_posterior` / `_cached_tag_matrix` | the per-read tag + GRADED posterior memo | BF_SPIRIT | keyed on the raw token tuple -- the reason the in-order feed was unreachable. The flip repairs it without touching the key |
| `hdlab/lexical_categories` (`word_shape_rich`, `position_class`, `_unk_sym`, `_log_shape_factor`, `feed_passage`, `DiscourseRegister`) | the organ that was starved | BF_SPIRIT | **not modified**; its two-route design is already right |
| `hdlab/situation_reader._read_causation` | consumer, **REPAIRED** | BF_SPIRIT (connective structure) | gated on a raw token; 49 of 112 connective sentences lost under the flip before the repair |
| `hdlab/situation_reader._read_timeline` | consumer, **REPAIRED** | BF_SPIRIT | same latent defect (0 of 23 on this sample, but a capital-initial `Had` is a normal English inversion) |
| `hdlab/referent_per_np` (`_content_head_positions`, `frame_heads`, `_mk_referent`) | the entity layer's candidate source | BF_SPIRIT (Kamp/Heim DRT) | flip only; `frame_heads`' documented mid-sentence-CAPITAL cue is alive again |
| `hdlab/coref.name_content_tokens` / `EntityAliaser` | the name decision for 10 organs | BF_SPIRIT | unchanged -- it already defers to the organ's category, which is WHY the `cased_span` arm is a measured no-op |
| `hdlab/space_reader`, `hdlab/causation_typing` | two more call sites of the source | BF_SPIRIT | flip only |
| `hdlab/crosstype_live_adapter` | builds the crosstype Doc from `sents` | BF_SPIRIT | docstring only; it now receives cased tokens and tags them better |
| `experiments/gum_coref.organ_tags` | **the board's loader** | instrument | feeds the organ RAW-CASED forms -- the reason the board cannot see this defect |
| `experiments/exp_crosstype_gum_conll_fullread_v1.gum_to_conll` | GUM -> the reader's own CoNLL | instrument | reused verbatim; it is what makes a MODERN full-read A/B possible at all |

---

## 12. AUDIT UPDATE (`notes/BRAIN_FOUNDATIONAL_AUDIT.md`)

- **`hdlab/scene_segment` -- the entry for `parse_conll_sentences` should say the hand-off, not just the organ.** The module is carried as `BF_SPIRIT`; the sentence source's `lower=True` default made its OUTPUT non-brain-foundational (the percept is destroyed before any organ reads it) and cost the whole substrate 0.4106 PROPN F1 and 0.0280 all-tag accuracy on every reader path. With the diff the hand-off is BF.
- **`hdlab/lexical_categories` -- add the reachability caveat to pri 112's entry.** The in-order feed is brain-foundational and was, as shipped, UNREACHABLE by its own consumers (100% of sentences re-tagged under a different key). "Landed is not live" applies to a cache key as much as to an organ.
- **A NEW GENERAL ENTRY worth carrying: an instrument that constructs its own input can hide a hand-off defect.** The board's GUM loader feeds the category organ raw-cased forms; the live reader fed it lowercased ones. Both are "the organ", and they differ by 0.41 F1. Any board row whose loader builds its own token stream should record WHAT CASE it feeds.

---

## 13. PRIORITY NEXT STEPS (for strategy)

1. **LAND THE DIFF.** Four `lower=False` arguments, two case-folded gates, two docstrings. `git apply --check` CLEAN at HEAD 0b89591f8. It is the largest single measured gain at the top of the chain in the project's current ledger and it is one argument per consumer.
2. **RE-PIN EVERY WITNESS THAT QUOTES A READER-PATH CATEGORY NUMBER.** Re-pinning is strategy's; the old vs new pairs are in §3 and §4 of this file. In particular pri 112's "the feed costs no extra passes" is true only after the flip.
3. **FILE: the board's rows do not run the reader** (§7). Either rebuild the headline rows on `SituationReader.read` over `gum_to_conll` output -- the converter exists and this cell uses it -- or record explicitly, per row, which token stream and which CASE that row feeds the organ.
4. **FILE: hand down a CODE, not a string** (§10 item 1) -- the successor problem for `hdlab/scene_segment`, and the structural fix that makes an accidental case-sensitive gate impossible.
5. **FILE, for the category organ's owner (pri 104/112's lane): register-conditioned reliability for the capital cue** (§6, §10 item 2), with the residual anatomy in §6 as its opening evidence.
6. **A ONE-LINE GUARD WORTH ADDING SOMEWHERE CHEAP:** a test that asserts the reader's per-read tag cache has **zero** entries whose lowercase collides with another entry. That is the whole class of defect ("the organ computed it and the consumer asked under a different key") in one assertion.

---
## 14. THE OWNER'S PUSH SCRIPT, RUN ON MYSELF BEFORE FINALIZING

**(i) How do we perform against the BRAIN at each rung, and where exactly is signal lost?** A competent human reader assigns proper-noun-hood on modern edited prose essentially perfectly on capitalised names, and supervised taggers sit around 0.97-0.98 UPOS. We were at **0.9049 all-tag / 0.4545 PROPN F1 on the reader's path** and are at **0.9328 / 0.8651** after the flip; the organ's own published UD-EWT figure is 0.912 (vs the NOT_BF perceptron's 0.945). **The remaining PROPN loss is 1,239 false negatives and 612 false positives on 127,919 tokens, and it is NOT at the forced position** (65 of the 1,239) -- it is mid-sentence, on registers whose capitalisation convention differs from the offline table's (§6). **Signal is no longer lost at the hand-off; it is limited by the organ's estimate of the cue's reliability in THIS passage.**

**(ii) Research every wall again and PROTOTYPE past it; a prototype that LOCATES the signal is allowed, but a heuristic is not the landed form.** Two prototypes built and measured (§6). Each is explicitly a LOCATOR: the per-string case card's landed form must be a GRADED card (counts of forced/non-forced observations, shrunk `a = n/(n+theta)`, written by the one in-order feed, read as-of the sentence) rather than the hard bit I used; the register-on-known-words arm I built IS the naive form and it is a CI-separated negative, so its landed form is NOT that -- it is a PER-PASSAGE re-estimation of the known-word offset (N4, section 10.2). **Neither prototype is in my diff.**

**(iii) Is the wiring alone sufficient to reach brain level? NO, and here is what else is, with its number.** The wiring takes the reader's categories from 0.4545 to 0.8651 PROPN F1. The remaining ~0.13 is a REPRESENTATIONAL gap, not a wiring one: the capital cue's reliability is estimated once, offline, over a mixed corpus, and then applied to a vlog transcript and a court transcript alike -- per-document `cased` PROPN F1 runs from 0.98 (court) to 0.40 (conversation) on the same organ (§6).

**(iv) The brain never does anything frozen -- every landed table or bias needs an observe path.** My diff lands **no table and no bias** -- it is four arguments and two case-folds, so there is nothing to freeze. The counts it feeds ARE plastic: the passage register (`update_document_register`) and the file cards are written by the one in-order feed on every read and cleared at each passage boundary, and the flip is what gives them a non-degenerate symbol to write (the case symbols were unreachable, §2c). *The flip does not add a frozen thing; it un-freezes an existing online one.*

**(v) Compare each rung with the state of the art on its own metric and name the glass-box lever.** UPOS on modern English: SOTA ~0.98, our count-based generative organ 0.9328 through the reader on GUM test (0.912 published on UD-EWT). The glass-box lever that closes part of the gap is named in (iii) and §10.2 -- per-passage cue reliability -- and it is the Competition Model's own mechanism, not a new one.

**(vi) Audit the negatives for FALSE NEGATIVES.** `cased_span` (N1) is a TRUE no-op with a mechanism I can point at in the source, not a weak implementation; I re-read `name_content_tokens` to confirm the caps route is unreachable when `span_upos` is present and that it lowercases its output regardless. The capcard prototype's near-null (N3) is bounded by ARITHMETIC before the measurement: only 65 of 7,173 gold proper nouns are missed at a forced position, so no implementation of that idea could be worth more than ~0.005 F1. The register-on-known-words arm (N4) is the one I would flag as possibly a weak implementation -- it reuses the organ's shrinkage verbatim but reads the register at the whole-vocabulary row, and a stronger form would re-estimate the offset for known words; that is why it is filed as a lead rather than closed.

**(vii) Look at the prior work on the same rung for wins already banked.** pri 109 found and landed the `lower=` parameter and the four explicit call sites -- this session did not re-derive it, it flipped it and measured what pri 109 could not see. pri 112 landed the in-order feed whose output this flip makes reachable. pri 104 landed the passage register whose SIGN this flip flips. **Three landed pieces of prior work were each worth more after the flip than before it, and none of them needed changing.**

---

## 15. WHAT WOULD TAKE THIS TO A FULL PASS ON EVERY CLAUSE OF THE BAR

The bar's category, entity, consumer and twin clauses are met CI-separated. **The board clause -- "the seven rows reported with CIs (up, down or flat)" -- is satisfied only in the trivial direction, and I would rather say so plainly than bank it:** the rows are FLAT, and they are flat because *none of the seven runs the reader* (§7, sentence-source call count 0 on every row in both arms), so "flat" is a fact about the board and not a measurement of the flip. The bar's word is met; the bar's INTENT -- "did the flip move the board?" -- cannot be answered by this board. To convert THAT clause:

1. **Rebuild the board's `coref` / `common_noun_coref` / `salience` rows on `SituationReader.read`** over `gum_to_conll` output (the converter exists; this cell uses it). Cost: the rows become ~16x slower per document, so they need a document cap and a re-pinned baseline. **Then a case A/B on the board means something.** *This is strategy's call, not mine -- it changes what the board measures.*
2. **Or: record, per board row, WHICH token stream and WHICH case that row feeds the organ** -- a one-line provenance field. Cheaper, and it would have made this defect visible in a grep.
3. The remaining ~0.13 of PROPN F1 is bounded and located (§6): per-passage cue reliability, in the category organ's own lane.

---

## 16. GAPS -- steps not performed, and not worked around

- **I did not run the FULL modern board twice.** I ran the SIX functions that produce the seven headline rows, twice, in one process (section 7), which is the same comparison at a fraction of the cost -- and the call counter makes the zero exact rather than underpowered. The board's other ~20 non-headline arms were not run; one of them (`board_affect_harm_help_dimension`'s live-reader cross-check on one-sentence synthetic CoNLL files) IS on the flip's path and is named for strategy.
- **The full-reader A/B is 16 documents, not 128.** A full `SituationReader.read` is ~30 s per document per arm; 16 x 4 arms was the session's budget. The category rung -- the row the flip is actually about -- IS measured on all 128 (section 3), and the 16-document reader numbers agree with it.
- **I did not touch `verification/`** (scope: section 7 of the brief names my writable files). The 19 bare `parse_conll_sentences(path)` call sites there are listed for strategy, not edited.
- **The two phase-4 levers are PROTOTYPES that locate signal, not landed forms**, and they are in the category organ's lane, not mine. Neither is in my diff.
- **A denial, reported verbatim, mid-session:** a concurrent session reported that a `status: PLACEHOLDER` draft of this file was blocking every commit under `notes/problems/`. My first move was to remove the draft and that was denied -- *"Permission to use Bash with command SL=... && rm -f "$SL/SOLVED.md" && ls "$SL" has been denied."* I did not retry a variant; I filled the file in to a valid status instead, which unblocked them (they confirmed).

---

## SUBMISSION PROMPT

```
Problem: the_reader_lowercases_every_token_at_its_one_sentence_source_so_the_category_organ_misses_70_percent_of_proper_nouns_on_the_live_path_flip_the_case_through_with_a_board_ab   (priority 116)

SOLVED. The reader's one sentence source lowercased every token before any organ saw it. Flipping it
(`lower=False` at the four hdlab call sites) takes the categories the reader's 25 downstream organs
ACTUALLY READ from PROPN F1 0.4545 to 0.8651 and all-tag 0.9049 to 0.9328 on the whole 127,919-token
MODERN GUM test split, +0.4106 CI[+0.3835,+0.4399] and +0.0280 CI[+0.0235,+0.0327], both CI-separated,
measured on the reader's own call sequence. The info-free twin -- each sentence's capital budget permuted
onto random tokens -- scores 0.6292 and loses by +0.2358 CI[+0.2173,+0.2557]; it also BEATS the shipped
reader by +0.1747, i.e. the input we ship is worse than scrambling the capitals at random.

Through the whole live reader on 16 modern GUM documents: PROPN F1 0.4923 -> 0.8544, entity files
2,459 -> 2,563, NAME-typed referent mentions 242 -> 599 (the bar asked for >= 150), who-did-what patient
up (+0.0215 CI-sep over the twin), pronoun coref identical to four decimals.

TWO THINGS THE SESSION FOUND THAT WERE NOT IN THE BRIEF.
(1) pri 112's one in-order feed already reads the passage CASED and caches the settled belief under
    tuple(cased sentence), while every consumer asked with the LOWERCASED tuple -- a different dict key.
    823 of 823 sentences were tagged TWICE per read and the good belief was never the one consumed;
    0 duplicates and 0 cache misses after the flip. The reader computed the right answer and read the
    worse copy.
(2) The board cannot see this defect and never could: experiments/gum_coref.organ_tags feeds the category
    organ the RAW-CASED GUM forms, so the board has been grading the organ at 0.8651 while the reader ran
    it at 0.4545 -- and none of the seven headline rows calls SituationReader.read at all (enumerated, and
    the sentence-source call counter reads 0 for all seven, both arms, in one process).

DELIVERABLE: notes/problems/<slug>/case_through_patch.diff -- four `lower=False` arguments, two case-folded
consumer gates (`_read_causation`, `_read_timeline`; 49 of 112 causal-connective sentences open with a
capitalised connective and stop matching otherwise) and two docstrings. `git apply --check` CLEAN at HEAD
0b89591f8. No hdlab/ or tools/ file was edited; every proposed edit was EXECUTED in the A/B first.

REVERIFY: experiments/exp_case_through_the_reader_v1.py --self-test, then --organ --docs 0 --thetas 100.
```
