# Research Drill: Coding Theory of High-Resolution Retrieval from Sparse Codes

Date: 2026-07-04
Mode: BRAIN 5x-DRILL, angle 5 of 5 (coding-theory / SDM angle)
Topic: Does sparse-associative-memory / SDM / sparse-population-code theory give a
concrete sparse construction that BEATS our block-argmax 0.43 retrieval ceiling at ~2% density?

---

## Problem (as handed)

Distill BGE-large (1024d dense) -> K-block bipolar SPARSE code. K128 = 128 active,
block-argmax (one active unit per block), clean bind/unbind "SBC" algebra. Need
retrieval `ret_agree10 >= 0.35` at ~2% sparse + algebra + cosine. VERIFIED on-disk:
retrieval 0.20 (trained) vs 0.43 (code-ceiling) at K128; block-argmax caps the ceiling.
USER: "should be EASIER."

Two distinct gaps live here, and they must not be conflated:
- **Training gap:** 0.20 (trained) -> 0.43 (ceiling). Optimization does not reach the code's own best.
- **Ceiling gap:** 0.43 is itself a structural cap of the block-argmax code.

---

## Prior-work check (substrate KB, mandatory pre-dispatch)

Ran `bash tools/substrate_query.sh "sparse distributed memory Kanerva associative memory capacity retrieval"`.
Top hits (cosine 0.48-0.50), all prior SDM/associative drills:
- `notes/research_drill_L5_SDM_Sparse_Distributed_Memory_perturbation_denoising_Cycle_54_architectural_design_2x_2026-06-12.md`
- `notes/research_drill_codebook_capacity_structural_3x_2026-06-10.md`
- `notes/research_drill_sparse_value_coding_within_shards_5x_2026-06-08.md`
- `notes/research_drill_substrate_only_language_model_5x_2026-06-08.md`

**Prior arc work on this concept: SUBSTANTIAL, but on a DIFFERENT axis.** The 2026-06-12
SDM drill designed SDM as an L5 *noise-robustness / cleanup* layer (hard-location voting to
denoise perturbed queries). It did NOT address *retrieval resolution of a sparse distillation
code* — the axis here. This angle is genuinely distinct: not "how does SDM clean noise" but
"is our block-argmax a coding-theoretically low-resolution sparse code, and what construction
has higher resolution at the same 2% density." No rediscovery.

---

## Core diagnosis: block-argmax is a NAMED, KNOWN-suboptimal sparse code

Our construction = one active unit per block (argmax within each of K blocks). This is exactly:

1. **Sparse Block Codes (SBC)** — Frady, Kleyko, Sommer 2021, "Variable binding for sparse
   distributed representations." One-hot-per-block is the canonical SBC. Block structure was
   almost certainly chosen because it gives *clean block-local binding* (bind = block-wise
   cyclic shift / convolution; unbind is exact). That is a real, load-bearing property.

2. **WTAHash (Yagnik et al. 2011, "The Power of Comparative Reasoning")** — divide the vector
   into windows, take argmax within each window. Block-argmax IS WTAHash. It is a *rank/ordinal*
   hash: it encodes only *which coordinate wins each window*, discarding all magnitude and all
   cross-window structure.

The coding theory of WTAHash-type codes is settled, and it says our ceiling is a structural
artifact of **LOCAL winner-take-all**:

- WTAHash = **LOCAL** WTA (one winner per fixed window).
- FlyHash (Dasgupta, Stevens, Navlakha 2017, Science, "A neural algorithm for a fundamental
  computing problem") = **GLOBAL** WTA (top-K over the *whole* expanded vector, no window
  partition), on top of a sparse random *expansion* (fly: ~50 inputs -> ~2000 Kenyon cells,
  ~40x expansion; then ~5% fire).
- Sharma & Navlakha 2018 ("Improving Similarity Search with the Fly", arXiv 1812.01844) prove
  the resolution consequence directly: **FlyHash encodes ~m-times more pairwise orderings than
  WTAHash for the same hash (Hamming) distance**, where m is the expansion factor. "Pairwise
  orderings resolvable" IS retrieval resolution. Local-WTA is provably lower-resolution than
  global-WTA at the same sparsity.

