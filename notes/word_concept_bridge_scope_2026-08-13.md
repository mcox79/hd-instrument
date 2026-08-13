# Scoping the lemma -> concept bridge (2026-08-13)

**SCOPE: DESIGN + MEASUREMENT ONLY. Nothing built, no code modified, nothing committed.**
`data/exp_anchor_pool_expansion_v1/` untouched; no process signalled. This note is the only file
written. Follows `notes/multisource_lookup_wiring_audit_2026-08-13.md`, which established that the
multi-source lookup stack works and is unreachable from the reading loop, and that the gap is a
missing TRANSLATION LAYER rather than a missing wire.

Read-only measurements were RUN this pass against `data/cskg_foundation_v1/` (1,213,912 edges,
re-counted), `data/exp_frontier_distance/lemma_distance.tsv` (16,812 rows),
`data/exp_definitional_predicate_v62/predicate_facts_v62.jsonl` (221) and
`data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl` (2,092). Every
number tagged MEASURED below was computed here, not copied.

---

## HEADLINE (four sentences)

1. **The lemma -> concept-node handoff is nearly trivial and glass-box-clean: CSKG node names are
   bare surface strings** (`{"subject": "eleven", ..., "obj": "sign"}`,
   `data/cskg_foundation_v1/edges_shard_00.jsonl:1`), so the handoff is an exact dictionary
   match. **A precedent already does exactly this** at
   `experiments/exp_state_of_mind_relevance_gather_reasoning_union_v1.py:168` (`if o in vset`).
2. **Coverage is not the blocker either.** MEASURED: 9,574 / 16,812 corpus lemmas (**56.95%**) are
   exact CSKG node strings; **92.7%** in the `f>=100` band.
3. **The blocker is that CSKG has no sense inventory and the ambiguity therefore relocates into
   EDGE selection, where the only available signal is the context vector already measured at
   1-3% MEANINGFUL.** MEASURED fanout for a corpus lemma used as CSKG subject: median 3, mean
   31.5, p90 68, max 7,709 (`light` 961, `plant` 622, `fruit` 405).
4. **The strongest counter-argument is now MEASURED, not rhetorical.** Within-2-hop CSKG
   connectivity between our own hand-scored definition subjects and their correct objects is
   **9.95% (v62) / 14.91% (v5)**, and a scramble control that pairs each object with a WRONG
   subject reproduces **8.69% / 10.78%** of it. CSKG contains our words but largely not our
   definitional relations, and at 2 hops mere reachability is close to content-free.

---

## 1. CONTRACT A -- what the lookup stack actually expects

### 1a. Item identity (the PARSE-stage type)

`hdlab/three_tier_loop.py:85-95`:

```python
def gap_item_key(subject: str, relation: str, candidate: str) -> str:
    return f"{subject}{KEY_SEP}{relation}{KEY_SEP}{candidate}"   # KEY_SEP = "||" (:81)
```

- Type: a single `str`. Not a URI, not a synset, not a sense id.
- `parse_gap_item_key` (`:98-103`) is the inverse and **raises `ValueError` on anything without
  exactly 3 `||`-separated parts** -- the one hard type constraint on the whole path.
- `DEFAULT_RELATION = "GAP_FACT"` (`:80`).
- Semantics (`:86-94`, verbatim): one `(subject, relation)` gap with several competing candidate
  answers becomes **several independently-gated items, one per candidate**, each gated on its own
  exposure/consistency. So the bridge must emit **one key per candidate**, not one key per lemma.

### 1b. Entry points and their signatures

