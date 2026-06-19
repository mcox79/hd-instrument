# Research -> Exp-Dev: EX-CONCEPT-1 rescue identified -- k=2 XOR context binding (retrieval-side only) + 2 novel write-rule directions

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~11:30
**Subject:** Write-rule rescue drill landed (Outcome B). LOAD-BEARING INSIGHT: write rule determines capacity QUALITY, not Markov CLASS; CONTEXT ENCODING determines Markov class. Three actionable rescues for EX-CONCEPT-1 sequence prediction.

---

## The reframe

Prior assumption: rescue substrate's bigram-level next-token prediction by changing the write rule.

Drill verdict: **The write rule does NOT determine Markov class. The CONTEXT ENCODING does.**

Algebraic proof: a single matrix-vector product W * phi(c_t) is a linear function of phi(c_t); it can only capture conditional expectation given the SINGLE most recent token (conditional-bigram class). To capture k-tuple context, the k-tuple must be encoded into a single vector BEFORE multiplication.

VSA XOR-binding does this naturally:

    context_k(t) = phi(c_{t-k+1}) XOR phi(c_{t-k+2}) XOR ... XOR phi(c_t)
    W += outer(context_k(t), phi(c_{t+1}))     (standard Hebbian on k-gram context)
    predict next: W * context_k(t)

This is k-th order Markov prediction with NO write rule change.

## Why our K=2/5/10 position-binding tests failed

We previously tested POSITION binding (each prior token bound to a position label, then summed). That has 1/K SNR penalty at small V_c due to flat-codebook crosstalk -- previous concept-vocabulary drill confirmed this.

XOR k-gram CONTEXT binding (no position labels; just consecutive XOR) has different SNR properties. Drill predicts HARD-PASS at 20-40% accuracy improvement over k=1 at M/N=0.05.

---

## Cell K2-XOR-1: k=2 XOR context binding empirical test (HIGHEST PRIORITY; cheapest decisive)

**Anchor:** `substrate_kgram_xor_context_binding_v1`

### Why this matters

This is the cheapest possible test of the rescue mechanism. Pure retrieval-side change. Zero write-cost overhead. Preserves ALL FOUR structural moats (cert, real-time write, TC0 retrieval, bipolar storage). If HP: substrate's sequence prediction is rescued to bigram-Markov class through simple context encoding.

### Architecture

- Synthetic Markov chain: V=256, M=400, N=4096, 3 seeds
- Compare two query strategies (write rule UNCHANGED -- standard Hebbian):
  - Variant K1: query = phi(c_t), standard substrate baseline
  - Variant K2: query = phi(c_{t-1}) XOR phi(c_t), k=2 XOR context binding
  - Variant K3: query = phi(c_{t-2}) XOR phi(c_{t-1}) XOR phi(c_t), k=3 XOR context binding
- Metric: next-token prediction accuracy on held-out 20% of sequence

### Pre-reg
- HP: accuracy(K2) >= 1.20 * accuracy(K1) at M/N=0.05 (20%+ improvement)
- MID: accuracy(K2) in [1.05, 1.20] * accuracy(K1) (modest improvement)
- HF: accuracy(K2) <= 1.02 * accuracy(K1) (no benefit -- substrate fundamentally at co-occurrence-bigram regardless of context encoding)

### Cost + wall
- $0 CPU
- ~30 seconds wall at N=4096
- 3 seeds

### Strategic

Resolves EX-CONCEPT-1 architectural question. If HP: substrate's sequence prediction has a clean retrieval-side rescue with all moats preserved. If HF: confirms Outcome C (substrate fundamentally at co-occurrence-bigram regardless of context encoding).

PROT-018: `_kgram_xor_context_binding_v1`
PROT-021: source=local CPU; n_seeds=3

---

## Cell THETA-BURST-1: Theta burst write (NOVEL; hippocampal-inspired)

**Anchor:** `substrate_theta_burst_multistep_write_v1`

### Why this matters

Hippocampal theta sequences (Sosa et al. Neuron 2024) compress a K-step forward sweep into each theta cycle. The write rule is multi-step lookahead: write not just (c_t, c_{t+1}) but also (c_t, c_{t+2}), ..., (c_t, c_{t+K}) with decaying weights.

This is NOT published in AI memory literature as a bipolar-compatible write rule. Drill identifies it as a novel direction.

### Architecture

- Same Markov chain setup as K2-XOR-1
- Write rule variants:
  - Baseline: W += outer(phi(c_t), phi(c_{t+1})) (standard Hebbian)
  - Theta-burst K=3: W += sum_{k=1..3} gamma^(k-1) * outer(phi(c_t), phi(c_{t+k})), gamma=0.7
  - Theta-burst K=5: W += sum_{k=1..5} gamma^(k-1) * outer(phi(c_t), phi(c_{t+k})), gamma=0.7
- Metric: multi-step prediction accuracy (predict c_{t+1}, c_{t+2}, c_{t+3})

### Pre-reg
- HP: theta-burst K=3 improves multi-step prediction (steps t+2, t+3) by >=15% over Hebbian; single-step (t+1) within 5%
- MID: modest improvement (~5-15%) on multi-step
- HF: theta-burst doesn't help OR degrades single-step prediction too much

### Cost + wall
- $0 CPU
- ~2-3 minutes wall (K times more write ops than baseline)
- 3 seeds

### Strategic

Tests whether neuroscience-inspired trajectory writes provide architectural value beyond k-gram context binding. If HP: substrate gains multi-step lookahead capability that complements k-gram context binding.

PROT-018: `_theta_burst_multistep_write_v1`
PROT-021: source=local CPU; n_seeds=3

---

## Cell CEREBELLAR-EXP-1: Cerebellar random-expansion write (NOVEL; capacity lift to O(N^2))

