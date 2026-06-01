# Strategy request: LLM-1 token-prediction experiment (2x-deep-optimized config)

## Trigger: research 2x deep drill 2026-05-31 (2 parallel Sonnet drills synthesized)

Origin: user 2026-05-31 -- "do a 2x deep research on this experiment to maximize possibility of passing." Per [[feedback-2x-means-depth]] = operational deepening on the design choices that determine pass/fail. Full audit at `notes/research_llm1_design_audit_v1_2026-05-31.md`. 2 drills: encoding+capacity (P_def 0.15 on open-domain) + domain+baseline (P_def 0.37 on Python code).

## Finding (one paragraph)

The original LLM-1 spec was set up to fail (1M-token open-domain Wikipedia at 2% coverage with weak baselines). The 2 drills jointly establish an OPTIMIZED config where the substrate has a fair shot: **Python source code domain + N=16384 substrate + permutation binding + N_ctx=4-5 + |V|=8000 BPE + PMI-weighted storage + coverage-weighted scoring + composite score (accuracy + audit + edit + deletion) against MKN-5 + FAISS k-NN + tiny LSTM baselines**. Joint P_def: **0.37 for substrate winning on raw CWT1** (coverage-weighted top-1) vs full baseline set; **0.60-0.70 for substrate winning on composite score even if losing CWT1**. The composite-win case is substrate-distinctive — algebraic audit + edit-isolation + deletion-cert are substrate-only capabilities by construction, baselines score 0 on these. Honest framing: if substrate loses CWT1 but wins composite, the narrative shifts from "substrate is a next-token-predictor" to "substrate is an auditable retrieval system that handles the cases LLMs structurally cannot."

## Recommended action

**1. Cap_map: NEW row proposed (research-only 🔬).**

Row name: "Substrate as next-token-predictor at limited-capacity (Python source)"

Initial P-band: **0.30-0.45** for raw-CWT1 HARD-PASS; **0.55-0.70** for composite-score HARD-PASS

Caveats: (a) Python source code specifically (constrained domain); (b) coverage fraction CF >= 0.10 is the threshold for meaningful comparison; (c) Zipfian function-word interference is the load-bearing open empirical risk per drill A; (d) substrate retrieval mechanism is SINGLE-HOP classical matmul-then-argmax, NOT depth-5 Path D (Path D adds overhead with no benefit at depth=1)

**2. NEW experiment to dispatch.**

**Anchor**: `llm1_token_prediction_python_v1_n16384`

**Spec sketch (exp_dev refines)**:

**Domain**: single-project Python source code (e.g., curated 50-100 file Python data-science project, OR single OSS library like NumPy core at ~100K tokens training / ~10K held-out). High structural regularity; vocabulary in a single project cluster is 500-2K tokens; bigram/trigram patterns recur at extremely high rates.

**Tokenization**: SentencePiece or BPE at |V| = 8000.

**Substrate setup**:
- N = 16384 (use modern-Hopfield-activation regime validated v297 at max_M=16N)
- BSC codebook for token + position codewords (drawn once, frozen)
- Storage W = (1/N) Σ v_l k_l^T

**Context encoding (Plate HRR-style permutation binding, drill A recommended)**:
For context window of N_ctx tokens (token_1, ..., token_{N_ctx}):
```
ctx_codeword = sign( perm_1(v_token_1) ⊙ perm_2(v_token_2) ⊙ ... ⊙ perm_{N_ctx}(v_token_{N_ctx}) )
```
where perm_i are fixed cyclic-shift permutations (position-specific), ⊙ is element-wise bipolar product.

**Context length sweep**: N_ctx ∈ {3, 4, 5}. Drill A recommends N_ctx=4-5 strongly over N_ctx=8 (interference quadratic in N_ctx).

