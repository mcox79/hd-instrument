# Research drill 3 of 3: language ingest pipeline + composition with existing primitives + required new infrastructure

**Date:** 2026-06-26
**Author:** research (Opus 4.7-1M)
**Drill type:** Path C executable-pipeline synthesis. Inventory + composition + gap identification on substrate-native LM ingest.
**Trigger:** USER directive to formalize Path C + start substrate-native language ingest. Testbed audit confirmed 81% (375/464) of chain-grade portfolio Path C-compliant. This drill is the EXECUTABLE assembly: which primitives to wire in what order, what is MISSING, what 3-5 cells to dispatch.
**Inputs read:**
- hdlab/char_trigram_encoder.py (substrate-mined chain-grade text->HD encoder)
- hdlab/sequence_memory.py (c3 chain-grade S matrix; ordered-pair binding)
- hdlab/generation.py (g1 MEASURED_MECHANISM; S + Langevin + codebook cleanup)
- hdlab/binding.py (HRR FFT circular convolution + FHRR complex mul)
- hdlab/bundling.py (recency-weighted superposition)
- hdlab/memory.py (Codebook one-sided cosine-floor bound)
- hdlab/refuse_gate.py (V_REL=256 chain-grade envelope)
- hdlab/continual.py (NREM replay proven-bound +0.57 drift_reduction)
- hdlab/working_memory.py (K_total=4096 / k_per_bank=64 chain-grade)
- hdlab/multi_hop.py (naive_chain K=2 chain-grade; partition_routed_chain primitive)
- hdlab/predictive_coding.py (gated Hebbian write; residual gate)
- notes/research_n1v3_provenance_audit_2x_drill_2026-06-24.md (n1_v3 top1=0.4455 CG verified)
- notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md (hub-spoke spec)
- notes/research_decode_side_lm_improvements_substrate_native_2026-06-22.md
- notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md (META_HARNESS_RIGGED)
- notes/research_brain_to_lm_relevance_audit_2x_drill_2026-06-23.md
- experiments/exp_n3_text8_ingest_cert_v1.py (prior text8 ingest)
- experiments/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1.py (T-calibrated)
- data/text8.txt (100MB ASCII Wikipedia corpus; on disk)
- data/substrate_index/ (159 partitions; algebra/concept/math/meta canonical)

**Calibration penalty applied:** P deflated 0.15-0.25; novel-synthesis cap = 0.50 per [[feedback-lit-scan-calibration-penalty]]. Pipeline composition has chain-grade primitives end-to-end so deflation is closer to 0.15 than 0.25; the LM-style autoregressive top-K cleanup at vocabulary scale IS the novel-synthesis frontier and capped at 0.50.

---

## HEADLINE

**The Path C language-ingest pipeline is buildable TODAY from 8 chain-grade primitives + 3 NEW infrastructure pieces. The architecture is: deterministic-hash token codebook -> char-trigram-Encoder OR direct-hash-bipolar token encoder -> HRR circular-convolution n-gram binding -> SequenceMatrix S ordered-pair store -> SubstrateGenerator (S + Langevin + cleanup) for autoregressive output -> NREM replay decorator for continual ingest -> refuse-gate calibration on heldout perplexity. The 3 new infrastructure pieces are: (1) `hdlab/lm_eval_harness.py` META_M7-compliant LM eval (the RIGGED-HARNESS lesson from 2026-06-23 says this is LOAD-BEARING -- without it, every LM cell will hit the cosine-softmax-T=1.0 trap), (2) `hdlab/token_vocab.py` deterministic-hash vocabulary management with growth-tracking, (3) `hdlab/bigram_gap_measurement.py` standardized bigram-gap primitive (current substrate top1=0.4455 vs word-bigram 0.4734 = ~1.13 bits BPC gap at V_TOK=50087; gap closure is the Stage-4 enabling lever).**

**Substrate partition decision:** language atoms live in NEW partition `data/substrate_index/lang/` (parallel to algebra/concept/math/meta). Token vocabulary is `lang/tokens.jsonl` (deterministic-hash codebook entries); ordered-pair bindings `lang/sequences.jsonl`; ingest provenance `lang/audit.jsonl`. Reusing concept partition would conflate semantic concepts with surface tokens and violate the W-vs-S separation invariant from c3.

**P_deflated for full pipeline producing chain-grade text8 ingest at V_TOK=4096-8192:** **0.55** (each component independently chain-grade; n-gram extension to depth 4-5 is the bottleneck per HRR crosstalk at sigma ~ sqrt(K/N); META_M7 eval harness is the most likely failure-class but is a methodology fix not a substrate failure).

**P_deflated for chain-grade text8 LM beating word-bigram baseline (closing the ~1.13 bits BPC gap):** **0.30** (cap on novel-synthesis applied; n1_v3 already hits top1=0.4455 vs bigram 0.4734 with corpus + Pythia substrate; need to demonstrate the lift carries on Path C substrate-native text8 ingest; the BPC measurement methodology is THE risk).

---

## CHEAP DECISIVE TEST (pre-registered)

**Cell name:** `lang_ingest_vocab_bigram_meta_m7_v1` (Phase-1 bootstrap)
**Wall budget:** ~3-4 hr remote_cpu_queue (matmul-bound: M_TOKENS approx 5M bigrams x N_DIM=4096 codebook outer products)
**Pre-flight:** schema-vet via tools/exp_dev/formula_selftests.py; sigma=0 sanity: every bigram retrievable at recall=1.000 by-construction; HDLAB_EXP_NAME set; commit-first; META_M7 REPRODUCE_PV2 rail mandatory.

**4-arm comparison on text8 next-token prediction (8192-token vocab; 80M train / 5M held tokens):**