**Anchor:** `substrate_cerebellar_random_expansion_write_v1`

### Why this matters

Albus 1971 cerebellar model + recent cerebellar circuit lit identifies random projection (granule cell expansion) as the architectural step that lifts effective capacity. In bipolar substrate terms:

- Random projection: phi_exp = R * phi (where R is N x N^2 random bipolar)
- Write in expanded space: W_exp += outer(phi_exp(c_t), phi_exp(c_{t+1}))
- Retrieval: read = W_exp * phi_exp(c_t); decode via transpose projection

**Capacity lifts from O(N) to O(N^2) patterns at quadratic retrieval cost.**

For N=4096: N^2 = 16M weights = 16 MB bipolar (feasible). Phase 3 implication: this may provide an alternative to n=3 cubic-tensor-write for Wikipedia capacity scope.

### Architecture

- N=1024 (smaller substrate-class for cubic-cost test feasibility)
- N_exp = 16384 (= 16 * N)
- Random projection R fixed (Gaussian bipolar)
- Compare:
  - Baseline: standard Hebbian at N=1024, M_max ~ 142
  - Cerebellar: Hebbian in N_exp space; effective M_max = ?
- Metric: storage capacity (M where retrieval accuracy first drops below 0.95)

### Pre-reg
- HP: cerebellar variant achieves M >= 1000 patterns at >=0.95 retrieval (>=7x baseline N at N=1024)
- MID: cerebellar achieves M in [N, 1000]
- HF: cerebellar provides no capacity improvement OR breaks bipolar storage

### Cost + wall
- $0 CPU (N=1024 + 16x expansion is feasible)
- ~5-10 minutes wall
- 3 seeds

### Strategic

If HP: this is a MAJOR architectural finding. Lifts substrate capacity from O(N) to O(N^2) without requiring true cubic-tensor (which is infeasible at Phase 3 scale). Provides alternative path to Wikipedia capacity scope. Worth full validation if HP.

PROT-018: `_cerebellar_random_expansion_write_v1`
PROT-021: source=local CPU; n_seeds=3

---

## Sequencing recommendation

**Run in this order (cheapest decisive first):**

1. **K2-XOR-1** (~30s; ALL FOUR MOATS preserved; cleanest test)
2. **THETA-BURST-1** (~2-3 min; novel direction; preserves moats)
3. **CEREBELLAR-EXP-1** (~5-10 min; novel architecture; Phase 3 implication)

Total wall time for all three: ~15 minutes. Total cost: $0.

If K2-XOR-1 HP: substrate's sequence prediction has clean rescue mechanism; broader strategic story sharpens.

If THETA-BURST-1 HP: novel architectural direction confirmed; warrants Phase 3 consideration.

If CEREBELLAR-EXP-1 HP: substrate capacity ceiling can be lifted via random expansion; Phase 3 may not need cubic-tensor-write.

---

## Why this is the right test set

Per [[feedback-pressure-test-negative-findings]]: every "substrate cannot do X" claim treated as operating-mode-specific hypothesis; enumerate alternate modes before accepting. The EX-CONCEPT-1 HF was substrate-as-generative-LM. This drill enumerates rescue modes:

- Write rule rescues: PARTIAL (PC residual breaks cert moat or sacrifices convergence)
- Context encoding rescues: PROMISING (k=2 XOR binding preserves all moats)
- Novel write architectures: 2 unexplored directions (theta burst + cerebellar expansion)

Per [[feedback-rescue-sketch-first-sequencing]]: cheapest rescue first. K2-XOR-1 is the cheapest decisive test (~30s; zero write change).

---

## Updated narrative

The audacious vision is unchanged: substrate cognitive-core (memory + reasoning + audit) + LLM (decoder) hybrid. The 5/7 categorical wins + 1000-exchange + 1000-doc + reasoning-reframe HARD_PASSes are the load-bearing capability story.

EX-CONCEPT-1 sequence prediction was a side question (can substrate also be a competitive LM?). Honest answer: substrate is bigram-level at standard query, but k=2 XOR context binding LIKELY rescues to bigram-Markov class with all moats preserved.

The drill clarifies: the depth gap to neural-LM remains fundamental (substrate is single-pass retrieval; neural LMs have multi-layer composition). Substrate is NOT a neural-LM replacement at any rescue level. But k-gram XOR binding may rescue substrate sequence prediction enough for some hybrid use cases.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: 3 cells test distinct architectural hypotheses (context encoding rescue + novel write architectures)
- Per [[feedback-rescue-sketch-first-sequencing]]: cheapest decisive first
- Per [[feedback-pressure-test-negative-findings]]: enumerate rescue modes for EX-CONCEPT-1 HF
- ASCII-only

PROT-018: anchors per cell
PROT-021: source=local CPU; n_seeds=3

---

**END.**

**Exp-Dev:** 3 cells routed. K2-XOR-1 is HIGHEST PRIORITY (~30s wall; ALL FOUR MOATS preserved). Confirms or rejects clean retrieval-side rescue for substrate sequence prediction. If HP: EX-CONCEPT-1 architectural question resolved + new substrate-MAX variant added. If HF: confirms substrate fundamentally at co-occurrence-bigram regardless of context encoding (Outcome C). Total batch: ~15 minutes wall, $0 cost.

**Testbed:** no action; awaiting storage probe completion.

**User:** Write-rule rescue drill landed with surprising verdict: the rescue lever is RETRIEVAL-SIDE (k=2 XOR context binding), not write-side. Zero overhead; all moats preserved. ~30s decisive empirical test. Plus 2 novel directions from neuroscience (hippocampal theta burst write + cerebellar random-expansion that lifts capacity to O(N^2)). All 3 testable for $0 in ~15 min wall.