| Entry point | file:line | What the caller must already hold |
|---|---|---|
| `ThreeTierLoop.__init__(foundation_store, seed_base, n_dim, relation, prelim_trust)` | `three_tier_loop.py:150` | an `HDFactStore` |
| `ThreeTierLoop.encounter(item_key, pole, context_vec, episode_id, pass_idx, *, also_strict=True)` | `:161` | the item key, a pole (`"POS"`/`"NEG"`), a **`np.ndarray` context vector**, an episode id, a pass index |
| `ThreeTierLoop.consolidate(pass_idx, cluster_key_fn, novelty_thresh, *, register_fn=gap_register_fn, ...)` | `:178` | a `Callable[[str], str]` cluster key fn and a float novelty threshold |
| `ThreeTierLoop.answer(item_key)` | `:197` | returns `(tier_tag, object_or_None)`, tier_tag in `FOUNDATION_RESOLVED` / `MIDDLE_RESOLVED` / `UNRESOLVED`; **priority order, NOT score fusion** (`:198-201`, Gap G1) |
| `gather_and_reason(query_vec, item_names, codebook, ent_idx, hop1_kg, hop2_kg, start_idx, hop1_rel_idx, hop2_rel_idx, k1, k2, n_ent, *, k_peel=25, sim_floor=0.05)` | `:120-139` | **the heavy contract, see below** |

`gather_and_reason` is where the real cost sits. It requires, all pre-built by the caller:

- `query_vec: np.ndarray` -- a real-valued concat(Re,Im) FHRR probe (`gather_reason.real_to_concat`,
  `gather_reason.py:66-70`), typically decoded from a `situation_model_accumulate.RelationRegister`.
  **`gather_and_reason` deliberately does NOT build this** (`three_tier_loop.py:126-129`).
- `item_names: List[str]` + `codebook: np.ndarray` -- built by `build_codebook`
  (`gather_reason.py:73-79`), sorted-name order, one FHRR vector per candidate item, **held in
  memory**.
- `ent_idx: Dict[str,int]` -- name -> integer entity index.
- `hop1_kg`, `hop2_kg` -- two `hdlab.kg_traversal.KGStore` objects with triples already ingested,
  and integer relation indices `hop1_rel_idx` / `hop2_rel_idx`.

**Load-bearing consequence:** `gather_reason.ca3_relevance_gather` (`:82-113`) and `fanout_two_hop`
(`:116-145`) **query no database**. The "sources" are entirely whatever the caller pre-loaded into
the codebook and the two `KGStore`s. There is no lazy/streaming path, no per-question fan-out. A
bridge cannot "call the lookup on a word"; it must first materialise a codebook and a KG index for
a candidate neighbourhood.

### 1c. Same-concept judgement

`experiments/exp_three_tier_loop_concept_coherence_v1.py:191` sets
`CONCEPT_MATCH_THRESHOLD = SIMILARITY_LINK_THRESHOLD` = **0.50**
(`hdlab/lexical_similarity.py:624`). The metric (cell docstring `:62-73`) **"keeps ONLY words IN
hdlab.lexical_similarity.CONCEPT_FEATURES"** -- words outside the hand lexicon are DROPPED, not
scored. `len(CONCEPT_FEATURES) == 359` MEASURED.

---

## 2. CONTRACT B -- what the reading loop holds at the instant of detection

`hdlab/reading_grounding_loop.py`, inside `process_sentence` (`:1006`):

```
:1050  for lemma in content_lemmas(sentence):        # sorted(set(normalize_lemma(w)))  :198-201
:1064      it = state.library.items.get(lemma)
:1068      if not is_gap(state, lemma): continue     # GapDetector margin < 0.625
:1075      ctx = _encode(sentence, lemma)            # context_vector_masked  :204
:1076      if not np.any(ctx != 0.0): continue
:1078      flagged = state.library.flag(lemma, episode_id, "POS", ctx, pass_idx, ...)
```

**Concretely in hand at `:1068`, and nothing else:**

| Datum | Type | Source |
|---|---|---|
| `lemma` | `str`, a normalized single word (`normalize_lemma` = `lemma_word`, `:186-195`) | `content_lemmas(sentence)` |
| `sentence` | `str`, the raw sentence | caller |
| `ctx` | `np.ndarray`, dim `CTX_D`, bag-of-content-words, target masked out | `:1075` |
| `episode_id`, `pass_idx` | `str`, `int` | caller |
| `state.library` | `Library` of prior traces for this lemma | `:951` |
| `state.space` | `ConceptSpace` -- the anchor pool `canonicalize` argmaxes over | `:952` |
| `state.known_seed` | `frozenset` of seed lemmas | `:954` |
| `state.store` | `HDFactStore` foundation | `:950` |
| `state.evidence[lemma]` | provenance rows `{episode_id, pass_idx, sent_id}` | `:1087-1091` |

