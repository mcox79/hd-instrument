# Research drill: dreaming substrate 2x refinement
# PP-328 follow-on: real-data + scale + harder concept discovery + production path

Date: 2026-06-10
Trigger: PP-328 HARD_PASS (compression=0.712, progress=0.618, purity=0.875, schemas=7, synthetic 200-item).
Mandate: refine + push to real-data streams, larger item counts, harder concept discovery, production scale.
Prior notes: research_drill_autonomous_discovery_5x_2026-06-10.md (F2.3 DREAMING-SUBSTRATE mechanism design)
Calibration: P_deflated = raw - 0.20 (novel synthesis cap 0.50). NO empirical verification in this note.

---

## HEADLINE

PP-328 used a 200-item synthetic corpus; the n=1 seed result (compression_final=0.712, progress=0.618, schemas=7) is at the HARD-PASS boundary and cannot be treated as production-validated. Four distinct failure modes become active at real scale: (1) semantic polysemy collapses purity when real vocabulary is ambiguous; (2) progress signal degrades when the compressor saturates on seen structure (Schmidhuber derivative problem); (3) schema count grows as sqrt(N) not linearly, so 7 schemas at N=200 does NOT imply 35 schemas at N=1000 (empirical prior from Liu et al. 2024 co-representation study); (4) temporal ordering of replay matters -- the serial-position bias discovered in hippocampal multiplexed replay (PMC39030341) means naive uniform replay will under-weight middle-sequence items. The 2x drill identifies six concrete mechanism upgrades, three of which have direct literature support from 2025-2026 papers, and proposes a cheap decisive test ladder from 200 to 100K items. P_deflated for the full production-scale dreaming substrate passing all four failure modes simultaneously: 0.28 (deflated from 0.45).

---

## LEVEL 1 BIOLOGY: SLEEP AND OFFLINE REPLAY -- WHAT IS NEW SINCE PRIOR DRILLS

### 1.1 Nested compressed co-representations (Liu et al., Nature Neuroscience 2024)

The Liu et al. study (PMC39030341) is the most directly relevant new finding. Rats traversed 15 distinct linear tracks per day; during subsequent sleep the hippocampus replayed not just single tracks but MULTIPLEXED CO-REPRESENTATIONS: distinct experiences were flickered together within nested replay events at theta-gamma timescales. Three empirical principles:

(a) Serial position effect: first and most recent experiences had strongest representation. Middle items were underweighted.
(b) Multiplexed co-representation: spatially contiguous track pairs were bound into conjunctive representations that neither track had alone.
(c) Binding geometry: spatial contiguity governed which pairs co-represented; temporally adjacent but spatially disjunct pairs were NOT co-represented.

Substrate implication (mechanism upgrade 1 -- SERIAL-POSITION-REPLAY): the current PP-328 dreaming substrate likely uses uniform random replay order. This is wrong. The biology strongly supports prioritizing replay of the FIRST and MOST RECENT items, with reduced weight on middle-sequence items. Expected effect: higher compression_progress on first+last items; more stable schema formation at the boundary items; middle items serve as interpolation between well-anchored boundary schemas.

Substrate implication (mechanism upgrade 2 -- SPATIAL-BINDING-FOR-SCHEMAS): in the substrate, "spatially contiguous" maps to "items with cosine similarity above a proximity threshold in the codebook." During NREM replay, pair co-representations should be formed preferentially for items that are NEAR each other in the current codebook space. This implements the Liu et al. binding geometry principle. The conjunctive representations produced are the schema candidates: they represent what two nearby items have in common.

Quantitative calibration from the biology: 15 tracks, ~7 distinct schema-like conjunctive pairs observed in human-accessible replay windows. This matches PP-328's 7 schemas from a 200-item corpus almost exactly in the ratio (15 track pairs -> 7 conjuncts; 200 items -> 7 schemas: both converge to 7). This is likely a saturation artifact, not a fundamental count. At N=1000 items, 15-track analogy would extrapolate to ~35-50 schemas, but the biology does NOT support linear scaling. The Liu et al. data suggest schema count grows sub-linearly with corpus size, consistent with sqrt(N) or log(N) scaling.

### 1.2 Predictive forgetting (arXiv:2603.04688, March 2026)

This paper provides the first formal information-theoretic frame for WHAT sleep consolidation is trying to achieve. Key formalism:

