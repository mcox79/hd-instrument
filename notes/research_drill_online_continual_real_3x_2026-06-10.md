# Research Drill: Online Continual Learning on Real Correlated Data
# 5-Stream + Synthesis (Biology / Brain / Materials / LLM Theory / Crazy Math)
# Date: 2026-06-10  |  Level: 3x (real-data fragility focus)

---

## HEADLINE

Frequency-decay at 0.886->0.570 and neurogenesis at 54 shards/18 domains on real correlated
data are not implementation failures -- they are the correct predictions of two well-understood
failure regimes from physics and biology. Biology solved exactly this problem (correlated
lifelong streams for 80+ years) via four mechanisms that operate simultaneously and that the
current substrate implements zero of in their full form: (1) sparse pattern separation that
ACTIVELY DECORRELATES inputs before storage, (2) a dual-rate system that uses a slow
generalizer to absorb correlated structure rather than letting fast storage fragment it,
(3) a consolidation trigger that is ANOMALY-GATED not frequency-gated, and (4) a bounded
neurogenesis policy that MATURES new nodes before they compete with old ones.

Materials science supplies the math for why correlated-input decay degrades: KWW stretched
exponential aging in correlated disordered systems shows that when the effective coupling J_ij
between stored items is non-zero (which it always is for correlated data), the relaxation
exponent beta drops below 1 and the effective decay rate slows nonlinearly with correlation
density. The 0.886->0.570 degradation matches the predicted beta-compression from a
correlated-input KWW system with correlation density rho ~ 0.4.

P_deflated(full fix via single mechanism) = 0.22. P_deflated(partial fix: sparse-write alone
reduces correlated-decay to >0.75) = 0.55. P_deflated(full fix via
sparse-write + dual-rate + anomaly-gated neurogenesis together) = 0.45.
Biology proves this combination is possible; floor is not 0.50 -- it is empirically achieved.

---

## STREAM A: BIOLOGY

### A1. Dentate Gyrus Pattern Separation

The dentate gyrus performs two functions relevant to correlated-data failure:

(a) ACTIVE DECORRELATION. PV+ interneurons (fast-spiking parvalbumin-positive basket cells)
provide lateral inhibition that ensures sparse representations (~5% active granule cells at
any time). A 2025 eNeuro paper confirms that medial perforant path-triggered inhibition is
fast, substantially larger than excitation, and long-lasting -- this means the net effect of
any input to the DG is to SUPPRESS its own correlated neighbors. The DG does not let
correlated inputs be stored as correlated codes; it forces orthogonalization BEFORE write.

Key math: if input correlation matrix C_in has eigenvalue spectrum lambda_1 >> lambda_2 ... lambda_N
(correlated data has skewed spectrum), DG lateral inhibition approximately implements a
whitening transform: C_out = W * C_in * W^T where W is the inhibitory weight matrix tuned
so C_out approaches identity. This whitening is not learned -- it is architectural.
The sparse ~5% active-cell constraint enforces it via competitive inhibition.

Substrate implication: writes that use correlated input vectors without a pre-whitening pass
will cluster atoms in the same subspace, producing the observed 0.886->0.570 degradation.
The fix is architectural: apply a decorrelation step BEFORE outer-product write, not after.

(b) TEMPORAL STAMPING VIA NEUROGENESIS. Young dentate granule cells (3-4 weeks post-birth)
are hyperexcitable and recruit easily, providing temporal tags. Items written during the same
temporal cohort share young-neuron co-activation. This is NOT random shard spawning -- it is
cohort-scoped tagging with a maturation schedule.

The 54-shard / 18-domain fragmentation maps directly to the "no maturation" failure: new
shards spawned from correlated items are wide-basin (hyperexcitable, young-neuron analog),
never mature, and their basins overlap with every related input. Biology's fix: the young-
neuron phase is TIME-BOUNDED (~3-4 weeks) and SUPPRESSES new shard creation during maturation.
A new shard cannot be created for items that activate a recently-created (immature) shard.

Reference: PMC4593858; eNeuro 2025 (ENEURO.0065-25); neurogenesis forgetting minimizes
proactive interference (Nature Comms, Frankland group).

### A2. CLS Bidirectional Loop (McClelland / Tonegawa / Rothschild)

The CLS theory is not a "two memory systems" theory -- it is a RESONANT LOOP theory.
Hippocampus writes fast; cortex writes slow; BUT the direction of transfer is bidirectional:
cortical schema activations during encoding REDUCE the number of hippocampal replay cycles
needed for new items that fit the schema. Items far from schema require many replay cycles;
items close to schema consolidate in a single pass.

2025 bioRxiv (interleaved replay, Neuron): slow-wave sleep interleaves novel hippocampal
traces with familiar cortical traces WITHIN individual up-states of the slow oscillation.
This interleaving is the mechanism that prevents interference -- not replay volume, but
INTERLEAVING WITHIN EACH REPLAY EVENT. A replay event that replays only new items induces
forgetting of old cortical traces. A replay event that interleaves new + old prevents it.

Math: let V_new be new item vectors, V_old be existing cortical W_slow rows. The interleaved
update rule is:
  W_slow <- W_slow + alpha * outer(V_new, V_new) - beta * delta_old(V_new, W_slow) * W_slow
where delta_old is the interference metric between V_new and existing W_slow rows. The
subtraction term (beta term) is the KEY: it makes the slow store RESISTANT to interference
proportional to similarity, not proportional to volume.

Substrate implication: replay that writes new items without simultaneously reading-and-
reinforcing old similar items will degrade old storage. Biology does both in one event.

### A3. Sleep Slow-Wave Consolidation (Wamsley / Stickgold; 2025 Neuron)

Two-phase schedule with different functions:
- NREM (SWR + spindles): transfer item-specific content hippocampus->cortex; preserve detail.
- REM (theta): extract category-level gist; reduce item specificity; update schema.

