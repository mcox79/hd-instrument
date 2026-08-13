# Distance-to-grounded-frontier over the whole corpus vocabulary (2026-08-13)

**Scope. MEASUREMENT ONLY.** No quality claim, no proposed fix, nothing wired, nothing written to
any canonical foundation path. One script + two outputs, all under
`data/exp_frontier_distance/` (`build_frontier_distance.py`, `metrics.json`,
`lemma_distance.tsv`). No `hdlab/` or `tools/` file touched. `OMP_NUM_THREADS=1`,
`OPENBLAS_NUM_THREADS=1`, `sorted(set(...))` throughout. Runtime 5.5s, fully deterministic.

Implements the USER's GAP == GROUNDING framing operationally: a gap is the shortest missing
RELATIONAL BRIDGE from a concept to the grounded frontier, so the natural measurement is the
distance distribution of the corpus vocabulary to that frontier over DEFINITIONAL edges.

---

## 1. The frontier, enumerated off disk

| quantity | value | how obtained |
|---|---|---|
| seed vocabulary, raw words | 1000 | `load_base_vocab_seed()` -> `data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv`, first 1000 rows |
| seed distinct lemmas | **887** | `normalize_lemma` (= `lemma_word`) over those 1000, `sorted(set(...))` -- exactly what `seed_known_words` does at `reading_grounding_loop.py:983-989` |
| grounded lemmas, STRUCTURED arm | **374** rows -> **374** distinct | subjects of `data/exp_structured_comparator_v1/arm_STRUCTURED_provenance.json` |
| grounded lemmas, CONTROL arm | 384 rows -> 384 distinct | `arm_CONTROL_provenance.json` |
| seed / grounded overlap | **0** | measured |
| **FRONTIER (STRUCTURED)** | **1,261** | seed UNION grounded |
| frontier (CONTROL, for reference) | 1,271 | |
| of the 887 seed lemmas, occurring in the corpus at all | **785** | |
| **of the 1,261 frontier lemmas, occurring in the corpus at all** | **1,159** | |

Confirms last night's `notes/downstream_bottleneck_trace_2026-08-13.md` numbers exactly
(887 / 374 / 1,261 / 16,812 / 16,507). The frontier is a SUPERSET of the anchor set at any single
decision time, so every "unreachable" verdict below is conservative in the right direction.

Corpus: `load_corpus_v5(None, lineaware=True)` = **34,169 sentences**, **16,812** distinct content
lemmas (`content_lemmas`), of which **16,507** pass `is_eligible_meaning`. Frequency below =
number of corpus sentences whose `content_lemmas` contain the lemma (this reproduces `fruit`=95,
`zone`=71 from last night).

---

## 2. The relational graph

**Edge semantics: `subject_head_lemma --(definitional fact)--> object`, DIRECTED, toward the
definiens.** That is the bridging direction the framing asks for: if the object is grounded, the
subject can be reached across the edge. Multi-word subjects are reduced to their head lemma
(`subject_head_lemma` where the file carries it; last alphabetic token otherwise -- English NPs
are right-headed). Both endpoints pass through `normalize_lemma` so they live in the same lemma
space as the corpus and the frontier. Self-loops (`X -> X`) are dropped; there was exactly 1
(in v62), 0 in v5. Relation labels are NOT distinguished -- an `ISA` edge and an
`ENABLING_CONDITION` edge count the same hop.

| source | rows | distinct edges | NEW edges it contributes (order v5, v62, v4, v3) |
|---|---|---|---|
| `definitional_facts_v5.jsonl` | 2,092 | 2,023 | 2,023 |
| `predicate_facts_v62.jsonl` | 221 | 216 | **216** |
| `definitional_facts_v4.jsonl` | 1,956 | 1,840 | **50** |
| `definitional_facts.jsonl` (v3) | 1,751 | 1,751 | **318** |

**Does v4/v3 add coverage? v4 essentially none (50 new edges, 2.7% of its own 1,840) -- it is a
near-subset of v5, as expected since v5 is v4 plus the term-boundary fix. v3 adds 318 (18.2%),
but v3 predates the `lemma_verb`->`lemma_word` fix that was landed precisely because it minted
non-word concepts.** Primary results below therefore use **CORE = v5 + v62** (2,239 edges, 2,357
nodes, 2,296 of them in the corpus vocabulary). ALL-4 is reported as a sensitivity check.

