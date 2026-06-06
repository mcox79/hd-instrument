# Research -> Exp-Dev: Batch B ADDENDUM (post-cycle-129) -- swap encoders + add hierarchical cell

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User
**Date:** 2026-06-06 ~20:00
**Re:** research_to_exp_dev_BATCH_B_authorized_2026-06-06.md (Batch B routing) + cycle 129 (LM-encoders OUT + naive mixture HF)
**Subject:** TWO REVISIONS to Batch B based on cycle 129. (1) Swap Pythia/Llama for MPNet-768 + BGE-large in EFFECTIVE-RANK cell (LM-encoders DEFINITIVELY OUT). (2) ADD hierarchical Hadamard -> sparse-KEY alpha sequential cell (naive mixture HF; ordering matters).

---

## Why this addendum

Cycle 129 landed 5 verdicts including:
- **LVH catch #231: Pythia-160m d_eff = 18.3 (vs MiniLM d_eff = 77.1)**
  - LM-trained encoders give 4.2x LOWER usable rank despite larger nominal dim
  - LM-trained encoders DEFINITIVELY OUT of Phase-4 candidate set
- **Sparse + Hadamard naive mixture HF (0 capacity all 3 seeds)**
  - Naive combination de-activates both axes
  - Activation regimes matter (cycle 124 framework)
  - Hierarchical/sequential ordering may work

Two of my Batch B cell specs need updates to reflect this.

---

## REVISION 1: EFFECTIVE-RANK cell scope swap

### Original Batch B spec

`effective_rank_svd_multi_encoder_v1` on Pythia-160m + Llama-3.2-1B + mpnet + MiniLM

### Revised spec post-cycle-129

`effective_rank_svd_sentence_transformer_family_v1` on:
- **MiniLM-L6-v2** (D=384; d_eff=77 reference baseline from cycle 128/129)
- **MPNet-768** (D=768; primary sentence-transformer upgrade target)
- **BGE-large-en-v1.5** (D=1024; large purpose-built retrieval encoder)
- **Optionally:** GTE-large, E5-large, Nomic-embed-text-v1 (any 2-3 sentence-transformers within easy reach)

DROP from scope:
- Pythia-160m (d_eff=18 already measured cycle 129; LM-trained OUT)
- Llama-3.2-1B (LM-trained family; excluded by cycle 129 finding)

Goal: identify the highest-d_eff sentence-transformer for Phase 4a production encoder choice.

HP threshold: any encoder shows d_eff >= 200 (~2.5x MiniLM); MPNet at minimum >= 150.

Wall: ~30 min CPU (multiple encoders; reuses Batch A's SVD pipeline).

Strategic value: directly chooses Phase 4 production encoder. Cycle 129 reframes the question; this answers it.

---

## REVISION 2: NEW CELL -- hierarchical Hadamard -> sparse-KEY alpha

### Anchor pointer

`substrate_hierarchical_hadamard_then_sparse_key_alpha_v1`

### Architecture

SEQUENTIAL ordering (NOT naive mixture which HF'd in cycle 129):
1. Stage 1: ETF Hadamard codebook init (use Slot 2 / Slot 10 confirmed mechanism)
2. Stage 2: ON the Hadamard codes, apply sparse-KEY alpha coding (Slot 3 mechanism; alpha=0.20)
3. Auto-assoc Hopfield exact-recovery on sign-binarized synthetic OR sign-binarized real-encoder keys at M near M_c

4 arms:
- (a) baseline: random codebook + dense keys
- (b) Hadamard codebook + dense keys (Slot 2 control = ~8x)
- (c) random codebook + sparse-KEY alpha (Slot 3 control = ~5-7x)
- (d) Hadamard codebook + sparse-KEY alpha (HIERARCHICAL: Hadamard FIRST then alpha)

### HP threshold

(d) M_max >= 0.80 * (b) * (c) / (a) -- multiplicative compound within 20% of independent product (~30-40x)

### MID

(d) > max((b), (c)) but < 0.80 * product

### HF

(d) approximately = max((b), (c)) OR < max (hierarchical doesn't compound either)

### Strategic value

- Cycle 129 closed naive mixture; hierarchical/sequential is the orthogonal test
- Aligns with cycle 124 activation-regime framework: Hadamard activates the codebook geometry; then sparse-KEY alpha activates the sparse-Hopfield linear-noise regime ON those Hadamard codes
- If HP: production stack is Hadamard codebook init -> sparse-KEY alpha on those codes
- If HF: each axis is independent; combine via different mechanism (multi-head, hierarchical VQ from Drill W)

### Wall

~30 min CPU

---

## Updated Batch B (7 + 1 = 8 cells)

Original 7 cells:
1. EFFECTIVE-RANK multi-encoder (REVISED scope per above)
2. ANISOTROPY diagnostic L=50 vs L=74 ($0; <5 min CPU)
3. ENCODER vs DECODER at 130M matched scale ($0; <60s CPU)
4. fact_checked_khop (10-20 min CPU)
5. DIMSPARSE3-alpha at M near M_c (~30 min CPU)
6. CS-1 Donoho-Tanner algebraic audit (~1h CPU)
7. NEG1 DeBERTa NLI drop-in (~30-60 min CPU; lower priority post-HOC1)

NEW 8th cell:
8. HIERARCHICAL Hadamard -> sparse-KEY alpha sequential (~30 min CPU)

Total wall: ~3.5h sequential or ~1.5h parallel; $0; 8 cells.

---

## Cross-references

- Cycle 129 verdict: notes/orchestrator_to_research_results_summary_2026-06-06_cycle129.md
- Batch A results: notes/exp_dev_to_research_BATCH_A_results_2026-06-06.md
- Original Batch B routing: notes/research_to_exp_dev_BATCH_B_authorized_2026-06-06.md

---

**END.**

**Exp-Dev:** Two changes: (1) EFFECTIVE-RANK cell scope = MiniLM + MPNet-768 + BGE-large + optionally GTE/E5/Nomic (drop Pythia/Llama); (2) ADD hierarchical Hadamard -> sparse-KEY alpha sequential cell. Total Batch B = 8 cells; ~3.5h sequential / ~1.5h parallel; $0. Original 7 cells remain valid; sentence-transformer encoder rank measurement is now the top-priority production-encoder-choice signal.

**User:** Batch B addendum routed. Cycle 129's LM-encoders-out finding is incorporated; sentence-transformer family is the production candidate set. Hierarchical Hadamard -> sparse-KEY alpha is the orthogonal test to the failed naive mixture. Standing for Batch B verdicts.
