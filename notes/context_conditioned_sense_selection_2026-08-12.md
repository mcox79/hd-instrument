# Context-conditioned sense selection -- can the substrate pick the RIGHT sense given a CONTEXT?

Arc: follows `notes/wire_reader_to_meaning_organs_2026-08-12.md` (8e364d807, 035a3acc5,
37d10e690), which refuted the islanding hypothesis and identified THIS as the measurement
that actually matters. Written incrementally as work proceeds.

## STEP 0 -- prior-work check + independent verification of inherited claims

Prior-work: `notes/PLAN_B_grounding_word_context_affect_superposition_map_2026-08-07.md`.
WHAT I TOOK FROM IT (rather than re-deriving):
- The architecture framing: word = superposition of (context-key (X) sense) bindings that
  COLLAPSES when the situation supplies a context key; Layer-3 "context-collapse read" =
  unbind + cleanup over the word's candidate senses. My selector IS that read, with the
  cleanup domain set to the word's k stored objects.
- The SUPPLIED-vs-EARNED line: the candidate-sense MENU is supplied DATA (there it is
  WordNet; here it is the store's own k objects for that subject -- strictly better, since
  the menu is what the substrate actually holds, not an external dictionary).
- Its stage-2/stage-4 controls, which I reuse in kind: SCRAMBLE as the decisive control
  (there: scramble-consequence, lift 0.514), and a single-sense stability baseline.
- Its OWN honest boundary, which is the warning for this cell: stages 2/4 proved the
  mechanism on a 2-way animacy context key with 6 hand-built words; its STATUS block records
  that on REAL prose "the teaching signal DOESN'T CARRY" and the loop is
  CONTEXT-EXTRACTION-limited. So the prior is NOT "this will work" -- the one time this
  architecture met real prose it failed. This cell is that meeting, on 288 real words.

WHAT IS NEW HERE (not in PLAN_B): PLAN_B specifies the design but was never run on the
landed foundation's own multi-sense words, and its context key is a hand-built 2-way
feature. This is the open-vocabulary, real-corpus, held-out instance of it.

### Inherited claims -- VERIFIED MYSELF (not inherited)

| claim | source | my verification | verdict |
|---|---|---|---|
| FLAGGED facts stay live+queryable | hd_fact_store.py:66 | read line 66: `ACTIVE_STATUSES = frozenset({"ACTIVE","COMBINED","FLAGGED"})`; `query()`:326 and `live_facts()`:332 both filter on it | CONFIRMED |
| 288 subjects (21.9%) hold >1 distinct sense | v3 fact set | recomputed off `definitional_facts.jsonl`: 1751 facts / 1316 distinct subjects / **288 multi-sense (0.2188)** / 723 facts involved | CONFIRMED |
| floor = mean(1/k) = 0.4316, mean k = 2.5104 | 035a3acc5 | recomputed: mean k **2.5104**, mean(1/k) **0.4316**, k-dist {2:187,3:77,4:12,5:7,6:3,7:1,10:1} | CONFIRMED exactly |
| re-banking 1751 v3 facts yields 1751 live | 8e364d807 | not re-run; NOT load-bearing for this cell (this cell reads the fact rows, it does not re-bank) | NOT RE-VERIFIED, and not relied on |

### NEW load-bearing fact the prior note did NOT surface (changes the design)

**621 of the 723 multi-sense facts (85.9%) have exactly ONE source sentence** (dist: 1->621,
2->78, 3->24). Only **7** of the 288 words have >=2 source sentences on EVERY sense.

This breaks the task's stated design as literally written ("hold out a source sentence, build
the sense from the rest"): for 86% of senses, holding out the only sentence leaves the sense
with no context at all. Leave-one-sentence-out is therefore an underpowered 7-word check, not
the main arm. The main arm must get its sense-side representation from a source that is
sentence-independent by construction -- see the leakage section below.

Also measured: a source sentence is shared across two senses of the same word for 4 words.
Those trials are label-ambiguous and are EXCLUDED (counted and reported).

## STEP 1 -- do I need to promote FHRRProcessStore?

NO. Decision recorded before building.
The question is whether the SELECTION FUNCTION (context key -> collapse onto the word's
candidate senses) carries signal at all. A superposition store is one IMPLEMENTATION of that
collapse; it cannot create signal that the selection function does not have. If selection
lands at floor, promoting the store would be pointless -- so measuring first is strictly
cheaper and strictly more informative. Measurement beats promotion.

If a later cell does promote it: its source cell
`experiments/exp_bootstrap_fhrr_superposition_fade_v3.py:80` carries verdict
**HARD_FAIL_PARTIAL**, and its 0.9556 is `capacity.retrieval_self_consistency` over a 3-way
fate codebook (MOVE/CREATE/DESTROY) with n_keys=225 -- a closed 3-way codebook, NOT
open-vocabulary senses. That number must not cross into this regime uncited.

## STEP 2 -- owned organs used (no reinvention)

Checked the repo inventory before building:
- `hdlab/random_indexing.py` `RandomIndexingEncoder(N=8192, sparsity=10, window=5,
  min_count, seed)` -- genuine open-vocabulary distributional encoder, corpus-agnostic
  (`fit_corpus(tokens)`), `encode(word)`, `has(word)`. Un-registered but built; mechanism
  landed MIDDLE_BAND in exp_n11. THIS is the context-vector organ; I do not rebuild it.
- `hdlab/grounded_similarity.py` -- 36,810-word x 12-dim (Lancaster sensorimotor 11 +
  Brysbaert concreteness) perceptual profiles. Covers 457/543 (84.2%) of the objects in the
  multi-sense set.
- `hdlab/lexical_similarity.py` `concept_similarity` -- NOT usable as the selector:
  measured, 16.4% of scored pairs saturate exactly at `GROUNDED_CAP=0.45`
  (`min(0.45, max(0.0, raw))`, grounded_similarity.py:190), which destroys ranking at the top
  of the scale. I use the RAW grounded profiles for RANKING only and never emit a
  same-idea/link decision, which is the only thing the cap exists to prevent.
- REJECTED: `experiments/.../SemanticHDEncoder` (external pretrained GloVe) and the gensim
  caches -- external pretrained embeddings, against the substrate-native/no-external-model
  invariant.
- `hdlab/ppmi_sparse_encoder.py` is registry `SHELVE`d and needs supervised concept labels;
  not used.

Corpus: `experiments/exp_definitional_grounding_v3.load_corpus()` -- the exact corpus the
facts came from. MEASURED: 32,955 sentences / ~623K tokens
(bio_new 11332, adv_new 7408, int_cont 4952, bootstrap 4640, ele_cont 4623).
HONEST CAP: 623K tokens is SMALL for distributional semantics (text8 = 17M). The
distributional selector is representation-limited by corpus size, and a null from it is a
null about THIS corpus at THIS size, not about distributional sense selection in general.

(continued below as the run proceeds)
