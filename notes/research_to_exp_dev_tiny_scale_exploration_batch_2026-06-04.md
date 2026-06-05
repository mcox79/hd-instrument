# Research -> Exp-Dev: Tiny-scale exploration empirical batch (substrate capability design space)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Subject:** User strategic direction: "trying everything on this tiny scale so we can really explore the space before it gets much more time intensive." Empirical exploration of substrate's broader capability design space at substrate-class N=2048-8192 while iteration is cheap.

---

## Strategic frame

Today's bio-architecture program validated 9 bio-primitives at substrate-class. User now asks: **what HAVEN'T we tested at tiny scale?**

Substrate capabilities we've explored deeply:
- Capacity management (B1-B8; capacity-mgmt taxonomy)
- Training-speed (Stage A hybrid)
- Bio-architecture composition (B36 refuted; B26 pending; pure-bio combined pending)

Substrate capabilities UNDER-EXPLORED at tiny scale:
- **Substrate-direct language modeling** (no LLM hybrid; full bio-primitive stack at max capacity)
- **Substrate generation** (iterated retrieval for novel sequence generation, not just retrieval)
- **Substrate reasoning** (multi-hop inference; logical deduction; spatial)
- **Substrate multi-modal empirical** (CIFAR-10 patches; vision data)
- **Substrate numerical** (arithmetic; counting; mathematical reasoning)
- **Substrate at biological scale** (N=100k+; qualitative behavior changes)
- **Substrate self-modification** (substrate adjusts own primitives)
- **Multi-substrate communication** (peer-to-peer beyond hierarchical aggregator)

This batch tests EACH at tiny scale (~5-30 min CPU per cell) to explore the design space cheaply.

---

## Exploration empirical cells (8 cells; ~2-4h total CPU)

### Cell EX1: Substrate-direct LM with full bio-primitive stack

- N=8192; Wikitext-2 char-LM; V=70
- Architecture: DG sparse (f=0.02) + cf-RPE + B3b exp-smoothed surprise + position-binding + D-ECR eviction + 5-substrate hierarchical aggregator
- One-pass training + 10% replay phase (palimpsest decay alpha=0.003 + bounded W_max=6 per Lazaro 2025)
- Test: held-out Wikitext-2 perplexity
- **HARD-PASS:** substrate-direct perplexity < 20 (within 4x of Pythia-160M ~5-10)
- **MIDDLE:** perplexity 20-60 (better than bigram baseline ~30)
- **HARD-FAIL:** perplexity > 60 (worse than bigram; substrate-direct LM not viable)
- WHY-DRILL on HF: identify bottleneck primitive (capacity? context? gating?); per-primitive ablation
- Wall: ~30-60 min CPU
- P_deflated: 0.20 (challenging but well-grounded)

### Cell EX2: Substrate generative output via iterated retrieval

- N=4096; trained on Bundle E E1 trigram task; full bio-primitive stack
- Generation: iterated unbinding for K=8-16 tokens (per token: query → retrieve → re-inject as context)
- Measure: BLEU vs random baseline; sequence coherence
- **HARD-PASS:** BLEU > 2x random baseline AND coherent K=8+ generation
- **MIDDLE:** BLEU 1.2-2x; partial coherence K=4-8
- **HARD-FAIL:** BLEU ~= random; substrate cannot generate beyond stored patterns
- Wall: ~15-30 min CPU
- P_deflated: 0.30

### Cell EX3: Substrate multi-hop reasoning

- N=2048; simple chain task: A→B, B→C stored as bindings; query "A→?" should retrieve C via 2-hop
- Test: 5-class chain depth K=2 → K=3 → K=5; retrieval accuracy at increasing depth
- **HARD-PASS:** retrieval accuracy >= 80% at K=3; >= 60% at K=5
- **MIDDLE:** K=3 accuracy 50-80% OR K=2 only
- **HARD-FAIL:** K=2 accuracy < 80% (substrate cannot do basic chain reasoning)
- Wall: ~10-20 min CPU
- P_deflated: 0.35

### Cell EX4: Substrate multi-modal smoke (CIFAR-10 patches)

- N=4096; CIFAR-10 32x32 RGB → 4x4 patches → bipolar projection
- Test: classification accuracy on test set; 10 classes
- **HARD-PASS:** >= 25% accuracy (2.5x chance baseline; substrate VSA primitives transfer to vision)
- **MIDDLE:** 13-25% accuracy (some signal)
- **HARD-FAIL:** <= 13% accuracy (substrate-class capacity insufficient for vision)
- Wall: ~30-60 min CPU
- P_deflated: 0.21 (per earlier CIFAR-10 routing)
- Engineering note: needs CIFAR-10 loader (torchvision absent per Exp-Dev prior note; manual urllib download + unpickle)

### Cell EX5: Substrate at biological-brain scale N=100k

- N=100,000; one-shot Hebbian storage of M=1000 random patterns
- Test: retrieval accuracy + per-pattern energy + crosstalk
- **HARD-PASS:** retrieval > 90% at M=1000 AND no qualitative behavior change vs N=8192 baseline
- **MIDDLE:** retrieval 60-90% OR observe new behavior (e.g., partial saturation patterns)
- **HARD-FAIL:** retrieval < 60% (substrate breaks at biological scale; needs architectural revision)
- Wall: ~10-30 min CPU (~12.5GB matrix W; might exceed laptop RAM; if so reduce to N=50k)
- P_deflated: 0.50 (algebraic prediction is favorable; N scaling is well-understood)

### Cell EX6: Substrate for arithmetic

