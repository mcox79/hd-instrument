# Longshot capability map — what could explode the value

Drafted 2026-05-19 23:30. These are the BIG BETS — capabilities that, if they
turn out to work, would 10x-100x the substrate's value. They're not in the
current capability map because we haven't even framed the question yet.

Ranked by **value-if-it-works × technical credibility**. The user wants to
identify ALL longshots; this is v1.

---

## Tier S — paradigm-shift longshots ($10B+ if they work)

### 1. Compositional reasoning chains
**The bet**: substrate composes stored atoms to DERIVE new facts. Given
atoms for "Paris is in France" and "France is in Europe", substrate produces
"Paris is in Europe" by atom composition — not memorization, not retrieval.

**Why it would explode value**: this is symbolic-AI-grade reasoning grafted
onto a sub-symbolic substrate. Solves the LLM "reasoning vs memorization"
distinction. Closes the gap between LLMs and formal logic systems.

**What's the test**: train substrate on (A,B) and (B,C) pairs; query for
(A,C). Does substrate transitively close the relation?

**Credibility**: medium. BSC bipolar binding has known compositional structure
(Plate 1995). Resonator can decompose products. But chained inference across
multiple bundles is untested.

**Estimate**: 2-week build. ~$10B market if it works (AGI-adjacent).

### 2. Anti-hallucination engine via evidence-backing
**The bet**: every substrate prediction REQUIRES traceable evidence in the
pool. If no evidence, substrate refuses to answer. Hard guarantee: no
hallucinations, only "I don't know" or evidence-backed answer.

**Why it would explode value**: hallucination is THE blocker for LLM
enterprise adoption (healthcare, legal, finance). Every major lab is fighting
this; nobody has hard guarantees.

**What's the test**: train substrate on N facts. Query both known facts
(should answer with evidence) and held-out facts (should refuse). Measure
false-positive rate (substrate answers wrongly without evidence).

**Credibility**: high. Substrate's pool retrieval is already evidence-keyed.
Just need to add a confidence threshold and "refuse if below."

**Estimate**: 1-week build. $20B+ market (regulated industries).

### 3. Long-context emulation via pool at extreme scale
**The bet**: pool entries function as effectively-unbounded context. Where
transformers strangle at 100K-1M tokens (quadratic attention cost), substrate
can have 10M+ pool entries with linear retrieval cost.

**Why it would explode value**: defeats the context-length arms race entirely.
Every LLM company is investing billions in long-context architectures
(Mamba, MoR, hyena, etc.). Substrate would win by sidestepping it.

**What's the test**: build substrate with POOL_SIZE=10M. Measure retrieval
latency, accuracy, and effective context usage. Compare to transformer at
equivalent context length.

**Credibility**: medium-high. Pool retrieval is O(pool_size × N) which is
linear in both, very tractable. The question is whether N=4096 atoms can
discriminate among 10M entries (likely needs N=16K or sparse codes).

**Estimate**: 1-month build. $30B+ market.

---

## Tier A — game-changer longshots ($1B-$10B if they work)

### 4. Causal reasoning via interventional edits
**The bet**: edit an atom counterfactually (set X=value), measure downstream
predictions. Pearl-style do-calculus with auditable atoms.

**Why it would explode value**: causal AI is a $5B+ market with no LLM
solution. RCT-grade reasoning grafted onto a memory substrate.

**What's the test**: train substrate on dataset with known causal structure.
Edit "cause" atom. Measure if "effect" predictions update consistently with
ground-truth causal model.

**Credibility**: medium. The math of intervention via atom-swap is clean.
But generalization beyond the training distribution is unproven.

**Estimate**: 2-week build.

### 5. Cross-modal substrate (text + image + audio at atom level)
**The bet**: bind text atoms with image embeddings and audio embeddings.
Substrate stores cross-modal memories with audit on each modality
independently.

**Why it would explode value**: multimodal is the current frontier (GPT-4V,
Gemini, Claude Opus). HDC substrate at fraction of cost with full audit.

**What's the test**: bind CLIP image features with byte K-grams. Decompose
to recover both modalities. Query cross-modally.

**Credibility**: medium-high. HDC literature has cross-modal binding examples
(Karunaratne resonator memory). Just untested in our substrate.

**Estimate**: 1-month build.

### 6. Continual self-improvement during deployment
**The bet**: substrate updates ITS OWN concepts based on usage feedback.
Hebbian learning loop independent of training. Substrate gets smarter from
being used.

**Why it would explode value**: closes the deployment-staleness gap. Every
LLM today gets stale after training cutoff; substrate would be the first
"always learning" deployed AI.

**What's the test**: deploy substrate on stream of (query, ground-truth)
pairs. Measure performance over time. Without retraining, does it improve?

**Credibility**: high (Hebbian update is online). But self-correction loops
can also diverge (positive feedback to wrong predictions).

**Estimate**: 2-week build with safety constraints.

### 7. Energy efficiency at neuromorphic scale
**The bet**: Hebbian + sparse retrieval scales energy LINEARLY with N+pool.
Transformer attention scales QUADRATICALLY. At sufficient scale, substrate
is 100-1000x more energy efficient.

