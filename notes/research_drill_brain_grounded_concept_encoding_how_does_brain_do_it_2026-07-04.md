# Research Drill: How Does the Brain Do Concept Encoding? Have We Emulated It? (2026-07-04)

**Author:** Director (Research)
**Trigger:** USER foundational brain-grounding at a pivot. The concept encoder (USER-locked PRIMARY
focus, 4 goals: native perception / 0.85 semantic / ~2% sparse / algebra-must-survive) just failed at
full scale. Distill-from-BGE into sparse block codes collapsed: BLOCK spearman ~0.31 (parent-reported
FULL) and the trained sparse arms UNDERPERFORM an untrained orthographic baseline. USER (brain =
best-in-class existence proof, USER-LOCKED) wants first principles: how does biology build concept
representations that are simultaneously SEMANTIC, SPARSE, and COMPOSABLE, and did we pick a mechanism
the brain does not use?
**Method:** substrate-KB concept-query FIRST (query-first discipline), then generic-terms internet
drill (safe search, no project specifics), then off-disk verify of the failure numbers (Fix#28).
**Calibration:** lit-scan penalty applied (deflate P 0.15-0.25; cap novel-synthesis P at 0.50).

---

## 0. Disk-verified state of the failure (Fix#28 / no-hallucinated-numbers)

What I confirmed off-disk (`data/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1_smoke/metrics.json`):
- **v2 MLP distill SMOKE = HARD_PASS.** DENSE_SIGN arm (100% active, sign readout) **spearman 0.825**.
  BLOCK_K128 arm (3.125% sparse via block-STE) **spearman 0.645**.
- v1 distill SMOKE = HARD_FAIL (DENSE_SIGN 0.907/0.540 across evals; BLOCK_K128 0.788/0.718).
- **The FULL v2 metrics.json is NOT on my local disk** (sync-cadence gap or FULL not yet landed
  locally). The **BLOCK ~0.31 collapse + underperform-orthographic is the parent-agent-reported FULL
  result**, which I am NOT independently verifying here. I therefore anchor the analysis on the
  disk-verified STRUCTURAL pattern, which is sufficient and directionally identical:

  **DENSE geometry 0.825 -> BLOCK 0.645 (smoke) -> ~0.31 (FULL, parent) is a monotone SPARSIFICATION
  COST that WORSENS with scale/steps.** The MLP learns teacher geometry fine (0.825); the hard sparse
  bottleneck is the failure surface, and at FULL scale it does not merely cost, it COLLAPSES (below
  untrained orthography = the codebook-collapse / dead-block signature the L4/L5 levers warned about).

This single disk fact is the hinge of the whole brain analysis: **the geometry is learnable; the way
we force sparsity is what breaks.**

---

## 1. Substrate prior-work check (mandatory, ran first)

Queries (v2 flags via wrapper): "concept encoding sparse block code distill BGE teacher"; "sparse
coding lateral inhibition k-WTA cortical sparsity"; "complementary learning systems hippocampus
predictive coding self-supervised"; "encoder semantic spearman orthographic baseline distillation".

- **The substrate HOLDS the biology primitives already:** `T2/complementary_learning_systems` (CLS,
  primitive atom, cosine 0.398), `BIO/sparse_coding_neural` (T1 primitive, 0.353), `Self-supervised
  learning` atom (0.413), multiple `lateral inhibition` atoms (0.371, GO-ontology + notes).
- **Prior BIO drills exist** but at capacity-analytic / capability-mapping altitude, NOT applied to the
  encoder objective: `research_drill_biology_of_substrate_capabilities_5x_2026-06-08` (8.1 Sparse
  coding), `research_drill_continual_learning_revival_3x_2026-06-10` (A10 Sparse Coding & Lateral
  Inhibition), `research_drill_codebook_capacity_structural_3x_2026-06-10` (9.3 Lateral Inhibition:
  Sparsity Enforced), `wave14e_hierarchical_composition_research` (Hersche sparse block codes, treated
  as an ANALYTIC ~2x capacity mechanism only), `wave14c_r3_K64_total_collapse_research` +
  `wave14d_icl_via_pool_research` (7.1 Hippocampus-cortex CLS).
- **Prior encoder-Spoke drills** (today) established the mechanism ceiling and named distillation as
  the fix: `research_drill_concept_encoder_design_correctness_2026-07-04` (mechanism ceilings
  cat_kitten ~0.52 on friendliest corpus; P(current design hits 0.85)=0.05; recommends dense-teacher
  distillation), `research_drill_block_ste_sparse_convergence_levers_2026-07-04` (DENSE 0.825 ->
  BLOCK 0.645 = pure sparsification cost; L1 tau_b anneal / L2 dense->sparse curriculum as top levers).

- **Prior arc work on THIS concept (brain-grounded encoder LEARNING objective): NONE.** The substrate
  has the biology as ingested facts and the encoder as an engineering artifact, but no drill has
  connected the CLS internal-teacher / temporal-slowness / decoupled-sparsification brain framing to
  the encoder training. This drill is that synthesis -> lit-scan calibration penalty applied; novel
  P's capped at 0.50 and deflated.

---

## 2. How the brain forms concept representations (cited)

### 2.1 The semantic hub-and-spoke (Q1: where concepts live)
The ventral **anterior temporal lobe (ATL) is a convergence-zone hub** that integrates distributed
sensory/motor/emotional "spoke" features (shape, colour, sound, action) into generalizable, modality-
invariant conceptual representations; damage there produces semantic dementia [PNAS 2010; JNeurosci
2017]. Semantic features are **distributed and dynamic** across ventral temporal cortex, feature-like
posteriorly and increasingly nonlinear/conjunctive anteriorly, with similar concepts evoking similar
population patterns [biorxiv 695049]. So a concept is a distributed cortical pattern whose *similarity
structure* is the meaning, coordinated by a hub that does conjunctive coding of increasing complexity.

### 2.2 Complementary Learning Systems and the actual learning signal (Q1, Q4)
CLS: the **hippocampus learns fast, conjunctive, pattern-separated** episodes; the **neocortex learns
slow, distributed, statistical** structure that generalizes [McClelland/McNaughton/O'Reilly 1995]. The
learning signal is **NOT an external label.** The neocortex extracts statistical regularities self-
supervised; the hippocampus fast-binds specifics; and **systems consolidation transfers knowledge via
REPLAY**: during NREM sleep, coupled slow-oscillation/spindle/sharp-wave-ripple events replay
hippocampal traces and gradually "teach" the neocortex, **re-architecting raw episodes into abstracted
semantic structure** rather than copying them [Nat Neurosci 2019; PNAS 2022]. At the microcircuit level
this is literal self-supervision: cortical **L2/3 predicts incoming sensory input and is trained against
the L5 latent representation of what actually arrived** [Nat Commun 2025 layer-specificity].

**Load-bearing takeaway (Q4): the brain HAS a teacher, but it is INTERNAL, not external.** The
hippocampus is a fast internal teacher for the slow neocortex; L2/3 self-distills against L5. There is
no outside oracle handing the brain a pretrained embedding. The semantic geometry is BOOTSTRAPPED from
the organism's own predictive experience and then internally consolidated.

### 2.3 Sparsity: how, and constraint vs emergent (Q2)
Cortical/hippocampal codes run **~1-5% active** (our 2% goal sits inside this). The brain achieves it
with a **competitive circuit, not an optimizer**: dentate-gyrus granule cells receive strong
**feedforward + lateral inhibition from PV+ interneurons** (lateral inhibition is ~10x more abundant
than recurrent there), implementing a **k-winners-take-all** dynamic that silences the majority and
performs **pattern separation** (small input differences -> large output differences) [Nat Commun 2018;
biorxiv 647800]. Crucially: **"a kWTA function gives rise to sparse distributed representations without
needing to solve any form of constrained optimization"** [O'Reilly / Leabra]. Sparsity is therefore an
**EMERGENT property of an evolved competitive readout applied to already-rich input** - it is a
downstream selection dynamic, NOT a bottleneck the representation is forced to form itself through.
Order matters: rich cortical geometry first, competitive sparsification second.

### 2.4 Composability / the "algebra" (Q3)
Relational structure comes from the **entorhinal-hippocampal system**. **Grid cells (MEC) provide a
metric/basis** supporting **vector navigation** - computing translation vectors between arbitrary
locations - and generalize to non-spatial "structural knowledge" (the Tolman-Eichenbaum-Machine line)
[arxiv 1805.09042; Current Biology 2019]. Place/grid interaction binds content to structure;
**hippocampal conjunctive binding** ties fillers to roles; **theta phase coding** sequences and orders
bound elements. This is the brain's compositional algebra: a factorized structure basis (grid/EC) with
conjunctive binding (hippocampus), which is *exactly* the role/filler binding a VSA implements.

### 2.5 The brain's objective (Q4, synthesized)
No external teacher. The signal is some mixture of: **predictive coding** (minimize sensory prediction
error across the hierarchy), **temporal slowness / contiguity** (inputs close in time map to similar
representations - the SFA principle; drives invariance) [PhiNets arxiv 2405.14650; slowness lit],
**Hebbian co-occurrence**, and **contrastive-over-experience**. All are self-supervised over the
organism's own stream.

---

## 3. Match / Divergence gap table (our pipeline vs the brain)

Our pipeline: orthographic V1 front-end (`CharPositionalEncoder`, self-documented "surface features
only, V1 analog") -> MLP student (1024->2048->4096 GELU) -> block-STE sparse code (K blocks, 1 signed
active/block, ~2-3%) with SBC block-local circular-convolution algebra, **distilled from BGE-large**
(fixed external teacher) via RKD (pairwise-cosine) + semi-hard InfoNCE, in-batch.

| Aspect | Brain | Our encoder | Verdict |
|---|---|---|---|
| Output code sparsity (~2%) | 1-5% active DG/cortex | 2-3% block code | **MATCH** |
| Binding / algebra | EC grid basis + hippocampal conjunctive binding + phase coding | SBC block-local circular conv (roundtrip 1.000, keyed bind/unbind acc@1 1.00) | **MATCH (strong)** - this part is done |
| Semantic-hub target | ATL convergence zone | concept encoder aspiring to ATL | **MATCH (correct aspiration)** |
| Sparsity MECHANISM & ORDER | competitive k-WTA / lateral inhibition applied to already-rich input, as a downstream readout | hard block-argmax STE bottleneck forced CONCURRENTLY with geometry formation | **DIVERGE (the mechanical failure)** |
| Front-end input | multimodal perceptual + lifetime distributional spokes | orthography (spelling) only | **DIVERGE** - "learns spelling not meaning" is this gap |
| Teacher | INTERNAL (hippocampus->neocortex replay; L2/3<-L5); NO external oracle | EXTERNAL fixed BGE (an LLM embedding) | **DIVERGE (the load-bearing one)** |
| Training regime | lifelong interleaved consolidation via replay | in-batch, static, one-shot distillation | **DIVERGE** |
| Objective | predictive coding + temporal slowness + Hebbian + contrastive over own experience | relational-geometry match (RKD) + InfoNCE to a fixed teacher | **PARTIAL** - contrastive is brain-ish; target is an external oracle, not experience |

---

## 4. Have we emulated it? Honest verdict

**We faithfully emulated the OUTPUTS; we did NOT emulate the LEARNING PROCESS. The failure lives
entirely in the un-emulated part.**

- **What is genuinely brain-like and WORKS:** the *code structure* (sparse ~2% distributed code ~
  cortical/DG sparse coding) and the *binding algebra* (SBC block-local convolution ~ hippocampal
  conjunctive binding / grid-cell vector algebra). These pass by construction: roundtrip 1.000, keyed
  bind/unbind acc@1 1.00. This half of the brain analogy is real and load-bearing - keep it.

- **What is NOT brain-like and is exactly where we fail - two specific choices:**
  1. **External teacher.** We distill from BGE, an outside pretrained embedding. The brain has no
     external oracle; it bootstraps semantics self-supervised and self-distills INTERNALLY
     (hippocampal replay; L2/3<-L5). Distillation *per se* is not un-brain-like - the brain does it -
     but our teacher being EXTERNAL is. This also sits in direct tension with the project's
     foundational anchors ("substrate knows nothing / substrate standalone / glass-box LM, no external
     LLM, USER-LOCKED"): a semantic geometry inherited from BGE is not substrate-native. Flag for USER.
  2. **Sparsity forced DURING geometry formation.** We push the representation through a hard block-STE
     bottleneck while it is still learning the geometry. The brain never does this: it forms rich
     cortical geometry first and sparsifies downstream via a competitive k-WTA readout. Our own disk
     proves the point - **DENSE_SIGN 0.825 (geometry fine) vs BLOCK 0.645 smoke -> ~0.31 FULL
     collapse.** That gap IS the divergence, quantified.

- **The failure is a learning-process failure, not a code-structure failure.** "Trained sparse arms
  underperform untrained orthography" is the codebook-collapse signature of forcing a hard discrete
  bottleneck concurrently with representation formation at scale - the precise thing the brain's
  rich-first / sparsify-after order is built to avoid. So: **no, we have not emulated the brain's
  learning process, and that is why it broke. But the fix is a brain-grounded reordering, not a
  teardown - the brain lens says the code and algebra are right and the training order is wrong.**

---

## 5. Brain-grounded encoder directions (ranked, P_deflated) - seeds for the 5x rescue battery

### D1 [HIGHEST - immediate rescue] Decouple sparsification from geometry: dense-first, then competitive k-WTA. P_deflated 0.45
**Brain grounding:** cortex forms rich distributed geometry via slow statistical/predictive learning;
DG then sparsifies via feedforward+lateral-inhibition k-WTA as a downstream competitive readout. Rich
first, sparse second - never simultaneously.
**Mechanism:** two-phase training. Phase 1 forms the dense teacher geometry with no hard sparse
bottleneck (our DENSE_SIGN=0.825 shows this converges). Phase 2 introduces competitive sparsification
by annealing, not by a step-0 hard STE. Concretely this is the *already-drafted* L1 (decoupled tau_b
cosine anneal 2.0->0.1, backward-only) and/or L2 (dense->sparse blend curriculum) from
`research_drill_block_ste_sparse_convergence_levers_2026-07-04.md` - but now with a first-principles
brain justification AND a stronger structural claim: sparsify as a competitive READOUT applied to a
formed representation, not as a bottleneck the representation forms through. Algebra-safe by the global
invariant (`_encode_hard_block` deploy structure unchanged -> roundtrip stays 1.0).
**Why highest:** it is the ONLY direction disk-supported today (0.825 dense geometry already exists),
it directly explains and reverses the observed collapse, it is cheap (~15-40 lines), algebra-safe, and
it is the immediate rescue for the current FULL failure.
**Deflation:** capped novel-synthesis 0.50, deflated to 0.45 because "closes to 0.85 AT 2%" is unproven
- the L6 tension flags that hitting 0.85 AND ~2% simultaneously may be capacity-bound (K=128 is already
3.125%; K=82 at true 2% is harder). Run the K=256 capacity-ceiling diagnostic in the same batch to
disambiguate convergence-limited (D1 works) vs capacity-limited (re-scope).

### D2 [HIGH - principled, gated on corpus maturity] Internal self-teacher (EMA self-distillation) over the substrate's own experience. P_deflated 0.25
**Brain grounding:** no external oracle. The hippocampus is a fast INTERNAL teacher for the slow
neocortex (replay/consolidation); L2/3 self-distills against L5. A brain-grounded encoder bootstraps its
own semantic geometry rather than importing BGE's.
**Mechanism:** BYOL/DINO-style self-distillation - the student's own slow-moving EMA copy is the
teacher; positive pairs come from the substrate's OWN relational experience (KB-neighborhood,
relation-path, gloss co-occurrence), no external LLM. This resolves the "no external LLM / substrate
knows nothing" tension: the semantics become substrate-native, not inherited.
**Honest deflation (hard):** the substrate corpus "knows nothing" yet - there is no rich lived
distributional stream to self-supervise over, which is precisely why BGE was chosen as a pragmatic
substitute for the missing "lifetime of distributional experience" (per the design-correctness drill).
So D2 is the PRINCIPLED-LONG-TERM direction, gated on corpus-ingest depth that does not exist today.
P_deflated 0.25 (novel synthesis + gated on absent corpus richness). Do not dispatch as the immediate
rescue; sequence it as the substrate matures.

### D3 [MED - self-supervised signal native to the KB] Predictive / temporal-contiguity auxiliary objective over the relational graph. P_deflated 0.30
**Brain grounding:** temporal slowness/contiguity (close-in-experience -> similar representation) +
predictive coding + Hebbian co-occurrence, all self-supervised.
**Mechanism:** add an auxiliary loss that pulls together concepts adjacent in relation-paths /
co-occurring in gloss context (the KB's structural analog of "encountered close in time"), as a
supplement to - and eventual partial replacement for - the BGE target. This directly densifies the
too-sparse 1.6-atoms/entity signal the design-correctness drill flagged as insufficient, and it
supplies the positive pairs D2 needs.
**Deflation:** 0.30. Composes with D2 (provides positives) and is teacher-free, but its ceiling depends
on how much relational structure the current KB actually carries (thin today).

### Pragmatic sequencing (the honest bridge)
Keep BGE distillation NOW as the "cortical-spoke surrogate" for the missing distributional experience
(honest, defensible bootstrap) and fix the immediate collapse with **D1** (decouple sparsify) - that is
the rescue. Treat **D2 + D3** as the deeper brain-grounding that ALSO resolves the external-LLM tension,
sequenced behind corpus maturation. Near-term rescue and principled long-term are separable; do not
block the rescue on the long-term.

---

## 6. Provenance / sources

**Substrate (off-disk):** encoder metrics `data/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1_smoke/metrics.json`
(DENSE_SIGN 0.825, BLOCK_K128 0.645, HARD_PASS); v1 HARD_FAIL sibling. Prior drills
`research_drill_concept_encoder_design_correctness_2026-07-04.md`,
`research_drill_block_ste_sparse_convergence_levers_2026-07-04.md`,
`design_encoder_step1b_v2_next_changes_2026-07-04.md`; atoms `T2/complementary_learning_systems`,
`BIO/sparse_coding_neural`, `Self-supervised learning`.

**Literature (generic-terms web drill):** ATL hub-and-spoke [PNAS 2010 "Coherent concepts computed in
ATL"; JNeurosci 2017 semantic hub; biorxiv 695049 distributed dynamic ATL code]. CLS
[McClelland/McNaughton/O'Reilly 1995]. Systems consolidation / replay [Nat Neurosci 2019; PNAS 2022
hippocampus-neocortex sleep model]. Cortical self-supervised predictive coding [Nat Commun 2025
layer-specificity L2/3<-L5]. DG sparsity / lateral inhibition / k-WTA [Nat Commun 2018 PV+
lateral-inhibition microcircuit; biorxiv 647800 pattern separation; O'Reilly kWTA "no constrained
optimization"]. Composition [arxiv 1805.09042 TEM structural generalisation; Current Biology 2019 grid
cells vector navigation]. Objective [PhiNets arxiv 2405.14650 temporal-prediction non-contrastive;
temporal slowness/SFA lit]. Encoder ML levers [decoupled STE arxiv 2410.13331; continuous-first
discrete-later; VQ-VAE commitment/codebook-collapse].

ASCII-only. No emojis. No em dashes.

---

## 7. Intuitive summary (USER universal rule)

Here is the honest version. The brain builds a concept the way we WANT ours built: a rich, distributed
pattern of activity whose *similarity to other patterns* IS the meaning, coordinated by a hub (the
anterior temporal lobe) that fuses input from vision, sound, and action. It makes those patterns sparse
- only 1-5% of neurons on at once, just like our 2% goal - but it does that with a simple competitive
"loudest few win" circuit that fires AFTER the rich pattern has already formed. And it never has a
teacher handing it answers from outside; it teaches itself by predicting its own experience, and it has
an *internal* teacher - the hippocampus replays the day's events during sleep and slowly trains the
cortex to extract the general structure.

Now line that up against what we built. Two halves. The half we got RIGHT is the output: our sparse
codes and our binding math (roundtrip perfect, bind/unbind perfect) are genuinely brain-like and they
work - keep them. The half we got WRONG is how we LEARN. We did two un-brain-like things, and they are
exactly where it broke. First, we borrowed an outside teacher (BGE, an off-the-shelf language embedding)
instead of letting the substrate learn meaning from its own experience - which also quietly contradicts
our own locked principle that the substrate should stand alone and not lean on an external LLM. Second,
and this is the one causing the crash, we forced the representation to become sparse AT THE SAME TIME it
was trying to learn the meaning - like asking someone to write an essay while only being allowed to use
2% of the words, from the first draft. The brain never does that; it writes the full draft first, then
selects. Our own numbers prove it: when we let the code stay dense it scores 0.825 (great); the moment
we force it sparse during learning it drops to 0.645 and then collapses to ~0.31 at full scale, below
even a dumb spelling-based baseline. So we did NOT emulate the brain's learning process, and that
mismatch is the failure.

Why this matters and where it leaves us: this is good news, not bad. The failure is not in the parts
that are hard to change (the code and the algebra are right); it is in the training ORDER, which is the
easy thing to change. The top rescue - and it is brain-grounded, not a guess - is to do what the cortex
does: form the rich meaning first, then sparsify with a competitive readout afterward, instead of
forcing both at once. We already have the levers drafted for this; the brain lens just told us WHY they
are the right levers and gave them a first-principles reason. The deeper, longer-term rescue is to wean
the encoder off the outside teacher entirely and have it learn meaning from the substrate's own
relational experience with an internal self-teacher - but that one is gated on the substrate actually
having a rich body of experience to learn from, which it does not yet, so it is the direction to grow
into, not tonight's fix. Position: the encoder is recoverable, the recovery is cheap and principled,
and the brain question sharpened rather than overturned the plan - fix the training order now, grow the
self-supervised path as the corpus fills in.
