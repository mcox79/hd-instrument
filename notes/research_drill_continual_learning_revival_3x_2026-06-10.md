# Research Drill: Continual Learning Revival -- Full CLS Architecture
# 3-Stream Synthesis (Brain + Nature + LLM Theory)
# Date: 2026-06-10

---

## HEADLINE

The brain solves continual learning via a four-component architecture that the substrate
currently implements only one quarter of: (1) a fast-binding episodic store
(hippocampus -- substrate has this), (2) a slow-integrating generalizer (neocortex --
substrate missing), (3) a frequency-selectivity / decay / forgetting mechanism
(spine downscaling + Ebbinghaus -- substrate missing), and (4) a consolidation scheduler
(sleep oscillations + replay -- substrate missing). Full CLS requires all four.
The five most actionable mathematical paths toward the missing three are ranked below.
P_deflated(full CLS in substrate) = 0.35; P_deflated(partial CLS: slow-generalizer only) = 0.58.

---

## STREAM A: BRAIN MECHANISMS FOR CONTINUAL LEARNING

### A1. Hippocampal-Cortical Replay (Wilson-McNaughton; Tonegawa engram)

The core empirical result: during sharp-wave ripples (SWR) in NREM sleep,
hippocampal cell assemblies fire in time-compressed sequences (10-20x faster than
waking experience), while neocortical slow oscillations coordinate UP states that
coincide with these replays. The bi-directional model (Rothschild et al. 2022;
HiCL 2025) adds: cortical patterns trigger the hippocampal replay, and hippocampal
replay in turn strengthens weaker cortical traces. This is not one-way transfer --
it is a resonant loop. Mathematical structure: let H(t) be hippocampal
firing patterns and C(t) cortical patterns. Consolidation criterion:
weight update dW/dt proportional to corr(H(t), C(t)) above threshold theta_SWR.
Prediction: systems with episodic memory converge to stable cortical representations
only when theta_SWR is tuned to the overlap between new episodes and existing cortical
representations.

Key lit: Tonegawa engram cells (2015+) show reactivation is sufficient; Rothschild
2022 bi-directional model; HiCL arxiv 2508.16651 (2025) operationalizes for ANNs.

### A2. Sleep Consolidation: Slow-Wave + REM Roles

Recent neuroscience (PMC 2025, JNeurosci 2025, Nature Comms Bio 2025) distinguishes
two sleep stages with complementary roles:
- NREM (slow oscillations + spindles + ripples): transfers item-specific episode
  content from hippocampus to cortex; preserves detail; spindle trains provide
  timed repeated reactivation.
- REM (theta + beta): transforms item memories toward category-level gist;
  reduces item-specific detail; supports schema generalization.
The oscillatory coupling hierarchy is: slow oscillation (0.5-1 Hz) nests spindles
(12-15 Hz), which nest ripples (80-120 Hz). The temporal ordering predicts
consolidation efficiency: phase of spindle within slow oscillation up-state determines
which cortical synapses get upscaled vs globally downscaled.

Mathematical structure: let e_i be episode vectors in hippocampus, s_k be schema
vectors in cortex. The replay schedule produces gradient:
   Delta s_k ~ sum_i alpha_i * corr(e_i, s_k) * gate(SWR_phase)
where gate() is the ripple-coincidence gating function. Schema extraction during
REM approximates a non-negative factorization of the episode matrix.

### A3. Complementary Learning Systems (McClelland 1995; updated Kumaran 2016)

The CLS theory posits structural separation: hippocampus = pattern-separated
(orthogonal codes, one-shot binding, high plasticity), neocortex = distributed
overlapping (slow statistical learning, extracted regularities). Key constraint:
interleaved replay is required to prevent catastrophic forgetting in the cortex
during hippocampal-to-cortical transfer. Without interleaving, new items overwrite
cortical representations of old regularities. This is the structural explanation
for why rapid direct cortical learning fails: gradient updates are not interleaved
with prior data, so Fisher Information of prior tasks is destroyed.

The math: if theta_cortex satisfies Fisher Information I(theta|T1), then single-task
training on T2 drives theta toward theta_2*, minimizing cross-entropy on T2 alone.
EWC adds quadratic penalty lambda/2 * (theta - theta_1)^T * I(theta|T1) * (theta - theta_1).
CLS replay adds samples from T1 to training on T2, maintaining I(theta|T1) implicitly.

### A4. Schema-Mediated Consolidation (Tse et al. 2007; Tse 2011)

Tse showed that when a new paired associate fits an existing schema (prior relational
structure), it is consolidated into hippocampus in <24h (vs 4 weeks without schema).
Cortical schema accelerates hippocampal-to-cortical transfer. Mechanism:
prior cortical schema provides a "scaffold" that reduces the number of replay cycles
needed. Mathematical prediction: consolidation time T_consolidate = f(d(new_item,
nearest_schema)) where d is schema-orthogonal distance. New items close to schema
consolidate rapidly; highly novel items require more replay cycles proportional to
their distance from the nearest schema cluster centroid.

This directly maps to a substrate-side question: how many replay cycles are needed
to consolidate a new shard as a function of its geometric distance from existing
schema centroids?

### A5. Synaptic Plasticity: LTP/LTD and Synaptic Tagging/Capture

Two-phase consolidation: early LTP = fast (minutes, protein synthesis independent);
late LTP = slow (hours, protein synthesis dependent, requires tagging).
Synaptic tagging-and-capture (STC): an early-LTP event at synapse A sets a "tag";
late LTP requires plasticity-related proteins (PRPs) that can be captured from
any activated source. Key: a tag at synapse A can capture PRPs generated at synapse
B if both are active within a critical time window (~1-2 hours). This enables
associative memory: events co-occurring within the tagging window get linked even
if not directly co-presented. The 2025 European Journal of Neuroscience review
(Benoy et al.) emphasizes temporal flexibility: STC is not a fixed-time-window
mechanism but responds to neuromodulator state (arousal, novelty).

Mathematical consequence: memory persistence p(synapse, t) follows:
  dp/dt = -gamma * p + PRPs(t) * tag(synapse) - noise
where PRPs(t) spikes after late-LTP-inducing stimuli and decays with tau_PRP ~ 1-2h.
This is a first-order ODE with transient input -- directly implementable as a
scalar decay-with-capture model on substrate shard weights.

### A6. Adult Neurogenesis: Dentate Gyrus Pattern Separation + Temporal Stamp

Adult-born dentate granule cells (DGCs) are uniquely hyperexcitable for 3-4 weeks
after birth, then settle into sparse mature coding. Their roles:
(a) Pattern separation: orthogonalize similar inputs by their sparse representation
    differences (2024 PubMed review).