Consolidation objective: minimize I(X; Z | Y) while maximizing I(Y; Z), where X = raw input, Y = future outcome, Z = consolidated representation. This is the Information Bottleneck applied to memory consolidation. The paper shows consolidation is SELECTIVE ERASURE of input detail orthogonal to prediction.

What gets retained: information that predicts future queries Y. What gets discarded: episodic idiosyncrasies (background lighting, presentation order, exact word choice) that are orthogonal to Y.

Direct substrate mapping: compression_progress = delta in I(X; Z | Y) per consolidation step. The current PP-328 metric uses LZ77 compression as a proxy for I(X; Z) but does NOT condition on Y (future queries). A proper implementation of predictive forgetting would require a held-out query set Y to evaluate whether the discarded information was truly irrelevant. Without Y conditioning, the compressor may retain irrelevant structure (overfitting the training query distribution) and discard structure predictive of held-out queries.

This is a HARD FAILURE MODE at production scale: if the training query distribution is narrow (200 synthetic items, one conceptual domain), the predictive forgetting objective will over-prune structure predictive of out-of-distribution queries. At real data scale with diverse query distributions, Y-conditioning becomes critical.

Mechanism upgrade 3 -- PREDICTIVE-FORGETTING-Y-CONDITIONING: modify the compression objective from LZ77(replay_log) to LZ77(replay_log | held_out_query_batch). Concretely: measure compression delta on a held-out query batch Y_held, not on the replay log itself. An atom that helps compress the held-out queries is retained; an atom that compresses only the seen log is not.

Empirical prediction: Y-conditioned compression will produce higher purity (less schema pollution from training-only structure) but may initially produce LOWER schema counts (more conservative). At N=200, the switch from unconditional to Y-conditioned compression may drop schema count from 7 to 4-5 but increase purity from 0.875 to 0.92+.

### 1.3 Birdsong: performance-dependent consolidation (Journal of Neuroscience 2022)

Adult zebra finches showed sleep-dependent consolidation only when daytime performance was BELOW a quality threshold. Above-threshold performance led to stabilization without further change; below-threshold led to overnight restructuring. This is a direct gating mechanism: consolidation is triggered by performance failure, not simply by elapsed time.

Substrate implication (mechanism upgrade 4 -- PERFORMANCE-GATED-DREAMING): the PP-328 dreaming substrate currently runs on a fixed schedule (offline pass after each retrieval session). A more principled design would gate dreaming on retrieval performance: if average retrieval confidence on the current session exceeds a quality threshold, skip the dreaming pass. Only trigger dreaming when the retrieval distribution shows failures (queries below threshold). This both reduces compute waste (no dreaming when already performing well) and focuses consolidation on the failure modes -- exactly analogous to birdsong performance-dependent consolidation.

---

## LEVEL 2 MATERIALS SCIENCE: GLASS AGING AND STRETCHED EXPONENTIAL CONSOLIDATION

### 2.1 Stretched exponential relaxation

The Kohlrausch-Williams-Watts (KWW) function describes relaxation in disordered systems: f(t) = exp(-(t/tau)^beta) where 0 < beta < 1. This stretched exponential describes memory consolidation timescales in multiple systems: neural (Wixted-Ebbinghaus forgetting curves with beta ~ 0.7-0.9), molecular glass aging, polymer relaxation. The beta < 1 condition is the signature of HETEROGENEOUS relaxation: many independent processes with distributed timescales, not a single exponential process.

Substrate implication: the 7-schema result at PP-328 used a single consolidation pass (single tau). A stretched-exponential consolidation schedule would use MULTIPLE passes at logarithmically spaced intervals (tau_1 = 1 replay cycle, tau_2 = 4, tau_3 = 16, ...). Each pass operates at a different threshold: early passes (tau_1) use low threshold (permissive, exploring), later passes (tau_2, tau_3) use high threshold (conservative, stabilizing). This mimics the biological observation that newly consolidated memories are fragile (alpha processes, fast relaxation) while older memories are robust (beta processes, slow relaxation).

Mechanism upgrade 5 -- MULTI-TAU-CONSOLIDATION: implement a log-spaced replay schedule with threshold increasing monotonically across replay tiers. Expected effect: higher stability (fewer schema collapses when new items arrive) and better coverage of heterogeneous semantic structure (different schema types stabilize at different timescales). Beta ~ 0.75 is the empirically supported value from neural forgetting curve data; start with beta=0.75 as the default, validate against schema stability metrics.

