# Research R5 — Corpus-C design for multi-task continual learning (Bet B)

**Topic.** Strategy's Bet B (Tier-1 KILLER, ⚪): train substrate on Corpus A,
then Phase-B established shift, then a *genuinely different* domain C
(e.g., code, hex, non-Latin). Retention ≥ 80% of single-task baseline on
each held-out task after C-phase. R5 asks: what is the right Corpus C — by
what selection criterion, with what measurement protocol, and with what
falsifiable prediction?

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real external
literature scan** (general-purpose subagent, generic-math queries, no
substrate fingerprint) — this is the first cycle where Pass 1 followed the
charter's "broad literature scan" instruction rather than prior-knowledge
synthesis. Pass 2 drills substrate-specific choices.

---

## Pass 1 — External literature scan (verified)

Generic-math queries via Agent subagent: "continual learning benchmark
corpus selection distribution shift," "byte-level language modeling domain
shift KL divergence," "catastrophic forgetting task-incremental evaluation
protocol," "rehearsal replay continual learning baseline," etc. No
substrate fingerprint.

### 1.1 What the 2024–2026 continual-learning literature says

**Standard recipe (Ibrahim et al. 2024, arXiv:2403.08763).** Canonical CPT
(continual pretraining) protocol: learning-rate re-warm + re-decay + 5–25%
replay of pretraining tokens. Demonstrated to *match* full re-training-
from-scratch on English → German and English → English-but-different.
This is the published baseline any substrate-CL claim has to beat.

**The community survey of record** (Shi et al., CSUR 2025,
arXiv:2404.16789) categorizes CL benchmarks by *what content* is added
(domain shift / skill shift / alignment shift), NOT by a distribution-
shift-magnitude axis. The survey explicitly flags that **there is no
community consensus on a single "how different is corpus B from corpus A"
number** — papers report shift magnitude post hoc via loss curves and
backward transfer, not as a pre-screen criterion.

**Replay buffer scaling (2025):**
- "Replay to Remember" (arXiv:2504.17780): 1–2% buffer suffices for NLU;
  5–10% needed for code/math; quantized models tolerate smaller buffers.
- SuRe (Hazard et al. Nov 2025, arXiv:2511.22367): surprise-driven
  prioritized replay + dual-LoRA EMA gives +5 accuracy points on
  Lifelong-NLP-Tasks vs prior SOTA; robust at reduced buffer.
- "Scalable Strategies for Continual Learning with Replay"
  (arXiv:2505.12512): well-tuned replay beats most of the "complex" CL
  methods literature. Honest read: replay is the strong baseline.

**Spurious forgetting (Zheng et al., arXiv:2501.13453).** Many reported
"forgetting" results turn out to be task-alignment loss rather than
knowledge loss — replay does not address this failure mode. Means: when
the substrate's BWT looks bad on Corpus C, distinguish "knowledge
forgotten" from "task alignment broken" before concluding.

**Byte-level multi-domain CL has no dedicated benchmark in 2024–2026.**
This is the gap the lit scan made most clear. ByT5 (arXiv:2105.13626)
and Byte Latent Transformer (Pagnoni et al. arXiv:2412.09871) are byte-
level *base* models, not CL benchmarks. CODETASK-CL (arXiv:2307.02435)
is the closest dedicated CL evaluation but is token-level. **All published
CL-with-corpus-C results are at token/subword granularity**; mapping
token-level findings to byte-level requires care.

### 1.2 Information-overlap measures for characterizing A vs B vs C

The corpus-linguistics literature has stronger methodology here than the
ML/CL literature does, and there is poor cross-talk between the two.

**Frequency-based corpus distance:**
- **Li & Dunn 2022 (arXiv:2206.04332)** — the strongest empirical claim
  in this literature. **χ² over n-gram frequencies** outperforms model-
  based measures on register-prediction across 39 languages. Robust,
  cheap, language-agnostic.
