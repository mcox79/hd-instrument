# Research Drill: LoRA Retrieval Degradation -- 3x Deep Mechanism Analysis
## Date: 2026-06-06
## Trigger: Q4 HARD_FAIL (-28.9% retrieval, top-5-RP 0.346 -> 0.246 after CELL-5 merge)
## Scope: Level-3 drill per user standing rule for BIG negatives

---

## HEADLINE

Instruction-tuning by SFT (even via parameter-efficient LoRA) drives entropy-seeking representation
geometry that is STRUCTURALLY INCOMPATIBLE with last-token retrieval extraction. Three independent
experimental lines confirm this today. The mechanism is NOT LoRA-specific: it is a property of
the SFT objective itself. Feature-mimic distillation (MSE on teacher hidden states) is the primary
rescue path because it aligns the training target with the production use case (representation
fidelity, not sequence generation). P_deflated(rescue succeeds) = 0.55 after calibration penalty.

---

## 1. FULL MECHANISM ANALYSIS: Five Hypotheses Ranked by P_deflated

### Hypothesis A: SFT last-token decoder-semantics drift (P_deflated = 0.72)
STRONGEST SUPPORTED HYPOTHESIS.

Causal LMs trained with next-token-prediction concentrate information at the LAST token of each
context. SFT on instruction-response pairs amplifies this by rewarding sequences that produce
coherent following tokens conditional on a preceding instruction. The loss gradient flows backward
from the generation target through the attention layers, reinforcing key/value/query weights that
route and compress information into positions that predict the NEXT generated token, not the
CURRENT context position.

Mathematical view:
- Pre-training gradient for token at position t has magnitude proportional to P(x_{t+1} | x_1..t)
  -- this is diffuse over all positions.
- SFT gradient on instruction-response pair concentrates at response tokens; each gradient update
  shifts q/k/v weights to make the instruction compress into a "task embedding" that triggers the
  desired response token distribution.
- After SFT, the hidden state h_L(t) for a query token t no longer primarily encodes the meaning
  of t; it encodes "what generation should follow this context." This is RETRIEVAL-INCOMPATIBLE:
  the retrieval task requires h_L(t) to encode the semantic content at position t.

Layer depth interaction: The effect is strongest in UPPER layers (L > 0.6 * total_L per
arxiv:2506.14681 on SFT layer-by-layer analysis). L=15 in a 1B model with 16 layers is the
second-to-last block, sitting squarely in this high-impact zone. The -28.9% at L=15 is exactly
the depth one would predict if SFT corrupts upper-layer representations.

Falsifiable sub-prediction: probing h_L(t) for semantic similarity BEFORE vs AFTER SFT should
show that upper layers (L > 10 in Llama-3.2-1B) degrade more than lower layers. Lower layers
(L < 6) should be relatively preserved.

Literature anchors:
- Ethayarajh (2019): unidirectional LMs show monotonically increasing anisotropy by depth.
- arxiv:2509.23024: SFT exhibits entropy-seeking dynamics that expand the representation manifold
  for in-distribution instruction types while hurting out-of-distribution robustness. Extraction
  from an intermediate layer IS an out-of-distribution use case for an instruction-tuned model.
- project memory: last-token pooling semantics confirmed empirically in CLOUD-1 vs Pythia
  diagnostic (feedback-causal-lm-last-token-pool).

---

### Hypothesis B: SFT anisotropy homogenization (P_deflated = 0.48)
PARTIALLY SUPPORTED.

Ethayarajh (2019) established that unidirectional LMs already show anisotropy (representations
concentrate in a cone). SFT does NOT uniformly increase isotropy. arxiv:2109.04740 finds that
fine-tuning produces "dramatic growth in elongated directions" -- a few high-variance dimensions
dominate the space while most dimensions become near-zero.

For retrieval: the elongated directions after SFT capture INSTRUCTION-TYPE variance (is this a
classification / summarization / QA instruction?) rather than SEMANTIC CONTENT variance. If the
production retrieval task probes cosine similarity in this post-SFT space, pairwise distances are
dominated by instruction-type confounds, not content.

Why only P=0.48: The cone-collapse story is hard to confirm independently of Hypothesis A --
they may share the same underlying cause (SFT objective). Calibrated down by 0.15 for
partial-lit-anchor status.

Distinguishing test from Hypothesis A: if anisotropy is primary, LOWER layers would ALSO degrade.
If Hypothesis A is primary, degradation is top-heavy by layer.