---

## 3. Distance histogram (PRIMARY: CORE = v5+v62, directed)

Distance(w) = minimum number of `subject -> object` hops from `w` to any frontier member;
computed by BFS from the frontier over reversed edges.

| distance | all 16,812 corpus lemmas | share | eligible only (16,507) |
|---|---|---|---|
| **0** (already frontier) | 1,159 | 0.0689 | 988 |
| **1** | **371** | 0.0221 | 370 |
| 2 | 113 | 0.0067 | 113 |
| 3 | 68 | 0.0040 | 68 |
| 4+ | 65 | 0.0039 | 65 |
| **UNREACHABLE** | **15,036** | **0.8944** | 14,903 |

**Decomposition of UNREACHABLE:** 14,314 (95.2% of them) have **no outgoing definitional edge at
all** -- they are the subject of zero extracted fact, so relational bridging has literally nothing
to work with. Only 722 have edges yet no path to the frontier.

**15,036 / 16,812 = 89.4% of the corpus vocabulary is unreachable from the frontier over the
definitional graph we own.** That is the bound on what relational bridging over these facts can
ever fix. Everything reachable at any distance is 1,776 lemmas = 10.6%; reachable but not already
frontier is 617 = 3.7%.

### Sensitivity to graph choice

| variant | 0 | 1 | 2 | 3 | 4+ | UNREACHABLE |
|---|---|---|---|---|---|---|
| **CORE directed (primary)** | 1,159 | **371** | 113 | 68 | 65 | **15,036** |
| CORE undirected | 1,159 | 515 | 416 | 333 | 224 | 14,165 |
| ALL-4 directed | 1,159 | 432 | 141 | 129 | 97 | 14,854 |
| ALL-4 undirected | 1,159 | 609 | 504 | 381 | 185 | 13,974 |

The most permissive possible reading -- every fact file ever produced, edges traversable in both
directions -- still leaves **13,974 / 16,812 = 83.1% unreachable**. The 89.4% headline is not an
artifact of the directedness choice or of excluding v3/v4.

---

## 4. Breakdowns

### (a) By corpus frequency band

| band | n lemmas | d0 | d1 | d2 | d3 | d4+ | UNREACHABLE | unreachable rate |
|---|---|---|---|---|---|---|---|---|
| f >= 100 | 742 | 384 | 39 | 11 | 7 | 7 | 294 | **0.396** |
| 30-99 | 1,460 | 329 | 80 | 25 | 10 | 13 | 1,003 | 0.687 |
| 10-29 | 2,567 | 238 | 85 | 32 | 24 | 26 | 2,162 | 0.842 |
| 4-9 | 3,539 | 156 | 84 | 29 | 16 | 9 | 3,245 | 0.917 |
| 2-3 | 4,463 | 32 | 65 | 12 | 7 | 6 | 4,341 | 0.973 |
| 1 | 4,041 | 20 | 18 | 4 | 4 | 4 | 3,991 | 0.988 |

**Frequency is the dominant predictor.** Unreachability climbs monotonically from 40% for the
742 most frequent lemmas to 99% for hapaxes. But note the head is not solved either: even in the
f>=100 band, 294 lemmas -- 40% of the corpus's most frequent content vocabulary -- have no path.

### (b) Proper nouns

Heuristic (corpus-derived, not from a tagger): a lemma is PROPER if >= 50% of its
non-sentence-initial token occurrences are capitalized, with >= 2 such occurrences. 2,656 PROPER
/ 14,156 COMMON.

| class | n | d0 | d1 | 2-4+ | UNREACHABLE | unreachable rate |
|---|---|---|---|---|---|---|
| PROPER | 2,656 | 138 | 83 | 14 | 2,421 | **0.911** |
| COMMON | 14,156 | 1,021 | 288 | 232 | 12,615 | **0.891** |

