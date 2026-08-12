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

## STEP 3 -- RESULTS (full run, `data/exp_context_conditioned_sense_selection_v1/metrics.json`)

841 trials / 288 words (8 trials excluded as label-ambiguous, 4 words). Floor 0.4316 analytic,
0.4321 empirical over 1000 seeds. RI: 598,709 fit tokens, vocab 13,342, 850 eval sentences
removed from the fit corpus (L1 asserted disjoint). Runtime 15.5s.

### MAIN ARM -- sense represented by the STORED OBJECT WORD: DECISIVE NULL

| arm | S1_DIST | S2_PERC | S3_COMBO |
|---|---|---|---|
| PRIMARY (subject-weighted) | **0.4296** | 0.4268 | 0.4162 |
| C1 cross-item context swap | 0.4249 (sd 0.0044) | 0.4280 (sd 0.012) | 0.4134 |
| C2 context lesion | 0.4221 | 0.4282 | 0.4243 |
| FLOOR | 0.4316 | 0.4316 | 0.4316 |

Every number is inside +/-0.016 of the floor. **The right context, a wrong context, and no
context at all all produce the same accuracy.** Restricting to the 469 trials with >=3 context
tokens makes it WORSE (S1 0.3807, S2 0.4066), so the null is not an artifact of the 210
trials the masking emptied. Micro CI for S1 [0.3618, 0.4322] straddles its own micro floor
0.3983.

Verdict **HARD_FAIL** -- and all three pre-registered failure conditions fired independently
(both selectors within 0.03 of floor; C1 drop 0.005 << 0.05; C2 within 0.03 of primary).

### C3 -- sense represented by ITS OWN OTHER SOURCE SENTENCES: GENUINE POSITIVE

| arm | acc | n | 95% CI |
|---|---|---|---|
| C3 strict leave-one-sentence-out | **0.6914** (subj-w 0.6481) | 162 | [0.6165, 0.7574] |
| C3 query-swap control | 0.4272 (sd 0.0245, 5 seeds) | 184 | -- |
| C3 count-matched (1 sentence per sense) | 0.6835 | 158 | -- |
| C3 same-segment-only | 0.5778 | 45 | [0.4330, 0.7103] |
| C3 same-segment-only, query-swapped | 0.3519 | 45 | -- |

Both confounds I could think of were tested and cleared:
- **Query-driven, not candidate-side.** Swapping in a query sentence from a DIFFERENT word
  collapses 0.6914 -> 0.4272 (lift 0.264). The lift is caused by the query.
- **Not a token-count / hubness artifact.** C3's target sense keeps more sentences after
  hold-out, so it could have won on a smoother mean vector alone. Capping every candidate at
  one sentence leaves it at 0.6835. (Measured token counts were near-identical anyway:
  target 13.6 vs competitor 12.99.)
- **Partly, but not wholly, topic/segment matching.** Restricting to words whose senses all
  sit in ONE segment (so segment identity carries zero information) drops it to 0.5778 --
  so roughly 0.11 of the headline lift WAS topic matching. The residual is still 0.226 above
  its own swap (0.3519), but n=45 and the CI lower bound (0.4330) sits essentially ON the
  floor. **The segment-free residual is suggestive, NOT established.** Do not quote 0.6914
  as a clean sense-selection number.

### THE DISSOCIATION -- what this actually shows

Same substrate, same retrieval operation, same 288 words, same floor. The ONLY thing that
changes between the null and the positive is **what the sense side is made of**:
- sense = the bare object word the store actually holds -> **0.4296 = floor, dead**
- sense = the sentences that sense came from          -> **0.6914, swap-controlled**

So the missing capability is NOT the collapse/retrieval mechanism, and NOT superposition
storage. It is that the landed foundation **banks the object word and throws the source
context away**, leaving nothing for a context key to match against. `source_sentences` survives
in the JSONL provenance but never enters the HD fact. That is the precise, small build target.

### HONEST TAIL -- and one claim I could NOT substantiate

13 of 274 scorable words (4.7%) are never selected correctly by either selector. That count is
weak evidence on its own: at mean 2.9 trials/word and floor-level accuracy, being 0-for-2 is
an ordinary coin-flip outcome, so this list is not a reliable "inseparable" set.
Fixed a real bug in the classifier mid-run: it counted sentence-initial capitalisation as a
proper noun and so mislabelled coal/oxygen/fish as entity collisions. After the fix: 12
"distinct senses, no context support", 1 genuine proper-noun collision (`airport ->
{entrance, gateway}`).

**Qualitative read, EXPLICITLY NOT MEASURED:** looking at the dead words, many "senses" do not
look like senses -- `chromosome -> {bound, copy, determinant, length, male, pair}`,
`fungi -> {chytridiomycota, chytrids, source}`, `fish -> {earliest, ostracoderm, vertebrate}`
read as fragments of definitional phrases, not as distinct meanings. If true this caps
achievable accuracy on the main arm.
**I tried to quantify it and FAILED to confirm it.** Machine proxies over all 288 words:
morphological near-duplicate object pair = 1 word (0.3%); any object failing the content-word
gate = 0 words (0%); 287/288 pass both. So my cheap proxies do NOT support the impression.
It stands as a hypothesis requiring a labelled check, not a finding. Reporting it as measured
would be exactly the over-claim this project's discipline forbids.
Separately measured and solid: 168/288 (58.3%) of multi-sense words have all senses inside one
segment -- the population the same-segment control runs on.

### PROMOTION: none. FHRRProcessStore was NOT promoted and was not needed.
The question was answered with the retrieval path that already exists plus two owned organs.
A superposition store implements the collapse; the measurement shows the collapse is not what
is broken, so promoting it would not have moved this result. Its HARD_FAIL_PARTIAL cell's
0.9556 (3-way fate codebook, 225 keys) never entered this cell in any form.