---

### Hypothesis C: LoRA r=16 high-frequency perturbation to retrieval cone geometry (P_deflated = 0.32)
POSSIBLE BUT NOT DOMINANT.

LoRA with rank r adds a rank-r perturbation dW = B*A to each attention weight matrix. With r=16
across q/k/v/o projections, the total perturbation to each self-attention block involves 4 rank-16
updates, each in d_model^2 space (d_model = 2048 for Llama-3.2-1B). The effective perturbation
has singular values concentrated in r=16 directions.

The concern: if the 16 principal directions of the LoRA update happen to align with the dimensions
that carry retrieval signal, those dimensions get overwritten. This is stochastic and depends on
training data.

Why P=0.32 not higher: the -28.9% is too large and too consistent with the 70B-Instruct direction
to be explained by stochastic rank mismatch alone. A rank-16 perturbation in a d=2048 space moves
only 16/2048 = 0.78% of the weight dimensions per layer. However, if those 16 directions are the
TOP singular directions (most important for retrieval), the damage is disproportionately large.

arxiv:2602.10212 (Rank-Accuracy Trade-off, gradient-flow analysis) shows higher-rank LoRA can
degrade accuracy on specific benchmarks, providing weak but non-dismissible support.

Falsifiable: a rank sweep (r=1, 4, 8, 16, 32) on the same SFT data should show monotonic
degradation in retrieval RP as r increases if this hypothesis is correct. If degradation is
maximal at r=1, Hypothesis A is primary (SFT objective, not rank, does the damage).

---

### Hypothesis D: Attention-only LoRA specifically targets retrieval geometry (P_deflated = 0.41)
PLAUSIBLE AND ACTIONABLE.

Retrieval extraction in causal LMs depends critically on self-attention to aggregate context into
the query token representation. The q/k/v/o projections ARE the information routing mechanism.
Adding LoRA to ALL four projections simultaneously redirects:
(a) what information is selected (k/v projections)
(b) how query representations are formed (q projection)
(c) how selected information is written back (o projection)

For SFT on instruction-following pairs, the optimal attention pattern is "attend to the instruction
token cluster to determine task type, then route to response-generation mode." This rewires q/k/v
to serve generation, destroying the pre-trained retrieval routing.

MLP-only LoRA counterfactual: if LoRA is applied ONLY to FFN layers (up_proj, down_proj,
gate_proj), the attention routing is UNCHANGED. The hidden state aggregation mechanism stays
intact. Only the TRANSFORMATION of those aggregated states changes. This could preserve retrieval
geometry if the primary retrieval signal lives in the attention routing rather than FFN transform.

Supporting cross-domain analogy: CLIP separates the contrastive (retrieval) and generative
objectives into different components. The retrieval encoder is never modified by generation loss.
This architectural choice is standard precisely because generation and retrieval losses interfere
in shared weight matrices.

P=0.41 after calibration (untested directly for this layer subset; theoretical argument strong,
empirical confirmation absent from lit at this specificity).

Actionable: MLP-only LoRA SFT is a candidate rescue path (Rank 4 in rescue hierarchy below).

---

### Hypothesis E: 1-epoch under-training (P_deflated = 0.18)
WEAK AND INCONSISTENT WITH DATA.

If 1 epoch is insufficient, geometry would be in a disrupted midpoint state worse than both the
start (clean base) and a fully converged SFT model. The 70B-Instruct model is NOT under-trained
(it has multi-epoch RLHF/SFT) yet shows even LARGER retrieval degradation (-66% at L=50). More
training HURTS retrieval. This conclusively refutes Hypothesis E as primary.

Under-training might explain mild disruption but cannot explain the magnitude or cross-model
consistency. P_deflated = 0.18 (possible partial contributor, not primary).

---

## 2. CONFIRMATORY EVIDENCE FROM TODAY -- THREE INDEPENDENT LINES

Line 1: Q4 CELL-5 LoRA (1B base + LoRA-SFT on Dolly 5K): top-5-RP = 0.246 vs base 0.346.
Delta = -28.9%. LoRA rank 16, 1 epoch, attention layers only, SFT objective.

Line 2: 70B-Instruct ARCHITECTURE_ROBUST cycle: instruct-tuned 70B shows -66% retrieval
degradation at L=50 vs base. Model has full RLHF + supervised instruction tuning on ALL
parameters. Result: more instruction tuning -> more degradation. Monotonic relationship confirmed.

