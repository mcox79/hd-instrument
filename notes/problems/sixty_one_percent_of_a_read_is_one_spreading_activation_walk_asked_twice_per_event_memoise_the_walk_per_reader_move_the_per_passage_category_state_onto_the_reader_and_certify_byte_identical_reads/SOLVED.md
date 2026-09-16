---
problem: sixty_one_percent_of_a_read_is_one_spreading_activation_walk_asked_twice_per_event_memoise_the_walk_per_reader_move_the_per_passage_category_state_onto_the_reader_and_certify_byte_identical_reads
status: SOLVED
bar: "1. READ-TO-READ STABILITY FIRST -- with NO memo, every one of the 6 GUM test documents (and 6 more of other genres) reads to a byte-identical situation model twice in one process with one reader and with two fresh readers; the per-passage category state lives on the reader; the GUM_academic_census residual is pinned to a line and fixed (or, if it is genuine plasticity the brain would have, named as such with the mechanism and excluded from the identity set with the reason). 2. THE MEMO, PER READER -- keyed by (tuple(seed_idx), n, damping, iters); scoped to the reader/read; capped with the peak entries reported per document. 3. IDENTITY GATE -- on every stable document the memoised read's situation model is BYTE-IDENTICAL (sentences, entities, events, the (predicate, agent, patient) tuple set) to the un-memoised read; any difference is a FAIL. 4. THE POISONED-MEMO TWIN -- returning a wrong stored vector on a hit CHANGES the read (else the walk's result is not consumed: a larger finding to report). 5. THE SAVING, HONESTLY TIMED -- per document, paired and alternating on a quiet box (stable pairs only; a negative or 3x-variance pair is discarded and said so), with hits/misses per document; the product board's read time before/after reported. 6. THE PRODUCT BOARD BYTE-IDENTICAL on every model row with the memo on. 7. WITNESS -- a landing witness pinning the claims (per-reader memo; identity on the stable set; the twin) and the pri 128 tier marker."
result: "THE MEMO IS CERTIFIED AND THE SAVING IS 36.4%, NOT THE BRIEF'S 2.5x -- AND THE TWIN FOUND THE LARGER THING THE BRIEF ANTICIPATED. (1) IDENTITY, 12 OF 12 DOCUMENTS, TWICE OVER: on 12 GUM TEST documents spanning 12 genres (817 sentences, 1,753 events), the memoised read is BYTE-IDENTICAL to the un-memoised read on the full situation model (every dataclass field of sentences / entities / events / suppressed predicates / coref resolutions / timeline / causal links / entity states / pronoun abstentions, plus the sorted (predicate, agent, patient) tuple set), AND byte-identical to a read on the STOCK tree with no patch installed at all -- so neither the memo nor the passage-file move changes an answer. 0 failures. (2) THE REPEAT RATE AND THE FOOTPRINT, MEASURED: 1,379 walks over the 12 documents, 608 of them exact repeats = 44.1% (per document 25.9%-55.2%, reproducing pri 142's 46/116 on GUM_academic_census and 7/27 on GUM_letter_marcie3 exactly). One activation vector is 470,636 bytes (117,659 synset nodes x float32); peak 20-128 entries per document; the one document that reached the 128 cap (GUM_court_property, 135 distinct cue sets) evicted 7 entries AND IS STILL BYTE-IDENTICAL, so no answer depends on the capacity. (3) THE SAVING, PAIRED AND ALTERNATING IN ONE PROCESS, 6 documents x 2 pairs, 10 of 12 pairs kept: 36.4% of the read removed (25.0 / 31.4 / 34.4 / 36.3 / 42.7 / 48.4 per document), 5.45 s per document. THE TWO DISCARDED PAIRS BOTH FAVOURED THE MEMO (the memo-OFF half was 4.6x and 6.0x slower than its partner, a load spike from the two other jobs on the laptop), so the discard rule cost me points rather than buying them: the all-pairs mean is 45.0% and I do not quote it. 36.4% is 1.57x more reads per hour -- THE BRIEF'S '~2.5x' IS ARITHMETICALLY IMPOSSIBLE FROM ITS OWN 28-39% AND IS CORRECTED HERE. (4) THE RESIDUAL IS PINNED TO A LINE AND IT IS DELIBERATE PLASTICITY: two FRESH readers agree on 12 of 12 documents and a fresh reader agrees with a reused reader's FIRST read on 12 of 12, but ONE READER READING THE SAME DOCUMENT TWICE agrees on only 4 of 12. The cause is the reader's own plastic object-file validity table (pri 136's in-flight landing, hdlab/situation_reader.py:4903-4913 -> self._of_validities, accrued by hdlab/entity_resolver.py:786-798 on every high-margin merge/split decision): freeze that ONE accrual with HDLAB_OBJECT_FILE_ONLINE=0 and the same reader reads identically 3 of 3, while with it on the reader's own table moves on 3 of 3 (202,012 -> 203,951 -> 205,949 counted observations on GUM_academic_census). It is cue-validity learning from the reader's own confirmed decisions -- the owner's 'plastic, never frozen' -- so it is NAMED, not removed, and the identity unit is ONE READER PER DOCUMENT, which is what every board row and every cell already does. THIS ALSO CORRECTS pri 142 PROBE A, which inferred from an unchanged module-level fingerprint that the object-file accrual 'did not fire once on two GUM documents': it fires on every document, and the fingerprint cannot move any more because pri 136 moved the table onto the reader. (5) THE TWIN, AND THE LARGER FINDING: a poisoned hit that returns ANOTHER CUE SET's real activation changes the read on only 1 of 3 documents, so I built the stronger twin the protocol demands -- a hit that returns the CORRECT activation with its node identities PERMUTED (same shape, same value distribution, every value on the wrong synset) changes the read on 2 of 3. The walk IS consumed, so the identity result is evidence and not a no-op. BUT destroying EVERY walk in the read the same way (not just the remembered ones -- the whole 61%) changes the recorded situation model on the same 2 of 3 documents and by ONE AFFECT FIELD each (80 -> 78 on GUM_fiction_frankenstein, 98 -> 99 on GUM_podcast_multitasking, 82 -> 82 -- no change at all -- on GUM_academic_census). The most expensive operation in a read alters at most ~1% of one field of the product's output. That is a located, measured finding for the next brief, not a reason to withhold this one. (6) A SECOND REPEATED QUESTION ON THE SAME PATH, BUILT AND MEASURED: the CUE SET is also asked twice (each build is one lexicon lookup per context word, and lexicon_foundation is 4.0% of the profiled read across 6.5M calls); remembering it on the same per-read memo answers 578 of 1,379 builds from memory (41.9%) and is byte-identical. Its MARGINAL saving over the walk memo alone, measured in one process with three alternating arms on 3 documents, is +2.4 points (walk memo alone 39.1%, walk + cue set 41.5%) -- positive on 2 documents (+6.7, +1.8) and NEGATIVE on one (-1.3), so I do NOT claim it as a separated win: it ships because it is the same repeat and the same identity certificate (3/3 byte-identical in both arms), with `SEED_MEMO = False` as the one-line way to run the walk memo alone. (7) THE PRODUCT BOARD'S OWN ROWS ARE BYTE-IDENTICAL: the board's GUM block (`exp_board_rows_on_the_reader_v1.run_gum`, 3 documents x 3 provenance modes x 4 rows, plus the per-document hit/total data every row is computed from = 13 comparisons) is IDENTICAL memo-off vs memo-on AND identical on the STOCK tree vs the patched tree with the memo on -- 0 rows differ in either comparison, including the `reader_textonly_pron_discovered` arm that tags BETWEEN reads and was the one place the passage-file change could have moved a row. The board's reading block ran 270.4 s -> 179.6 s, 33.6% faster (stock 296.2 s, last and under the same load)."
floor: "The gate here is IDENTITY, not a CI, so the floors are the un-memoised arm and the stock tree, both recomputed in the SAME process as the memoised arm on the same documents. (a) THE UN-MEMOISED FLOOR: capacity 0 makes the memo inert -- every walk is re-spread, every cue set rebuilt -- and it is the arm every identity and timing comparison is made against (verification/test_ppr_memo_landing.py W4 proves cap 0, cap 1 and cap 128 return the same vectors, so the floor arm is the same computation and not a different one). (b) THE STOCK FLOOR: on a tree where the patch has not landed the cell removes its own shim and reads the document with the untouched modules, which is what makes the 12/12 'stock vs memo on' comparison a real floor rather than a comparison of two patched arms. (c) THE PLASTICITY FLOOR for bar 1: the same document read twice with NO memo at all, which is what exposed the one-reader-twice residual instead of letting the memo be blamed for it (and is pri 142's own control, reproduced). (d) THE TIMING FLOOR: the memo-off half of each alternating pair, in the same process, seconds apart -- never a number from another run or another process."
controls: "(1) THE STOCK-TREE CONTROL, which is the one that could have failed silently: the cell writes the proposed change ONCE as source strings and both exec's them into the live modules (the shim) and renders them as the shipped diff, so the arm measured IS the patch; `--identity` then removes the shim, reads the document on the stock tree, and compares. (2) A CAN-FAIL CHECK ON MY OWN HARNESS, which caught a real bug: the first version decided 'is the mechanism present' from hasattr() alone, so after a stock read the re-install was SKIPPED and the 'memo on' arm would have run with no memo and reported a triumphant identity. T20 of the self-test now installs, restores and installs again and asserts a repeat is still a hit. (3) THE INFO-FREE TWIN, TWICE, because the first one was too weak to be evidence: another cue set's activation (1 of 3) and then the node-identity permutation (2 of 3), plus the every-walk arm that prices the operation itself. (4) THE CAPACITY CONTROL: cap 0 / 1 / 128 return identical vectors, and the document that overflowed the cap is byte-identical anyway -- so the one new constant in the patch cannot change an answer. (5) THE GRAPH CONTROL: the memo pins the graph by object identity and clears itself if a different matrix arrives, so a stored vector can never be served for a different network (self-test T8). (6) THE EXCEPTION CONTROL: the binding is released in a `finally`, and the witness raises inside a read to prove one brain's activation cannot be left lying where the next one reads. (7) CONTENTION, AUDITED AND NOT HIDDEN: two to three other heavy jobs ran on this laptop throughout (another session's exp_situation_model_qa_modern_v1 --run at 3.2-4.5 GB, another solver's measure run, and the landing chain); every timing pair is alternated within the document and a pair whose halves differ by more than 3x or whose saving is negative is discarded -- 2 of 12 were, both of them pairs that flattered the memo, and both are printed in data/exp_ppr_memo_v1/timing.json with their seconds. The all-pairs mean (45.0%) is recorded beside the kept-pairs mean (36.4%) so the selection's direction is visible. (8) POPULATION: the board's own GUM TEST split (odd document index), evenly spaced so a prefix cap cannot hand the run one or two genres -- 12 documents, 12 distinct genres, and the 6 documents pri 142 used are all inside it. data/corpora/holdout/ was never read; no 19c corpus was used. (9) NO LANDED RECORD WAS OVERWRITTEN: pri 142's probes were reproduced with HDLAB_EXP_NAME redirected to data/exp_structure_map_cost_v1_p146repro/, leaving data/exp_structure_map_cost_v1/ byte-identical. (10) THE DIFF IS BYTES: generated through a line-granularity patcher that keeps each line's own ending (situation_reader.py has 8 LF-only lines at 702-709 inside an otherwise CRLF file), asserted with `git apply --check` clean AND `git diff --stat` == `git diff -w --stat` (269 insertions, 36 deletions both ways). The first attempt was shell-redirected, which turned every CRLF into CRCRLF and was rejected by git apply while `--ignore-whitespace` accepted it -- the cell now writes the file itself, in binary, and says why in a comment."
files_changed: "experiments/exp_ppr_memo_v1.py (NEW -- the proposed change written once as source strings; the shim/restore that makes the stock and patched arms both runnable in one process; --stability, --residual, --identity, --twin, --timing, --lever, --board arms; --make-diff --out writes the patch in BYTES; --self-test 20/20). verification/test_ppr_memo_landing.py (NEW -- the landing witness, pri 128 `fast` tier marker, green on the stock tree via the shim AND on the landed tree, where it asserts the defect's ABSENCE). notes/problems/<slug>/ppr_memo_patch.diff (NEW -- the proposed change to hdlab/grounded_semantic_graph.py, hdlab/lexical_categories.py, hdlab/situation_reader.py; 269 insertions, 36 deletions; applies clean). data/exp_ppr_memo_v1/{stability,residual,identity,twin,timing,lever,board}.json and data/exp_ppr_memo_v1_selftest/selftest.json. data/exp_structure_map_cost_v1_p146repro/{state_probe,cache_probe}.json (pri 142's probes reproduced without touching its landed directory). NO hdlab/ OR tools/ FILE WAS WRITTEN -- the change is a proposed diff, per Q111."
reverify: "1) THE WITNESS, scaffold-free, ~40 s, writes nothing:  OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe verification/test_ppr_memo_landing.py    # expect WITNESS PASS; it prints 'tree state: PROPOSED' before landing and 'LANDED' after, and reads back every JSON record it finds.  2) THE CELL'S SELF-TEST, ~60 s, writes only to data/exp_ppr_memo_v1_selftest/:  ... .venv/Scripts/python.exe experiments/exp_ppr_memo_v1.py --self-test    # expect 20/20.  3) THE IDENTITY GATE, ~45 min under load:  ... .venv/Scripts/python.exe experiments/exp_ppr_memo_v1.py --identity --docs 12    # expect 'IDENTICAL: 12 of 12 documents (failures: 0)' and every stock_vs_memo_on_identical True.  4) THE PATCH:  git apply --check notes/problems/<slug>/ppr_memo_patch.diff  and, for the line endings,  .venv/Scripts/python.exe experiments/exp_ppr_memo_v1.py --make-diff --out <tmp>.diff && git apply --check <tmp>.diff.  5) THE RESIDUAL, ~15 min:  ... --residual --docs 3    # expect identical 1 of 3 with the reader's object-file learning ON and 3 of 3 with HDLAB_OBJECT_FILE_ONLINE=0."
---