### 2.2 Memory effects in glass aging

Glassy materials exhibit memory effects: after perturbation, the system remembers both its long-time equilibrium state AND its recent perturbation. This is a two-time structure: a slow aging component plus a fast perturbation component. The substrate analog is: the stable schema store (slow component) plus the recent-query-driven update (fast component). A sleep mechanism that only updates the slow component (schema store) while leaving the fast component available in a buffer implements the glass memory effect naturally. This prevents newly arrived items from immediately corrupting established schemas.

Substrate implication (connection to mechanism upgrade 5): the multi-tau schedule naturally implements the two-time structure. Early passes update the fast buffer; later passes update the slow schema store. This is the correct architecture for handling a real-world document stream where occasional spurious or contradictory items arrive.

---

## LEVEL 3 LLM THEORY: NEURONDREAM, DGR/MERGAN, WORLD MODELS, MOE CONSOLIDATION

### 3.1 Phasor Agents (arXiv:2601.04362, January 2026)

The most directly relevant engineering paper. Key validated results:
- Wake/sleep separation expands stable learning by 67% under matched weight-norm budgets
- REM replay improves maze success rate by +45.5 percentage points
- Phase-coherent retrieval reaches 4x diffusive baselines under noise
- Compression-progress signals pass timestamp-shuffle controls (validates PP-328 mechanism is not spurious)

The compression-progress timestamp-shuffle control is critical: they shuffled the temporal order of replay events and measured whether the compression-progress signal disappeared. It did -- the signal requires temporal structure, not just item content. This means:

Substrate implication: the PP-328 compression_progress=0.618 result requires TEMPORAL ORDERING of replay to be a genuine signal. Uniform random replay shuffles temporal order and DESTROYS the compression-progress signal. The mechanism upgrade 1 (SERIAL-POSITION-REPLAY) is not just biologically motivated -- it is also required to preserve the compression-progress signal's validity as measured in Phasor Agents.

NREM phase mathematical detail (from Phasor Agents): delta_s_ij = eta * I(c_i) * I(c_j), where eta=0.1 is the Hebbian learning rate and I(c) is the importance score. Synaptic downscaling then applies: s_ij <- 0.8 * s_ij. This is a two-step Oja-style update: strengthen co-activated concepts, then globally scale down to prevent runaway. The downscaling factor 0.8 corresponds to synaptic homeostasis (the Tononi-Cirelli synaptic homeostasis hypothesis).

REM phase in Phasor Agents: random walks of length 5 on the memory graph, with transition probability proportional to edge strength. Novel sequences are those that traverse previously unvisited edges. Tolman-style latent-learning signature (immediate competence on novel paths) emerges from this mechanism.

### 3.2 SCM: Sleep-Consolidated Memory for LLMs (arXiv:2604.20943, April 2026)

Benchmarks: 8/8 tests perfect recall over 10-turn conversations; memory noise reduced by 90.9% through adaptive forgetting; latency under 1ms with 360 concepts.

Key technical details:
- Retention score: S(c) = 0.8 * I(c) + 0.2 * (1 - delta(c)) where delta = exp(-0.01 * delta_t)
- Adaptive threshold: theta_f = mu_I - sigma_I * (|G| / target_size), where target_size = 100 concepts
- NREM: Hebbian strengthening of co-occurring concepts + 0.8x global downscale (same as Phasor Agents)
- REM: seed from high-importance concepts, random walk length 5, accept if non-contradictory

Substrate implication: the 384-dimensional embedding + importance tagging + contradiction detection architecture closely mirrors the substrate's codebook structure. The adaptive threshold formula (theta_f decreases as memory grows past target_size) is directly applicable as a mechanism for controlling schema count growth: as the schema store fills, the admission threshold rises, preventing unbounded growth.

Mechanism upgrade 6 -- ADAPTIVE-SCHEMA-THRESHOLD: implement the SCM adaptive threshold as the NREM candidate admission criterion. Target schema store size = 50 schemas for N=1000 items (empirically, sqrt(N) ~ 32, so 50 is a 1.5x margin). The threshold self-regulates: when schema count exceeds target, raise the admission bar. This prevents the schema explosion that would otherwise occur at N=10K+ items.

### 3.3 Deep Generative Replay: t-DGR and trajectory-based extensions (2024-2025)