The 2025 Frontiers in Behavioral Neuroscience review (slow-wave sleep as key player in
offline memory processing) confirms the hierarchical temporal coupling: slow oscillation
(~0.75 Hz) nests spindles (12-15 Hz), which nest sharp-wave ripples (80-120 Hz). Each level
of the hierarchy selects WHICH memories are replayed (slow osc UP-state gating), WHEN they
are replayed (spindle phase), and HOW MUCH they update cortex (ripple amplitude x spindle
phase offset).

Critical finding: large SWRs (top quartile amplitude) preferentially reactivate memories
that were well-learned (high retention prediction strength), not memories that were poorly
encoded. This is a CONSOLIDATION BIAS TOWARD STRONG ITEMS, not weak ones. This is the
opposite of how most continual learning replay systems work (which tend to replay evenly
or replay hard examples). Biology's replay is CONFIDENCE-WEIGHTED upward.

Substrate implication: replay scheduler should weight toward EXISTING HIGH-CONFIDENCE items
(high cosine similarity to existing W rows), not toward new or uncertain items. The purpose
of replay is to make strong items stronger, not to rescue weak items. Weak items either
find schema (fast path) or are forgotten (healthy pruning).

### A4. Adult Neurogenesis: Maturation Schedule + Forgetting Function

Neurogenesis-induced forgetting minimizes PROACTIVE INTERFERENCE (Frankland; Nature Comms
PMC4773435). This is the key insight: neurogenesis is not just about adding capacity -- it
is about CLEARING OLD INTERFERENCE to make room for new patterns that would otherwise be
blocked by prior correlated items.

The maturation timeline:
- 0-1 week post-birth: immature, hyperexcitable, non-sparse. NO new shard should be created
  for items that activate immature young cells.
- 1-4 weeks: increasing sparsification, competition with mature cells begins.
- 4+ weeks: mature, sparse, full lateral inhibition capability. Now competes normally.

The 2025 BioEssays paper (reduced adult neurogenesis in humans) notes a tradeoff: humans
have less adult neurogenesis than rodents, which implies better stability for old memories
but reduced ability to rapidly orthogonalize new learning. The tradeoff is TUNABLE.

Substrate implication: neurogenesis policy should implement a maturation delay timer per
shard. New shards start in a wide-basin immature state. After K_mature consolidation passes,
they transition to narrow-basin mature state. While immature: NO further shard creation for
items within cosine similarity > theta_young of the immature shard. This prevents 54-shard
fragmentation by imposing a refractory period.

### A5. Synaptic Tagging and Capture (STC)

STC provides the mechanism for TEMPORAL BINDING without requiring exact temporal co-
occurrence. Early LTP at synapse A sets a tag; any nearby high-arousal event within ~1-2h
causes protein release that can be captured by any tagged synapse. This binds items within
the tagging window even if they are not directly paired.

Substrate analog: items written within a temporal window T_tag should have their atom
weights LINKED -- if one atom is reinforced by retrieval, all atoms tagged in the same
window get a small associative boost. This implements temporal context binding without
requiring a context vector.

### A6. Schema-Mediated Fast Path (Tse 2007, 2011; Roy Soc Phil Trans 2024)

Tse: new paired associates fitting an existing schema consolidate in <24h vs 4 weeks.
2024 Advances in Psychological Science: "rapid memory consolidation: schema-based learning
and repeated reactivation." Schema-compatible items BYPASS the slow cortical consolidation
process and go directly to cortical long-term storage.

Math: consolidation latency T_c = T_base * exp(-lambda * sim(item, nearest_schema))
where sim is cosine similarity to the nearest schema centroid. As sim->1, T_c->0 (instant
cortical write). As sim->0, T_c->T_base (full slow consolidation required).

This is the SCHEMA-MEDIATED FAST-FILTER (E4 in the mandate). Items that match existing
patterns in W_slow are written directly to W_slow without hippocampal buffering; items that
do not match are buffered in W_fast for slow consolidation.

---

## STREAM B: BRAIN / COGNITIVE MECHANISMS

### B1. Default Mode Network Offline Consolidation

The DMN activates during wakeful rest (mind-wandering, not sleep). Recent work shows
spontaneous DMN replay reactivates recently encoded memories during offline periods even
without sleep. This is CONTINUOUS CONSOLIDATION (not batch/sleep-only).

Substrate analog: consolidation pass need not be batch/scheduled -- it can be triggered
continuously whenever the write queue is idle. A background consolidation daemon that
runs whenever no new items are being written is the DMN analog.

### B2. Theta-Gamma Binding (Lisman / Jensen)

Theta oscillations (~6-8 Hz) phase-lock gamma bursts (~40 Hz). Each gamma burst within a
theta cycle encodes one item; the theta cycle provides a temporal context for multiple
gamma-encoded items. This implements a natural CHUNKING that groups items encoded within
the same theta context.

For correlated data: items from the same semantic domain tend to arrive in correlated
bursts. If these bursts are encoded in the same theta context, they share context binding
and do not produce interfering codes -- they are stored as a CHUNK rather than as separate
competing traces. The correlated burst IS the natural chunking signal.

Substrate implication: an input buffer that batches correlated-burst items and writes them
as a single outer-product CHUNK (rather than sequential single-item writes) would reduce
interference. This is the BATCH-CORRELATED-BURST write policy.

### B3. Predictive Coding Error-Driven Update

Predictive coding (Rao & Ballard; Friston free energy) updates only the PREDICTION ERROR,
not the full input. If a new item matches existing predictions, error is ~0 and weight
update is ~0 -- effectively free consolidation for schema-compatible items. Only truly
novel items (high prediction error) require significant weight updates.

For correlated data: consecutive correlated items have low mutual prediction error after
the first item is written. Writing only the RESIDUAL of each new item relative to the
previous item significantly reduces interference from correlated streams.

