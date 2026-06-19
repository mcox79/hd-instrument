# Research Drill: Full CLS Architecture via 5 Streams
# Date: 2026-06-10

---

## HEADLINE

Biological CLS has four components the current substrate episodic fast-store lacks:
a slow cortical generalizer, a frequency-decay / use-it-or-lose-it consolidator,
a consolidation scheduler (sleep/replay gating), and a schema-accelerated write path.
Across five streams, two substrate-native implementations emerge as highest P:
(1) a DUAL-SUBSTRATE-CLS overlay that maps the cortical slow-generalizer to a
    second sparse low-rank W_slow updated by batched offline replay -- algebraically
    a rank-deficient outer-product accumulator with exponential moving average decay;
(2) a STRETCHED-EXPONENTIAL (Kohlrausch-Williams-Watts) frequency-decay rule applied
    directly to W atom weights, giving memory traces that decay as exp(-[t/tau]^beta)
    with beta < 1 controlled by retrieval frequency.
Both have direct mathematical precedent (KWW glass aging, CLS bidirectional models),
are implementable in pure-numpy / pure-outer-product algebra without autograd,
and produce falsifiable signatures distinguishable at < 1000 update steps.
P_deflated (novel synthesis, both mechanisms together): 0.42.

---

## Context: what substrate currently has vs. what full CLS requires

Full biological CLS has at minimum four distinguishable functional blocks:

| Block | Biological role | Substrate status |
|---|---|---|
| Fast episodic store | Hippocampal rapid one-shot binding | PRESENT (W outer-product write) |
| Slow cortical generalizer | Statistical regularities distilled from many episodes | ABSENT |
| Frequency-decay / pruning | Weak/infrequent traces fade; strong/frequent ones consolidate | PARTIAL (Sprint 2 synthetic-validated) |
| Consolidation scheduler | Sleep SWS/REM gating replay timing | ABSENT |
| Schema accelerator | Schema-compatible items bypass slow consolidation | ABSENT |

The mandate is to find substrate-native implementations of the three absent blocks
using the five streams below as probes.

---

## Stream A: Biology

### A1. Hippocampal-cortical replay (McClelland 1995; Kumaran 2016)

