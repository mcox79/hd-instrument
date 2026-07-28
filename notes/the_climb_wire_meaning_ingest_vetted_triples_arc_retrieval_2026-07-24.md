# THE CLIMB -- wire meaning into the vetted store + ingest vetted triples + answer ARC by fact-retrieval

**Staged 2026-07-24 (Director), GATED on the capacity-re-check `aacccd1d` verdict.** Dispatch the moment the capacity VET banks. This is step 2 of the ingestion NEXT-sequence (`notes/ingestion_learn_sleep_loop_2026-07-24.md`).

## GOAL (USER)
Substrate matches by MEANING and its knowledge CLIMBS the human grade-scale. Current honest floor: ARC-Easy broad-ingest +0.043 lexical / +0.042 semantic = still ~CHANCE. The lever (per 29530/29533 VETs) = a proper VETTED HD-SEMANTIC KB answering ARC by FACT-retrieval, NOT more sentence-IR. This cell tests whether that lever lifts the scale off the floor.

## INGREDIENTS (all banked/local -- confirmed on disk 2026-07-24)
- **Fact store**: `hdlab/hd_fact_store.py` (29531/29532) -- trust-vetting + sharded + O(1) index. Fact = role-slot HD bundle (REL/ARG0/ARG1/SOURCE/TRUST).
- **Semantic encoder**: `SemanticHDEncoder` from `experiments/exp_semantic_hd_encoder_meaning_match_v1.py` (29533) -- fused GloVe + WordNet syn/hyper -> JL 300->2048 HD. AUC 0.96. Use it to encode the FILLERS (subj/obj) semantically.
- **Vetted triples source**: `data/datasets/conceptnet5_en_100k.jsonl` -- 100k clean `{subject,predicate,object}` English triples (curated KB = flows through the trust-gate as a TRUSTED source). Plus WordNet relations (nltk, 117659 synsets) + ARC_Corpus.txt (14M sentences) for extracted science triples.
- **ARC measure**: `data/corpora/arc/ARC-V1-Feb2018-2/` (Easy 2251 / Challenge 1119) + the glass-box MC-QA harness pattern from `exp_arc_knowledge_scale_ingest_climb_v1.py` (29530).

## THE CELL (exp_dev to design N/seeds/bands)
1. **Ingest** ConceptNet triples (trusted source) + optionally ARC_Corpus-extracted triples THROUGH the trust-gate into the fact store (semantic fillers via SemanticHDEncoder).
2. **FUZZY conflict** via semantic similarity, not exact-match (USA==United_States, cat~kitten): resolve conflicts by trust when the (s,r) MATCH is fuzzy. This is the 29531-VET gap (#a: conflict was exact-dictionary, no surface-variant).
3. **Answer ARC by FACT-retrieval**: encode Q+choice, retrieve supporting FACTS from the store (glass-box evidence), score, argmax. Compare vs the 29530 sentence-IR lexical floor (+0.043) and the 29533 semantic-IR (+0.042). Does fact-retrieval BEAT both?
4. **Controls (mandatory, honest)**: empty-store baseline ~chance; scramble control collapses; broad-ingest (answer-agnostic, NOT test-targeted -- the FAIR number per 29530); no answer-key leak (IR index from stem+ALL choices only).

## STORAGE BRANCH RESOLVED (capacity VET 29534, 2026-07-24)
**Capacity-re-check BANKED (29534 MM): NO forced hybrid.** The semantic store is foundation-scale on the real bipolar rep (no wall, proven V=100k genuine full-fact path / 1M analytical; the feared 0.588 anisotropy was a false alarm -- wrong object, GloVe-only bipolar codes were always ~0.014). => **SINGLE semantic-rep store** (simpler): fillers stored as semantic HD; fuzzy conflict = native semantic cosine. NO exact-key/semantic-fuzzy split needed. Honest bound to carry: genuine capacity proven to 100k (1M analytical) -- fine for the ConceptNet-100k + ARC-corpus ingest scale; revisit for on-disk millions.

## HONEST EXPECTATION (deflated)
Fact-retrieval SHOULD beat sentence-IR IF ARC answers are fact-lookupable. But: (a) many ARC-Easy Qs need COMPOSITION not a single triple; (b) ConceptNet is commonsense-heavy, thin on grade 3-9 SCIENCE specifics -> coverage may cap the climb (a curriculum-breadth problem, not a mechanism problem -- diagnose which). Challenge stays flat (multi-hop reasoning = separate layer, step 3 of the sequence). Deliverable = the honest fact-retrieval climb number + WHERE coverage vs mechanism limits it.