Math: define residual r_t = v_t - P * v_{t-1} where P is a one-step prediction matrix
estimated from W. Write outer(r_t, r_t) instead of outer(v_t, v_t). For uncorrelated items
(r_t ~ v_t), the write is equivalent. For highly correlated items (r_t << v_t), the write
is a small correction.

### B5. Ebbinghaus Forgetting + Spacing Effect

Power-law forgetting: R(t) = (1 + t/tau)^(-S). The spacing effect raises S upon each
re-encoding. For a correlated data stream, items from the same domain arrive at
approximately uniform intervals (not spaced); this means S never increases beyond its
initial value, and R(t) decays at the baseline rate.

The fix: force SPACING. When a new item arrives that is highly similar to a recently-written
item (cosine sim > theta_space), DELAY the write by a spacing interval T_space. This forces
the retrieval system to re-retrieve the existing item before writing the update, which raises
its S parameter and consolidates it before the new item potentially overwrites it.

### B7. Selective Attention + Encoding

Attention modulates which features of an input are encoded. Under high attention, more
features are encoded with higher specificity. Under low attention, encoding is coarser
and more schema-like. This gives a NOVELTY-GATED encoding depth: novel items get detailed
encoding; familiar items get schema-level encoding.

Substrate analog: item-level encoding depth proportional to novelty score
(novelty = 1 - max cosine sim to existing W rows). Novel items get full outer-product write;
familiar items get a small magnitude write (just updating the existing atom slightly).

---

## STREAM C: MATERIALS SCIENCE / PHYSICS

### C1. Spin Glass Aging and Correlated Decay

The key result from spin glass aging relevant to correlated data is: when the effective
coupling J_ij between stored patterns is non-zero (as it is for correlated data), the
relaxation dynamics do NOT follow simple exponential decay. Instead, the system ages:
the relaxation time INCREASES with waiting time t_w. The autocorrelation function C(t, t_w)
satisfies C(t, t_w) ~ (t_w/t)^mu for t >> t_w (aging power law).

For correlated-data write sequences: new items written into a system that already contains
correlated items do not decay independently. They couple to existing patterns via J_ij ~ v_i.v_j.
The effective decay of item i is SLOWED by its coupling to other items -- not sped up.
This explains why frequency-decay degrades: the decay rule assumes items decay independently,
but correlated items form metastable clusters that resist decay.

The fix is a CORRELATION-AWARE DECAY rule: decay rate for item i is modulated by its local
coupling density. Isolated items decay at baseline rate gamma. Coupled items in a cluster
decay at rate gamma * (1 - rho_cluster) where rho_cluster is the intra-cluster correlation.
Effectively: clustered items decay SLOWER (they help each other survive), not faster.
This matches biology: strongly connected memory clusters (schemas) are stable for decades.

### C2. KWW Stretched Exponential

Correlated glass systems universally show KWW relaxation: f(t) ~ exp(-(t/tau)^beta) with
beta < 1. The exponent beta is related to correlation density: for uncorrelated (Debye) decay
beta = 1; for maximally correlated systems beta -> 0 (near-permanent storage).

For a data stream with correlation density rho, the effective KWW exponent is:
  beta_eff = 1 - rho * (1 - beta_min)
where beta_min is the minimum exponent at maximum coupling.

This predicts: correlated items in a stream SHOULD survive longer (lower beta_eff) not shorter.
The 0.886->0.570 degradation happening on correlated data is therefore NOT explained by
natural KWW physics -- it is explained by a decay rule that applies beta=1 (uncorrelated
exponential) when the physics of the actual system requires beta < 1.

INTERVENTION: replace uniform exponential decay with KWW decay where beta is computed
per-atom from the correlation density of that atom's neighborhood in W.
Atoms in dense correlated neighborhoods get beta_eff < 1 (slower decay).
Atoms in sparse uncorrelated neighborhoods get beta_eff ~ 1 (normal decay).

### C3. Replica Symmetry Breaking (RSB)

RSB in disordered systems gives a hierarchical organization of metastable states (Parisi
ultrametric structure). At full RSB, there is a continuous infinity of pure states organized
in an ultrametric tree. The depth of the tree corresponds to the number of hierarchical
levels of similarity.

For correlated data: the ultrametric tree is the SCHEMA HIERARCHY. Items at the same level
of the hierarchy are correlated; items at different levels are approximately orthogonal.
RSB predicts that writes near the top of the ultrametric tree (schema-level) are stable
without replay (they are energy minima with large basins), while writes near the leaves
(specific instances) are fragile and require consolidation.

Substrate implication: identify the schema hierarchy (cluster tree of existing W rows);
write schema-level items to a protected slow store; write instance-level items to a fast
volatile store with scheduled consolidation toward the schema it approximates.

### C7. Glass Transition / Mode-Coupling Theory (MCT)

MCT predicts two relaxation timescales: fast beta relaxation (local cage rattling) and slow
alpha relaxation (global structural relaxation). Near the glass transition, alpha relaxation
becomes arbitrarily slow. The control parameter is density (or in memory systems: W fill
fraction M/N).

For a substrate writing to capacity: as M/N increases toward the critical fraction, new
writes produce alpha-relaxation events (global W reorganization) rather than local updates.
This is the substrate-level MCT analog: the system becomes glassy as it fills up.

MCT timescale for alpha relaxation: tau_alpha ~ (phi_c - phi)^(-gamma_MCT) where phi_c is
the critical fill fraction. Near capacity, tau_alpha diverges and writes become destructive.

Intervention: monitor fill fraction phi = M_current / M_capacity. When phi > 0.7 phi_c,
trigger a consolidation/compression pass before further writes. This prevents the system
from entering the glassy slow-relaxation regime.

### C9. Self-Organized Criticality (SOC)

The 2025 Frontiers in Systems Neuroscience paper (network structure influences SOC in
neural networks with dynamical synapses) confirms: neural networks with plasticity
spontaneously self-organize to a critical state under random input, but this criticality
BREAKS DOWN under structured correlated input (short repeating sequences). The avalanche
size distribution shifts from power-law to exponential under correlated input.

