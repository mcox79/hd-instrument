# Pre-reg: exp_foundation_validation_harness_v4_proximity_v1

## Why (third instrument-repair attempt -- a different mechanism, not a re-tune)

`exp_foundation_validation_harness_v3_tightened_v1` (metrics:
`data/exp_foundation_validation_harness_v3_tightened_v1/metrics.json`) fixed the diagnosed
short-prefix-over-match bug (`freq_pick` flips `com` -> `people`, `freq_rate` 0.96 -> 0.8267,
matching an independent manual recompute to 4 decimals) but **failed its own pre-registered
decisive gate**: the random-decoy arm `chance_hat` moved only 0.7667 -> 0.76 (statistically flat),
nowhere near the pre-registered `<=0.15` near-chance ceiling. v3's own pre-reg named the correct
escalation on this exact outcome and forbade the alternative: *"a genuinely different mechanism
(proximity window / dependency-aware check), proposed as a v4, not a parameter sweep on v3's
coverage threshold."* `MIN_STEM_COVERAGE` is NOT retuned here; it is imported unchanged from v3.

## Diagnosis of the remaining defect (new evidence gathered before writing this fix)

v3's own report already names the mechanism: `cooccurs_v3` still treats "some sentence, out of
30889, contains a covering match for both words, anywhere in it" as co-occurrence. Two additional
pieces of evidence, gathered from the SAME frozen snapshot's corpus loading before writing any new
code (`scratch/_probe_corpus_sentence_length_stats.py`, `scratch/_probe_corpus_long_sentences.py`,
both throwaway probes, not durable):

1. **Sentence length distribution** (30889 sentences, `V1.CORPUS_SOURCES_FULL`, same tokenizer as
   v3): mean 22.7 tokens, **median 18 tokens**, p25=12, p75=25, p90=33. Most sentences are short
   enough that "anywhere in the sentence" is not obviously permissive on its own -- the defect is
   sharper than sentence length alone explains.