- **Extended Jensen-Shannon divergence for multiple corpora** (Lu, CEUR
  Vol-2086 2017): pairwise + multi-way JSD over unigrams and bigrams.
  Bounded in [0, log 2], smoothed; better-behaved than raw KL for
  empirical estimates from finite samples.
- **Rényi-family generalized entropies** (Gerlach et al.,
  arXiv:1611.03596): tunable head-vs-tail weighting for similarity.

**Learned-feature-space:**
- **Achille et al. ICML 2021 (arXiv:2011.00613)** — Fisher-Rao distance
  on the space of tasks. Computed from learned features; *predictive* of
  whether transfer will help or hurt. The single best-validated "task
  similarity" measure in 2021–2025.
- "Quantifying Dataset Similarity to Guide Transfer Learning"
  (arXiv:2510.10866, 2025): newer, more accessible CLS-style predictor.

**Perplexity-gap as distance:**
- Thrush et al. 2024 (arXiv:2409.05816): perplexity gap is a sufficient
  signal for data-selection decisions.
- "Perplexity-Aware Data Scaling Law" (arXiv:2512.21515): perplexity
  landscapes predict CPT performance directly.
- **Paloma** (Magnusson et al. NeurIPS 2024 D&B, arXiv:2312.10523): 546
  stratified domains, per-domain perplexity varies by **2–8 bits-per-byte**
  for a single base model. Closest existing "corpus-distance" benchmark;
  but Paloma uses domain perplexity post hoc, not as a screen.

**Honest read.** No paper draws a single canonical "corpus-distance
number" for byte-level CL. The defensible move per the lit scan is to
**report multiple coordinates** (byte-unigram JSD + byte-bigram JSD +
bits-per-byte gap + optional Fisher-Rao on learned features) and treat
the corpus pair's position in that multi-axis space as the
characterization, not as a single scalar.

### 1.3 Specific Corpus-C candidates with published CL evaluation status

The lit scan surfaced these byte-distribution properties for common
candidate domains:

| Candidate C | Byte distribution | Published byte-level CL evaluation? |
|---|---|---|
| **Code (Python / C / JS)** | Heavy structure; punctuation-rich; high indentation. ~5–10 BPB for general LM (Paloma) | CODETASK-CL (arXiv:2307.02435) is dedicated CL benchmark, but token-level. No dedicated byte-level CL benchmark. |
| **Hex / binary-encoded data** | Bytes restricted to {0-9, a-f, newline} for hex; full byte range for raw binary. KL > 1.5 from English. | **NO published byte-level CL benchmark.** Real opportunity. |
| **Non-Latin UTF-8 scripts** (Chinese, Arabic, Devanagari) | Constrained to high-bit byte ranges (0xE0–0xEF for 3-byte UTF-8 CJK). Per-byte entropy LOWER than ASCII because the high-bit bytes are script-locked. | Gogoulou et al. 2024 (arXiv:2311.01200) covers Nordic languages (still mostly Latin1); no published CL eval for byte-disjoint scripts. |
| **Structured data (JSON / XML / YAML)** | Heavy structural tokens (`{`, `}`, `:`, `,`, `"`); very low byte-entropy. | No dedicated CL benchmark. |
| **Domain-specific text (legal / medical / scientific)** | Vocabulary shift; byte distribution similar to general prose. | Heavily benchmarked at token level (BioMedLM, Law-LM lineage). |

**Implicit "hardness" ordering by published BWT damage** (lit scan
inference): code > non-Latin script > domain-specific text. Code is the
canonical "stress test" because byte distribution differs maximally from
prose while remaining legitimate-natural-distribution data.

### 1.4 The replay-helps envelope — what the literature does NOT say

The single most important finding from the lit scan: **no published paper
characterizes the replay-helps envelope as an explicit function of
distribution-shift magnitude.** The D-CPT scaling laws (arXiv:2505.07796)
and Perplexity-Aware Scaling Law (arXiv:2512.21515) come closest — they
predict the *shape* of the CPT loss curve as a function of distribution
gap — but neither paper names the failure boundary where replay stops
helping.