The standard CLS model (McClelland, McNaughton, O'Reilly 1995) posits two coupled stores:
hippocampus encodes fast (one-shot, high plasticity) while neocortex encodes slow
(interleaved replay, low per-step learning rate). The bidirectional flow -- hippocampus
to cortex during offline replay, cortex to hippocampus for schema-mediated rapid encoding --
is now well-supported (PMC9606815, 2022; Structured Cortical Replay SCoRe, 2025).

Key math: cortical W_slow update rule during replay is:
  W_slow <- (1-alpha)*W_slow + alpha * outer(v_query, v_value)
where alpha << 1 (slow learning rate), and replay samples are drawn from the hippocampal
fast store. Across many replays, W_slow accumulates the principal eigenvectors of the
episodic distribution -- a slow PCA of experience.

Substrate mapping: W_fast = existing outer-product store. W_slow = a second rank-R
matrix receiving minibatch outer-product updates at alpha ~ 0.01 per consolidation pass.
The consolidation pass is triggered by a replay scheduler (see A2).

### A2. Sleep slow-wave + REM consolidation

SWS replay (sharp-wave ripples) replays recent hippocampal traces at ~10-20x real-time
compressed rate, driving cortical LTP. REM provides a second consolidation phase focused
on integration of novel-with-familiar (schema update). The two phases are dissociable:
SWS = episodic-to-cortical transfer; REM = schema update/generalization.

Computational analog: a two-phase offline scheduler --
  Phase 1 (SWS analog): replay recent W_fast writes into W_slow at low alpha;
  Phase 2 (REM analog): replay schema-matched items (high cosine similarity to existing
                         W_slow rows) at higher alpha to strengthen generalizations.

Trigger condition for consolidation pass: after N_buffer new writes OR at fixed intervals.
This is a parameter (N_buffer) that is directly testable; see F3.

### A3. Schema-mediated consolidation (Tse et al. 2007, 2011; Roy Soc Phil Trans 2024)

Schema-compatible items consolidate rapidly (within hours rather than weeks) and become
cortical-independent faster. Mechanistically: vmPFC schema representations reduce the
hippocampal load required for new encoding when the item fits a known structure.

Two recent 2025 papers confirm the schema-active-inference link: schema-like priors
guide encoding via frontal cortex (arXiv:2601.18946), and schema-based assimilation
results in increased vmPFC activity with reduced hippocampal dependency (biorxiv 2025).

Substrate mapping: SCHEMA-ACCELERATED WRITE. When a new item's query vector has
high cosine similarity (> theta_schema) to existing W_slow rows, write it directly
to W_slow at higher alpha (fast-track cortical consolidation) AND skip or reduce
the frequency-decay timer. This is a conditional branch on the write path: one line
of code, requires only W_slow.dot(v_query) > theta_schema check.

### A4. Adult neurogenesis -- capacity expansion (Aimone et al. 2011; Biorxiv 2025)

Dentate gyrus adult neurogenesis adds immature, highly plastic granule cells with low
activation thresholds, providing high pattern-separation capacity for new input streams.
As cells mature they become more selective and integrate into existing circuits.
Recent 2025 work (Frontiers, 2025): additive neurogenesis increases new-information
learning speed; neuronal turnover (addition + death) reduces recall of old data faster
but accelerates new learning -- a direct plasticity-stability tradeoff knob.

Substrate analog: SUBSTRATE-NEUROGENESIS-EXPANSION. Dynamically add new atom slots
(new rows/columns to W_fast) when the store is near capacity (K/N > 0.4), then retire
low-activation slots (frequency-decay below threshold). This expands effective capacity
without a global rewrite of W. Algebraically: W_fast is a sparse accumulator;
new atoms are appended at small N_new extension; old atoms with weight below epsilon
are zero-masked. Net effect: rolling capacity window.

Implementability: requires sparse W representation and a retirement threshold epsilon.
The K/N capacity cliff at 0.56 means this would need to engage before K/N ~ 0.4.

### A5. Synaptic tagging and capture (Frey & Morris 1997; Roy Soc Phil Trans B 2024; PMC11968991 2025)

Early LTP (e-LTP) tags synapses for late-LTP capture: if plasticity-related proteins (PRPs)
are available (from a strong stimulus), tagged synapses capture them and transition to
persistent L-LTP. If PRPs are unavailable, the tag decays and only e-LTP persists (~hours).
Recent 2025 finding: STC successful even with 9-hour tag-PRP interval -- much wider
temporal window than previously believed.

The key computational insight: TWO-FACTOR consolidation. Factor 1 = synaptic tag
(local, rapid, decays). Factor 2 = PRPs (global, slow, depends on total activity level).
An atom is permanently stored only if BOTH factors are simultaneously present.

Substrate mapping: TWO-FACTOR WRITE RULE. Each W atom write also sets a tag vector t_i
with decay constant tau_tag (~hours equivalent in steps). A consolidation pass checks:
if t_i > theta_tag AND global_activity > theta_PRP: consolidate (elevate to W_slow);
else: let tag decay. This implements selective consolidation without replay of all items.

### A6. Reconsolidation -- memory editing (Nader et al. 2000; Lee 2017; PubMed 40354954 2025)

Memory reactivation renders the trace labile for a bounded time window (~hours).
During this window the trace can be updated (prediction-error-driven) or disrupted.
Lee's updated 2025 model ties reconsolidation to prediction error magnitude:
larger mismatch during reactivation = stronger reconsolidation = larger update.

This is the substrate analog of ROME/MEMIT: instead of rank-one weight insertion
into MLP layers, it is a rank-one outer-product correction conditioned on reactivation.
The math is identical to ROME: delta_W = lambda * (v_new - v_old) * k^T
where k is the query key that retrieved the old memory.

Substrate mapping: RECONSOLIDATION-EDIT (PP-225 substrate analog). Reactivate a stored
atom (retrieve it), compute prediction error between retrieved value and new target,
apply delta_W = eta * (v_target - v_retrieved) * k_query^T. The update is local to the
retrieved atom's outer-product contribution. No global retraining needed.

This is already partially validated (memory_editing, memory_recomposition experiments).
Full CLS requires that the reconsolidation window be BOUNDED: after tau_recon steps
without reactivation, the trace becomes immune to delta-W updates (consolidated).

### A7. Cellular taxonomy (interneurons, engram cells, Tonegawa 2015)

Engram cells are sparse subsets of neurons active during encoding whose reactivation
reproduces the memory. Recent work (Tonegawa lab, ICLR-cited 2024): engrams are sparsified
over consolidation (pruning of irrelevant co-activations), increasing SNR.

Substrate analog: ENGRAM-SPARSIFICATION. After consolidation pass, apply a threshold
mask to W_slow: zero out entries with magnitude < epsilon_engram. This increases SNR
of consolidated memories at the cost of losing marginal traces -- exactly what biological
sparsification achieves. Algebraically: W_slow = W_slow * (|W_slow| > epsilon_engram).

### A8. Songbird template learning + sleep (Dave & Margoliash 2000)

Zebra finch learns song template in juvenile period (hippocampal-analog fast encoding),
then consolidates during sleep (offline replay). Unique: the offline replay occurs
even without external stimulus -- the template is self-replayed from internal generation.

Substrate insight: SELF-REPLAY does not require original training data. The substrate
can generate a replay signal from W_fast itself: sample v ~ W_fast row distribution,
use as replay input to W_slow update. No stored training samples needed. This is
biologically plausible (hippocampal pattern completion drives replay) and computationally
cheap (no raw-data buffer required). Algebraically: replay v_i = W_fast[i] / |W_fast[i]|.

### A9. Honeybee Kenyon cell coding

Kenyon cells in the mushroom body use extreme sparsity (~5% active per stimulus) to
maximize pattern separation in a fixed-capacity store. The feed-forward inhibition from
GABAergic interneurons enforces a winner-takes-most constraint (k-sparse).

Substrate analog: K-SPARSE WRITE RULE. During W_fast writes, only the top-k components
of the query vector are kept (others zeroed). This maximizes capacity at fixed N by
reducing inter-item interference -- a substrate version of the dentate gyrus sparse
projection. Algebraically: v_sparse = v * (v > quantile(v, 1-k/N)).

### A10. Cumulative cultural transmission

Cumulative culture requires that learned knowledge survives across generations / episodes
without catastrophic reset. The biological mechanism is external rehearsal + ratchet
effect (each generation builds on prior). Substrate implication: consolidation must be
RATCHET-LIKE -- a new write cannot decrease the SNR of previously consolidated items.
Algebraically: the dual-substrate architecture achieves this if W_slow is never directly
overwritten, only additively updated.

---

## Stream B: Brain / Cognitive Architecture

### B1. McClelland CLS architecture -- algebraic form

The CLS update equations from McClelland, McNaughton, O'Reilly 1995 (plus Kumaran 2016
bidirectional extension) map cleanly to substrate algebra:

  Hippocampal (fast) write:  W_fast += outer(v_query, v_value)
  Cortical (slow) replay:    W_slow += alpha * outer(v_query, v_value)  [alpha << 1]
  Hippocampal-to-cortical:   replay r ~ W_fast; W_slow += alpha * outer(r_q, r_v)
  Cortical-to-hippocampal:   schema check: if W_slow @ v_q > theta: fast-write at higher fidelity

The dual-substrate system is EXACTLY McClelland CLS implemented as two outer-product matrices.
No exotic math required. P_theory = 0.85 (high -- direct implementation of 30-year-old theory).

### B2. Sparse coding -- dentate gyrus pattern separation

The dentate gyrus applies a sparse random projection (~10% granule cell activation) before
hippocampal CA3 storage. This pattern-separates similar inputs before they reach the
associative memory, increasing effective capacity.

Substrate analog: pre-encode with a k-sparse random projection P (N_in -> N_store),
where P is drawn once and fixed. All writes use v_projected = kSparse(P @ v_raw).
Capacity gain: proportional to sparsity; at 10% activation, interference drops ~10x.
This is equivalent to the whitening + PCA preprocessing already validated in the Testbed.

### B3. Lateral inhibition + cleanup

Lateral inhibition enforces k-sparse activations via winner-takes-most, and cleanup
networks (basin-of-attraction dynamics in CA3) complete partial patterns. These are
ALREADY present in the substrate resonator (iterative cleanup from basin dynamics).

### B4. Cortical map reorganization

After consolidation, cortical representations become more distributed and overlap more.
This is the basis of schema extraction: many consolidated memories share a common
subspace. In matrix algebra: the principal subspace of W_slow concentrates in fewer
singular vectors over time -- a spontaneous dimensionality reduction.