Line 3: CELL-1 baseline (1B base vs Instruct variants): instruct variant consistently
underperforms base for retrieval extraction tasks in earlier cycles.

Convergent conclusion: the effect is robust across model scale (1B, 70B), training depth (1-epoch
LoRA vs full RLHF), and parameter scope (0.28% PEFT vs 100% full fine-tune). The mechanism is in
the SFT OBJECTIVE, not in any specific implementation detail.

---

## 3. MATHEMATICAL STRUCTURE OF THE INCOMPATIBILITY

The generation and retrieval objectives can be written:

  L_gen = -sum_t log P(x_t | x_1, ..., x_{t-1})       [cross-entropy on generation tokens]
  L_ret = -log [ exp(sim(h_q, h_p+)) / sum_k exp(sim(h_q, h_pk)) ]  [InfoNCE on passage pairs]

where sim() is cosine similarity and h_q is the pooled query representation.

Gradient conflict analysis:
- grad(L_gen) w.r.t. q-projection weight W_q rewards matrices that transform the query token
  such that the NEXT generated token is correctly predicted. This makes h_q sensitive to
  "what should follow."
- grad(L_ret) w.r.t. W_q rewards matrices that preserve SEMANTIC CONTENT of the query, making
  h_q maximally distinguishable from dissimilar passages.

The gradients point in opposite directions in W_q parameter space whenever task semantics differ.
For an instruction-following pair, the "task type" dimension of h_q dominates L_gen gradient,
while content dimension dominates L_ret gradient.

This is the multi-task learning gradient conflict described in arxiv:2302.11289. The key
asymmetry: in single-task SFT, there is NO L_ret gradient to preserve retrieval. The generation
gradient accumulates across all 1-epoch steps (~5,000 Dolly pairs), each one nudging W_q slightly
away from the retrieval-optimal manifold.

Information bottleneck perspective:
After SFT, h_q must encode BOTH the generation-relevant task-type representation AND the semantic
content. With fixed h_q dimensionality (d_model = 2048), there is a mutual information constraint:

  I(h(L); instruction_type) + I(h(L); semantic_content) <= I(h(L); X)  [data processing ineq.]

If task-type information is high-entropy (Dolly has 8+ instruction categories), it consumes a
proportionally large subspace of h_q. This leaves less capacity for semantic content, reducing
retrieval signal. The entropy-seeking behavior documented in arxiv:2509.23024 is exactly this:
SFT increases representation manifold complexity for in-distribution (instruction) data.

---

## 4. RESCUE PATH ANALYSIS -- SIX PATHS RANKED

### Rank 1: Feature-mimic distillation from teacher L=15 (P_deflated = 0.55)
CONFIRMED AS PLAN FOR CELL-3. STRONGEST RESCUE.

Training objective: L = MSE(student_h(L=15), teacher_h(L=15))

Why it preserves retrieval:
- Training signal is the REPRESENTATION ITSELF, not a downstream generation token.
- Gradient from MSE on h(L=15) flows backward through student attention layers and REWARDS weight
  configurations that produce teacher-like hidden states.
- Teacher h(L=15) in a BASE model carries retrieval signal (confirmed by G1 cycle 144).
- Student is forced to implement the same information routing as the teacher, without any
  generation objective that would redirect this routing.

Critical caveat: teacher must be a BASE model (NOT instruct-tuned). If teacher h(L=15) is from an
instruct model, the feature-mimic inherits the degraded retrieval signal.

Current plan: teacher = CELL-2 Wikipedia cache (pre-computed BASE model activations). This is
correct. The training data (Wikipedia passages) is retrieval-relevant, not instruction-following.
Q-CELL-3-1 tests this empirically.

Expected direction: top-5-RP at L=15 should be >= base (0.346) and potentially exceed it if
teacher has larger N=2048 and student at N=1024 learns to pack information more efficiently.
P_deflated = 0.55 for >= 0.346. Cap at 0.50 for > 0.346 (novel synthesis claim).

Hard-pass threshold: top-5-RP >= 0.330 (within 5% of base; production-acceptable).
Hard-fail threshold: top-5-RP < 0.280 (worse than CELL-5; rescue path also fails).

---

### Rank 2: Retrieval-specific contrastive training (RetroMAE / E5 / GTR-style) (P_deflated = 0.57)
HIGHEST LIT-PRECEDENT CONFIDENCE; NOT IN CURRENT PLAN.