This is a genuine open question in the published 2024–2026 literature.
The substrate's R5/Bet B test, if framed properly, could be the first
characterization. **That changes the framing of the experiment from "does
the substrate's CL work?" to "where does replay-based CL break in
distribution-shift magnitude, and is the substrate's break-point earlier
or later than transformer baselines?"**

Replay failure modes the literature DOES document:
- **Buffer < 1%** for hard domains (code/math) — Replay to Remember 2025.
- **Byte-disjoint shifts** where unigram overlap is near-zero (e.g.,
  Latin → CJK) — multilingual CPT (arXiv:2504.04152).
- **Spurious-forgetting cases** where the failure is task-alignment loss,
  not knowledge loss (Zheng et al. 2025) — replay doesn't help here at all.

---

## Pass 2 — Substrate-specific drill: what Corpus C tests Bet B properly?

The substrate's predicted CL mechanism (per `wave14c_random_replay_mechanism_research.md`
and `wave14d_multi_task_cl_research.md`): random replay during Phase B
training projects the Phase-B W-delta onto the row-space of the Phase-A
pool. The +0.66–0.73 BWT result is the substrate "rehearsing" the
bigram structure that Phase B's training overwrote.

This mechanism predicts a sharp envelope across distribution-shift
magnitude:

- **At small unigram-KL shift** (e.g., shuffle(A), English → English-MD):
  substrate's pool covers most of B's bigrams; replay restoration is
  near-complete. Predicted BWT > 0.5.
- **At medium unigram-KL shift** (e.g., English → Python source, KL ≈
  0.15–0.3): partial bigram overlap (both share ASCII; both have
  word-like structures); replay restores partial Phase-A bigrams but
  cannot help Phase-B Python-specific tokens. Predicted BWT ≈ 0.2–0.4.
- **At large unigram-KL shift** (e.g., English → hex, KL ≈ 1.5–2.5):
  almost no bigram overlap; pool's stored A-bigrams are useless on
  B-corpus queries. Predicted BWT ≈ 0–0.1.

For the substrate's Tier-1 KILLER "multi-task CL works at production
scale" claim to be defensible, **C must be a domain where the substrate's
predicted BWT is BOTH positive AND non-trivial** — i.e., medium-shift,
not small (where everything works) and not large (where nothing works).

### 2.1 The three viable Corpus-C candidates

After the lit scan and the substrate mechanism analysis, three candidates
survive:

**Candidate C1: Python source code (standard "hard but realistic" choice)**

- **Distribution shift from English prose**: byte-unigram KL ≈ 0.15–0.3
  per Paloma + prior survey. Bigram KL ≈ 0.8–1.2.
- **Published baseline**: CODETASK-CL (token-level) exists; Paloma
  includes GitHub split; Ibrahim et al. 2024 implicitly tested
  English → German which is similar magnitude.
- **Why this is the right primary C**:
  - It is the canonical published stress-test for CL — comparable
    numbers exist for transformer baselines.
  - Substrate-mechanism prediction is informative: bigram overlap is
    partial (both share ASCII space, both use word-like structures),
    so substrate's replay restoration should be partial but non-zero.
  - Predicted BWT in the 0.2–0.4 range is exactly the "non-trivial,
    not certain to win" zone where the experiment is decisive.
- **Risks**:
  - Code's structured nature (heavy indentation, repeated bigrams like
    `\n   `, `def `, `()`) may give the substrate an *unfair* advantage
    because the pool stores high-frequency bigrams well.
  - Token-level CL baselines may not map 1:1 to byte-level.

**Candidate C2: Hex-encoded binary data (substrate-novel stress test)**

- **Distribution shift from English prose**: byte-unigram KL ≈ 1.5–2.5
  (extreme: bytes restricted to {0-9, a-f, newline}). Bigram KL ≈ 3–4.
- **Published baseline**: **NONE.** This would be a substrate-novel
  benchmark — no byte-level CL paper has tested hex/binary as Corpus C.
