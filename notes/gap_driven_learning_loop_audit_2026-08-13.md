# Gap-driven learning loop: does it work? — audit 2026-08-13

**Question (USER, verbatim):** *"this is what our learning system is supposed to do - whatever we
don't know, build grounded data based on it. Is it not functioning correctly?"*

**Scope of this audit.** Read-only. `os.walk` over `hdlab/` (150 modules excl. `__init__`),
runtime import closures via `sys.modules`, `data/` enumeration (45,376 files / 131 GB), reconcile
to `data/capability_registry.jsonl` (123 rows). No code modified, no experiment run.

---

## VERDICT LETTER: **(c)** — acts only WITHIN an already-chosen corpus, so it can never notice "we have no everyday vocabulary". With **(b)** as the proximate mechanism.

Not (d). The parts exist and self-test PASS. Not (a) alone — an actor exists
(`hdlab/gap_driven_reader.py`, HARD_PASS, commit `7dd02833b`), it is simply never called by
anything that reads real text.

**Plain language:** the system notices *individual words it does not understand*, but only among
words that appear in text a human has already handed it. It has no ability to look at a shelf of
books and pick one. There is no shelf: the list of readable material is a **4-entry Python dict**
with no `simplewiki` key, so reading Simple Wikipedia was not a decision the substrate declined to
make — it was not an option the substrate could represent.

---

## 1. WHAT EXISTS (enumeration first, registry second)

150 modules on disk. All eight candidates named in the brief are REAL, at HEAD, self-tested:

| module | exists | live-imported by the reading path | reaches a text source |
|---|---|---|---|
| `hdlab/gap_detector.py` | yes | **YES** | no |
| `hdlab/gap_driven_reader.py` | yes | **NO** | no (caller supplies docs) |
| `hdlab/reading_grounding_loop.py` | yes | is the entry point | **no** |
| `hdlab/grounding_acquisition_loop.py` | yes | **YES** | no (zero file I/O) |
| `hdlab/three_tier_loop.py` | yes | NO (disjoint closure) | no |
| `hdlab/prelim_tier.py` | yes | NO (via three_tier) | no |
| `hdlab/gather_reason.py` | yes | NO (via three_tier) | no |
| `hdlab/word_acquisition_loop.py` | yes | NO | `corpus_paths` arg only |

### Registry reconciliation
The registry does not contradict this. All six relevant rows say
`integration_status=WIRED, pipeline_status=WIRED_BUT_NOT_PIPELINE_REACHABLE` — including
`gap_driven_reader_self_directed_order` (line 109) and `gap_detector_familiarity_gate` (line 108).
The registry already admits the actor is unreachable. `grounding_acquisition_loop` has **no row at
all** (one of the 62 unregistered modules), yet is live — the registry-first blindness CLAUDE.md
§2 warns about, reproduced.

---

## 2. WIRED-NESS BY RUNTIME, NOT GREP

```
import hdlab.reading_grounding_loop  ->  40 hdlab modules in sys.modules
  includes: gap_detector, grounding_acquisition_loop, hd_fact_store, lexical_similarity, ...
  ABSENT:   gap_driven_reader, three_tier_loop, prelim_tier, gather_reason, word_acquisition_loop

import hdlab.three_tier_loop         ->  41 hdlab modules (15.3 s)
  includes: gather_reason, prelim_tier, kg_traversal, grounding_acquisition_loop
  ABSENT:   reading_grounding_loop, gap_detector, gap_driven_reader
```

