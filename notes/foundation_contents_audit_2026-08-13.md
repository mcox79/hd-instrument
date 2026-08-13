# Foundation contents audit -- what is ACTUALLY banked on disk (2026-08-13)

READ-ONLY measurement. No code modified, nothing committed. Every number below was recomputed
off disk on 2026-08-13 from the file named beside it; none is recalled or carried over from a
prior note. Scripts were run out-of-tree (temp dir) with `.venv/Scripts/python.exe`; the only
repo file written is this one.

---

## 1. Inventory of banked foundation stores (`data/foundation/`)

`hdlab/foundation_persistence.py` defines the canonical snapshot format: a DIRECTORY containing
`store/store_meta.json` + `store/store_tensors.npz` + `store/store_facts.json`,
`concept_space.npz`, `library_pending.json`, `library_pending_ctx.npz`, `manifest.json`, and
(format_version 2 only) `grounding_provenance.jsonl`, `grounding_refusals.jsonl`,
`evidence_pending.json`. `store/store_facts.json` is the plaintext fact ledger; it is what every
count below is taken from for the HDFactStore-format stores.

Sizes/mtimes from `Get-ChildItem -Recurse` over `D:\AI\hd-instrument\data\foundation`.

### 1a. Real HDFactStore snapshots (6)

| Store dir | Total size | Newest file mtime | fmt | rows in `store/store_facts.json` |
|---|---|---|---|---|
| `reading_grounding_v1` | 19.33 MB | 2026-08-12 09:46:32 | 1 | **7966** |
| `reading_grounding_v2_qualityfix` | 20.75 MB | 2026-08-12 13:55:04 | 2 | **2146** |
| `reading_grounding_v1_smoke` | 3.42 MB | 2026-08-12 01:50:42 | 1 | 1264 |
| `reading_grounding_v2_qualityfix_smoke` | 4.61 MB | 2026-08-12 13:27:28 | 2 | 1300 |
| `reading_grounding_v1_post_bootstrap_control_copy` | 6.11 MB | 2026-08-12 01:54:24 | 1 | 1248 |
| `reading_grounding_v1_smoke_post_bootstrap_control_copy` | 2.05 MB | 2026-08-12 01:49:44 | 1 | 894 |

### 1b. NOT foundation snapshots -- bare JSONL from the definitional extractor (3)

These three directories are named like foundation snapshots but contain **no `store/`, no
`manifest.json`, no vectors**. They were never loaded into an HDFactStore and are not reloadable
by `foundation_persistence.load_foundation`.

| Dir | File | Size | mtime | rows |
|---|---|---|---|---|
| `reading_grounding_v3_definitional` | `definitional_facts.jsonl` | 0.97 MB | 2026-08-12 14:35:06 | 1751 |
| `reading_grounding_v4_parsefix` | `definitional_facts_v4.jsonl` | 1.74 MB | 2026-08-12 15:56:32 | 1956 |
| `reading_grounding_v5_termboundary` | `definitional_facts_v5.jsonl` | 1.14 MB | 2026-08-12 16:30:12 | **2092** |

(`reading_grounding_v3_definitional/grounding_provenance.jsonl.json` is a 46-byte stub reading
`{"note": "see definitional_facts.jsonl"}`.)

### 1c. `data/foundation_snapshots/` -- two snapshots, both byte-identical to v1 full

sha256 of `store/store_facts.json`, first 16 hex chars:

- `reading_grounding_v1_full_20260812T142513Z` -> 7966 rows, `00aa8f1ac2c7c178`
- `reading_grounding_v1_smoke_20260812T135041Z` -> **7966 rows**, `00aa8f1ac2c7c178`
- `data/foundation/reading_grounding_v1` -> 7966 rows, `00aa8f1ac2c7c178`

**Finding: the snapshot labelled `_smoke_` is NOT the smoke store.** The live smoke store has
1264 rows; this snapshot has 7966 and hashes identical to the full store. Both "snapshots" are
the same bytes. The label is wrong; anyone treating `..._smoke_...` as an independent smoke
artifact would be reading the full store.

---

## 2. Relation breakdown -- ALL facts, primary store

Source: `data/foundation/reading_grounding_v1/store/store_facts.json` (7966 rows).

| relation | count | share of rows |
|---|---|---|
| `KNOWN_WORD` | **4422** | 55.51% |
| `GROUNDED_MEANING` | **3544** | 44.49% |

There are **no other relation values**. All 7966 rows have `status = ACTIVE`
(`manifest.json`: `n_facts = 7966`, `n_live_facts = 7966`) -- nothing was ever superseded,
flagged, or replaced.

