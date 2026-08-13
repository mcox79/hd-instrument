# PRE-REGISTRATION -- structured-comparator ablation (exp_structured_comparator_v1)

**Filed:** 2026-08-13, BEFORE any arm of this cell was run.
**Anchor:** `structured_comparator_v1`   **Output:** `data/exp_structured_comparator_v1/`
**Owner constraint:** GROWTH IS PAUSED. Nothing this cell writes enters a canonical foundation
path. The structured comparator ships behind a flag that is **default-OFF**; shipped behaviour
is unchanged.

---

## 1. The finding this ablation tests

`notes/brain_fidelity_audit_readout_2026-08-13.md` establishes off disk that the meaning
read-out's decision variable is `_cos()` (`hdlab/reading_grounding_loop.py:399-403`): cosine
between two bags of hashed content words built by `context_vector()`
(`hdlab/grounding_acquisition_loop.py:117-134`), argmax over `ConceptSpace` anchors. Propose
(`:684-688`), the informativeness gate, AND verify (`:690-694`) all route through the same
`canonicalize_fast`. Verify re-runs the identical statistic on a fresh encounter and tests
`== hypothesis.obj`: new evidence, SAME ruler. A systematic bias in the metric is therefore
invisible to verification -- consistent co-occurrence is indistinguishable from correct meaning.

The Director's blind hand-score (`notes/director_handscore_readout_v1_2026-08-13.md`) measured
**3 MEANINGFUL / 19 RELATED / 78 NOISE** over 100 rows. Failures are topical co-occurrence:
`whisky->wedding`, `banana->people`, `aphotic->marry`, `checklist->joe`.

**Hypothesis under test (H1):** the dominant cause of the NOISE band is that the comparator
compares WORD PROXIMITY. If the comparator instead compares RELATIONAL STRUCTURE, the
topical-neighbour error class shrinks and the MEANINGFUL rate rises.

**H0 (pre-declared LIVE and acceptable):** meaning quality is not limited by the comparator's
feature space, and structuring the comparator moves nothing.

---

## 2. Arms -- ONE variable

Both arms run the identical loop: same corpus, same curriculum order, same `ARM_SEED`, same
`HDFactStore`, same `Library` / `consolidation_pass` / schema gate / PBV control flow, same
`ConceptSpace` accumulator, same `canonicalize_fast` argmax, same `SENSE_MATCH_THRESH`,
same commit-strength gate. F1/F3 are OFF in BOTH arms (proven irrelevant by the 2026-08-13
hand-score; they are not varied here).

**The ONE variable is the function that builds the vector a lemma is profiled and compared by.**

| | CONTROL | STRUCTURED |
|---|---|---|
| encoder | `context_vector_masked` (unchanged) | `structural_vector_masked` (new, flagged) |
| feature alphabet | bare content-word lemma | `(dependency_relation, filler_lemma)` pair |
| which words enter | EVERY content word in the sentence | ONLY the target's 1-hop syntactic neighbourhood + co-arguments of its head |
| composition | `sign(sum(word_vec))` | `sign(sum(bind(rel_vec, filler_vec)))`, bind = elementwise multiply |

`CONTROL` is the current shipped default (`readout=None`, `freeze_episode=False`) and must
reproduce `data/exp_grounding_quality_readout_v1` BASE: **384 facts, pairs_digest
`836571fa99d5765d`**, corpus `load_corpus_v5(None, lineaware=True)` = 34,169 sentences.

### 2.1 What STRUCTURED actually compares

For target token `i` in a parsed sentence, features are:

* `("^" + deprel(i), lemma(head(i)))` -- the relation the target bears to its head;
* `(deprel(j), lemma(j))` for every dependent `j` of `i`;
* `("~" + deprel(i) + ":" + deprel(j), lemma(j))` for every co-argument `j` sharing the
  target's head -- the predicate-mediated link.

Fillers are restricted to content lemmas and the target's own lemma is never a filler
(the no-leak invariant, inherited from `context_vector_masked`).

Each feature is bound with the substrate's own bipolar binding operation (elementwise multiply,
`hdlab/event_bundle.py:146`, `hdlab/gap_detector.py:85-88`) over hashlib-seeded symbol vectors
drawn by **byte-identical** convention to `context_vector`'s own per-word draw
(`grounding_acquisition_loop.py:129-131`). A self-test asserts that summing the UNBOUND filler
vectors of a sentence's content words reproduces `context_vector` exactly, which is what makes
this a feature-space swap and not a second, incomparable vector space.

