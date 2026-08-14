# PRE-REG -- exp_context_conditioned_near_neighbour_v1

Filed 2026-08-13, **COMMITTED BEFORE THE CELL RUNS AND BEFORE ANY ARM IS SCORED**.
Author: hdi_exp_dev. Cell: `experiments/exp_context_conditioned_near_neighbour_v1.py`.
Parent evidence: `notes/brain_drill_encoder_lexical_semantics_2026-08-13.md` (element **E4**,
the SEMANTIC CONTROL GAP), `notes/lit_scan_semantic_control_near_neighbour_2026-08-13.md`,
`data/exp_near_vs_far_diagnostic_v1/metrics.json`, `notes/context_vector_signal_v1_2026-08-12.md`.

`hdlab/` IS NOT MODIFIED BY THIS CELL. It is read and called.

---

## 1. Why this cell exists, and why it is NOT another SimLex cell

Four cells have now tested CONTEXT-FREE word-pair similarity and all four failed:

| cell | primary rho | source |
|---|---|---|
| distinctiveness weighting | null | MEASURED@data/exp_distinctiveness_weighted_composition_v1/metrics.json |
| differentia supply (A) | 0.0247 | MEASURED@data/exp_differentia_feature_supply_v1/metrics.json:rho_primary.A |
| genus supply (B) | 0.0179 | MEASURED@same:rho_primary.B |
| scramble floor (E) | -0.0235 | MEASURED@same:rho_primary.E |
| grounded sensorimotor (C), pooled | 0.2759 | MEASURED@same:rho_primary.C |
| grounded sensorimotor (C), FAR half | 0.3042 | MEASURED@data/exp_near_vs_far_diagnostic_v1/metrics.json |
| grounded sensorimotor (C), NEAR half | 0.1245, CI includes 0 | MEASURED@same |

The one channel that carried anything degrades **monotonically as pairs get closer** and is at
null on strict WordNet siblings/synonyms -- exactly the distinction the substrate needs.

**SimLex-999 is NOT used as the primary here, and that is deliberate.** SimLex is a CONTEXT-FREE
benchmark: a pair of words with a single scalar rating and no sentence. Running it again would
repeat the framing error this cell exists to correct. Per the drill's element E4, the brain's
semantic control system (IFG/pMTG) does not select from a candidate list -- it applies GAIN,
dynamically boosting whichever feature dimension the CURRENT CONTEXT requires (Chiou & Lambon
Ralph 2018, *Cortex*, DCM; F(2,34)=3.86, p=.03). **The brain never computes context-free word-word
similarity.** Our `concept_similarity(a, b)` is a bare two-argument function with no context port:
a POSITION gap, not a shape gap.

Separately, `notes/context_vector_signal_v1_2026-08-12.md` established that our per-encounter
context vector carries REAL measured signal (flip-rate D = +0.2155, 95% CI [+0.1982, +0.2332],
replicated at two scales against three independent nulls) and that **all of that signal lives in
argmax IDENTITY, none in the cosine magnitude**. We compute genuine context and then discard it at
the comparison step.

**HYPOTHESIS:** context-conditioning creates near-neighbour discrimination that context-free
comparison provably cannot.

---

## 2. Task -- NEAR-NEIGHBOUR DISAMBIGUATION IN CONTEXT

Given a real corpus sentence with the target word MASKED, and two near-neighbour candidates (the
true word and a distractor), choose the correct one. **Chance is 0.50 by construction**, so the
discriminator has RANGE BY CONSTRUCTION and cannot be floor-pinned -- the defect that made two
earlier cells undecidable.

### 2.1 Item construction (deterministic; MASTER_SEED = 20260813)

Corpus: `data/corpora/simplewiki/simplewiki_clean_v1.txt` (2,779,032 lines,
`data/corpora/simplewiki/stats.json`, CC BY-SA, dump 2026-07-02).