**What is NOT in hand:** no POS tag, no dependency parse, no sense id, no document id beyond
`episode_id`, no candidate set of any kind. `is_gap` (`:1001`) probes
`gap_detector.familiarity(lemma, KNOWN_RELATION="KNOWN_WORD", KNOWN_OBJECT="CORE")` -- a fixed
relation/object pair, so the detector returns only a **boolean-ish margin**, never a candidate.
`FamiliarityResult.matched_key` (`gap_detector.py:125`) holds the nearest KNOWN triple, which is
not a candidate meaning for the unknown word.

There is **no hook**: `process_sentence`'s signature (`:1006-1012`) has no callable parameter that
could reach an external source, and neither does `checkpoint`.

### The shape of the mismatch, stated exactly

| | reading loop | lookup stack |
|---|---|---|
| unit | one lemma `str` | one `subject\|\|relation\|\|candidate` `str` |
| what it has | 1 word + 1 context vector | needs subject, relation AND candidate |
| candidate source | `state.space` anchors only (`:1055`, `:1297`, `:1063`) | caller-built codebook + KGStore |

**The bridge must supply the `relation` and the `candidate` -- the reading loop supplies only the
`subject`.** That is the translation layer, stated precisely.

---

## 3. THE GLASS-BOX CONSTRAINT, per option

Invariant: no external LLM at inference; no borrowed embedding/parser/reader may BE the meaning or
comprehension organ. Supplying knowledge/data/structure is permitted; supplying the MECHANISM is
not.

| Option | Verdict | Reasoning |
|---|---|---|
| **Exact string match `lemma` -> CSKG node** | **RESPECTS** | A dictionary lookup on a surface string. No learned parameters, fully auditable, invertible. It supplies DATA (which nodes exist) and the substrate keeps the decision. Precedent already in-tree at `exp_state_of_mind_...:168`. |
| **Morphological normalisation via WordNet morphy** | **RESPECTS** | Already on the live path (`thematic_role_labeler.py:241-253` via `normalize_lemma`). A morphological normaliser, not a meaning organ. Audit `notes/multisource_lookup_wiring_audit_2026-08-13.md:150-156` reached the same verdict. |
| **WordNet synsets as a CANDIDATE inventory** | **RESPECTS, with care** | Enumerating `wn.synsets(lemma)` supplies structure/data. It becomes a VIOLATION the moment WordNet's own similarity (`path_similarity`, Lesk overlap) makes the SELECTION -- then the borrowed resource is the disambiguation mechanism. `wordnet_polarity_propagation.py:159-176` already sits on that line: it uses `path_similarity` neighbour vote, which is WordNet deciding. |
| **Neural entity linker (BLINK/GENRE/ReFinED-class), or any learned bi-encoder mention-to-entity model** | **VIOLATES** | This is the standard solution and it is exactly the prohibited shape: a borrowed learned model performs the mention -> concept decision. The decision is the comprehension act. Not smuggleable via "we only use it for candidates" -- its output IS the candidate ranking. **Do not build this.** |
| **Sentence/word embeddings (SBERT, fastText, GloVe) to score candidates** | **VIOLATES** | Same reason. A borrowed distributional model would be doing the sense selection. The project already distinguishes "supplying features" from "being the read-out"; here it would be the read-out. |
| **`concept_similarity` over `CONCEPT_FEATURES`** | **RESPECTS** | Hand-authored McRae-style feature norms; glass-box, inspectable, scramble-controlled (`lexical_similarity.py:662-677`). Its problem is coverage (section 5), not legitimacy. |
| **Grounded fallback (Lancaster sensorimotor + Brysbaert)** | **RESPECTS but INERT here** | Norm tables are data. But it is **capped at `GROUNDED_CAP` 0.45, structurally below the 0.50 link threshold** (`lexical_similarity.py:589-597`), so it can never assert "same concept" -- by construction it cannot do this job. |