Same breakdown for `reading_grounding_v2_qualityfix/store/store_facts.json` (2146 rows):
`KNOWN_WORD` 1512, `GROUNDED_MEANING` 634, all ACTIVE.

`GROUNDED_MEANING` by `source` field, v1: `reading:adv_new` 1337, `reading:int_cont` 840,
`reading:bio_new` 598, `reading:ele_cont` 584, `reading:bootstrap` 185. All 3544 carry
`trust_sym = TRUST_MID`.

---

## 3. Tautology verdict: **CONFIRMED at 65.69%**

Counted on the 3544 `GROUNDED_MEANING` rows of
`data/foundation/reading_grounding_v1/store/store_facts.json`.

Three normalizations were computed; **all three give the identical count**, so the number is not
an artifact of normalization choice:

| normalization | tautologies (`subject == obj`) | % of 3544 |
|---|---|---|
| exact string | 2328 | 65.69% |
| `.lower()` | 2328 | 65.69% |
| `hdlab.thematic_role_labeler.lemma_verb(.lower())` | 2328 | 65.69% |

(They agree because the store already writes lowercased, suffix-stripped lemmas on both sides.)

**Verdict: the recalled 65.7% figure is CORRECT.** 2328/3544 = 0.65688 = 65.69%. Not stale, not
wrong. These rows are `(X, GROUNDED_MEANING, X)` and assert nothing.

Tautologies by segment: `reading:adv_new` 864, `reading:int_cont` 636, `reading:ele_cont` 399,
`reading:bio_new` 305, `reading:bootstrap` 124.

**`reading_grounding_v2_qualityfix` has 0 tautologies out of 634** grounded facts. The v2
quality fix eliminated this class completely -- at the cost of grounded-concept count dropping
3544 -> 634 (and note only 1216 of the 3544 were ever non-tautological, so the real comparison is
1216 -> 634).

---

## 4. Non-tautological grounded facts, and objects-per-subject

Primary store `reading_grounding_v1`:

- **Non-tautological grounded facts: 1216** (3544 - 2328), 34.31% of grounded facts,
  15.27% of all 7966 rows.
- Distinct subjects among all 3544 grounded facts: **3544** -- exactly 1:1.
- Distinct subjects among the 1216 cross-grounded facts: **1216** -- also 1:1.

**Objects-per-subject distribution (non-tautological facts):**

| distinct objects per subject | subjects |
|---|---|
| 1 | **1216** |
| 2 | 0 |
| 3+ | 0 |

max fan-out = 1. Same in `reading_grounding_v2_qualityfix`: 634 subjects, all fan-out 1.

**This is a structural consequence, not evidence about the world.** `GROUNDED_MEANING` is
declared `FUNCTIONAL` cardinality in the store config (see `reading_grounding_loop.py`
`relation_cardinality={KNOWN_RELATION: "FUNCTIONAL", MEANING_RELATION: "FUNCTIONAL"}`), and the
loop grounds each lemma exactly once (`n_live_facts == n_facts`, zero REPLACE/FLAG statuses on
disk). **The store is architecturally incapable of holding two meanings for one word**, so the
"multiple conflicting meanings per word" signal the task asked about CANNOT be read from this
store. Its absence carries no information.

By contrast, the definitional-extractor JSONL *can* hold multiple objects per subject and does:
`definitional_facts_v5.jsonl` -- 1713 distinct subjects over 2092 rows, fan-out 1: 1416,
fan-out 2: 232, fan-out 3+: 65, max 6.

---

## 5. Noise LOWER BOUND (no hand-scoring)

Method, applied to the **1216 non-tautological** grounded facts of `reading_grounding_v1`:

1. **Closed-class / function-word objects** -- `hdlab.closed_class_lexicon.is_closed_class`,
   as it exists on the live path (UD-EWT majority-UPOS functional class UNION spaCy English
   stop words, plus `lemma_verb` normalization).
2. **Proper-noun objects** -- corpus-derived, not hand-listed, mirroring criterion (i) of the
   closed-class lexicon. A lemma is PROPER iff the MAJORITY of its **non-sentence-initial**
   occurrences in the corpora the loop actually read are capitalized. Corpus = 568 files:
   `data/corpora/onestop/Texts-SeparatedByReadingLevel/{Ele,Int,Adv}-Txt/*.txt` plus
   `data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt`. Lemmas were
   normalized with the same `lemma_verb` the loop uses. Lemmas with <2 informative occurrences
   are UNKNOWN and are **NOT** counted as noise.