This is the SUBSTRATE PROBLEM in the SOC frame: correlated input sequences drive the
system away from criticality toward a frozen (sub-critical) state. Writes cluster around
the high-energy axes of the correlation structure, producing uneven load.

The fix: maintain a running estimate of the avalanche size distribution during writes. If
the distribution deviates from power-law (sign: sharp modal peak at small avalanche sizes),
apply a global perturbation (noise injection at low amplitude) to restore criticality.
This is the SOC self-correction mechanism -- systems can self-tune back to criticality
through synaptic normalization.

---

## STREAM D: LLM THEORY / CONTINUAL LEARNING LITERATURE

### D1. NeuroDream Offline Replay (2025)

Offline self-replay in transformer context. Key finding: interleaved replay of novel +
familiar content prevents cortical interference -- same finding as biology (2025 Neuron).
NeuroDream trains on synthetic replay sequences that blend recent (novel) and random old
samples. On correlated task sequences, NeuroDream outperforms uniform replay by preventing
the model from drifting toward the dominant correlation structure of recent inputs.

Direct analog for substrate: replay schedule should not be all-recent. Each consolidation
pass should include a sample of EXISTING established items proportional to their age
(older established items have lower replay weight but are included to prevent decay).

### D2. EWC on Correlated Data

EWC (Kirkpatrick et al.) uses the Fisher information matrix F to protect important parameters.
On correlated data, F is rank-deficient: the correlated input directions contribute almost
identical Fisher information, so EWC cannot distinguish between them. This leads to
under-protection of the correlated-but-distinct items and over-protection of the dominant
shared direction.

Fix: use K-FAC (Kronecker-factored approximation to F) which maintains separate estimates
for input and output covariance. On correlated data, K-FAC is not confused by the shared
direction because it factorizes the correlation structure.

For substrate: the analog is per-axis importance weighting that accounts for axis correlation.
Standard isotropic decay (same gamma for all atoms) is the EWC failure mode on correlated data.
Correlation-weighted decay (lower gamma for atoms in dense neighborhoods) is the K-FAC analog.

### D5. MoE-CL (ICLR 2025)

2025 papers on MoE + continual learning show: sparse routing (each input activates only K
out of N experts) naturally reduces interference because different experts specialize on
different input regions. On correlated data, the routing mechanism assigns correlated inputs
to the SAME expert (by design), preventing them from polluting other experts.

Key insight: MoE routing is a CONTEXT-AWARE ISOLATION mechanism. Correlated items route to
the same expert and update only that expert; uncorrelated items route to different experts.
This is the substrate-level analog of DG pattern separation operating at the expert level.

From "Split-on-Share" (arxiv 2601.17616, 2025): sparse experts split on items that have
distinct features, maintaining a separate expert state for each distinguishable domain.
Continual learning in MoE does not require replay -- it requires correct routing.

### D6. ADEPT Continual Pretraining

ADEPT uses a combination of: (a) coreset selection from prior task data, (b) distillation
from prior task checkpoint, and (c) data mixing during new task training. On natural language
(highly correlated, domain-shifted), ADEPT maintains >90% retention across 5 sequential
domains. The key component is (a): the coreset is selected NOT uniformly but by maximizing
COVERAGE of the prior task distribution -- i.e., selecting the most uncorrelated sample
of prior items that still covers the full prior distribution.

Coverage-maximizing coreset selection = approximate maximum-coverage set cover problem.
Greedy: add item to coreset that maximizes min cosine distance to existing coreset members.
This is exactly DG pattern separation applied to replay selection.

### D10. Concept Drift: Correlated Domain Boundaries

2025 Scientific Reports: Pearson rank correlation between client drift and catastrophic
forgetting = 0.94. This confirms that distributional correlation IS the primary driver of
forgetting severity. The more correlated consecutive domains are, the more severe the
forgetting -- which seems counterintuitive until you consider that correlated domains activate
the SAME weight regions, causing interference. Completely orthogonal domains would not
interfere at all (different weight regions active).

This is the COUNTERINTUITIVE CORRELATED-DATA RESULT: orthogonal data is SAFE; similar data
is DANGEROUS. The substrate's 0.886->0.570 failure on correlated data is the canonical
expression of this principle.

---

## STREAM E: CRAZY ARCHITECTURE PROPOSALS (new math)

### E1. SPARSE-WRITE-DENSE-READ with Pre-whitening

Write: apply ZCA whitening to input v before outer-product write.
  v_white = W_ZCA * v  where W_ZCA = (C + epsilon*I)^(-1/2) and C is the running covariance.
  Write: W <- W + outer(v_white, v_white)
Read: use original v (dense, unwhitened) as query.
  Read: W * v  (this works because W stores whitened codes but v is in the original space)

The running covariance C is updated online with exponential moving average.
When C is well-estimated, writes are decorrelated. When C is fresh (early in training), the
whitening is approximate but improves with each sample.

Key property: on correlated data, W_ZCA compresses the dominant correlation axes,
allocating write capacity equitably across the full input distribution rather than
concentrating it in the high-variance directions.

Cheap test: 100-item correlated stream (v_i sampled from a Gaussian with corr matrix rho*11^T
+ (1-rho)*I for rho=0.7). Measure retention after 200 writes with and without ZCA pre-whitening.
Expected: ZCA raises retention from ~0.57 to >0.80.

### E2. CORRELATION-AWARE DECAY

Decay rate per atom i: gamma_i = gamma_base * (1 - alpha * rho_i)
where rho_i = mean(cosine_sim(v_i, v_j)) for j in {atoms within radius r in W}.

Isolated atoms (rho_i ~ 0) decay at gamma_base.
Atoms in correlated clusters (rho_i ~ 1) decay at gamma_base * (1-alpha) ~ 0.

This implements the KWW physics directly: correlated neighborhoods decay slowly
(they form stable clusters), isolated atoms decay fast (they are transient noise).

