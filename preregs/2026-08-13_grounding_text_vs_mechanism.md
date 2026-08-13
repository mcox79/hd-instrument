# Pre-registration -- GROUNDING READ-OUT: IS THE BINDING CONSTRAINT THE TEXT OR THE MECHANISM?

anchor_name: `grounding_text_vs_mechanism`
cell: `experiments/exp_grounding_text_vs_mechanism.py`
output: `data/exp_grounding_text_vs_mechanism/` (EXPERIMENT-LOCAL ONLY -- growth is paused; no
canonical foundation path is written, nothing is banked)
written: 2026-08-13, BEFORE any run of this cell. Bands below are frozen and are not adjusted
after seeing data.

## 1. WHY THIS CELL EXISTS

Blind hand-score of the GROUNDED_MEANING read-out
(`notes/director_handscore_readout_v1_2026-08-13.md`): 3 MEANINGFUL / 19 RELATED / 78 NOISE over
100 rows. Segment split: OpenStax-Biology rows 9/17 = 52.9% meaningful-or-related vs
OneStopEnglish news 13/81 = 16.0% (Fisher p=0.0024). But 8 of the 9 bio hits were RELATED, not
MEANINGFUL.

Two explanations demand opposite responses:

- **(A) TEXT HYPOTHESIS.** News mentions entities without defining them; dense expository text
  explains them. Remedy: read textbooks.