**Two disjoint closures.** The reading/grounding organ and the three-tier lookup organ share
`grounding_acquisition_loop` and `hd_fact_store` but **neither imports the other**. This
independently confirms the core claim of `notes/multisource_lookup_wiring_audit_2026-08-13.md`
("the lookup path is concept-level, the reading loop is lemma-level, they do not share a
boundary") — by runtime import closure rather than by grep. That note is **upheld**.

`gap_driven_reader` is imported by exactly one file repo-wide:
`experiments/exp_gap_driven_reader_controlled_v1.py:110`. Nothing in `hdlab/`, nothing in
`tools/`, nothing in `verification/`.

---

## 3. CONTROL FLOW: "the loop notices it lacks knowledge about domain X — what happens next?"

It never notices a **domain**. It notices a **word**, and only a word that is already in front of
it. Line by line:

1. `hdlab/reading_grounding_loop.py:1006` `process_sentence(state, sentence, episode_id, pass_idx, ...)`
   — **the sentence is a parameter.** This module has no `run()`, no `main()`, no corpus loader.
   Its only file opens are frontend assets (`:300-303`, lazy in-function — invisible to grep).
2. `:1050` `for lemma in content_lemmas(sentence):` — **the entire universe of discoverable gaps
   is the set of words in the string just passed in.** A word absent from the chosen corpus can
   never be flagged, by construction. This is the whole finding in one line.
3. `:1068` `if not is_gap(state, lemma): continue` → `:994-1003` `is_gap()` →
   `state.gap_detector.familiarity(lemma, KNOWN_RELATION, KNOWN_OBJECT)`. Real gap signal, memoized
   in `state.gap_cache` (`:955`).
4. `:1075` `ctx = _encode(sentence, lemma)` — the *same sentence* becomes the evidence.
5. `:1078` `flagged = state.library.flag(lemma, episode_id, "POS", ctx, pass_idx, ...)`.
6. **Terminus.** `flag()` appends a trace to an in-memory Library. Later,
   `checkpoint()` (`:1291`) either grounds the item from accumulated same-corpus context, or
   refuses it (`_make_grounding_gate`, `:1102`, appending to `state.refusals`), or escalates it.

**No branch reaches a corpus, a source, or a reading action.** There is no `else: go_read(X)`.
The gap is flagged, attempted against text already in hand, and recorded as a failure.

Confirmed at HEAD **and** in the working tree: `hdlab/reading_grounding_loop.py` is modified
locally, but `git diff -U0` shows the first hunk after line 82 is at **line 1226** — the traced
path (1006-1092) is byte-identical to HEAD.

---

## 4. CORPUS SELECTION — the deciding code, quoted

Repo-wide, **zero** occurrences of `select_corpus`, `choose_corpus`, `next_corpus`, `pick_corpus`,
`corpus_selection`, `corpus_scheduler`. Corpus choice is a hard-coded dict plus a CLI arg:

`experiments/exp_reading_grounding_loop_cycle2_v1.py:132-137`
```python
SEGMENT_POOL_LOADERS = {
    "ele_cont": load_ele_continuation,
    "int_cont": load_int_continuation,
    "adv_new":  load_adv_new,
    "bio_new":  load_biology_sentences,
}
```

`experiments/exp_reading_grounding_loop_cycle3_groundingfix_v1.py:66`
```python
SEGMENTS = ["bootstrap", "ele_cont", "int_cont", "adv_new", "bio_new"]   # cardinality_ok gate
```

`experiments/exp_reading_grounding_loop_cycle3_groundingfix_v1.py:127`
```python
pool = SEGMENT_POOL_LOADERS[segment](limit_sentences)
```
where `segment` comes from `:385 ap.add_argument("--segment", choices=SEGMENTS + [...])`.

**There is no `simplewiki` key.** The entire readable universe of the definitional pipeline is
those four loaders. `data/corpora/` holds 36 entries; the loop can address 4.

The one genuinely gap-conditioned selector, `hdlab/gap_driven_reader.py:192-200`:
```python
def rank_material(state, target_lemma, candidate_docs: Dict[str, Sequence[str]]) -> ...
```
ranks **only what the caller hands it**. Its docstring is explicit: *"the load-bearing
gap-awareness lives entirely in WHICH target_lemma the caller passes in ... this function is
intentionally target-agnostic."* Its only caller builds **4 synthetic f-string templates of
pseudowords per trial** (`exp_gap_driven_reader_controlled_v1.py:213-220`); grep for
`corpus|corpora` in that file returns nothing. It has never seen real text.

Coverage statistics ARE computed in several places (e.g.
`exp_breadth_foundation_active_growth_loop_ud_ewt_v1.py:412`) but every one feeds a pass/fail
verdict. **No coverage statistic anywhere is read by a branch that picks a text source.**

### The sharpest version of the finding
`data/corpora/simplewiki/simplewiki_clean_v1.txt` (251 MB) has been on disk since **2026-07-28**,
and **is already read** — by `experiments/exp_scale_meaning_learn_arc_heldout_v4_breadth.py:180-188`,
a different arc. So this is not "we lacked the corpus" and not "we lacked a loader". Both existed,
in this repo, for 16 days. What is missing is any mechanism that connects *what is missing* to
*what is available*. Likewise commit `7c26d429c` acquired 5 non-biology OpenStax titles that the
loop still cannot address.

---

## 5. ARE GAP RECORDS PERSISTED? Yes — and the blind spot was 65% visible in them.

The `GapDetector` verdict itself is **thrown away**: `FamiliarityResult` is in-memory,
`state.gap_cache` is not serialized by `save_foundation`.

But the reading loop's refusal ledger IS persisted:
`data/foundation/reading_grounding_v2_qualityfix/grounding_refusals.jsonl` — 1.75 MB,
**11,122 records, 3,689 distinct lemmas**. Seven fields, 100% populated:

```
{"lemma":"artwork",     "reason":"TAUTOLOGY_NO_ANCHOR","pass_idx":1,  "segment":"bootstrap","n_exposures":6, "best_cos":0.3849,"candidate_object":null}
{"lemma":"grass",       "reason":"TAUTOLOGY_NO_ANCHOR","pass_idx":41, "segment":"ele_cont", "n_exposures":5, "best_cos":0.3347,"candidate_object":null}
{"lemma":"proposal",    "reason":"TAUTOLOGY_NO_ANCHOR","pass_idx":99, "segment":"adv_new",  "n_exposures":6, "best_cos":0.2659,"candidate_object":null}
{"lemma":"prometaphase","reason":"TAUTOLOGY_NO_ANCHOR","pass_idx":165,"segment":"bio_new",  "n_exposures":9, "best_cos":0.3725,"candidate_object":null}
{"lemma":"cephalochordata","reason":"TAUTOLOGY_NO_ANCHOR","pass_idx":197,"segment":"bio_new","n_exposures":4,"best_cos":0.2633,"candidate_object":null}
```
(30 sampled evenly through the file; the everyday words `artwork / grass / designer / storey /
proposal / toll / squash / tobacco` sit alongside `prometaphase / cephalochordata / saprob`.)

Companion: `library_pending.json` — **10,296 lemmas flagged as gaps that never grounded**.
`manifest.json` growth curve: `cumulative_grounded: 263, cumulative_escalated: 3847,
cumulative_pending: 10296, n_refused_cumulative: 11122`.

**Would the blind spot have been visible?** Partly, and this is the frustrating part:

- The records carry **`segment`**, so a one-line group-by exposes it. I ran it:
  - refusals by segment: `adv_new 3974, bio_new 3010, int_cont 2334, ele_cont 1464, bootstrap 340`
  - and on the positive side, `definitional_facts_v5.jsonl` (2,092 facts, 1,734 distinct terms):
    **`bio_new` = 1,118 distinct terms = 64.5%** of everything the substrate has ever defined.
    (The brief's "1,111 terms" is right to within a dedupe convention; its "*every* definitional
    fact came from biology" is 64.5%, not 100% — worth stating precisely.)
- **Nothing on disk performs that group-by.** `state.refusals` is written
  (`foundation_persistence.py:350`), counted (`:365 "n_refusals"`), and read back (`:386`) — and
  then **never consulted by any decision**. Every other reference in the repo is
  `len(state.refusals)` or a per-pass count.
- There is **no domain field** and **no aggregate record type**. "We have no everyday-vocabulary
  definitions" is a statement about words *never encountered*, and no per-term ledger can express
  it. Only "our definitions are 64.5% one segment" is derivable — and only by a query a human
  writes.

No SQLite/DuckDB gap table exists (34 `trace.duckdb` files, all a single `events` table).

---

## 6. THE SMALLEST CONCRETE CHANGE

### (A) To let the substrate FIND the blind spot itself — ~6 lines, one call site

The data is already collected, already tagged by segment, already persisted, and already reloaded.
The only missing act is the aggregation.

- **Function:** `hdlab/reading_grounding_loop.py::checkpoint()` (line **1291**).
- **Call site:** the growth-curve row it already assembles at lines **1396-1400**, which today
  contains `"n_refused_this_pass"` and `"n_refused_cumulative"`.
- **Missing connection:** add two group-bys to that same dict —
  `Counter(r["segment"] for r in state.refusals)` and the matching
  `grounded_by_segment` over the promoted facts.
- **Why this is sufficient for detection:** that dict is already written into
  `manifest.json`'s `growth_curve_all` by `foundation_persistence.py:350/365` and reloaded at
  `:386`. The number `{bio_new: 1118, ele_cont: 129}` would then be a standing, persisted,
  first-class field that any session-start read or cron surfaces — instead of an ad-hoc query
  nobody thought to run for 16 days. **This is a detector, not a fix**: it makes the imbalance
  loud; it does not make the substrate act on it.

### (B) To let the substrate ACT on it — three connections, one of which does not exist

1. **`CORPUS_REGISTRY: Dict[str, Callable[[], Sequence[str]]]`** enumerating `data/corpora/`.
   **Does not exist anywhere.** ~15 lines. This is the shelf. Without it there is nothing for a
   selector to select *over*, which is why (c) rather than (a) is the verdict.
2. **`rank_material(state, target, candidate_docs)`** (`gap_driven_reader.py:192`) called with
   `candidate_docs` drawn from that registry instead of the synthetic dict in
   `exp_gap_driven_reader_controlled_v1.py:213`. **A call site, not new code** — the function is
   already HARD_PASS.
3. **A driver** binding `state.refusals` / `library_pending` → `next_read_target()`
   (`gap_driven_reader.py:211`) → `rank_material()` → the chosen loader. `reading_grounding_loop`
   has **no top-level driver at all**; the harness in `experiments/` plays that role and its
   schedule is the frozen 5-element `SEGMENTS` list.

Honest scoping: (1) and (3) are genuinely new code, perhaps 60-100 lines total. But note the
economics — the *ranking* organ, the *gap* organ, and the *corpora* all already exist and are
already validated. What is absent is the wiring, and specifically an enumerable corpus registry.
This is the `WIRE-don't-island` gate failing exactly as designed to be caught, on a module the
registry itself already flags `WIRED_BUT_NOT_PIPELINE_REACHABLE`.

---

## 7. TRIPLE-CHECK STATEMENT (CLAUDE.md Evidence §5)

1. **Right file** — cited paths under `D:/AI/hd-instrument/hdlab/` and `experiments/`, not
   `_scratch_*` or same-named neighbours; absolute paths throughout.
2. **Right version** — HEAD `4093464b4`. `hdlab/reading_grounding_loop.py` is locally modified;
   `git diff -U0` confirms the earliest hunk after line 82 is at 1226, so the traced gap path
   (1006-1092) is identical at HEAD and in the tree. Checked for an already-landed fixing commit:
   `git log` on `gap_driven_reader.py` / `gap_detector.py` / `three_tier_loop.py` shows their
   introducing commits (`7dd02833b`, `700e9efe3`, `4249cbfa6`) and **no** subsequent wiring commit.
3. **Right environment** — `.venv/Scripts/python.exe` for every import closure and every JSON read.
4. **Right corpus** — `simplewiki` verified present (251 MB, mtime 2026-07-28) and verified read by
   `exp_scale_meaning_learn_arc_heldout_v4_breadth.py`, i.e. its absence from the definitional
   pipeline is a wiring fact, not an availability fact.
5. **Right metric** — segment shares recomputed from
   `definitional_facts_v5.jsonl` directly (2,092 rows / 1,734 distinct terms), not quoted from a note.
6. **Right arm** — no arm comparison is made in this audit; where I cite a landed verdict I quote
   the `metrics.json` string verbatim.

**What in the brief is wrong on disk.** The brief says Simple Wikipedia "**fixed it**". Coverage,
yes: `data/exp_differentia_feature_supply_v1/metrics.json` records `coverage999=0.350` from
169,982 simplewiki facts. But the same file's verdict is **`HARD_FAIL`**:
`A-B=+0.0068 [-0.1179,0.1395]`, CI includes 0 — *"the DIFFERENTIA adds nothing over the GENUS"*
(commit `9825510bf`). The **coverage** blind spot was fixed; the **downstream benefit** was not
demonstrated. That distinction matters for what gets built next: it means fixing corpus selection
is necessary but is not yet shown to be sufficient.

**Superseded-by check.** `notes/multisource_lookup_wiring_audit_2026-08-13.md` is **UPHELD**, not
stale — its concept-level/lemma-level split is confirmed here by runtime import closure.
