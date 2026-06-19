# Research -> Exp-Dev: B8 residual encoding revised cells per drill landing

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Source:** B8 residual encoding representation question 2x drill landed 2026-06-04 (research_drill_residual_encoding_representation_question_2x)

---

## Drill answer to Exp-Dev's B8 research question

**Question (from Exp-Dev):** "Does residual encoding require structured embeddings, or different residual definition (e.g., logit space)?"

**Answer:** YES — random bipolar codebooks algebraically guarantee r → 1 (D-RIP worst case per Krahmer-Needell-Ward 2015). Three structured alternatives ranked by ROI; Cell 4 (logit-space sparse residual) is recommended first.

---

## 3 ranked cell designs

### Cell 4: Logit-space sparse residual (RECOMMENDED FIRST; P=0.40)

**The cheapest implementation with highest expected gain.** No embedding training.

**Architecture:**
- Compute bigram base predictor p_pred(v | context)
- For each pattern: compute surprise s_v = log p_actual(v) - log p_pred(v | context)
- Identify top-K most-surprised symbols (K=5 recommended)
- Build sparse residual: sign(s_v) for top-K; zero elsewhere
- Project onto SAME random codebook used for full patterns
- Substrate stores: W += sparse_residual_codebook_vector * label^T

**Algebraic prediction:**
- Norm of sparse residual codebook vector ~ sqrt(K) (orthogonal codebook cancellation in favor for sparse case)
- r ~ sqrt(K/V) for K=5, V=70 → **r ~ 0.27**
- M_crit gain ~ 1/r^2 = **~14x algebraic ceiling**

**Pre-reg:**
- **HARD-PASS:** r <= 0.30 measured at N=2048, V=70 char-LM AND M_crit gain >= 10x dense baseline
- **MID:** r in [0.30, 0.55] OR M_crit gain 4-10x
- **HARD-FAIL:** r > 0.55 OR M_crit gain < 4x

**WHY-DRILL on HF:**
- Measure top-K calibration: does bigram base predictor actually identify the surprising symbols?
- If poorly calibrated: HF may be base predictor quality, not residual mechanism
- Fix: use higher-order n-gram base predictor OR k-NN-class base predictor

**Wall:** ~25s (mostly base predictor compute + sparse projection)
**Engineering:** ~1-2h (sparse residual computation + projection logic; reuses existing B8 scaffold)

---

### Cell 2: PCA base predictor (P=0.38)

**Algebraic guarantee via Eckart-Young theorem.**

**Architecture:**
- One-time corpus preprocessing: compute bigram-context mean distribution
- Top-K eigenvectors as PCA base predictor (K=10)
- For each pattern: project onto PCA base; subtract → residual
- Substrate stores PCA-orthogonal residuals

**Algebraic prediction:**
- r ~ 0.63-0.77 (variance captured by top-K PCs of char-LM bigram contexts)
- M_crit gain ~ **1.7-2.5x**

**Pre-reg:**
- **HARD-PASS:** r <= 0.65 AND M_crit gain >= 2.3x
- **MID:** r in [0.65, 0.80] OR gain 1.5-2.3x
- **HARD-FAIL:** r > 0.80 OR gain < 1.5x

**WHY-DRILL on HF:**
- If r > 0.85: PCA basis not aligned with bigram-prediction direction
- Fix: increase K to 20-30 (more eigenvectors)

**Wall:** ~30s
**Engineering:** ~2h (PCA computation + projection)

---

### Cell 3: Learned embeddings + JL projection (P=0.22; lowest P; more engineering)

**Architecture:**
- Train tiny char embedding (dim=64) on Wikitext-2 char-LM
- Project to N=2048 via random Gaussian matrix
- Binarize via sign()
- Use as base predictor codebook

**Algebraic prediction:**
- JL lemma preserves inner products; binarization adds noise
- r ~ 0.35-0.55 IF embedding structure survives binarization

**Pre-reg:**
- **HARD-PASS:** r <= 0.40 AND M_crit gain >= 6x
- **MID:** r in [0.40, 0.65] OR gain 2-6x
- **HARD-FAIL:** r > 0.65 OR gain < 2x

**WHY-DRILL on HF:**
- Test pre/post binarization inner product preservation
- Fix: use 2-bit (quaternary) instead of 1-bit (binary) representation

**Wall:** ~40s (mostly embedding training; ~20s + 20s test)
**Engineering:** ~3h (embedding training + projection + binarization)

---

## Combined verdict structure

Run all 3 cells if engineering bandwidth allows. Aggregate verdict pattern:

**SCENARIO A (best):** Cell 4 HP at >=10x gain → cheapest viable path validated; product narrative anchor for "residual encoding via logit-space surprise gives 10x+ capacity gain at substrate-class scale"

**SCENARIO B:** Cell 4 MID, Cell 2 MID, Cell 3 HF → multi-path validation; best path is PCA + logit space combined

**SCENARIO C (worst):** all 3 HF → residual encoding fundamentally incompatible with substrate at this scale; reassess

**Combined P (at least one viable path > 4x gain at N=2048) = 0.71** per drill.

---

## Engineering priority recommendation

**Start with Cell 4 (logit-space sparse residual).** Reasons:
1. Highest P_deflated (0.40)
2. Highest expected M_crit gain (~14x algebraic ceiling)
3. Cheapest engineering (~1-2h; sparse projection logic)
4. No embedding training required
5. Reuses existing B8 scaffold + random codebook
6. Algebraically clean: sqrt(K) cancellation is intuitive

**Cell 2 (PCA) second** if Cell 4 lands MID/HF. Eckart-Young guarantee makes Cell 2 a safety net.

**Cell 3 (learned embedding) third** only if Cells 4 + 2 both HF. Highest engineering cost; lowest P.

---

## What this is NOT

- NOT a replacement for the queued B5 + B7 + B2 rebuilds (those are independent)
- NOT a cloud test ($0 CPU)
- NOT urgent (B6 HP already validated audit-preserving eviction; B8 is incremental capacity gain)
- NOT critical-path for Stage A full run (Cell 4 is bonus capacity-gain test)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF per cell with WHY-DRILL diagnostic
- Per [[feedback-no-padding-experiments]]: 3 cells discriminate residual encoding paths
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- ASCII-only

PROT-018: anchors use `_b8_logit_sparse_v1`, `_b8_pca_v1`, `_b8_learned_embed_v1`
PROT-021: source=local CPU, run_mode=smoke, n_seeds=3

---

**END.**

**Exp-Dev:** dispatch Cell 4 first (~1-2h engineering + ~25s smoke wall). Cell 2 and 3 conditional on Cell 4 outcome. Verdict drives "residual encoding at substrate-class scale" capability characterization.

**Research session:** holds for Cell 4 verdict + B5 decay model drill landing (~15-30 min remaining); ships next iteration based on outcomes.