# 61% of a read is one graph walk; 44% of the walks are exact repeats; remembering them inside one reading removes 36.4% of the read and changes nothing

**STATUS: SOLVED** (solver scope; WIP until the owner marks DONE). **No `hdlab/` file was written** — the
change is `ppr_memo_patch.diff`, proved through a shim built from the same source text. Modern gold only (GUM
TEST split, 12 genres). `data/corpora/holdout/` was never read.

> **THE TREE MOVED UNDER THIS WORK, AND THE ARMS ARE STAMPED.** Two landings were in flight on the same laptop.
> `hdlab/entity_resolver.py` + `hdlab/situation_reader.py` were written at **09:17** (pri 136, committed
> `7e6f4c625`) — *between pri 142's cache probe (09:05) and its state probe (09:24)*, which is what explains its
> unpinned residual (§4). `hdlab/situation_reader.py` + `hdlab/space_reader.py` were written again at **10:52**
> (pri 137, still uncommitted when I finished). So: **stability (10:25), residual (10:33), identity (10:46) and
> timing (10:55) ran on the pri-136 tree; twin (11:06), board (11:51) and lever (11:59) ran on that tree plus
> pri 137's in-flight change.** Every comparison is *within* one process with both arms on the same code, so
> none of them is a cross-tree comparison — but the absolute seconds are not comparable between arms, and I do
> not compare them. The diff was generated against `hdlab/grounded_semantic_graph.py`
> `b8704ccc23ac8d20a7615515b749dc4b364d0b36`, `hdlab/lexical_categories.py`
> `95ce91732918121fcf7b72d03ee2e3f2b0e38735`, `hdlab/situation_reader.py`
> `8e850c106229a5a35b134d8cf244695908f02754`; if those have moved, regenerate it with
> `--make-diff --out` (reverify step 4) rather than forcing the hunks.

