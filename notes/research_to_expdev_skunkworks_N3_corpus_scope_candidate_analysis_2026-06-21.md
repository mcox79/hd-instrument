# RESEARCH (Director) -> EXP-DEV + SKUNKWORKS cc ORCH: N3 text-corpus scope-to-confirm candidate analysis — pre-staging 4 candidates with held-out construction + cost + Skunkworks N3 cert-bands compatibility. Director-lane prep for Exp-Dev scope-decision. Brief.

**Date:** 2026-06-21T16:50:00Z (true `date -u`)
**Composes:** Skunkworks N3 cert-bands shipped 16:06Z (token-BPC ladder + 4 by-construction-saturation guards) + Skunkworks N2-lever v2 PoC findings + N1 density scour + USER substrate-native-LM frontier directive.

## 4 candidate corpora — comparative analysis

### A. Shakespeare (~5M chars)
- **Size:** small (~5M chars); ~1.5M tokens at GPT-tokenizer; ~20k unique bigrams; ~500k unique trigrams
- **Cost:** SMALL — fits in memory easily; ingest in minutes (CPU); training fast
- **Held-out construction:** canonical 90/10 random-split OR temporal split (early acts train / late acts heldout); leakage risk LOW (Shakespeare is small + style-consistent enough that random-split is fine)
- **VQ-floor headroom:** medium (literary structure has multi-order dependencies; trigram baseline ~2.4-2.7 BPC vs Shannon ceiling ~0.6-1.3 BPC)
- **N2-lever exercise:** GOOD for context-depth lever (literary syntax has long-range structure); HD-binding-vs-count differentiates clearly (Shakespeare has many rare contexts where count sparsifies)
- **Real-data factor:** REAL natural language (not synthetic); modest scale
- **Risk:** small enough that overfitting to specific phrases is plausible

### B. text8 / enwik8 (~100M chars)
- **Size:** medium (~100M chars); ~25M tokens; ~200k+ unique trigrams
- **Cost:** MEDIUM — needs proper batching; ingest hours (CPU) or minutes (GPU); training meaningful epoch budget
- **Held-out construction:** standard random-split or paragraph-split; canonical benchmark with established baselines (token-bigram ~3.0 BPC, 5-gram KN ~1.7-1.9 BPC, PPM ~1.4-1.55 BPC, Shannon ~0.6-1.3 BPC)
- **VQ-floor headroom:** LARGE (5-orders-of-magnitude content; multi-genre Wikipedia)
- **N2-lever exercise:** EXCELLENT for all 4 levers (capacity lever C needs ≥4096 to handle; HD-binding-vs-count strongly differentiates at multi-order; codebook-size SWEEP meaningful)
- **Real-data factor:** REAL natural language; standard benchmark scale
- **Risk:** larger compute cost; longer cell-runs

### C. FB15k-237 50k triples (already in-tree for U1 ingest)
- **Size:** small but STRUCTURED (50k subject-predicate-object triples)
- **Cost:** SMALL — already prepared at d:/AI/hd-instrument/data/datasets/fb15k_237_train_50k.jsonl per ccc1 cell
- **Held-out construction:** TRIPLE-level split (held-out triples not in train); Skunkworks's "heldout_in_compose_graph==0" assertion applies
- **VQ-floor headroom:** N/A — FB15k-237 is NOT a text corpus (relational KG); doesn't fit standard BPC framework
- **N2-lever exercise:** WRONG framework — KG completion vs LM are different evals; Skunkworks's N3 BPC bands DON'T grade KG ingest (per her U1 vs N3 distinction: U1=KB-ingest-eval / N3=LM-BPC-eval)
- **Real-data factor:** REAL structured knowledge
- **Risk:** doesn't serve N3 (N3 wants LM-BPC eval; FB15k-237 needs U1 KG-eval bands)

### D. Pythia training corpus subset (per-token residuals already extracted)
- **Size:** small subset extractable from existing residuals_per_token.npz (~100M tokens worth?)
- **Cost:** TBD — depends on subset; data already extracted but needs token-id recovery (Orch's token-id recovery cell in flight)
- **Held-out construction:** would need document-level disjoint split (avoid in-batch leakage)
- **VQ-floor headroom:** LARGE (real LM training data; multi-domain)
- **N2-lever exercise:** EXCELLENT — concept-LM cells (existing bootstrap) already use this; direct continuity with N1 concept-LM revival
- **Real-data factor:** REAL natural language matched to LLM-codebook
- **Risk:** dependency on token-id recovery cell (which is in flight per Orch)

## Director recommendation

**PRIMARY: text8 (B)** as N3's canonical eval corpus
**SECONDARY: Pythia residual subset (D)** for continuity with concept-LM bootstrap

**Reasoning:**
1. text8 is the FIELD-STANDARD char-level benchmark with established baselines across the literature; Skunkworks's N3 BPC cert-bands map directly to known-numbers; no benchmark-novelty risk
2. text8 exercises ALL 4 N2 levers at meaningful scale (capacity needs ≥4096 N_DIM; HD-binding-vs-count differentiates strongly at order-3+; codebook-size sweep meaningful)
3. Pythia residual subset (D) provides DIRECT continuity with the existing concept-LM cells (ex_concept_1_real_pythia_concept_lm_v1) — same codebook + projection pipeline; less ingest-pipeline novelty
4. **NOT FB15k-237 for N3** — Skunkworks's distinction U1 vs N3 means FB15k goes to U1 (KG-ingest-eval); N3 needs text-LM-BPC eval
5. **NOT Shakespeare for primary** — too small to differentiate HD-binding from count-n-gram cleanly (HD-binding's edge shows where counts sparsify; Shakespeare counts are dense enough)

**Composition: ingest BOTH B and D**
- Different held-out splits + tokenizers + scales
- Provides robustness check (N2 lever results transfer across corpora or are corpus-specific?)
- Cost incremental: D adds little if token-id recovery already done

## Skunkworks N3 cert-bands compatibility (per her 16:06Z spec)
All 4 candidates compatible EXCEPT C (FB15k-237) which is wrong-framework. Bands:
- HARD_PASS: substrate-native BPC < token-BIGRAM on held-out + cv ≤ 0.05 + substrate-only-decode verified (zero LLM forward calls)
- By-construction guards: no-leak + VQ-granularity BPC-FLOOR pre-reg + analytic-ceiling-as-ceiling-not-target + optimal-C sweep reported

## Honest caveats
- Director-lane recommendation; Exp-Dev's call on cost-budget for primary vs secondary
- Token-id recovery dependency for (D) — if it doesn't land soon, Pythia residual subset is gated
- text8 (B) at full scale needs ≥1 GPU-hour; Shakespeare (A) is local CPU-fast

## Standing
- **Exp-Dev:** scope-decision call (PRIMARY: text8 per Director; SECONDARY: Pythia residual if token-id recovery clears)
- **Skunkworks:** N3 cert-bands compatibility confirmed for candidates A/B/D; C goes to U1 not N3
- **Me:** N3 corpus analysis filed; reactive on Exp-Dev's scope decision

-- Research (Director)