**Proper nouns are NOT the story.** Their unreachable rate (91.1%) is barely above common words
(89.1%), and they are only 16.1% of the unreachable population. Removing every proper noun would
move the headline from 89.4% to 89.1%.

### (c) Concreteness (Brysbaert et al. BRM `Conc.M`)

10,587 of 16,812 corpus lemmas covered; 6,225 not covered.

| band | n | UNREACHABLE | unreachable rate |
|---|---|---|---|
| Conc >= 4.0 | 2,802 | 2,416 | 0.862 |
| 3.0-3.99 | 2,786 | 2,401 | 0.862 |
| 2.0-2.99 | 3,527 | 3,156 | 0.895 |
| Conc < 2.0 | 1,472 | 1,309 | 0.889 |
| NOT COVERED | 6,225 | 5,754 | 0.924 |

Mean concreteness by distance: d0 **3.20**, d1 **3.49**, d2 3.62, d3 3.56, d4+ 3.70,
UNREACHABLE **3.16** (n=9,282 rated).

**Concreteness does NOT predict distance-to-frontier.** The unreachable rate is flat to within
3.3 points across the whole concreteness range, and the unreachable set's mean concreteness
(3.16) is essentially the frontier's own (3.20). If anything the *reachable-but-not-frontier*
words are slightly MORE concrete than the frontier. The only band that stands out is
NOT-COVERED-by-Brysbaert (92.4% unreachable) -- technical and proper vocabulary, which is a
coverage confound, not a concreteness finding.

**Combined answer to "are the far words the abstract ones, the rare ones, or the proper nouns":
the RARE ones, decisively. Not the abstract ones, and not the proper nouns.**

---

## 5. The decisive number: distance exactly 1

**371 corpus lemmas (370 eligible) are exactly one definitional hop from the frontier.** These are
the immediately-bridgeable set: 2.2% of the corpus vocabulary, and they would grow the frontier's
corpus-visible footprint from 1,159 to 1,530 (+32%).

By bridge-target role: 232 bridge only to SEED lemmas, 124 only to GROUNDED lemmas, 15 to both.

**Both lemmas that died last night are in this set.** `fruit` (f=95) is distance 1 via
`fruit --COPULA--> agent` (v5 fid 967, seed target, 1 attestation). `zone` (f=71) is distance 1
via three edges, all from MULTI-WORD subjects reduced to the head `zone`:
`dead zone --GLOSSARY_COLON--> area`, `dead zone --VP4_OCCURS_WHEN--> cause` (v62),
`abyssal zone --GLOSSARY_COLON--> deep`.

### Top 100 distance-1 lemmas by corpus frequency

Format: `lemma (freq) -> bridging object [role] | source pattern`, one bridge shown (the first of
up to 3 frontier objects). Full machine-readable list with all fields is
`data/exp_frontier_distance/metrics.json` -> `distance_1_top100_by_corpus_freq`; the complete
per-lemma table is `data/exp_frontier_distance/lemma_distance.tsv` (16,812 rows).