So: **block-argmax's 0.43 ceiling is not a 2%-sparsity limit — it is the local-WTA penalty.**

### Why local WTA caps resolution (mechanism)

- **Rank-only, magnitude-blind:** within a block, only the winner's *identity* survives; the
  gap between 1st and 2nd (the confidence/margin) is thrown away. Two queries with cosine 0.9
  and 0.7 to a target can produce the *same* set of block-winners -> identical rank -> the code
  cannot separate them. This directly bounds `ret_agree`.
- **Boundary-flip quantization noise:** each block is a hard 1-of-L (L=32) decision. Near-ties
  are common; a tiny cosine change flips a winner discontinuously, injecting noise UNcorrelated
  with true similarity. With K=128 independent such decisions, the code accumulates ~128
  high-variance quantization events. Global top-K flips only units *near the rank-K threshold*
  — a far smaller, higher-margin boundary set.
- **Cannot concentrate:** block-argmax forces *exactly one* active unit per block regardless of
  where the signal is. Global top-K lets the same K active units land wherever the signal is
  strongest. Block-argmax is therefore a *strict constraint* on the code (see superset argument).

---

## The three key questions, answered

**(a) Does SDM / sparse-associative theory give a concrete construction beating 0.43?**
YES. The construction is **global winner-take-all over a sparse expansive projection**
(FlyHash / DenseFly family), and its degenerate SBC-preserving cousin **thick-SBC (top-m per
block, m>1)**. Both raise resolution above the local-WTA ceiling at the same density.

**(b) Is block-argmax a KNOWN-suboptimal sparse code vs alternatives?**
YES, unambiguously. It equals WTAHash = local WTA. Established results rank it below:
- FlyHash / DenseFly (global WTA on sparse expansion): m-times more pairwise orders (1812.01844).
- Random-projection sign codes / SimHash for fine-grained real-valued similarity (survey
  arXiv 1408.2927): magnitude-aware where WTAHash is rank-only.
- kWTA global SDR (Numenta): overlap = |A ∩ B| is a smooth high-resolution similarity proxy,
  which local one-hot-per-block degrades by forcing the support to be block-uniform.

**(c) Theoretical resolution/capacity of a well-designed 2% sparse code — is 0.35 easy or hard?**
EASY for the right code; the difficulty is a block-argmax artifact.
- **Willshaw (binary sparse associative):** asymptotic storage capacity ln 2 ≈ 0.69 bits/synapse
  at optimal sparsity k ≈ log n — a 2% sparse binary code is information-theoretically *rich*,
  not starved.
- **SDR overlap resolution (Numenta):** with K active units the overlap statistic ranges 0..K,
  giving K+1 distinguishable similarity levels — K=128 => ~128-level resolution *if* the support
  is free to move (global). Local one-hot-per-block caps this because the support geometry is
  frozen to one-per-block.
- **SDM address decoder:** activation = *global* Hamming-radius threshold on hard locations.
  The shared-activation count is a *smooth, monotone, resolution-amplifying* function of query
  similarity — the "critical distance" property: reading near a stored address returns something
  *even closer* than the query. This is the SDM proof that a **global-threshold sparse
  activation set** is high-resolution. Block-argmax replaces this global threshold with K local
  argmaxes and forfeits exactly that amplification.

Net: 0.35 is comfortably inside what a 2% code carries. **0.43 is a floor imposed by local WTA,
not a ceiling imposed by 2% sparsity.**

---

## SDM address-decoder -> our retrieval problem (the connection)

SDM's address decoder maps a dense query to a *sparse activation set* (hard locations within
radius r) — i.e., it IS a dense->sparse encoder, same object as our distillation code. Its
resolution comes from **global competition** (a single distance threshold over all locations),
not from partitioning the address space into independent blocks. Our block-argmax is what you
get if you shatter SDM's global radius into K independent per-block radii — you keep sparsity
but destroy the cross-block, magnitude-graded, critical-distance resolution that makes SDM work.
The fix is to restore global competition while retaining enough block structure for binding.

---