**Storage strategy: PMI-weighted (NOT random, NOT frequency)**:
Score each candidate (ctx, next_token) pair by `score = log(freq(ctx, tok) / (freq(ctx) × freq(tok)))` (pointwise mutual information).
Store top-M pairs by PMI score where (a) freq(ctx, tok) >= 2 (at least seen twice), (b) freq(ctx, tok) < 50 (not a trivial high-frequency pattern KN already captures perfectly).
Target M = 10K, 25K, 50K (sweep).

**Retrieval**: single-hop classical matmul-then-argmax. Query with `ctx_codeword`, compute `v_pred = W @ ctx_codeword`, return top-K most similar codewords from the value codebook. NOT Path D depth=5.

**Test split**: held-out 10K-token Python source; tokenize identically; for each position compute the test-context-codeword and query substrate.

**Baselines** (must be trained on SAME training split, same tokenization):
- **B1 MKN-5**: KenLM modified Kneser-Ney smoothed 5-gram language model
- **B2 FAISS k-NN**: FAISS index over same training datastore; retrieve nearest-neighbor context (TF-IDF or character n-gram embedding); predict next token of nearest neighbor. **Closest competitor for product positioning.**
- **B3 tiny LSTM**: 1-2M params, 1-2 layers, hidden 256-512, trained to convergence
- **B4 GPT-2-small reference**: optional zero-shot or quick fine-tune; reference ceiling only

**Substrate-distinctive measurements** (substrate-only; baselines score 0):
- Audit completeness: fraction of substrate predictions with valid algebraic decomposition trace (target = 1.0 by construction)
- Edit-consistency: edit 100 stored (ctx, tok) pairs; verify subsequent queries return updated value
- Deletion-consistency: delete 100 stored contexts; verify subsequent queries to those contexts either abstain or fall back