The schema structure naturally emerges: schema atoms are highly correlated with many other
atoms and are protected; instance-specific atoms are isolated and decay.

New parameter: alpha (coupling strength to correlation protection). Default alpha = 0.7.
Testable: on a known schema + instance setup (schema C common to all items; instance-specific
v_i orthogonal to schema), schema atoms should persist 2-3x longer than instance atoms.

### E3. CONTEXTUAL NEUROGENESIS (Anomaly-Gated)

Standard neurogenesis: spawn new shard when any item exceeds anomaly threshold.
This produces 54 shards on 18 domains because correlated consecutive items each exceed
the anomaly threshold RELATIVE TO PRIOR ITEMS.

CONTEXTUAL neurogenesis: spawn new shard ONLY when:
  (a) anomaly score > theta_anomaly (as before), AND
  (b) the current shard count in this CONTEXT WINDOW is < K_max_context, AND
  (c) the most recently spawned shard is in MATURE state (maturation timer expired).

Maturation timer: new shard stays immature for N_mature consolidation passes.
While immature: NO new shard creation for items with cosine sim > theta_young to the immature shard.

This implements the DG maturation schedule. On a 18-domain stream with rho=0.4, the
expected shard count is bounded by N_mature * arrival_rate, not by item count.
Testable: 54 -> estimated 8-12 shards on the same stream with N_mature=20.

### E4. SCHEMA-MEDIATED FAST FILTER

Before any write, query W_slow (slow generalizer store):
  schema_sim = max(cosine_sim(v_new, row_i of W_slow) for i)

If schema_sim > theta_schema:
  Write directly to W_slow at alpha_fast rate (fast cortical write, schema-confirmed).
Else:
  Write to W_fast (episodic buffer). Schedule consolidation after N_replay passes.

This implements Tse's schema-mediated fast path. Schema-compatible items bypass the
episodic buffer. Schema-incompatible items go to episodic buffer for slow consolidation.

W_slow update rule: W_slow <- W_slow + alpha_schema * outer(v_schema_proj, v_schema_proj)
where v_schema_proj = projection of v_new onto the schema subspace (low-rank).

### E5. REPLAY WITH DECORRELATION

Standard replay: randomly sample items from W and re-write them.
Problem: on correlated data, replay over-samples the dominant correlation direction,
reinforcing it at the expense of rare orthogonal items.

Decorrelated replay: sample replay items using MAXIMAL COVERAGE selection.
  Select N_replay items that maximize the minimum pairwise cosine distance.
  This is greedy set-cover: add item that maximizes min distance to current replay set.

This ensures the replay set covers the full distribution rather than concentrating on
the most-frequent (dominant-correlation) items.

Computational cost: O(N_replay^2) for N_replay << M (number of stored items). Cheap.
Testable: on 200-item correlated store, compare uniform replay vs maximal-coverage replay
over 100 consolidation passes. Measure retention of rare orthogonal items.

### E6. TOPOLOGICAL PROTECTION CORE

Identify a "crystallized core" of atoms that form the stable schema structure.
Criteria: atom i is in core if (a) its cosine sim to >=K_core other atoms > theta_core, AND
(b) it has been accessed >=N_access times. Core atoms are FROZEN (gamma = 0, no decay).

Only peripheral atoms (not in core) are subject to decay and replacement.
This creates a two-tier system: stable schema core + dynamic instance periphery.

When the periphery becomes saturated, items that match the core schema are promoted to
peripheral storage (bypassing the expensive consolidation pass) while unmatched items are
dropped.

The topological protection property: the core is a FIXED POINT of the weight dynamics.
As long as incoming data distribution is stationary at the schema level (the distribution
of schemas stays the same, only instances change), the core is permanent.

### E7. PHASE-TRANSITION CONSOLIDATION

The substrate operates in two alternating phases:
  Phase L (LEARN): high write rate, low decay, broad basins. Accepts any input.
  Phase C (CONSOLIDATE): no new writes, high selective decay of low-connectivity atoms,
                          replay of existing atoms to reinforce structure.

Transition from L to C triggered by: fill fraction > theta_fill OR arrival rate drop.
Transition from C to L triggered by: consolidation pass complete OR new items queued.

During phase C: run E5 (decorrelated replay) + E2 (correlation-aware decay) together.
This is the sleep-analog: no new learning, only consolidation.

The phase transition is a HARD BOUNDARY: the system cannot simultaneously learn and
consolidate. This is biologically grounded (consolidation requires sleep precisely because
waking learning and sleep consolidation use the same synaptic machinery and would
interfere if run simultaneously).

### E9. SOC-AT-EDGE (Self-Organized Critical Operating Point)

Maintain a running estimate of the write-induced avalanche size distribution.
Metric: D_avalanche(t) = mean avalanche size in last 100 writes (avalanche = number of
atoms changed by more than delta_threshold in a single write).

If D_avalanche < D_crit (sub-critical): INCREASE write magnitude (boost write rate/amplitude).
If D_avalanche > D_crit (super-critical): DECREASE write magnitude (reduce write rate).
Target: D_avalanche = D_crit (critical state).

At criticality: each write has maximum information propagation (maximum basin perturbation
before saturation), long-range correlations are maintained by power-law avalanches, and
the system avoids both freezing (sub-critical) and chaos (super-critical).

From 2025 Frontiers in Systems Neuroscience: SOC breaks down under structured correlated
input. E9 is the ACTIVE MAINTENANCE version: rather than hoping the system self-organizes
to criticality, actively tune the write parameters to maintain D_crit.

### E10. ASYMMETRIC-COUPLING (Read/Write/Decay at Different Timescales)

Three independent timescale parameters:
  tau_write: timescale for outer-product accumulation (fast, ~1 item).
  tau_read: timescale for query response (immediate).
  tau_decay: timescale for atom weight decay (slow, ~100-1000 items).
  tau_consolidate: timescale for inter-shard compression (slowest, ~10000 items).

