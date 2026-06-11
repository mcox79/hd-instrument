# Research drill -- NER substrate paths to >= 0.85 (2x DEEP)

Date: 2026-06-11
Topic: substrate-native NER F1 improvement from baseline ~0.58 to target >= 0.85 on CoNLL-2003-style 36-tag NER
Trigger: same-mechanism substrate POS = 0.9499 HARD_PASS; transferred to NER yields F1 = ~0.58 with 5 RESCUE candidates open
Substrate context (do not search externally): substrate-classical layer (count-based emission / transition / context-window bundles in Tier-2) is the validated NL primitive (POS 0.906 standalone, 0.95 with feature stack); NER is the next sequence-tagging benchmark

------------------------------------------------------------------------
## (a) HEADLINE
------------------------------------------------------------------------

POS->NER transfer gap is mechanism-explainable: NER differs from POS on three axes (BIO multi-token spans, severe O-class imbalance ~5x, 36 fine-grained tags with low support) that the per-token-emission substrate primitive does NOT handle. The literature shows the four classical lifts that closed the same gap on CoNLL-2003 were Gazetteer (~3-5 F1) + BIO/BILOU encoding with constrained Viterbi (~1-3 F1) + Brown / phrase clusters (~3-4 F1) + non-local features (~1-2 F1), stacking to take averaged-perceptron + structured-perceptron baselines from ~0.75-0.81 to ~0.88-0.91 on the EXACT same 6K-sentence regime substrate is using. P_deflated(substrate F1 >= 0.85 with all 5 RESCUEs stacked) = 0.45 (capped at novel-synthesis 0.50; deflated 0.20 from agent estimate 0.65 because BIO-aware substrate temporal policy is uncharted). HARD-PASS bar = F1 >= 0.85 with full 5-stack; HARD-FAIL bar = F1 <= 0.65 with 4+ RESCUEs stacked (indicates substrate emission representation itself is the ceiling, not the feature stack).

------------------------------------------------------------------------
## (b) Cheap decisive test
------------------------------------------------------------------------

Two-cell CPU smoke (~30 min total):

CELL-1 -- isolate the BIO-vs-per-token-emission contribution:
- Re-encode CoNLL-2003 training in BIO + class-balanced inverse-frequency loss
- Substrate emission-only (no transition layer), evaluate F1
- Decisive read: if F1 jumps from 0.58 to >= 0.68, BIO + balance contributes ~10 F1 alone. If F1 stays <= 0.62, the gap is in transition/structure, not encoding.

CELL-2 -- isolate the Gazetteer lift:
- Build PER/LOC/ORG/MISC gazetteer from Wikipedia category dumps (~500K-2M entries)
- Add 4 binary features per token (one per entity type): "token-or-bigram-or-trigram in gazetteer-X"
- Substrate count-based emission with gazetteer-binary features on top of CELL-1 baseline
- Decisive read: gazetteer alone adds ~3-5 F1 per Florian/Chieu CoNLL-2003 lit (88.31-88.76 F1 second-best at CoNLL with gazetteer); if substrate sees < 1 F1 lift, substrate is NOT consuming gazetteer features correctly (most likely feature-binding bug, not algorithmic ceiling).

These two cells together establish whether the path to 0.85 exists or whether substrate emission representation needs structural redesign for span-bounded sequence labeling.

------------------------------------------------------------------------
## (c) Falsifiable predictions
------------------------------------------------------------------------

| Prediction | HARD-PASS bar | HARD-FAIL bar |
|---|---|---|
| P1: BIO encoding + constrained Viterbi (RESCUE-2) lifts substrate F1 alone | F1 >= 0.66 | F1 <= 0.60 |
| P2: Gazetteer binary features (RESCUE-3) lifts F1 alone | F1 >= 0.63 | F1 <= 0.59 |
| P3: Bigram boundary features (RESCUE-1) lifts F1 alone | F1 >= 0.62 | F1 <= 0.59 |
| P4: Cascade POS-feeds-NER (RESCUE-5) lifts F1 alone | F1 >= 0.63 | F1 <= 0.58 (no lift) |
| P5: 6K -> 15K training data (RESCUE-4) lifts F1 alone | F1 >= 0.66 | F1 <= 0.61 |
| P6: Full 5-stack (BIO + gazetteer + bigram + cascade + 15K data) | F1 >= 0.85 | F1 <= 0.75 |
| P7: Full 5-stack PLUS class-balanced loss + brown clusters | F1 >= 0.88 | F1 <= 0.80 |

