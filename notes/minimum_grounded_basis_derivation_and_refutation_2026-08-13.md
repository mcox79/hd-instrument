# Minimum grounded basis: derivation, and why the brain-fidelity gate REFUTES it (2026-08-13)

**Scope. ANALYSIS ONLY.** No `hdlab/` or `tools/` file touched, no git add/commit, nothing written
to any canonical foundation path (GROWTH STAYS PAUSED). All output under
`data/exp_minimum_basis/` (`build_basis.py`, `controls.py`, `metrics.json`, `controls.json`,
`basis_top200.json`, `corpus_vocab.json`). `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`,
`sorted(set(...))` throughout. Every number below is off disk.

**Bottom line: the derivation is REFUTED by its own falsification test.** The basis is not
early-acquired child vocabulary; once you control for corpus frequency it is not more concrete,
not more sensorimotor, and not earlier-acquired than the corpus at large. It is a frequency +
topology artefact. Separately and independently, the covering problem has no good solution at all:
the definitional graph reaches only 14% of the corpus vocabulary no matter how many anchors you
grant it.

---

## 1. The graph

**Edge semantics.** A definitional fact `(SUBJ, REL, OBJ)` asserts SUBJ's meaning is expressed in
terms of OBJ (`ATP -> process`, `VBNC state -ENABLING_CONDITION-> enter`). For *bridging* the
useful direction is the reverse: **if OBJ is grounded, SUBJ becomes reachable in one hop**, so the
graph edge is `OBJ -> SUBJ` ("enables"). Subject identity = the extractor's own `subject_head_lemma`
where present, else `lemma_word` of the last token of the subject surface (English NPs are
head-final). Self-loops (`SUBJ == OBJ`, the tautology class) are dropped -- they carry no bridge.

| set | rows | self-loops | edges kept |
|---|---|---|---|
| v5 `definitional_facts_v5.jsonl` | 2092 | 0 | 2092 |
| v62 `predicate_facts_v62.jsonl` | 221 | 1 | 220 |
| v4 `definitional_facts_v4.jsonl` | 1956 | 0 | 1956 |
| v3 `definitional_facts.jsonl` | 1751 | 0 | 1751 |

- v5+v62 only: **2,312 edge instances, 2,239 distinct edges, 2,357 nodes**.
- all four (v3+v4+v5+v62): **6,019 edge instances but only 2,607 DISTINCT edges, 2,595 nodes**.
  v4 and v3 are near-supersets/predecessors of v5 -- 3,707 extra rows buy **368 distinct edges and
  238 nodes**. Coverage headroom from the older extractions is marginal.

**The graph is flat, not hubbed.** 1,357 source nodes; max out-degree **54** (`process`); the top
20 sources account for only **12.9%** of all edges; **917 / 1,357 source nodes have out-degree 1**.
There is no small set of high-fan-out nodes to exploit -- which is exactly why the covering curve
below is bad.

**960 of 2,595 nodes have no incoming edge at all** (source-only). Those can never be reached by
bridging from anything; they must be anchored directly.

---

## 2. The covering problem

**Algorithm: classic greedy maximum-coverage** (repeatedly take the candidate whose k-hop
reachable set adds the most uncovered targets; deterministic tie-break by sorted lemma). Greedy is
an **approximation** (1 - 1/e for max-coverage), **not the true optimum**, which is NP-hard. The
numbers below are therefore upper bounds on |S|; the true minimum is somewhat smaller but the
conclusion does not turn on the gap.

**Target set.** Corpus (`load_corpus_v5(None, lineaware=True)`, 34,169 sentences) yields **18,648
distinct lemmas, 18,276 `is_eligible_meaning`**. *Caveat: the bottleneck trace reports 16,812 /
16,507 for the same corpus; my tokenizer is v5's own `TOK` + `lemma_word`, which is evidently not
identical to whatever the trace used. I could not reconcile the two and did not try to -- the
ratios below move by <2 points either way.* The only lemmas any covering solution could ever reach
are those present in the graph: **2,563 of 18,276 = 14.02%**. That ceiling is the headline.

Coverage curve, |S| needed, target = the 2,563 reachable lemmas (graph = all four sets):

| target coverage | k=1 | k=2 | k=3 |
|---|---|---|---|
| 50% | 264 | **165** | 140 |
| 80% | 655 | **522** | 492 |
| 95% | 1,039 | **871** | 841 |
| 100% | 1,167 | 999 | 969 |