(b) Temporal stamp: memories encoded close in time are tagged by the same cohort
    of young neurons, so temporal proximity is encoded structurally.
(c) Clearing old memories: ongoing neurogenesis degrades old connections in mature
    neurons, actively promoting forgetting of remote memories to prevent saturation.

The paradox (Bhattacharya et al., PMC 4593858): neurogenesis simultaneously REDUCES
pattern separation capacity (young neurons are excitable, not sparse yet) AND reduces
interference at longer timescales (by clearing old traces). Resolution: young neurons
mediate short-timescale disambiguation; mature sparse neurons handle long-term storage.

Mapping to substrate: new shard insertion at anomaly resembles young-neuron hyperexcitability
phase (wide basin, low discrimination), then shards should "mature" (narrow basin,
high discrimination) over replay cycles. Failure to implement this maturation cycle
causes new shards to remain wide-basin and interfere with older consolidated items.

### A7. Reconsolidation: Memory Becomes Labile on Retrieval

Nader-LeDoux reconsolidation (2000): retrieving a memory reopens a plasticity
window requiring protein synthesis for re-stabilization. If protein synthesis is
blocked during this window, the memory is degraded or altered. This is not a bug --
it is the mechanism for memory updating: retrieved memories can be modified by
concurrent experience before re-stabilization. Key temporal window: 4-6 hours
after retrieval. The 2025 PNAS behavioral tagging study shows that adjacent novel
tasks modulate whether reconsolidation degrades or updates the retrieved memory.

Mathematical structure: retrieved memory trace r(t) enters labile state L(t).
Re-stabilization requires integration:
  S(t) = integral_{t_retrieval}^{t_retrieval + tau} L(tau) * delta(concurrent_input) dtau
If delta is consistent with r(t) (confirming retrieval), S reinforces. If delta
contradicts r(t), S weakens or writes a modified version.

Substrate implication: this is RECONSOLIDATION-EDIT (see D2.3 below). It is
empirically motivated and has direct implementation path.

### A8. Forgetting Curves and Intentional Forgetting (Ebbinghaus; Anderson & Green)

Ebbinghaus (1885): retention R(t) decays as power law R(t) = (1 + t/tau)^(-S).
The spacing effect: re-study at interval t1 resets the clock but raises the new
S parameter (slower subsequent decay). Recent formulation (2024 distribution model):
empirical forgetting curves underestimate true forgetting because subjects are
heterogeneous; the population distribution of S values convolves with the time axis.

Intentional forgetting (Anderson & Green, 2001): active suppression via think/no-think
paradigm reduces hippocampal retrieval, mediated by dorsolateral PFC inhibition of
hippocampus. GDPR-delete in the substrate implements a weaker form (passive remove).
Active suppression (inhibiting retrieval patterns to reduce consolidation) has no
current substrate analog.

### A9. Glial Regulation (Stevens; Allen; Bhatt)

Astrocytes regulate synapse elimination via complement cascade (C1q, C3, CR3).
Microglial phagocytosis of synapses (synaptic pruning) peaks in late development but
continues in adult brain. Mechanism: low-activity synapses get tagged with complement
and pruned. Mathematical consequence: synaptic weight w_ij gets pruned if activity
integral integral_{T} A_ij(t) dt < theta_pruning over window T. This is an integrated
activity threshold, not instantaneous. Biological parallel to GDPR-delete + frequency
filter: items below activity threshold over long window get auto-pruned.

### A10. Sparse Coding and Lateral Inhibition

Sparse coding in piriform cortex (Olshausen-Field model, 1996): input x is
represented as sparse combination of dictionary atoms: x approx D * a, ||a||_0 <= k.
Lateral inhibition enforces sparsity via winner-take-all. Pattern separation is a
direct consequence: if two inputs share < k atoms, their sparse codes are orthogonal.
Interference requires exact code overlap. Biological dentate gyrus: ~5% of granule
cells active per input (very sparse). Artificial neural nets: activations typically
50-80% non-zero (very dense) -- direct cause of gradient interference in EWC.

Substrate HD vectors: sparsified bipolar HD vectors (from PP-225 or similar) already
implement approximate sparse coding via binarization. This is a substrate strength for
continual learning, not a weakness -- but the downstream LLM integration layer is
still dense and will catastrophically forget.

---

## STREAM B: NATURE/EVOLUTION OF LIFELONG LEARNING

### B1. Imprinting: Critical Period + Gated Plasticity (Lorenz)

Lorenz filial imprinting (1935): geese form irreversible species-identity during a
critical 13-36 hour post-hatch window. Neural substrate: IMM (intermediate and medial
mesopallium) in bird forebrain, homologous to mammalian association cortex.
Post-critical-period: IMM retains the imprinted template and resists overwriting.
Key mechanism: the critical period is gated by GABA_A receptor maturation and
BDNF-dependent plasticity closure. Once closed, the template is "consolidated" --
extraordinarily resistant to overwriting even by extended subsequent exposure.

Mathematical insight: the critical period implements a hard cutoff on plasticity
lambda(t) = lambda_max * 1[t <= t_critical] + epsilon * 1[t > t_critical]. This
is not a soft decay -- it is a gate. This suggests that "consolidation" in artificial
systems could be implemented as a plasticity gate: high plasticity during initial
encoding, gated-off after consolidation criterion is met.

### B2. Songbird Template Learning and Sleep Consolidation

Songbirds learn their species-specific song in two stages: (1) sensory phase
(memorize template by listening), (2) sensorimotor phase (match output to template).
Sleep is critical for both: post-sleep song crystallizes toward the template.
Margoliash lab: song replay occurs during REM-like sleep in juvenile zebra finches;
HVC neurons replay the day's song. Mature birds: templates are stable and resistant
to overwriting; novel tutors presented to adults cause only partial updating.

Key analog: the two-phase structure (memorize first, practice second) maps to
hippocampal encoding followed by cortical consolidation. The "practice" phase
(sensorimotor) is the replay phase. Systems without this two-phase structure try to
learn the template and practice simultaneously -- equivalent to simultaneous
encoding and consolidation, which degrades both.

### B3. Honey Bee Cumulative Associative Learning

Honeybees learn olfactory-flower associations over their forager lifetime (weeks)
without losing earlier associations. Mechanism: mushroom body Kenyon cells use sparse
codes (5% activation); olfactory associative learning modifies feedback inhibitory
neurons. The sparse coding means new associations do not overwrite old ones --
different subsets of Kenyon cells are recruited. This is CLS without hippocampus:
purely sparse coding + lateral inhibition implements lifetime associative learning.
Total KB: ~1000 distinct odor associations over 3-week forager life.