| bucket (of 1216 cross-grounded facts, v1) | count | % of 1216 | % of 3544 |
|---|---|---|---|
| closed-class object | 119 | 9.79% | 3.36% |
| proper-noun object | 265 | 21.79% | 7.48% |
| **NOISE LOWER BOUND (union)** | **384** | **31.58%** | **10.84%** |
| neither (unclassified) | 821 | 67.52% | -- |
| UNKNOWN (too rare to classify) | 11 | 0.90% | -- |

Closed-class SUBJECTS: 13 (a further defect class, not added to the bound above).

Most frequent closed-class objects: `also` (31), `say` (15), `like` (5), `more` (5), `most` (5),
`see` (4), `us` (3), `my` (3), `our` (3), `make` (3), `take` (3).
Most frequent proper-noun objects: `holdcroft` (3), `nero` (3), `dubna` (3), `mendel` (3),
`kenyan` (2), `oberg` (2), `christine` (2), `gps` (2), `caribbean` (2), `helena` (2),
`marshall` (2), `belem` (2), `riken` (2), `nobel` (2), `lanka` (2).

**This 31.58% is a LOWER BOUND on noise, not a quality score.** It counts only facts whose object
is provably in a category that cannot be a word's meaning. It says NOTHING about the 821
"neither" facts -- those contain both genuine hits (`auction -> house`) and open-class garbage
(`billionair -> end`, `domain -> top`, `artwork -> himself`) that this method cannot separate
without hand-scoring. It also does not count stemmer artifacts: e.g. `cal` (26 occurrences as an
object in v2) is `lemma_verb("called")`, a non-word, and is classified as neither closed-class
nor proper by the criterion. The true noise fraction is higher than 31.58%; how much higher is
not measured here.

If the tautologies are folded back in, then of all 3544 grounded facts, at minimum
2328 + 384 = **2712 (76.52%)** are demonstrably contentless or wrong-category.

Same measurement on `reading_grounding_v2_qualityfix` (634 grounded, all cross-grounded):
closed-class objects **0**, proper-noun objects **54**, unknown 3, noise lower bound **54 =
8.52%**. Both the tautology band and the closed-class band were closed by the v2 fix; the
proper-noun band was NOT.

Same measurement on `definitional_facts_v5.jsonl` (2092 rows): closed-class objects **0**,
proper-noun objects **88**, unknown 150, noise lower bound **88 = 4.21%**.

---

## 6. Provenance: definitional extractor vs reading/grounding loop

**They cannot be confused, because they were never mixed -- they live in different files, and
the definitional extractor's output was never banked into any HDFactStore at all.**

- `FactRecord` on disk (`store_facts.json`) has exactly these fields:
  `fid, subject, relation, obj, source, trust_sym, trust_level, status`.
- The `source` field values present across ALL SIX HDFactStore snapshots in `data/foundation/`
  are, without exception: `seed_base_vocabulary`, `reading:bootstrap`, `reading:ele_cont`,
  `reading:int_cont`, `reading:adv_new`, `reading:bio_new`. The `reading:` prefix is written by
  `reading_grounding_loop.commit_grounding` (`f"reading:{source_tag}"`).
- **Therefore 100% of the 3544 GROUNDED_MEANING facts in `reading_grounding_v1`, and 100% of the
  634 in v2_qualityfix, came from the READING/GROUNDING loop. Zero came from the definitional
  extractor.**
- The definitional extractor's 1751 / 1956 / 2092 facts (v3/v4/v5) exist ONLY as bare JSONL in
  `reading_grounding_v{3,4,5}_*`. They have their own richer schema
  (`pattern`, `patterns_seen`, `n_attestations`, `pmi`, `source_sentences`,
  `definiendum_surface`, `definiens_surface`, `subject_type`, `subject_head_lemma`) and carry
  per-fact provenance the HDFactStore schema has no column for.

**The important caveat: `source` records the CORPUS SEGMENT, not the PIPELINE.** If definitional
facts were ever banked into an HDFactStore they would land with a `source` string in the same
namespace, and after banking the two pipelines would be indistinguishable unless the writer chose
a distinguishing tag by convention. There is no schema-level pipeline field and no enforcement.
Today the separation holds only because the extractor output was never banked.

v5 pattern distribution (`definitional_facts_v5.jsonl`, 2092 rows): COPULA 648, GLOSSARY_COLON
519, APPOSITIVE 495, CALLED 422, REFERS_TO 8. `subject_type`: COMMON 1763, PROPER 329.
Segments: bio_new 1371, bootstrap 281, adv_new 167, int_cont 141, ele_cont 132.
(v3 has no `subject_type` field at all -- 1751/1751 null.)

---