**Primary metrics**:
- **CWT1 = Coverage-Weighted Top-1**: top-1 correct on covered contexts / total covered contexts (substrate's raw retrieval quality on what it covers)
- **CF = Coverage Fraction**: covered contexts / total test contexts (substrate's distribution coverage)
- **Top-5 coverage-conditional**: at the covered slice
- **Perplexity on covered contexts** (NOT unconditional perplexity — Coverage limitations would dominate)
- **Interpolated perplexity**: substrate emits logit where context covered, KN-5 backs off elsewhere; this is the production-realistic measurement

**Composite score** (substrate-distinctive headline):
```
CS = 0.40 × CWT1 + 0.20 × audit_completeness + 0.20 × edit_consistency + 0.20 × deletion_consistency
```
Pre-reg HARD-PASS: CS >= 0.55.

**Pre-registered HARD-PASS / HARD-FAIL / MIDDLE-BAND** (joint drill A + drill B):

| Band | Condition |
|---|---|
| **HARD-PASS (raw)** | CWT1 ≥ 0.50 AND CF ≥ 0.10 AND CWT1 > MKN-5 conditional top-1 AND interpolated PPL < 0.95 × MKN-5 PPL AND composite ≥ 0.55 |
| **HARD-PASS (composite-only)** | CWT1 < MKN-5 OR PPL non-improving BUT composite ≥ 0.50 AND audit/edit/deletion all > 0.95 — substrate wins on distinctive capabilities |
| **MIDDLE-BAND** | CWT1 ∈ [0.35, 0.50) at CF ≥ 0.10 OR composite ∈ [0.45, 0.55] — partial signal; re-run at higher M |
| **HARD-FAIL** | CWT1 < 0.30 at CF ≥ 0.10 OR CF < 0.05 at M=50K OR PPL on covered contexts > 30 (worse than MKN-5 on code) |

**Cost**: ~1-2 weeks engineering + ~1-2h GPU per full run. Local 8GB GPU sufficient at N=16384 (Modern Hopfield validated at this N per v297). KenLM/FAISS/LSTM training are CPU. NO CLOUD SPEND.

**Sequencing**:
- Parallel to substrate-LLM Phase 1 build (no GPU contention; small workload)
- After D7 Bet B + reasoning storage Phase 1 smoke (per existing sequencing) — but this experiment is small enough it can be interleaved during their GPU idle periods
- Before substrate-LLM Phase 1 Week 5 evaluation — results from this experiment inform whether the substrate's bridge-output is meaningful for next-token prediction at small scale

## Confidence

Joint P_def estimates:
- **Raw CWT1 wins vs full baseline set on Python source**: 0.37 (drill B; range 0.30-0.45 depending on collision rate + coverage scaling)
- **Composite score wins even if CWT1 loses**: 0.60-0.70 (drill B; algebraic edit/deletion columns are substrate-dominant by construction)
- **Joint: at least one HARD-PASS condition (raw OR composite-only)**: ~0.55-0.70
- **HARD-FAIL across all bands**: ~0.15-0.25

Calibration penalty: -0.18 to -0.20 applied (uncharted regime; no direct published precedent for bipolar VSA at this capacity scale on code next-token prediction; closest evidence is HDC text classification at 93-94% accuracy on different task class).

## Critical open empirical risks (load-bearing for the verdict)

1. **Zipfian function-word interference** (drill A open synthesis question 1): high-frequency tokens ("the", "of", "and" — analogue: "def", "self", "return" in Python) appear in nearly every context window. Their codewords appear in nearly every stored context key, creating systematic off-diagonal interference in W not captured by random-pattern capacity analysis. **This is the biggest empirical unknown.**
2. **Context collision rate** (drill B open synthesis question 2): in repetitive code, many distinct positions share identical N_ctx token contexts (e.g., `return x` appears hundreds of times). Substrate's collision-resolution policy (most recent / average / superposition) may dominate CWT1.
3. **Coverage scaling law** (drill B open synthesis question 1): does CF grow sub-linearly with M_stored? If so, M=50K may not reach CF >= 0.10 on a 100K-token training corpus.
4. **Modern Hopfield regime accessibility** (drill A open synthesis question 3): the validated capacity envelope assumes pattern-separation; structured-corpus context keys may violate this.
5. **Long-tail behavior** (drill B citation Guo 2025): kNN retrieval helps high-frequency tokens, fails on long-tail; substrate's algebraic structure may or may not offer differential value here.

## Files of interest

- `notes/research_llm1_design_audit_v1_2026-05-31.md` (audit identifying 5 design issues with original spec)
- Drill A return: encoding + capacity findings (permutation binding recommended; N=16384; N_ctx=4-5; |V|=8000; PMI-weighted storage; P_def 0.15 on open-domain Wikipedia → 0.37 on Python)
- Drill B return: domain + baseline + criteria findings (Python source #1, SQL #2, dialogue #3, recipes #4, Wikipedia control; MKN-5 + FAISS k-NN + tiny LSTM baseline set; CWT1 + composite score; coverage-weighted reporting)
- `notes/substrate_capability_map.md` v297 (Modern Hopfield N=16384 max_M=16N empirically validated; substrate-side capacity headroom for this experiment)
- Memory: [[feedback-no-smoke]] (honest framing of weak vs strong baselines), [[feedback-2x-means-depth]] (drill discipline), [[feedback-lit-scan-calibration-penalty]] (P_def deflation)

## Not auto-dispatched

This is a research delivery + recommendation. Orchestrator decides:
- (a) Whether to add the cap_map row at 0.30-0.45 / 0.55-0.70 P-bands
- (b) Experiment dispatch timing (can run in parallel; doesn't gate on anything)
- (c) Engineering ownership (exp_dev for substrate side; testbed for baseline + comparison harness)
- (d) Whether to scope to single-project Python (~100K tokens) OR small-OSS-library (~500K tokens) — drill B recommends single-project for fair coverage

No engineering work begins without orchestrator queueing.

---
BULK-ARCHIVED 2026-06-01: previously processed (cap_map v311+ reflects acted-on work); routing closed retroactively per dashboard inbox-clearance Path A.