1. **Pass 1** -- token counts over the whole corpus (regex `[a-z']+` on the lowercased line).
2. **Vocabulary** `V` = tokens with count >= `MIN_WORD_COUNT` (300), `isalpha()`, `len > 3`,
   `wn.morphy(w,'n') == w` (BASE FORM ONLY -- this is what keeps `ability`/`abilities` out),
   and having >= 1 WordNet noun synset.
3. **STRICT near-neighbour groups.** For each `w in V` take `s0 = wn.synsets(w,'n')[0]`, the
   DOMINANT noun sense. Group words by (a) `s0.name()` -- same synset = SYNONYMS; (b) each
   `h in s0.hypernyms()` -- shared DIRECT hypernym = SIBLINGS / co-hyponyms. Groups of size
   2..`MAX_GROUP` (40). This is the predecessor's S1 NEAR criterion (N1 synonym OR N2 direct
   co-hyponym), **tightened to the dominant sense of both words** so a distractor cannot be
   "near" only through an obscure sense. The LOOSE all-synsets variant (the predecessor's literal
   criterion) is computed and reported as a SECONDARY read.
4. Pairs = all within-group combinations, **excluding** any pair where the two words share a
   `normalize_lemma` or where one is a morphological variant of the other (sec 2.3).
5. **Pass 2** -- for each word in a surviving pair, collect up to `K_SENT` (100) corpus sentences
   with 8..40 tokens in which the word occurs EXACTLY ONCE.
6. **HELD-OUT SPLIT.** Each word's 100 sentences are shuffled with a `hashlib.sha256(word)`-derived
   seed (never builtin `hash()`, PROT-023/F.5); the first `N_PROFILE` (70) build that word's
   ANCHOR and the remaining 30 form its EVAL pool. **The two pools are disjoint by construction**
   -- no sentence that builds an anchor is ever scored, and vice versa.
7. For each pair `(a,b)` in sorted order and each direction `(target, distractor)`, the FIRST
   leak-surviving eval sentence of `target` becomes an item. Constraints: each eval SENTENCE is
   used at most once globally; each target word contributes at most `MAX_ITEMS_PER_WORD` (4)
   items. Items are then truncated to `MAX_ITEMS` in sorted item-id order.

Sampling is NATURAL, not force-balanced: which direction of a pair yields an item depends on
sentence availability. The realised balance is reported so the FREQUENCY arm is interpretable.

### 2.2 WordNet asset
WordNet 3.0 via nltk (`%APPDATA%/nltk_data/corpora/wordnet.zip`). **`data/wordnet_cache/` is EMPTY
on disk** -- confirmed; the predecessor's nltk access path is reused. `wn.get_version()` is
recorded in metrics.

### 2.3 LEAK CONTROLS (run BEFORE the measurement; reported regardless of outcome)
A token `t` is a MORPHOLOGICAL VARIANT of word `w` iff `t == w`, or
`normalize_lemma(t) == normalize_lemma(w)`, or (`t.startswith(w)` and `len(t)-len(w) <= 3`), or
(`w.startswith(t)` and `len(w)-len(t) <= 3` and `len(t) >= 4`). Deliberately over-inclusive: a
leak control should over-remove.

- **L1** the sentence must not contain the target word or any morphological variant ANYWHERE other
  than the single masked slot;
- **L2** the sentence must not contain the distractor or any morphological variant anywhere;
- **L3** after masking, >= `MIN_CONTEXT_WORDS` (4) distinct content lemmas must remain.

Per-check removal counts are reported in `metrics.json:leak_controls`.

---

## 3. ARMS

| # | arm | what it sees | mechanism |
|---|---|---|---|
| 1 | `CONTEXT_CONDITIONED` (treatment) | THIS sentence's masked context | argmax over the two candidate anchors, via the substrate's OWN read-out |
| 2 | `CONTEXT_FREE` (critical control) | the SAME sentence's content words, but compared CONTEXT-FREE | argmax of mean `concept_similarity(candidate, w)` over the sentence's content lemmas |
| 3 | `CONTEXT_SCRAMBLED` (floor) | a DIFFERENT item's real sentence | identical to arm 1, different query |
| 4 | `FREQUENCY` | corpus counts only | pick the corpus-more-frequent candidate |
| 5 | `CHANCE` | nothing | 0.50, stated |