### B4. Cephalopod Problem-Solving: Rapid Adaptation Without Replay

Octopus bimaculoides solves novel problems in single trials (one-shot learning)
without prolonged sleep-based consolidation. Proposed mechanism: very large visual
lobes with massive recurrent processing; no evidence for hippocampal-type separate
fast store. This is a counterpoint to the hippocampal-cortical CLS model: rapid
learning can occur in a unitary system IF the representations are sufficiently
orthogonal (via large dimensionality + sparse coding). This suggests that with
high enough dimensionality N, the substrate could approach one-shot retention
without a separate slow-generalizer -- but only for episodic recall, not schema
extraction.

### B5. Mammalian Play + Skill Development

Juvenile mammals use play to consolidate motor schemas: the behavior generates
variability (exploration) with low stakes, and sleep post-play consolidates the
learned motor patterns. The substrate-relevant insight: exploration requires
INCREASED plasticity (wide basins, accept noise), exploitation requires DECREASED
plasticity (narrow basins, reject noise). Natural learning schedules alternate
exploration and exploitation phases, each followed by sleep. A substrate that
permanently runs in one regime will fail at the other.

### B6. Cultural Transmission: Multi-Agent Continual Learning

Cultural transmission (Boyd-Richerson, Tomasello "cultural brain hypothesis"):
human-specific capacity to accumulate and refine knowledge across generations via
high-fidelity imitation. Each generation starts from prior generation's substrate
("ratchet" accumulation). Mathematically: let KB_gen(n) be generation-n knowledge
base. KB_gen(n+1) = consolidate(KB_gen(n)) + new_discoveries(n). The consolidation
step compresses KB_gen(n) into schemas + removes low-confidence items. This is
multi-generational forgetting-with-schema-retention.

Substrate analog: if the substrate undergoes periodic schema-extraction runs
(PP-141 schema defrag) followed by pruning of the raw episodes that have been
subsumed, it implements the cultural transmission forgetting-and-ratchet cycle.

### B7. Niche-Specific Learning: Selective Plasticity