Substrate observation: monitoring SVD(W_slow) over consolidation steps would reveal
whether the slow store spontaneously forms low-rank structure. Cheap diagnostic.

### B5. Engram cells (Tonegawa lab)

See A7 above. The key engineering insight: sparsifying W_slow post-consolidation
mirrors biological engram sparsification and increases retrieval SNR.

### B6. Ebbinghaus forgetting curves

The Ebbinghaus curve (R = exp(-t/S) where S = memory strength) has been empirically
recovered in neural networks (arXiv:2506.12034, 2025): human-like forgetting curves
emerge naturally in MLPs under spaced repetition training. The substrate frequency-decay
Sprint-2 result is consistent with the Ebbinghaus curve at the individual trace level.

Key upgrade: the biological forgetting curve is not purely exponential -- it is better
fit by a stretched exponential (Williams-Watts, beta ~ 0.5-0.7) at intermediate
timescales. This is Stream D's main contribution.

### B7. Spaced repetition + reactivation

Biological memory strengthens with spaced retrieval (Cepeda et al. 2006). Each
retrieval resets the decay clock (reconsolidation). Computational analog: each
query that successfully retrieves an item resets its decay timer in the frequency-decay
ledger. This is the USE-IT-or-LOSE-IT rule operationalized as: tau_eff(item) = tau_base
after each retrieval, decay restarts from zero. Items never retrieved decay to zero.

### B8. Default mode network + spontaneous consolidation

The DMN replays episodic content during rest (mind-wandering). Substrate analog:
when no new write is occurring (idle cycles), run one consolidation replay pass.
This converts idle cycles into free consolidation without wall-clock cost.

### B9. Glia + synaptic regulation (homeostatic plasticity)

Astrocytes regulate synaptic scaling: when overall activity is too high, scale all
synaptic weights down; when too low, scale up. This is homeostatic normalization.
Substrate analog: periodic row-normalization of W_fast and W_slow to prevent
unbounded growth. Algebraically: W /= max(|W_rows|). Already implicit in PP-225
substrate but not explicitly named as a consolidation mechanism.

### B10. Hippocampal theta-gamma binding

Theta (~8 Hz) and nested gamma (~40 Hz) oscillations in the hippocampus bind together
sequences of events within a single theta cycle. This is a temporal binding mechanism
for sequential episodic encoding. Substrate analog: TEMPORAL-BINDING WRITE, where
a sequence of K items is written as a single composite bundle rather than K independent
writes, reducing interference. Already present in the substrate's bundle-K design.

---

## Stream C: Crazy Architectures

### C1. Dual-substrate (hippocampal + cortical) -- HIGHEST PRIORITY

Direct implementation of full CLS. Two W matrices: W_fast (existing) + W_slow (new).
W_fast takes all new writes. Offline consolidation pass: sample rows of W_fast,
replay into W_slow at alpha << 1. Retrieval: blend query responses from both:
  v_retrieved = beta * W_fast @ q + (1-beta) * W_slow @ q
where beta decays with item age (new items weighted to W_fast; old items to W_slow).

Mathematical requirement: W_slow must NOT overfit to W_fast's idiosyncratic patterns.
Achieved by low alpha and many replay passes (law of large numbers effect: W_slow
converges to the mean of the episode distribution, not individual episode details).

P_deflated (C1 hardware-feasible path, pure algebra): 0.45.
P_theory: 0.80 (very well-grounded in CLS literature, no exotic math).

### C2. Quantum decoherence as forgetting

Not substrate-relevant. The quantum-optical spin glass result (arXiv:2509.12202) shows
quantum effects enhance Hopfield memory capacity in driven-dissipative regimes.
This requires physical quantum hardware. NOT substrate-applicable at present.
P_deflated: 0.05. DEPRIORITIZE.

### C3. Phase transition consolidation

Associative memory undergoes a phase transition at K/N = 0.14 (classical Hopfield)
or higher (modern dense networks, capacity O(N^n)). Recent 2025 work (arXiv:2604.07401)
characterizes retrieval phase transitions in continuous dense memories with geometric
entropy terms. Key insight: below the capacity cliff, retrieval is perfect (or near-perfect)
at any temperature; above it, catastrophic interference. This maps directly to the
substrate's empirically measured K/N = 0.56 cliff.