### 3.1 ORGAN REUSE -- exactly which functions (standing rule: a mechanism that shares an
already-built process REUSES that organ; it does not build a parallel one)

Arms 1 and 3 are built from these, imported and called UNMODIFIED:

- `hdlab.reading_grounding_loop.context_vector_masked(sentence, target_lemma)` -- the no-leak
  masked context encoder, used VERBATIM to build every anchor.
- `hdlab.reading_grounding_loop.ConceptSpace` + `.observe()` -- the substrate's own running
  per-lemma context accumulator. An anchor for word `w` is exactly what the reading loop builds:
  the accumulated sum of `context_vector_masked` over `w`'s own encounters, sign-bundled by
  `ConceptSpace.anchor_matrix()`.
- `hdlab.reading_grounding_loop.canonicalize_fast(new_lemma, query, space, thresh, eligible_mask)`
  -- the substrate's own read-out. `eligible_mask` is a PRE-EXISTING parameter of that function;
  restricting it to the two candidates is the intended use, not a modification. `thresh = -1.0`
  makes the read-out a pure argmax (accept always), which is the channel the context-vector cell
  measured to carry ALL the lemma-specific signal.
- `hdlab.reading_grounding_loop.normalize_lemma` / `content_lemmas`; and
  `hdlab.grounding_acquisition_loop.content_words` / `context_vector` transitively.

The ONE new function in the cell is `_ctx_masked_multi(sentence, lemmas)` -- context_vector_masked
generalised to mask a SET of lemmas, needed because the query must be symmetric with respect to
BOTH candidates (an asymmetric query would leak the answer). **Self-test S4 asserts it is
BYTE-IDENTICAL to `hdlab.context_vector_masked` when the set has one element**, which is what makes
it a reuse rather than a re-implementation.

Arm 2 calls `hdlab.lexical_similarity.concept_similarity(a, b, use_grounded_fallback=True)` -- the
current live context-free path (CONCEPT_FEATURES, falling back to
`hdlab.grounded_similarity.grounded_similarity`, capped at `GROUNDED_CAP = 0.45`).

### 3.2 Why arm 2 is the right control (the one-variable isolation)
Arm 2 is given the SAME sentence and the SAME candidates. The ONLY thing removed is
context-CONDITIONING: every comparison arm 2 makes is a static, context-blind word-word similarity,
pooled. This is a STRONGER control than "no sentence at all" (which would degenerate into a prior
and duplicate arm 4). By construction the two candidates are dominant-sense near-neighbours, so
their context-free similarity to any third word is near-identical -- which is precisely why a
context-free method cannot win here, and precisely what makes arm 1 - arm 2 the load-bearing delta.

### 3.3 Arm 3 is the control that matters most
Arm 3 uses a REAL sentence from a DIFFERENT item, with that item's candidates AND this item's
candidates both masked out. Donor assignment is a deterministic derangement over sorted item ids
(offset `n//2 + 1`, advanced while the donor shares a candidate). If arm 1 beats arm 3, the gain is
from THIS context, not from having any context at all.

---

## 4. BANDS -- PRE-DECLARED, COMMITTED BEFORE RUNNING, NOT ADJUSTED AFTER SEEING NUMBERS

Let `a1..a4` be arm accuracies on the SAME items.

- **HARD_PASS** (all four): `a1-a2 >= +0.10` AND `a1-a3 >= +0.08` AND `a1-a4 >= +0.05`, each with a
  paired-bootstrap 95% CI on the DELTA excluding 0, AND `a1` significantly above 0.50
  (bootstrap CI on `a1-0.50` excluding 0).
- **CONTEXT_IS_THE_MISSING_PIECE** (weaker but real): `a1-a2 >= +0.05` with CI excluding 0,
  AND `a1 > a3`.