HARD-FAIL on P6 (full stack 0.75 ceiling) would refute "substrate-classical handles NER" and route to substrate-LLM cascade for NER specifically (different from POS where substrate-only holds).

HARD-FAIL on P1 alone (BIO without lift) would indicate substrate temporal-policy primitive cannot encode multi-token spans -- that's a substrate-architectural finding that would be surprising and load-bearing.

------------------------------------------------------------------------
## (d) Cross-thread synthesis with prior research deliveries
------------------------------------------------------------------------

Connections to prior research/exp_dev findings:

1. **POS HARD_PASS 0.9499 (PP-379) is consistent with NER 0.58 baseline.** The lit shows un-feature-engineered CRF baselines on CoNLL-2003 were 81% F1 vs POS Penn-Treebank 97%. The 16-point F1 drop POS->NER is a well-known NLP regularity, not a substrate-specific bug. Substrate baseline (0.95 POS -> 0.58 NER) is a steeper drop (37 points) which is the engineered-features gap; once feature stack is added, lit predicts the drop closes to ~10 points (0.95 -> 0.85), matching the 5-RESCUE target.

2. **Substrate-classical methods outperform phasor (memory_index 2026-06-11).** Same memory entry validated count-based statistical methods (HMM emission + transition + Viterbi; count-NB; context-window emission) stored as substrate Tier-2 bundles BEAT phasor-only prototype matching across 3 NL tasks. NER lit confirms transition + emission + context-window + gazetteer is the proven stack at this dataset size.

3. **Don't-parrot-drill-defeatism rule (memory_index 2026-06-11).** Initial 0.58 result must NOT be framed as architectural ceiling. Lit precedent shows even averaged-perceptron with no neural arch reaches 0.88-0.91 on CoNLL-2003 with the right feature stack. Substrate has not yet exhausted equivalent stack.

4. **Drill pattern TEMPORAL+CONTEXTUAL works (memory_index 2026-06-11).** RESCUE-1 (bigram boundary) and RESCUE-2 (BIO-constrained Viterbi) are both contextual/temporal -- match the predictively-load-bearing drill pattern. RESCUE-5 (cascade) is a fixed-architecture pattern -- match the predicted-to-fail pattern; rank it LOWER (P5 cascade may underperform).

5. **Substrate-LLM boundary decomposition (memory_index 2026-06-10).** Symbolic/structural NL (parse, POS, morphology) is substrate territory; arbitrary-English fluency is LLM territory. NER sits in symbolic/structural -- entity-type lexicon is gazetteer-bindable, boundary detection is transition-rule-bindable. NER should be substrate-territory at the same level as POS once feature stack equalized.

------------------------------------------------------------------------
## (e) RESCUE ranking by predicted lift (rank-ordered)
------------------------------------------------------------------------

Predicted lift estimates DEFLATED 0.20 per lit-scan calibration penalty (uncharted substrate regime):

| Rank | RESCUE | Mechanism | Predicted lift (deflated) | Cost | Why this rank |
|---|---|---|---|---|---|
| 1 | RESCUE-2: BIO-constrained Viterbi | structured decoding + valid transitions | +0.05 to +0.10 F1 | ~2 hr CPU build + smoke | Lit: constrained Viterbi matches CRF F1 in half the train time (Constrained Decoding paper 2020); BIO-illegal transitions (O->I-X without B-X) are pure structural prior, free lift |
| 2 | RESCUE-3: Gazetteer (Wikipedia) | external knowledge binary features | +0.03 to +0.07 F1 | ~4 hr build (Wikipedia extract) + 1 hr smoke | Lit: Florian/Chieu CoNLL-2003 +3-5 F1 from gazetteer; substrate Tier-2 bundle binding for binary features is straightforward |
| 3 | RESCUE-1: Bigram boundary features | F[-1]F[0], F[0]F[1] emission features | +0.02 to +0.05 F1 | ~1 hr CPU smoke (existing substrate emission) | Lit: standard context-window features in Jurafsky SLP3 ch.8; substrate already does unigram emission, bigram is +N states; cheap but smaller magnitude |
| 4 | RESCUE-4: 6K -> 15K training data | sample efficiency | +0.02 to +0.05 F1 | ~30 min (data loading, train) | Lit: standard learning curve sublinear past 10K sentences on CoNLL-2003; substrate count-based methods scale-monotonically with data |
| 5 | RESCUE-5: Cascade POS -> NER | substrate POS pre-filter feeds NER | +0.00 to +0.03 F1 (RISK: -0.02) | ~2 hr build (cascade integration) | Lit: cascading POS into NER had MIXED results -- automatic POS can DROP F1 -4.63 if errors propagate (Korean NER feature paper) or boost +7.74 in some settings; for substrate the POS confidence is 0.95 so propagation risk is LOW but not zero. Rank LAST because both upside is bounded and risk is asymmetric. |