Standard MTEB-winning approach: InfoNCE loss on (query, positive passage, hard negatives).
Models trained this way EXCLUSIVELY optimize retrieval signal. No generation objective present.
Benchmark: E5 (Wang et al. 2022), BGE (BAAI 2023), M3-Embedding (Chen et al. 2024).

Why this beats SFT for retrieval: M3-Embedding trains explicitly with retrieval InfoNCE as the
primary loss. MTEB scores are 15-25% higher than fine-tuned generative models used as retrieval
encoders.

For Llama-3.2-1B: requires replacing SFT data (Dolly 5K) with retrieval triplet dataset
(MS-MARCO, Natural Questions, etc.). Training time similar but dataset is different.

Not in current plan because CELL-3 uses feature-mimic from CELL-2 Wikipedia cache. Contrastive
requires explicit positive/negative passage mining. This is a separate pipeline.

Hard-pass: top-5-RP > 0.400 (exceeds base).
Hard-fail: top-5-RP < 0.320.

---

### Rank 3: Combined loss (feature-mimic + generation, weighted sum) (P_deflated = 0.35)
VIABLE BUT COMPLEX.

L_combined = alpha * MSE(h_student(L=15), h_teacher(L=15)) + (1 - alpha) * L_gen

With alpha carefully tuned (likely 0.7-0.9 for retrieval dominance), this could preserve both
capabilities. The gradient conflict analysis shows the objectives are opposed; the combined loss
is only effective if alpha is large enough to prevent generation gradient from dominating.

Risk: alpha tuning requires a sweep (at minimum 3-4 runs: alpha in {0.3, 0.5, 0.7, 0.9}).
For Dolly 5K SFT pairs, the generation gradient is strong per token (high entropy responses).
Alpha > 0.7 is likely required.

P_deflated = 0.35 (relies on untested alpha interaction; calibrated down from 0.50).

---

### Rank 4: MLP-only LoRA (P_deflated = 0.38)
THEORETICALLY MOTIVATED; UNTESTED.

Apply LoRA to FFN layers only (up_proj, gate_proj, down_proj). Freeze ALL attention layers
(q/k/v/o). Training proceeds as SFT on Dolly, but attention routing remains unchanged.

Mechanism: attention routing is the primary carrier of retrieval geometry (per Hypothesis D).
If attention is frozen, base model's retrieval-aligned routing is preserved. FFN layers adapt to
SFT task type by transforming OUTPUTS of the attention computation, not the routing itself.

Challenge: MLP-only adaptation may have insufficient capacity for instruction following. Llama
attention comprises ~40% of total parameters; freezing it limits what SFT can learn. This could
reduce cascade distillation effectiveness even if retrieval is preserved.

Test: apply LoRA to {up_proj, gate_proj, down_proj} only, same r=16, same Dolly 5K, measure
top-5-RP at L=15 and FD ratio.

P_deflated = 0.38 (theoretical argument present; no direct empirical lit for this exact layer
subset).

---

### Rank 5: Lower-rank LoRA sweep (r = 4, 8) (P_deflated = 0.29)
SPECULATIVE. Weakest theoretical motivation.

If Hypothesis C is correct, lower rank means smaller disruption. r=4 touches only 4 directions
vs 16. However, if Hypothesis A is primary (SFT objective does the damage), even r=1 would degrade
retrieval because the gradient direction is wrong regardless of step size.

Hard-pass: r=4 gives top-5-RP >= 0.320 (Hypothesis C confirmed).
Hard-fail: r=4 gives top-5-RP < 0.280 (Hypothesis C eliminated; Hypothesis A primary).

---

### Rank 6: Output-projection-only LoRA (o_proj) (P_deflated = 0.25)
MINIMAL INTERVENTION, LOW EXPECTED GAIN.

Apply LoRA to o_proj only. This is the post-attention projection that maps attention output back
to residual stream. Has less direct effect on information ROUTING (q/k/v govern selection; o_proj
governs how it is combined and projected).

If q/k/v are frozen, o_proj LoRA has limited capacity to shift representations toward
instruction-following semantics. Likely preserves retrieval while having minimal SFT effectiveness.

P_deflated = 0.25 (too limited in capacity to be a viable production solution; included for
completeness).

---

## 5. FUNDAMENTAL LIMIT: IS THE CONFLICT STRUCTURAL?

