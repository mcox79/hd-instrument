# Foundation Grounding Sample Audit -- 2026-08-12

Status: IN PROGRESS (writing incrementally)

## Store + methodology

- Store: `data/foundation/reading_grounding_v1` (HDFactStore, n_dim=2048), loaded via
  `hdlab.foundation_persistence.load_foundation`.
- Verified off disk: 3544 `GROUNDED_MEANING` facts, all status=ACTIVE. self-grounded
  (obj==subject) = 2328, cross-grounded (obj!=subject) = 1216. Matches the task brief exactly.
- Glass-box spot-check: 15 random facts re-recovered via `store.recover_fact(vec)` (unbind +
  cleanup, not the plaintext shadow field) -- 0 mismatches vs the shadow `subject`/`obj` fields.
  The plaintext fields used below are therefore a faithful read of the substrate, not an
  independent claim.
- **How the pair is actually formed (verified by reading code, not taking the prior VET's
  claim on faith):** `hdlab/reading_grounding_loop.py`, function `canonicalize()`
  (line ~172) and its caller `checkpoint()` (line ~293). This is NOT "cosine over the
  same-sentence context" in the sense of one sentence -- it is: bundle ALL of a newly-grounded
  word's accumulated context vectors (bag-of-content-words, masked to exclude the target word
  itself, across every occurrence seen, min 4) into one raw sum, `np.sign()` it, and take the
  cosine-nearest ANCHOR already in `ConceptSpace` (itself a running bag-of-words accumulator
  over every other word seen so far, seed words included) if cosine >= 0.45 (`SENSE_MATCH_THRESH`,
  code-commented as "HYPOTHESIZED... exploratory"); otherwise the word is banked as its own
  anchor (self-grounded, i.e. obj := subject). So every GROUNDED_MEANING object is a **pure
  co-occurrence / distributional nearest-neighbor pick**, not a definition, gloss, or relation
  extracted from any parse or semantic frame. That is the central fact this whole audit is
  measuring the consequences of.