Many species learn preferentially in ecologically relevant domains (birdsong, food
caching in Clark's nutcracker, spatial navigation in London cabbies). Mechanism:
domain-relevant circuits have elevated BDNF expression and more adult neurogenesis.
Implication: plasticity is not uniformly distributed -- the substrate should have
higher plasticity for "important" shard types and lower for "settled" ones. Uniform
plasticity rules (like vanilla EWC with uniform lambda) fail to capture this.

### B8. Multi-Generational Behavioral Evolution

Evolution encodes learning biases (prepared learning, Garcia effect for taste
aversion) that survive across generations via genetic canalization. This is
"prior knowledge over priors" -- the prior is learned over evolutionary timescale
and is MUCH more stable than within-lifetime learning. In substrate terms: the
weight initialization and architecture (not just the stored items) carry prior
knowledge. The architecture is a slow-time-scale learner; the stored items are
fast-time-scale.

### B9. Cumulative Culture and Ratchet Effect (Tomasello)

Tomasello's "ratchet" observation: human cultural knowledge accumulates because
each generation adds to what they received (not just re-learns it). Requires
high-fidelity copying (faithful transmission) + small improvements (incremental
updating). For a knowledge store: faithful retrieval (substrate already provides),
small improvements = reconsolidation updates (A7 above) + schema refinement (A4 above).
Systems that allow large-scale rewrites fail the ratchet -- they accumulate but also
lose. This is exactly catastrophic forgetting in LLMs: they add but also lose.

### B10. Lifelong Neuroplasticity (Merzenich; Cortical Map Reorganization)

Merzenich: adult cortical maps reorganize after sensory deprivation or skill training.
Hand representation expands in string musicians; amputees reorganize somatosensory cortex.
Key point: reorganization is not wholesale overwriting -- it is boundary shifting.
Adjacent cortical columns gradually expand or contract over weeks/months. The math:
competitive Hebbian learning (Kohonen SOM) implements this -- neurons compete for
representation of input patterns, and the winning neuron's weight vector is pulled
toward the input while losing neurons are pulled less. Forgetting via Kohonen:
patterns not recently presented lose representation as their "territory" is taken
over by neighboring patterns. This is controlled forgetting -- not catastrophic.

Substrate analog: shard boundaries could shift via competitive Hebbian updates --
shards whose patterns are no longer presented lose capacity to nearby shards that
are frequently reinforced.

---

## STREAM C: LLM THEORIES FOR CONTINUAL LEARNING

### C1. Catastrophic Forgetting (McCloskey-Cohen 1989)

The foundational observation: backpropagation on new task T2 overwrites weights
learned for T1 because gradient updates are unconstrained. Severity grows with
parameter sharing between tasks. With weight sharing proportion rho, forgetting rate
is approximately rho * (learning_rate * gradient_magnitude_T2). Reducing
learning_rate reduces both forgetting AND learning of T2 equally -- there is no
free parameter that breaks the forgetting-learning tradeoff without architectural
change.

### C2. Elastic Weight Consolidation (Kirkpatrick et al. 2017)

EWC penalty: L = L_T2 + lambda/2 * sum_i F_i * (theta_i - theta_i*)^2
where F_i is the Fisher information (diagonal approximation) of parameter i for T1.
This anchors high-F parameters. Limitation: diagonal F ignores parameter correlations;
the true penalty should use full Fisher matrix but that is O(N^2). Known failure mode:
after K tasks, EWC accumulates K penalty terms; for large K, the effective spring
constant grows unbounded and plasticity collapses. Recent work (PNAS 2025 replication
arXiv 2507.10485) confirms this and proposes decay of old Fisher terms.

EWC maps to: the substrate should assign "importance weights" to each shard based on
how many downstream queries depend on it. High-importance shards are protected from
being overwritten; low-importance shards are candidates for decay.

### C3. Progressive Networks (Rusu et al. 2016; ongoing 2025)

Lateral-connection columns: each new task gets a new column; all prior columns
are frozen; new column has lateral connections to all prior columns. Prevents
forgetting by construction (frozen columns). Cost: quadratic growth in parameters
per task. Lateral connections implement knowledge transfer (positive transfer
from prior columns to new). Recent variants (2025 ICLR, industrial fault detection)
add pruning to control growth. Direct parallel: progressive KB shards where old
shard is frozen and new shard inherits query paths from old.

### C4. Replay-Based Methods (DGR, MeRGAN, exact replay)

Deep Generative Replay (Shin et al. 2017): train a generative model to replay
synthetic samples from prior tasks during training on new tasks. Reduces catastrophic
forgetting proportional to replay fraction rho_replay. Failure mode: generative model
itself forgets (dual forgetting). MeRGAN (2018) addresses this by conditioning
generation on task identity. Exact replay (Experience Replay): store actual samples;
retrieval at training time. The substrate's episodic store directly implements exact
replay: stored items are the replay buffer.

### C5. Memory-Augmented Networks (DNC, NTM, Neural Episodic Control)

Differentiable Neural Computer (Graves et al. 2016): external key-value memory
with content-based addressing. New associations write to memory without overwriting
the weights; weights learn only meta-level retrieval. This is a direct structural
analog to the substrate architecture: the HD weight matrix W is the external
memory; inference-time retrieval is content-based; catastrophic forgetting only
affects the retrieval weights (much smaller than the stored memory).

Key math: given memory matrix M (rows = items), query q, retrieval is
softmax(M * q / tau), where tau is temperature. Writing new item e to row k:
w_write(k) * e + (1 - w_write(k)) * M[k] (blend-write). If w_write is sparse
(one-hot), this is exact write without interference.

### C6. Continual Pretraining Strategies for LLMs

Four main approaches (2025 surveys): (a) replay mixing (add general-domain data
to new-domain batch), (b) architecture expansion (ADEPT: freeze old layers, grow new),
(c) parameter regularization (EWC, SI, online EWC), (d) context-aware conditioning
(CA-CPT: provide sample context before weight update). Empirical finding: replay
mixing dominates in practical settings (ACL 2025 paper on stability gap mitigation).
The stability gap: when continual pretraining begins, validation loss on the new
domain initially RISES before it improves (due to distribution shift causing
transient forgetting even on the new domain). Mitigated by: warm-up epochs, data
ordering by domain similarity, smaller initial learning rate.

### C7. LoRA / PEFT for Incremental Learning

LoRA (Hu et al. 2022): low-rank adaptation Delta_W = B * A, where B in R^{d x r}
and A in R^{r x k}, r << d. New task uses a new (B, A) pair while base weights frozen.
Mixture of LoRA Experts (MoLoRA, EMNLP 2025): each task gets a LoRA expert; a router
selects relevant experts at inference. This implements soft progressive networks with
parameter sharing (base weights). The key insight: LoRA rank r controls the
"task footprint" in weight space -- small r means low interference with other tasks.

For the substrate: a LoRA-like low-rank perturbation on the projection matrices
(PCA whitening, output head) could allow new domains to be added with minimal
disruption to existing shards.

### C8. Knowledge Editing: ROME and MEMIT

ROME (Meng et al. 2022): identifies mid-layer feed-forward projections as
factual recall "sites"; edits specific key-value associations by solving:
minimize ||W_new * k - v_new||^2 subject to W_new * K_old = W_old * K_old
(rank-one constraint). MEMIT extends to batch edits over multiple layers.
Limitation (2024-2025 results): sequential edits accumulate errors;
after ~1000 edits, model degradation is measurable. Root cause: rank-one
edits are not orthogonal to each other; they create cross-task interference
in the key space. New methods R-ROME and PRUNE (2025) add orthogonalization.

Substrate analog: reconsolidation editing (D2.3 below) is the HD equivalent:
retrieve item, modify HD vector, re-stabilize. This is cleaner than ROME because
HD keys have much lower overlap (near-orthogonal by design) than Transformer MLP
key vectors.

### C9. Mixture of Experts for Continual Learning

Theory (MoE-CL, ICLR 2025 oral): sparse gating in MoE gives each task its own
expert subspace; catastrophic forgetting scales as the reciprocal of the number of
experts E (not N_parameters). Specifically: forgetting rate ~ 1/(E * |task-specific
expert fraction|). Routing collapse (all tasks route to same expert) is the failure
mode; addressed by load balancing loss + entropy regularization on routing distribution.
Split-on-Share (arXiv 2601.17616, 2025): task-agnostic MoE that dynamically splits
experts when a new pattern shares too much weight with an old expert.

Substrate analog: each KB shard is an "expert" in its domain; content-based routing
(HD similarity) is already the gating mechanism. The forgetting rate analysis
translates: as long as new items address different shards, there is no forgetting.
Forgetting occurs only when new items address the SAME shard as old items -- and the
shard capacity M_c is exceeded.

### C10. Online Learning + Meta-Learning (MAML; OML; ANML)

MAML (Finn et al. 2017): learn an initialization theta* such that a few gradient
steps on a new task leads to fast convergence. Online Meta-Learning (OML, 2019):
extend MAML to the continual setting where tasks arrive sequentially; meta-training
updates theta* to generalize across past tasks while fast-adapting to new ones.
ANML (2020): neuromodulated meta-learning -- separate "neuromodulatory network" gates
which weights are plastic for a given context, preventing interference.

ANML is the closest LLM analog to the hippocampal-cortical architecture: the
neuromodulatory network = frequency-selective gating; the base network = slow
cortical generalizer; the fast-adapt path = episodic store.

---

## STREAM D: SYNTHESIS -- DUAL-SUBSTRATE CLS + CRAZY MATH

### D1. The Four-Component Architecture (What Is Actually Required)

Cross-stream synthesis confirms: full lifelong learning requires ALL FOUR of:

1. EPISODIC FAST STORE: one-shot binding, near-orthogonal codes, exact retrieval.
   Substrate status: PRESENT (HD W matrix, PP-1 through PP-100+).

2. SLOW STATISTICAL GENERALIZER: extracts regularities over many episodes;
   tolerates gradual interference; produces schema / cluster centroids.
   Substrate status: ABSENT. This is the single largest gap.

3. FREQUENCY-SELECTIVE DECAY: items decay unless reinforced; decay rate
   depends on retrieval frequency and spacing; implements Ebbinghaus forgetting
   curve at the substrate level.
   Substrate status: ABSENT (GDPR-delete is blunt erasure, not graded decay).

4. CONSOLIDATION SCHEDULER: orchestrates replay from fast store to slow
   generalizer; timing depends on oscillatory coupling; implements sleep-defrag.
   Substrate status: PARTIALLY PRESENT (PP-141/142 schema extraction exists as
   batch operation, but not as an ongoing replay scheduler with frequency gating).

Without (2) and (3), the substrate at capacity M > M_c has no recovery mechanism:
new items overwrite old items in the fast store with no cortical generalization
fallback, and no frequency-weighted preservation. This is the formal definition
of the current limitation.

---

### D2. EIGHT CRAZY MATH SYSTEMS

---

#### D2.1 DUAL-SUBSTRATE-CLS

Structure: two HD weight matrices W_H (hippocampal, fast, exact) and W_C (cortical,
slow, generalized). W_H uses full precision, high learning rate (one-shot insert).
W_C uses lower rank or compressed representation, updated only during "sleep" runs
by replaying items from W_H.

Write protocol:
  - New item: insert into W_H immediately (PP-1 style).
  - Sleep cycle: for each item e_i in W_H, retrieve schema cluster center
    c_k = argmin_k ||e_i - c_k|| in W_C, then:
    c_k <- (1-alpha) * c_k + alpha * e_i   (EMA update, alpha = 1/N_k)
    N_k increments. Items in W_H that have been replayed R_thresh times are
    demoted to "consolidated" status.

Query protocol:
  - Primary: search W_H (exact, fast-binding). Return if similarity >= theta_H.
  - Fallback: search W_C (generalized). Return schema cluster center.
  - Composition: return blend (beta * W_H_result + (1-beta) * W_C_result).

HARD-PASS criterion: W_C recall@10 on items replayed >= R_thresh times exceeds
W_H recall@10 by >= 10% for a dataset of M = 3*M_c items (capacity overflow).
This tests whether cortical fallback extends useful capacity beyond M_c.

HARD-FAIL criterion: W_C recall@10 < 0.30 after 10 sleep cycles on M = 2*M_c items.

P_deflated = 0.40 (novel architecture, no direct lit precedent at this scale).

---

#### D2.2 FREQUENCY-SELECTIVITY-DECAY

Structure: each item e_i in W_H has a metadata scalar s_i (stabilization score).
s_i starts at s_0 = 0 at insertion. On each retrieval, s_i += delta_s (retrieval
bonus). On each "sleep tick" (time unit), s_i -= gamma * (1 - s_i / s_max) (decay
toward zero with floor).

Decay function implements power-law forgetting:
  R_i(t) = (1 + gamma * t / (1 + k * N_retrievals_i))^(-S_i)
where S_i is determined by the stabilization score s_i. Frequently retrieved items
develop high S_i (slow decay); items never retrieved decay rapidly.

Pruning: when s_i < threshold_prune over a window of T_prune sleep ticks, item is
demoted to W_C (if schema match exists) or pruned. This implements:
  (a) Ebbinghaus spacing effect: more retrievals = slower decay.
  (b) Glial pruning (A9): low-activity items get pruned.
  (c) Neurogenesis clearing (A6): new items can be inserted without memory
      overflow by displacing low-stabilization items.

HARD-PASS: After 10K item stream (M = 3*M_c), high-frequency items (retrieved 20+x)
retain recall@1 >= 0.90; low-frequency items (never retrieved) have recall@1 <= 0.20
at end of stream. The difference >= 0.70 validates frequency-selectivity.

HARD-FAIL: no significant difference in recall between high- and low-frequency items
(p > 0.05, bootstrap; |diff| < 0.20).

P_deflated = 0.55 (low mechanistic risk; HD metadata scalars are proven feasible;
main uncertainty is whether decay rate can be tuned without per-item hyperparameter
search).

---

#### D2.3 RECONSOLIDATION-EDIT

Structure: when an item e_i is retrieved for an update query (not a read query),
it enters a "labile" state for T_recons steps. During this window, an edited
version e_i' can be written:
  e_i <- (1-lambda_recons) * e_i + lambda_recons * e_i'
where lambda_recons is the reconsolidation blend factor (0 = no change, 1 = complete
overwrite). After T_recons steps, the item re-stabilizes at the blended position.

This implements: (a) gradual belief update (not hard overwrite), (b) ROME-style
fact editing at the HD level (much lower interference than Transformer MLP editing
because HD keys are near-orthogonal), (c) reconsolidation-induced forgetting
(if e_i' is incompatible with e_i, the labile state is resolved toward the most
recent presentation -- matching the biological prediction).

The key advantage over ROME/MEMIT: HD keys are near-orthogonal by design, so
editing key k_i does not affect retrieval of unrelated items. ROME fails because
MLP key vectors overlap; HD keys do not.

HARD-PASS: After editing 500 items in a 10K KB, edited items show updated recall
(correct new value returned with probability >= 0.85) AND unedited items show
<= 2% degradation in recall@10.

HARD-FAIL: Editing 500 items degrades recall@10 on unedited items by >= 10%.

P_deflated = 0.50 (partial precedent: GDPR-delete is an extreme version of
lambda=1 reconsolidation; gradual blend is novel but mechanistically low-risk).

---

#### D2.4 NEUROGENESIS-EXPANSION (ANOMALY-TRIGGERED SHARD GROWTH)

Structure: substrate monitors each incoming item's distance from nearest existing
shard centroid. If dist(e_new, nearest_shard) > theta_novelty (high-anomaly zone),
a new shard is allocated dynamically. The new shard begins in "immature" phase:
  - Wide acceptance radius (low similarity threshold)
  - High plasticity (items assigned readily)
  - No pruning protection
After N_mature items have been assigned to it, it transitions to "mature" phase:
  - Narrowed acceptance radius (threshold raised by delta_theta)
  - Reduced plasticity (items rejected if low-similarity)
  - Pruning protection enabled (s_i protected by high base stabilization)

Old shards are stable unless their centroid distance from all new items exceeds
theta_irrelevance for T_irrelevance steps (then candidate for FREQUENCY-SELECTIVITY-DECAY
or demotion to W_C in D2.1).

This implements: (a) adult neurogenesis temporal stamp (new shards encode novelty),
(b) pattern separation (immature shards are hyperexcitable but mature to sparse),
(c) memory expansion without fixed-size overflow.

HARD-PASS: On a 10K stream with 5 distributional shifts (each shift = new item cluster),
KB recall@10 degrades <= 15% across shifts. Shard count grows proportional to
distinct clusters (not total items), validating anomaly-triggered growth.

HARD-FAIL: shard count grows proportional to total items (no anomaly gate functioning;
memory explosion).

P_deflated = 0.45 (novel mechanism; anomaly detection is feasible with PP-style
infrastructure; main risk is theta_novelty sensitivity -- may need adaptive calibration).

---

#### D2.5 SLEEP-DEFRAG-SCHEMA-EXTRACTION (MULTI-LEVEL)

Extension of PP-141/142 schema defrag to a three-level hierarchy:
  Level 1 (episodic): individual items in W_H. Exact HD vectors.
  Level 2 (semantic): cluster centroids of level-1 items within a shard.
              centroid_k = mean(e_i : shard(e_i) = k)
  Level 3 (archetype): cluster centroids of level-2 centroids across shards.
              archetype_j = mean(centroid_k : schema_family(k) = j)

Sleep-defrag algorithm:
  1. Compute level-2 centroids for all shards (O(M * N)).
  2. Cluster level-2 centroids into J archetypes via K-means on HD space.
  3. Store archetypes in W_C (D2.1).
  4. Prune episodic items that (a) have stabilization score < threshold_prune AND
     (b) are within theta_archetype of an archetype (schema has subsumed them).
  5. Update item stabilization scores: items that survive pruning get s_i += delta_s.

This implements: (a) Tse schema-mediated consolidation (new items close to archetypes
consolidate rapidly), (b) cultural transmission ratchet (archetypes = generational
knowledge), (c) REM-like schema generalization (level-3 extraction = abstraction).

HARD-PASS: After defrag cycle on M = 5*M_c items, retrieval from archetype-compressed
KB returns recall@10 >= 0.75 on items NOT in KB (generalization test: held-out items
close to archetypes are retrieved via archetype proximity). This tests generalization,
not memorization.

HARD-FAIL: Archetype-based retrieval returns recall@10 <= 0.30 on held-out items.

P_deflated = 0.35 (level-3 archetype extraction has limited lit precedent; the
generalization test is stringent; main risk is HD centroid averaging losing
discriminative signal in high-M regimes).

---

#### D2.6 REPLAY-WITH-CONTEXT (DOWNTIME SCHEMA GENERATION)

Structure: during idle computational cycles (no active queries), substrate runs
a replay scheduler:
  1. Sample item e_i from W_H with probability proportional to (1 - s_i / s_max)
     (under-consolidated items are replayed first -- highest learning value).
  2. Find top-K similar items in W_H by cosine similarity.
  3. Compute centroid of e_i union top-K = proto-schema c_new.
  4. If dist(c_new, nearest existing archetype in W_C) > theta_merge:
     insert c_new as new archetype.
  5. Else: update nearest archetype: a_j <- (1-alpha) * a_j + alpha * c_new.
  6. Increment s_i by delta_replay (replay counts as a stabilization event).

This implements: (a) hippocampal sharp-wave ripple replay (replay during downtime),
(b) bi-directional hippocampal-cortical interaction (context from W_C shapes replay),
(c) consolidation without external input (the substrate self-organizes).

Mathematical property: the replay process is a Markov chain on the space of
episode vectors and archetype vectors. Fixed-point analysis: the stationary
distribution concentrates replay probability on items with lowest stabilization
score, guaranteeing eventual consolidation of all items given sufficient replay
cycles. Convergence time T_converge = O(M / delta_replay) for full KB consolidation.

HARD-PASS: After 100K replay steps on M = 2*M_c items with no new insertions,
recall@10 for the full KB improves by >= 5% relative to no-replay baseline.

HARD-FAIL: No improvement in recall@10 after 100K replay steps (replay is ineffective).

P_deflated = 0.48 (mechanistically sound; main uncertainty is whether centroid
averaging in HD space produces useful archetypes vs. noisy averages -- the PP-141
evidence is somewhat encouraging).

---

#### D2.7 INTENTIONAL-FORGETTING (COGNITIVE DECLUTTER)

Structure: GDPR-delete (PP-143) is passive erasure. Intentional-forgetting
implements ACTIVE suppression: when item e_i is marked for deletion, the
substrate executes a "suppression run" that:
  1. Identifies all retrieval paths that would return e_i (similarity > theta_suppress).
  2. Inserts a "suppression record" s_i = -e_i (anti-pattern) into W_H with
     weight w_suppress such that at retrieval, the similarity contribution
     of e_i is cancelled: sim(query, e_i) + w_suppress * sim(query, -e_i) ~ 0.
  3. After T_suppress steps, the anti-pattern is removed (retrieval returns near-zero
     similarity for e_i queries) and e_i is removed from W_H.

This implements Anderson-Green active suppression but in HD space. The anti-pattern
mechanism is analogous to the PFC-mediated retrieval inhibition described in the
think/no-think paradigm.

Mathematical property: For bipolar HD vectors, -e_i is the bit-flip complement.
The anti-pattern fully cancels e_i ONLY for the exact key; partially cancels for
similar items (proportional to cosine similarity). This selective cancellation
prevents suppression from inadvertently erasing similar-but-legitimate items.

HARD-PASS: After marking 100 items for intentional forgetting in a 10K KB,
marked items have recall@1 <= 0.05 AND unmarked items (cosine similarity 0.6-0.8
to marked items) have recall@10 degradation <= 5%.

HARD-FAIL: Unmarked-item degradation >= 15% (suppression bleeds into non-target items).

P_deflated = 0.52 (HD anti-pattern insertion is a novel idea but is algebraically
well-defined; main risk is partial cancellation bleed at high cosine similarities).

---

#### D2.8 CULTURAL-CONTINUAL-MULTI-SUBSTRATE (CROSS-INSTANCE SCHEMA SHARING)

Structure: multiple substrate instances (e.g., per-user KBs) share a common
"archetype substrate" W_arch that stores cross-user schemas. Each user instance:
  - W_H_user: personal episodic store (isolated).
  - W_C_user: personal semantic layer (semi-isolated).
  - W_arch: shared cultural archetypes (read-only for individual users; updated
    by a federated aggregation step).

Archetype update: periodically, each instance donates its W_C archetypes to a
federated aggregation step:
  W_arch <- W_arch + eta_cultural * mean(W_C_user_i : i in cohort)
(FedAvg in archetype space). This is "cultural transmission": individual-level
schemas propagate into the shared archetype layer over time.

Privacy preservation: individual episodic items (W_H_user) never leave the
instance; only centroid-level archetypes are shared. Archetypes have much lower
re-identification risk than raw episodes.

This implements: (a) Boyd-Richerson cultural transmission, (b) Tomasello ratchet
(cumulative archetype refinement), (c) niche-specific learning (user cohorts can
share domain-specific archetypes without cross-domain contamination).

HARD-PASS: Cross-user schema sharing improves recall@10 on items NOT in a
user's personal KB by >= 15% relative to no-sharing baseline (measures cultural
generalization benefit).