- **Why interesting**:
  - Tests the substrate's CL mechanism at the disjoint-byte-set edge,
    where the lit scan predicts replay should fail.
  - If the substrate's predicted-failure-at-large-shift holds, this is
    a defensible kill-line: "substrate CL works through unigram-KL ≈ X,
    fails beyond."
  - Substrate-unique contribution to the literature (the lit scan
    confirms this is unbenchmarked).
- **Risks**:
  - High likelihood of "trivially-hard" outcome (BWT ≈ 0) → not
    informative about the substrate's positive capabilities.
  - Hex distribution is somewhat artificial (lab data, not user-facing).
    Critics may argue it's not a realistic test.

**Candidate C3: Non-Latin UTF-8 (CJK) — Japanese hiragana or Mandarin Chinese**

- **Distribution shift from English prose**: byte-unigram KL ≈ 2–3 (CJK
  uses 3–4 byte UTF-8 encoding, distinct byte range). Bigram KL ≈ 4–5.
- **Published baseline**: Gogoulou et al. 2024 (Nordic) is closest but
  uses Latin-1 throughout. No published CL eval for byte-disjoint
  scripts. Closer to substrate-novel than C1.
- **Why interesting**:
  - The byte distribution is structured (high-bit bytes only) but
    distinct from English. Tests substrate's response to "different but
    not random" byte distribution.
  - More realistic than hex; users actually deploy multilingual systems.
- **Risks**:
  - Substrate's pool is byte-K-grams, not character-K-grams. UTF-8 byte-
    bigrams in CJK don't form natural "linguistic" units; substrate may
    not extract useful structure.
  - Predicted BWT may be similar to C2 (near-zero) if byte-disjointness
    dominates over byte-structure.

### 2.2 Recommended primary + parallel design

**Primary C: Python source code (Candidate C1).**

Reasoning: it is the only candidate that the lit scan confirms has
published transformer baselines for direct comparison, AND it falls in
the substrate's predicted "non-trivial, non-certain" BWT range. The
positive outcome (BWT in 0.2–0.4 range) would be a real Tier-1 KILLER
unlock; the negative outcome (BWT near zero) would still be informative
because we can compare to published transformer numbers.

**Parallel C: Hex-encoded binary data (Candidate C2).**

Reasoning: substrate-novel stress test at the disjoint-byte-set edge.
Cheap to run alongside C1 (smaller distinct-byte vocabulary, faster
training). If the predicted "substrate CL fails at large unigram-KL"
holds, C2 provides the kill-line; if substrate surprisingly succeeds
on C2, that's a strong substrate-unique capability claim.

**Deferred C: Non-Latin UTF-8 (Candidate C3).**

Reasoning: substrate-mechanism prediction is too uncertain (byte-
structure vs byte-disjointness tradeoff is unclear). Reopen if C1 and
C2 produce surprising results that motivate the test.

### 2.3 Information-content matching protocol — the multi-axis report

Per the lit scan's "no single corpus-distance number" finding, the
substrate's Bet B experiment must report **multiple coordinates**:

1. **Byte-unigram JSD** A↔B, A↔C, B↔C (cheapest screen).
2. **Byte-bigram JSD** for the same three pairs (catches code vs prose).
3. **Bits-per-byte gap**: BPB(W_A, corpus_X) − BPB(W_A, corpus_A) for
   X ∈ {B, C} (Paloma/Thrush-style knowledge-gap signal). Computed
   *before* Phase B training.
4. **Fisher-Rao on pool feature space** (Achille et al.) — pool entries
   from A vs B vs C, Fisher-Rao distance between empirical feature
   distributions. Optional but strongest predictor per literature.

Report all four; do not collapse to one number. This is the substrate's
contribution to the methodology gap the lit scan identified.

---

## Specific experimental design (pseudocode)

**Experiment(s)**: `wave14b_multitask_cl_v1_C_python` (primary) and
`wave14b_multitask_cl_v1_C_hex` (parallel stress test). Pre-registered at
`preregs/2026-05-21_wave14b_multitask_cl_v1.md` (Experiment Dev to
author). Multi-probe by construction.