- **HARD_FAIL** (either): CI on `a1-a2` includes 0 (context adds nothing), OR `a1 <= a3`
  (any context works as well as the right one -> the gain is an artifact).
- Anything else: **MIDDLE_BAND**.
- Per META_RULE_L, a delta clearing its floor by < 5% of the floor is reported as MIDDLE_BAND, not
  HARD_PASS (`STRICT_MARGIN = 0.05 * floor`).

HARD_FAIL is evaluated FIRST and dominates: an artifact verdict cannot be overwritten by a pass.

`HP_SCOPE`: the four HARD_PASS gates apply to arm 1 ONLY. Arms 2/3/4 are controls and inherit no
pass gate. Arm 5 (CHANCE) is a stated constant with no gate.

### 4.1 Power (declared before the run)
n >= `MIN_ITEMS` = 200 is a HARD gate: **if fewer than 200 clean items can be built the cell STOPS
and reports the count rather than running underpowered** (`verdict = INSUFFICIENT_ITEMS_NO_READ`).
That gate has correctly stopped two cells this week.

`crlb_floor_computed`: for a paired binary comparison the delta's standard error is
`sqrt(p_disc)/sqrt(n)` where `p_disc` is the discordance rate; the reported
`mde_95 = 1.96 * bootstrap_sd(delta)`. `crlb_formula_reference`: McNemar/paired-binomial
`se(delta) = sqrt((b + c))/n`, equivalently `sqrt(p_disc/n)` for the difference of paired
proportions. At the pessimistic `p_disc = 0.50` and n = 200, `mde_95 = 0.098`; at n = 4000,
`mde_95 = 0.022`. `discriminator_reachability = True` (the +0.10 HARD_PASS delta is above the
n=200 floor and far above the n=4000 floor). The accuracy ceiling is 1.0 and arm 2 is expected at
~0.50, so `a1 >= 0.60` is required -- reachable, not capacity-capped.

Bootstrap: >= 5000 paired resamples, fixed seed `BOOTSTRAP_SEED = 20260813`, percentile CIs, all
arms recomputed on the SAME resampled index set (the arms score the same items). A CLUSTER
bootstrap resampling TARGET WORDS (not items) is reported as a disclosed secondary, because a
target word can contribute up to 4 items.

---

## 5. Compute architecture
`(b) sequential-CPU with justification`. Total work: two streaming passes over a 251 MB text file
(~30 s measured), ~2,700 anchor accumulations of 70 x 256-dim bipolar bundles, and <= 4000 argmax
read-outs over a 2-row masked slice. Estimated wall < 10 min end to end; a GPU would be pure
overhead. Thread pins `OMP_NUM_THREADS` / `OPENBLAS_NUM_THREADS` / `MKL_NUM_THREADS = 1` are set at
the TOP of the file BEFORE numpy is imported (never as an inline shell env prefix).
Storage strategy: `sharded` -- each candidate word has its OWN anchor vector; nothing is bundled
across concepts. `no_composition` (single-hop read-out).