Binding makes role and filler jointly necessary for a match: `dog`-as-`nsubj`-of-`chase` and
`dog`-as-`obj`-of-`chase` are near-orthogonal features, whereas the bag records only `dog`.

### 2.2 Owned organs reused -- nothing parallel built

| organ | file:line | role here |
|---|---|---|
| POS tagger (glass-box averaged structured perceptron, UD EWT) | `hdlab/pos_tagger.py:80` + asset `data/frontend_assets/pos_tagger_ud_ewt_upos.json` | UPOS per token |
| arc parser (hashed MST) | `hdlab/arc_parser.py:207` + asset `data/frontend_assets/arc_parser_richfeat_ud_ewt.npz` | unlabeled heads |
| arc labeler (UD deprels, 36 labels) | `hdlab/arc_labeler.py:111` + asset `data/frontend_assets/arc_labeler_hashed_ud_ewt.json` | relation per arc |
| bipolar bind / quantize | `hdlab/event_bundle.py:146`, `hdlab/gap_detector.py:85-88` | role-filler binding |
| symbol-vector draw | `hdlab/grounding_acquisition_loop.py:129-131` | hashed filler vectors |
| lemma normalizer | `hdlab/thematic_role_labeler.py:235` (`lemma_word`) | filler + target lemmas |
| everything downstream | `ConceptSpace`, `canonicalize_fast`, `make_pbv_fns`, `consolidation_pass`, `HDFactStore`, `GapDetector` | UNCHANGED, both arms |

**Correction to the dispatch brief, verified on disk:** `reading_grounding_loop.py:101` imports
only `lemma_word` from `thematic_role_labeler`. Predicate-argument ROLES are **not** already
available on this path. `thematic_role_labeler.role_feats` (`:393`) additionally requires POS
tags plus a TRAINED perceptron (`train_perceptron`, `:427`) for which no persisted artifact
exists on disk. The UD front-end above is the reusable, already-trained organ that does supply
relational structure, so it is what this cell wires. `frame_slot_role` (`:112`) is a supplied
lookup needing no training, but it maps only subj/obj/iobj of a listed verb and is strictly
narrower than the UD deprel set; it is not used.

**`gap_detector.ca3_match_score` / `cleanup_family` deliberately NOT wired.** They are attractor
cleanup over a codebook; swapping the argmax for an attractor read-out would be a SECOND
variable on top of the feature-space swap and would confound this ablation. The audit's own
sec 4 lists them as step (2) after step (1) the feature space. Step (1) is what is tested here.
If STRUCTURED passes, the attractor comparator is the next cell, not this one.

---

## 3. THE ANTI-CIRCULARITY GATE -- discharged BEFORE the full run

If STRUCTURED internally reduced to cosine-over-context-bags, the result would be fake.

**Witness 1 -- argmax provably disagrees.** Both encoders were run over the same 3,992-sentence
corpus slice (`data/exp_structured_comparator_v1/_probe_disagree.json`), building two
`ConceptSpace`s; argmax was then taken for every lemma present in both.
**Disagreement = 6145 / 6283 = 0.9780.** The two comparators are not the same function.

**Witness 2 -- the worked disagreement example, on the documented failure.**
`whisky` occurs in 6 corpus sentences; `wedding` co-occurs in the bag in every sentence that
produced the hand-scored `whisky -> wedding` error, and is **structurally unreachable in all of
them** (`data/exp_structured_comparator_v1/_probe_witness.json`):

| corpus sentence (segment) | CONTROL bag | STRUCTURED features |
|---|---|---|
| "One buyer ordered nine cases of Japanese whisky costing over $750 a bottle for a **wedding** reception" (int_cont -- the exact hand-scored row 016) | bottle, buyer, case, costing, japanese, nine, order, reception, **wedding** | `(^mark, costing)`, `(~mark:obl, bottle)`, `(~mark:obl, reception)` |
| "One super-rich person bought nine boxes of Japanese whisky that cost more than over $750 a bottle for a **wedding** party" (ele_cont) | bottle, box, buy, cost, japanese, more, nine, party, person, rich, super, **wedding** | `(^nmod, box)`, `(acl, cost)`, `(amod, japanese)`, `(~nmod:nummod, nine)` |
| "The attraction of the imported whisky was that no one who came to the **wedding** would ..." (ele_cont) | able, attraction, come, drink, find, india, same, **wedding** | `(^obj, import)`, `(~obj:conj, come)` |