```text
config:
  N = 4096
  K = 32  # match current R10 best-config K used in Phase B baselines
  pool_size = 4096
  seeds = [7, 17, 23, 31, 41]  # 5-seed standard
  M_replay_fraction = 0.10  # Ibrahim 2024 canonical recipe (10% replay)

corpus_setup:
  corpus_A = English wiki (current substrate base corpus)
  corpus_B = Phase-B established shift (current Phase-B corpus)
  corpus_C_primary = Python source code from CodeParrot or
                     The-Stack-dedup (license: permissive)
  corpus_C_stress = hex-encoded random binary
                    (uniform bytes mapped to ASCII hex digits)

  # Information-content matching: same total bytes across corpora
  bytes_per_corpus = 50_000_000  # 50 MB; tunable for compute budget

phase_protocol (per seed):
  # Phase A: substrate trains on corpus_A from scratch
  W_A, pool_A = substrate_train(corpus_A, init=zeros)

  # Information-overlap measurement (BEFORE Phase B)
  bpb_A_on_A = bpb(W_A, corpus_A)  # baseline
  bpb_A_on_B = bpb(W_A, corpus_B)  # measure shift magnitude
  bpb_A_on_C = bpb(W_A, corpus_C)  # measure shift magnitude
  unigram_jsd_AB, unigram_jsd_AC = compute_byte_unigram_jsd(...)
  bigram_jsd_AB, bigram_jsd_AC = compute_byte_bigram_jsd(...)
  # optional: fisher_rao on pool features (cheap probe)

  # Phase B: substrate trains on corpus_B with 10% replay of A
  W_AB, pool_AB = substrate_train(
    corpus_B,
    init=(W_A, pool_A),
    replay_fraction=0.10,
    replay_source=corpus_A
  )

  # Phase C: substrate trains on corpus_C with 10% replay of A+B (5%+5%)
  W_ABC, pool_ABC = substrate_train(
    corpus_C,
    init=(W_AB, pool_AB),
    replay_fraction=0.10,  # split equally between A and B sources
    replay_source=mix(corpus_A, corpus_B)
  )

multi_probe_battery:
  # Per active_priorities Bet B criteria (substrate-internal, calibrated
  # against Ibrahim et al. 2024's "match-from-scratch" benchmark)

  # 1. Phase-A held-out bpc retention
  bpc_A_held_out_after_C = bpb(W_ABC, holdout_A)
  bpc_A_baseline = bpb(W_A, holdout_A)
  retention_A = bpc_A_baseline / bpc_A_held_out_after_C  # ratio, lower better
  # Target: retention_A >= 0.80 (i.e., bpc no more than 25% worse than baseline)

  # 2. Phase-B held-out bpc retention
  retention_B = bpc_B_baseline / bpb(W_ABC, holdout_B)
  # Target: retention_B >= 0.80

  # 3. Phase-C learn-curve: positive bpc gain vs untrained
  gain_C = bpb(W_zero, holdout_C) - bpb(W_ABC, holdout_C)
  # Target: gain_C > 0 (substrate learned SOMETHING about C)

  # 4. BWT (Hupkes et al. continual-learning convention)
  bwt = mean([
    bpb(W_ABC, holdout_A) - bpb(W_AB, holdout_A),  # how much A degraded post-C
    bpb(W_ABC, holdout_B) - bpb(W_B, holdout_B),   # how much B degraded post-C
  ])
  # Target: bwt >= 0 (no catastrophic forgetting; ideally close to zero
  # or slightly negative meaning IMPROVEMENT)

  # 5. Spurious-forgetting probe (per Zheng et al. 2025)
  # Distinguish knowledge loss from task-alignment loss
  spurious_check = pool_retrieval_intact(pool_ABC, A_facts) AND
                   pool_retrieval_intact(pool_ABC, B_facts)
  # Target: if retention metrics fail, spurious_check should PASS,
  # indicating the failure is mechanism-level (replay didn't work)
  # not surface-task-level

verdict_logic:
  PASS iff (all required):
    retention_A >= 0.80 AND retention_B >= 0.80 AND gain_C > 0
    AND bwt >= 0  (no catastrophic forgetting)
    AND multi-seed (3 of 5 seeds pass; 5 of 5 ideal)

  PARTIAL iff:
    retention_A >= 0.80 AND retention_B in [0.50, 0.80] AND gain_C > 0
    (substrate partially retains B; product-relevant)

  KILL iff:
    Either retention < 0.50 across 3 seeds
```