v5+v62 only (target 2,325): 50% = 233 / 148 / 128; 80% = 581 / 466 / 440; 95% = 903 / 743 / 715.

**Read the compression ratio, not the count.** At k=2, 871 anchors buy 2,435 lemmas: a basis
**one third the size of the thing it covers**. Going k=2 -> k=3 saves only 30 anchors. That is not
a basis, it is a list. As a fraction of the *corpus*, the 95% solution covers **13.3%** of eligible
vocabulary; 50%/80%/95% of the full 18,276-lemma corpus vocabulary is **unreachable at any |S|**.

**Defensible target = there isn't one on this graph.** If forced: |S| = 165 at k=2 for half of the
reachable 14%, i.e. **165 new anchors to reach 7.0% of corpus vocabulary**.

---

## 3. THE BRAIN-FIDELITY GATE -- REFUTED

Primary basis under test: graph=all, k=2, greedy top-200. Norms: Brysbaert concreteness
(37,058 single-word rows), **Kuperman AoA `AoA_Kup_lem`, 51,695 rows -- we DO have AoA data**,
Lancaster `Max_strength.sensorimotor` (39,707). Test: Mann-Whitney U two-sided + rank-biserial
correlation (rbc; positive = basis stochastically larger).

### 3a. Naive comparison vs corpus at large -- looks like a pass

| norm | basis median (n) | corpus median (n) | p | rbc |
|---|---|---|---|---|
| concreteness | 3.555 (180) | 3.100 (10,244) | 9.5e-4 | +0.144 |
| AoA (years) | 7.90 (178) | 9.53 (10,246) | 1.7e-14 | -0.335 |
| sensorimotor | 3.657 (180) | 3.412 (10,221) | 3.7e-4 | +0.155 |

More concrete, earlier, more sensorimotor. Effects are small-to-moderate but real. **This is the
result that would have been reported if the controls had been skipped.**

### 3b. Control 1 -- frequency-matched. THE EFFECT DISSOLVES.

Basis members are frequent corpus words, and frequency predicts both concreteness and AoA. Matched
control: for each basis member draw a corpus lemma from the same `log10(freq+1)` bin (0.1 dex), 20
independent draws, seed 20260813.

| norm | basis median | freq-matched median | median p | median rbc | draws p<.05 |
|---|---|---|---|---|---|
| concreteness | 3.555 | 3.205 | **0.143** | +0.092 | 4 / 20 |
| AoA (years) | 7.90 | 7.405 | **0.331** | **+0.061** | 1 / 20 |
| sensorimotor | 3.657 | 3.537 | **0.266** | +0.070 | 4 / 20 |

**Not significant on any norm, and on AoA the sign REVERSES** -- the basis is if anything
marginally *later*-acquired than frequency-matched corpus words. The 3a result was a frequency
effect wearing a grounding costume.

### 3c. Control 2 -- vs the seed vocabulary, which is genuinely early

The 887 seed lemmas are the right positive reference for "what humans ground first". The battery
separates them from the corpus cleanly on AoA (median **5.05y vs 9.53y, p=4.6e-292, rbc -0.773**)
-- so the test *can* detect an early-acquired set. Note it does NOT find the seed more concrete
(rbc -0.051): early vocabulary is early, not especially concrete.

Basis vs seed:

| norm | basis | seed | p | rbc |
|---|---|---|---|---|
| AoA (years) | 7.90 | 5.05 | **2.8e-41** | **+0.644** |
| concreteness | 3.555 | 3.040 | 7.1e-5 | +0.189 |
| sensorimotor | 3.657 | 3.559 | 0.288 | +0.051 |

**The basis is ~2.9 years later-acquired than the seed, at the largest effect size anywhere in this
analysis.** The prediction under test was "if the basis is real it should look like early child
vocabulary". It does not. It looks like mid-schooling textbook vocabulary.

### 3d. Control 3 -- topology-only baseline

Take the 200 highest-out-degree nodes, no covering solve at all. vs corpus: concreteness rbc
+0.165, AoA rbc -0.305, sensorimotor rbc +0.102 -- **statistically indistinguishable from the
greedy basis's +0.144 / -0.335 / +0.155**. The covering solve adds nothing the raw degree ranking
did not already have. Greedy gain correlates with out-degree at Spearman **rho = 0.578
(p = 3.5e-19, n=200)**; hub/basis Jaccard 0.333 at top-50, 0.307 at top-200.

### 3e. Face validity of the members