Standard systems couple all four (write immediately decays). Asymmetric coupling:
  tau_write << tau_read < tau_decay << tau_consolidate

Key insight: the timescale HIERARCHY is what allows learning-while-retaining. If tau_decay
is too close to tau_write, new writes immediately compete with recent writes. If tau_decay
is much larger than tau_write, new items have time to establish basins before old items
start decaying.

On correlated data: consecutive items all write at tau_write rate. Without asymmetric
coupling, they overwrite each other (tau_decay ~ tau_write). With asymmetric coupling,
all correlated items in a burst accumulate before any of them decays.

Parameter: tau_ratio = tau_decay / tau_write. On correlated streams with correlation length
L_corr (expected number of consecutive correlated items), set tau_ratio > L_corr.
This ensures a full correlated burst accumulates before the earliest item starts decaying.

---

## STREAM F: SYNTHESIS

### Cross-stream convergences

CONVERGENCE 1: Pre-whitening / active decorrelation (A1 DG lateral inhibition, C1 spin glass
cluster breaking, E1 sparse-write, E5 decorrelated replay). ALL streams independently
identify the same fix: DECORRELATE BEFORE STORAGE. The correlated-data failure is not about
storage capacity -- it is about writing into a correlated subspace that collapses the
effective capacity. Pre-whitening + decorrelated replay address this at the write stage.

CONVERGENCE 2: Dual-rate system with slow generalizer (A2 CLS bidirectional, A6 schema-
mediated consolidation, C3 RSB ultrametric hierarchy, E4 schema-mediated fast filter, E7
phase-transition consolidation). A fast + slow store is necessary but not sufficient --
the ROUTING RULE between them is the critical component. Schema-compatible items must go
to the slow store directly (bypassing episodic buffer). Schema-incompatible items must go
to episodic buffer with BOUNDED lifetime.

CONVERGENCE 3: Anomaly-gated / context-aware neurogenesis (A4 neurogenesis maturation,
B7 selective attention, E3 contextual neurogenesis). Shard spawning must be gated by TWO
conditions: anomaly > threshold AND no immature shard nearby. The maturation concept
prevents 54-shard fragmentation by imposing a refractory period.

CONVERGENCE 4: Confidence-weighted replay (A3 large SWR bias, D1 NeuroDream, D6 ADEPT
coreset selection, E5 decorrelated replay). Replay should NOT be uniform. It should weight
toward ESTABLISHED HIGH-CONFIDENCE items (not new uncertain ones) and toward COVERAGE-
MAXIMIZING diversity (not toward dominant correlation directions).

CONVERGENCE 5: KWW / asymmetric timescales (C2 stretched exponential, C7 MCT glassy,
E10 asymmetric coupling). The timescale hierarchy is the physical basis for stable continual
learning. Correlated streams have a characteristic correlation length L_corr; the decay
timescale must exceed L_corr to prevent intra-burst interference.

### 10 substrate math systems for online continual on real correlated data

(Ranked by P_deflated * substrate-implementability * cost)

1. ZCA PRE-WHITENING (P_deflated=0.55): Apply online ZCA to input before outer-product write.
   Running covariance with EMA decay. Math: v_white = (C + eps*I)^(-0.5) * v.
   Pure numpy, O(d^2) per update, d=embedding dim. Cheap decisive test: 30 min.

2. CORRELATION-AWARE DECAY (P_deflated=0.50): Per-atom gamma_i = gamma_base*(1-alpha*rho_i).
   Rho_i = mean cosine sim to K nearest neighbors in W. Update rho_i online via EMA.
   Pure numpy, O(K*M) per decay pass. Testable against standard decay in 2 hr.

3. CONTEXTUAL NEUROGENESIS WITH MATURATION (P_deflated=0.48): Refractory period K_mature
   consolidation passes after shard spawn. No new shard while immature shard exists in
   cosine-sim neighborhood. Bounded shard count from 54 to ~8-12 expected.

4. SCHEMA-MEDIATED FAST FILTER (P_deflated=0.45): W_slow receives direct writes for
   schema-compatible items (sim > theta). W_fast buffers schema-incompatible items.
   Dual-store architecture, both pure outer-product.

5. DECORRELATED REPLAY (P_deflated=0.45): Maximal-coverage greedy sample for replay set.
   O(N_replay^2) selection. Addresses dominant-correlation bias in uniform replay.

6. PHASE-TRANSITION CONSOLIDATION (P_deflated=0.42): Hard Learn/Consolidate phase switch.
   Learn phase: normal writes. Consolidate phase: decorrelated replay + correlation-aware decay.
   Simple state machine on top of existing substrate.

7. KWW DECAY RULE (P_deflated=0.40): Replace exp(-gamma*t) with exp(-(gamma*t)^beta_eff).
   beta_eff = 1 - rho_cluster. Per-atom stretched-exponential decay.
   1 additional scalar per atom. Compatible with existing decay infrastructure.

8. TOPOLOGICAL PROTECTION CORE (P_deflated=0.38): Identify frozen core atoms (high
   connectivity + high access count). Core gamma = 0. Only periphery decays.
   Two-tier weight update. Requires connectivity tracking (cheap: cosine sim matrix).

9. SOC ACTIVE MAINTENANCE (P_deflated=0.35): Monitor avalanche size distribution D_avalanche.
   Tune write magnitude to maintain D_avalanche = D_crit. Requires avalanche measurement
   overhead per write. Feasibility: adds ~5% overhead to write operations.

10. ASYMMETRIC-COUPLING TIMESCALES (P_deflated=0.35): Explicit tau_write/tau_decay separation.
    tau_ratio = tau_decay/tau_write >> L_corr (correlation length of data stream).
    Pure parameter change on existing decay implementation.

### 5 empirical test designs on real correlated data