- **(B) MECHANISM HYPOTHESIS.** The read-out is a similarity / co-occurrence proxy: it returns
  the nearest neighbour in a "what appears near what" space (`whisky->wedding`,
  `checklist->joe`, `banana->people`). On this account better text buys more TOPICAL ADJACENCY
  and never MEANING -- exactly the 8-RELATED-to-1-MEANINGFUL shape observed. The standing
  discipline names this an architectural fault ("similarity-proxy where the brain reasons =
  arch fix").

This cell must be able to come back saying THE MECHANISM IS THE PROBLEM. That outcome is
pre-declared as expected and fully acceptable.

## 2. DESIGN -- ONE VARIABLE: THE CORPUS

Two arms. The ONLY difference is which sentences are read. Mechanism, settings, seeds, reading
order policy, chunk size, base-vocabulary seed and read-out configuration are byte-identical.

| | arm NEWS | arm TEXTBOOK |
|---|---|---|
| source | OneStopEnglish, `data/corpora/onestop/Texts-SeparatedByReadingLevel/{Ele,Int,Adv}-Txt`, all 189 files per level | OpenStax `data/corpora/textbook_{biology_2e,anatomy_physiology_2e,psychology_2e,microbiology,chemistry_2e}/cleaned/*.clean.txt` |
| sentence split | `exp_definitional_grounding_v5._clean_sentences` (same recipe as cycle1 `clean_sentences`) | the SAME `_clean_sentences`, applied PER LINE (v5's F9 line-aware fix, so glossary/paragraph boundaries are not flattened) |
| MEASURED pool | 20,394 sentences (Ele 6,176 / Int 6,810 / Adv 7,408) | 137,029 sentences (bio 30,498 / a&p 27,352 / psych 30,378 / micro 27,251 / chem 21,550) |

**MATCHED N = 20,394 sentences per arm** = the full NEWS pool (the smaller side). NEWS reads
everything; TEXTBOOK is subsampled to exactly the same count.

**Subsampling policy (identical code path in BOTH arms).** Split each arm's pool into contiguous
blocks of 150 sentences (= `CHUNK_SIZE`, so a block never straddles a chunk boundary), select
blocks uniformly without replacement with `random.Random(42)` until the target N is reached,
then restore the original document order and truncate to exactly N. Block sampling (not
per-sentence sampling) preserves local discourse contiguity, which the read-out depends on, and
samples across the whole of every book rather than front matter. For NEWS the selection is a
no-op (target == pool size); the same function still runs.

**Read-out configuration = the CURRENT DEFAULT** (`make_pbv_fns(state)`: readout=None,
freeze_episode=False, i.e. tonight's `PBV_BASE`). F1+F3 are OFF and are NOT varied here --
tonight showed the flags do not move the hand-score, and varying them would add a second
variable.

Shared, identical in both arms: `N_DIM`, `ARM_SEED=4201`, `seed_known_words(load_base_vocab_seed())`,
`CHUNK_SIZE=150`, `checkpoint(..., schema_thresh=SCHEMA_THRESH_FULL, pbv=True,
commit_strength=PBV_COMMIT_STRENGTH)`, `revive_terminal=True`.

## 3. PRIMARY DISCRIMINATOR -- BLIND DIRECTOR HAND-SCORE (bands frozen here)

Instrument: the Director's blind hand-score, n=50 rows per arm, rubric MEANINGFUL / RELATED /
NOISE per `notes/foundation_grounding_sample_2026-08-12.md`. THE CELL ASSIGNS NO BUCKETS AND
CLAIMS NO QUALITY BAND.

Primary statistic: **MEANINGFUL rate on the TEXTBOOK arm.**

- **TEXT_HYPOTHESIS_SUPPORTED** -- MEANINGFUL >= 0.20. A >5x rise over tonight's 2-4% means the
  text was the binding constraint.
- **MIXED** -- MEANINGFUL in [0.10, 0.20).
- **MECHANISM_IS_BINDING** -- MEANINGFUL < 0.10 **AND** RELATED materially above the NEWS arm
  (>= +0.10 absolute). Better text buys topical adjacency but NOT meaning. Pre-declared,
  expected, fully acceptable.
- If MEANINGFUL < 0.10 and RELATED is NOT above NEWS by >= 0.10, the outcome is
  **NULL_NO_TEXT_EFFECT** (the corpus swap moved nothing at all); it licenses no claim about
  which hypothesis is right, only that this manipulation failed to discriminate.

Power: SE of a proportion at n=50, p~0.2 is 0.057; the 0.10-wide bands are at ~1.75 SE. n=50/arm
cannot resolve differences below ~0.10. Declared before the run.

## 3.1 SECONDARY, REPORTED, NOT GATED

RELATED rate per arm and the MEANINGFUL:RELATED ratio per arm. Under (A) the ratio shifts toward
MEANINGFUL; under (B) it stays adjacency-dominated.

## 4. THE CO-OCCURRENCE CONTROL -- THE POINT OF THE CELL

The control that reproduces the result FROM THE WRONG SOURCE. For every row in the blind sample,
compute what a plain sentence-window co-occurrence baseline predicts for that subject, over THAT
ARM'S OWN READ CORPUS (the exact sentence list the substrate saw), and seal it in
`cooccurrence_control.json` keyed by `blind_id`. It is NEVER printed in the scoring sheet.

Baselines (window = one sentence, the same "document" convention as
`hdlab/low_information_filter.build_profile`; candidates are open-class lemmas per
`hdlab/closed_class_lexicon.is_closed_class`, excluding the subject itself; lemmatised with
`hdlab.thematic_role_labeler.lemma_word`):

- `pmi_top1` -- argmax of PMI(subject, w) = log2( c(s,w) * N_sent / (c(s) * c(w)) ) over
  candidates with c(s,w) >= 3. Ties: higher c(s,w), then lexicographic.
- `freq_top1` -- most frequent co-occurring open-class lemma. Ties: lexicographic.
- `pmi_top5`, `freq_top5` -- the corresponding top-5 lists.

Reported per arm: exact-match agreement of the substrate's object with `pmi_top1`, with
`freq_top1`, with either; and top-5 containment. Chance floor: the same agreement recomputed
after permuting the substrate objects across subjects within the arm (`random.Random(42)`).

Pre-registered reading (frozen; reported, does not gate the primary):

- **COOC_REPRODUCES (supports B)** -- either-top1 agreement >= 0.50, or top-5 containment
  >= 0.70, AND at least 0.20 absolute above the permutation floor.
- **COOC_PARTIAL** -- either-top1 in [0.20, 0.50) or top-5 containment in [0.40, 0.70), above
  the floor.
- **COOC_DOES_NOT_EXPLAIN** -- either-top1 < 0.20 and top-5 containment < 0.40, i.e. the
  substrate output is NOT reproducible from plain co-occurrence. This weakens (B) and is the
  outcome that would license looking harder at the text explanation.

If the substrate output largely REPRODUCES the co-occurrence baseline, (B) is supported
REGARDLESS of the hand-score.

## 5. STRUCTURAL GATES (machine-checked by the cell; no quality content)

- **S1 cardinality** -- 2 arm_done units + 2x10 decile progress units present in `units.jsonl`.
- **S2 integrity** -- per arm: 0 tautology facts (subject == object), 0 closed-class objects,
  0 no-leak violations (a base-vocabulary seed lemma appearing as newly grounded).
- **S3 arms-must-differ** -- sha256 over each arm's sorted (subject, object) set differs.
- **S4 matched N** -- both arms read EXACTLY the same number of sentences.
- **S5 yield floor** -- each arm banks >= 50 GROUNDED_MEANING facts (else the 50-row sample is
  not drawable and no hand-score is possible).
- **S6 blind hygiene** -- `SCORING_SHEET.txt` contains no `best_cos`, `schema_score`,
  attestation counter, `fid`, `segment`, arm name or corpus name; exactly one context line per
  row; the renderer never opens `arm_key.json` (asserted structurally: the render function is
  given only the blind rows).

Any S1/S2/S3/S4/S5/S6 failure => verdict HARD_FAIL and the sample is NOT fit to hand-score.
Otherwise verdict = `STRUCTURAL_PASS_PENDING_B3`.

## 6. SAMPLING AND BLINDING

n=100 pooled, 50 per arm, `random.Random(42).sample` over fid-sorted rows (the same convention as
`data/exp_definitional_grounding_v5/b3_audit_sample_DEF_V5.json`), shuffled with
`random.Random(42)`, arm labels stripped into `arm_key.json`. Full per-row provenance (fid,
segment, best_cos, schema_score, counters) is sealed in `blind_provenance_sealed.json`;
`blind_sample.json` and `SCORING_SHEET.txt` carry none of it.

**DECLARED LIMITATION -- THE BLIND IS PARTIAL.** The corpus IS the variable, so the context
sentence printed for scoring reveals the genre. A reader can often infer the arm from the
sentence itself. This cannot be removed without removing the context the rubric needs. What IS
enforced: no arm label, no segment tag, no corpus name, shuffled order, sealed key, and no
metadata that correlates with the arm. The hand-score must therefore be read as
GENRE-VISIBLE-BUT-LABEL-BLIND. This is a real weakness of the primary instrument and is one more
reason the co-occurrence control (sec 4), which is label-free and machine-computed, is the
stronger evidence in this cell.

## 7. DETERMINISM / OPS

`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1` set before numpy import;
`sorted(set(...))` only, never `list(set(...))`; no built-in `hash()`; fixed seeds throughout;
ASCII-only source. Resumable via `tools/exp_checkpoint` `units.jsonl`; resume granularity is
ARM-level (a killed arm re-reads from its first sentence; decile units are a progress ledger).
Writes are confined to `data/exp_grounding_text_vs_mechanism/`. Nothing is banked, nothing is
committed by the cell, no canonical foundation path is touched.

## 8. WHAT THIS CELL CANNOT SETTLE

- It cannot distinguish "textbooks help" from "textbook GENRE STATISTICS help" -- the corpora
  differ in vocabulary, sentence length and repetition as well as in expository density.
- The read-out is noun-only upstream (0 genuine verb definitions in the current foundation), so
  neither arm can produce a verb meaning; a textbook advantage on verbs is untestable here.
- One pass, one seed per arm. No variance estimate across seeds.
- No claim about the canonical foundation: nothing here is banked or wired.