| # | lemma | freq | bridging object | role | src / pattern |
|---|---|---|---|---|---|
| 1 | cell | 1602 | membrane | grounded | v5 APPOSITIVE |
| 2 | population | 605 | factor | grounded | v5 COPULA |
| 3 | protein | 482 | macromolecule | grounded | v5 COPULA |
| 4 | carbon | 317 | matter | seed | v62 VP4_OCCURS_WHEN |
| 5 | bacteria | 311 | domain | grounded | v5 CALLED |
| 6 | cycle | 291 | convert | grounded | v62 VP2_BY_WHICH |
| 7 | add | 283 | boss | seed | v5 APPOSITIVE |
| 8 | function | 280 | hormone | grounded | v5 CALLED |
| 9 | acid | 269 | macromolecule | grounded | v5 GLOSSARY_COLON |
| 10 | waste | 208 | country | seed | v5 COPULA |
| 11 | electron | 194 | charge | seed | v5 CALLED |
| 12 | project | 190 | college | seed | v5 COPULA |
| 13 | stage | 177 | head | seed | v62 VP4_OCCURS_WHEN |
| 14 | ocean | 176 | deep | seed | v5 APPOSITIVE |
| 15 | evolution | 174 | change | seed | v5 REFERS_TO |
| 16 | generation | 167 | making | seed | v5 COPULA |
| 17 | muscle | 163 | control | seed | v5 CALLED |
| 18 | virus | 162 | cause | seed | v5 COPULA |
| 19 | oil | 158 | fat | seed | v5 GLOSSARY_COLON |
| 20 | production | 156 | company | seed | v5 COPULA |
| 21 | photosynthesis | 147 | process | grounded | v5 COPULA |
| 22 | rate | 145 | death | seed | v5 GLOSSARY_COLON |
| 23 | effect | 141 | change | seed | v62 VP4_OCCURS_WHEN |
| 24 | potential | 137 | difference | seed | v5 CALLED |
| 25 | solution | 133 | machine | grounded | v5 COPULA |
| 26 | france | 128 | position | seed | v5 APPOSITIVE |
| 27 | layer | 126 | endoderm | grounded | v5 COPULA |
| 28 | britain | 125 | place | seed | v5 COPULA |
| 29 | view | 124 | interest | seed | v5 APPOSITIVE |
| 30 | apple | 122 | company | seed | v5 APPOSITIVE |
| 31 | atp | 121 | process | grounded | v5 APPOSITIVE |
| 32 | reproduction | 121 | generate | grounded | v62 VP4_OCCURS_WHEN |
| 33 | elements | 117 | table | seed | v5 COPULA |
| 34 | insect | 116 | food | seed | v5 COPULA |
| 35 | meiosis | 116 | process | grounded | v5 GLOSSARY_COLON |
| 36 | infection | 113 | human | seed | v62 VP4_OCCURS_WHEN |
| 37 | artist | 112 | king | seed | v5 CALLED |
| 38 | flow | 108 | body | seed | v62 VP2_BY_WHICH |
| 39 | charity | 106 | trust | seed | v5 APPOSITIVE |
| 40 | flower | 97 | trait | grounded | v5 COPULA |
| 41 | carbohydrate | 96 | macromolecule | grounded | v5 COPULA |
| 42 | egg | 95 | process | grounded | v5 COPULA |
| 43 | **fruit** | 95 | agent | seed | v5 COPULA |
| 44 | prison | 94 | blow | seed | v5 APPOSITIVE |
| 45 | biology | 92 | study | grounded | v5 GLOSSARY_COLON |
| 46 | signal | 92 | convert | grounded | v62 VP4_OCCURS_WHEN |
| 47 | shock | 90 | lose | seed | v62 VP4_OCCURS_WHEN |
| 48 | replication | 88 | process | grounded | v5 COPULA |
| 49 | adaptation | 85 | trait | grounded | v5 CALLED |
| 50 | china | 85 | bag | seed | v5 COPULA |
| 51 | economy | 84 | mistake | seed | v5 APPOSITIVE |
| 52 | mutation | 83 | change | seed | v5 APPOSITIVE |
| 53 | survey | 82 | report | seed | v5 APPOSITIVE |
| 54 | respiration | 81 | break | seed | v5 CALLED |
| 55 | sunlight | 78 | factor | grounded | v5 COPULA |
| 56 | theory | 78 | test | seed | v5 GLOSSARY_COLON |
| 57 | fertilization | 77 | process | grounded | v5 COPULA |
| 58 | phase | 76 | second | seed | v5 GLOSSARY_COLON |
| 59 | variation | 76 | difference | seed | v5 COPULA |
| 60 | antigen | 75 | macromolecule | grounded | v5 GLOSSARY_COLON |
| 61 | supporter | 73 | issue | grounded | v5 APPOSITIVE |
| 62 | antibody | 72 | agent | seed | v5 COPULA |
| 63 | **zone** | 71 | area | seed | v5 GLOSSARY_COLON |
| 64 | bowie | 70 | act | seed | v5 COPULA |
| 65 | eukaryote | 67 | process | grounded | v5 APPOSITIVE |
| 66 | regulation | 67 | keep | seed | v62 VP2_BY_WHICH |
| 67 | england | 64 | close | seed | v5 APPOSITIVE |
| 68 | formation | 64 | head | seed | v62 VP4_OCCURS_WHEN |
| 69 | learning | 64 | make | seed | v62 VP4_OCCURS_WHEN |
| 70 | lipid | 64 | macromolecule | grounded | v5 COPULA |
| 71 | performance | 61 | report | seed | v5 CALLED |
| 72 | moocs | 60 | idea | seed | v5 COPULA |
| 73 | salary | 60 | start | seed | v5 GLOSSARY_COLON |
| 74 | expression | 56 | information | seed | v62 VP1_PROCESS_OF |
| 75 | banks | 55 | man | seed | v5 APPOSITIVE |
| 76 | plate | 55 | plane | seed | v5 CALLED |
| 77 | gradient | 54 | area | seed | v5 GLOSSARY_COLON |
| 78 | digestion | 53 | move | seed | v62 VP4_OCCURS_WHEN |
| 79 | mandela | 53 | figure | seed | v5 APPOSITIVE |
| 80 | allergy | 52 | reason | seed | v5 COPULA |
| 81 | competition | 52 | rates | grounded | v5 APPOSITIVE |
| 82 | rain | 52 | cause | seed | v5 GLOSSARY_COLON |
| 83 | ribosome | 52 | macromolecule | grounded | v5 COPULA |
| 84 | smoke | 51 | cover | seed | v5 APPOSITIVE |
| 85 | explanation | 48 | tropics | grounded | v5 COPULA |
| 86 | chromatid | 47 | hold | seed | v5 CALLED |
| 87 | moon | 46 | hand | seed | v5 CALLED |
| 88 | overall | 44 | sell | seed | v5 APPOSITIVE |
| 89 | wood | 44 | officer | seed | v5 APPOSITIVE |
| 90 | revolution | 43 | book | seed | v5 APPOSITIVE |
| 91 | bay | 42 | issue | grounded | v5 COPULA |
| 92 | proton | 42 | charge | seed | v5 CALLED |
| 93 | reptile | 42 | fish | seed | v5 APPOSITIVE |
| 94 | allen | 40 | old | seed | v5 COPULA |
| 95 | track | 39 | sound | seed | v5 APPOSITIVE |
| 96 | loneliness | 38 | problem | seed | v5 COPULA |
| 97 | vienna | 38 | city | seed | v5 COPULA |
| 98 | august | 36 | earth | seed | v5 APPOSITIVE |
| 99 | genetics | 36 | study | grounded | v5 COPULA |
| 100 | tower | 36 | set | seed | v5 APPOSITIVE |