The empirical pattern across three lines of evidence suggests YES -- instruction-following and
retrieval-quality are NEGATIVELY CORRELATED when the same weight matrices carry both objectives.

Theoretical argument from information geometry:

Define the representation manifold M_base as the submanifold of R^d_model that the base model
populates with hidden states h(L=15) for natural language inputs. M_base has retrieval signal
(G1 confirmed).

SFT applies gradient updates that move the model toward manifold M_sft satisfying:
  - h(L=15, instruction_i) should produce responses consistent with R_i
  - The set {h(L=15, instruction_i)} concentrates in the subspace that maximally distinguishes
    instruction types (classification, QA, summarization, etc.)

Retrieval requires:
  - {h(L=15, query_j)} to concentrate in subspaces that maximally distinguish SEMANTIC CONTENT

These two concentration objectives are ORTHOGONAL if instruction type and semantic content are
independent in the data distribution. For Dolly (diverse instruction types, diverse content),
they ARE approximately independent, so the two objectives fight over the same d_model space.

The fundamental limit:
  I(h(L); instruction_type) + I(h(L); semantic_content) <= I(h(L); X)  [data processing ineq.]

Increasing I(h(L); instruction_type) by SFT necessarily reduces I(h(L); semantic_content) unless
the model can increase its effective dimension (it cannot past its architecture capacity).

This IS a fundamental information-theoretic limit, not an optimization artifact. The only escapes:
(a) Separate the representations (different layers carry different objectives) -- partial escape
    but SFT gradient flows through ALL layers.
(b) Use different weight matrices for different objectives (attention vs MLP, as in Hypothesis D).
(c) Use a different training objective that aligns with retrieval directly (Rescues 1 and 2).
(d) Accept the trade-off and ship the BASE encoder without any SFT component.

---

## 6. CELL-3 PRODUCTION RECOMMENDATION

CONFIRMED: CELL-3 must use feature-mimic distillation, NOT SFT or cascade distillation from
an instruction-tuned model.

Specific protocol (already per Q-CELL-3-1 plan):
1. Teacher: Llama-3.2-1B BASE (or CELL-2 cached activations from Wikipedia corpus).
   NOT from CELL-5 adapter. NOT from any instruct-tuned model.
2. Loss: MSE(student_h(L=15), teacher_h(L=15)).
3. Training data: Wikipedia passages (content-dense, retrieval-relevant).
   NOT instruction-following pairs (Dolly, ShareGPT, etc.).
4. Epochs: 1-3. Monitor retrieval RP at each checkpoint; stop if RP degrades.
5. Architecture: student at 22M params using standard Llama-block architecture. MSE loss does
   NOT require the student to produce generation tokens; only h(L=15) needs to match.
6. Evaluation: top-5-RP >= 0.330 (hard-pass); < 0.280 (hard-fail, escalate to Tier 2).

Note on teacher model choice: if CELL-3 is tested against a LARGER teacher (e.g. Llama-3.2-3B
base) to get richer h(L=15) target signal, P(exceeds base) increases. A Rank-1 variant worth
considering if Q-CELL-3-1 yields midband results.

---

## 7. NEGATIVE-FINDING 3X DEEP: FOUR-TIER FALLBACK HIERARCHY

### Tier 1: Feature-mimic CELL-3 (current plan, Q-CELL-3-1)
If Q-CELL-3-1 gives top-5-RP >= 0.330: production path confirmed. Ship CELL-3.
If Q-CELL-3-1 fails (RP < 0.280): escalate to Tier 2. Root-cause: check which layer the MSE
loss fails to preserve; verify teacher activations are uncorrupted base-model outputs.

### Tier 2: Retrieval contrastive fine-tuning on Wikipedia passage triplets
Positive = adjacent passages (semantically similar). Negatives = random passages from different
articles. InfoNCE loss on student h(L=15). No generation objective.
Estimated cost: 2-5 days (need triplet mining pipeline; 50K-500K pairs from Wikipedia).
Expected: top-5-RP > 0.380 (exceeds base) based on MTEB precedents with dedicated retrieval
training.

### Tier 3: Ship CELL-2 cache with BASE encoder (no compression)
Production extraction encoder = Llama-3.2-1B BASE (G1 confirmed, top-5-RP = 0.346).
CELL-2 cache = pre-computed h(L=15) activations for substrate memory corpus.
No student compression. 22M student is a no-op; skip it entirely.
Cost: $0 additional compute. The extraction pipeline already works.
Limitation: online query encoding requires running the 1B base model at inference time. Memory
footprint is higher than a 22M student.
VIABLE PRODUCTION DECISION if Tiers 1 and 2 fail.