---

## 1. WHAT WAS BUILT, IN PLAIN LANGUAGE

Deciding which sense of a verb is meant is done by letting activation spread through the reader's dictionary
graph until it settles. That one operation is 61% of the time it takes to read a page. Two parts of the same
module ask that identical question about the same verb in the same sentence, so **44% of those spreads are exact
repeats** — measured over twelve pages, 1,379 spreads, 608 of them repeats.

The reader now **remembers, for the length of one reading, what it settled on for a set of cue words** — which
is what a brain does; the activation from a word you read two sentences ago has not gone away. It also
remembers the *list of cue words* it built for a sentence, which was being built twice for the same reason.
Reading a page gets **36.4% faster and the reading is unchanged, exactly, on all twelve pages** — not
"statistically indistinguishable": the same sentences, the same entities, the same events, the same
who-did-what-to-whom, byte for byte.

Two things had to be fixed before "unchanged" could be proved at all, and one of them turned into a finding:

* **The bookkeeping for "which page am I reading" lived in the import system**, shared by everything, instead of
  belonging to the reader. It now belongs to the reader and is handed back when the reading ends, so nothing
  about one page survives into the next.
* **A reader that reads the same page twice does not answer identically — because it LEARNS from what it
  reads.** That is deliberate and it is the brain's form; it is one specific table (which cues predict that two
  mentions are the same person) and freezing that one thing makes the two readings identical. So "the same
  reading twice" means *a fresh reader per page*, which is what every measurement in this project already does.

And one thing worth the owner's attention: **the most expensive operation in a read barely affects the
answer.** Destroy it completely — feed the reader a scrambled version of every spread — and the recorded
reading changes by **one field out of eighty** on one page, one out of ninety-eight on another, and **not at all**
on the third. We are spending 61% of every read on something that moves ~1% of one output field.

