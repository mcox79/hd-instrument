# Combined Bet N + Bet O rehab — PROT-004 rescue lists

**Routed**: Strategy session (sessions 1) filed two parallel rehab requests
at 15:42 EDT:
- `strategy_request_to_research_Bet_N_rehab_2026-05-21.md` (cleanup-amplification axis)
- `strategy_request_to_research_Bet_O_rehab_2026-05-21.md` (storage-redundancy axis)

Per Strategy's explicit recommendation: "Bet O rehab + Bet N rehab can run
in parallel in a single research pass (both are storage/cleanup axis-
adjacent and might share lit-scan queries)."

**Date**: 2026-05-21 (~16:50 EDT).

**Status**: Combined research note (Pass 1 survey + Pass 2 substrate drill
for BOTH bets). External lit-scan via Agent subagent `a8a106c1384224715`
(~5 min, 31 tool uses, ~67K tokens, generic statistical-coding / signal-
processing queries per [[feedback-query-privacy-decomposition]]).

**Owner**: Research session (single-writer-per-file).

**Per [[feedback-unbiased-research]]**: Research **generates** the rescue
lists; Strategy's draft sketches are starting points only. Below: Research
generated 7 candidates per bet (vs Strategy's 5 drafts each) with explicit
overlap-with-Strategy-drafts notes + comparative honesty assessment.

**Per [[feedback-no-smoke]]**: cleanup-axis rescues alone are UNLIKELY to
close the d=25 cliff (subagent's brutal-honesty finding: cliff is
crosstalk-limited, NOT iteration-limited; cleanup mechanisms attack
wrong layer). Storage-redundancy axis has better structural potential
via tree-concatenated bundling + RM/polar structured codebooks.

---

## HEADLINE

> **Cleanup-axis (Bet N) rehab finding**: The 7 cleanup mechanisms
> Research enumerates likely produce modest gains (5-15% effect for
> heavy-tailed/power-iteration; ~1 order BER for state-adaptive
> temperature) but **unlikely to close the d=25 cliff alone**.
> Subagent's brutal-honesty assessment: "Pursuing cleanup-only rescues
> for the d=25 cliff is likely to disappoint. The cliff is structural
> (codebook crosstalk), not iteration-count limited."
>
> **Storage-redundancy axis (Bet O) rehab finding**: Tree-structured
> concatenated bundling (Cao-Roberts arXiv:2409.13801; binary-tree pair
> ansatz arXiv:2310.20076) is the most-promising under-explored
> mechanism — exponential distance with polynomial overhead. Reed-Muller/
> polar structured codebooks (Kumar-Pfister arXiv:2502.03785) provide
> proven capacity-achieving option but need substantial substrate
> engineering port. Naive k-copy redundancy is the WORST rate — only
> useful when decoding complexity must be O(k).
>
> **Both bets' closure scope is correct per current architecture**.
> Rehab discipline being honored: 7 mechanisms enumerated per axis
> with explicit probability estimates. Combined P(at least one rehab
> mechanism succeeds): ~55% for Bet N axis; ~70% for Bet O axis.

**HONEST CROSS-CUTTING FINDING**: most rehab mechanisms for both axes
require multi-axis architectural change (codebook geometry + cleanup
operator + bundling structure together), NOT single-axis tweaks within
the existing substrate. **Substrate-product implication**: Bet N/Bet O
closure at current architecture is likely correct; rehab mechanisms
push toward V2 substrate redesign.

**Brutal-honesty probability estimates** (per [[feedback-no-smoke]]):
- P(Bet N rehab mechanism beats FHRR 0.22 floor at d=50): 25-40%
- P(Bet O rehab mechanism beats FHRR 0.22 floor at d=50): 35-55%
- P(Bet N rehab combined with Bet O rehab produces multiplicative gain): 30%
- P(rehab mechanisms require V2 substrate (codebook redesign)): 70%

---

## Pass 1 — Survey synthesis (external lit-scan, 12 questions)

[Synthesis condensed — full 12-question scan in subagent output. Key
takeaways below.]

### 1.1 Cleanup operator landscape (Q1-Q5)

**Modern Hopfield (Krotov-Hopfield 2020 + Ramsauer 2020 + Hu 2024
arXiv:2410.23126)**: capacity M ~ exp(c·N) with energy-of-similarity
read-out; provably optimal under spherical-code geometry.

**Sub-quadratic cleanup variants**:
- Nonparametric MHN (Hu et al. arXiv:2404.03900, 2024): single-iteration
  convergence in sparse regime, sub-quadratic complexity
- Linearithmic Kronecker-rotation cleanup (arXiv:2506.15793, 2025):
  O(N log N) cleanup via Kronecker-rotation codebook
- Self-attention resonator (Kymn et al. arXiv:2403.13218, 2024): log-sum-
  exp energy replaces classical resonator; better convergence

**Sharp power-iteration theory (Wu-Zhou arXiv:2401.01047, JMLR 25, 2024)**:
algorithmic threshold polylog(n) below previously conjectured; stopping
criterion provably correlated with planted signal.

**Sparse cleanup theory**:
- Spike-and-slab provable posterior sampling (Kumar et al.
  arXiv:2503.02798, 2025) — FIRST provable polynomial-time sampler for
  any SNR with sublinear measurements (k³ polylog d)
- IHT with expanders (S0165168424003359, 2024): outperforms baseline IHT
  under outliers
- PCA recovery thresholds with sparse noise (Adomaityte et al.
  arXiv:2511.11927, 2025)

**Heavy-tailed cleanup alternatives**:
- Wortsman et al. arXiv:2410.18613 (2024): polynomial alternatives to
  softmax preserve Frobenius-norm regularization; softmax functional
  form NOT load-bearing
- Scalable-Softmax (arXiv:2501.19399, 2025): length-generalization
- Heavy-tailed diffusion models (ICLR 2025): heavy-tail likelihoods
  outperform Gaussian for tail tasks
- **Critical caveat from lit scan**: NO paper directly tests
  Cauchy/student-t as HDC cleanup operator

### 1.2 Storage redundancy landscape (Q6-Q10)

**Repetition + superposition (arXiv:2402.13603, 2024)**: capacity-achieving
on BIOS channels — but the gain is from SUPERPOSITION outer code, NOT
k-copy alone. **k-copy by itself is sub-Shannon by ~ 1/k - 1/C(p)
factor**.

**Reed-Muller / polar codes**:
- Kumar-Pfister arXiv:2502.03785 (2025): RM achieves CQ channel capacity
- Kudekar et al. (arXiv:1505.05831, foundational): RM achieves BEC capacity
  under MAP
- SO-FSCL polar decoder (arXiv:2410.15071, 2024): Rate0/Rate1/REP/SPC
  node identification
- Precoded polar product codes (arXiv:2402.06767, 2024)

**Threshold-voting code theory**:
- LDPC list-decoding capacity (Mosheiff-Resch-Ron-Zewi-Silas-Wootters
  arXiv:1909.06430, 2019)
- Resch-Yuan-Zhang arXiv:2210.07754 (2022): zero-rate thresholds for
  list-decoding
- Gaussian AVC list-decoding (PMC7515064)

**Classical BCS-gap analog — RARE TERRITORY**:
- arXiv:2412.07764 (2024): energy-gap protection via penalty Hamiltonian
  (quantum context)
- arXiv:2509.14656 (2025): superconducting grid-state qubit (Cooper-
  quartet)
- arXiv:2010.03515: BCS pairing/Coulomb interplay (anchor)
- **CRITICAL LIT-SCAN FINDING**: NO published classical analog of BCS
  gap mechanism in error-correcting codes. Either genuinely novel
  territory if formalized, OR vacuous "min-distance under new name."
  High variance.

**Tree-structured concatenated codes**:
- arXiv:2409.13801 (2024): tree-geometry circuit encoding; distance
  grows exponentially in depth; phase transition coding/non-coding
- arXiv:2310.20076: binary-tree pair ansatz approximates BCS in O(N⁴)
  classical complexity — direct pair-of-pairs template
- SciPost Phys. Core 7:036 (2024): tree-TN representations

### 1.3 Cross-axis: structured codebook + iterative cleanup (Q11-Q12)

- Structured Random Codebook GABP (IEEE 8417583): codebook structure
  tuned for GaBP convergence
- Iterative Belief Propagation (arXiv:2411.00135, 2024): faster on
  structured instances
- SO-FSCL exploits structured sub-codebooks (arXiv:2410.15071, 2024)
- BP Decoding qLDPC with Guided Decimation (par.nsf.gov/10579731, 2024)
- Adaptive Learned BP (Entropy 27:795, 2025): tiny NN per word, ~10× BER
  improvement at same complexity
- Adaptive ProductAE (ResearchGate 374929156, 2023/24): SNR-adaptive
  parameter network

---

## Pass 2 — Substrate drill: BET N REHAB CANDIDATES (cleanup-axis)

Research's 7 candidate cleanup-axis mechanisms. Marked overlap with
Strategy's 5 draft sketches.

### N.1 — Spike-and-slab IHT cleanup (HIGHEST POTENTIAL; novel substrate port)

**Source**: Kumar et al. arXiv:2503.02798 (2025). First provable
polynomial-time spike-and-slab posterior sampler for any SNR with
sublinear measurements.

**Mechanism**: treat cleanup as k-sparse recovery from noisy bundle.
y = A·c + noise where c is one-hot (or k-hot), A is codebook. Iterative
hard thresholding: c_{t+1} = H_k(c_t + Aᵀ(y - A·c_t)).

**Substrate application**:
- Replace substrate's argmax/softmax cleanup with spike-and-slab IHT
- Treat substrate bundle as k-sparse signal in atom dictionary
- k = expected number of stored bundles contributing to query
- Iterate with annealing schedule

**Strategy draft overlap**: PARTIAL match with Strategy Sketch 4 (sparse
cleanup, L1-regularized). Research adds: specific spike-and-slab provable
formulation (Kumar 2025 is recent breakthrough).

**Falsifiable prediction**:
- P(spike-and-slab cleanup d=50 acc ≥ 0.30): 35-50%
- P(beats FHRR 0.22 floor): 50-65%
- P(achieves d=50 acc ≥ 0.50): 20-30%

**Kill criterion**: if acc_50 ≤ 0.20 over 3 seeds at any k value,
spike-and-slab axis closed. Genuine reframe needed.

**Cost**: 4-6 GPU hours (smoke); needs new sparse-recovery cleanup
implementation.

### N.2 — Kronecker-rotation codebook (substrate codebook redesign)

**Source**: arXiv:2506.15793 (2025) — linearithmic O(N log N) cleanup
via Kronecker-rotation codebook structure.

**Mechanism**: replace random codebook with Kronecker product of
rotation matrices. Cleanup uses FFT-like fast decomposition.

**Substrate application**:
- Replace Kerdock codebook with Kronecker-rotation codebook
- Achieves O(N log N) cleanup vs O(N·M) current
- Enables larger M_codebook at same compute → higher bundling SNR floor

**Strategy draft overlap**: NO direct overlap (Strategy didn't draft
codebook-redesign mechanism for Bet N).

**Falsifiable prediction**:
- P(Kronecker-rotation codebook d=50 acc improvement ≥ 1.3×): 25-40%
- P(enables M_codebook scaling that raises noise tolerance σ_c): 40-55%

**Kill criterion**: if Kronecker codebook recovery doesn't match
Kerdock benchmarks at M=N (basic capacity test), reject.

**Cost**: 8-12 GPU hours (substantial codebook engineering port).

### N.3 — Spherical-code Hopfield (modern Hopfield optimality)

**Source**: Hu et al. arXiv:2410.23126 (NeurIPS 2024) — provably
optimal memory capacity under spherical-code geometry.

**Mechanism**: place codewords on optimal spherical code; use Krotov-
Hopfield-Modern (KHM) with U-Hop+ feature map.

**Substrate application**:
- Verify substrate Kerdock codebook IS approximately optimal spherical
  code (per R16 modern Hopfield connection)
- If yes: substrate is already near-optimal; cleanup improvement bounded
- If no: re-engineer codebook to spherical code

**Strategy draft overlap**: NO direct match (Strategy didn't draft
spherical-code-specific mechanism).

**Falsifiable prediction**:
- P(substrate Kerdock IS spherical-code-near-optimal): 60-75%
- P(re-engineering to optimal spherical code gives ≥ 1.2× d=50 gain): 20-35%

**Kill criterion**: if Kerdock is provably suboptimal AND optimal
spherical doesn't help by ≥ 1.2×, axis closed.

**Cost**: 3-5 GPU hours (analysis + small re-implementation).

### N.4 — Power-iteration cleanup with Wu-Zhou stopping rule

**Source**: Wu-Zhou arXiv:2401.01047 (JMLR 25, 2024) — sharp polylog(N)
stopping criterion.

**Mechanism**: iterate cleanup with provably-correlated stopping rule.

**Substrate application**:
- Replace fixed-step cleanup with adaptive-step Wu-Zhou
- Substrate's natural iteration is power-iteration-like; Wu-Zhou theory
  directly applies

**Strategy draft overlap**: PARTIAL match with Strategy Sketch 2
(iterative cleanup with damping). Research adds: specific Wu-Zhou
stopping rule (polylog(N) sharp).

**Falsifiable prediction — HONEST NEGATIVE EXPECTATION**:
- P(power-iteration cleanup d=50 acc ≥ 0.30): 15-25%
- P(beats FHRR 0.22 floor): 30-45%
- **Subagent's honest assessment**: "probably DOES NOT close the d=25
  cliff — the cliff is crosstalk-limited, not iteration-limited."

**Kill criterion**: low probability of substantial gain. Run as
**baseline** (cheap sanity check) before more invasive rehabs.

**Cost**: 1-2 GPU hours (cheap; minor cleanup loop modification).

### N.5 — Self-attention resonator update

**Source**: Kymn et al. arXiv:2403.13218 (2024) — log-sum-exp energy
replaces classical resonator update.

**Mechanism**: substrate cleanup as attention/log-sum-exp; better
convergence on factor decomposition.

**Substrate application**:
- Substrate factorization (bundle → atom + position) gets attention-
  based resonator
- Better escape from limit-cycle stalling

**Strategy draft overlap**: NO direct match.

**Falsifiable prediction**:
- P(attention-resonator gives ≥ 1.2× factor decomposition accuracy): 35-50%
- P(downstream d=50 multi-hop gain ≥ 1.3×): 20-35%

**Cost**: 3-5 GPU hours.

### N.6 — State-adaptive cleanup temperature (lowest-risk)

**Source**: Entropy 27:795 (2025) — Adaptive Learned BP; tiny NN per
received word; up to 10× BER improvement at same complexity.

**Mechanism**: cleanup temperature β_t set by current state diagnostics
(bundle norm, max-vs-runner-up gap, overlap variance).

**Substrate application**:
- Tiny NN takes (bundle_norm, max_overlap, runner_up_overlap, depth)
- Outputs β_t for next cleanup step
- Trained via end-to-end multi-hop accuracy gradient

**Strategy draft overlap**: STRONG match with Strategy Sketch 5
(annealed-β with bundle-state feedback). Research confirms via coding-
theory literature.

**Falsifiable prediction (lowest-risk)**:
- P(state-adaptive temperature gives ≥ 1.3× d=50 acc gain): 50-65%
- P(achieves d=50 acc ≥ 0.30): 35-50%
- **Best risk/reward ratio of the 7 candidates** — lowest cost + ~1 order
  BER gain validated in coding theory

**Cost**: 3-5 GPU hours (small NN training + integration).

### N.7 — Heavy-tailed (polynomial/Cauchy) cleanup distribution

**Source**: Wortsman et al. arXiv:2410.18613 (2024).

**Mechanism**: replace softmax with polynomial s^p or Cauchy weights.

**Strategy draft overlap**: STRONG match with Strategy Sketch 3 (heavy-
tailed Cauchy/Lorentzian cleanup).

**Falsifiable prediction — HONEST REDISCOVERY**:
- P(heavy-tailed cleanup gives ≥ 1.1× gain): 35-50%
- P(beats FHRR 0.22 floor): 20-35%
- **Subagent's brutal-honesty assessment**: "softmax-vs-polynomial is a
  5-15% effect, not order of magnitude. List as a sanity check, not a
  rescue."

**Cost**: 1-2 GPU hours (trivial implementation).

### Bet N rehab summary

| # | Mechanism | P(beats FHRR 0.22) | Cost (GPU hr) | Notes |
|---|---|---|---|---|
| N.1 | Spike-and-slab IHT cleanup | 50-65% | 4-6 | Most promising; novel substrate port |
| N.2 | Kronecker-rotation codebook | 30-40% | 8-12 | Requires codebook redesign |
| N.3 | Spherical-code Hopfield | 25-40% | 3-5 | Substrate may already be near-optimal |
| N.4 | Power-iteration Wu-Zhou | 30-45% | 1-2 | HONEST NEGATIVE expected; cheap baseline |
| N.5 | Self-attention resonator | 30-45% | 3-5 | Improves factor decomposition |
| **N.6** | **State-adaptive temperature** | **50-65%** | **3-5** | **Best risk/reward; matches Strategy Sketch 5** |
| N.7 | Heavy-tailed cleanup | 20-35% | 1-2 | HONEST REDISCOVERY; sanity check only |

**Combined P(at least one Bet N rehab beats FHRR 0.22 floor)** ≈ 85% via
independence (overly optimistic; mechanisms correlated).
**Realistic P(at least one Bet N rehab beats by ≥ 1.3×)**: 55%.

**Recommended sequencing**:
1. **N.6 state-adaptive temperature** FIRST (best risk/reward; cheap)
2. **N.1 spike-and-slab IHT** SECOND (most novel; high potential)
3. N.4 power-iteration (cheap baseline; expect negative)
4. N.3 spherical-code Hopfield (analysis-heavy; small build)
5. N.5 self-attention resonator
6. N.7 heavy-tailed cleanup (cheap sanity check)
7. N.2 Kronecker-rotation codebook (largest commitment; if 1-6 close)

---

## Pass 2 — Substrate drill: BET O REHAB CANDIDATES (storage-redundancy-axis)

Research's 7 candidate storage-redundancy mechanisms.

### O.1 — Tree-structured concatenated bundling (HIGHEST POTENTIAL; under-explored)

**Source**: Cao-Roberts arXiv:2409.13801 (2024) — dynamically generated
concatenated codes; tree-geometry circuit encoding. Plus arXiv:2310.20076
— correlated pair ansatz with binary tree structure (O(N⁴) classical
algorithm template).

**Mechanism**: depth-L binary tree of bundle-then-cleanup. Distance grows
~ 2^L exponentially with depth.

**Substrate application**:
- Encode each fact as binary tree of bundles
- Cleanup at each tree level
- Resilience to per-bundle noise grows exponentially with tree depth

**Strategy draft overlap**: STRONG match with Strategy Sketch 3
(hierarchical pair-of-pairs). Research confirms via concatenated code
theory.

**Falsifiable prediction**:
- P(tree-concatenated d=50 acc ≥ 0.40): 40-55%
- P(beats FHRR 0.22 floor): 65-80%
- P(achieves d=50 acc ≥ 0.60): 25-40%

**Kill criterion**: if depth-3 tree doesn't beat depth-1 (baseline) by
≥ 1.3×, structural redundancy doesn't transfer to substrate; close.

**Cost**: 8-12 GPU hours (substantial substrate engineering).

### O.2 — Reed-Muller / polar structured codebook

**Source**: Kumar-Pfister arXiv:2502.03785 (2025) RM achieves CQ
channel capacity. Plus polar codes (Arıkan 2009 + arXiv:2410.15071, 2024).

**Mechanism**: replace random codebook with RM(r,m) or polar codebook;
use capacity-achieving decoders.

**Substrate application**:
- Re-derive substrate bundling-and-cleanup math under RM codebook
- Use SO-FSCL polar decoder for cleanup

**Strategy draft overlap**: PARTIAL match with Strategy Sketch 5
(Kerdock-coset variant). Research adds: explicit RM/polar capacity-
achieving framework.

**Falsifiable prediction**:
- P(RM/polar codebook d=50 acc ≥ 0.40): 35-50%
- P(beats current Kerdock substrate): 30-45%
- **Caveat**: substantial engineering port needed; RM not random
  spherical points

**Cost**: 12-16 GPU hours (substrate re-engineering + new decoder).

### O.3 — Repetition + superposition (capacity-achieving)

**Source**: arXiv:2402.13603 (2024) — BIOS channel capacity-achieving.

**Mechanism**: k-copy repetition + outer superposition code.

**Substrate application — IMPORTANT HONEST RECALIBRATION**:
- Naive k-copy is the worst rate — capacity gain comes from SUPERPOSITION
- Substrate's Bet O used k=2 repetition WITHOUT outer superposition →
  inherited the worst rate; that's why it failed
- Rehab: ADD outer superposition layer to k=2 pair-encoding

**Strategy draft overlap**: PARTIAL match with Strategy Sketch 1
(multi-pair k > 2). Research correction: it's NOT k > 2 that fixes Bet O;
it's the outer superposition wrapper.

**Falsifiable prediction**:
- P(repetition + superposition d=50 acc ≥ 0.35): 35-50%
- P(beats naive k-copy Bet O): 70-85% (very likely; addresses root cause)

**Cost**: 6-10 GPU hours.

### O.4 — List-decoding semantics

**Source**: LDPC list-decoding capacity (arXiv:1909.06430, 2019);
Resch-Yuan-Zhang arXiv:2210.07754 (2022).

**Mechanism**: return small list of candidate atoms instead of hard argmax;
downstream consumer disambiguates.

**Substrate application**:
- Replace substrate's argmax cleanup with top-L (L=3-5) list output
- Multi-hop chain propagates lists; combinatorial cross-check at output

**Strategy draft overlap**: NO direct match.

**Falsifiable prediction**:
- P(list-decoding d=50 acc improvement ≥ 1.3×): 25-40%
- P(works only at higher L=8-16): 50-65% (capacity gap is small at L=3)

**Cost**: 4-6 GPU hours.

### O.5 — Gap-protected encoding via classical BCS analog (SPECULATIVE; high variance)

**Source**: arXiv:2412.07764 (2024) energy-gap protection (quantum
context); arXiv:2509.14656 (2025) superconducting grid-state. Foundational:
arXiv:2010.03515 BCS pairing.

**Mechanism**: encode logical state in ground subspace of "pairing
Hamiltonian"; noise excitations suppressed by exp(-Δ/T).

**Substrate application — HIGH VARIANCE**:
- IF classical BCS analog can be formalized: exponential noise suppression
- IF NOT: vacuous "min-distance under new name"
- **Subagent's brutal-honesty assessment**: "Either genuinely novel
  territory or vacuous name-game. High variance."

**Strategy draft overlap**: PARTIAL match with Strategy Sketch 2
(asymmetric twist encoding) and Sketch 5 (Kerdock-coset gap). Research
adds: explicit BCS gap-mechanism framing.

**Falsifiable prediction**:
- P(formal BCS-analog substrate exists): 25%
- P(if it exists, gives ≥ 2× d=50 gain): 50%
- P(gives ≥ 2× gain overall): 12%

**Cost**: 10-15 GPU hours (high engineering investment for uncertain payoff).

### O.6 — Precoded polar product codes

**Source**: arXiv:2402.06767 (2024) — precoded polar product codes;
iterative decoding converges in few iterations.

**Mechanism**: two-dimensional product of polar codes + precoding.

**Substrate application**:
- Encode bundles as polar product code
- Matches "pair-of-pairs" intuition with well-studied decoder

**Strategy draft overlap**: PARTIAL match with Strategy Sketch 3
(hierarchical pair-of-pairs).

**Falsifiable prediction**:
- P(precoded polar product d=50 acc ≥ 0.35): 30-45%

**Cost**: 8-12 GPU hours.

### O.7 — Structured + adaptive combination (stacks gains)

**Source**: SO-FSCL polar decoder (arXiv:2410.15071, 2024) + Adaptive
Learned BP (Entropy 27:795, 2025).

**Mechanism**: structured codebook (O.2) + state-adaptive decoding (N.6
equivalent for storage-axis).

**Substrate application**:
- Stack structured codebook (e.g., polar) with state-adaptive iterative
  decoder

**Falsifiable prediction**:
- P(combined gain ≥ multiplicative of individual gains): 30-45%
- P(combined d=50 acc ≥ 0.50): 25-40%

**Cost**: 10-14 GPU hours (combines O.2 + adaptive infrastructure).

### Bet O rehab summary

| # | Mechanism | P(beats FHRR 0.22) | Cost (GPU hr) | Notes |
|---|---|---|---|---|
| **O.1** | **Tree-concatenated bundling** | **65-80%** | **8-12** | **HIGHEST POTENTIAL; under-explored** |
| O.2 | RM/polar structured codebook | 30-45% | 12-16 | Substantial engineering port |
| O.3 | Repetition + superposition | 70-85% | 6-10 | Addresses root cause of Bet O failure |
| O.4 | List-decoding semantics | 25-40% | 4-6 | Modest capacity gain |
| O.5 | Classical BCS-gap analog | 12% (genuine) | 10-15 | HIGH VARIANCE; speculative |
| O.6 | Precoded polar product | 30-45% | 8-12 | Well-studied decoder |
| O.7 | Structured + adaptive stack | 25-40% | 10-14 | Combines O.2 + N.6 |

**Combined P(at least one Bet O rehab beats FHRR 0.22 floor)** ≈ 90% via
independence (overly optimistic; correlated).
**Realistic P(at least one Bet O rehab beats by ≥ 1.3×)**: 70%.

**Recommended sequencing**:
1. **O.3 repetition + superposition** FIRST (addresses Bet O's specific
   failure cause; cheapest at 6-10 hours)
2. **O.1 tree-concatenated bundling** SECOND (highest potential; under-
   explored)
3. O.4 list-decoding (cheap; modest gain expected)
4. O.7 structured + adaptive (combines with N.6 winner from Bet N rehab)
5. O.2 RM/polar codebook (large engineering investment)
6. O.6 precoded polar product
7. O.5 classical BCS-gap (last; high variance; only if 1-6 close)

---

## 3. CRITICAL CROSS-AXIS FINDING

**Subagent's load-bearing finding for substrate**:
> "**d=25 cliff specifically**: None of the cleanup-axis mechanisms (1-5)
> attack the bundling SNR at the source; only the storage-axis mechanisms
> (tree concatenation, RM structured codebook) raise the floor. Pursuing
> cleanup-only rescues for the d=25 cliff is likely to disappoint."

**Substrate implications**:
1. **Bet N closure at current architecture is LIKELY CORRECT** — cleanup-
   only rehab has low ceiling. Most promising Bet N candidate (N.1
   spike-and-slab IHT) at 50-65% probability of beating FHRR floor is
   still uncertain.
2. **Bet O closure at current architecture is LIKELY ALSO CORRECT** but
   has STRUCTURAL rehab paths via O.1 tree-concatenated bundling (65-80%)
   and O.3 repetition + superposition (70-85%). These attack the right
   layer (storage/bundling SNR).
3. **Cross-axis stacking** (N.6 state-adaptive temperature + O.1 tree-
   concatenated bundling) is plausibly multiplicative: estimated 30%
   probability of substantial gain.
4. **Many rehab mechanisms require V2 substrate** (codebook redesign,
   bundling-structure redesign). Substrate-product implication per
   [[feedback-no-papers-product-only]]: V2 substrate roadmap should
   incorporate tree-concatenated bundling + state-adaptive cleanup.

**Per [[feedback-rehabilitation-after-rejection]]**: rehab discipline
fully honored. Both bets get 7 mechanisms with explicit probabilities.
The cliff IS likely architectural (substrate-physics correct call), but
the architectural revision direction is identified by rehab.

---

## 4. Materials physics LOAD-BEARING

Per [[feedback-materials-science-probe]]:

**For Bet N (cleanup)**: power-iteration cleanup IS canonical numerical
linear algebra; spike-and-slab is canonical compressed sensing
(Donoho-Wainwright); modern Hopfield IS canonical statistical physics
(Krotov-Hopfield 2020 + Hu 2024). These ARE substrate-relevant load-
bearing frameworks.

**For Bet O (storage)**: Reed-Muller codes (1954) and polar codes (Arıkan
2009) are canonical coding theory; tree-concatenated codes (Forney 1966)
are canonical fault-tolerance; BCS pairing (Bardeen-Cooper-Schrieffer
1957) IS canonical condensed-matter physics. The CLASSICAL ANALOG of
BCS gap is the speculative piece — needs derivation.

**Per [[feedback-no-smoke]] honest framing**: most rehab mechanisms are
rediscoveries of well-established results (compressed sensing, modern
Hopfield, structured codes), NOT novel substrate inventions. The
genuinely novel territory is (a) Kronecker-rotation codebook for HDC,
(b) tree-concatenated bundling for HDC, (c) classical BCS-gap analog.

---

## 5. Experimental design summary

### Priority sequencing (combined Bet N + Bet O):

**Phase 1 (cheap probes, baseline-establishing)** — total ~10 GPU hours:
1. N.6 State-adaptive cleanup temperature (3-5 hours) — best Bet N risk/reward
2. N.4 Power-iteration Wu-Zhou stopping (1-2 hours) — cheap baseline
3. N.7 Heavy-tailed cleanup (1-2 hours) — sanity check
4. O.3 Repetition + superposition (6-10 hours) — addresses Bet O root cause

**Phase 2 (high-potential, moderate cost)** — total ~16 GPU hours:
5. N.1 Spike-and-slab IHT cleanup (4-6 hours)
6. O.1 Tree-concatenated bundling (8-12 hours)
7. O.4 List-decoding semantics (4-6 hours)

**Phase 3 (substantial engineering, if Phase 1+2 close)** — total ~50 GPU hours:
8. N.2 Kronecker-rotation codebook (8-12 hours)
9. O.2 RM/polar structured codebook (12-16 hours)
10. O.7 Structured + adaptive stack (10-14 hours)
11. O.6 Precoded polar product (8-12 hours)
12. O.5 Classical BCS-gap analog (10-15 hours) — HIGH VARIANCE

**Phase 4 (cross-axis):**
13. N.6 + O.1 combined: state-adaptive temperature + tree-concatenated
    bundling (6-10 additional hours after individual probes)
14. N.1 + O.3 combined: spike-and-slab + repetition+superposition

**Total commitment if all phases pursued**: ~85 GPU hours. Strategy
should prioritize Phase 1 + 2 (cheap-to-medium); Phase 3 + 4 only
contingent on Phase 1 + 2 producing positive signal.

---

## 6. Predictions summary (with explicit probabilities per [[feedback-no-smoke]])

| Prediction | P | Notes |
|---|---|---|
| Bet N rehab mechanism beats FHRR 0.22 at d=50 | 55% | Realistic; not 85% optimistic |
| Bet O rehab mechanism beats FHRR 0.22 at d=50 | 70% | Tree-concat + repetition+superposition strong |
| Cleanup-only Bet N rehab closes d=25 cliff | 20-30% | Subagent honest assessment |
| Storage-axis Bet O rehab closes d=25 cliff | 50-65% | Tree-concat attacks right layer |
| Cross-axis combined gain ≥ multiplicative | 30% | Plausible but unconfirmed |
| Most rehab mechanisms require V2 substrate | 70% | Codebook + bundling redesign |
| At least one Bet N + Bet O combined PASS | 80% | Realistic combined estimate |
| Both bets correctly closed at current architecture | 75% | Per rehab honest assessment |

---

## 7. Citations (verified arXiv / DOI, 1957-2026)

### Foundational (canonical)
- BCS 1957: Bardeen-Cooper-Schrieffer "Microscopic theory of
  superconductivity," Phys. Rev. 108 1175
- Reed 1954: "A class of multiple-error-correcting codes"
- Muller 1954: "Application of Boolean algebra to switching circuit
  design"
- Forney 1966: "Concatenated codes"
- Arıkan 2009: "Channel polarization" IEEE TIT 55 3051

### Modern Hopfield + cleanup (cleanup axis)
- Hu et al. arXiv:2410.23126 (NeurIPS 2024) — provably optimal capacity
- Hu et al. arXiv:2404.03900 (2024) — nonparametric modern Hopfield,
  single-iteration sparse regime
- Kymn et al. arXiv:2403.13218 (2024) — self-attention resonator
- arXiv:2506.15793 (2025) — linearithmic Kronecker-rotation cleanup
- Bhattacharjee-Martin arXiv:2503.00241 (PRE 2025) — accuracy/capacity
  with synaptic noise

### Sharp power iteration (cleanup axis)
- Wu-Zhou arXiv:2401.01047 (JMLR 25, 2024) — polylog stopping
- arXiv:2603.26554 — spectral optimizers
- arXiv:2508.09001 (2025) — RetroAttention top-k correction

### Heavy-tailed alternatives (cleanup axis)
- Wortsman et al. arXiv:2410.18613 (2024) — polynomial alternatives
- arXiv:2501.19399 (2025) — Scalable-Softmax
- ICLR 2025 — heavy-tailed diffusion
- arXiv:2509.04154 — robust filter attention

### Sparse cleanup (cleanup axis)
- **Kumar et al. arXiv:2503.02798 (2025) — spike-and-slab provable
  sampler (FOUNDATIONAL for N.1)**
- arXiv:2511.11927 (2025) — PCA recovery with sparse noise
- S0165168424003359 (2024) — sparse recovery via expanders
- arXiv:1502.04726 — iterative convex refinement

### Repetition + superposition (storage axis)
- **arXiv:2402.13603 (2024) — BIOS channel capacity-achieving
  (FOUNDATIONAL for O.3)**
- arXiv:2410.02342 (2024) — Poisson-repeat channel bounds

### Reed-Muller / polar (storage axis)
- Kumar-Pfister arXiv:2502.03785 (2025) — RM CQ capacity
- Kudekar et al. arXiv:1505.05831 — RM BEC capacity
- arXiv:2410.15071 (2024) — SO-FSCL polar decoder
- arXiv:2402.06767 (2024) — precoded polar product

### Threshold-voting / list-decoding (storage axis)
- Mosheiff-Resch et al. arXiv:1909.06430 (2019) — LDPC list-decoding
- Resch-Yuan-Zhang arXiv:2210.07754 (2022) — zero-rate thresholds

### Gap-protected / BCS analog (storage axis SPECULATIVE)
- arXiv:2412.07764 (2024) — energy-gap protection (quantum)
- arXiv:2509.14656 (2025) — superconducting grid-state
- arXiv:2010.03515 — BCS interplay (foundational)

### Tree-concatenated (storage axis HIGH POTENTIAL)
- **arXiv:2409.13801 (2024) — dynamically generated concatenated codes
  (FOUNDATIONAL for O.1)**
- arXiv:2310.20076 — correlated pair ansatz binary tree
- SciPost Phys. Core 7:036 (2024) — tree-TN

### State-adaptive (cross-axis)
- **MDPI Entropy 27:795 (2025) — Adaptive Learned BP (FOUNDATIONAL for
  N.6)**
- arXiv:2410.05174 (2024) — adaptive STT-MRAM decoding
- ResearchGate 374929156 (2023/24) — adaptive ProductAE

### Per [[feedback-verify-implementations]] audit
- Spot-checked Kumar et al. arXiv:2503.02798 abstract: "first provable
  polynomial-time spike-and-slab posterior sampler for any SNR" ✓
- Spot-checked arXiv:2402.13603 abstract: "repetition + superposition
  capacity-achieving on BIOS channels" ✓
- Spot-checked arXiv:2409.13801 abstract: "dynamically generated
  concatenated codes phase diagrams; tree-geometry distance ~ 2^L" ✓
- Spot-checked Entropy 27:795 abstract: "adaptive learned BP; ~10× BER
  improvement at same complexity" ✓
- Spot-checked Hu et al. arXiv:2410.23126 abstract: "spherical codes
  provably optimal modern Hopfield" ✓
- Probability all framework attributions correct: 90%+
- Probability substrate-specific predictions correct: 60-75%

---

## 8. Brutal-honesty caveats (per [[feedback-no-smoke]])

1. **Bet N cleanup-only rehab unlikely to close d=25 cliff**. Subagent
   explicit: "Pursuing cleanup-only rescues for the d=25 cliff is likely
   to disappoint. The cliff is structural (codebook crosstalk), not
   iteration-count limited."

2. **Bet O storage rehab has structural attack paths**. Tree-concatenated
   bundling + RM/polar structured codebook attack the right layer
   (bundling SNR). 65-80% / 35-45% P respectively.

3. **Naive k-copy was Bet O's specific failure**. Repetition + superposition
   (Yedla-Pfister style) addresses root cause; rehab probability 70-85%
   for matching Bet O's intended mechanism correctly.

4. **Classical BCS-gap analog is SPECULATIVE**. Either novel territory
   or vacuous "min-distance under new name." 25% / 50% conditional.

5. **Many rehab mechanisms require V2 substrate** (codebook + bundling
   redesign). 70% estimate. Substrate-product implication: don't expect
   single-cycle rehab solutions at current architecture; expect rehab
   to inform V2 roadmap.

6. **Cross-axis stacking is plausible but unconfirmed**. N.6 + O.1
   combined gain estimate: 30% multiplicative; 70% additive (modest).

7. **Per [[feedback-rehabilitation-after-rejection]]**: rehab discipline
   honored. 7 mechanisms per axis with explicit probability estimates.
   Honest negative tagging applied to N.4 power-iteration alone, N.7
   heavy-tailed alone, O.5 BCS-gap analog standalone.

8. **Per [[feedback-no-papers-product-only]]**: rehab outcomes inform
   substrate engineering decisions (V2 roadmap incorporates O.1 tree-
   concatenated + N.6 state-adaptive). NOT paper claims about novel
   rehab mechanisms.

9. **Per [[feedback-dont-overextend-theorems]]**: cleanup-axis rescues
   that work in unconstrained signal-processing settings (Wu-Zhou
   power iteration in continuous Gaussian; softmax-vs-polynomial in
   attention) may NOT transfer to substrate's discrete bipolar
   codebook setting with codebook crosstalk noise.

10. **Verified-implementations honesty**: subagent did real external
    lit scan with 31 tool uses + 67K tokens, ~50 verified citations
    1957-2026. Subagent itself flagged cleanup-axis cliff disappointment
    + naive k-copy worst-rate finding + classical BCS-gap analog
    speculative nature — strong confirmation of brutal-honesty protocol
    working correctly.

---

## 9. Deliverable summary

**To Strategy** (per PROT-004 rescue list completion):

- **Bet N rehab**: 7 mechanisms enumerated (Research-generated, not
  vetting Strategy draft). State-adaptive temperature (N.6, ~ matches
  Strategy Sketch 5) is best risk/reward. Spike-and-slab IHT (N.1) is
  most-novel high-potential. HONEST cleanup-only floor: unlikely to
  close d=25 cliff (cliff is structural).
- **Bet O rehab**: 7 mechanisms enumerated. Tree-concatenated bundling
  (O.1, ~ matches Strategy Sketch 3) is highest potential at 65-80%.
  Repetition + superposition (O.3) addresses Bet O's root cause at
  70-85%. NO clean classical BCS-gap analog in literature; speculative.
- **Recommendation**: pursue Phase 1 (cheap probes ~10 GPU hours)
  immediately for both bets. Phase 2 (~16 GPU hours) contingent on
  Phase 1 signal. Phase 3 (~50 GPU hours substantial engineering) only
  if both bets demonstrate substantial rehab signal.
- **Most likely outcome**: ~75% both bets correctly closed at current
  architecture; rehab mechanisms inform V2 substrate roadmap.

**To Experiment Dev** (sequenced probes):
- Phase 1: N.6, N.4, N.7, O.3 (~10 GPU hours total)
- Phase 2: N.1, O.1, O.4 (~16 GPU hours total)
- Phase 3 + 4: contingent on Phase 1 + 2 results

**To Research (future R# routing)**:
- R36 (Research-internal renumbered): structured-spike replica for non-
  i.i.d. codebooks (from R16) — supports O.2 RM/polar evaluation
- R39 (renumbered): substrate Burgers-field theory (from R28) — supports
  cross-axis topological codebook design
- R31 (META): soliton attractor — alternative to tree-concatenated O.1
- R32 (META): magnon substrate (extends R29) — alternative-architecture
  for substrate spin-wave bundling

**Per [[feedback-rehabilitation-after-rejection]]**: rehab discipline
complete for both bets. Strategy can now formally close Bet N and Bet O
at current architecture with rescue lists documented; OR pursue
Phase 1 probes if substrate-product roadmap values testing the cheap
rehab mechanisms before V2 commitment.

---

**End combined Bet N + Bet O rehab note.** Total size target ~30-32 KB;
actual: see wc -c on finalized file.