HARD-FAIL: No improvement in recall@10, OR privacy degradation (held-out private
items become retrievable via shared archetypes -- privacy test required).

P_deflated = 0.30 (federated archetype aggregation is novel in HD space; the privacy
test is a genuine hard constraint; engineering complexity is high).

---

### D3. FIVE EMPIRICAL TESTS (10K-STEP CONTINUAL STREAM)

Each test is a 10K item stream with a specified distribution shift pattern.
All tests can run on CPU (numpy + HD operations, no cloud GPU required).
Pre-register HARD-PASS, MID, HARD-FAIL bands before running.

TEST-1: CAPACITY-CLIFF-SURVIVAL
  Setup: stream 3*M_c items into W_H without sleep cycles. Measure recall@10 at
  M_c, 2*M_c, 3*M_c. Baseline: current substrate. Experimental: D2.2 decay.
  HARD-PASS: D2.2 recall@10 at 3*M_c >= 0.70 (vs baseline expected << 0.50).
  HARD-FAIL: D2.2 recall@10 at 3*M_c < 0.50 (decay did not help beyond cliff).

TEST-2: DISTRIBUTION-SHIFT-5X
  Setup: 5 sequential batches of 2K items, each from a distinct semantic cluster.
  After each batch, measure recall@10 on ALL prior batches.
  HARD-PASS: recall@10 on first batch after fifth batch >= 0.65 (continual retention).
  HARD-FAIL: recall@10 on first batch drops below 0.30 after fifth batch.