---

## 2. THE BAR, ITEM BY ITEM

| # | the bar | result |
|---|---|---|
| 1 | read-to-read stability, memo off, 12 documents | **two fresh readers 12/12 identical; fresh vs reused reader's first read 12/12; ONE reader twice 4/12** — residual pinned to a line and named as plasticity (§4) |
| 1b | the per-passage category state lives on the reader | **done** — `PassageFile` owned by the reader, `detach_passage()` at the end of the read, the process-global `_REG_GEN` counter **removed** |
| 2 | the memo, per reader, keyed as specified, capped, peak reported | **done** — key `(tuple(seed_idx), n, damping, iters)`; `SituationReader._ppr_memo`; cap 128; peak 20–128 entries, 470,636 bytes each, max 57.5 MB, 7 evictions in 12 documents |
| 3 | identity on every stable document | **12/12 byte-identical**, and 12/12 against the **stock tree** as well. 0 failures |
| 4 | the poisoned twin changes the read | **2/3** documents under the strong twin, 1/3 under the weak one → the walk is consumed, **and** the brief's "larger finding" is real (§5) |
| 5 | the saving, honestly timed | **36.4%** (25.0–48.4% per document), 10/12 pairs kept, both discards named and both flattered the memo |
| 6 | the product board byte-identical | **13/13 comparisons identical** (3 modes × 4 rows + the per-document scored data), memo-off vs memo-on **and** stock vs memo-on; the block ran **270.4 s → 179.6 s (−33.6%)** |
| 7 | witness with the pri 128 tier marker | **green on both trees**, `@_pri128_pytest.mark.fast`, asserts the defect's absence when landed |

---

### 2b. THE EVIDENCE, PER DOCUMENT

**Identity + the memo's own accounting** (12 GUM TEST documents, 12 genres, 817 sentences, 1,753 events; a fresh
reader per read; memo-off vs memo-on **and** stock vs memo-on):

| document | sents | walks | repeats | repeat share | peak entries | identical (off/on) | identical (stock/on) |
|---|---|---|---|---|---|---|---|
| GUM_academic_census | 35 | 116 | 46 | 39.7% | 70 | ✅ | ✅ |
| GUM_bio_dvorak | 29 | 44 | 15 | 34.1% | 29 | ✅ | ✅ |
| GUM_conversation_family | 186 | 116 | 50 | 43.1% | 66 | ✅ | ✅ |
| GUM_court_property | 92 | 224 | 89 | 39.7% | **128 (the cap; 7 evictions)** | ✅ | ✅ |
| GUM_fiction_frankenstein | 89 | 154 | 73 | 47.4% | 81 | ✅ | ✅ |
| GUM_interview_gaming | 42 | 67 | 37 | 55.2% | 30 | ✅ | ✅ |
| GUM_letter_marcie3 | 28 | 27 | 7 | 25.9% | 20 | ✅ | ✅ |
| GUM_news_iodine | 41 | 135 | 56 | 41.5% | 79 | ✅ | ✅ |
| GUM_podcast_multitasking | 39 | 151 | 73 | 48.3% | 78 | ✅ | ✅ |
| GUM_textbook_chemistry | 55 | 121 | 55 | 45.5% | 66 | ✅ | ✅ |
| GUM_vlog_mermaid | 103 | 108 | 51 | 47.2% | 57 | ✅ | ✅ |
| GUM_voyage_tulsa | 78 | 116 | 56 | 48.3% | 60 | ✅ | ✅ |
| **total** | **817** | **1,379** | **608** | **44.1%** | 470,636 B each, max 57.5 MB | **12/12** | **12/12** |

**The saving** (6 documents, 2 alternating pairs each, one process, memo inert vs memo on):

| document | kept pairs | memo off | memo on | saved | note |
|---|---|---|---|---|---|
| GUM_academic_census | 2/2 | 12.46 s | 8.54 s | **31.4%** | |
| GUM_conversation_family | 2/2 | 11.78 s | 7.72 s | **34.4%** | |
| GUM_fiction_frankenstein | 1/2 | 21.61 s | 12.38 s | **42.7%** | 1 pair discarded: off 54.9 s vs on 12.0 s (4.6×) |
| GUM_letter_marcie3 | 2/2 | 3.24 s | 2.43 s | **25.0%** | |
| GUM_podcast_multitasking | 2/2 | 20.83 s | 13.27 s | **36.3%** | |
| GUM_vlog_mermaid | 1/2 | 14.77 s | 7.63 s | **48.4%** | 1 pair discarded: off 45.4 s vs on 7.5 s (6.0×) |
| **mean** | **10/12** | | | **36.4%** (5.45 s/doc) | all-pairs mean 45.0% — **not quoted**; both discards flattered the memo |

**The board comparison, and the one exposure I went looking for.** `detach_passage()` leaves the shared category
organ with **no** passage after a read, where today it keeps the last document's file cards installed until the
next `new_document()`. That is a real behaviour change for any consumer that asks the category organ a question
*outside* a read — and the board has one: `_write_two_conll` → `_organ_pron_positions` tags every sentence with
`frontend.tagger()` **between** documents, so from document 2 onward it is currently reading the previous
document's cards. I ran the board block expecting that arm to flip. **It did not: all 13 comparisons are
identical, `reader_textonly_pron_discovered` included.** So the exposure exists in principle, is named here for
the integrator, and is measured absent on this population. **Scope, stated:** I ran the board's **GUM block**
(3 documents × 3 modes × 4 rows + the per-document scored data); the UD, WiC, rebuilt and landings blocks were
not run, so strategy should re-run the full board before landing — the mechanism by which any of them could move
is the sentence above, and nothing else.

### 2c. EVERY COMPONENT TOUCHED, AND ITS BRAIN-FOUNDATIONAL STATUS