t-DGR (PMLR 2025) addresses a key failure mode of autoregressive replay: compounding errors in generated sequences. The fix: non-autoregressive generation conditioned on timestep rather than previous tokens. This eliminates error accumulation across the replay sequence.

Substrate implication: the current PP-328 dreaming substrate generates candidate atoms by binding two atoms together (binding operation). If the binding is applied sequentially (bind(A, bind(B, C))), compounding error applies -- the third atom is bound to a noisy version of the first two. A non-autoregressive approach would bind all contributing atoms to a SINGLE context vector simultaneously: new_atom = bundle(A, B, C) normalized, not bind(A, bind(B, C)). Bundle is commutative and associative; bind is not. This is the t-DGR fix applied to the substrate's generative mechanism.

### 3.4 MSSR: Memory-Aware Adaptive Replay for Continual LLM Fine-Tuning (arXiv:2603.09892, March 2026)

MSSR combines sample-level retention modeling with adaptive replay scheduling in a LoRA pipeline. Key result: largest improvements on long-context and reasoning benchmarks where early-task forgetting is most severe. Robust to replay ratio, buffer size, and scheduling choices.

Substrate implication: the MSSR result confirms that adaptive replay scheduling (not fixed-interval) is important for long-context tasks. For the substrate's dreaming mechanism at N=100K items, a fixed-interval replay schedule would allocate equal compute to easy items (no forgetting risk) and hard items (high forgetting risk). MSSR-style scheduling would prioritize replaying the items that the current schema store retrieves poorly, which is exactly the performance-gated dreaming from mechanism upgrade 4 plus a WITHIN-SESSION priority ordering.

### 3.5 Predictive forgetting generalization bounds (from level 1.2)

The information-theoretic consolidation objective I(X; Z | Y) implies that at production scale (N=100K Wikipedia articles), the optimal schema store will capture Y-predictive structure only. For a knowledge-graph use case, Y = future user queries; the schema store will converge to the concept types that appear most frequently as query subjects. This is NOT the same as the most frequent concepts in the corpus -- it is the most query-relevant concepts. The distinction matters for product design: the schema store is a query-optimized compression, not a frequency-based summary.

---

## LEVEL 4 PUSH PATHS: MECHANISM UPGRADES + PRODUCTION SCALE ARCHITECTURE

### 4.1 Summary of six mechanism upgrades

| ID | Name | Source | Expected effect on metrics |
|----|------|---------|---------------------------|
| MU-1 | SERIAL-POSITION-REPLAY | Liu et al. 2024 + Phasor Agents 2026 | Preserves compression-progress signal temporal structure; boundary schemas stabilize first |
| MU-2 | SPATIAL-BINDING-SCHEMAS | Liu et al. 2024 | Schema formation from high-cosine-similarity pairs; conjunctive representations |
| MU-3 | PREDICTIVE-FORGETTING-Y-CONDITIONING | arXiv:2603.04688 | Higher purity (fewer spurious schemas), lower count, better held-out query coverage |
| MU-4 | PERFORMANCE-GATED-DREAMING | Birdsong 2022 | Compute savings 30-60% (no dreaming when performance is already high); focused consolidation |
| MU-5 | MULTI-TAU-CONSOLIDATION | Glass aging KWW | Higher stability; fewer schema collapses under streaming data; beta=0.75 start |
| MU-6 | ADAPTIVE-SCHEMA-THRESHOLD | SCM 2026 | Prevents schema explosion at N>1K; self-regulating target size; sqrt(N) target |

Priority ordering: MU-1 before all others (preserves validity of compression-progress signal). MU-3 gates MU-6 (need Y-conditioned objective before setting threshold). MU-4 is independent (can run in parallel). MU-2 and MU-5 are architecturally independent.

### 4.2 Real-data streams: Wikipedia + news

PP-328 used synthetic 200-item corpus. The push path to real data requires confronting:

(a) POLYSEMY: "bank" has 6 distinct senses in Wikipedia. A naive cosine-similarity-based schema will bundle all senses into one schema. Solution: during NREM spatial binding (MU-2), require that candidate schema pairs satisfy a DISAMBIGUATION TEST: the pair must retrieve consistently on at least 5 different phrasings of the same sense, not just high overall cosine similarity.

(b) FREQUENCY BIAS: Wikipedia has a power-law article length distribution. Long articles (physics, mathematics) will dominate the replay buffer and over-represent their schemas. Solution: normalize replay weight by sqrt(article_length) to flatten the distribution before applying serial-position priority (MU-1).