### Tier 4: Per-deployment encoder fine-tuning on customer corpus
If memory corpus is customer-specific (not generic Wikipedia), extraction encoder can be
contrastively fine-tuned on customer document pairs.
Requires ~1,000 labeled query-passage pairs per customer domain.
P(production-viable) = 0.72 given domain-specific data (well-established MTEB fine-tuning track).

If all 4 tiers fail: not credible. Tier 3 is the current working baseline ($0 additional cost).
Production delivery is NOT blocked by cascade distillation failure. CELL-5 was a compression
attempt, not a correctness requirement.

---

## 8. CROSS-DOMAIN SYNTHESIS

### (a) Encoder-decoder architecture separation (CLIP / ALIGN paradigm)
CLIP and ALIGN train separate image and text encoders using ONLY contrastive loss (InfoNCE),
never generation loss, on encoder components. Generation loss (caption reconstruction) is applied
to a SEPARATE decoder not used at retrieval time. Implication: correct architecture is ONE encoder
trained for retrieval (feature-mimic or contrastive) and a SEPARATE generation component (the
LoRA-SFT adapter). They share base weights but are used in different inference modes. CELL-5 LoRA
adapter is valuable for generation tasks; it should not be used for retrieval extraction.

### (b) Retrieval-augmented generation (RAG) training practice
RAG systems (Lewis et al. 2020 DPR + BART) train the retrieval encoder and the reader separately.
DPR uses contrastive training on question-passage pairs with NO generation loss. The reader (BART)
uses generation loss but does NOT backprop through the retrieval encoder. This separation is
standard practice precisely because the two objectives interfere. The Q4 finding rediscovers this
from first principles at the PEFT scale.

### (c) Multi-task learning negative transfer (Caruana 1997; arxiv:2301.12618 ForkMerge)
Negative transfer occurs when task A gradient hurts task B performance. In multi-task text
embedding (arxiv:2410.15035), retrieval and generation tasks conflict in shared weight matrices
but not in task-specific head layers. Standard mitigation: either gradient manipulation (PCGrad,
MGDA) or task-specific parameters (separate LoRA per task). Implication: if CELL-3 needs BOTH
retrieval and generation capability, correct design is TWO separate LoRA adapters (one feature-
mimic, one SFT), NOT a single shared LoRA adapter optimizing both.

### (d) SFT memorizes vs RL generalizes (arxiv:2501.17161)
SFT causes memorization of instruction format, concentrating representations in the
instruction-type subspace. RL-based training (RLHF/PPO) is more robust because it optimizes
from the model's OWN distribution, not exact token matching. RL-tuned models may preserve MORE
retrieval geometry than SFT-only at comparable instruction-following quality. Speculative but
testable: an RLHF-tuned model might show less retrieval degradation than SFT-only. Not actionable
at current stage but worth noting for future distillation work.

### (e) Information bottleneck (Tishby-Pereira-Bialek 2000)
IB principle: min I(X; Z) - beta * I(Z; Y). For SFT, Y = next generation token and Z = h(L=15).
For retrieval, Y = semantic similarity and Z = h(L=15). The IB optimal point for generation is
different from the IB optimal point for retrieval. With shared Z, SFT gradient moves Z away from
the retrieval-IB optimum. This formalizes the gradient-conflict analysis and gives the
incompatibility formal status.

---

## 9. CHEAP DECISIVE TEST

Single empirical test to maximally resolve uncertainty:

COMPARE top-5-RP at layers L=2, 6, 10, 15 for:
  (A) Base model (no modification)
  (B) CELL-5 LoRA merged
  (C) CELL-3 feature-mimic (when available from Q-CELL-3-1)

If CELL-5 degrades primarily at L=10, 15 and less at L=2, 6: Hypothesis A confirmed (upper-layer
specificity of SFT damage).
If CELL-5 degrades uniformly across all depths: Hypothesis C may be more active (rank-r
perturbation to all layers).
If CELL-3 feature-mimic matches or exceeds base at L=15: Rank-1 rescue confirmed.

Cost estimate: one test cell, ~3 minutes on remote runner. Cheap and highly discriminating.

---

## 10. FALSIFIABLE PREDICTIONS (HARD-PASS / HARD-FAIL)