## 7. Marker rows -- `KNOWN_WORD` / `CORE`

In `reading_grounding_v1/store/store_facts.json`:

- **4422 `KNOWN_WORD` rows**, each with `obj` literally the string **`CORE`**
  (4422/4422 -- one distinct object value), 4422 distinct subjects.
- Source breakdown: `reading:adv_new` 1337, `reading:int_cont` 840, `reading:bio_new` 598,
  `reading:ele_cont` 584, `reading:bootstrap` 185, `seed_base_vocabulary` **878**.
- There is no separate `CORE` *relation*; `CORE` is the object of every `KNOWN_WORD` row.

**So "7966 facts" = 4422 vocabulary markers + 3544 meaning assertions.** The markers are pure
bookkeeping (they tell the gate "this word is known"); they assert no content and should never
be counted in a "facts" or "knowledge" total. 878 of them are the pre-loaded seed vocabulary, so
only 3544 were minted by reading.

v2_qualityfix: 1512 `KNOWN_WORD`/`CORE` rows (878 seed + 634 from reading), 634
`GROUNDED_MEANING`.

---

## Headline restatement, primary store `data/foundation/reading_grounding_v1/`

| quantity | value |
|---|---|
| rows in `store/store_facts.json` | 7966 |
| `KNOWN_WORD`/`CORE` marker rows | 4422 (878 seed + 3544 from reading) |
| `GROUNDED_MEANING` facts | 3544 |
| ...of which tautological `(X,GM,X)` | 2328 = 65.69% (recalled 65.7% CONFIRMED) |
| ...of which non-tautological | 1216 = 34.31% |
| ...of the 1216, closed-class object | 119 |
| ...of the 1216, proper-noun object | 265 |
| ...noise LOWER BOUND on the 1216 | 384 = 31.58% |
| grounded facts with >1 object | 0 (structurally impossible: FUNCTIONAL cardinality) |
| facts from the definitional extractor | 0 |

---

## What I could NOT verify

- **Whether any of the 821 "neither" facts are actually meaningful.** The closed-class + proper-
  noun screen is a category filter, not a quality judgement. Hand inspection of the first rows
  shows both plausible (`auction -> house`) and plainly wrong (`artwork -> himself`,
  `billionair -> end`, `domain -> top`, `sale -> real`) entries in that bucket. Separating them
  requires hand-scoring, which was out of scope here. The 31.58% figure must never be reported
  as "68% good".
- **The true proper-noun rate.** My PROPER criterion is corpus-derived from the 568 files listed
  above with a simple regex tokenizer and a `(?<=[.!?])\s+|\n+` sentence split; it is not a
  parser. It will miss proper nouns that appear mostly sentence-initially, and it cannot judge
  the 11 (v1) / 3 (v2) / 150 (v5) lemmas with <2 informative occurrences. It is deliberately
  conservative so that the resulting number stays a lower bound.
- **Whether the corpus set I scanned exactly matches what the loop read.** I inferred the corpus
  files from `experiments/exp_reading_grounding_loop_cycle2_v1.py` loaders (OneStop
  Ele/Int/Adv + `concepts_biology.clean.txt`) and scanned all of them, whereas the run used
  file-index slices (`ELE_N_FILES`, `INT_SLICE`) and per-segment sentence caps. Scanning a
  superset only makes the capitalization statistics better-estimated, but I did not reproduce
  the exact slices.
- **Stemmer damage.** `lemma_verb` is a suffix stripper that returns non-words
  (`called -> cal`, `arteries -> arteri`, `billionaire -> billionair`, `duplicate -> duplicat`,
  `macrophage -> macrophag`). Many subjects and objects on disk are these non-words. I did not
  quantify how many facts are corrupted this way; it is a separate defect class and it is NOT
  included in the noise lower bound.
- **`concept_space.npz` / `library_pending.*` contents.** Not opened. This audit covers the
  fact ledgers only. The manifests report 8130 pending library items in v1 and 10296 in v2,
  read off `manifest.json`, but I did not verify those against the files.
- **Semantic correctness of the definitional-extractor facts.** The v5 hand-score
  (64% meaningful, `notes/director_handscore_b3_v5_termboundary_2026-08-12.md`) is a prior
  result I did not recompute; the only v5 numbers above are the row/pattern/fan-out/noise counts
  I measured today.
- **Whether other HDFactStore snapshots exist outside `data/foundation/` and
  `data/foundation_snapshots/`.** A recursive search for `store_facts.json` under `data/`
  returned exactly the 8 paths reported here (6 foundation + 2 snapshots), but stores in other
  serialization formats, if any, would not have been found by that search.