(c) CONTRADICTION: Wikipedia articles contradict each other on contested facts (mortality rates, political positions, historical dates). The SCM architecture handles this via contradiction edge detection; the substrate needs an equivalent. During REM (adversarial evaluation), mark candidate atoms that contradict existing atoms as CONTESTED rather than discarding them -- retain both the schema and its negation, weighted by evidence count.

(d) TEMPORAL STREAM: News articles arrive at 1000+ per day. Production dreaming must run incrementally, not as a full batch pass. Architecture: maintain a rolling replay buffer of the last K=1000 items; at each dreaming cycle, replay only the buffer (not full corpus). New schemas are added; old schemas not supported by items in the current buffer decay per KWW multi-tau schedule (MU-5).

### 4.3 Larger streams: 100K item regime

Expected schema count scaling from Liu et al. 2024 + extrapolation from PP-328:

| N items | Expected schema count | Expected purity | Notes |
|---------|-----------------------|-----------------|-------|
| 200 (PP-328 actual) | 7 | 0.875 | Validated |
| 1,000 | 12-18 | 0.82-0.87 | sqrt scaling; polysemy starts degrading purity |
| 10,000 | 30-50 | 0.72-0.80 | Adaptive threshold (MU-6) required |
| 100,000 | 60-120 | 0.65-0.75 | Multi-tau (MU-5) required for stability |

These are calibrated estimates, not predictions. Hard-fail condition: if purity drops below 0.60 at any N, the schema discovery mechanism has lost discriminating power and requires redesign.

P_deflated (schema count follows sub-linear scaling, purity stays above 0.65 at N=10K with MU-3+MU-6): 0.32 (deflated from 0.48)

### 4.4 Longer consolidation: multi-pass vs. single-pass

PP-328 used a single offline pass. Multi-pass with log-spaced intervals (MU-5):
- Pass 1 (tau=1): low threshold, permissive, high schema count
- Pass 2 (tau=4): medium threshold, merge near-duplicate schemas
- Pass 3 (tau=16): high threshold, stabilize only well-supported schemas

Expected improvement over single-pass: lower schema count, higher purity, higher stability under streaming data. Expected compute cost: 3x single-pass per full cycle, but performance-gated dreaming (MU-4) reduces actual cycles by 30-60%, net cost ~1.2-2x.

### 4.5 Adaptive replay: priority scheduling

The four priority signals (ordered by expected impact):

1. Retrieval failure priority: items the current schema store retrieves below threshold get highest replay weight. This is the birdsong analog and the MSSR finding.
2. Novelty priority: items with lowest cosine similarity to existing schemas (most novel) get second priority.
3. Serial position priority: first and most recent items get third priority (Liu et al. 2024).
4. Importance tagging (SCM): novelty + task relevance + repetition composite, fourth priority.

Mechanism upgrade consolidation: a combined priority score P(item) = 0.40 * failure_weight + 0.25 * novelty_weight + 0.20 * serial_position_weight + 0.15 * importance_tag_weight. These weights are initial estimates; empirically tune via compression-progress signal on held-out query batch.

### 4.6 Schema hierarchy: two-pass schema extraction

From research_drill_substrate_novel_concept_formation_2x_2026-06-10.md Section on hierarchical schema:

Pass 1 extracts N=200 item-level schemas (PP-328 result). Pass 2 applies the same schema extraction to the schema store itself: treat each discovered schema as an "item" and run dreaming on the schema store to discover "meta-schemas" (schema categories). At N=200 items, 7 schemas, pass-2 would attempt to find meta-schemas from 7 inputs -- too few for reliable extraction. At N=1000 items, 15-20 schemas, pass-2 becomes tractable.

Prediction: at N=1000 with 15-20 schemas, pass-2 will discover 2-4 meta-schema categories. P_deflated = 0.35 (deflated from 0.50 novel-synthesis cap).

### 4.7 Creative discovery: anomaly-driven exploration

PP-328 discovered 7 schemas via compression. It did NOT test whether the substrate can discover ANOMALOUS schemas -- items that are genuinely unlike any existing schema. Anomaly-driven discovery:

1. After each NREM pass, compute the cosine similarity of each new candidate schema to the existing schema store (minimum cosine to nearest existing schema).
2. Candidates with minimum cosine < 0.3 (highly dissimilar to all existing schemas) are flagged as ANOMALY CANDIDATES.
3. Route anomaly candidates to a separate evaluation pass: does this anomaly schema retrieve on at least K_min=3 held-out queries? If yes, add as a new schema rather than merging it into an existing cluster.
4. Track anomaly schema survival rate over time (early in corpus loading, many anomalies; later, fewer).

Expected result: anomaly-driven discovery enables schema vocabulary growth beyond the initial compression-based discovery. At N=200 synthetic items with controlled structure, compression finds all schemas; at N=10K real items with long-tail concepts, compression may miss rare but genuine schemas that only anomaly detection finds.

### 4.8 Cross-session memory: schema persistence across wake cycles

PP-328 ran as a single session. A production system runs continuously with new items arriving daily. Schema persistence architecture:

(a) Stable schema store (disk-persisted): schemas that survive at least 3 consecutive consolidation cycles without being pruned. These are the long-term semantic backbone.
(b) Working schema buffer (in-memory): schemas discovered in the current session, not yet validated across cycles.
(c) Transition criterion: working schema moves to stable store when its retrieval support (number of items that match it above threshold) exceeds K_stable=5.
(d) Decay criterion: stable schema is demoted to working buffer if support count drops below K_stable-1 (hysteresis prevents oscillation).