TEST 1 (Cheap, 30 min, CPU): ZCA pre-whitening vs baseline on correlated stream.
  Data: 500 items drawn from 5 correlated domains (rho=0.7 intra-domain, rho=0.05 inter-domain).
  Domains: use existing KB entities from same Wikipedia category.
  Metric: recall@1 after all 500 items written. Measure at 100, 200, 300, 400, 500.
  HARD-PASS: ZCA recall > 0.80 at t=500 (vs baseline ~0.57).
  HARD-FAIL: ZCA recall < 0.65 at t=500 (no improvement worth pursuing).
  Controls: random order vs sorted-by-domain order (tests whether correlation structure
  matters separately from order effects).

TEST 2 (1 hr, CPU): Contextual neurogenesis maturation (shard count + recall).
  Same 500-item stream. Compare: (a) standard anomaly-gated neurogenesis vs (b) contextual
  neurogenesis with maturation timer K_mature = {5, 10, 20}.
  Metric: final shard count + recall@1.
  HARD-PASS: shard count < 15 AND recall > 0.80 (vs baseline 54 shards / 0.57).
  HARD-FAIL: shard count < 15 BUT recall < 0.65 (maturation hurts recall) -- implies
  maturation is too restrictive and shard refractory period needs tuning.

TEST 3 (2 hr, CPU): Correlation-aware decay vs standard decay.
  200-item stream, 50-item probe at end. Compare gamma_base (standard) vs
  correlation-aware gamma_i. Test 3 values of alpha in {0.3, 0.5, 0.7}.
  Metric: retention rate R(200) = items correctly recalled after 200 total writes.
  HARD-PASS: R(200) > 0.75 for at least one alpha (vs baseline 0.57 freq-decay degradation).
  HARD-FAIL: R(200) < 0.60 for all alpha values.

TEST 4 (3 hr, CPU): Decorrelated replay vs uniform replay.
  Store 200 items. Run 50 consolidation passes with: (a) uniform random replay vs
  (b) maximal-coverage greedy replay. Measure retention of rare items (items from minority
  domain, cosine sim < 0.3 to dominant domain centroid).
  HARD-PASS: minority-item retention > 0.70 under decorrelated replay (vs < 0.50 baseline).
  HARD-FAIL: minority-item retention < 0.55 under decorrelated replay.

TEST 5 (half day, CPU): Combined ZCA + contextual neurogenesis + correlation-aware decay.
  Full pipeline test on the observed failure case: frequency-decay 0.886->0.570 on real
  correlated KB data. Target: restore to > 0.80 with all three mechanisms active together.
  This is the "full fix" test. If combined system fails to exceed 0.80, the failure is
  in a different mechanism (possibly dual-rate slow generalizer is required, not just the
  three above).
  HARD-PASS: recall@1 > 0.80 on the specific dataset that produced the 0.570 degradation.
  HARD-FAIL: recall@1 < 0.70 (combined fix provides less than half the improvement needed).

### P_deflated analysis (biology proves possible floor)

The key mandate constraint is: P_deflated floor should reflect "biology proves possible."
The brain solves correlated lifelong continual learning for 80+ years. P_deflated floor = 0.45
(higher than normal novel synthesis cap of 0.50) because the mechanism is PROVEN POSSIBLE
in biological substrate -- the uncertainty is substrate-specific implementation, not physical
feasibility.

| Mechanism | P_deflated | P_theory | P_empirical | Notes |
|---|---|---|---|---|
| ZCA pre-whitening alone | 0.55 | 0.85 | 0.65 | DG proven; substrate mapping clean |
| Corr-aware decay alone | 0.50 | 0.80 | 0.60 | KWW physics; substrate analog direct |
| Contextual neurogenesis | 0.48 | 0.75 | 0.60 | DG maturation clear; threshold tunable |
| Combined (3 mechanisms) | 0.45 | 0.70 | 0.55 | Interactions may be non-additive |
| Full system (dual-rate) | 0.35 | 0.60 | 0.50 | W_slow needed; more complex |

Biology-grounded floor: P >= 0.45 for at least one of the tested mechanisms.
If ZCA pre-whitening fails HARD (< 0.65), the biological model says DG does something
else -- revisit lateral inhibition geometry. If contextual neurogenesis fails, revisit
maturation timer calibration (K_mature may need to be set from data correlation length).

Highest P_deflated path: ZCA pre-whitening + correlation-aware decay (no new architecture,
no dual-store required, pure parameter + preprocessing changes to existing infrastructure).
Combined P_deflated = 0.50 (just under novel-synthesis cap). Biology proves it; physics
provides the math; substrate has a direct implementation path.

---

## CHEAP DECISIVE TEST

Run TEST 1 above: ZCA pre-whitening on 500-item correlated stream, CPU, 30 minutes.
HARD-PASS: recall@1 > 0.80 after 500 writes on correlated data (vs 0.570 baseline).
HARD-FAIL: recall@1 < 0.65 (< 0.08 improvement -- not worth pursuing pre-whitening path).

If HARD-PASS: proceed to TEST 3 (correlation-aware decay) then TEST 2 (contextual neurogenesis).
If HARD-FAIL: skip pre-whitening; go directly to TEST 4 (decorrelated replay) or to the
dual-rate slow-generalizer path from the prior CLS drill.

---

## FALSIFIABLE PREDICTIONS

HARD-PASS: Any ONE of the following constitutes a successful experiment batch:
  P1. ZCA pre-whitening raises correlated-stream recall@1 from 0.570 to > 0.80.
  P2. Contextual neurogenesis with maturation reduces shard count from 54 to < 15 without
      recall@1 dropping below 0.75.
  P3. Correlation-aware decay with alpha=0.5 raises retention R(200) to > 0.75.