**Smoke test (queue_add gate)**: N=512, M=200, K=8, bytes_per_corpus=1MB,
seeds=[7]. Target runtime ~30s. Pre-registered oracle assertions: bpc
gain_C > 0 even at smoke scale (the substrate should learn SOMETHING
about C in 1MB).

**Self-test**: 4 synthetic cases:
- All-three-corpora-identical (A=B=C=English): predict retention_A
  ≈ retention_B ≈ 1.0; gain_C close to baseline; BWT ≈ 0. (Trivial
  positive control.)
- Phase-C = random bytes (no learnable structure): predict
  retention_A, retention_B unaffected; gain_C ≈ 0. Replay protects A/B
  even with useless C.
- Phase-C = shuffle of A (no new content): predict same as identical
  case; trivial.
- Phase-C = corpus with disjoint byte set (e.g., only bytes 200-255):
  predict retention_A and retention_B preserved if replay is well-tuned;
  gain_C measures whether substrate learns the new byte set.

**Wall budget**: 50MB × 3 corpora × 5 seeds × 2 candidates (C_python + C_hex)
= ~750MB total training data; ~2 GPU hours total at full scale. Smoke ~30s
per variant.

---

## Materials analog (load-bearing)

The substrate's predicted CL mechanism — replay restores the bigram
joint via subspace projection of W-delta onto Phase-A pool row-space —
has a direct condensed-matter analog: **paramagnetic-to-ferromagnetic
phase transition under external field**.

**The analog.** In a spin-glass system (Sherrington-Kirkpatrick), random
disorder dominates and there is no long-range order. Apply an external
ordering field (e.g., a global magnetic field favoring one direction):
the system either aligns with the field (paramagnetic → ferromagnetic
transition) or remains frustrated, depending on the disorder strength
vs field strength.