`wedding` is in the CONTROL bag in all three and in the STRUCTURED feature set in none.
CONTROL demonstrably produced `whisky -> wedding`; STRUCTURED **cannot** produce it from this
corpus. The same holds for `checklist -> joe`: `joe` and `kittinger` are in the bag and are
excluded by structure in both corpus sentences. For `banana`, structure isolates
`(^nsubj, fruit)` -- the correct hypernym -- from a 12-word bag that also contains
`adult, apple, ate, week, orange`.

**This gate is discharged: STRUCTURED is not circular with `_cos()`.** It remains a dot product
under the hood, which the audit anticipated and explicitly permitted ("the point is WHAT is
being compared, not whether a dot product is involved").

### 3.1 The declared cost of structure -- pre-registered, NOT corrected for

Measured over 7,740 (sentence, target) pairs sampled at seed 42
(`_probe_witness.json:density`):

| | mean features/encounter | median | zero-feature rate |
|---|---|---|---|
| CONTROL | 11.33 | 11 | 0.0017 |
| STRUCTURED | 2.86 | 3 | 0.0214 |

STRUCTURED sees **~4x less** per encounter. This is not a bug to be tuned away: FILTERING IS
THE MECHANISM, and adding the excluded words back is precisely reverting to the bag. It is
recorded here, before the run, as a covariate and as the leading alternative explanation for a
NULL or HURTS outcome ("structure was starved", not "structure is irrelevant"). It is reported
in `metrics.json` and must be stated in any write-up of a negative result.

Second declared limitation: the UD front-end is trained on UD EWT (web text) and is used
out-of-domain on news + OpenStax biology. It is visibly noisy -- in the row-016 sentence it
mistags `whisky` as SCONJ and attaches it as `mark` to `costing`. Parse noise degrades
STRUCTURED and does not touch CONTROL, so it is a conservative bias against H1: a NULL is
attributable to parse quality, whereas a PASS is achieved DESPITE it.

---

## 4. PRIMARY discriminator, bands FIXED before data

Primary = the **Director's blind hand-score**, MEANINGFUL rate, n = 50 per arm, pooled 100,
shuffle seed 42, labels sealed in `arm_key.json`. Rubric MEANINGFUL / RELATED / NOISE per
`notes/foundation_grounding_sample_2026-08-12.md`.

`delta = MEANINGFUL(STRUCTURED) - MEANINGFUL(CONTROL)`

| band | criterion |
|---|---|
| **STRUCTURAL_FIX_WORKS** | `MEANINGFUL(STRUCTURED) >= 0.15` AND `delta >= +0.10` |
| **PARTIAL** | `delta` in `[+0.05, +0.10)` |
| **NULL** | `abs(delta) < 0.05` -- pre-declared acceptable and genuinely possible |
| **HURTS** | `delta <= -0.05` |

### 4.1 Power -- stated plainly

Reference floor: CONTROL is expected at the measured `p1 ~= 0.02-0.03` (BASE 1/50; pooled
3/100). With n = 50/arm:

* `SE(delta) = sqrt(p1(1-p1)/50 + p2(1-p2)/50)`.
* At `p1 = 0.03, p2 = 0.15`: `SE = 0.056`, observed `delta = 0.12 = 2.14 SE`. Two-sided power
  at alpha 0.05 is approximately **0.57**.
* **Minimum detectable delta at 2 SE = +0.11** (i.e. STRUCTURED must reach about 0.14).

**Is the design underpowered? For the PARTIAL band, YES and it is declared so in advance:
`delta` in [0.05, 0.10) sits BELOW the 2-SE resolution at n=50 and cannot be distinguished from
noise. A PARTIAL result licenses a re-score at larger n and nothing else.** Resolving a true
delta of +0.075 needs n ~= 88/arm at 2 SE, or n ~= 172/arm for 80% power.

**For the primary STRUCTURAL_FIX_WORKS band the design CAN return a positive, and this is the
specific defect it fixes relative to the previous cell.** The 2026-08-12 read-out cell was
floor-limited: both arms were pinned at 2-4%, so the maximum attainable delta was 3/50 - 0/50 =
0.06, INSIDE its own NULL band -- it could not have returned a non-NULL verdict at any
allocation. Here only CONTROL is pinned; STRUCTURED is unconstrained upward. 8/50 MEANINGFUL in
STRUCTURED against the expected 1-2/50 in CONTROL yields `delta >= +0.12` and clears the band.
The floor pathology does not recur.

---

## 5. SECONDARY discriminator -- MECHANISTIC, independent of hand-scoring

**Agreement with a plain co-occurrence baseline, per arm.** This is the headline number if the
hand-score is ambiguous, and it is computed with no human in the loop.

Baseline: raw sentence-level co-occurrence counts over the full 34,169-sentence corpus between
content lemmas. For a banked subject `s`, `TOP1(s)` / `TOP5(s)` are its highest-count
co-occurrents restricted to `is_eligible_meaning`, ties broken by sorted lemma order.
For each arm, over its own banked `(s -> o)` facts:

* `cooc_agreement_top1 = mean[ o == TOP1(s) ]`
* `cooc_agreement_top5 = mean[ o in TOP5(s) ]`

Pre-declared direction: **CONTROL tracks the co-occurrence baseline closely; STRUCTURED
diverges from it.**

> **If `cooc_agreement_top5(STRUCTURED) >= cooc_agreement_top5(CONTROL) - 0.05`, the structured
> comparator DID NOT BIND, and that is the headline finding REGARDLESS of the hand-score.**
> A hand-score improvement on top of unchanged co-occurrence agreement would be reported as
> unexplained and not credited to the mechanism.

Also recorded, hand-score-independent: per-arm fact count, admission rate, confirm rate,
revision rate, `n_refusals` by reason, mean features/encounter, parse coverage, and the
`(subject, object)` pairs digest per arm (S3 arms-must-differ).

---

## 6. Structural gates (cell-level, evaluated by the cell)

* **S1 cardinality** -- 2 arms x 5 segments = 10 units present in `units.jsonl`.
* **S2 integrity** -- zero tautology facts `(X, GROUNDED_MEANING, X)`, zero closed-class
  objects, zero no-leak violations (no seed word grounded) in BOTH arms.
* **S3 arms-must-differ** -- the two arms' pairs digests differ.
* **S4 CONTROL regression** -- CONTROL's `n_meaning_facts == 384` AND
  `pairs_digest[:16] == "836571fa99d5765d"`. A mismatch does not abort the run but is recorded
  as `control_reproduces_reference = false` with the observed values, and any comparison is
  then reported as NOT matched to the reference.
* **S5 yield floor** -- each arm banks >= 50 GROUNDED_MEANING facts, else the 50-row sample is
  drawn with replacement-free `min(50, n)` and the shortfall is declared.
* **S6 parse coverage** -- fraction of STRUCTURED-arm sentences successfully parsed; recorded,
  no threshold.

## 7. Blind-sample protocol (no-leak)

Pooled n = 100 (50/arm), `random.Random(42).sample` over fid order, combined and shuffled at
seed 42, `blind_id` assigned after shuffle. `SCORING_SHEET.txt` follows the EXACT format of
`data/exp_grounding_quality_readout_v1/SCORING_SHEET.txt`. Omitted from the sheet so block
shape carries no arm signal: `best_cos`, `schema_score`, every attestation counter, `fid`,
`segment`. Exactly ONE context sentence per row, truncated to 160 chars. `arm_key.json` is
written separately and is never opened while the sheet is rendered.

## 8. What this cell will NOT claim

1. No quality claim of any kind. The cell emits no tier; the Director scores blind.
2. No cross-comparison to the 64% v5 definitional-extraction number -- a DIFFERENT pipeline
   (a hand-written parser SUPPLYING facts, not a read-out ACQUIRING one). No ratio or "gap"
   between them is meaningful.
3. No claim that a co-occurrence-agreement change alone is a quality improvement.
4. Nothing is promoted, wired ON, or written to a canonical foundation path. Growth stays paused.