## 6. SCHEMA-VET fields
```yaml
cardinality_ok: true                  # EXPECTED_N_UNITS = 4 scored arms x n_items
sweep_alignment_verdict: ALIGNED      # no sweep axis; n_items is the only scale axis
discriminating_fraction: 1.00         # chance is 0.50 by construction; 0/1 saturation impossible
composition_edges:
  - from: context_vector_masked
    to: ConceptSpace.observe
    A_natural_output_shape: bipolar (256,) sign vector
    B_natural_input_shape: (d,) float accumulator increment
    verdict: SHAPE_MATCH
  - from: ConceptSpace.anchor_matrix
    to: canonicalize_fast
    A_natural_output_shape: (n_anchors, 256) sign matrix + sorted anchor list
    B_natural_input_shape: exactly that (canonicalize_fast reads space.anchor_matrix())
    verdict: SHAPE_MATCH
positive_control_arms:
  - arm: CTX_MASKED_MULTI_REPRODUCES_HDLAB
    primitive: hdlab.reading_grounding_loop.context_vector_masked
    tolerance: 0.0                    # byte-identical required
    if_outside_tolerance: BLOCK_DISPATCH (the cell has forked the organ)
  - arm: SELF_RETRIEVAL_SANITY
    description: an anchor scored against a HELD-IN profile sentence of its own word must beat a
      random other anchor well above chance; if the anchor space cannot even retrieve itself the
      harness is broken, not the hypothesis.
    floor: 0.70
    if_below: BLOCK_DISPATCH (INSTRUMENTATION_SUSPECT)
functional_requirements:
  - req: represent a word by the contexts it occurs in
    primitive: ConceptSpace + context_vector_masked (reading_grounding_loop)
  - req: condition a comparison on the current context
    primitive: canonicalize_fast query vector (this is the E4 port that did not exist for word pairs)
  - req: restrict the comparison to two candidates
    primitive: canonicalize_fast eligible_mask (pre-existing parameter)
  - req: a context-free comparator to isolate against
    primitive: lexical_similarity.concept_similarity (unmodified)
real_code_path_exercised: [context_vector_masked, ConceptSpace, canonicalize_fast, concept_similarity, grounded_similarity]
substrate_signature_checked: [context_vector_masked, canonicalize_fast, ConceptSpace.observe, concept_similarity]
guard_baseline_validated: [ARM3_NOT_AT_FLOOR]   # arm 3 is a REAL sentence, expected NEAR 0.50, not
                                                # structurally 0; the a1<=a3 guard is checked
                                                # against arm 3's own measured value, not a floor
deterministic_seeding: true           # hashlib + fixed ints only; no builtin hash(), no list(set())
arms_differ_verified: true            # sha256 over each arm's per-item choice vector; all distinct
final_metrics_atomicity: tmp_replace  # SMOKE writes to SEPARATE directories
calibration_check: default_ok_for_this_regime   # no tuned constant sits between context and verdict;
                                                # thresh=-1.0 disables the only threshold in the path
baseline_in_band: true                # arm 2 predicted ~0.50, inside (0.05, 0.95)
cell_chunked: false                   # single deterministic run, no seed axis
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
progress_logging: print_flush_true
```

## 7. Smoke gate (multi-scale; n_items is the load-bearing axis)
SMOKE at `n_items = 150` AND `n_items = 600` (4x), to SEPARATE output directories. Smoke must show:
(a) >= 1 item built at each scale and the leak controls each reporting a count;
(b) the four arms bit-DIFFERENT (META_RULE_AF);
(c) arm 2 in (0.05, 0.95) (META_RULE_AG);
(d) the SELF_RETRIEVAL_SANITY positive control >= 0.70;
(e) no arm all-constant and no arm at a sentinel.
A smoke that shows all-zero / all-constant metrics, 0 valid items, or a <100 ms exit is
`INSTRUMENTATION_SUSPECT` and is NOT shipped.

## 8. What each outcome means
- **HARD_PASS** -> the E4 POSITION gap is real and closable: adding a context port to the
  comparator buys near-neighbour discrimination that no context-free comparator can reach. The
  build target moves to wiring a context port into the comparator.
- **CONTEXT_IS_THE_MISSING_PIECE** -> same direction, smaller magnitude; worth building, not worth
  claiming.
- **HARD_FAIL via `a1-a2` CI including 0** -> context-conditioning is NOT the lever at this
  read-out; E4 is refuted for this mechanism and the next drill goes elsewhere (E1/E2 supply, or a
  richer context encoder than a bag-of-content-words bundle).
- **HARD_FAIL via `a1 <= a3`** -> any context works as well as the right one; the gain is an
  artifact of having a query vector at all. This is the outcome that would most cleanly kill the
  hypothesis and it is deliberately made easy to reach.

## 9. Wire status
`MEASUREMENT_ONLY_NO_WIRE`. Nothing in `hdlab/` is modified. Wiring is a separate decision after a
verdict.