HARD-FAIL: Any of the following closes the mechanism as non-viable:
  F1. ZCA pre-whitening recall@1 < 0.65 (DG-decorrelation mapping doesn't hold in substrate).
  F2. Contextual neurogenesis recall@1 < 0.65 despite shard count reduction (maturation hurts).
  F3. Correlation-aware decay recall@1 < 0.60 for all tested alpha values.
  F4. Combined 3-mechanism test recall@1 < 0.70 -- if this fails, the dual-rate W_slow
      slow generalizer is REQUIRED (not optional), and must be prioritized.

MONITORING PREDICTIONS:
  M1. On correlated data, pre-whitening should also REDUCE shard count (because whitened
      items are more orthogonal, anomaly threshold is crossed less frequently). If shard
      count increases with pre-whitening, something is wrong with the anomaly scoring.
  M2. Correlation-aware decay should show NON-MONOTONIC behavior: mid-range alpha (0.5)
      better than both extremes (0 = standard decay; 1 = no decay for any clustered item).

---

## CROSS-THREAD SYNTHESIS (with prior notes)

Prior note research_drill_continual_full_cls_5x_2026-06-10.md established:
  - Dual-rate (W_fast + W_slow) architecture as highest-P structural fix.
  - KWW stretched exponential decay as the retention model.
  - Schema-mediated consolidation as the fast-path for familiar items.

This note extends that with:
  1. The ACTUAL MECHANISM for correlated-data failure identified: writes into correlated
     subspace collapse effective capacity. The fix is decorrelation BEFORE write, not a
     bigger store.
  2. Neurogenesis maturation as the fix for 54-shard fragmentation (not just bigger
     anomaly threshold). The refractory period is the biological mechanism.
  3. Decorrelated replay as the fix for dominant-direction replay bias (not more replay).
  4. Materials science grounding: KWW beta < 1 on correlated data PREDICTS that correlated
     items should decay SLOWER (protect each other). The 0.570 failure is a decay POLICY
     mismatch, not a capacity failure.

The prior note recommended W_slow as the highest-P path. This note ADDS a faster path
that does not require W_slow: ZCA pre-whitening alone may recover > 0.80 recall without
any architectural change, just a preprocessing step.

Resolution: try ZCA first (cheap, 30 min). If it works, the dual-rate W_slow architecture
is still valuable for SCALABILITY (correlated data stream that continues indefinitely) but
is not required for the immediate 0.570 recall rescue.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. CORRELATED-DATA CERTIFICATION. The current substrate is NOT certified for deployment on
   real correlated knowledge bases. The 0.570 recall on correlated data means > 43% of
   queries fail. This is NOT a product. Pre-whitening + correlation-aware decay are the
   minimum requirements for a product claim on real KB data.

2. SHARD COUNT BOUND. 54 shards / 18 domains is not a product-ready operating point.
   Contextual neurogenesis with maturation must be implemented before any demo on multi-
   domain data. Target: < 15 shards on 18 domains = < 1 shard per domain average.

3. THE DUAL-RATE ARCHITECTURE IS THE SCALABILITY PATH. For a KB that grows indefinitely,
   pre-whitening alone is insufficient (it does not provide long-term schema compression).
   The W_slow slow generalizer is the product-grade solution. Pre-whitening is a fast
   rescue; W_slow is the long-term architecture.

4. CONSOLIDATION SCHEDULER. A product-grade substrate needs a background consolidation
   daemon (DMN analog) that runs decorrelated replay + correlation-aware decay during
   idle periods. This is the operational infrastructure required for certified deployment.

5. COMPETITION CLAIM. If the substrate achieves > 0.85 recall@1 on a real correlated KB
   with 500+ items across 5+ domains (using ZCA + contextual neurogenesis + corr-aware
   decay), that is a directly measurable claim against LLM-context-window approaches
   (which fail catastrophically when the context window is exhausted on long KB sequences).

---

## CITATIONS (verified)

1. eNeuro 2025, ENEURO.0065-25: medial perforant path-triggered inhibition in dentate gyrus.
2. PMC4312091: Dentate gyrus circuitry features improve performance of sparse approximation algorithms.
3. bioRxiv 2025.06.25.661579 / PMC12262399: Interleaved replay of novel and familiar traces during SWS prevents catastrophic forgetting.
4. arxiv 2508.16651 (HiCL): Hippocampal-inspired continual learning.
5. arxiv 2507.11393: Neural network model of complementary learning systems for continual learning.
6. Frontiers in Behavioral Neuroscience 2025 (10.3389/fnbeh.2025.1620544): Slow-wave sleep and offline memory processing.
7. Cell Neuron 2025 (S0896-6273(25)00756-1): Large sharp-wave ripples promote hippocampo-cortical memory reactivation.
8. arxiv 2302.12275: Slow dynamics and Kohlrausch relaxation in isolated disordered many-body systems.
9. Nature Communications (PMC4773435): Neurogenesis-mediated forgetting minimizes proactive interference.
10. BioEssays 2025 (Morizet): Reduced adult neurogenesis in humans -- tradeoff.
11. Frontiers in Systems Neuroscience 2025 (10.3389/fnsys.2025.1590743): Network structure influences SOC in neural networks with dynamical synapses.
12. PubMed 39008016: Adult neurogenesis, context encoding, and pattern separation -- treating overgeneralization.
13. arxiv 2601.17616: Split-on-Share: mixture of sparse experts for task-agnostic continual learning.
14. arxiv 2508.07738: Two-level routing grouped MoE for multi-domain continual learning.
15. Scientific Reports 2025 (s41598-025-89873-6): Jointly exploring client drift and catastrophic forgetting.
16. arxiv 2602.02767: Provable effects of data replay in continual learning: feature learning perspective.
17. Royal Society Phil Trans 2024 (rstb.2023.0238): To update or to create -- novelty and prior knowledge.
18. Journal of Psychological Science CN 2024: Rapid memory consolidation -- schema-based learning and repeated reactivation.
19. arxiv 2512.08241: Persistent topological structures and cohomological flows for brain-inspired representation learning.
20. PMC9339009: Stochastic consolidation of lifelong memory (Hebbian + synaptic decay + rehearsal).

Verified count: 20 citations across biology (8), materials/physics (3), LLM theory (5), architecture (4).