| ARM | Token encoder | N-gram binding | Generation | Eval metric |
|---|---|---|---|---|
| ARM_A_NULL_UNIGRAM | char_trigram (existing) | NONE (unigram only) | argmax over codebook | top1 + cv |
| ARM_B_BIGRAM_HRR | deterministic-hash bipolar | HRR circular convolution depth=2 | S @ k_prev + cleanup | top1 + cv + BPC |
| ARM_C_TRIGRAM_HRR | deterministic-hash bipolar | HRR depth=3 | S + Langevin + cleanup | top1 + cv + BPC |
| ARM_D_CHAR_TRIGRAM_BIGRAM | char_trigram | HRR depth=2 | S + cleanup | top1 + cv + BPC |

**Per-arm metrics (META_M7-compliant; learned from 2026-06-23 RIGGED-HARNESS audit):**
- **top1 accuracy** (substrate's strongest metric per n1_v3 CG ruling; NOT BPC)
- **top5 accuracy** (per [[feedback-experiment-bias-master-checklist]] BIAS-S band-calibration regime-check)
- **BPC measured via temperature-calibrated softmax** (T-grid [0.05, 0.1, 0.2, 0.5, 1.0]; auto-pick T minimizing held BPC; mandatory per META_HARNESS_RIGGED v2)
- **bigram-gap** = (substrate_top1 - word_bigram_top1) absolute; sign matters
- **per-seed cv** (3 seeds at smoke; 5 at full)

**Discriminator (load-bearing):** does ARM_B_BIGRAM_HRR (substrate-native deterministic-hash bipolar encoder + HRR depth=2 binding + cleanup) match or beat n1_v3 cert anchor top1=0.4455 on equivalent V_TOK regime? Specifically: does substrate-native Path C ingest carry the same bigram-gap-closure signal that the Pythia/word2vec-encoded n1_v3 demonstrated?

**Pre-reg HARD bands:**
- **HARD_PASS**: ARM_B_BIGRAM_HRR top1 >= 0.40 AND cv <= 0.05 AND BPC at T* below random-baseline by >= 0.5 bits AND verified-by-construction-NOT-saturated (i.e. discriminator visible: ARM_A_NULL_UNIGRAM top1 <= 0.25 at same V_TOK). P_deflated = **0.30**.
- **MIDDLE_BAND**: ARM_B_BIGRAM_HRR top1 in [0.20, 0.40) OR cv in (0.05, 0.10]. P_deflated = **0.45**.
- **HARD_FAIL**: ARM_B_BIGRAM_HRR top1 < 0.20 AT EVERY temperature AND BPC > random-baseline (substrate worse than uniform). P_deflated = **0.25**.

**HARD-FAIL revival paths pre-registered (per [[feedback-route-negatives-to-research-2x-3x-revival-drills]]):**
- If ARM_B HF + ARM_C HF + ARM_D CG: char-trigram encoder is the load-bearing fix; route Path C atomization to char_trigram_encoder as the substrate-native text encoder primitive.
- If ALL non-baseline arms HF: cleanup is failing at LM scale; route to Modern Hopfield attractor + softmax-beta cleanup (Gap 3 ANCHOR_1 in flight) as composition layer.
- If ARM_B passes BPC band but FAILS top1 band: BPC-vs-top1 measurement methodology not yet aligned for Path C (META_HARNESS_RIGGED reissue); dispatch META_M7_v2 audit cell before any more LM ingest.

**Distinguishing-regime gate (mandatory per C5):**
- ARM_A_NULL_UNIGRAM must HARD_FAIL at top1 <= 0.25 (otherwise V_TOK is too small and substrate cannot fail by-construction; META rule from `META_multi_bank_WM_per_bank_capacity_governs`).
- ARM_D_CHAR_TRIGRAM_BIGRAM is the discriminator on encoder choice: if Arms B and D both PASS, the encoder is interchangeable; if only D passes, char_trigram is load-bearing; if only B passes, deterministic-hash bipolar is the cleaner substrate-native path.

---

## SECTION 1: Path C pipeline requirements (operational spec)

### 1.1 Token-to-codebook stage

**Substrate-native token encoder spec:**
```python
def token_to_hd(token: str, n_dim: int = 4096) -> np.ndarray:
    seed = int.from_bytes(blake2b(token.encode(), digest_size=4).digest(), "big")
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)
```

Identical pattern to `_bipolar_hv` in `hdlab/char_trigram_encoder.py:44` -- the difference is the seed input (whole token vs trigram). Per-token codebook entries are deterministic from token content; vocabulary GROWTH is automatic (new token -> new hash -> new entry; never collides for distinct strings with high probability per birthday bound at 32-bit seed: 65k tokens have collision probability ~0.5; at 64-bit seed: 4B tokens have collision prob ~0.5; recommendation: use blake2b digest_size=8 for vocabulary > 50k tokens).

**Verified primitives reused:**
- `_seed_for_trigram` deterministic hash pattern (hdlab/char_trigram_encoder.py:38)
- `_bipolar_hv` bipolar codebook generation (hdlab/char_trigram_encoder.py:44)
- `CharTrigramEncoder._hv_for_trigram` caching pattern (hdlab/char_trigram_encoder.py:75)

**Honest scope:** at V_TOK = 8192 with N_DIM = 4096, the bipolar codebook has crosstalk floor approx sqrt(V_TOK / N_DIM) = sqrt(2) approx 1.41 vs ideal orthogonality. This is the per-token signal-to-noise budget. n1_v3 at V_TOK=50087 N_DIM=4096 hits top1=0.4455 = 36.5x lift over Pythia residual ratio so the regime IS substrate-feasible at high vocabulary; the question is whether the deterministic-hash bipolar codebook is sufficient OR if char_trigram bag-of-features is required.

### 1.2 N-gram binding stage (HRR circular convolution)

**Primitive:** `hdlab/binding.py:bind` (HRR via FFT). Verified line 17-20:
```python
fa = torch.fft.fft(a)
fb = torch.fft.fft(b)
out = torch.fft.ifft(fa * fb).real.to(a.dtype)
```

**Bigram binding:**
```python
bigram_hv = bind(token_to_hd(t_prev), permute(token_to_hd(t_curr)))
```
The `permute` rotates t_curr by 1 position to make binding NON-commutative (preserves word order). Without permute, bind(a,b) == bind(b,a) and "cat dog" is indistinguishable from "dog cat".

**Trigram binding (recursive):**
```python
trigram_hv = bind(bind(token_to_hd(t_minus2), permute(token_to_hd(t_minus1))),
                  permute(permute(token_to_hd(t_curr))))
```

**HRR crosstalk budget at depth K:** sigma_noise ~ sqrt(K / N_DIM); cleanup recovers when codebook density M satisfies M < N_DIM / (4 ln(M)) (Plate 1995 capacity bound). At N_DIM=4096, K=3, V_TOK=8192: bound says cleanup recovers IF V_TOK < 4096 / (4*9.0) approx 113 -- this is the per-position binding capacity AT FULL TRIGRAM DEPTH; in practice we use cleanup against ALL V_TOK = 8192 entries which exceeds the bound, so cleanup will be degraded at depth K=3 unless we use partition routing or Modern Hopfield (Ramsauer 2021) attractor sharpening. This is THE structural risk for trigram-depth ingest and is why ANCHOR_2 (Modern Hopfield prototype attractor) below is rank-2.

### 1.3 Sequence binding stage (g1b S matrix)

**Primitive:** `hdlab/sequence_memory.py:SequenceMatrix` (chain-grade c3). For each text8 sentence:
```python
S = SequenceMatrix(n_dim=4096)
hd_seq = torch.stack([token_to_hd(t) for t in tokens])  # [T, n_dim]
S.bind_sequence(hd_seq)  # writes all adjacent ordered pairs
```

The S matrix is `[N_DIM, N_DIM]` -- 64MB at N_DIM=4096 float32; 256MB at N_DIM=8192. Memory-feasible at single-machine scale.

**Capacity:** c3 cell HARD_PASS at depth=10, K=20, N_DIM=4096; g1b autoregressive generation MEASURED_MECHANISM at sequence-pair density approx 327 pairs at N_DIM=4096 (Hebbian capacity bound). text8 has approx 17M tokens = 17M ordered-pairs; this VASTLY exceeds the single-S capacity. Need PARTITIONED S matrices (one per topic / one per chunk) OR sparse-S construction. Recommendation: use partition_routed_chain pattern from `hdlab/multi_hop.py:189` -- route each pair to a partition by hash(t_prev) mod n_partitions; each partition holds approx 17M / 1024 = 17k pairs which IS within capacity at N_DIM=4096.

### 1.4 W matrix (content / Hebbian) ingestion

**Architecture invariant from c3:** S matrix (sequence binding) is SEPARATE from W matrix (content store). W is updated via Hebbian outer-product when binding tokens to their semantic representations (e.g. token-to-context-window-bundle). For pure n-gram LM, W is NOT NEEDED -- the S matrix IS the language model. W enters only when ingesting semantic content (e.g. binding "Paris" to the bundle of context words it co-occurs with).

For substrate-native LM bootstrap, the architecture is:
- S matrix: ordered-pair token bindings (next-token prediction)
- Codebook (Codebook class from hdlab/memory.py): all V_TOK token HD vectors for cleanup
- W matrix: ENTERS LATER for semantic content (Phase-2 ingest of math/science corpora)

### 1.5 Storage partition design

**Decision:** new partition `data/substrate_index/lang/`. Files:
- `lang/tokens.jsonl` -- one atom per token; atom.id = token string, atom.metadata.codebook_seed = blake2b hash, atom.metadata.frequency = corpus count
- `lang/sequences.jsonl` -- relation atoms for ordered-pair bindings (NOT individual pair entries -- the S matrix lives in `data/lang_S_matrix.npz`; this file records BINDING_EVENTS metadata for audit)
- `lang/audit.jsonl` -- standard partition audit log
- `lang/S_matrix.npz` -- the ordered-pair S matrix as npz (memmapped at load)
- `lang/codebook.npz` -- the [V_TOK, N_DIM] codebook for cleanup

**Why a new partition (not concept/algebra):**
- W-vs-S separation from c3 META atom: language sequence S matrix is orthogonal to algebra/concept W matrices.
- Substrate-mining discipline: language data is a NEW modality; conflating with existing partitions risks store-load failures + per-class metric pollution.
- Per `feedback-never-git-add-A`: the partition is git-tracked; bulk-ingest writes must serialize per `reference-substrate-bulk-ingest-concurrency-gotcha`.

---

## SECTION 2: Existing primitives composition (assembly pseudocode)

```python
# ============================================================================
# Substrate-native language ingest pipeline (Path C; zero LLM at inference)
# ============================================================================

import numpy as np, torch, hashlib
from hdlab.char_trigram_encoder import CharTrigramEncoder
from hdlab.binding import bind, unbind
from hdlab.bundling import bundle
from hdlab.sequence_memory import SequenceMatrix
from hdlab.memory import Codebook
from hdlab.generation import SubstrateGenerator
from hdlab.refuse_gate import calibrate_refuse_threshold
from hdlab.continual import nrem_replay_decorator
from hdlab.multi_hop import partition_routed_chain
from hdlab.predictive_coding import predict, residual

N_DIM = 4096
V_TOK = 8192
N_PARTITIONS = 16  # S-matrix routing partitions

# ----------------------------------------------------------------------------
# Stage 1: Build deterministic-hash token codebook
# ----------------------------------------------------------------------------
def token_to_hd(token: str, n_dim: int = N_DIM) -> np.ndarray:
    seed = int.from_bytes(
        hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest(), "big"
    ) & 0xFFFFFFFF
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)

# Build top-V_TOK most-frequent tokens from text8 stream
from collections import Counter
text8 = open("data/text8.txt").read()  # 100MB
tokens = text8.split()  # ~17M whitespace-separated words
freq = Counter(tokens)
vocab = [t for t, _ in freq.most_common(V_TOK)]
token_to_idx = {t: i for i, t in enumerate(vocab)}
unk_idx = V_TOK  # OOV slot

# Codebook: [V_TOK+1, N_DIM] bipolar
codebook_np = np.stack([token_to_hd(t) for t in vocab] + [token_to_hd("<UNK>")])
codebook = torch.from_numpy(codebook_np).float()  # [V_TOK+1, N_DIM]

# ----------------------------------------------------------------------------
# Stage 2: Partition-routed S matrices for sequence binding
# ----------------------------------------------------------------------------
S_partitions = [SequenceMatrix(N_DIM) for _ in range(N_PARTITIONS)]

def route_partition(token_idx: int) -> int:
    return token_idx % N_PARTITIONS

# Stream-ingest bigrams from text8
for i in range(1, len(tokens)):
    t_prev_idx = token_to_idx.get(tokens[i-1], unk_idx)
    t_curr_idx = token_to_idx.get(tokens[i], unk_idx)
    k_prev = codebook[t_prev_idx]
    k_curr = codebook[t_curr_idx]
    p = route_partition(t_prev_idx)
    S_partitions[p].bind_pair(k_prev, k_curr)
    # Checkpoint every 1M pairs (D1/D2 timeout discipline)
    if i % 1_000_000 == 0:
        for pi, S in enumerate(S_partitions):
            np.save(f"data/lang_S_p{pi}_checkpoint_i{i}.npy", S.S.numpy())

# ----------------------------------------------------------------------------
# Stage 3: Autoregressive generation (substrate-native; zero LLM)
# ----------------------------------------------------------------------------
def generate_next_token(t_prev: str, k_top: int = 5) -> list[tuple[str, float]]:
    t_prev_idx = token_to_idx.get(t_prev, unk_idx)
    k_prev = codebook[t_prev_idx]
    p = route_partition(t_prev_idx)
    k_predicted = S_partitions[p].predict_next(k_prev)
    # Cosine sim to all codebook entries; top-K cleanup
    cb_norm = codebook / (torch.linalg.norm(codebook, dim=1, keepdim=True) + 1e-8)
    k_pred_norm = k_predicted / (torch.linalg.norm(k_predicted) + 1e-8)
    sims = cb_norm @ k_pred_norm
    top_idx = torch.argsort(sims, descending=True)[:k_top]
    return [(vocab[int(i)] if int(i) < V_TOK else "<UNK>",
             float(sims[int(i)])) for i in top_idx]

# ----------------------------------------------------------------------------
# Stage 4: Refuse-gate calibration on heldout
# ----------------------------------------------------------------------------
held_tokens = tokens[-100000:]
in_dist_scores = []
ood_scores = []
for i in range(1, len(held_tokens)):
    preds = generate_next_token(held_tokens[i-1], k_top=1)
    actual = held_tokens[i]
    if preds[0][0] == actual:
        in_dist_scores.append(preds[0][1])
    else:
        ood_scores.append(preds[0][1])
gate = calibrate_refuse_threshold(
    torch.tensor(in_dist_scores), torch.tensor(ood_scores), split=0.5
)
# gate["tau"] is the substrate's confidence threshold for next-token emission

# ----------------------------------------------------------------------------
# Stage 5: NREM-replay continual ingest decorator
# ----------------------------------------------------------------------------
# Wrap the bind_pair calls with periodic replay-consolidation
# (Replay buffer = recently-seen pairs; replay re-Hebbs random subset)
@nrem_replay_decorator(replay_every=10000, replay_frac=0.2)
def write_pair_with_replay(S, k_prev, k_curr, **kwargs):
    S.bind_pair(k_prev, k_curr)

# ----------------------------------------------------------------------------
# Stage 6: META_M7-compliant eval harness (NEW; see Section 3)
# ----------------------------------------------------------------------------
# from hdlab.lm_eval_harness import eval_lm_top1_calibrated_BPC
# metrics = eval_lm_top1_calibrated_BPC(
#     generate_fn=generate_next_token, vocab=vocab,
#     held_tokens=held_tokens, t_grid=[0.05, 0.1, 0.2, 0.5, 1.0]
# )
```

**Composition validation against chain-grade primitives:**
- `token_to_hd` -> reuses `_bipolar_hv` pattern (char_trigram_encoder CG)
- `bind/unbind` -> hdlab/binding.py (verified in c3 / g1b CG cells)
- `SequenceMatrix.bind_pair` -> c3 chain-grade primitive
- `Codebook.lookup` -> cosine-floor-bound from hdlab/memory.py
- `partition_routed_chain` -> hdlab/multi_hop.py multi-hop CG primitive
- `calibrate_refuse_threshold` -> V_REL=256 chain-grade envelope
- `nrem_replay_decorator` -> +0.57 drift_reduction proven-bound

**8 of 9 ingest-pipeline stages have chain-grade primitive backing.** The 9th (META_M7 LM eval harness) is the NEW infrastructure piece.

---

## SECTION 3: Required new infrastructure (3 pieces)

### 3.1 `hdlab/lm_eval_harness.py` -- META_M7-compliant LM eval

**Why load-bearing:** the 2026-06-23 RIGGED-HARNESS audit (notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md + cert ledger row 698) found that **7+ HARD_FAILs on substrate-as-LM were methodology-confound NOT substrate-failure**. The trap: cosine-similarity outputs are NOT log-probabilities; softmax at T=1.0 on cosine outputs uniformizes the distribution; BPC computed from uniform predictions LOOKS WORSE than random when in fact top1 prediction is strong (n1_v3 top1=0.4455 vs unigram 0.2757). Every LM ingest cell will hit this trap without a standardized eval harness.

**Interface spec:**
```python
def eval_lm_top1_calibrated_BPC(
    generate_fn: Callable[[str, int], list[tuple[str, float]]],
    vocab: list[str],
    held_tokens: list[str],
    t_grid: list[float] = [0.05, 0.1, 0.2, 0.5, 1.0],
) -> dict:
    """META_M7-compliant LM eval. Returns top1, top5, BPC at OPTIMAL temperature.

    Mandatory output fields per [[feedback-experiment-bias-master-checklist]]:
      - top1, top1_cv (3+ seeds)
      - top5, top5_cv (BIAS-S regime check)
      - BPC_T_optimal, T_optimal (temperature-calibrated; auto-pick T minimizing BPC)
      - BPC_T_1p0 (uncalibrated reference; the RIGGED metric)
      - unigram_baseline_top1, word_bigram_baseline_top1
      - bigram_gap = top1 - word_bigram_baseline_top1
      - sanity_top1_at_random = 1.0 / len(vocab)
      - regime_check_passed: bool (top1 > 2*sanity_top1)
    """
```

**Build cost:** ~1 day; ~150 lines; verification test in `verification/test_lm_eval_harness.py`.

### 3.2 `hdlab/token_vocab.py` -- vocabulary management

**Why load-bearing:** ingest pipelines need deterministic vocabulary state (cannot recompute on every cell run); the OOV / UNK handling is per [[feedback-clean-encoder-tests-no-contamination]] discipline.

**Interface spec:**
```python
class TokenVocab:
    def __init__(self, n_dim: int = 4096, v_max: int = 50000): ...
    def build_from_corpus(self, tokens: Iterable[str], v_top: int) -> None:
        """Builds vocab from top-V most-frequent tokens; persists to lang/tokens.jsonl"""
    def encode(self, token: str) -> tuple[int, np.ndarray]:
        """Returns (idx, hd_vector). UNK token gets idx=v_max, deterministic UNK hv."""
    def codebook_matrix(self) -> np.ndarray:
        """Returns [V_TOK+1, N_DIM] codebook (cached after first call)."""
    def freeze(self) -> None:
        """Disable further vocabulary growth. Required before publishing chain-grade cell."""
    def grow_with(self, new_tokens: list[str]) -> int:
        """Add new tokens to vocab; returns # added. Only callable pre-freeze."""
    def save(self, partition_dir: str) -> None: ...
    @classmethod
    def load(cls, partition_dir: str) -> "TokenVocab": ...
```

**Build cost:** ~1 day; ~120 lines.

### 3.3 `hdlab/bigram_gap_measurement.py` -- standardized gap primitive

**Why load-bearing:** "bigram gap" is the LM measurement axis but currently every cell reimplements it differently (n1_v3 vs n3 vs hoc1_word_bigram_v1). Standardize once.

**Interface spec:**
```python
def measure_bigram_gap(
    substrate_top1: float, held_tokens: list[str], vocab: list[str]
) -> dict:
    """Compute substrate top1 - word-bigram top1 with consistent baseline.

    word-bigram baseline = empirical conditional P(t_curr | t_prev) from held stream.
    Returns:
      gap: substrate_top1 - bigram_top1 (positive = substrate ABOVE bigram; chain-grade lift)
      bigram_top1: the baseline
      substrate_top1: passed through
      substrate_vs_uniform_baseline: substrate_top1 - 1/|vocab|
      n_bigrams_seen_at_test: count of bigrams where t_prev was seen in training
      coverage: fraction of test bigrams where bigram baseline can be computed
    """
```

**Build cost:** ~3 hours; ~80 lines.

### 3.4 What is NOT new infrastructure (already in hdlab/)

- LM-style autoregressive top-K cleanup: **already in `hdlab/generation.py:SubstrateGenerator`** (line 86). g1 MEASURED_MECHANISM; the cleanup IS the load-bearing complement (cell-validated).
- Corpus chunking + streaming: standard Python iteration over `text8.txt`; no special primitive needed (the partition_routed_chain handles routing).

---

## SECTION 4: Composition with in-flight Gap work

In-flight gap cells (per overnight queue inspection):

| Gap | Cell in queue | Expected outcome | Impact on language ingest |
|---|---|---|---|
| Gap 1 routing | `gap1_partition_routing_bidirectional_collide_and_fly_lsh_v1_META_M7` running | If HP: oracle-routing scope closed; partition-routed-chain becomes autonomous | **MAJOR**: N_PARTITIONS=16 stage in pipeline above becomes self-routing; can scale to N_PARTITIONS=1024+ |
| Gap 3 compositional | `gap3_modern_hopfield_prototype_attractor_v1` queued | If HP: basin-sharpening attractor closes linear-bundle-ceiling at 0.5 heldout | **CRITICAL for trigram depth**: Section 1.2 noted HRR crosstalk floor at depth K=3; Modern Hopfield cleanup directly sharpens that |
| Gap 4 continual | `gap4_two_tier_generational_W_v1` running | If HP: TWO_TIER hippo-cortex closes scaling | **ENABLES decade-scale ingest**: continual text8 -> wikitext -> arxiv ingestion without forgetting earlier passes |
| Gap 2 anisotropy | CLOSED (cap_map RED->GREEN) | Treated as feature not bug | Affirms substrate is ALREADY at cosine-physics-floor; pipeline does NOT need geometric rescue |

**If all 4 gaps land chain-grade simultaneously:**
- Pipeline becomes: substrate has full brain stack (hippo Gap 4 + PFC compositional Gap 3 + cortex storage + sleep NREM + multi-hop Gap 1 routing)
- Language ingest then composes ALL primitives: tokens -> bigrams -> trigrams (via Modern Hopfield) -> schemas (via compositional) -> continual ingest (via TWO_TIER)
- This is the **glass-box LM equivalence path**: every step auditable; zero LLM at inference

**Composition order (after gaps land):**
1. `lang_ingest_vocab_bigram_meta_m7_v1` (THIS cell -- Phase 1; closes Section 2 pipeline)
2. `lang_ingest_trigram_modern_hopfield_attractor_v1` (Phase 2; uses Gap 3 attractor for depth=3+)
3. `lang_ingest_two_tier_continual_v1` (Phase 3; uses Gap 4 for adding wikitext on top of text8)
4. `lang_ingest_partition_routed_autonomous_v1` (Phase 4; uses Gap 1 router; closes oracle dependency)

---

## SECTION 5: Audit-device lift

Stage 3 audit-device chain-grade at production (V_C=2000, V_REL=50, M_KV=10k, p95<0.2ms). Language ingest extends:

| Layer | Current (Audit-Device) | After Language Ingest |
|---|---|---|
| Input encoding | char-trigram on names | char-trigram OR deterministic-hash bipolar tokens |
| Storage | W (content) + R (relations) + E (entities) | + S (sequences) + lang/tokens codebook |
| Output | retrieve (cosine + refuse-gate) | + GENERATE (SubstrateGenerator autoregressive) |
| Audit | full provenance per query | + per-token generation provenance (NEW) |
| Latency | p95 < 0.2ms | + ~0.5-1ms per generated token (estimate; S @ k_prev = 4096x4096 mul = 16M ops) |
| LLM at inference | 0 | 0 (CONFIRMED) |

**Glass-box LM property:** every generated token has a provenance chain (t_prev -> partition p -> S_p @ k_prev -> top-K cosine sims -> cleanup pick). NO LLM in the loop. The audit-device's per-query trace extends naturally to per-token trace.

---

## SECTION 6: Risk surfaces

### R1: audit_core_C2_C3_whitened_pythia/llama dependency (USER-flagged)

**Audit:** searched hdlab/ for "pythia" / "llama" / "minilm" string references in production code paths. Findings:
- `hdlab/`: **0 hits** of pythia/llama/minilm in production primitives. The hdlab/ library is encoder-agnostic.
- `experiments/`: many hits (these are CELLS that USED Pythia/MiniLM as DIAGNOSTIC PROBES, per [[project-path-c-substrate-owned-encoder-is-the-answer]]). The cells are not on the production hdlab/ path.

**Verdict:** R1 RESOLVED. Production hdlab/ code is encoder-agnostic; Pythia/LLama appearances are in diagnostic experimental cells only. Path C compliance per testbed audit holds.

### R2: corpus completeness; substrate-mine FIRST

Substrate-mined: cert_ledger.jsonl has 8+ text8-related cells (exp_text8_substrate_pseudoLM_*, exp_substrate_pc_hierarchy_text8_lm_*, exp_n3_text8_ingest_cert_v1*). Per [[feedback-substrate-mine-capacity-before-extrapolating]]:

**Existing text8 ingest state:**
- exp_n3_text8_ingest_cert_v1_smoke2: ledger row indicates METRICS_INFRA_FAILURE (smoke-only; never reached full)
- exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1: T-calibrated variant exists; partial results
- exp_substrate_pc_hierarchy_text8_lm_v2: predictive coding hierarchy variant; partial_metrics_s0.json only

**None of the existing text8 cells used the FULL pipeline from Section 2.** The closest is n1_v3 on Wikipedia (top1=0.4455 CG) but that used Pythia residuals NOT substrate-native encoding. The Path C substrate-native text8 ingest pipeline IS un-trodden ground in the substrate; this cell IS the first attempt.

**Verdict:** R2 acknowledged; pipeline is GENUINELY novel for Path C substrate-native; the prior cells are diagnostic probes (Pythia-encoded) not Path C-compliant attempts.

### R3: vocabulary scale risk -- N=8192 may cliff at small V_TOKEN

HRR crosstalk floor at V_TOK / N_DIM = 8192/4096 = 2.0 -- above the orthogonality budget. The substrate IS in elevated-crosstalk regime at this vocabulary. Modern Hopfield attractor (Gap 3 ANCHOR_1) is the canonical fix; without it, Phase-1 cell may MIDDLE_BAND at top1 around 0.3.

**Mitigation:** smoke at V_TOK=2048 first; if HARD_PASS at low vocab, scale up. If full cell at V_TOK=8192 HARD_FAILs but smoke at V_TOK=2048 HARD_PASSES, the failure is vocabulary-scale-driven not architecture-driven (revival path = wait for Gap 3 Modern Hopfield to land).

### R4: smoke-to-full sign-flip risk (META_M7)

Per the 2026-06-23 RIGGED-HARNESS finding, smoke runs at N_TOKENS=100k can sign-flip vs full at N_TOKENS=80M. Mitigation: smoke at 10x reduction NOT 1000x; pre-reg HARD_PASS bands MUST be band-relative not absolute; mandatory T-calibration sweep both at smoke AND full.

### R5 (NEW): Hebbian capacity overrun at full text8

17M ordered pairs across N_PARTITIONS=16 = ~1M pairs per partition. Per Plate 1995 HRR capacity bound: N_DIM=4096 supports approx N/(4 ln M) = 4096/(4*13.8) = 74 ORTHOGONAL pairs before degradation. At 1M pairs per partition, every partition is at 13,500x over capacity. The S matrix sum-saturates and predict_next returns the column-sum-attractor (per docstring at `hdlab/sequence_memory.py:88` "the raw S-matrix outputs may drift toward the column-sum attractor").

**This is THE risk.** Mitigations:
- **Codebook cleanup at every step** (architectural; already in pipeline)
- **Sparse-S construction**: only bind pairs where conditional probability P(t_curr | t_prev) > threshold (drops uninformative noise)
- **N_PARTITIONS scale-up**: at N_PARTITIONS=1024 we have 17k pairs per partition (still over capacity but only 230x not 13,500x; closer to Modern-Hopfield-rescuable regime)
- **Frequency-weighted binding**: bind_pair scaled by sqrt(freq) instead of unit Hebbian; concentrates capacity on frequent bigrams

**Recommendation:** Phase-1 cell uses N_PARTITIONS=64 + sparse-S threshold P(t_curr|t_prev) > 0.001 + codebook cleanup; if HF, revival path is partition_routed_chain over more partitions OR sparse-S threshold tightening.

---

## SECTION 7: Recommended ingest cells (3-5 concrete; rank-ordered)

### CELL 1 (rank-1, cheapest decisive): `lang_ingest_vocab_bigram_meta_m7_v1`

- **Goal:** vocabulary build + bigram ingest + bigram-gap measurement; META_M7-compliant
- **Arms:** 4 (ARM_A_NULL_UNIGRAM / ARM_B_BIGRAM_HRR / ARM_C_TRIGRAM_HRR / ARM_D_CHAR_TRIGRAM_BIGRAM)
- **Config:** V_TOK=8192, N_DIM=4096, N_PARTITIONS=64, sparse-S threshold=0.001, text8 train=80M / held=5M
- **Cost:** ~3-4 hr remote_cpu_queue (matmul-bound)
- **Pre-reg bands:** see Section "Cheap decisive test" above
- **Discriminator:** ARM_B vs ARM_A is encoder-question; ARM_B vs ARM_D is char_trigram-vs-token-hash question
- **META_M7 rail:** mandatory T-grid; mandatory top1+top5+BPC report; sanity-top1-at-random pre-reg
- **Dependency:** none; can ship immediately
- **Output partition:** new `data/substrate_index/lang/`

### CELL 2 (rank-2, depth extension): `lang_ingest_trigram_modern_hopfield_attractor_v1`

- **Goal:** trigram-depth ingest using Modern Hopfield attractor for cleanup (closes HRR crosstalk at K=3)
- **Arms:** 3 (ARM_TRIGRAM_VANILLA_CLEANUP / ARM_TRIGRAM_MODERN_HOPFIELD / ARM_TRIGRAM_K_SET_BUNDLE)
- **Config:** V_TOK=8192, N_DIM=4096, N_PARTITIONS=64, depth=3
- **Cost:** ~5-6 hr remote_cpu_queue
- **Dependency:** Gap 3 Modern Hopfield primitive must land chain-grade FIRST (in queue)
- **Pre-reg:** HARD_PASS = ARM_TRIGRAM_MODERN_HOPFIELD top1 >= 0.40 AND beats ARM_TRIGRAM_VANILLA_CLEANUP by >= 0.05 absolute

### CELL 3 (rank-3, generation evaluation): `lang_ingest_autoregressive_generation_eval_v1`

- **Goal:** end-to-end generation quality (not just next-token) on text8; substrate generates 50-token sequences and we measure trigram quality, repetition rate, diversity
- **Arms:** 3 (ARM_GREEDY_TOPK1 / ARM_NUCLEUS_TOPP_0p9 / ARM_LANGEVIN_SIGMA_0p1)
- **Config:** Uses g1 SubstrateGenerator from Cell 1's S matrices; sigma_scale sweep [0.0, 0.05, 0.1, 0.2]
- **Cost:** ~2-3 hr local_cpu_queue (generation is cheap; cleanup is per-token argmax)
- **Pre-reg:** HARD_PASS = diversity_5gram >= 0.3 AND repetition_rate <= 0.4 AND trigram_chrf >= 0.2
- **Substrate-product implication:** if HP, substrate IS a viable autoregressive generator at this vocabulary scale

### CELL 4 (rank-4, refuse-gate calibration): `lang_ingest_refuse_gate_calibration_text8_heldout_v1`

- **Goal:** apply hdlab/refuse_gate.py to LM scores; calibrate tau on heldout; demonstrate substrate-LM-with-confidence
- **Arms:** 2 (ARM_NO_GATE_BASELINE / ARM_REFUSE_GATE_TAU_CALIBRATED)
- **Config:** uses Cell 1's S matrices; in-dist = top1==actual scores; ood = top1!=actual scores
- **Cost:** ~30 min local_cpu_queue (single-pass over held)
- **Pre-reg:** HARD_PASS = balanced_acc >= 0.70 AND in_dist_accept >= 0.55 AND ood_refuse >= 0.55
- **Substrate-product implication:** glass-box LM with substrate-native "I don't know" capability

### CELL 5 (rank-5, continual extension): `lang_ingest_continual_nrem_replay_v1`

- **Goal:** demonstrate substrate ingests text8 + wikitext-103 sequentially without forgetting text8 bigram-gap
- **Arms:** 3 (ARM_SEQUENTIAL_NO_REPLAY / ARM_NREM_REPLAY_FRAC_0p2 / ARM_INTERLEAVED_BASELINE)
- **Config:** ingest text8 first (Cell 1's pipeline), measure bigram-gap, then ingest wikitext-103, measure bigram-gap on text8 AGAIN, measure forgetting
- **Cost:** ~8-10 hr remote_cpu_queue (multi-corpus ingest)
- **Dependency:** Gap 4 TWO_TIER may land first; if so, compose with TWO_TIER
- **Pre-reg:** HARD_PASS = text8_bigram_gap_after_wikitext / text8_bigram_gap_before >= 0.9 (less than 10% forgetting)

**Recommendation:** ship Cell 1 FIRST (decisive on encoder + bigram architecture). Cells 2-5 wait for: Cell 1 verdict + Gap 3 Modern Hopfield land + Gap 4 TWO_TIER land. Total Phase-1 ingest program: Cell 1 + Cell 3 + Cell 4 = ~6-8 CPU-hr at full; can ship in one cycle if Gap 3/4 results don't change the bands.

---

## SECTION 8: Substrate-product story consolidation

**If Phase-1 lands chain-grade (Cells 1-4):**
- Substrate is **a glass-box LM at vocabulary scale 8192** with substrate-native encoding (zero LLM at inference, zero LLM at ingest, full audit trail per token)
- The bigram-gap-closure signal that n1_v3 demonstrated on Wikipedia/Pythia is reproduced on text8/Path-C-substrate-native
- Stage 4 LM-equivalence path opens: substrate can be a drop-in autoregressive generator for downstream tasks (per [[project-path-c-substrate-owned-encoder-is-the-answer]])
- Can compose with math ingest (ProofWiki / Coq library cells already drafted; routing notes 2026-06-13 list) and science ingest for multi-domain substrate-product

**Substrate-product narrative:**
> "The substrate is the LM. There is no separate language model. The substrate's HD codebook IS the embedding table; the substrate's S matrix IS the next-token distribution; the substrate's Codebook cleanup IS the decoder; the substrate's refuse-gate IS the calibrated confidence. Every token in every generation is auditable from input to output through the same primitives that validate every cert-grade atom in the Store."

**Substrate-product cap_map implications (annotation candidates):**
- PP-X NEW: "Substrate-native text8 LM" at YELLOW band 0.55-0.65 EXPLORATORY pending Cell 1 outcome
- PP-Y NEW: "Glass-box LM with refuse-gate" at YELLOW band 0.50-0.60 EXPLORATORY pending Cell 4 outcome
- PP-Z NEW: "Continual multi-corpus language ingest" at FUSCHIA design-only pending Cell 5 + Gap 4

**Gating reality check:**
Per [[feedback-capability-dev-is-goal-cert-grade-is-instrument]]: capability development is the goal; cert-grade is the instrument. Even if Phase-1 cells land MIDDLE_BAND not chain-grade, the substrate-product narrative ADVANCES because the pipeline is composable AND auditable. The substrate-product is the **glass-box property** + **substrate-native composition**, not specifically the BPC number. n1_v3 carried this lesson: HARD_FAIL on BPC but CG on top1 with metric_scope clause. Expect Phase-1 to need similar honest-scope handling.

---

## CROSS-THREAD SYNTHESIS

This drill 3 of 3 synthesizes with:

**Drill 1 equivalent (lit-survey-style):** prior research_drill_substrate_only_language_model_5x_2026-06-08 + research_drill_substrate_direct_generative_language_modeling_3x_2026-06-04 -- those drilled WHETHER substrate-only LM is theoretically possible (yes, Plate 1995 + Eliasmith 2003 + Kanerva 2009 all establish HRR is Turing-complete; Kleyko 2022 surveys VSA LMs). This drill takes that for granted and goes to assembly.

**Drill 2 equivalent (composition-survey):** prior research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23 (hub-spoke 4-encoder federation; recommended S1 atom-encoder shipped first). This drill is COMPATIBLE with the hub-spoke architecture -- Section 7 Cell 1 IS the S1-equivalent for language modality.

**Drill 3 (THIS): operational assembly.** Closes the trio with executable pipeline + chain-grade primitive backing + 3 NEW infrastructure pieces.

**Cross-thread convergence:**
- All 3 drills converge on **char_trigram_encoder OR deterministic-hash bipolar as the input layer** (Path C)
- All 3 converge on **HRR FFT binding as the n-gram layer**
- All 3 converge on **SequenceMatrix S as the next-token layer**
- All 3 converge on **codebook + Modern Hopfield (Gap 3 in flight) as the cleanup layer**
- All 3 converge on **refuse-gate as the calibration layer**

The composition was always there; this drill formalized the assembly.

**Adjacency triggered (per Trigger C):**
New adjacency between Gap 3 (Modern Hopfield) and language ingest (n-gram depth extension). Should queue a follow-up drill comparing Modern Hopfield basin-sharpening on LM next-token cleanup vs vanilla cosine-floor cleanup -- but this is already what Section 7 Cell 2 tests; no separate research drill needed.

**Adjacency NOT triggered:** none. This drill consolidates rather than expanding.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Glass-box LM is buildable in 1-2 weeks** of cell-author time at Phase-1 scope (Cells 1+3+4). The 8-primitive backbone exists today.
2. **Substrate-native ingest is corpus-portable**: text8 -> wikitext -> arxiv -> ProofWiki -> Coq library all use the same pipeline; only the tokenization and partition routing change.
3. **Multi-domain substrate-product**: language + math + science ingest compose because they share the S/W/E/R triad architecture. Math ingest already drafted (cells 7/8 ProofWiki/Coq from 2026-06-13).
4. **Stage 4 LM-equivalence is the unlock**: if Phase-1 chain-grades, substrate IS a viable replacement for small LM components in product stack -- not via LLM API, via substrate-native autoregressive generation.
5. **The cert architecture extends naturally**: every ingest event is an atom; every generation event has provenance; the W/S/E/R partitions hold the language atoms. Per-token audit is per-atom audit.

---

## CITATIONS (verified count: 9 substrate-internal; 5 external)

**Substrate-internal (read for this drill, verified line/file existence):**
1. hdlab/char_trigram_encoder.py (lines 38-132; CharTrigramEncoder + _bipolar_hv + _seed_for_trigram)
2. hdlab/sequence_memory.py (lines 31-115; SequenceMatrix + bind_pair + bind_sequence + predict_next)
3. hdlab/generation.py (lines 51-138; SubstrateGenerator + generate_step + generate)
4. hdlab/binding.py (lines 12-46; bind + unbind)
5. hdlab/bundling.py (lines 12-50; bundle)
6. hdlab/memory.py (lines 31-77; Codebook + cosine-floor bound docstring)
7. hdlab/refuse_gate.py (lines 32-131; calibrate_refuse_threshold + V_REL=256 envelope)
8. hdlab/continual.py (lines 32-147; replay_cycle + nrem_replay_decorator + +0.57 drift_reduction)
9. hdlab/multi_hop.py (lines 36-189; naive_chain + partition_routed_chain)

**External (referenced for theoretical bounds):**
1. Plate 1995 -- HRR capacity bound N/(4 ln M); pp. 623-641 IEEE Trans. NN.
2. Kanerva 2009 -- Hyperdimensional computing; Cognitive Computation 1(2):139-159.
3. Eliasmith 2003 -- HRR / NEF for cognitive modeling.
4. Kleyko 2022 -- A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures; ACM Computing Surveys 55(6:1-40).
5. Ramsauer 2021 -- Hopfield Networks is All You Need; ICLR 2021 (basin-sharpening attractor reference for Cell 2).

**Non-verified (cited from MEMORY but not re-checked this cycle):**
- 2026-06-23 META_HARNESS_RIGGED audit ledger row 698
- n1_v3 cert ledger row 699 (top1=0.4455 chain-grade)
- c3 chain-grade verdict for sequence_memory primitive (commit a27939c5)
- g1 MEASURED_MECHANISM for generation primitive (commit 7083c38b)