**This list is NOT quality-filtered and no hand-scoring was done on it.** It answers "which lemmas
have a relational path" and nothing else. Several rows are visibly not usable meanings
(`china -> bag`, `prison -> blow`, `moon -> hand`, `add -> boss`, `wood -> officer`); no rate is
claimed for that, see section 6.

---

## 6. Degree distribution, and whether hubs make distance-1 cheap

CORE graph: 2,357 nodes, 2,239 edges. Mean out-degree 1.46, mean in-degree 1.91, max in-degree 49.

In-degree histogram: 799 nodes with in-degree 1, 168 with 2, 84 with 3, 42 with 4, 62 with 5-9,
**18 with 10-49**, 0 above 49.
Out-degree histogram: 1,075 with 1, 312 with 2, 100 with 3, 28 with 4, 18 with 5-9, 2 with 10-49.

Top in-degree nodes: `process` 49, `structure` 31, `cell` 24, `molecule` 19, `study` 18,
`organism` 17, `animal` 13, `organ` 12, `division` 12, `body` 11, `stage` 11, `plant` 11,
`species` 11, `substance` 10, `clade` 10.
**Top-10 in-degree nodes account for only 9.2% of all edges.**

Restricting to the 371 distance-1 lemmas: they use **182 distinct frontier nodes** as bridge
targets across 406 bridge links. The most-used bridge target is `process` (47 of 371 = 12.7%),
then `study` (18), then `body`/`change` (8 each). Top-2 targets = 16.0% of bridge links; top-20 =
41.6%. Counterfactual: deleting `process` from the frontier drops distance-1 from 371 to 332
(-10.5%); deleting the top-5 in-degree nodes drops it to 315 (-15.1%); top-10 to 307 (-17.3%).