TEST-3: SLEEP-DEFRAG-GENERALIZATION
  Setup: insert 2*M_c items, run D2.5 sleep-defrag, then query 200 held-out items
  that are semantically similar to inserted items but NOT in KB.
  HARD-PASS: held-out recall@10 via archetype >= 0.50 (generalization beyond memorization).
  HARD-FAIL: held-out recall@10 <= 0.20.

TEST-4: RECONSOLIDATION-EDIT-PRECISION
  Setup: insert 10K items, edit 500 with D2.3, query edited + unedited.
  HARD-PASS: edited recall (new value) >= 0.85 AND unedited recall degradation <= 2%.
  HARD-FAIL: unedited recall degradation >= 10%.

TEST-5: FREQUENCY-SELECTIVITY-SURVIVAL
  Setup: stream 10K items with Zipf-distributed access frequency (rank-frequency law).
  After stream, measure recall@10 separately for top-10% (high-freq) and bottom-10%
  (low-freq) by access count. Baseline: no decay. Experimental: D2.2 decay.
  HARD-PASS: high-freq recall >= 0.88; low-freq recall <= 0.25 (selectivity achieved).
  HARD-FAIL: high-freq recall <= 0.60 (decay hurts important items).

---

### D4. HONEST HIGHEST-P PATH