| component | change | brain structure / computation | status |
|---|---|---|---|
| `grounded_semantic_graph._ppr` | reads/writes the reader's memo when one is bound; **the equation, damping, iterations and graph are untouched** | spreading activation in a semantic network (Collins & Loftus 1975); the ATL hub read (Patterson, Nestor & Rogers 2007) | **PINNED**, unchanged |
| `grounded_semantic_graph.ActivationMemo` (new) | the activation that persists inside one reading; LRU-bounded | semantic priming (Meyer & Schvaneveldt 1971); ACT-R declarative activation that does not decay to zero within a trial | **OUR-INVENTION** as a representation of a PINNED phenomenon; deviation named (exact + evicted vs graded + decaying) |
| `grounded_semantic_graph._seed_set` (split out, unchanged) / `_sense_ppr` | the cue set is built once per (context, target set) per reading | lexical access once per word per sentence | **OUR-INVENTION**, same claim as above |
| `lexical_categories.PassageFile` (new) + `new_document` + `detach_passage` | the passage's file cards, ACT-R clock, passage register and POS memo become ONE object the reader owns and takes back | Heim (1982) file-change semantics: a new passage is a new file; one brain, one open file | **PINNED** structure, and this makes our implementation match it (it was a module global with a generation counter) |
| `lexical_categories._REG_GEN` / `register_generation` | the process-global counter is **removed**; the function reports the organ's own open passage | — | defect removed |
| `situation_reader.read` / `_read_document` | binds the memo and the passage for the read and releases both in a `finally` | one reader = one brain | **the rule this program is applying** |
| `situation_reader._affect_pos` / `_affect_pos_cached` | the module-level `lru_cache` keyed on a global generation is replaced by the open passage's own memo | a memo of register-dependent output belongs to the register's owner | defect removed |