## Concrete construction most likely to beat block-argmax (ranked)

The design tension is real and named: **SBC block structure buys clean bind/unbind; one-hot-per-
block is the resolution bottleneck.** Ranked so lower-risk first:

**#1 (do this regardless — closes the TRAINING gap, cheap, no code change):**
Soft-to-hard annealed training of the *current* block-argmax code. Replace hard per-block argmax
with **entmax / Gumbel-softmax per block at temperature T**, anneal T -> 0 over training, with a
**straight-through** estimator and a **listwise ranking distillation loss** (align code-overlap
ranking to BGE cosine ranking; e.g., InfoNCE over BGE top-neighbors) rather than pointwise MSE.
Rationale: the 0.20-vs-0.43 gap is the signature of a hard, high-variance quantizer that
gradient descent cannot climb through. **Reaching the existing 0.43 ceiling ALREADY clears the
0.35 target.** This is the single highest-expected-value, lowest-cost move.

**#2 (SBC-preserving ceiling lift, minimal algebra change): "thick-SBC" (top-m per block).**
Allow m active units per block (m ≈ 3-4, signed/ternary) instead of one-hot. Raises per-block
resolution from 1-of-L (rank-only) to graded m-of-L, and — critically — the code set becomes a
**strict superset** of block-argmax, so its ceiling is provably >= 0.43 (superset argument
below). Binding stays block-local (bind an m-sparse block via convolution; unbind reads the
m-sparse filler). Lowest-risk way to lift the ceiling while keeping SBC algebra.