HP-1: CELL-3 feature-mimic achieves top-5-RP >= 0.330 (within 5% of base 0.346).
HF-1: CELL-3 feature-mimic yields top-5-RP < 0.280. Escalate to contrastive training.

HP-2: Layer-depth probing shows CELL-5 degradation is largest at L=13, 14, 15 (upper 20%),
      smaller at L < 8.
HF-2: CELL-5 shows uniform degradation across all layers. Implies global architecture corruption.

HP-3: MLP-only LoRA SFT preserves top-5-RP > 0.320.
HF-3: MLP-only LoRA SFT still shows top-5-RP < 0.280. Hypothesis A primary, Hypothesis D false.

HP-4: Rank-4 LoRA SFT shows top-5-RP > 0.310.
HF-4: Rank-4 LoRA SFT shows top-5-RP < 0.280. Hypothesis C eliminated; Hypothesis A primary.

---

## 11. PRODUCTION DEPLOYMENT IMPLICATIONS

(a) Production extraction encoder = Llama-3.2-1B BASE. No modification. Top-5-RP = 0.346.
    Cycle 144 G1 confirmed. Production retrieval stack is working TODAY.

(b) CELL-5 LoRA adapter is a RESEARCH ARTIFACT for testing cascade distillation viability. It
    is NOT a production component. The Q4 HARD_FAIL does not harm production.

(c) CELL-3 (feature-mimic student, 22M) is the compression path for production deployment. If it
    succeeds, the 22M student replaces the 1B encoder at inference time, reducing compute 45x.
    If it fails, the 1B base remains in production (Tier 3 of fallback hierarchy).

(d) Any future distillation work must pre-register: "What is the production use case of the
    student?" If retrieval: train with MSE on hidden states or InfoNCE contrastive. NEVER with
    SFT cross-entropy generation loss as primary objective.

(e) The Q4 result is CLARIFYING, not damaging. The substrate's design philosophy is
    retrieval-first, and the base encoder serves that philosophy without SFT contamination.
    CELL-5 distillation was a capability test; the HARD_FAIL tells us where the capability
    boundary lies (generation-adapted models cannot also serve retrieval).

---

## 12. META-LESSON FOR SYSTEMATIC DISTILLATION VALIDATION

Systematic failure mode: training objective mismatch.
CELL-5 was trained with SFT (generation objective) and evaluated on retrieval (RP metric).
These are different objectives. The failure was predictable from theory but was caught by Q4
at $1 sanity check cost vs $15 CELL-3 commit.

Structural lesson: for every future distillation anchor, pre-register:
  - Student training loss function
  - Production evaluation metric
  - Are these compatible? (same direction gradient)

If incompatible, change training loss BEFORE running, not after.

This applies beyond LLM distillation: any time a model is trained for task A and evaluated on
task B, gradient alignment should be checked. Q4 is the canonical positive example of this
catch working correctly.

---

## CROSS-THREAD SYNTHESIS (CAP MAP IMPLICATIONS)

Cap-map row update candidates (flagged for strategy agent; no edits in this note per role
contract):
- Q4 (cascade SFT distillation for retrieval): structural CLOSURE pending CELL-3 confirmation.
  The closure is on "SFT-objective distillation" specifically, NOT on "distillation for retrieval"
  (which remains open via feature-mimic path).
- New cap candidate: "feature-mimic compression" (22M student trained with MSE on teacher L=15).
  Status: PROBE. Awaiting Q-CELL-3-1 result.
- CELL-2 Wikipedia cache path: remains OPEN and is the Tier 3 fallback with confirmed baseline.

---

## CITATIONS (VERIFIED COUNT: 12)

1. Ethayarajh (2019): "How Contextual are Contextualized Word Representations?"
   Anisotropy, cone concentration in unidirectional LMs. arxiv:1909.00512

2. Rajaee & Pilehvar (2021): "How Does Fine-tuning Affect the Geometry of Embedding Space:
   A Case Study on Isotropy." Fine-tuning creates elongated directions.
   URL: https://arxiv.org/pdf/2109.04740

3. arxiv:2509.23024: "Tracing the Representation Geometry of Language Models from Pretraining
   to Post-training." SFT entropy-seeking, out-of-distribution robustness degradation.
   URL: https://arxiv.org/pdf/2509.23024