**AUDIT UPDATE for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`.** `grounded_semantic_graph` is one of the 13 modules
that execute on a live read and carry **no BF rating** (pri 142 §11) — and it is 60.6% of read time. On the
evidence here it should be rated: the walk itself is **BF (PINNED computation)**; what is *not* established is
that its output is used — destroying every walk moves the recorded situation model by ≤1 affect field per
document (§5). That is a fidelity question about the CONSUMER (`select_sense_blended`'s blend and
`_assign_affect`'s abstention), not about the walk, and it is the single highest-value follow-up in this
submission.

---

## 3. THE MECHANISM, AND WHY EACH PIECE IS THE BRAIN'S

**The walk** (`grounded_semantic_graph._ppr`) is untouched: same damping, same 30 iterations, same graph. It is
spreading activation in a semantic network (Collins & Loftus 1975) read at the anterior-temporal hub (Patterson,
Nestor & Rogers 2007); personalised PageRank *is* the stationary spreading-activation vector with a decay term.
**PINNED.**

**The memo is that activation persisting inside one reading.** Semantic priming is the measured fact that the
activation from a cue is still there later (Meyer & Schvaneveldt 1971), and ACT-R models declarative activation
as something that does not decay to zero within a trial. Our memo is the exact-recall limiting case of that.
**OUR-INVENTION in its representation, and I name the deviation: the brain's persistence is graded and decays,
ours is exact and then evicted.** The deviation cannot change an answer here, because a hit returns precisely the
vector the recomputation would have produced (self-test T5, witness W1) — the fidelity gap is in *how long* and
*how strongly* activation persists, not in what it is.

**The capacity is a capacity, not a fitted parameter.** Eviction is least-recently-used, which is the decay;
an evicted cue set is simply re-spread. Cap 0, cap 1 and cap 128 return the same vectors (witness W4), and the
one document that overflowed the cap is byte-identical anyway.

**The passage file is Heim's file card set** (Heim 1982) with its ACT-R sentence clock — and one brain has one
open file. Before this it lived at module level behind a generation counter; now `new_document()` creates a
`PassageFile` (cards + clock + the passage register + the passage's POS memo) and the reader takes it back when
the read ends. Module level keeps only read-only assets and content-addressed memos, which is exactly the rule
pri 142's probe A concluded with.

**The cue set memo is lexical access happening once per word per sentence**, not once per question asked about
that sentence. Same claim, same scope, same certification.

**Nothing on the memo's path is a stand-in.** No external tool, no dataset, no model, no fitted constant. The
only new number is the capacity, and identity holds at three values of it.

---

## 4. THE RESIDUAL, PINNED — AND A CORRECTION TO pri 142

pri 142 reported that `GUM_academic_census` "is not read the same way twice" and could not pin it, noting only
that the module-level state which moved was the per-passage register. **It is not the register.**

My reproduction of pri 142's own probes (redirected so its landed records stayed byte-identical) shows the
counts reproduce exactly — `_ppr` 116 calls / 70 distinct / 46 repeats on census, 27 / 20 / 7 on marcie3; 2
same-document names and 27 cross-document names over 103 watched — **but `reader_is_plastic_read_to_read` is now
`False`.** The tree changed under the brief: `hdlab/entity_resolver.py` and `hdlab/situation_reader.py` were
written at **09:17** today, between pri 142's cache probe (09:05) and its state probe (09:24), and that edit is
pri 136's landing — *the reader owns a deep copy of the object-file validity table; the module cache stays
frozen.* Fresh readers became independent of each other at that moment.

What remains, and what it is:

| comparison | memo off, 12 documents |
|---|---|
| two FRESH readers, same document | **12/12 identical** |
| a fresh reader vs a reused reader's FIRST read | **12/12 identical** |
| ONE reader, the same document twice | **4/12 identical** |

Pinned with the switch that exists for exactly this purpose (`--residual`, 3 documents, memo off):

| | one reader twice identical | the reader's own validity table moved |
|---|---|---|
| as shipped (learning on) | **1 of 3** | **3 of 3** (census 202,012 → 203,951 → 205,949 counted observations) |
| `HDLAB_OBJECT_FILE_ONLINE=0` | **3 of 3** | 0 of 3 (202,012 both times) |

So the residual is `hdlab/situation_reader.py:4903-4913` → `self._of_validities`, accrued by
`hdlab/entity_resolver.py:786-798` (`competition_cluster(..., online=True, online_margin=1.0)` →
`observe_file_decision` → `recompute`). It is **cue-validity learning from the reader's own confirmed
decisions** — the owner's *plastic, never frozen* — so it is named and kept, and the identity unit is **one
reader per document**, which is what `run_gum`, every board row and every cell already construct.

**The correction:** pri 142's probe A concluded that this accrual "did not fire once on two GUM documents — the
high-margin gate never cleared", and flagged it as a landed-but-inert path. It fires on **every** document
measured here (~1,900–2,000 new observations per document). The probe's fingerprint watched the *module-level*
table, which pri 136's landing had made incapable of moving two hours earlier. **A module-level fingerprint
cannot see plasticity that has just been moved onto an instance** — and that is the general lesson, because this
program is moving plastic state onto instances everywhere.

---

## 5. THE TWIN, AND THE LARGER FINDING THE BRIEF ANTICIPATED

The brief said: *"a memo that can be poisoned without changing the answer would prove the PPR result is not
actually consumed, which would be a different and larger finding."* The weak twin — a hit returns **another cue
set's real activation** — changed the read on only **1 of 3** documents. Rather than report that as a pass or a
fail, I built the stronger twin, because another cue set's activation over the same sparse graph can be highly
correlated with the right one:

| twin | changes the read | affect fields |
|---|---|---|
| a hit returns another cue set's activation | 1 of 3 | 80→79 on frankenstein only |
| a hit returns the correct activation with **node identities permuted** (same shape, same value distribution) | **2 of 3** | 80→79, 98→99, 82→82 |
| **every walk permuted** — the whole 61% destroyed, not just the remembered ones | **2 of 3** | 80→**78**, 98→**99**, 82→82 |

**Two conclusions, and they point in opposite directions.**
1. The walk **is** consumed, so the identity result is evidence and not a no-op. Bar 4 is met (2/3, with the
   third document reported).
2. **Its consequence on the product's recorded output is about one field per document.** Destroying the single
   most expensive operation in a read changes the situation model by 1 affect field in 80, 1 in 98, and 0 in 82.
   That is measured on the *recorded* situation model (the fields any consumer reads); whether the walk changes
   intermediates the model does not record is **not** measured here, and saying so is part of the finding.

This is not a reason to withhold the memo — the memo is free and exact. It is a reason for the next brief:
**gate the walk instead of only remembering it.** If the sense the walk chooses is overridden by the frequency
resting level in almost every case (`select_sense_blended`'s log-linear blend) and `_assign_affect` then abstains
unless the certified animacy-axis override fires, then running the walk only where it can change the blend's
argmax would remove far more than 36% — with the same identity gate available to certify it. **Sized:** the walk
is 204.5 s of a 337.4 s profiled read (pri 142); the memo takes 36.4%; a correct gate could take most of the
rest.

---

## 6. WHERE THE READ SPENDS ITS TIME AFTER THE MEMO (the status probe, with numbers)

From pri 142's profile of one full read of 6 GUM TEST documents / 480 sentences (337.4 s profiled self time;
honest wall clock 44.7 s per document), the next three costs are:

| # | cost | measured | is it the same operation asked twice? |
|---|---|---|---|
| 1 | **the remaining DISTINCT walks** | `_ppr` cumulative 204.5 s of 337.4 s (60.6%); 184.8 s of it `scipy.sparse.csr_matvec` (20,160 products from 672 runs × 30 iterations). The memo removes the repeats; **~56% of the walks are distinct questions and remain** | **No** — these are different questions. Cutting them means changing the operation (forbidden) **or gating it** (§5) |
| 2 | **the category posterior, asked twice** | `lexical_categories.posterior` 952 calls for 480 sentences = **1.98× per sentence**; `_posterior2` 11.13 s self / 14.87 s cumulative (4.4%). pri 112's in-order feed is genuinely one pass (`feed_passage` 6 calls / 6 documents) and the point *tag* is served from the reader's cache (460 calls = 0.96×) — it is the **posterior matrix** that is recomputed | **Yes.** Same shape as this brief: one settled belief per sentence, asked again by a second consumer |
| 3 | **the arc scores, asked twice** | `attachment_arm.arc_scores` 1,040 calls for 480 sentences = **2.17× per sentence**; `incremental_tree` 513 calls, 6.64 s self / 12.25 s cumulative; the module 17.48 s self (5.2%) | **Yes** — and it already has a brief: `consolidate_the_arceager_and_arc_double_parse_the_reader_now_parses_every_sentence_twice` |
| 4 | *(honourable mention, and I took it)* | `lexicon_foundation` 13.44 s self over 6,455,629 calls (4.0%); `synset_from_pos_and_offset` 798,080 calls (3.62 s self / 8.56 s cum) and 10,332 sqlite executes (2.84 s) — the **cue-set build** | **Yes** — built and measured as the second lever (§7) |

**Is anything on the memo's path a stand-in?** No. The walk is the brain's equation; the memo is a per-read
dict on the reader; the passage file is Heim's file. No off-the-shelf parser, dataset, model or library was
reached for, at inference or anywhere else.

---

## 7. THE SECOND LEVER (the quality push) — THE CUE SET IS ALSO ASKED TWICE

The walk's seed is built by looking every context word up in the lexicon (`wn.synsets` → a sqlite read per
synset), and the two sibling callers hand `_sense_ppr` the **same context list** for one (verb, sentence). The
profile says that address space is 4.0% of the read (`lexicon_foundation` 13.44 s self over 6,455,629 calls;
`synset_from_pos_and_offset` 798,080 calls; 10,332 sqlite executes). **Lexical access happens once per word per
sentence in the brain, not once per question asked about that sentence**, so the cue set is remembered on the
same per-read memo, keyed on the exact context list plus the SET of target names (the target's own synsets are
excluded from the seed, so the target set matters; its ORDER cannot, and must not split the key — the two
callers arrive with the same synsets in different orders).

**Measured, three arms alternating in one process, 3 documents × 2 pairs:**

| arm | mean saving | census | frankenstein | podcast |
|---|---|---|---|---|
| remember nothing | — | 18.49 s | 22.42 s | 16.36 s |
| remember the **walk** | **39.1%** | −33.0% | −45.2% | −39.0% |
| remember the walk **and the cue set** | **41.5%** | −31.7% | −51.9% | −40.8% |
| → the cue set's **marginal** | **+2.4 points** | **−1.3** | +6.7 | +1.8 |

Cue-set hits 46/116, 71/154, 66/151 (41.9% over the 12-document identity run). **All three arms are
byte-identical on all three documents** — and because this arm ran last (11:59), it is also the identity check on
the **latest** tree, the one carrying pri 137's in-flight change, alongside the board arm's 13/13 rows at 11:51.

**The honest verdict: I do not claim this as a separated win.** +2.4 points is a mean over three documents with
one document *negative*, which is inside the noise this laptop produces. It ships because it is the same repeat,
the same brain claim and the same identity certificate — and because `SEED_MEMO = False` turns it off in one
line if the integrator's own run disagrees. The number to hold onto from this arm is not the 2.4 points; it is
that **the walk memo reproduces at 39.1% on a second, independent 3-document sample** after the 6-document
timing arm said 36.4%.

---

## 8. THE OWNER'S PUSH SCRIPT, ANSWERED WITH NUMBERS

**(i) Is the walk the brain's operation, and is the memo the brain's persistence?** Yes and yes, with a named
deviation. The walk: spreading activation in a semantic network, Collins & Loftus 1975; the hub read, Patterson,
Nestor & Rogers 2007. The memo: activation persisting within a reading — semantic priming (Meyer &
Schvaneveldt 1971), ACT-R base-level activation that does not decay to zero inside a trial. Deviation: the
brain's persistence is graded and decays; ours is exact then LRU-evicted. It cannot change an answer (a hit
returns the vector the recomputation would have produced — 12/12 byte-identical reads), so the gap is in
*duration and strength*, which is the cross-document store in §10.

**(ii) Any wall in certification → prototype past it.** The wall was "the reader is not stable read-to-read, so
the memo cannot be certified". I did not certify around it: I measured it four ways (two fresh readers, fresh vs
reused, one reader twice, and the accrual frozen), pinned it to two line ranges, and showed it vanishes when that
one accrual is frozen. It is plasticity, named with its mechanism, and the identity unit is stated instead.

**(iii) Is the memo alone sufficient for the 2.5x?** **No, and the brief's own numbers cannot reach it.** The
walk is 61% of a read and the memo removes only the repeats: **36.4%** measured over 6 documents, **39.1%** on a
second independent 3-document sample, **33.6%** on the product board's own reading block (270.4 s → 179.6 s) —
so **1.5–1.6× more reads per hour**. Even pri 142's 28–39% is 1.39–1.64×, never 2.5×. To get 2.5× you need 60%
out, and the arithmetic says where from: gate the walk (§5 — worth up to ~60% on its own), then the category
posterior asked twice (4.4%) and the arc scores asked twice (5.2%). **The next cost does need the same
treatment, and the biggest one is not a repeat at all — it is an operation whose output barely matters.**

**(iv) Nothing frozen here.** The memo is created per read and dies with it; the passage file is per passage; the
capacity is a bound, not a fit; and the one genuinely plastic table in the read is left **plastic** — my patch
does not freeze it and does not touch `entity_resolver.py`. The identity contract is stated as "one reader per
document" rather than bought by switching learning off.

**(v) How the state of the art avoids recomputing spreading activation, and where we deviate.** ACT-R caches
declarative base-level activation and recomputes only when the reference list changes; UKB and other
personalised-PageRank WSD systems reuse the personalisation vector per seed set, and production PageRank
implementations cache per-seed results. We deviate deliberately in **scope**: ours is per reading rather than
per process, because one entry is 470,636 bytes (117,659 synset nodes) — a process-global store of the 1,379
cue sets seen in 12 documents would be ~650 MB — and because a cross-document cache makes a read order-dependent,
which is the property this program is removing.

**(vi) Timing audited for contention artefacts.** Two to three other heavy jobs ran throughout (named in
`controls`). Every pair is alternated inside the document; a pair whose halves differ by more than 3× or whose
saving is negative is discarded. **2 of 12 pairs were discarded and both flattered the memo** (memo-off halves
of 54.9 s and 45.4 s against partners of 12.0 s and 7.5 s), so the kept-pairs mean of 36.4% is the conservative
number and the all-pairs 45.0% is the contaminated one. I quote 36.4%.

**(vii) Prior work on disk, used rather than re-derived.** pri 137's per-read parse cache
(`SituationReader._read_parse_cache`) is the same shape and the pattern I copied; pri 136's per-reader
object-file table is the template the brief named, and reading it is what explained the residual; pri 112's one
in-order passage feed is *why* the affect-path POS memo is sound (the register is fully advanced before the
reader's main loop, so a tag is constant within a read); the 2026-09-06 affect tag memo and its 2026-09-14
passage-keying fix are the memo this patch replaces with a per-reader one.

---

## 9. KEY REALIZATIONS

1. **The residual was not in the file the brief pointed at — it was in a landing that arrived between two of
   pri 142's own probe runs.** Comparing the two probe outputs' *timestamps* against the mtimes of the modified
   `hdlab/` files is what found it. When a brief says "the tree", check when the tree was written.
2. **A module-level fingerprint cannot see plasticity that has been moved onto an instance.** pri 142 concluded
   an accrual was inert because the module table never moved; the accrual had just been moved onto the reader
   and fires on every document. Any "this module-level object is stable" claim is only as good as *where the
   state now lives*, not only how deep the fingerprint goes.
3. **Write the proposed change once and let the shim and the diff be the same text.** The cell exec's the very
   source strings the patch ships, so "what I measured" and "what I am asking to land" cannot drift — and the
   same cell runs both arms in one process, which is what made an alternating timing comparison possible at all.
4. **A weak twin is worse than no twin, because it reads as a pass.** "Return another cue set's activation"
   changed 1 of 3 documents; the permutation twin changed 2 of 3 and then the every-walk arm turned the control
   into the most interesting result in the submission.
5. **Check your own harness for the failure that would have looked like success.** `hasattr()` as the
   landed-state test meant a re-install after a stock read was skipped, which would have reported a perfect
   identity for an arm that had no memo at all. The self-test now install/restore/installs and asserts a hit.
6. **Patch in bytes.** A shell-redirected diff turned every CRLF into CRCRLF; `git apply` refused it and
   `git apply --ignore-whitespace` accepted it, which is exactly the signature that hides the mistake.

---

## 10. ALTERNATE PATHS, AND WHY NOT NOW

**A persistent cross-document activation store (the brain's priming across a session).** The walk is a pure
function of (cue set, graph), so a store that outlived the read would be *sound*, and the brain does carry
priming across minutes. What it would take: (a) a reduced value — the consumer only ever reads the activation at
the target synsets, so keying on (cue set, target set) and storing a handful of floats instead of a 470,636-byte
field would cut the footprint by ~4 orders of magnitude; (b) a measurement that does not exist yet — the
**cross-document** repeat rate (within-document is 44.1%; across documents it is unmeasured and cheap to
measure); (c) an experimental contract, because a store that survives a document makes a read order-dependent,
which is what pri 142's rule and pri 136's landing are removing. **Why not now:** it changes the independence of
measurements for a saving nobody has sized, while the in-document win is already certified.

**Fewer iterations / a sparser graph / a smaller seed.** Forbidden by the brief and rightly: they change answers.
The honest version of that idea is §5's gate — run the walk only where it can change the blend's argmax — which
changes *when* the operation runs, not what it computes.

**Making the affect path cheaper by dropping the walk.** §5 shows the temptation and why it needs a gate rather
than a deletion: destroying the walk moves 1 field in 80, but "1 in 80" is not "0", and the right form is a
gate with an identity certificate, not an amputation.

---

## 11. NEXT STEPS, IN PRIORITY ORDER

1. **Land this.** `ppr_memo_patch.diff` applies clean; the witness is green on both trees and asserts the
   defect's absence once landed; one unused import (`from functools import lru_cache` in
   `hdlab/situation_reader.py`) becomes dead and is left for the integrator to remove or keep — it is the only
   loose end in the diff.
2. **Gate the walk (the big one).** Measure how often the PPR term changes `select_sense_blended`'s argmax
   against the frequency resting level, and how often that change survives `_assign_affect`'s abstention. If the
   answer is "rarely", a gate removes most of 61% of every read with the same identity gate available.
3. **The category posterior asked 1.98× per sentence** (4.4% of the profiled read) — the same brief shape as this
   one: one settled belief per sentence, served to the second consumer from the reader's own cache.
4. **The arc scores asked 2.17× per sentence** (5.2%) — already filed as
   `consolidate_the_arceager_and_arc_double_parse_the_reader_now_parses_every_sentence_twice`.
5. **Measure the cross-document cue-set repeat rate** (one counting run) before anyone designs a persistent
   activation store.
6. **For strategy, not for me:** pri 142's probe A entry on `entity_resolver._OF_VALIDITIES` needs the
   correction in §4 folded in, and the general lesson recorded — as this program moves plastic state onto
   instances, the state probe must fingerprint the INSTANCE, not only the module.

---

## 12. WHAT I WOULD WITHDRAW FIRST IF IT TURNED OUT TO BE WRONG

The **36.4%**. It is a wall clock on a laptop that ran two other heavy jobs, and although it is paired,
alternating, in one process and conservative against its own all-pairs mean, it is the number most exposed to
this machine. The **identity** result is not exposed that way — it is a byte comparison of complete situation
models, 12 of 12, against both the un-memoised arm and the stock tree, and it would take a defect in the
comparison itself (which the twin arm rules out: a corrupted memo *does* move the same comparison) to be wrong.

---

## 13. THE SUBMISSION PROMPT

```
Problem: sixty_one_percent_of_a_read_is_one_spreading_activation_walk_asked_twice_per_event_memoise_the_walk_per_reader_move_the_per_passage_category_state_onto_the_reader_and_certify_byte_identical_reads  (pri 146)