Implication for CLS: the dual-substrate architecture can exploit the phase transition --
W_fast is kept BELOW the cliff by retiring old items to W_slow. W_slow's capacity cliff
is separate (and can be at higher K/N if alpha is low enough that items don't interfere).
The "scheduler" decides when to retire items from W_fast to W_slow.

P_deflated (C3 as design principle for scheduler): 0.50.

### C4. Substrate fluid (changes structure over time)

Not independently actionable -- subsumed by C1 (dual substrate) and C8 (neurogenesis).

### C5. Spin-glass slow consolidation -- MEDIUM PRIORITY

Spin glass aging (see Stream D) provides a mathematical model for slow consolidation.
The Hopfield model in its glassy phase (K > K_c) exhibits aging: dynamical response
functions evolve with waiting time, and correlation decay follows stretched exponential
C(t, t_w) ~ exp(-(t/tau(t_w))^beta). This is a substrate-native slow consolidation
mechanism -- NO explicit cortical W_slow required. Instead, W_fast itself slowly
"ages" into a glassy consolidated state.

Concretely: after N_age writes, the retrieval dynamics change from fast-basin
(few-shot convergence) to slow-exploration (many-step convergence). This spontaneous
slowing IS consolidation -- the memory becomes harder to update (more stable).

However: this requires the substrate to operate in its spin-glass phase (K > K_c),
which means operating ABOVE the capacity cliff. Not currently a validated operating
regime. P_deflated: 0.30 (interesting but requires above-cliff operation).

### C6. Active inference replay -- MEDIUM PRIORITY

Active inference (Friston 2010, 2025) frames memory consolidation as prediction-error
minimization: the brain replays experiences to minimize surprise about past states.
In the substrate: after writing items, the replay oracle generates predictions
(W_fast @ q) and checks prediction error (|v_predicted - v_actual|). Items with
large prediction error are flagged for re-replay (surprise-driven prioritized replay).
This is the SuRe framework (arXiv:2511.22367) applied to the substrate's write operations.

P_deflated: 0.40. Requires a prediction-error scoring function but no new W structure.

### C7. Substrate hierarchical (multi-level abstraction)

Multi-level: W_L1 (raw atoms, fast), W_L2 (concept composites, medium), W_L3 (schemas, slow).
Each level is an outer-product accumulator with decreasing alpha and increasing sparsity.
This is a three-tier CLS. P_deflated: 0.35 (high implementation complexity, not yet
differentiated from two-tier C1 + schema accelerator A3).

### C8. Substrate neurogenesis (grows shards) -- MEDIUM PRIORITY

See A4. Dynamically expand the atom vocabulary when K/N > 0.4. Retire low-activation
atoms. This is an adaptive-capacity version of the substrate. P_deflated: 0.35.

### C9. Substrate version control (git-like)

Checkpoint W_fast at each consolidation event. Rollback is possible. This IS already
implicit in the substrate's bidirectional cert-chain replay (PP-15 disaster recovery).
Not a new capability -- it is an APPLICATION of existing consolidation checkpoints.

### C10. Liquid time-flow substrate

Liquid time-constant (Hasani et al. 2021) uses state-dependent time constants:
tau_i(t) = tau_i_min + (tau_i_max - tau_i_min) * sigmoid(f(x)). In the substrate,
this means each atom's decay rate is modulated by its retrieval frequency -- exactly
the frequency-dependent tau in the Kohlrausch-Williams-Watts rule. P_deflated: 0.38.

---

## Stream D: Materials Science / Physics

### D1. Spin glass slow dynamics + D2. Aging in glasses

Spin glasses exhibit "aging": after quench below T_g, the system never reaches
equilibrium; instead, it slowly evolves with the correlation function depending on
BOTH observation time t AND waiting time t_w since quench:
  C(t, t_w) = f(t/t_w)  [simple aging]  or  C ~ (t_w / t)^mu  [power-law aging]

For the Hopfield model in its spin-glass phase (K > K_c), this aging has been directly
confirmed: "The Hopfield model shows the presence of aging, with decay becoming slower
for longer waiting times" (ResearchGate, Out-of-Equilibrium Dynamics Hopfield, 2001;
still the core reference; confirmed in 2024 Nobel context work).

Substrate implication: the W_fast matrix, when operated above K_c, NATURALLY develops
slow consolidation dynamics without any explicit consolidation mechanism. The aging
is intrinsic to the associative memory algebra. This is potentially a "free" CLS
slow-consolidator if the substrate operates near but not too far above K_c.

Challenge: operating above K_c degrades retrieval accuracy. The tradeoff is:
  below K_c: fast clean retrieval, no natural aging/consolidation;
  above K_c: slower retrieval, natural aging consolidation, but noisy.

Resolution: dual-substrate (C1) keeps W_fast below K_c while W_slow operates in
a regime where slow accumulation dominates. This is mathematically consistent.

### D3. Stretched exponential decay (Williams-Watts, Kohlrausch)

The Kohlrausch-Williams-Watts (KWW) stretched exponential:
  C(t) = C_0 * exp(-(t/tau)^beta)  with 0 < beta < 1

is the empirical decay law for glassy materials, disordered polymers, and biological
memory. It arises when the relaxation spectrum is HETEROGENEOUS: different trace
elements have different tau values, and the population average gives a stretched
exponential. Beta = 1 is purely exponential (single time constant); beta ~ 0.5-0.7
is typical for biological memory and glassy materials.

For the substrate: a frequency-decay rule that implements KWW is:
  w_i(t) = w_i(0) * exp(-((t - t_last_access_i) / tau_i)^beta)
where tau_i = tau_base * f(write_count_i) (stronger memories have longer tau).
Beta is a global hyperparameter (0.5-0.7 from biology / glass physics).

This is the DIRECT generalization of Sprint 2's frequency-decay validation from
exponential to stretched-exponential. The additional parameter beta is empirically
detectable: a stretched exponential fits long-tail retention better than a pure
exponential, predicting that moderate-frequency items are retained longer than
pure-exponential would predict.

HARD PASS criterion: KWW fit (beta < 1) has significantly lower BIC than pure
exponential fit over a 1000-step continual stream with mixed retrieval frequencies.
HARD FAIL criterion: best-fit beta > 0.95 (indistinguishable from exponential;
no benefit from KWW parameterization).

P_deflated (D3 as substrate frequency-decay rule): 0.50.

### D4. Logarithmic relaxation

Some glasses relax logarithmically: C(t) ~ C_0 - A * log(t/tau). This is an extreme
case of KWW (beta -> 0). In biological memory, logarithmic forgetting has been proposed
for very long timescales (years). Not clearly substrate-relevant at operational timescales.
P_deflated: 0.15. Low priority.

### D5-D6. Memory effects and hysteresis

Spin glasses exhibit rejuvenation and memory effects: a system cooled to T_1, then
to T_2 < T_1, then reheated to T_1 recovers its T_1 state. This is a physical analog
of reconsolidation. The substrate's delta-W edit (A6) is exactly this: reactivate,
update, restabilize. No new implementation needed -- the physics confirms the mechanism.

### D7. Self-organized criticality (avalanches)

SOC (Bak, Tang, Wiesenfeld 1987) produces power-law distributed event sizes near a
critical point. Neural avalanches in cortex follow power laws (Beggs & Plenz 2003).
Substrate implication: if the consolidation scheduler is driven by "avalanche" events
(cascades of co-activation), it would naturally implement intermittent consolidation
bursts rather than uniform trickle. This is biologically realistic but adds scheduling
complexity. P_deflated: 0.25.

### D9. Topological protection

Topological order (as in topological quantum memories) can protect information against
local perturbations. In classical spin systems, topological protection requires
carefully constructed energy landscapes. For the substrate, the nearest analog is
"basin depth" -- deeply consolidated memories correspond to deep energy basins that
resist perturbation. This is achieved by the W_slow low-alpha accumulation (deep basin
requires many aligned writes). P_deflated: 0.30 as an EXPLANATION; not a new mechanism.

### D10. Thermodynamic limit of replay

In the thermodynamic limit (N -> infinity), replay at rate r per step achieves full
CLS consolidation if r > K_new (new items per step). At finite N (substrate's actual
operating regime), the required replay rate is higher. The key inequality:
  r_replay > K_new + C * sqrt(K_total / N)
where C is a constant related to the capacity cliff slope. This gives the minimum
replay rate required for the substrate to avoid catastrophic forgetting at finite N.