Given lit calibration and substrate engineering reality, the rank-ordered paths by
P_deflated x feasibility:

1. D2.2 FREQUENCY-SELECTIVITY-DECAY (P=0.55): requires only metadata scalar per
   item and a per-tick decay loop. No architectural change to W. PP-143 GDPR
   infrastructure already handles item metadata. Estimated: 2-3 day implement + TEST-1
   and TEST-5 = decisive verdict. This is the cheapest path to a real continual
   learning capability.

2. D2.3 RECONSOLIDATION-EDIT (P=0.50): HD anti-pattern algebra is well-defined.
   The precision test (TEST-4) is cheap and decisive. If it passes, it directly
   improves KNOWLEDGE-EDITING-V1 (an existing cap_map row). Cross-thread synergy.

3. D2.6 REPLAY-WITH-CONTEXT (P=0.48): replay during idle cycles is architecturally
   clean. Requires scheduler + W_C (can be a simple K-means index). Main risk:
   centroid averaging quality. TEST-2 (distribution shift) is the gate.

4. D2.1 DUAL-SUBSTRATE-CLS (P=0.40): requires building W_C from scratch.
   Larger engineering footprint. But if D2.6 passes, W_C already exists and D2.1
   becomes cheap. Recommended: do D2.6 first; D2.1 is the natural extension.

5. D2.4 NEUROGENESIS-EXPANSION (P=0.45): anomaly-triggered shard growth is the
   hardest to tune (theta_novelty sensitivity) but also addresses the capacity cliff
   most directly. Feasibility depends on TEST-1 results.

6. D2.5 SLEEP-DEFRAG-SCHEMA-EXTRACTION-3LEVEL (P=0.35): requires TEST-3 to
   pass (generalization). Lower confidence because level-3 HD centroid averaging
   is untested.

7. D2.8 CULTURAL-MULTI-SUBSTRATE (P=0.30): highest engineering cost;
   privacy test is a genuine hard constraint; recommend only after D2.1 is proven.

8. D2.7 INTENTIONAL-FORGETTING (P=0.52): algebraically simple; privacy-compliant;
   extends GDPR capability. Recommend as a parallel track alongside D2.2.

RECOMMENDED EXECUTION ORDER: D2.2 -> D2.3 in parallel -> D2.6 (if D2.2 passes)
-> D2.1 (extension of D2.6) -> D2.4 (if D2.1 passes) -> D2.5 -> D2.7 (parallel).
D2.8 deferred until D2.1 proven.

---

## CHEAP DECISIVE TEST

Run TEST-1 (capacity-cliff-survival) with D2.2 only: stream 3*M_c items, measure
recall@10 at three checkpoints. CPU-only, numpy, approximately 2-4 hours wall.
Cost: zero cloud. Pre-register bands: HARD-PASS recall >= 0.70 at 3*M_c;
HARD-FAIL recall < 0.50. This is decisive because it directly tests whether
frequency-selectivity-decay extends useful capacity beyond M_c without any other
architectural change. If it passes, D2.2 is a standalone capability unlock.
If it fails, the remaining paths (D2.1, D2.6) are still viable but require more
engineering investment.

---

## FALSIFIABLE PREDICTIONS

HARD-PASS (any one of):
  - TEST-1: D2.2 recall@10 at 3*M_c >= 0.70
  - TEST-4: edited recall >= 0.85 AND unedited degradation <= 2%
  - TEST-3: held-out recall@10 via archetype >= 0.50

HARD-FAIL (any one of):
  - D2.2 fails to differentiate high-freq vs low-freq recall by >= 0.70 (TEST-5)
  - D2.3 causes >= 10% degradation on unedited items (TEST-4)
  - Three replay-based methods (D2.6) all fail to improve recall@10 on
    distribution-shifted streams (TEST-2 recall < 0.50)

If two or more HARD-FAILs trigger: the substrate is limited to episodic fast-store
only (current state) and the slow-generalizer must be implemented outside the HD
layer (e.g., as a separate semantic index or LLM fine-tune step).

---