**Verdict: `process` IS a hub and does make a tenth of distance-1 cheap, but hubs do NOT dominate
-- 89.5% of distance-1 survives removing the single biggest hub, and 82.7% survives removing the
top ten.** `thing` is not a hub here at all (in-degree 1). The graph is dominated by degree-1
leaves, not by a small hub core.

---

## 7. Honest limits (asked for explicitly)

**(a) Reachability is not correctness.** Distance over extractor-supplied edges measures
RELATIONAL REACHABILITY: whether a chain of extracted definitional facts connects a lemma to a
grounded anchor. It says nothing about whether traversing that chain would produce a correct
meaning. `fruit --COPULA--> agent` is a distance-1 edge and is also, read plainly, not a usable
definition of fruit. These are different claims and this document only supports the first.
Nothing here was hand-scored.

**(b) How much rests on the 64%-scored facts.** Of the 371 distance-1 lemmas, **333 (89.8%)
bridge via a v5 edge only**, 31 (8.4%) via a v62 edge only, 7 (1.9%) via both. On edges, v5
supplies 2,023 of 2,239 CORE edges (90.4%) and v62 supplies 216 (9.6%). So the distance-1 result
rests almost entirely on the 2,092 definitional facts hand-scored at **64% MEANINGFUL**
(`notes/director_handscore_b3_v5_termboundary_2026-08-12.md`), NOT on the 221 predicate facts
scored at 94%. Taken at face value, a naive 0.64 multiplier on the v5-only portion would put the
"MEANINGFUL bridge" count near 213+29 -- **that arithmetic is NOT performed as a claim here**,
because the hand-score was drawn over facts, not over the specific 371 bridging edges, and
distance-1 edges are not a random sample of facts.

**(c) Hubs: reported above** -- `process` carries 12.7% of bridge links; hubs do not dominate.

### What I could NOT verify

* **That any bridge is a correct meaning.** No hand-scoring, no quality tier, no accuracy rate.
* **That the loop could actually traverse these edges.** This is a graph measurement over fact
  FILES. The read-out's live candidate set is `space.anchor_matrix()`, which these facts do not
  populate; I did not run the loop and I make no claim that adding a distance-1 lemma to the
  frontier is mechanically possible in the current code, nor what it would score.
* **Head-lemma reduction is lossy.** 615 / 2,092 v5 subjects (29.4%) and 111 / 221 v62 subjects
  (50.2%) are multi-word. Reducing them to the head COLLAPSES distinct terms into one node --
  `dead zone` and `abyssal zone` both become `zone`, 11 different `* cycle` terms become `cycle`.
  This INFLATES connectivity and therefore UNDERSTATES the unreachable count. I did not measure a
  multi-word-preserving variant.
* **The proper-noun label.** A capitalization heuristic over corpus tokens, not a POS tagger; it
  will misclassify sentence-initial-only proper nouns and title-cased headings. The v5 files'
  own `subject_type` field (1,763 COMMON / 329 PROPER) was not used as the label because it
  covers only fact subjects, not the 16,812-lemma vocabulary.
* **Corpus frequency semantics.** Frequency = sentences containing the lemma, not token count;
  a lemma occurring twice in one sentence counts once. This matches `content_lemmas` and
  reproduces the previously reported `fruit`=95 / `zone`=71.
* **Whether v3's 318 extra edges are trustworthy.** They were excluded from PRIMARY on the
  documented grounds that v3 predates the `lemma_word` fix; I did not audit them individually.
* **Any claim about a DIFFERENT corpus or seed.** Every number is specific to the 34,169-sentence
  v5 line-aware corpus and the 1000-word base-vocabulary seed. The 117,642-sentence OpenStax
  corpus is not ingested and is not measured here.
* **Relation-type weighting.** `ISA`, `ENABLING_CONDITION`, `PROCESS_ACTION` etc. were all treated
  as one hop. Whether a `PROCESS_ACTION` hop is the same kind of bridge as an `ISA` hop is not
  addressed.