**#3 (biggest ceiling lift, needs binding redesign): DenseFly-style global WTA on sparse
expansion.** Project BGE 1024d -> expanded D' (D' = 8192-16384, 8-16x) via sparse random (or
learned) projection; take **GLOBAL top-K** (K = 0.02 D') winners across the whole vector, ternary
(keep sign). Similarity = sparse-code overlap/dot. Train with straight-through global top-K +
ranking loss. This is where FlyHash's "m-times more pairwise orders" resolution comes from
(expansion factor m + global competition). Binding no longer block-local: use a sparse-VSA
binding scheme over the global support — context-dependent thinning (Rachkovskij-Kussul) or
sparse-block binding on a *coarse* residual block partition (hybrid: fine global support for
retrieval resolution, coarse block tags for binding). Highest ceiling, highest integration cost.

**Recommendation:** ship #1 immediately (it alone likely clears 0.35 by reaching 0.43); pre-reg
#2 as the ceiling-lift arm (SBC-safe); hold #3 as the high-headroom arm if #1+#2 stall or if the
target is later raised well above 0.43.

### Superset argument (near-proof the ceiling MUST rise)

Block-argmax is the special case of both thick-SBC (m=1) and global top-K (with the added
constraint "exactly one winner per predefined block"). The feasible code set of thick-SBC and of
global top-K each *contains* every block-argmax code plus many others. Therefore
`code_ceiling(thick-SBC) >= code_ceiling(global-topK-with-block-cap) >= code_ceiling(block-argmax) = 0.43`,
with equality only in the measure-zero case that the optimal support happens to be exactly
one-per-block. The ceiling rises by construction; FlyHash theory says the rise is large
(multiplicative in expansion), not marginal.

---

## Honest scope + calibration

STRONG (established literature, direct transfer):
- Block-argmax = WTAHash = local WTA; FlyHash (global WTA) encodes ~m-times more pairwise orders
  at equal sparsity (Dasgupta-Stevens-Navlakha 2017; Sharma-Navlakha 2018). Established.
- SDM critical-distance resolution amplification from a *global* threshold (Kanerva 1988).
- Willshaw ln2 capacity: 2% sparse binary is information-rich (classical).
- SDR overlap = high-resolution similarity proxy (Numenta). Established.
- Superset argument (ceiling monotonic under constraint relaxation): a proof, not a heuristic.

MODERATE:
- That closing the training gap via soft-to-hard anneal reaches ~0.43 on *our* distillation
  regime specifically (standard trick, but our exact loss/data uncharted).

SPECULATIVE (calibration-capped):
- Exact magnitude of the ceiling lift for thick-SBC / DenseFly on our BGE distillation at our N
  and metric — must be measured; not directly precedented at our config.

**P (deflated):** The pure *ceiling-lift* sub-claim (global-WTA / thick-SBC ceiling > 0.43 and
clears 0.35 with room) rests on the superset proof + FlyHash: **P ~= 0.85**. The full *actionable*
claim — a fixed construction + soft-to-hard training achieves `ret_agree10 >= 0.35` — has two
largely-independent success paths (reach 0.43 at current code via anneal; OR lift the ceiling via
#2/#3). Naive lit-scan ~0.75; this is direct literature transfer (NOT novel synthesis, so no 0.50
cap), but our distillation regime is uncharted, so apply the standard 0.15-0.25 deflation:
**P_deflated ~= 0.60** that `ret_agree10 >= 0.35` is reached with construction #1 (and >0.35 with
comfortable margin once #2 is added).

Symmetric check (anti-negativity both ways): I am NOT inflating. The 0.43 ceiling is a verified
on-disk fact and the superset argument is airtight, so the *directional* claim ("should be
easier — yes") is high-confidence; the *quantitative* claim is where I deflate.

---

## Pre-reg smoke (cheap, decisive)

At current N, small corpus (~500 items), compute `ret_agree10` for THREE codes at matched ~2%
density on the SAME BGE targets, block-count-controlled:
- (i) block-argmax (baseline, expect ~0.43 ceiling with oracle assignment / ~0.20 trained);
- (ii) global top-K over the SAME 4096-d projection (no block partition), oracle assignment;
- (iii) thick-SBC m=3 (top-3 per block), oracle assignment.
HARD-PASS for the coding-theory claim: (ii) and/or (iii) ceiling > 0.43 by >= 5pp AND clears 0.35.
HARD-FAIL / falsify: (ii),(iii) ceilings <= 0.43 (would mean 2% sparsity, not local-WTA, is the
true limit — contradicts theory; investigate whether the projection itself is rank-deficient).
This is a pure encode/measure smoke (no training), so it isolates the CEILING question from the
training question and is CPU-cheap.

---

## Citations (generic, literature-only)

- Kanerva, P. (1988). Sparse Distributed Memory. MIT Press. [address decoder, critical distance]
- Willshaw, D., Buneman, O., Longuet-Higgins, H. (1969). Non-holographic associative memory.
  Nature. [sparse binary capacity ln2]
- Yagnik, J. et al. (2011). The Power of Comparative Reasoning (WTA hash). ICCV. [= block-argmax]
- Dasgupta, S., Stevens, C., Navlakha, S. (2017). A neural algorithm for a fundamental computing
  problem. Science 358(6364). [FlyHash: global WTA on sparse expansion]
- Sharma, J., Navlakha, S. (2018). Improving Similarity Search with the Fly. arXiv 1812.01844.
  [DenseFly; FlyHash encodes ~m x more pairwise orders than WTAHash]
- Frady, E.P., Kleyko, D., Sommer, F.T. (2021). Variable binding for sparse distributed
  representations. IEEE TNNLS. [Sparse Block Codes = our SBC algebra]
- Numenta (Ahmad, Hawkins). Properties of Sparse Distributed Representations. [overlap resolution]
- Ramsauer, H. et al. (2020). Hopfield Networks Is All You Need. ICLR 2021. [dense-WTA dual, beta
  = soft radius; supports soft-to-hard annealing rationale]

---

## Bottom line

Block-argmax = local WTA = WTAHash, a coding-theoretically low-resolution sparse code. Its 0.43
ceiling is the LOCAL-WTA penalty, not a 2%-density limit. Willshaw/SDM/SDR/FlyHash theory all say
a 2% sparse code carries ample resolution for `ret_agree10 >= 0.35`; the fix is to restore GLOBAL
competition (global top-K / thick-SBC, both strict supersets of block-argmax => provably higher
ceiling) and to close the training gap with soft-to-hard annealing + a ranking distillation loss.
USER's "should be easier" is correct: reaching even the *current* code's own 0.43 ceiling already
clears 0.35.