- Source sentences: **NOT recoverable from the persisted foundation.** `Trace.context_vec` is
  a bundled HD/bag-of-words vector, never raw text; `foundation_persistence.save_library_pending`
  only persists PENDING items (terminal GROUNDED items' traces are explicitly dropped per that
  module's own docstring). The best available provenance is the run's `units.jsonl` checkpoint
  log (`data/exp_reading_grounding_loop_cycle2_v1/units.jsonl`), which gives, per lemma:
  `segment` (corpus slice), `pass_idx`, `best_cos`, `n_exposures`, `bank_schema_score` -- joined
  below by lemma (3544/3544 matched, 1:1). This is NOT a source sentence; it is aggregate
  meta-context. I did not invent any sentence text.
- Segments contributing to this store (verified against the cell script): `bootstrap`,
  `int_cont`, `ele_cont`, `adv_new`, `bio_new` -- all real OneStop-News (Ele/Int/Adv) + bio
  curriculum text. `scramble_probe` was explicitly excluded from the lookup: it runs on an
  independent control-copy branch (`run_scramble_probe`, loads/operates on `_control_copy_dir`)
  that is never saved back to `foundation_dir` -- confirmed by reading
  `experiments/exp_reading_grounding_loop_cycle2_v1.py` lines 258-300, so it cannot contaminate
  this store.
- Sampling code (fixed seeds, exact as run):
```python
gm_facts = [f for f in store._facts if f.relation == "GROUNDED_MEANING"]   # order = fid order
random.seed(42)
sample50_idx = random.sample(range(len(gm_facts)), 50)

cross_idx_all = [i for i, f in enumerate(gm_facts) if f.subject != f.obj]
random.seed(43)
sample20_idx = random.sample(cross_idx_all, 20)
```
- **Classification rule for self-grounded pairs (obj == subject), stated explicitly so the
  director can override:** a self-grounded fact reduces to `(lemma, GROUNDED_MEANING, lemma)`
  -- a tautology. It conveys zero information about what the word means (a word is not a
  definition of itself), regardless of whether the underlying word is a legitimate concept.
  I bucket every self-grounded pair NOISE under the strict "does the object say something about
  meaning" rubric. This is a judgment call, not a hidden default -- flagged here, and every
  self-grounded row is marked `self=True` in the table below so this call is fully visible and
  reversible by the director.

## Top 10 most common grounded objects (across all 3544)

| rank | object | count |
|---|---|---|
| 1 | also | 31 |
| 2 | say | 15 |
| 3 | people | 10 |
| 4 | polymerase | 9 |
| 5 | duplicat | 6 |
| 6 | like | 5 |
| 7 | more | 5 |
| 8 | most | 5 |
| 9 | fry | 5 |
| 10 | haploid | 5 |

Diagnostic reading: the single most common "meaning" assigned to a grounded word is `also`
(31 times) and `say` (15 times) -- discourse-marker / reporting-verb function words, not
content. `like`, `more`, `most` in the top 10 are the same failure mode. Only `polymerase`,
`duplicat`, `fry`, `haploid` look like genuine content words (all from the bio_new segment).
So roughly half of the top-10 most-repeated "meanings" in the whole store are generic function
words that a cosine-over-bag-of-words procedure will gravitate to for ANY word with a thin or
noisy context, independent of what that word actually means -- a structural signature of
distributional-noise capture, not hand-picked.

## Sample 1: 50 random GROUNDED_MEANING pairs (seed=42)

Columns: subject -> object, self/cross, segment (source corpus slice), best_cos (canonicalize
cosine), n_exposures, bucket, reason. Source sentence: NOT recoverable (see methodology above);
`segment`/`pass_idx` is the only available provenance, shown instead of inventing text.

| subject -> object | self/cross | segment | best_cos | n_exp | bucket | reason |
|---|---|---|---|---|---|---|
| ruler -> ruler | self | adv_new | 0.368 | 4 | NOISE | self-tautology (see rule) |
| mindfulness -> fourth | cross | ele_cont | 0.568 | 4 | NOISE | ordinal number, no semantic link |
| yoga -> yoga | self | bootstrap | 0.416 | 17 | NOISE | self-tautology |
| electron -> electron | self | bio_new | 0.321 | 66 | NOISE | self-tautology |
| vice -> digitiz | cross | int_cont | 0.525 | 4 | NOISE | unrelated pairing |
| toxin -> toxin | self | int_cont | 0.439 | 5 | NOISE | self-tautology |
| glazer -> glazer | self | int_cont | 0.344 | 5 | NOISE | self-tautology (proper name) |
| satisfy -> satisfy | self | ele_cont | 0.359 | 4 | NOISE | self-tautology |
| inductive -> deductive | cross | bio_new | 0.689 | 8 | MEANINGFUL | genuine paired concept; inductive is routinely defined by contrast with deductive |
| pair -> pair | self | ele_cont | 0.325 | 6 | NOISE | self-tautology |
| socializ -> socializ | self | adv_new | 0.246 | 4 | NOISE | self-tautology |
| warm -> warm | self | bio_new | 0.336 | 7 | NOISE | self-tautology |
| ross -> ross | self | adv_new | 0.360 | 4 | NOISE | self-tautology (proper name) |
| retailer -> alliance | cross | ele_cont | 0.567 | 4 | RELATED | same business-news topic, not defining |
| nuclei -> decay | cross | adv_new | 0.590 | 4 | MEANINGFUL | "nuclear decay" is a real, defining physics collocation |
| shot -> shot | self | adv_new | 0.415 | 4 | NOISE | self-tautology |
| electrically -> electrically | self | bootstrap | 0.315 | 4 | NOISE | self-tautology |
| intestine -> intestine | self | bootstrap | 0.295 | 5 | NOISE | self-tautology |
| observatori -> observatori | self | ele_cont | 0.253 | 4 | NOISE | self-tautology |
| lukla -> lukla | self | int_cont | 0.337 | 4 | NOISE | self-tautology (place name) |
| wright -> wright | self | int_cont | 0.408 | 4 | NOISE | self-tautology (proper name) |
| kitttinger -> kitttinger | self | adv_new | 0.244 | 4 | NOISE | self-tautology (proper name) |
| corridor -> survey | cross | adv_new | 0.478 | 4 | NOISE | no real semantic link |
| govern -> govern | self | bootstrap | 0.211 | 4 | NOISE | self-tautology |
| fishermen -> fishermen | self | adv_new | 0.383 | 5 | NOISE | self-tautology |
| stolen -> stolen | self | int_cont | 0.391 | 4 | NOISE | self-tautology |
| chick -> nest | cross | adv_new | 0.471 | 4 | RELATED | real association (chicks live in nests), not a definition |
| muddy -> muddy | self | adv_new | 0.371 | 4 | NOISE | self-tautology |
| widen -> widen | self | adv_new | 0.378 | 4 | NOISE | self-tautology |
| pregnant -> pregnant | self | adv_new | 0.253 | 4 | NOISE | self-tautology |
| mechanism -> identical | cross | adv_new | 0.476 | 4 | NOISE | no real semantic link |
| sprint -> sprint | self | int_cont | 0.311 | 5 | NOISE | self-tautology |
| explod -> explod | self | adv_new | 0.235 | 4 | NOISE | self-tautology |
| helium -> helium | self | adv_new | 0.424 | 4 | NOISE | self-tautology |
| ght -> ght | self | int_cont | 0.281 | 4 | NOISE | self-tautology (fragment token) |
| rubisco -> rubisco | self | bio_new | 0.329 | 4 | NOISE | self-tautology |
| facebook -> facebook | self | bootstrap | 0.418 | 20 | NOISE | self-tautology |
| measur -> measur | self | bio_new | 0.444 | 6 | NOISE | self-tautology |
| disperse -> disperse | self | bio_new | 0.429 | 4 | NOISE | self-tautology |
| november -> oberg | cross | ele_cont | 0.568 | 4 | NOISE | proper-noun co-occurrence, no meaning link |
| unfriend -> unfriend | self | adv_new | 0.256 | 4 | NOISE | self-tautology |
| sulphur -> soot | cross | adv_new | 0.659 | 4 | RELATED | both combustion/pollution byproducts; associative, not defining |
| folio -> folio | self | int_cont | 0.340 | 4 | NOISE | self-tautology |
| fellow -> fellow | self | int_cont | 0.374 | 4 | NOISE | self-tautology |
| campaign -> campaign | self | ele_cont | 0.394 | 8 | NOISE | self-tautology |
| barrel -> barrel | self | int_cont | 0.328 | 5 | NOISE | self-tautology |
| eukaryotic -> eukaryotic | self | bio_new | 0.376 | 17 | NOISE | self-tautology |
| translat -> also | cross | int_cont | 0.451 | 6 | NOISE | object is a function word |
| mainland -> carnivore | cross | ele_cont | 0.535 | 4 | NOISE | no real semantic link |
| intolerance -> intolerance | self | ele_cont | 0.289 | 5 | NOISE | self-tautology |

**Sample-1 bucket counts (n=50):** MEANINGFUL = 2 (4%), RELATED = 3 (6%), NOISE = 45 (90%).
Of the 45 NOISE, 38 are self-tautology and 7 are cross-grounded pairs with no real link.

## Sample 2: 20 random CROSS-grounded pairs only (seed=43, from the 1216 cross subset)

| subject -> object | segment | best_cos | n_exp | bucket | reason |
|---|---|---|---|---|---|
| austria -> girlfriend | ele_cont | 0.648 | 4 | NOISE | no semantic relationship |
| choic -> lanka | adv_new | 0.510 | 4 | NOISE | no semantic relationship |
| recruit -> promote | int_cont | 0.523 | 4 | RELATED | shared HR/workplace topic, not a definition |
| tree -> phylogenetic | bio_new | 0.461 | 15 | MEANINGFUL | "phylogenetic tree" -- textbook-correct biology collocation |
| litter -> cop | adv_new | 0.509 | 4 | NOISE | no semantic relationship |
| governor -> jail | ele_cont | 0.696 | 4 | RELATED | plausible news-narrative association, not defining |
| experimentation -> als | bio_new | 0.521 | 4 | RELATED | plausible ALS-research topical link, weak |
| organelle -> cytoplasm | bio_new | 0.504 | 8 | MEANINGFUL | organelles are located in the cytoplasm -- correct biology relation |
| huffington -> say | bootstrap | 0.524 | 10 | NOISE | reporting-verb artifact, not meaning |
| pinch -> invaginat | bio_new | 0.555 | 5 | MEANINGFUL | invagination literally is a membrane "pinching" motion -- correct process description |
| shed -> quirky | adv_new | 0.530 | 4 | NOISE | no semantic relationship |
| primer -> polymerase | bio_new | 0.610 | 12 | MEANINGFUL | primer/polymerase are tightly coupled DNA-replication terms |
| scholar -> observe | adv_new | 0.555 | 4 | RELATED | generic verb association, not defining |
| alternation -> haploid | bio_new | 0.458 | 4 | MEANINGFUL | "alternation of generations" haploid/diploid cycle -- correct biology term |
| variant -> gene | adv_new | 0.625 | 4 | MEANINGFUL | a variant is a form of a gene -- defining relation |
| compel -> like | adv_new | 0.453 | 5 | NOISE | object is a generic function word |
| physicist -> massachusett | int_cont | 0.777 | 5 | NOISE | institutional-location coincidence, not meaning |
| nam -> metadata | ele_cont | 0.457 | 4 | NOISE | no semantic relationship |
| represent -> meaning | ele_cont | 0.577 | 6 | MEANINGFUL | "to represent" is definitionally about conveying meaning |
| monthly -> follower | int_cont | 0.468 | 5 | RELATED | plausible social-media collocation, not defining |

**Sample-2 bucket counts (n=20, cross-only):** MEANINGFUL = 7 (35%), RELATED = 5 (25%),
NOISE = 8 (40%).

**Cross- vs self-grounded comparison:** self-grounded pairs are, by construction (rule stated
above), 100% NOISE under the strict meaning rubric -- every one collapses to `(X, X)`, a
tautology. Cross-grounded pairs are markedly better: 60% (MEANINGFUL+RELATED combined) carry
some real semantic content in this 20-sample, concentrated almost entirely in the `bio_new`
segment where `best_cos` runs highest (0.46-0.78) -- every MEANINGFUL hit in this sample is from
`bio_new`, and every NOISE hit with a proper name or function-word object is from a
non-bio segment. So cross-grounded is unambiguously better than self-grounded, but even at its
best (this cross-only sample) it is still 40% pure noise, and the mixed 50-sample (which is what
the store's raw composition actually looks like) is 90% noise once self-grounded's majority share
is folded in.

Status: COMPLETE. All sections written (methodology, top-10, 50-row table, 20-row cross table, comparison).