**Statement required by the brief:** the workable options do NOT all violate the invariant. The
candidate-GENERATION half is cleanly solvable within the invariant by exact string match. It is the
SELECTION half that has no glass-box solution currently in hand -- and the reason is not the
invariant, it is that the only in-invariant selector we own is measured broken (section 4).

---

## 4. AMBIGUITY -- named honestly

### 4a. The ambiguity is NOT where it looks

CSKG carries **no sense inventory**. MEASURED: node strings beginning `bank` number 52, but they
are `bank`, `bank_account`, `bank_airplane`, `bank_at_atm`, ... -- **multi-word PHRASE nodes, not
senses of `bank`**. There is exactly ONE node named `bank`, and it conflates the financial, river
and aviation senses. Same for `cell` (35 such strings, one bare `cell`) and `charge` (62, one bare
`charge`).

**Consequence:** `lemma -> node` is 1:1 and unambiguous. The polysemy does not disappear -- it
relocates INSIDE the single node, spread across its edges. So the disambiguation problem is
**edge selection, not node selection**.

### 4b. The size of the selection problem, MEASURED

Corpus lemmas appearing as a CSKG **subject**: 7,440 / 16,812 (44.25%). For those, the number of
outgoing edges (= candidate `(relation, candidate)` pairs the bridge would emit):

| statistic | value |
|---|---|
| median | **3** |
| mean | **31.5** |
| p90 | **68** |
| max | **7,709** |
| median distinct relations | 2 |

Per-word: `light` 961 edges / 11 relations, `plant` 622 / 10, `fruit` 405 / 9, `bank` 117 / 7,
`charge` 18 / 3, `zone` 15 / 4, `cell` 10 / 5, `protein` 9 / 5.

The distribution is brutally skewed in the wrong direction: the fanout is small for rare, low-value
words and enormous for exactly the frequent, high-value words the loop most needs.

### 4c. What would disambiguate -- and it is the broken mechanism

At `:1075` the loop holds **one signal that varies with the situation**: `ctx`, the
bag-of-content-words context vector (target masked). That is the only thing that could rank 68
candidate edges.

**That vector is the mechanism already measured as failing.** Per `notes/STATUS.md:45-57`:
three blind hand-scores at **1-3% MEANINGFUL / 73-90% NOISE**; stabilisation (F1+F3) NULL and
floor-limited; textbook swap REFUTED; co-occurrence-as-explanation refuted; role-bound structural
encoding NULL (0% vs 2%) despite binding mechanically. MEMORY records that context-conditioned
sense selection HARD_FAILED both indexes, **below the random floor**.

**Verdict, stated plainly as the brief requires: yes -- the disambiguator is the mechanism we
already know is broken. A bridge built on it would INHERIT the existing failure, not fix it.** The
bridge would convert "argmax over ~1,159 corpus-visible anchors" into "argmax over ~1,159 anchors
plus up to 68 KG edges", using the same scoring signal. There is no independent evidence that
enlarging the candidate set helps when the selector is the failing component; MEMORY's own
`downstream_bottleneck_trace` finding (bottleneck is DOWNSTREAM of feature selection) points the
opposite way.

The one honest caveat in the other direction: KG edges carry a **typed relation** (`/r/MadeOf`,
`/r/IsA`), which anchors in `state.space` do not. A relation-typed candidate is a genuinely
different object from an untyped anchor, and it is not strictly proven that the same selector fails
on it. That is a hypothesis, not a finding, and D2 below is the cheap way to test it.

---

## 5. THE 359-ENTRY CEILING -- what it does and does not cap

MEASURED:

| quantity | value |
|---|---|
| `len(CONCEPT_FEATURES)` | **359** |
| corpus lemmas (16,812) covered by `CONCEPT_FEATURES` | **310 = 1.84%** |
| `CONCEPT_FEATURES` entries that are CSKG nodes | 329 / 359 |
| corpus lemmas that are exact CSKG nodes | **9,574 = 56.95%** |
| corpus lemmas that are CSKG subjects | 7,440 = 44.25% |

Exact-match coverage by corpus frequency band:

| band | n lemmas | in CSKG | rate |
|---|---|---|---|
| f >= 100 | 742 | 688 | **0.927** |
| 30-99 | 1,460 | 1,276 | 0.874 |
| 10-29 | 2,567 | 1,847 | 0.720 |
| 4-9 | 3,539 | 2,092 | 0.591 |
| 2-3 | 4,463 | 2,056 | 0.461 |
| 1 | 4,041 | 1,615 | 0.400 |

**Assessment. The 359 entries do NOT cap candidate GENERATION.** Generation is exact string match
against 475,168 distinct CSKG node strings (MEASURED), and reaches 57% of the vocabulary / 93% of
the frequent head. The audit's framing of 359 as "the ceiling on the bridge" is too pessimistic for
that half.

**The 359 entries DO hard-cap the same-concept JUDGEMENT step**, and that cap is absolute for two
compounding reasons:
1. The concept-coherence metric **drops** out-of-lexicon words rather than scoring them
   (`exp_three_tier_loop_concept_coherence_v1.py:62-73`). At 1.84% corpus coverage, on real reading
   text almost every word is dropped and the metric degenerates.
2. The grounded fallback that covers ~39,707 words **cannot rescue it**: capped at 0.45, strictly
   below the 0.50 link threshold (`lexical_similarity.py:589-597`), so it is mathematically
   incapable of returning a "same concept" verdict. Raising the cap is not a free fix -- the cap
   exists because MEASURED `apple`/`orange` raw cosine 0.952 vs `happy`/`joyful` 0.962 are
   statistically inseparable (`lexical_similarity.py:594-597`).

**Realistic coverage of the bridge end-to-end, as a hypothesis not a finding:** candidate
generation ~57% of vocabulary (93% of frequent words); same-concept clustering effectively ~2%;
so a bridge that needs the clustering step is capped near 2%, and a bridge that does NOT need it is
capped near 57% on generation and then gated by the selection problem in section 4.

---

## 6. CANDIDATE DESIGNS

### D1 -- EXACT-STRING NODE MATCH, candidates only, no selection (cheap)

**What it does.** At `:1068`, after the gap fires: look `lemma` up in a prebuilt CSKG node index.
If present, emit its outgoing edges as `gap_item_key(lemma, relation, obj)` keys. Do not select
among them; do not write to `state.space`; only COUNT and LOG what the bridge would have offered.
A pure instrumentation build.

- **Glass-box verdict: RESPECTS.** Dictionary lookup, no learned component, precedent at
  `exp_state_of_mind_...:168`.
- **Failure mode.** Produces a large unranked candidate pile with no way to choose (median 3 but
  p90 68, max 7,709), and offers no answer for the 43% of lemmas absent from CSKG. It also cannot
  distinguish the correct sense because the node is sense-conflated (4a).
- **CAN-FAIL DISCRIMINATOR (cheap, hours not days).** *Known-answer recall.* For each of the 221
  v62 facts (94% hand-scored) and 2,092 v5 facts (64%), does `obj` appear among the candidates
  D1 emits for `subject_head`, at K<=2 hops? **Pre-registered ceiling, MEASURED this pass:**
  reachability within 2 hops is 22/221 = **9.95%** (v62) and 312/2,092 = **14.91%** (v5); 1-hop
  alone is 3/221 and 35/2,092. **Pre-registered floor, MEASURED this pass:** a scramble control
  pairing each object with a WRONG subject head reaches **8.69%** (v62) and **10.78%** (v5).
  D1 FAILS if ranked recall@10 does not exceed the scramble arm by a paired margin excluding 0.
  Given the ceiling is 9.95% and the scramble floor is 8.69%, **D1 is very likely to fail on v62 by
  construction** -- which is precisely why this is worth running first and cheaply.