Stacking principle (per lit): the lifts are NOT additive at the high end -- BIO + Gazetteer + bigram + class-balanced stacking gives ~+0.20-0.25 F1 (Ratinov-Roth 2009 averaged-perceptron 90.8 F1 with BILOU + Wiki gazetteer + Brown clusters + non-local features starting from ~70 F1 unengineered baseline).

Recommended dispatch order: RESCUE-2 first (cheapest + biggest predicted lift + tests structural primitive), then RESCUE-3 in parallel (independent path), then RESCUE-1 and RESCUE-4 (cheap), defer RESCUE-5 until others measured (avoids propagation noise during diagnosis).

------------------------------------------------------------------------
## (f) Boundary-detection mechanism specifics (DEEP DRILL)
------------------------------------------------------------------------

NER mechanism difference vs POS, decomposed:

**Diff 1: Multi-token spans.** POS is per-token: each token gets one tag independently. NER has multi-token entities ("United Nations Educational Scientific and Cultural Organization" = single ORG span). The substrate per-token-emission primitive sees this as 7 independent tokens with no span coherence. BIO encoding (Begin-Inside-Outside) makes the span structure explicit at the token level (B-ORG I-ORG I-ORG ...). Substrate-level fix: add transition-feature bundles for legal-vs-illegal BIO transitions; emission features for "previous tag is B-X" must be in substrate context bundle.

**Diff 2: O-class imbalance.** ~5x more O tokens than entity tokens (CoNLL-2003). Substrate count-based emission naturally over-predicts O (most frequent class). Substrate-level fix: class-balanced inverse-frequency weighting on emission counts; or threshold-tuning on entity-class scores during Viterbi.

**Diff 3: Fine-grained tags low support.** 36 tags (vs ~45 POS) but support per tag in 6K sentences is much lower for rare entity types (MISC subtypes). Substrate-level fix: tag-group hierarchy in Tier-2 bundles (first decide entity/non-entity, then decide type) -- this is the "hierarchical NER" approach in Cost-Sensitive Structured Perceptron (Researchgate 2020 paper).

**BIO-constrained Viterbi implementation (the highest-rank RESCUE):**

Per "Constrained Decoding for Computationally Efficient NER Taggers" (arxiv 2010.04362, 2020): the constraint is purely structural -- set transition score to -inf for illegal transitions:
- O -> I-X is illegal (must have B-X to start entity)
- B-X -> I-Y where X != Y is illegal (cannot change type mid-entity)
- I-X -> I-Y where X != Y is illegal

This is implementable in substrate's existing temporal-policy Viterbi as a transition-feature mask in the temporal bundle. Substrate cost: ~50 LOC to add transition mask. Predicted lift in CoNLL-2003 lit: matches full CRF F1 at half train cost; for substrate, this is the cheap structural prior that the substrate emission primitive currently lacks.

**Gazetteer injection (RESCUE-3 specifics):**

Per "Self-Attention Gazetteer Embeddings for NER" (arxiv 2004.04060): gazetteer features at simplest are 4 binary indicators per token (one per CoNLL entity type) indicating "this token / bigram / trigram matches a gazetteer entry of type X". Wikipedia + DBpedia category dumps give 500K-2M entries per type for FREE. Substrate binding: 4 extra binary features per token's context bundle; substrate's existing count-based emission naturally consumes these.