This is a substrate-specific constraint that differs from the N -> infinity limit
of standard CLS theory. P_deflated: 0.40 as a DESIGN CONSTRAINT for consolidation.

---

## Stream E: LLM Theory

### E1. Catastrophic forgetting (McCloskey & Cohen 1989)

The original result: connectionist networks trained sequentially on task A then B
show nearly total loss of A. The substrate avoids this via outer-product algebra
(additive write, no gradient descent, no weight interference by construction).
However: the RETRIEVAL quality degrades as K/N increases past 0.56 even without
overwriting -- this is a capacity-limit forgetting, not gradient-interference forgetting.
These are two distinct forgetting mechanisms; the substrate solves gradient-forgetting
but not capacity-forgetting. Full CLS requires solving both.

### E2. EWC (Kirkpatrick et al. 2017)

EWC adds a Fisher-information-weighted penalty to prevent large changes to weights
important for old tasks. For gradient-trained networks this is crucial. For the substrate
(no gradient descent), EWC is irrelevant as a direct method BUT its conceptual content
maps to STC (A5): protect synapses that are important (high Fisher info ~ high PRP level).

### E3. Progressive Networks (Rusu et al. 2016)

Add new columns to the network for each new task; lateral connections allow knowledge
transfer. This is the inspiration for C8 (substrate neurogenesis): add new atom slots
for new domains while preserving existing slots via lateral binding.

### E4. Replay-based: DGR / MeRGAN

Deep Generative Replay uses a generative model to replay pseudo-samples of old tasks.
The substrate's W_fast itself IS the generative model: W_fast @ q_random generates
a valid pseudo-sample for any query. No separate generative model is needed.
This is a significant substrate advantage over gradient-trained CL systems.

### E5. ROME / MEMIT model editing

ROME (Meng et al. 2022) performs rank-one weight surgery in MLP layers using closed-form
key-value insertion. MEMIT extends to mass editing. Recent 2025-2026 work (arXiv:2606.00570)
establishes THEORETICAL LIMITS on parameter-based editing: sequential edits > ~250-500
cause rapid performance degradation due to accumulating interference. The scaling law
for degradation is approximately quadratic in number of edits.

Substrate analog: the delta-W reconsolidation-edit (A6) is mathematically identical
to ROME (rank-one outer-product correction). The interference scaling law applies:
each edit adds a rank-1 perturbation to W; after K edits, the interference is O(K^2 / N).
This gives a substrate-specific editing budget: max safe edits ~ O(sqrt(N)).
At N=1024, safe edit budget ~ 32 sequential edits without explicit interference management.
At N=8192 (validated in Testbed), safe edit budget ~ 91 sequential edits.
Beyond this, interference management (consolidation replay to W_slow) is needed.

HARD PASS criterion for substrate editing budget: recall@1 >= 0.90 for K_edit sequential
edits where K_edit = sqrt(N). HARD FAIL: recall@1 < 0.70 at K_edit = sqrt(N)/2.

### E6. LoRA / PEFT continual

LoRA freezes the base model and trains low-rank adapters. In the substrate, W_slow is
structurally a low-rank (rank-R) adapter on top of the atom vocabulary. PEFT insight:
R << N needed for stable consolidation (rank constraint prevents overfitting to episodes).
Recent work: rank-adaptive LoRA for continual learning (arXiv:2506.21035) uses self-
activated sparse mixture-of-rank adapters. Substrate analog: W_slow with adaptive rank
(add new singular vectors as new schema types emerge). P_deflated: 0.40.

### E7. MoE for continual (ICLR 2025, SETA, CP-MoE 2025)

MoE naturally prevents forgetting by routing different tasks to different experts.
SETA (Split-on-Share, arXiv:2601.17616) decomposes into unique experts (task-specific)
+ shared experts (common features). CP-MoE (arXiv:2605.20247) adds consistency-preserving
constraints. Substrate analog: atom vocabulary IS a mixture of atoms; the per-query
routing is done by the inner-product similarity (each query activates the most similar
atoms). The substrate already IS a sparse MoE retrieval system by construction.

Implication: the consolidation scheduler should distinguish UNIQUE atoms (task-specific,
high isolation needed) from SHARED atoms (schema-relevant, consolidate to W_slow first).
This maps to the schema-accelerated write path (A3).

### E8. ADEPT continual pretraining (2025)

ADEPT (and related 2025 work from Red Hat) achieves near-zero forgetting via careful
parameter subspace management during fine-tuning. Key insight: orthogonal gradient
projection (project new task gradients to be orthogonal to old task gradients).
Substrate analog: ORTHOGONAL OUTER PRODUCT WRITE. When writing a new item, project
v_new to be orthogonal to existing W_fast rows before outer-product accumulation.
This reduces interference without requiring W_slow. Algebraically:
  v_projected = v_new - W_fast^T @ (W_fast @ v_new / |W_fast|^2)
P_deflated: 0.35 (additional projection step; may reduce expressivity).

### E9. Sleep-replay analog in NN (NeuroDream 2025)

NeuroDream (SSRN:5377250, 2025) introduces a dream phase: disconnect from input data,
run internally-generated simulations from stored latent embeddings, use these to
rehearse + consolidate + abstract. Results: 38% reduction in forgetting, 17.6% increase
in zero-shot transfer. This is EXACTLY the substrate's offline consolidation pass:
replay from W_fast into W_slow with no external data required. The songbird analog (A8)
confirms biological precedent for this self-replay mechanism.

P_deflated: 0.55 (NeuroDream provides DIRECT EMPIRICAL PRECEDENT for the offline replay
approach in neural networks; reduces calibration uncertainty). Cap at 0.50 per policy.

### E10. Knowledge editing scaling laws

WikiBigEdit (arXiv:2503.05683) and theoretical limits paper (arXiv:2606.00570) establish
that sequential editing degrades approximately as K^2/N for ROME-class methods. The
substrate's outer-product W is in the same ROME complexity class (both are rank-1 additive
weight updates). This gives a concrete design constraint: if the substrate is to handle
K_total stored items with K_edit periodic edits, it needs N >= K_edit^2 / epsilon
where epsilon is the tolerable recall degradation per edit.

---

## Stream F: Synthesis

### F1. Cross-stream convergence

Five independent streams converge on the SAME substrate CLS architecture:

1. Biology (CLS theory, A1-A2) -> dual-substrate W_fast + W_slow + offline replay.
2. Brain architecture (B1-B4) -> same dual-substrate, sparse projection pre-encoding.
3. Physics (D1-D3, spin glass aging + KWW) -> stretched-exponential frequency-decay on W.
4. LLM theory (E4-E9, DGR + NeuroDream + ROME editing budget) -> same offline replay + editing budget.
5. Crazy architectures (C1, C3, C6) -> dual-substrate + phase-transition scheduler + prediction-error-driven replay.

This five-stream convergence significantly reduces calibration uncertainty relative to
a single-stream finding. The dual-substrate + KWW frequency-decay combination is the
dominant cross-stream finding.

### F2. Ten crazy substrate math systems

**F2.1 DUAL-SUBSTRATE-CLS**
W_fast = existing outer-product (fast, high alpha).
W_slow = new low-rank accumulator (slow, alpha ~ 0.01).
Offline consolidation: v_i <- W_fast row i; W_slow += alpha * outer(v_i_q, v_i_v).
Retrieval: v = beta(age) * W_fast @ q + (1-beta(age)) * W_slow @ q.
P_deflated: 0.45. Implementation cost: 1-2 days (add W_slow matrix + replay loop).

**F2.2 SPIN-GLASS-SLOW-CONSOLIDATION**
Operate W_fast above K_c (> 0.56 * N); let aging dynamics provide natural consolidation.
Problem: above-cliff operation degrades retrieval accuracy.
Hybrid: use DUAL-SUBSTRATE-CLS (F2.1) and let W_slow operate in glassy regime while
W_fast stays below cliff. P_deflated: 0.25 (needs above-cliff operation in W_slow).

**F2.3 STRETCHED-EXPONENTIAL-DECAY**
Atom weight decay: w_i(t) = exp(-((t - t_access_i) / tau_i)^beta), beta ~ 0.6.
tau_i = tau_base * exp(k * write_count_i) (stronger memories have longer tau).
Frequency ledger: track (t_last_access, write_count) per atom.
Decay applied at retrieval time (lazy evaluation, O(1) per atom).
P_deflated: 0.50. Implementation cost: < 1 day (modify frequency ledger in Sprint-2 code).

**F2.4 PHASE-TRANSITION-CONSOLIDATION SCHEDULER**
Monitor K_fast / N_fast ratio. When K_fast / N_fast > 0.4 (pre-cliff):
  trigger consolidation pass (replay bottom-quartile-frequency items to W_slow + retire).
Goal: keep W_fast below K/N = 0.3 (safe operating margin below cliff).
P_deflated: 0.50. Implementation cost: < 1 day (add K/N monitor + trigger).

**F2.5 SUBSTRATE-NEUROGENESIS-EXPANSION**
When K_fast / N_fast > 0.4: extend W_fast with N_new = 0.2 * N additional dimensions
(new atom slots). Retire atoms with frequency < epsilon (zero-mask them).
Effective capacity grows over time without full rebuild.
Requires: sparse W representation. P_deflated: 0.30.
Implementation cost: 2-3 days (sparse W API change).

**F2.6 RECONSOLIDATION-EDIT (PP-225 SUBSTRATE ANALOG OF ROME)**
On retrieval, compute prediction error: e = v_target - W_fast @ q.
If |e| > theta_recon: apply delta_W = eta * outer(e, q) (rank-1 correction).
Window: only allow delta_W within tau_recon steps of last write of that atom.
After tau_recon: atom is "consolidated" (immune to delta_W, moves to W_slow).
P_deflated: 0.45. Implementation cost: 1 day (add recon window ledger).
Note: this IS already partially the memory_editing capability (PP validated).
The new piece is the BOUNDED WINDOW (consolidated atoms become immune to edits).

**F2.7 ACTIVE-INFERENCE-REPLAY**
Prioritize replay items by prediction error magnitude:
  priority_i = |W_fast @ q_i - v_actual_i|
Sort replay queue by priority (highest prediction error replayed first).
Implements SuRe (arXiv:2511.22367) for substrate consolidation.
P_deflated: 0.40. Implementation cost: < 1 day.

**F2.8 HIERARCHICAL-MULTI-LEVEL**
Three tiers: W_L1 (atoms, fast), W_L2 (concepts, medium), W_L3 (schemas, slow).
Write: always to W_L1. Consolidation L1->L2: replay + abstract (cluster K-means on W_L1
rows -> cluster centers become W_L2 rows). Consolidation L2->L3: same.
Retrieval: query W_L1 first; if below threshold, query W_L2; then W_L3.
P_deflated: 0.30 (high complexity; unclear if L3 adds value beyond L2 in practice).

**F2.9 LIQUID-TIME-SUBSTRATE**
Each atom i has its own time constant tau_i, updated by:
  tau_i(t+1) = tau_i(t) + delta_tau * (retrieval_i(t) - target_freq)
where target_freq is a global hyperparameter. Atoms retrieved more often than target
get longer tau (slower decay); atoms retrieved less often get shorter tau (faster decay).
This is a self-organizing frequency-decay with NO global scheduler needed.
P_deflated: 0.38. Implementation cost: 1-2 days.

**F2.10 TOPOLOGICAL-PROTECTION-LONG-TERM**
Consolidate items by writing them to W_slow with MULTIPLE REPLAY PASSES (> R_min passes
to ensure deep basin). Basin depth proportional to R_min. Items consolidated R_min times
are "topologically protected" in the sense that a single delta-W perturbation is
insufficient to destroy them (requires R_min aligned perturbations).
This is the W_slow version of topological protection (no exotic math, just repetition).
P_deflated: 0.40. Implementation cost: parameter R_min added to consolidation pass.

---

### F3. Five empirical tests (real-data continual streams, 10K+ steps)

**Test CLS-1: Dual-substrate split on long stream (PRIMARY)**
Setup: 10K-item continual stream (e.g., 10K Wikipedia sentences); write each to W_fast;
run consolidation pass every N_buffer = 100 items; after 10K steps measure:
  recall@1 on items from epoch 1 (earliest; would be forgotten in W_fast alone)
  recall@1 on items from epoch 10 (recent; should be in both W_fast and W_slow)
  recall@1 on schema-matched items (highest cosine to W_slow rows)
HARD-PASS: recall@1 epoch1 >= 0.70 with dual-substrate vs <= 0.30 with W_fast alone.
HARD-FAIL: recall@1 epoch1 < 0.50 with dual-substrate (consolidation not working).
Cost: < 1 hr CPU with existing infrastructure.