2. **A previously-unnoticed corpus-loading confound**: one entry in `base_vocabulary_glob`
   (`data/corpora/base_vocabulary/cleaned/...`) is a CSV word-frequency table (`word,freq_rank,
   subtlex_freq_pm,subtlex_count,aoa_years,ogden_850,dolch_level,dolch_rank`, alphabetically
   sorted, ~74286 rows) with no sentence-terminal punctuation, so `_split_sentences` never breaks
   it -- it loads as **one single "sentence" of 74660 tokens**, confirmed by direct inspection
   (`sentences[30881]`, preview and tail both show CSV rows). Under same-sentence-anywhere
   (v1/v2/v3's `cooccurs`), this one degenerate pseudo-sentence alone is enough to make almost any
   two moderately common English words "co-occur" for free, independent of prefix handling --
   because the table's rows are close to exhaustive English vocabulary. This is corroborated,
   not fixed: this pre-reg does not modify corpus loading or exclude the row (out of scope per the
   v3 pre-reg's "everything else unchanged, reused by import"); it explains why the defect is a
   corpus-membership artifact and motivates the mechanism chosen below, which suppresses it as a
   structural side effect rather than requiring a separate patch.

## Fix: proximity window (chosen over dependency-parse)

**Chosen mechanism: PROXIMITY WINDOW.** Two matched tokens (one covering-matching the lemma, one
covering-matching the other candidate, `_prefix_covers` reused unchanged from v3 at
`MIN_STEM_COVERAGE=0.6`) must occur within `PROXIMITY_WINDOW` tokens of each other in the SAME
sentence -- not merely anywhere in it.

**Why proximity over dependency-parse, stated before building either:** `pos_tagger` /
`arc_parser` / `arc_labeler` exist on the live path (`hdlab/pos_tagger.py`,
`hdlab/arc_parser.py`, `hdlab/arc_labeler.py`) and were considered. Proximity is chosen for three
reasons, all checkable before commitment: (a) it directly targets BOTH diagnosed defects above --
a tight window structurally suppresses the degenerate 74660-token pseudo-sentence for free (two
words alphabetically far apart in a CSV table will almost never land within a few tokens of each
other, whereas same-sentence-anywhere counts them as co-occurring with certainty), without needing
a separate corpus-loading patch; (b) it is a strict tightening of the SAME primitive already
self-tested and landed in v3 (`_prefix_covers`), so it carries over v3's self-tests unchanged
rather than introducing a new, unvalidated scoring dependency; (c) proven runtime budget -- v3's
full run (150 samples x 4 arms, 30889 sentences) completed in 181s; a dependency parse of 30889
sentences is untested at this scale and would add a second unvalidated instrument (the parser's
own accuracy on this corpus is unmeasured) on top of the one already being repaired. If v4 also
fails its gate, dependency-parse becomes the next-in-line v5 candidate with its own pre-reg.

**`PROXIMITY_WINDOW` value, derived from a corpus structural statistic BEFORE running any
`cooccurs_v4` computation against the real store (same discipline as `MIN_STEM_COVERAGE=0.6`,
fixed from a worked example, not fit to the outcome):**

For two uniformly-random token positions in a sentence of length `n`, the expected absolute
distance is `E[|i-j|] = (n^2-1)/(3n) ~= n/3` for the range `[1,n]`. Using the corpus's OWN median
sentence length (18 tokens, a structural corpus statistic, not the `chance_hat` outcome):
`18/3 = 6`. **`PROXIMITY_WINDOW = 6` tokens.** Interpretation: two matches closer together than the
distance expected from two independently-placed random tokens in a typical sentence indicate
non-arbitrary proximity (the two words are plausibly in the same clause); two matches at or beyond
that expected-random distance are not distinguishable from chance co-membership. This is computed
once, from a fixed corpus-structural number (median sentence length), and is not swept, tuned
against `chance_hat`, or revisited after seeing the real-store result.

```
def cooccurs_v4(lemma, other, tokenized_sentences, window=PROXIMITY_WINDOW):
    for tokens in tokenized_sentences:
        lemma_pos = [i for i, t in enumerate(tokens) if _prefix_covers(lemma, t)]
        if not lemma_pos:
            continue
        other_pos = [j for j, t in enumerate(tokens) if _prefix_covers(other, t)]
        if not other_pos:
            continue
        if any(abs(i - j) <= window for i in lemma_pos for j in other_pos):
            return True
    return False
```

`prefix_count_v3` (the frequency-floor ranker) is reused UNCHANGED by import from v3 -- it counts
corpus-wide token frequency, not co-occurrence, and is not implicated by the proximity defect.
`_prefix_covers` and `MIN_STEM_COVERAGE=0.6` are reused UNCHANGED by import from v3
(wire-don't-island; the v3 fix demonstrably worked on the frequency arm and is not being
re-litigated here).

## Self-tests (formula correctness, BEFORE any real-store run)

1. `_prefix_covers` worked examples: reused verbatim from v3 (imported, not reimplemented) --
   `com`/`comes`=True, `com`/`company`=False, `villag`/`village`=True, etc.
2. **Window boundary, the case this fix is built on**: a constructed sentence where lemma-match
   and other-match are exactly 6 tokens apart must return True (`>=`-equivalent, boundary
   inclusive); exactly 7 tokens apart must return False.
3. **Genuine-relation case** (positive control): "the champion agent negotiated the historic
   treaty" -- `champ`/`agent` at distance 1 -- must return True under `cooccurs_v4`.
4. **Same-sentence-but-far case, the specific discriminating case this v4 exists to fix**:
   construct a single long sentence (>40 tokens) with the lemma-match near the start and an
   unrelated other-match near the end (distance > `PROXIMITY_WINDOW`). Assert `cooccurs_v3`
   (v3, imported) returns True on this pair (same-sentence-anywhere) AND `cooccurs_v4` returns
   False on the identical pair -- the direct before/after proof that the new mechanism changes the
   verdict on the exact defect class diagnosed above.
5. **Degenerate-pseudo-sentence regression check**: construct a synthetic long comma-separated
   "CSV-row" style pseudo-sentence (mimicking the real `base_vocabulary` defect, alphabetically
   ordered unrelated tokens) containing both a lemma-match and an unrelated other-match far apart
   in token position; `cooccurs_v4` must return False on it while `cooccurs_v3` returns True --
   demonstrates the mechanism suppresses the diagnosed corpus-loading confound without touching
   corpus loading.
6. Known-answer arm (production `n_dim=2048`) reused unchanged from v2/v3 -- must still be
   `accuracy=1.0, instrument_valid=True` (mandatory instrument gate, unaffected by this change).

## The decisive gate -- declared BEFORE running against the real store (UNCHANGED from v3)

Same gate, same threshold, not retuned: **`chance_hat <= 0.15`.**

- If `chance_hat > 0.15`: **INSTRUMENT_STILL_LOOSE**, reported explicitly. This would be the THIRD
  consecutive failure of the same validity gate across three different mechanisms
  (same-sentence-anywhere-unnormalized -> same-sentence-anywhere-coverage-normalized ->
  proximity-window-coverage-normalized). Per the task's explicit framing, three failures in a row
  is itself the finding: this claim-1 correctness question needs a structurally different
  construction (dependency-aware relation extraction, most likely) rather than any further
  tightening of a co-occurrence-style check, and must be reported plainly as such -- not softened,
  not re-tuned, no claim-1 number asserted from any version of this harness.
- If `chance_hat <= 0.15`: proceed to read claim 1's ordinary bands (unchanged since v1): `gap =
  precision_hat - floor_max`; `HARD_PASS` iff `gap >= 0.20` AND `wilson_precision_lo >
  wilson_floor_hi`; `HARD_FAIL` iff `gap < 0.05`; else `MIDDLE_BAND`. `floor_max =
  max(chance_hat, ortho_rate, freq_rate)`, all three recomputed under `cooccurs_v4` /
  `prefix_count_v3` (frequency ranker unchanged from v3).

## Stated expectation (honest prediction, committed before running)

I expect `chance_hat` to drop substantially below v3's 0.76, for two structural reasons that do
not depend on the specific data: (a) the degenerate 74660-token pseudo-sentence, which alone was
capable of manufacturing free co-occurrence for large numbers of common-word pairs under
same-sentence-anywhere, is structurally defused by a 6-token window (two alphabetically-distant
words are essentially never within 6 tokens of each other in that table); (b) even in ordinary
sentences (median 18 tokens), a random unrelated word pair is only "close" (<=6 tokens) some
fraction of the time, not with the near-certainty same-sentence-anywhere implies. I do NOT have
confidence it lands under 0.15 in one step -- some genuinely adjacent-in-text but semantically
unrelated word pairs will still pass (common function-word-mediated proximity, e.g. "X and Y" or
list constructions), and the store's `decoy` pool is drawn from only 334 distinct grounded-meaning
objects, which may co-occur closely with a given lemma via definitional-sentence structure even
when unrelated to THIS specific lemma's meaning. If the gate still fails, that is reported as the
third consecutive INSTRUMENT_STILL_LOOSE, honestly, per the task's explicit falsifier instruction.

## Scope / non-goals

- Claims 2 and 3 are NOT recomputed -- read back from v2's landed `metrics.json` unchanged, exactly
  as v3 did (they do not use `cooccurs`/`prefix_count`).
- `MIN_STEM_COVERAGE=0.6` and `prefix_count_v3` are NOT retuned or reimplemented -- imported
  unchanged from v3 (wire-don't-island).
- Frozen snapshot reused UNCHANGED: `data/foundation_snapshots/reading_grounding_v2q_full_
  20260815T182838Z/`. No new freeze, no write into `data/foundation/`.
- `SEED=20260815` carried over unchanged (same 150-pair sample as v2/v3, same decoy/ortho draws,
  for an apples-to-apples comparison across all three versions).
- Corpus loading itself (the CSV-blob pseudo-sentence defect) is NOT patched here -- noted as
  diagnostic evidence motivating the mechanism choice, not as a fix target. If a future pass wants
  to fix corpus ingestion, that is a separate pre-reg.