Ranks 1-12 by coverage gain: `process` (67), `structure` (63), `cell` (50), `molecule` (49),
`community` (24), **`joy` (23)**, `organism` (23), `category` (22), `enter` (21),
`characteristic` (19), `diet` (19), `atom` (18). The single highest-gain member is `process` --
precisely the abstract hub named in advance as the artefact signature.

Junk bridges are load-bearing in the solution, not incidental: `joy -> {report, study}` (corpus
freq 9), `congratulations -> minister`, `canada -> {food, offender, smartphone}`,
`director -> {campbell, clapper, graham, imafidon, ...}`, `company -> {apple, ltd, mondadori,
pavegen, ...}`. These are news-appositive extractions, not definitions, and they inflate coverage.

### VERDICT

**REFUTES.** Under the pre-stated criterion the basis fails: it is not early-acquired (it is 2.9
years later than the seed, p=2.8e-41), and its concreteness/sensorimotor advantage over the corpus
does not survive frequency matching (p=0.14 / 0.27). A topology-only degree ranking reproduces the
whole apparent effect. **The covering solution is a topology artefact.** The one thing that would
have made it interesting -- convergence between what the graph says is structurally basic and what
children acquire first -- is absent.

---

## 4. The basis itself

Full table: `data/exp_minimum_basis/basis_top200.json` (lemma, gain, cumulative coverage, corpus
freq, out-degree, concreteness, AoA, sensorimotor, in_seed, in_grounded, is_new).

Of the top 200 (graph=all, k=2): **35 in the 887-lemma seed, 7 in the 374 STRUCTURED-grounded set,
42 in the 1,261 anchor universe -- 158 are NEW.** (k=1 basis: 147 new; v5+v62-only k=2 basis: 161
new.) So the implied work for the top-200 alone is ~158 concepts, and for the 871-member 95%
solution it is several hundred more -- to buy 13% of corpus vocabulary.

---

## 5. Cross-check against the seed vocabulary

`data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv` holds **74,287 rows**
(word, freq_rank, subtlex_freq_pm, subtlex_count, aoa_years, ogden_850, dolch_level, dolch_rank --
SUBTLEX-ranked, AoA- and Ogden/Dolch-annotated). The loop takes the **top 1,000 -> 887 distinct
lemmas**. The seed is a frequency-ordered slice of a 74k list: **the pool is not the constraint --
73,287 unused rows sit on disk.**

Overlap with the graph:

| quantity | value |
|---|---|
| seed lemmas present in the definitional graph at all | 245 / 887 |
| seed lemmas inside the 2,563-lemma target | 237 |
| STRUCTURED-grounded lemmas inside the target | 100 |
| anchor universe (1,261) inside the target | 337 |
| target reached by the existing 887 seed, k=1 | 549 / 2,563 = 21.4% |
| target reached by the existing 887 seed, k=2 | 667 / 2,563 = 26.0% |
| target reached by the full 1,261 anchor universe, k=2 | 918 / 2,563 = 35.8% |

**The existing anchors already reach 36% of everything the graph could ever reach**, and greedy
needs 165 optimally-chosen anchors for 50%. The seed is not badly chosen and it is not too small in
principle -- what is small is the definitional graph.

**What this implies.** The pool problem is not *which* words. It is (a) how words ENTER -- the two
entry sites are seed-membership and already-grounded, and nothing about being a good bridge target
gets a word in -- and (b) that we have 2,607 distinct definitional edges over an 18k-lemma corpus,
so there is almost nothing to bridge *along*. Expanding the seed from 1,000 to N is cheap and
available; it will not fix a 14% reachability ceiling.

---

## 6. What I could NOT verify

- **The 16,812 / 16,507 corpus-vocabulary figures from the bottleneck trace.** My recount gives
  18,648 / 18,276 on the same corpus loader. I did not locate the trace's tokenizer to reconcile.
- **Whether the definitional facts are CORRECT.** I used them as a graph. The 65.7%-tautology and
  64%-hand-scored findings still apply; `joy -> report` shows junk edges are in the solution.
- **Anything about grounding QUALITY.** Reachability is not meaning. A word being 2 hops from an
  anchor says nothing about whether traversing those hops yields the right sense.
- **The true optimum |S|.** Greedy only.
- **Norm coverage of the basis is ~90%** (180/200 concreteness, 178/200 AoA) -- the missing 20 are
  technical terms (`macromolecule`, `organelle`, `taxon`, `gnetophytes`), which are exactly the
  *least* early-acquired members. Their absence biases the basis's AoA **downward**, so the
  refutation in 3c is conservative.