### D2 -- RELATION-TYPED CANDIDATE INJECTION into the read-out (medium)

**What it does.** D1's candidates, but the top-k by CSKG edge weight/trust are injected into
`state.space` as anchors carrying their relation type, so `canonicalize` (`:599`) can argmax over
them alongside existing anchors. This is the smallest change that lets a KG candidate actually WIN
a read-out. Architecturally it is the same shape as the default-OFF `anchor_pool` hook at `:1063`.

- **Glass-box verdict: RESPECTS.** All parts are owned: string match (data), CSKG edge trust
  (data), `canonicalize` cosine argmax (our own organ). No borrowed model decides.
- **Failure mode. This is the design that inherits the known failure.** The selector is
  `canonicalize`'s cosine over the context vector -- measured 1-3% MEANINGFUL. Adding candidates to
  a broken argmax plausibly makes the read-out WORSE by adding distractors: MEASURED, the p90 lemma
  would contribute 68 new competitors against a current anchor field of ~1,159.
- **CAN-FAIL DISCRIMINATOR.** *Mechanistic, not hand-scored:* **tautology-refusal rate and argmax
  displacement.** Run with and without injection on the same corpus and compare (a) the
  `REFUSAL_TAUTOLOGY` rate in `state.refusals` (`:1135`) -- injection should REDUCE it if the pool
  was the binding constraint; (b) the fraction of lemmas whose argmax changes; (c) the fraction of
  final objects that are KG-sourced. D2 FAILS if tautology rate does not fall, or if argmax
  displacement is high (>50%) while known-answer recall (D1's metric) does not rise -- that
  combination means it is churning, not resolving.
  **Note the trap:** MEMORY records that 65.7% of existing grounded facts are
  `(X, GROUNDED_MEANING, X)` tautologies, so tautology rate is a genuinely sensitive, non-saturated
  telemetry channel here.

### D3 -- WORDNET SYNSET INVENTORY as the sense layer, CSKG for relations (heavier)

**What it does.** Use `wn.synsets(lemma)` to get the one thing CSKG lacks -- an explicit sense
inventory -- then attach CSKG edges to whichever synset shares lemmas with the edge's object. The
bridge emits `(lemma, relation, candidate)` keys tagged by synset.

- **Glass-box verdict: RESPECTS ONLY IF selection stays ours.** Enumerating synsets and their lemma
  sets is data. The moment `path_similarity` / Lesk gloss overlap picks the sense, WordNet is the
  disambiguation mechanism and it **VIOLATES**. `wordnet_polarity_propagation.py:159-176` already
  crosses that line, so this design must not reuse that function's Stage B.
- **Failure mode.** Two, both previously observed. (i) **Coverage:**
  `exp_combined_dictionary_consequence_word_learning_tool_v1` HARD_FAILed with dictionary coverage
  6/33 lemmas. (ii) **The sense-selection step is still the broken selector** -- WordNet supplies
  the inventory but not the choice, so D3 buys structure and inherits the same failure as D2, at
  much higher cost.
- **CAN-FAIL DISCRIMINATOR.** *Sense-inventory utility:* measure the fraction of gap lemmas for
  which WordNet returns >1 synset AND the CSKG edges partition non-trivially across them. D3 FAILS
  if the partition is degenerate (most edges land on one synset or on none) -- i.e. if the sense
  inventory does not actually carve the candidate set, D3 reduces to D1 at greater expense. This is
  cheap to pre-check and should gate the build.

---

## 7. RECOMMENDED PRIMARY DISCRIMINATOR (not a hand-scored quality delta)

**Ranked known-answer recall@k over the 221 + 2,092 held facts, run WITH the scramble-subject
control in the same experiment.**

Rationale, per the standing 2026-08-13 lesson (two experiments unresolvable because a 50-row sample
cannot detect a difference at a 1-3% floor): this metric needs **no new hand-scoring**, uses
answers already scored at 94% and 64%, has n = 2,313 rather than 50, and is mechanistically
computable.

**Pre-registered bands, all MEASURED this pass rather than guessed:**

| quantity | v62 (n=221, 94% scored) | v5 (n=2,092, 64% scored) |
|---|---|---|
| subject head present in CSKG | 148 (0.670) | 1,306 (0.624) |
| both endpoints present | 134 (0.606) | 1,138 (0.544) |
| connected at 1 hop | 3 (0.0136) | 35 (0.0167) |
| **connected within 2 hops (CEILING)** | **22 (0.0995)** | **312 (0.1491)** |
| **scramble-subject control (FLOOR)** | **0.0869** (min 0.0769, max 0.0995, 5 seeds) | **0.1078** (min 0.1018, max 0.1123) |

**Critical caveat, and it is the most important sentence in this note:** the scramble control
already reproduces **87% of v62's and 72% of v5's** within-2-hop reachability. **Reachability at 2
hops is therefore close to content-free** -- CSKG's hub structure connects almost anything to
almost anything in two steps. Consequently:

- Do **NOT** use raw reachability as the discriminator; it is near-vacuous and would produce a
  false positive. This is exactly the "control that reproduces the win from the WRONG source"
  pattern the standing layered-controls discipline warns about.
- The discriminator must be **RANKED recall@k (k = 1, 5, 10)** with the scramble arm ranked
  identically, so the claim is "the right subject ranks the right object higher than a wrong
  subject does", not "a path exists".
- Pre-register that on v62 the ceiling (0.0995) sits at the scramble maximum (0.0995). **v62 alone
  cannot resolve this.** Use v5 as primary (ceiling 0.1491 vs scramble 0.1078, a real gap) and
  report v62 as the higher-precision but underpowered secondary.

Secondary mechanistic discriminator: **tautology-refusal rate delta** (D2), which is sensitive
because the tautology rate is currently 65.7% and nowhere near saturation.

---

## 8. THE STRONGEST ARGUMENT AGAINST BUILDING THIS -- and whether it defeats the proposal

**The argument.** *A bigger candidate pool cannot help when selection is independently broken, and
we have measured that selection is broken.* Five routes have been eliminated on the read-out path
(`STATUS.md:45-57`), all with the candidate pool held roughly fixed, and the trace concluded the
bottleneck is DOWNSTREAM of feature selection. The bridge is a CANDIDATE-SUPPLY intervention. On
the `banana` case the structured comparator isolated the correct hypernym feature `(^nsubj, fruit)`
and the arm still scored 0/50 -- the right candidate was present and still did not win. Adding 68
KG edges to that argmax adds distractors to a selector that already fails with the answer in hand.

**The measured reinforcement, new this pass.** Even granting a perfect selector, the ceiling is
low: only 9.95% / 14.91% of our own known answers are reachable within 2 hops, and a scramble
control reproduces most of that. CSKG is a COMMONSENSE graph; our facts are DEFINITIONAL/textbook.
61% of the pairs have both endpoints present as nodes and are still not connected by the relations
we need. **CSKG has our words but not our relations.** This is the same class of finding as the
`genuine_cross_source_corroboration_v1` HARD_FAIL: source thinness.

**Does it defeat the proposal?** **It defeats D2 and D3 as builds right now. It does NOT defeat
D1.** The distinction:

- D2/D3 spend real effort to feed a selector measured at 1-3%, over a source measured at a ~10-15%
  answer ceiling with a near-vacuous 2-hop control. Building either now is the "easy adjacent
  thing" pattern, and MEMORY's standing discipline says select by brain-foundational-correctness,
  not by availability. **Recommend: do not build D2 or D3 yet.**
- D1 is not a candidate-supply intervention at all -- it is a MEASUREMENT that costs little and
  resolves whether the multi-source stack has anything to offer the reading loop. The audit's own
  open item #1 ("whether the three-tier loop would help the reading loop if wired -- nothing tests
  that pairing") is exactly what D1 closes. **Recommend: run D1's discriminator; treat it as a
  source-adequacy test, not as a wiring step.**

Honest counter-counter-argument, offered against my own recommendation: this note's numbers already
go a long way toward answering D1 without building it. If the 2-hop ceiling of 14.91% against a
10.78% scramble floor is judged decisive on its own, the correct action is to **record the source
as inadequate and stop**, rather than to build even the cheap version. I lean toward running the
ranked version because reachability and ranked recall are genuinely different measurements and I
have only measured the former -- but I hold that as a preference, not a finding.

**What this does NOT license:** none of the above says the reading loop should never consult an
external source. It says *CSKG specifically* is a poor match for *definitional* gaps. The research
shopping list in `notes/research_three_tier_knowledge_sourcing_gather_layer_2026-08-11.md`
(Reactome, Rhea, WorldTree) targets typed definitional relations and is not refuted by anything
here.

---

## 9. WHAT I COULD NOT VERIFY

1. **That ranked recall@k differs from reachability.** I measured 1-hop and 2-hop REACHABILITY and
   its scramble control. I did NOT run `fanout_two_hop`'s actual scoring, so I do not know what
   recall@10 would be. Every ranked number in section 7 is a proposed measurement, not a result.
2. **Whether the bridge would help or hurt the read-out.** Unchanged from the prior audit's open
   item #1. No cell imports both stacks; I ran neither together. Section 4c's verdict that the
   bridge would inherit the failure is a **strong hypothesis grounded in the measured selector
   failure, not a demonstration**.
3. **Head-lemma reduction is lossy and I inherited it.** I reduced multi-word subjects to the last
   alphabetic token then `lemma_word` -- the same convention as
   `notes/frontier_distance_2026-08-13.md`, which flags that 29.4% of v5 and 50.2% of v62 subjects
   are multi-word and that collapsing them INFLATES connectivity. My 9.95% / 14.91% ceilings are
   therefore, if anything, OVERSTATED.
4. **The scramble control I used permutes SUBJECTS within the fact set**, not a uniform draw from
   all 475,168 CSKG nodes. It is the conservative choice (permuted subjects have realistic degree),
   but it is one control, not the full battery. Only 5 seeds.
5. **ConceptNet 5.7, ATOMIC, CauseNet, Wikidata coverage.** I measured CSKG only. The 498 MB
   ConceptNet gz was not decompressed. A different source could have a different answer, and
   nothing here should be read as "external sources cannot help".
6. **`director_kb` (1,288,991 entities) as an alternative gather layer.** Not evaluated. It is a
   build-time index queried by the agent's tooling; whether it could serve the substrate at read
   time is unexamined.
7. **Whether `CONCEPT_FEATURES` could be grown cheaply.** I measured its size and coverage. I did
   not assess authoring cost per entry, nor whether the 39,707-word grounded asset could be
   re-derived into feature-norm form under the invariant.
8. **Runtime cost of the bridge.** `gather_and_reason` needs an in-memory codebook and two KGStore
   indices per query neighbourhood. I did not measure memory or latency for a 475,168-node
   codebook, and I suspect it does not fit the reading loop's per-lemma budget -- unverified.
9. **Any claim about a different corpus or seed.** Everything is specific to the 34,169-sentence v5
   line-aware corpus and the 1,000-word base-vocabulary seed. The 117,642-sentence OpenStax corpus
   is not ingested.
10. **I did not re-run any experiment cell or self-test this pass** (a detached run is live). All
    verdicts cited are read from the prior audit and `STATUS.md`, not recomputed.

### Method note

`Glob` avoided entirely per the standing false-negative warning; discovery used `Grep` and `Read`
with absolute paths. Measurements ran via `.venv/Scripts/python.exe` reading stdin heredocs, no
files written to `scratch/` or elsewhere, no code modified, nothing committed, no process signalled.
No permission denials occurred.