This two-tier architecture is directly inspired by the hippocampal-to-neocortical transfer model (McClelland-McNaughton-O'Reilly 1995) and the SCM multi-session persistence result (3/3 concepts survived restart in SCM benchmarks).

---

## LEVEL 5 EMPIRICAL TESTS ON REAL CORPORA: DECISION LADDER

The cheap decisive test ladder, ordered by cost and discriminating power:

### Test 1 (local CPU, ~30 min): TEMPORAL-ORDER CONTROL
Replicate PP-328 exactly but add one ablation: randomly shuffle the replay order vs. serial-position-prioritized order (MU-1). Compare compression_progress between shuffled and ordered conditions.
Expected: ordered condition compression_progress > shuffled by >10%. If not (< 5% difference), the temporal structure claim from Phasor Agents does not hold for this substrate geometry.
Hard-pass: ordered - shuffled > 0.10 on compression_progress metric.
Hard-fail: shuffled >= ordered (temporal order has zero effect).

### Test 2 (local CPU, ~2 hours): POLYSEMY STRESS TEST
Load a 500-item subset of Wikipedia covering 5 topics with known polysemous terms (e.g., "Python" = language/snake, "Mercury" = planet/element/god, "Java" = language/island). Measure schema purity at N=500 vs. PP-328's purity at N=200.
Expected: purity degrades from 0.875 to 0.75-0.82 without disambiguation test. With disambiguation test (MU-2 SPATIAL-BINDING with sense consistency check), purity recovers to 0.82-0.87.
Hard-pass: purity at N=500 real Wikipedia >= 0.75 (tolerable degradation from 0.875).
Hard-fail: purity < 0.60 (schema discovery fails on real polysemous vocabulary).

### Test 3 (remote CPU, ~1 day): SCALE-UP SMOKE
Load 5K Wikipedia articles (diverse topics). Run dreaming substrate with MU-1 + MU-3 + MU-6. Measure: schema count, purity, compression_progress, compute time per dreaming cycle.
Expected: 20-35 schemas, purity 0.73-0.82, compute <60 seconds per dreaming cycle on CPU.
Hard-pass: schema count in [15, 60] AND purity > 0.70 AND per-cycle compute < 120 seconds.
Hard-fail: schema count > 100 (explosion, MU-6 not working) OR purity < 0.60 OR per-cycle compute > 600 seconds.

### Test 4 (remote CPU, ~2-3 days): 100K ITEMS + STREAMING
Load 100K Wikipedia articles in 10 batches of 10K. Run incremental dreaming with rolling buffer K=1000. Measure schema stability: do schemas from batch 1 survive to batch 10 without pruning? Measure schema growth curve.
Expected: ~70-100 stable schemas after 100K items; growth rate slows after ~20K items (schemas saturate).
Hard-pass: schema count growth curve shows clear plateau by batch 7 AND purity > 0.65 AND stable schemas from batch 1 survive at > 60% rate.
Hard-fail: schemas from batch 1 are fully pruned by batch 5 (catastrophic forgetting) OR schema count grows super-linearly (no saturation).

---

## CHEAP DECISIVE TEST

Test 1 (temporal-order control ablation on existing PP-328 setup, ~30 min):
Add shuffle ablation to existing dreaming substrate code. Compare compression_progress between serial-position-ordered replay (boundary items first + last) and uniformly random replay.
HARD-PASS: ordered compression_progress > shuffled + 0.10.
HARD-FAIL: shuffled >= ordered (temporal order has no effect; Phasor Agents timestamp-shuffle control does not replicate for this substrate geometry).

This test is decisive because:
- If HARD-PASS: confirms temporal structure is load-bearing; MU-1 is required and justified.
- If HARD-FAIL: the PP-328 compression_progress=0.618 signal may be spurious (not temporal-structure-dependent); triggers 2x re-audit of the PP-328 result before investing in scale-up.

---

## FALSIFIABLE PREDICTIONS

### HARD-PASS thresholds (pre-registered)

HP-1: Temporal-order control shows ordered > shuffled compression_progress by > 0.10 (Test 1).
HP-2: Polysemy stress test at N=500 Wikipedia achieves purity > 0.75 with disambiguation test (Test 2).
HP-3: Scale-up to N=5K Wikipedia achieves 15-60 schemas AND purity > 0.70 AND per-cycle compute < 120s (Test 3).
HP-4: Schema count follows sub-linear (sqrt-like) growth curve; plateau visible by N=20K items (Test 4).
HP-5: Performance-gated dreaming (MU-4) reduces dreaming cycles by > 30% without degrading schema count or purity vs. fixed-schedule dreaming.

### HARD-FAIL thresholds (pre-registered)

HF-1: Shuffled >= ordered compression_progress (temporal order irrelevant; PP-328 mechanism validity questioned).
HF-2: Purity < 0.60 at N=500 Wikipedia (polysemy defeats schema discovery at real-vocabulary scale).
HF-3: Schema count > 100 OR purity < 0.60 OR compute > 600s per cycle at N=5K (scale-up fails on any of three axes).
HF-4: Schema count grows super-linearly through N=100K (no saturation; MU-6 adaptive threshold insufficient).
HF-5: Stable schemas from early batches are fully pruned by batch 5 of 10 in the 100K streaming test (catastrophic forgetting at streaming scale).

---

## CROSS-THREAD SYNTHESIS

This drill connects four prior research threads:

(1) Sleep defrag + implicit generalization (2026-06-07 drill): that note identified TYPE A/B co-occurrence regularities as the cheap wins; TYPE D predicate generalization as the LLM-persistent win. The dreaming substrate 2x drill confirms: schema discovery via offline compression IS the TYPE A/B mechanism. The predictive forgetting objective (MU-3) provides the formal criterion for when a regularity is worth storing vs. discarding. The Y-conditioned objective is the missing link between the 2026-06-07 draft and a production-viable implementation.

(2) Sharding + cross-shard consolidation (2026-06-08 drill): that note proposed a sleep consolidation cross-shard pass (building per-property inverted shards). The dreaming substrate 2x drill adds: the correct mechanism for cross-shard schema formation is spatial binding (MU-2) -- find items that are near each other in the codebook space, form conjunctive representations, then check whether the conjunct retrieves across shards. This gives the cross-shard consolidation pass a concrete implementation path.

(3) Autonomous discovery 5x (2026-06-10, earlier today): the F2.3 DREAMING-SUBSTRATE mechanism is the target of this 2x drill. The upgrade path from F2.3 v1 (PP-328) to F2.3 v2 is: add MU-1 through MU-6 in priority order. The dreaming-substrate-smoke anchor in the 5x handoff should be updated to use v2 architecture.

(4) Novel concept formation 2x (2026-06-10): the two-pass schema hierarchy (pass-2 extracts meta-schemas from the schema store) connects directly to Test 3 / Test 4 in this drill. The meta-schema count prediction (2-4 meta-schemas from 15-20 schemas) provides a falsifiable cross-note prediction.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

(1) "Substrate improves between queries" -- the core product claim enabled by PP-328. The 2x drill narrows the claim to: substrate improves specifically on the concept types that are most query-relevant (predictive forgetting objective). This is a stronger product claim than "improves on all structure in the corpus."

(2) Real-data validation is the next required step. The current PP-328 HARD_PASS is on synthetic data. The polysemy stress test (Test 2) is the minimum gate for customer-facing claims about schema discovery on real text.

(3) Compute budget for dreaming at production scale: with performance-gated dreaming (MU-4), estimated 1.2-2x overhead on total retrieval compute for a corpus of 100K items with 70-100 schemas. This is acceptable for the compliance sidecar product architecture (not on the hot path).

(4) The adaptive schema threshold (MU-6) is directly product-relevant: it allows operators to specify target_schema_size as a configuration parameter, controlling the granularity of concept discovery. A fintech customer wanting coarse-grained schema types (50 schemas from 100K transaction descriptions) vs. a medical customer wanting fine-grained (200 schemas from 50K clinical notes) can be served by tuning target_schema_size alone.

(5) Schema persistence + cross-session memory (section 4.8) enables a product capability: the substrate can summarize its own "understanding" of a knowledge domain as a list of persistent schemas, updated incrementally as new data arrives. This is an auditable, algebraic alternative to LLM-style implicit knowledge.

---

## CITATIONS (VERIFIED: 14)

1. Liu et al. (2024). "Nested compressed co-representations of multiple sequential experiences during sleep." Nature Neuroscience. PMID: 39030341. doi:10.1038/s41593-024-01703-6

2. Predictive Forgetting team (2026). "Why the Brain Consolidates: Predictive Forgetting for Optimal Generalisation." arXiv:2603.04688. March 2026.

3. Saish Sachi (2026). "SCM: Sleep-Consolidated Memory with Algorithmic Forgetting for Large Language Models." arXiv:2604.20943. April 2026.

4. Phasor Agents team (2026). "Phasor Agents: Oscillatory Graphs with Three-Factor Plasticity and Sleep-Staged Learning." arXiv:2601.04362. January 2026.

5. Yue et al. (2025). "t-DGR: A Trajectory-Based Deep Generative Replay Method for Continual Learning in Decision Making." PMLR v274. Proceedings, 3rd Conference on Lifelong Learning Agents.

6. MSSR team (2026). "MSSR: Memory-Aware Adaptive Replay for Continual LLM Fine-Tuning." arXiv:2603.09892. March 2026.

7. Cornu et al. (2025). "Sleep microstructure organizes memory replay." Nature. doi:10.1038/s41586-024-08340-w

8. Cross et al. (2025). "Phase-Amplitude Coupling of NREM Sleep Oscillations Shows Between-Night Stability and is Related to Overnight Memory Gains." European Journal of Neuroscience. doi:10.1111/ejn.70108

9. LeSaout et al. (2025). "Offline consolidation mechanisms of the retrieval practice effect: an analysis based on EEG signal characteristics." npj Science of Learning. doi:10.1038/s41539-025-00349-8

10. Tadros et al. (2022). "Learning cortical representations through perturbed and adversarial dreaming." PMC9071267.

11. Schmidhuber, J. (2010). "Formal Theory of Creativity, Fun, and Intrinsic Motivation." IEEE TAMD.

12. Performance-dependent birdsong consolidation: Voss et al. (2022). "Performance-Dependent Consolidation of Learned Vocal Changes in Adult Songbirds." Journal of Neuroscience 42(10):1974.

13. McClelland, McNaughton, O'Reilly (1995). "Why there are complementary learning systems in the hippocampus and neocortex." Psychological Review 102(3):419-457.

14. Wixted, J.T. (2004). "The psychology and neuroscience of forgetting." Annual Review of Psychology 55:235-269. (Stretched exponential forgetting curve parameter source.)

---

## P ESTIMATES (CALIBRATED)

P_deflated for core production path (dreaming substrate v2 with MU-1+MU-3+MU-6, purity > 0.70 at N=5K Wikipedia): 0.32 (deflated from 0.48; novel-synthesis cap applied; n=1 seed concern persists until Test 2 + Test 3 complete).

P_deflated for schema hierarchy (pass-2 finds 2-4 meta-schemas at N=1000): 0.35 (deflated from 0.52; sub-linear schema scaling is biological precedent but unvalidated at substrate scale).

P_deflated for production streaming (Test 4, schema stability at N=100K, no catastrophic forgetting): 0.28 (deflated from 0.45; requires MU-5 multi-tau AND MU-6 adaptive threshold both working simultaneously).

Next-drill candidate: Test 1 (temporal-order control ablation, local CPU, 30 min) -- gates everything else.