- N=2048; substrate stores arithmetic rules (V=10 digits + operations)
- Test: 2-digit addition retrieval (e.g., "5+3" → "8")
- Pre-train substrate on 100 random examples; test on held-out
- **HARD-PASS:** >= 70% accuracy on held-out 2-digit addition
- **MIDDLE:** 30-70%
- **HARD-FAIL:** < 30% (substrate cannot do arithmetic at this scale)
- Wall: ~10-20 min CPU
- P_deflated: 0.20 (substrate's algebraic substrate is not naturally numerical)

### Cell EX7: Substrate self-modifying sparsity

- N=4096; substrate stores patterns at multiple sparsity levels f={0.5, 0.1, 0.05, 0.02, 0.005}
- Substrate adjusts ITS OWN sparsity based on retrieval accuracy per region
- Test: after meta-learning phase, does substrate's chosen f outperform fixed f=0.05?
- **HARD-PASS:** adaptive f > best fixed f by >= 10%
- **MIDDLE:** adaptive ~= best fixed
- **HARD-FAIL:** adaptive worse than best fixed (self-modification adds noise)
- Wall: ~20-30 min CPU
- P_deflated: 0.25 (novel; meta-learning at substrate scale is exploratory)

### Cell EX8: 2-substrate peer-to-peer communication

- 2 substrates at N=2048 each; trained on overlapping but different corpora
- Communication protocol: substrate A queries substrate B for missing patterns; B returns top-K
- Test: does substrate A's effective knowledge improve via B's help?
- **HARD-PASS:** A's perplexity reduces by >= 10% via B's communication
- **MIDDLE:** 3-10% improvement
- **HARD-FAIL:** no measurable improvement
- Wall: ~20-30 min CPU
- P_deflated: 0.30

---

## Total budget

8 exploration cells x 3 seeds = 24 measurements. Per-cell wall 10-60 min CPU; aggregate ~2-4h CPU total.

Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU (all laptop-local).

Per [[feedback-small-scale-first-methodology]]: tiny-scale exploration BEFORE scaling up.

## Pre-reg discipline

Each cell has explicit HP/MID/HF + WHY-DRILL hooks. NO implicit PASS expectation. Per pressure-test methodology: HF triggers diagnostic before iteration.

Realistic outcome (P_average ~0.27): 2-3 of 8 HP; 3-4 MID; 1-2 HF with specific WHY-DRILL fix paths.

---

## Engineering bandwidth

You're CPU-drained per cycle 71. This batch fills the queue with HIGH-INFORMATION exploration work (not padding). Each cell discriminates a specific capability hypothesis.

Per [[feedback-no-padding-experiments]]: each cell tests a distinct substrate capability dimension. Not padding.

## Sequencing recommendation

Priority 1 (cheapest + most-informative; ~1-2h total):
- EX2 substrate generation (15-30 min)
- EX3 multi-hop reasoning (10-20 min)
- EX6 arithmetic (10-20 min)
- EX7 self-modifying sparsity (20-30 min)

Priority 2 (engineering-heavier; ~2-3h additional):
- EX1 substrate-direct LM full stack (30-60 min)
- EX4 CIFAR-10 multi-modal (30-60 min + CIFAR-10 loader engineering ~30 min)
- EX5 N=100k scale (10-30 min; RAM-check first)
- EX8 2-substrate communication (20-30 min)

Build at your pace; expect 4-8 hours engineering across all 8 cells.

---

## What this is

This is the **BREADTH EXPLORATION pass** at tiny scale. Per user direction: try everything cheap before iteration gets time-intensive at larger scale.

If 3+ exploration cells HP: substantial broadening of substrate's known capabilities at substrate-class scale. Validates substrate as multi-capability architecture, not single-capability primitive set.

If most HF: substrate's capabilities are CONCENTRATED in capacity/audit/retrieval; not generative/reasoning/multi-modal. Refines product narrative correctly.

Either way: SUBSTRATE'S CAPABILITY DESIGN SPACE EMPIRICALLY MAPPED at tiny scale.

---

## Standing 2x research authorization

Per user direction: 2x research drills authorized whenever warranted. I will dispatch drills as needed without further confirmation:
- WHY-DRILL on HF outcomes
- Algebraic deepening when mechanism is non-obvious
- Cross-domain probes when bio precedents converge
- Capability characterization when new HP unlocked

---

## ~20 min check rhythm

Per user: checking for new notes every 20 min. Will follow up promptly on any HF/HP/diagnostic requests.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF per cell
- Per [[feedback-no-padding-experiments]]: each cell discriminates distinct capability
- Per [[feedback-small-scale-first-methodology]]: tiny-scale BEFORE scaling
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- Per [[feedback-pressure-test-negative-findings]]: WHY-DRILL on HF per cell
- ASCII-only

PROT-018: anchors use `_ex<N>_v1` suffix
PROT-021: source=local CPU, run_mode=smoke (3 seeds)

---

**END.**

**Exp-Dev:** 8 exploration cells; ~2-4h CPU total; $0; expects 2-3 HP + 3-4 MID + 1-2 HF with diagnostic paths. Priority 1 cheapest first (EX2/EX3/EX6/EX7); Priority 2 heavier engineering. Build at your pace.

**Research session:** 2 broader-exploration drills in flight (substrate-direct LM 3x; unexplored capabilities 2x). Standing for those + this empirical batch + Phase 0.5 v1 Llama (~1.3h to npz) + composition tests (B26, Pure-bio combined) + B5-bounded + B8 Cell 4.

User direction acknowledged: explore design space at tiny scale BEFORE scaling. Standing 2x research auth. ~20 min check rhythm. Will respond promptly to all exp-dev notes.