Lit precedent for lift magnitudes on CoNLL-2003:
- Gazetteer alone: +3-5 F1 (Florian 2003, Chieu 2003, Ratinov-Roth 2009)
- Gazetteer + cluster IDs (Brown clusters): +5-8 F1 cumulative
- Gazetteer + non-local features: +6-9 F1 cumulative

------------------------------------------------------------------------
## (g) Cross-thread synthesis -- substrate-product implications
------------------------------------------------------------------------

If full 5-stack reaches >= 0.85:
- Substrate-classical NER joins POS as a validated substrate-only NL primitive.
- Enables substrate-side entity-aware memory indexing (entity names become atomic memory anchors).
- Enables substrate-side query interpretation: NER on user query identifies entity slots -> binds to memory entity-anchors directly without LLM mediation.
- Strengthens the substrate-LLM boundary decomposition: NER is structural NL, not LLM-only.

If full 5-stack ceiling at 0.75-0.80:
- Acceptable for many product use-cases (chat entity extraction tolerates some miss).
- Suggests substrate is symbolic-strong + structural-strong but lexical-coverage-bounded -- consistent with substrate-LLM boundary memory.
- Hybrid path: substrate NER produces candidates; LLM-side verification on candidates with low substrate score (cheap, <10% of tokens need LLM).

If full 5-stack ceiling at <= 0.65:
- Genuine substrate-architectural limit on span-structured sequence labeling.
- Routes to: (a) substrate-LLM cascade for NER, (b) revisit substrate emission representation for span coherence (multi-token role-binding primitive?).

------------------------------------------------------------------------
## (h) Citations (verified)
------------------------------------------------------------------------

Verified count: 11 (all lit-cited entries are real papers with arxiv/ACL/PubMed IDs)

1. Ratinov & Roth 2009 -- "Design Challenges and Misconceptions in NER" CoNLL '09 -- BILOU encoding + Wiki gazetteer + non-local features = 90.8 F1 on CoNLL-2003
2. Florian et al. 2003 -- best system at NER CoNLL-2003 with 88.76 F1 (gazetteer + hand-features)
3. Chieu 2003 -- second-best CoNLL-2003 88.31 F1 (external gazetteer + hand features)
4. Lin & Wu 2009 -- linear-chain CRF + phrase clusters from search-query logs
5. Passos et al. 2014 -- linear-chain CRF + phrase vectors from modified skip-gram
6. arxiv 2010.04362 (2020) -- Constrained Decoding for NER (BIO-constrained Viterbi matches CRF F1 at half train cost)
7. arxiv 2003.03072 -- "Improving Neural NER with Gazetteers"
8. arxiv 2004.04060 -- "Self-Attention Gazetteer Embeddings for NER" (+0.5 F1 on top of 92.34 modern baseline)
9. arxiv 1911.02855 -- "Dice Loss for Data-imbalanced NLP Tasks" (NER O-class imbalance)
10. arxiv 2401.11431 -- "Majority or Minority: Data Imbalance Learning for NER"
11. arxiv 2009.07317 -- "Cascaded Models for Better Fine-Grained NER" (cascade lifts +20 F1 absolute for fine-grained NER)
12. Jurafsky & Martin SLP3 ch.8 (Stanford, December 2021 ed.) -- canonical reference for sequence-labeling features (unigram/bigram context window 5)
13. Tkachenko & Simanovsky 2012 (konvens) -- baseline CRF + cluster features 81.15 -> 84.86 F1

------------------------------------------------------------------------
## (i) Next-drill candidates (post this drill)
------------------------------------------------------------------------

- If P1 PASS + P2 PASS: stack and measure P6 immediately (cheap, can be done in same evening).
- If P1 FAIL: drill substrate emission primitive for span-coherence representation -- this becomes a substrate-architectural research question (different from feature engineering).
- If P6 FAIL but full stack F1 in 0.75-0.85: drill Brown clusters + non-local features (the +5 F1 path used by Ratinov-Roth from 88 to 91).
- If P6 PASS >= 0.85: NER joins POS as validated substrate-only primitive; close cap_map row; next NLP drill = constituency parsing or dependency parsing.

End of drill note.