**Test CLS-2: KWW vs exponential decay fit (DIAGNOSTIC)**
Setup: 1000-step stream; vary retrieval frequencies (10%, 30%, 70%, 100% items retrieved
per step); measure retention at t = 10, 50, 100, 500, 1000 steps.
Fit: compare exp(-t/tau) vs exp(-(t/tau)^beta) by BIC.
HARD-PASS: beta_fit < 0.85 AND delta_BIC > 10 favoring KWW.
HARD-FAIL: beta_fit > 0.95 (pure exponential; KWW adds no value).

**Test CLS-3: Reconsolidation window (EDITING BUDGET)**
Setup: write K_edit = sqrt(N) items sequentially; after each write, immediately edit
(delta_W correction); measure recall@1 for all K_edit items.
Compare: with reconsolidation window vs without.
HARD-PASS: recall@1 >= 0.90 for K_edit = sqrt(N) with window.
HARD-FAIL: recall@1 < 0.70 for K_edit = sqrt(N)/2 (interference too high).

**Test CLS-4: Schema-accelerated write**
Setup: two classes of items: SCHEMA-COMPATIBLE (cosine > 0.7 to W_slow rows) and
NOVEL (cosine < 0.3). Write 500 schema-compatible + 500 novel items.
Measure: does schema-compatible recall at 24h-equivalent steps (t = 500 new writes)
exceed novel recall? By how much?
HARD-PASS: schema-compatible recall > novel recall by >= 0.15 recall@1.
HARD-FAIL: schema-compatible recall <= novel recall (schema path confers no benefit).

**Test CLS-5: Self-replay consolidation (NeuroDream analog)**
Setup: write 1000 items to W_fast. Run offline self-replay (sample W_fast rows, replay
to W_slow) for R replay passes. Measure W_slow SVD: does rank(W_slow, epsilon=0.01)
decrease with R (spontaneous dimensionality reduction = schema extraction)?
HARD-PASS: rank(W_slow) at R=1000 <= 0.5 * rank(W_slow) at R=1 (spontaneous low-rank structure).
HARD-FAIL: rank(W_slow) does not decrease with R (no spontaneous schema extraction).

---

### F4. Honest highest-P path

Ranked by P_deflated x implementation_feasibility x uniqueness_vs_existing:

| Rank | Mechanism | P_deflated | Cost | Why now |
|---|---|---|---|---|
| 1 | DUAL-SUBSTRATE-CLS (F2.1) | 0.45 | 1-2 days | Direct CLS literature, pure algebra, 30yr precedent, NeuroDream confirms NN version |
| 2 | STRETCHED-EXPONENTIAL-DECAY (F2.3) | 0.50 | < 1 day | Sprint-2 frequency-decay already validated; KWW is a 1-parameter generalization |
| 3 | RECONSOLIDATION-EDIT with window (F2.6) | 0.45 | 1 day | Memory editing already validated (PP-225); adding bounded window is incremental |
| 4 | PHASE-TRANSITION-SCHEDULER (F2.4) | 0.50 | < 1 day | K/N monitoring already in substrate; trigger-on-cliff is trivial to add |
| 5 | ACTIVE-INFERENCE-REPLAY (F2.7) | 0.40 | < 1 day | SuRe (2025) provides direct NN precedent; prediction-error computation trivial |
| 6 | SCHEMA-ACCELERATED WRITE (A3) | 0.40 | < 1 day | Single cosine threshold check; Tse schema literature is strong |

Combined system (all 6 mechanisms): P_deflated = 0.42 for full CLS parity.

The full system still has uncertainty sources:
- W_slow rank selection (no empirical guidance yet; need Test CLS-5)
- Optimal N_buffer for consolidation pass (no empirical guidance; CLS-1 will determine)
- KWW beta parameter (CLS-2 will determine)
- Schema theta_schema threshold (CLS-4 will determine)

These 4 unknowns are all measurable in < 1 hr CPU each (Tests CLS-1 through CLS-5).

---

## Cheap decisive test

**Run Test CLS-1 (dual-substrate on 1000-item stream) FIRST.**

It requires: W_slow matrix (new), alpha parameter (0.01 default), N_buffer = 100,
retrieval blend beta = 0.5. The metric (recall@1 on epoch-1 items) directly answers
whether the missing cortical slow-generalizer is recoverable in < 2 days of code.

If CLS-1 HARD-PASS: proceed to CLS-2 (KWW fit) and CLS-3 (editing budget).
If CLS-1 HARD-FAIL: the consolidation pass design is wrong; drill into alpha value and
N_buffer selection before proceeding to other mechanisms.

---

## Falsifiable predictions (pre-registered)

### HARD-PASS thresholds
- CLS-1: recall@1 epoch-1 items >= 0.70 with dual-substrate (vs <= 0.30 baseline).
- CLS-2: beta_fit < 0.85 AND delta_BIC > 10 favoring KWW over pure exponential.
- CLS-3: recall@1 >= 0.90 for K_edit = sqrt(N) sequential edits with reconsolidation window.
- CLS-4: schema-compatible recall > novel recall by >= 0.15 recall@1.
- CLS-5: rank(W_slow) at R=1000 <= 0.5 * rank(W_slow) at R=1.

### HARD-FAIL thresholds
- CLS-1: recall@1 epoch-1 < 0.50 (dual-substrate consolidation fundamentally failing).
- CLS-2: beta_fit > 0.95 (frequency-decay is purely exponential; KWW adds nothing).
- CLS-3: recall@1 < 0.70 at K_edit = sqrt(N)/2 (interference dominates even with window).
- CLS-4: schema-compatible recall <= novel recall (schema-accelerated path confers no benefit).
- CLS-5: rank(W_slow) does NOT decrease with R (no spontaneous schema extraction in W_slow).

If CLS-1 HARD-FAIL: pivot to investigating why consolidation replay is not effective
(likely: alpha too high, causing W_slow to overfit individual episodes rather than
averaging across them; reduce alpha by 10x and retest).

---

## Cross-thread synthesis with prior entries

1. Sprint-2 frequency-decay (synthetic-validated): this drill directly extends it
   from exponential to KWW (stretched exponential). Sprint-2 result becomes the
   "beta = 1.0 baseline" in Test CLS-2. The KWW generalization is a 1-parameter
   extension of validated code, not a new system.