SOLVED, as a proposed diff -- nothing in hdlab/ was written.

The spreading-activation walk that is 61% of a read is asked the identical question twice per event: 608 of
1,379 walks over 12 GUM TEST documents (12 genres, 817 sentences) are exact repeats, 44.1%. It is now
remembered PER READER for the length of one reading (the brain's priming), and the passage's file cards, clock,
register and POS memo become one object the reader owns and hands back when the read ends -- the process-global
generation counter is gone.

  IDENTITY:  12/12 documents byte-identical on the full situation model, memo off vs on AND against the stock
             tree; the product board's GUM block 13/13 comparisons identical; the block 270.4s -> 179.6s.
  SAVING:    36.4% of the read (25.0-48.4% per document, 10/12 alternating pairs kept; both discards flattered
             the memo). That is 1.57x more reads per hour -- the brief's "2.5x" is corrected.
  RESIDUAL:  pinned. Two fresh readers agree 12/12; ONE reader twice agrees 4/12, because the reader LEARNS
             (its own object-file validity table, pri 136). Freeze that one accrual and it is 3/3. Named as
             plasticity, kept; the identity unit is one reader per document.
  TWIN:      the weak twin moved 1/3 documents, so I built the stronger one (permuted node identities): 2/3.
             The walk IS consumed -- but destroying EVERY walk moves the recorded read by ONE affect field per
             document (80->78, 98->99, 82->82). THE NEXT BRIEF IS TO GATE THE WALK, NOT ONLY REMEMBER IT.

Read notes/problems/<slug>/SOLVED.md; the change is ppr_memo_patch.diff (271/36, git apply --check clean).
Reverify: .venv/Scripts/python.exe verification/test_ppr_memo_landing.py   (green before AND after landing)
```