**Why it would explode value**: data center power is the binding constraint
on AI deployment. Anyone who solves energy wins enterprise. Worth $100B+.

**What's the test**: benchmark substrate energy use vs equivalent-capability
transformer on standardized workload. Need actual silicon measurement
(neuromorphic chip via Loihi/Akida).

**Credibility**: medium. Asymptotic argument is sound. But constants matter:
substrate may need N=16K which is bigger than expected. Also: real workloads
have many overhead costs.

**Estimate**: 3-month build (needs hardware partner). $100B+ market.

---

## Tier B — interesting longshots ($100M-$1B if they work)

### 8. Constitutional/policy guarantees via atom edits
**The bet**: substrate-stored "constitutional rules" that LITERALLY constrain
predictions via bundle structure — not soft RLHF, hard prohibitions.

**Why it matters**: regulators want hard guarantees. RLHF can be jailbroken;
atom-level prohibitions might be unbreakable.

**Test**: train substrate. Encode prohibition: "never output sequence X."
Adversarially probe for X. Measure leakage rate vs RLHF baseline.

**Estimate**: 2-week build.

### 9. Spiking neural network deployment (Loihi/Akida)
**The bet**: substrate's Hebbian + bipolar maps to spiking hardware. Could be
1000x more energy efficient than GPU inference.

**Why it matters**: ultra-low-power on-device AI (IoT, wearables, embedded).

**Test**: port substrate to Loihi 2 via NxSDK. Measure latency, power vs
GPU. Need Intel hardware partner.

**Estimate**: 6-month build (hardware integration).

### 10. Symbolic reasoning hybrid
**The bet**: substrate's atomic structure supports exact symbolic operations
alongside continuous learning. Hybrid neural/symbolic system.

**Why it matters**: neuro-symbolic has been "the future" for 30 years.
Substrate's auditable atoms might finally close the gap.

**Test**: encode a symbolic rule (e.g., "if X then Y") as a substrate edit.
Query Y given X. Measure consistency with symbolic logic.

**Estimate**: 1-month build.

### 11. Reversible / quantum-compatible computation
**The bet**: bipolar ±1 atoms map to quantum spin states. Substrate could
port to quantum hardware. Operations (sum-bundle, atom-multiply) are
reversible — exponentially more energy efficient at scale.

**Why it matters**: quantum AI is speculative but worth tracking.

**Test**: design substrate primitive in QASM. Run on IBM Q (1000 atoms max
with current hardware).

**Estimate**: 6-month exploration, mostly framework work.

---

## Tier C — wildcards / framework bets

### 12. Mode-vector / Hopfield-as-attention bridge
**The bet**: substrate's binding generalizes Hopfield attention (Ramsauer
2020 "Hopfield Networks Are All You Need"). Substrate becomes a drop-in
transformer replacement.

**Why it matters**: if true, substrate inherits all of transformer's
generality with auditability bonus.

**Test**: implement Hopfield-attention via substrate primitives. Run on a
standard transformer benchmark. Compare to attention-based baseline.

**Estimate**: 1-month build.

### 13. Hebbian replacement for backprop in specific layers
**The bet**: substrate's delta-rule could replace gradient descent for
memory layers, attention layers, embedding layers. Hybrid backprop+Hebbian
training where critical-path layers use Hebbian.

**Why it matters**: if even 30% of weights can be Hebbian-trained, that's
3x training cost reduction.

**Test**: ablate one layer of a transformer to Hebbian training. Measure
final loss vs full-backprop baseline.

**Estimate**: 2-week build.

### 14. Self-modeling / metacognition
**The bet**: substrate represents its OWN reasoning state in its pool.
Substrate can introspect: "why did I predict X?", "what's my confidence?"

**Why it matters**: AGI-adjacent. Most ambitious bet on the list.

**Test**: encode the substrate's own internal state into its pool. Query
substrate about its own predictions. Measure self-consistency.

**Estimate**: 6-month exploration.

---

## How to prioritize

**Highest value × highest credibility**: anti-hallucination engine (#2). Big
market, clean test, mostly already implementable with current substrate.

**Most distinctive technical bet**: long-context emulation via pool (#3).
Defeats the entire context-length arms race if scales hold.

**Smallest first test**: causal interventional edits (#4). Reuses our edit
primitive, just adds counterfactual probing.

**The product-aligned bet given compliance wedge**: anti-hallucination
engine (#2) PLUS constitutional guarantees (#8). Both directly serve the
compliance/regulator buyer profile from the converging research.

## What's NOT in this list (and why)

- **Generation quality matching GPT-4**: this is in the "killer functionality"
  Tier 1, not a longshot. Already framed.
- **Faster R10**: incremental, not paradigm-shift.
- **Better PPMI**: same — being tested via sparse coding now.
- **Larger N or K**: scaling, not longshot.

## Open question for user

Which of these would you want to actually TEST? Cost ranges from 1-week
(anti-hallucination engine) to 6-month (neuromorphic hardware port). Several
are testable with the existing substrate; some require new builds.

The compliance-product direction makes #2 (anti-hallucination) and #8
(constitutional guarantees) particularly synergistic with the wedge.