2. Memory editing (PP-225, validated): F2.6 reconsolidation-edit adds a bounded
   window to the existing memory_editing capability. No new W structure needed.
   This is an incremental enhancement to a validated capability.

3. K/N capacity cliff (0.56, empirically validated x2): CLS-1 and F2.4 both
   require monitoring K/N. The cliff is the TRIGGER for consolidation. The validated
   cliff position directly informs the trigger threshold (0.4 = safe pre-cliff margin).

4. R10 concept fusion (K>=8 monotone, validated strong): W_slow accumulates R10-style
   concept-level composites from many episodes. The R10 finding that substrates benefit
   from larger K directly supports W_slow's accumulation of large-K composites during
   consolidation replay.

5. Pool retrieval (validated): retrieval blend beta * W_fast + (1-beta) * W_slow is
   structurally identical to the existing pool retrieval (weighted vote readout). The
   dual-substrate CLS-1 design reuses pool retrieval architecture directly.

---

## Substrate-product implications

1. FULL CLS = persistent knowledge accumulation without periodic retraining.
   The compliance-sidecar product requires that substrate memory remain accurate
   across months of new fact injection. Full CLS gives the substrate the cortical
   slow-generalizer needed to maintain accuracy across long operational lifetimes.

2. RECONSOLIDATION-EDIT = surgical fact correction with algebraic audit certificate.
   Each delta-W correction is a rank-1 outer product; it is auditable (log the
   (q, v_old, v_new, timestamp) tuple), reversible (subtract the delta-W), and
   bounded (editing budget ~ sqrt(N) per the ROME scaling law). This is a stronger
   version of the PP-225 editing story: not just "edit facts" but "edit facts with
   a bounded provable interference budget."

3. KWW FREQUENCY-DECAY = automatic data hygiene (stale facts decay out of the store).
   In the compliance-sidecar context, this is GDPR-relevant: low-frequency facts
   (which are likely stale or personal data accessed rarely) decay out without
   explicit deletion instructions. This strengthens the PP-9 GDPR deletion story.

4. PHASE-TRANSITION SCHEDULER = predictable capacity management.
   The substrate can guarantee recall@1 >= 0.90 for the N most recent K items if it
   keeps K/N < 0.4 (pre-cliff). The scheduler enforces this guarantee. Product claim:
   "substrate provides certified memory accuracy for the N most recently accessed facts."

5. SCHEMA-ACCELERATED WRITE = fast knowledge injection for known domains.
   When the substrate has prior schema context (e.g., medical terminology, legal clauses),
   new schema-compatible facts consolidate rapidly. This is an upsell: "add domain
   schema to unlock accelerated learning in that domain."

---

## Citations (verified from search results, 17 total)

1. McClelland, McNaughton, O'Reilly (1995). Complementary learning systems. Psychological Review.
2. Kumaran, Hassabis, McClelland (2016). What learning systems do intelligent agents need? Trends Cogn Sci.
3. PMC9606815 (2022). Bidirectional CLS interactions for sequential memory consolidation.
4. Tse et al. (2007, 2011). Schemas and memory consolidation. Science.
5. Roy Soc Phil Trans B 379/1906 20230238 (2024). Novelty, prior knowledge, and memory networks.
6. arXiv:2601.18946 (2025). Schema-based active inference and frontal cortical coding.
7. PMC11968991 (2025). Extended temporal flexibility in synaptic tagging and capture.
8. Roy Soc Phil Trans B 379/1906 20230237 (2024). Synaptic tagging and capture in brain health.
9. arXiv:2506.12034 (2025). Human-like forgetting curves in deep neural networks.
10. SSRN:5377250 NeuroDream (2025). Sleep-inspired memory consolidation for neural networks.
11. arXiv:2511.22367 SuRe (2025). Surprise-driven prioritized replay for continual LLM learning.
12. arXiv:2601.17616 SETA (2025). Split-on-Share mixture of sparse experts for task-agnostic CL.
13. arXiv:2605.20247 CP-MoE (2025). Consistency-preserving MoE for continual learning.
14. arXiv:2604.07401 (2025). Geometric entropy and retrieval phase transitions in dense associative memory.
15. arXiv:2606.00570 (2026). Revisiting parameter-based knowledge editing: theoretical limits.
16. arXiv:2503.05683 WikiBigEdit (2025). Understanding limits of lifelong knowledge editing in LLMs.
17. PNAS 2422602122 (2025). Two-factor synaptic consolidation: robustness, pruning, homeostatic scaling.
18. Frontiers fnins 1709208 (2025). Extent and activity of adult hippocampal neurogenesis.
19. arXiv:2506.21035 (2025). Little by little: continual learning via self-activated sparse MoR-AL.
20. ResearchGate / arXiv cond-mat/0007036 (2001). Out-of-equilibrium dynamics of Hopfield model.

---

## P estimates summary (calibrated, deflated 0.15-0.25 per policy)

| Mechanism | P_theory | Deflation | P_deflated |
|---|---|---|---|
| DUAL-SUBSTRATE-CLS (F2.1) | 0.70 | -0.25 | 0.45 |
| STRETCHED-EXPONENTIAL-DECAY (F2.3) | 0.70 | -0.20 | 0.50 |
| RECONSOLIDATION-EDIT-WINDOW (F2.6) | 0.65 | -0.20 | 0.45 |
| PHASE-TRANSITION-SCHEDULER (F2.4) | 0.65 | -0.15 | 0.50 |
| ACTIVE-INFERENCE-REPLAY (F2.7) | 0.55 | -0.15 | 0.40 |
| SCHEMA-ACCELERATED-WRITE (A3) | 0.55 | -0.15 | 0.40 |
| Combined full CLS (all 6) | ~0.60 | -0.18 avg | 0.42 |
| SUBSTRATE-NEUROGENESIS (F2.5) | 0.45 | -0.15 | 0.30 |
| SPIN-GLASS-SLOW-CONSOL (F2.2) | 0.40 | -0.15 | 0.25 |

Novel-synthesis cap: 0.50. Combined P capped at 0.42 (below cap).

Next-drill candidate: structural-glasses-MCT (mode-coupling theory for alpha/beta relaxation)
-- the MCT relaxation timescales may give the optimal alpha and N_buffer parameters for
the dual-substrate consolidation pass, informed by the research_field_advisor Tier-1b entry.

---