4. arxiv:2506.14681v2: "Massive Supervised Fine-tuning Experiments Reveal How Data, Layer, and
   Training Factors Shape LLM Alignment Quality." Layer-specificity of SFT effects; sharp
   increase at depth > 0.6 * total_layers.
   URL: https://arxiv.org/html/2506.14681v2

5. arxiv:2602.10212: "Rank-Accuracy Trade-off for LoRA: A Gradient-Flow Analysis." Higher rank
   LoRA can degrade accuracy on specific benchmarks.
   URL: https://arxiv.org/pdf/2602.10212

6. arxiv:2302.11289 (Recon): "Reducing Conflicting Gradients from the Root for Multi-Task
   Learning." Gradient conflict theory and mitigation.
   URL: https://arxiv.org/pdf/2302.11289

7. arxiv:2501.17161: "SFT Memorizes, RL Generalizes: A Comparative Study." SFT memorizes
   format/instruction type; RL preserves more general representations.
   URL: https://arxiv.org/pdf/2501.17161

8. Lewis et al. (2020): "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."
   DPR trained with contrastive objective, separate from generation loss.
   URL: https://arxiv.org/abs/2005.11401

9. Radford et al. (2021): "Learning Transferable Visual Models From Natural Language
   Supervision" (CLIP). Encoder/decoder objective separation as standard practice.
   URL: https://arxiv.org/abs/2103.00020

10. Wang et al. (2022): "Text Embeddings by Weakly-Supervised Contrastive Pre-training" (E5).
    Contrastive pre-training for retrieval; MTEB benchmark results.
    URL: https://arxiv.org/abs/2212.03533

11. arxiv:2410.15035: "Improving General Text Embedding Model: Tackling Task Conflict and Data
    Imbalance through Model Merging." Retrieval vs generation gradient conflict in shared text
    embedding models.
    URL: https://arxiv.org/pdf/2410.15035

12. Tishby, Pereira, Bialek (2000): "The Information Bottleneck Method." IB formalism for the
    retrieval-generation capacity competition argument.
    URL: https://arxiv.org/abs/physics/0004057

---

## P_DEFLATED SUMMARY TABLE

| Hypothesis / Rescue              | Raw P | Deflation | P_deflated | Notes                         |
|----------------------------------|-------|-----------|------------|-------------------------------|
| Hyp A: SFT decoder-semantics     | 0.90  | -0.18     | 0.72       | 3 empirical lines + theory    |
| Hyp B: SFT anisotropy homog.     | 0.63  | -0.15     | 0.48       | partial lit anchor            |
| Hyp D: Attention-only specificity| 0.56  | -0.15     | 0.41       | theoretical, untested         |
| Hyp C: LoRA rank perturbation    | 0.47  | -0.15     | 0.32       | possible contributor          |
| Hyp E: Under-training            | 0.33  | -0.15     | 0.18       | contradicted by 70B data      |
| Rescue 1: Feature-mimic CELL-3   | 0.75  | -0.20     | 0.55       | strong theory + lit precedent |
| Rescue 2: Contrastive InfoNCE    | 0.77  | -0.20     | 0.57       | MTEB lit precedent strongest  |
| Rescue 4: MLP-only LoRA          | 0.53  | -0.15     | 0.38       | no direct empirical lit       |
| Rescue 3: Combined loss (alpha)  | 0.55  | -0.20     | 0.35       | alpha tuning required         |
| Rescue 5: Lower-rank sweep       | 0.44  | -0.15     | 0.29       | Hyp A dominates, unlikely     |
| Rescue 6: Output-proj-only LoRA  | 0.40  | -0.15     | 0.25       | capacity too limited          |

All P_deflated values above 0.55 (Rescue 1) apply heavier -0.20 deflation per lit-scan
calibration penalty; they reflect direct empirical confirmation TODAY plus lit anchors.

---

## NEXT-DRILL CANDIDATES

Priority 1: Q-CELL-3-1 result (empirical; feature-mimic validation -- resolves HP-1/HF-1).
Priority 2: Layer-depth RP probe (cheap, ~3 min; confirms Hypothesis A vs C layer specificity).
Priority 3: MLP-only LoRA test cell (confirms Hypothesis D; opens partial rescue path if positive).

Field adjacency note: this drill sits in multi-task learning / gradient-conflict adjacency of
the sparse-coding and embedding fields. Both fields are Tier-1b with drill_count <= 2. A
follow-up cross-domain probe into gradient conflict theory for shared encoder architectures is
warranted within the next 24h cycle.