The substrate's Phase-B training is exactly the "external field" on the
A-trained substrate. The field magnitude is set by the unigram/bigram
distribution shift; the existing order (A's stored bigrams) is the
substrate's internal disorder. Three regimes correspond to three CL
outcomes:

- **Small shift (small field)**: A's internal order dominates; B's
  training perturbs minimally; substrate retains A's structure
  (paramagnetic-stable analog). Predicted BWT > 0.5.
- **Medium shift (intermediate field)**: A's bigrams and B's bigrams
  *coexist* — substrate sits in a multi-stable regime where pool
  retrieval favors A-bigrams but W has been updated for B. This is
  exactly the **glass phase with two coexisting ordered states**, where
  replay's role is to keep the A-order from being annihilated by the
  field. Predicted BWT in 0.2–0.4 range.
- **Large shift (strong field)**: B's bigrams overwhelm A's; substrate
  cannot retain both. Replay's projection onto the A-pool row-space
  approaches zero because the A and B row-spaces are nearly disjoint.
  Predicted BWT ≈ 0 (ferromagnetic alignment with B; A forgotten).

This maps cleanly to the **AT line in spin-glass theory**
(de Almeida-Thouless 1978): the boundary in field-strength × temperature
space where replica symmetry breaks. The substrate's CL transition
should occur at an analogous boundary in **distribution-shift-magnitude
× replay-fraction** space.

**Predictive consequence.** Per the AT-line analogy, the substrate's
"replay envelope" should be a **smooth phase boundary**, not a sharp
cliff. The 5-seed sweep across A→B→C with varying C corpora should map
out this boundary — the substrate's contribution to the "replay-helps
envelope" gap the lit scan identified.

This is the materials reason for why the multi-axis distance reporting
matters: the spin-glass phase boundary is multi-dimensional (field
strength + temperature + disorder strength), so a single scalar
"corpus distance" cannot characterize it. Reporting JSD-unigram +
JSD-bigram + BPB-gap + Fisher-Rao gives the substrate a 4-coordinate
map of the phase boundary — the right object to compare against the
published transformer baselines.

---

## Falsifiable prediction

**Primary prediction (C_python, Candidate C1):**

At N=4096, K=32, M_replay_fraction=0.10, corpus sizes 50MB each, 5 seeds:

- byte_unigram_JSD(A, C_python) ∈ [0.15, 0.30] (measured pre-training).
- byte_bigram_JSD(A, C_python) ∈ [0.8, 1.2].
- bpb_gap(W_A, corpus_C_python) ∈ [3, 6] (pre-Phase-C bits-per-byte gap).
- **retention_A ≥ 0.85** post-Phase-C (5-seed mean).
- **retention_B ≥ 0.80** post-Phase-C.
- **gain_C ≥ 0.5 bpb** (substrate learns Python's main structure).
- **BWT ∈ [-0.05, +0.10]** (no catastrophic forgetting; possibly small
  improvement from Phase-C bigram regularization).

**Stress prediction (C_hex, Candidate C2):**

- byte_unigram_JSD(A, C_hex) ∈ [1.5, 2.5].
- **retention_A ≥ 0.90** post-Phase-C (replay protects A).
- **retention_B ≥ 0.85** post-Phase-C.
- **gain_C in [0.1, 0.5]** (substrate learns the constrained hex byte
  set but cannot recover meaningful structure beyond marginal).
- **BWT ∈ [-0.10, +0.05]** (replay holds A/B; Phase-C contributes
  minimal damage because the disjoint byte set has near-zero interaction
  with stored A/B bigrams).

**Kill criterion (closes Bet B at ❌ in current architecture).**

If retention_A < 0.50 OR retention_B < 0.50 in C_python, with 3 of 5
seeds, AND the spurious_forgetting probe fails (i.e., pool retrieval is
also degraded — actual knowledge loss, not task-alignment loss), then
the substrate's CL story does not extend beyond same-distribution shifts.
The Tier-1 KILLER claim "true continual learning at production scale"
moves to ❌ pending a substrate redesign.

If retention_A or retention_B fails but spurious_forgetting probe shows
the pool is INTACT, the failure is in the substrate's readout / W-side
mechanism, not in the storage. That's a different (and more tractable)
fix path — would warrant a R10 (substrate readout) research note rather
than closing Bet B.

**Falsifier for the substrate-uniqueness claim.**

If retention_A and retention_B both pass at C_python with the canonical
Ibrahim 2024 recipe (LR-warmup + decay + 10% replay), but a transformer
baseline run with the same recipe ALSO achieves retention ≥ 80%, then
the substrate's CL is not substrate-*unique* — it's the well-tuned
replay recipe doing the work. The substrate-unique claim requires either
(a) higher retention than transformer at the same recipe, or (b)
retention at lower replay fraction than transformer needs, or (c)
positive retention at distribution-shift magnitudes where transformer
catastrophically forgets. The experiment should report all three
substrate-vs-transformer comparisons explicitly.

---

## Citations

1. **Ibrahim et al. (2024). "Simple and Scalable Strategies to
   Continually Pre-train Large Language Models."** arXiv:2403.08763.
   — Canonical CPT recipe (LR re-warm + decay + 5–25% replay).
   Demonstrated to match retraining-from-scratch; the substrate must
   compare against this baseline.

2. **Shi et al. (2025). "Continual Learning of Large Language Models:
   A Comprehensive Survey."** ACM Comput. Surv. arXiv:2404.16789.
   — Survey of record for 2024–2026 CL. Notes the lack of community
   consensus on a distribution-shift-magnitude axis.

3. **Magnusson et al. (2024). "Paloma: A Benchmark for Evaluating
   Language Model Fit."** NeurIPS 2024 D&B, arXiv:2312.10523.
   — 546 stratified domains with per-domain BPB. Closest existing
   "corpus-distance" benchmark; supports the multi-axis reporting
   recommendation.

4. **Li & Dunn (2022). "Corpus Similarity Measures Remain Robust
   Across Diverse Languages."** arXiv:2206.04332.
   — χ² over n-gram frequencies; the strongest empirical corpus-
   distance measure across 39 languages. Source for the byte-bigram
   distance methodology.

5. **Gogoulou et al. (2024). "Continual Learning Under Language Shift:
   Order Matters for Language Models."** TSD 2024, arXiv:2311.01200.
   — Nordic language CL; cleanest published "order matters" finding.
   Provides the closest comparable transformer baseline for
   distribution-shift-magnitude CL.

6. **Achille et al. (2021). "An Information-Geometric Distance on the
   Space of Tasks."** ICML 2021, arXiv:2011.00613.
   — Fisher-Rao distance for task similarity. The most-predictive
   single learned-feature-space measure in 2021–2025; provides the
   optional 4th coordinate in the multi-axis reporting recommendation.

7. **Zheng et al. (2025). "Spurious Forgetting in Continual Learning
   of Language Models."** arXiv:2501.13453.
   — Distinguishes knowledge loss from task-alignment loss. Critical
   for the substrate's "spurious_forgetting probe" in the verdict
   logic; ensures we measure the right failure mode.

8. **Hazard et al. (Nov 2025). "SuRe: Surprise-Driven Prioritised
   Replay for Continual LLM Learning."** arXiv:2511.22367.
   — Current SOTA on prioritized replay. If the substrate's vanilla
   10% replay underperforms expectations, SuRe is the next variant to
   port.

9. **Thrush et al. (2024). "Improving Pretraining Data Using Perplexity
   Correlations."** arXiv:2409.05816.
   — Perplexity gap as data-selection signal. Justifies the bpb_gap
   coordinate in the multi-axis reporting.

10. **de Almeida, Thouless (1978). "Stability of the
    Sherrington-Kirkpatrick solution of a spin glass model."** J. Phys. A
    11, 983. (No arXiv — classical foundation.)
    — Materials-science anchor for the AT-line analogy to the substrate's
    replay envelope.

---

## Routing

- **Experiment Dev (E_B)**: this note recommends TWO experiments:
  - `wave14b_multitask_cl_v1_C_python` (primary, Candidate C1)
  - `wave14b_multitask_cl_v1_C_hex` (parallel stress test, Candidate C2)
  Both share the multi-probe battery + spurious_forgetting probe. Total
  ~2 GPU hours at full scale. Smoke ~30s per variant.

- **Strategy**: this note proposes (a) Bet B receives a clean
  experimental design ready for Experiment Dev to build; (b) the cap_map
  receives a future row addition under "Continual learning" for the
  3-coordinate distance reporting methodology (substrate-novel
  contribution to the published-literature methodology gap the lit scan
  identified); (c) Bet B kill criterion now has both retention floor AND
  spurious-forgetting probe, which is more rigorous than the prior
  active_priorities framing. Strategy keeps writer exclusivity on the
  cap_map.

- **Research (this session, future cycles)**: if `wave14b_multitask_cl_v1_C_python`
  passes, no further R5 research needed; Strategy upgrades cap_map row
  and the Tier-1 KILLER claim moves from ⚪ to 🟢 partial. If retention_A
  or retention_B fails on C_python but spurious_forgetting probe shows
  pool intact, route to a new research question on substrate W-side
  readout mechanism (parallel to R1's W-side edit research). If both
  retention probes fail across 3 seeds AND spurious_forgetting also
  fails, the multi-task CL story closes ❌ in current architecture; the
  fallback would be designing a substrate variant with stronger
  inter-corpus interference protection (e.g., per-corpus W blocks, akin
  to Candidate 4 in R1).