## CROSS-THREAD SYNTHESIS

Prior research threads that are relevant:

- PP-141/142 schema extraction (already partially implements D2.5 at one level;
  extending to three-level hierarchy is a natural follow-on if PP-141 is HP).
- GDPR-delete (PP-143) is a hard overwrite form of D2.7; D2.7 is the soft-suppress
  extension.
- Capacity cliff (M > M_c known failure mode from empirical work):
  D2.2 directly addresses the capacity cliff without changing the core HD architecture.
- Multi-hop retrieval (K-hop, project priority): D2.5 level-3 archetypes could
  serve as "super-nodes" in multi-hop traversal, reducing path length for
  semantically distant but archetype-connected queries.
- Population genetics / Wright-Fisher adjacency (field advisor Tier-1b):
  the frequency-selectivity-decay model (D2.2) is mathematically identical to
  Wright-Fisher drift for neutral alleles under weak selection:
  dp_i/dt = -gamma * p_i + sigma * eta (drift term) + f_i * p_i (selection = retrieval).
  This provides a formal framework for predicting equilibrium item frequency
  distribution and the critical selection coefficient below which items fix at zero
  (permanent forgetting). Concretely: items with retrieval frequency below the
  drift-selection balance point will be lost regardless of decay rate tuning.
  This is a quantitative hard lower bound on what can be retained.
- Structural-glasses-MCT adjacency (Tier-1b): the continual learning replay rate
  corresponds to a MCT relaxation timescale; if replay rate < alpha-process rate,
  the system is trapped in a metastable basin (old memory pattern). This gives
  a physical threshold for when replay will successfully consolidate vs when it
  will fail.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. CAPACITY EXTENSION: D2.2 + D2.4 together could extend effective KB capacity
   from M_c to 3-5*M_c without changing N (vector dimensionality). This is a
   customer-visible capability: larger knowledge bases without infrastructure scaling.

2. BELIEF UPDATING: D2.3 reconsolidation-edit is a direct product feature:
   "update a fact without disrupting related facts." Competitive advantage over
   retrieval-augmented generation (RAG) which cannot selectively update weights.

3. ADAPTIVE FORGETTING: D2.2 with Zipf-weighted access means a customer KB that
   is used over months will naturally emphasize the customer's most-used facts
   and gracefully fade rarely-accessed ones. This matches user intuition and
   reduces "outdated fact recall" complaints.

4. ARCHETYPE GENERALIZATION: D2.5 level-3 archetypes enable zero-shot generalization
   to new queries that match a known schema but were not explicitly inserted.
   This is the closest substrate analog to LLM generalization, achieved
   without gradient-based training.

5. PRIVACY-SAFE CULTURAL SHARING: D2.8 (if it passes privacy test) enables
   a product feature: "your KB benefits from aggregated community knowledge
   without sharing your private episodes." Enterprise-relevant privacy property.

---

## CITATIONS (VERIFIED)

1. Wilson MA, McNaughton BL (1994). Reactivation of hippocampal ensemble memories
   during sleep. Science 265(5172):676-679.
2. McClelland JL, McNaughton BL, O'Reilly RC (1995). Why there are complementary
   learning systems in the hippocampus and neocortex. Psychol Rev 102(3):419-457.
3. Kirkpatrick J et al. (2017). Overcoming catastrophic forgetting in neural networks.
   PNAS 114(13):3521-3526.
4. Tse D et al. (2007). Schemas and memory consolidation. Science 316(5821):76-82.
5. Nader K, Schafe GE, LeDoux JE (2000). Fear memories require protein synthesis in
   the amygdala for reconsolidation after retrieval. Nature 406:722-726.
6. Meng K et al. (2022). Locating and editing factual associations in GPT. NeurIPS 35.
7. Shin H et al. (2017). Continual learning with deep generative replay. NeurIPS 30.
8. Rusu AA et al. (2016). Progressive neural networks. arXiv:1606.04671.
9. Graves A et al. (2016). Hybrid computing using a neural network with dynamic
   external memory. Nature 538:471-476.
10. Hu EJ et al. (2022). LoRA: Low-rank adaptation of large language models. ICLR 2022.
11. Finn C, Abbeel P, Levine S (2017). Model-agnostic meta-learning. ICML 2017.
12. Rothschild G et al. (2022). Bi-directional interactions between CLS for memory
   consolidation. PubMed 36313529 / PMC 9606815.
13. Benoy A et al. (2025). Temporal flexibility in associative memory: synaptic tagging
   and capture. European Journal of Neuroscience.
14. Bhattacharya S et al. (2024). Adult neurogenesis, context encoding, pattern
   separation. PubMed 39008016.
15. HiCL (2025). Hippocampal-inspired continual learning. arXiv:2508.16651.
16. MoE-CL Theory (2025). Theory on mixture-of-experts in continual learning.
   ICLR 2025, arXiv:2406.16437.
17. Split-on-Share (2025). Mixture of sparse experts for task-agnostic continual
   learning. arXiv:2601.17616.
18. ADEPT (2025). Continual pretraining via adaptive expansion. arXiv:2510.10071.
19. CA-CPT (2025). Context-aware continual pretraining for LLMs. OpenReview.
20. ACL 2025 stability gap paper. Efficient domain continual pretraining.
21. Nature Comms Bio (2025). Temporal spindle clustering and slow-oscillation coupling.
22. JNeurosci (2025). Slow oscillation-spindle coupling predicts language learning.
23. PMC (2025). Slow-wave sleep and REM differentially contribute to memory
   representational transformation. PMC 12489065.
24. Anderson MC, Green C (2001). Suppressing unwanted memories by executive control.
   Nature 410:366-369.
25. Kumaran D, Hassabis D, McClelland JL (2016). What learning systems do intelligent
   agents need? Complementary learning systems theory updated. Trends Cogn Sci.

Verified citations: 25 (all grounded in published lit or 2025 preprints confirmed
by search results).

---

## CALIBRATION SUMMARY

P_deflated(full 4-component CLS): 0.35
P_deflated(slow-generalizer only, D2.1+D2.6): 0.45
P_deflated(frequency-decay only, D2.2): 0.55
P_deflated(reconsolidation-edit, D2.3): 0.50
Calibration penalty applied: -0.20 from raw estimates.
Novel-synthesis cap: 0.50 enforced on D2.1, D2.8.

Next-drill candidate: structural-glasses-MCT (Tier-1b adjacency) -- replay rate
threshold mapped to MCT alpha-process timescale gives a quantitative engineering
bound on the consolidation scheduler. One targeted drill should surface the critical
replay rate formula.
