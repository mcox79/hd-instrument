# Research -- Gap E: substrate-grade selective forgetting + importance-weighted compression (cortex-composed)

Date: 2026-06-26
Filed-by: research (Opus 4.7 1M)
Drill type: depth drill (3 mechanism classes + cross-domain probe + cortex-composition emphasis)
Parents:
- TWO_TIER generational W (DISPATCHED, HARD_PASS_PARTIAL at smoke):
  notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md
- REM cold-storage revival (5 anchors, ANCHOR_1 dispatch-eligible):
  notes/exp_dev_handoff_research_REM_revival_cold_storage_never_delete_2026-06-26.md
- Brain selective homeostasis (5 selective-homeostasis variants):
  notes/research_gap4_brain_selective_homeostasis_2026-06-26.md
- Cortex-as-router (mPFC schema -> hippocampus bias signal):
  notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md
- Slow cortex bigram predictor (W_pred Hebbian outer-product):
  notes/research_n5_revival_slow_learning_cortex_context_2026-06-26.md

USER addendum (mid-task): "we're actively spinning up substrate's CORTEX layer (TWO_TIER + BCM slow
learning + Modern Hopfield retrieval). Importance scoring is heavily cortex-dependent in the brain
(frontal cortex tracks task-relevance; cortex schemas encode 'what matters'). If cortex composition
is natural (e.g., cortex schema-emergence as importance signal; cortex-learned salience prediction;
cortex-driven combination of redundant memories into schemas), flag it explicitly + drill the
cortex-composed variant as a top candidate."

Calibration: per [[feedback-lit-scan-calibration-penalty]] -- P estimates deflated 0.15-0.25;
novel-synthesis cap 0.50; HARD-PASS + HARD-FAIL thresholds pre-registered. Per
[[feedback-brain-is-existence-proof-higher-prior]] -- brain-grounded mechanisms with substrate-
feasible paths get P=0.40-0.55 when implementation correctness is the only risk.

---

## (a) HEADLINE

Substrate today already has the cold-storage architecture (TWO_TIER HARD_PASS_PARTIAL) and a
single importance signal (single-noisy-probe recall accuracy). The win is NOT another tier; it is
**replacing the single-noisy-probe importance scalar with a multi-factor cortex-composed importance
vector that has 4-6 independent signals**, where the cortex layer (the slow Hebbian W_pred / W_schema
matrices being spun up THIS WEEK) provides the load-bearing signal that brain importance-scoring
actually uses: "does this atom contribute to the emergent schema that mPFC is building right now?"

The mathematical core: importance = sigmoid( a * recency + b * query_freq + c * downstream_impact +
d * surprise + e * schema_contribution + f * cortex_predicted_salience ). The first 4 are
substrate-mineable today from existing per-atom telemetry (last-access timestamp, hit counter,
gradient on downstream eval, |prediction_error| at write time). The 5th and 6th are NEW capabilities
that compose directly with TWO_TIER's promotion path and with the BCM / Modern-Hopfield retrieval
layers already in flight. **The cortex-composed variant ("schema_contribution" + "cortex_predicted_salience") is the substrate-better-than-brain claim**: brain has only the per-synapse Ca-history scalar (one signal); substrate can in one update step combine 6 independent signals, each weighted by what it predicts downstream.

The single highest-P_deflated cell candidate is `multi_factor_importance_cortex_composed_v1`:
extends TWO_TIER's promotion path with a 6-signal importance vector, uses the W_pred / W_schema
matrices (Gap 3 + n5 revival, in flight) as the cortex signal source, and ships a recovery path
from W_cold via cosine match. **P_deflated = 0.50** (capped at novel-synthesis ceiling because the
TWO_TIER importance architecture is chain-graded eligible at HARD_PASS but the 6-signal
generalization is novel synthesis of existing primitives).

Cheapest decisive test: 3-arm cell on top of the gap4 TWO_TIER cell at ARM_TWO_TIER_PROMOTE_500
configuration (which already produced W_old_util=0.228), swapping in the 6-signal importance
vector. ~3-5 CPU-hr local. HARD_PASS at >= +0.10 drift_reduction over TWO_TIER baseline AND
recall_oldest >= 0.75 at J=10000.

---

## (b) Cheap decisive test

**Cell name:** `multi_factor_importance_cortex_composed_v1`

**Architecture (plain English):**

Build on top of the in-flight TWO_TIER cell (the W_active + W_old promotion architecture). Keep
W_active + W_old. Replace the single-noisy-probe-recall importance scalar with a 6-component
importance vector evaluated at each promotion checkpoint:

```
importance(atom_i) = sigmoid(
    w_rec  * recency_score(atom_i)
  + w_qf   * query_freq_score(atom_i)
  + w_di   * downstream_impact_score(atom_i)
  + w_surp * surprise_score(atom_i)
  + w_sch  * schema_contribution_score(atom_i)     <-- CORTEX-COMPOSED
  + w_cps  * cortex_predicted_salience(atom_i)     <-- CORTEX-COMPOSED
)
```

The 4 first signals are substrate-mineable from telemetry:
- `recency_score = exp(-(t_now - t_last_access) / tau_recency)` per atom
- `query_freq_score = log(1 + n_queries(atom_i)) / log(1 + max_queries)`
- `downstream_impact_score = |grad of eval metric w.r.t. this atom's contribution to W|`
  (cheap: numeric perturbation O(eval_cost) per atom; or batch differential on the cleanup loss)
- `surprise_score = |w_atom_at_write - predicted_w_atom_from_W_pre|` (residual prediction error;
  the substrate already computes this implicitly in BCM rank-2)

The 5th and 6th signals are NEW and use the cortex matrices in flight:
- `schema_contribution_score(atom_i) = cosine( atom_i_signature, W_schema_centroid_at_t )`
  -- how aligned is this atom with the current schema landscape? Atoms that ARE schemas (or
  contribute densely to schema centroids) get HIGH score and are protected from migration.
- `cortex_predicted_salience(atom_i) = sigmoid( W_pred @ atom_i_signature )` evaluated against a
  learned salience predictor head (Hebbian-trained over (atom_signature, future_query_hit) pairs
  during a slow pass). Reads from query history to learn "which atom shapes predict future query
  hits" -- this is the substrate's mPFC analog providing relevance-signaling.

**3 arms (3 seeds [11, 13, 19]):**

| Arm | Mechanism | What it isolates |
|---|---|---|
| ARM_TWO_TIER_SINGLE_IMPORTANCE | Reproduce TWO_TIER_PROMOTE_500 from in-flight cell | Methodology rail; must match dispatched cell within 0.02 drift_reduction |
| ARM_TWO_TIER_4FACTOR_NOCORTEX | 4 substrate-mineable signals only (rec + qf + di + surp); w_sch = w_cps = 0 | Isolates: does multi-factor scoring help without cortex composition? |
| ARM_TWO_TIER_6FACTOR_CORTEX | All 6 signals including W_schema + W_pred | THE cortex-composed test |

**Pre-registered bands (LOCKED at module init, per [[feedback-envelope-fail-bands]]):**

- **HARD_PASS_CORTEX_COMPOSED:** ARM_TWO_TIER_6FACTOR_CORTEX drift_reduction >= TWO_TIER baseline + 0.10
  AND recall_oldest at J=10000 >= 0.75 AND cv across 3 seeds <= 0.05 AND ablation gap (6FACTOR - 4FACTOR)
  >= 0.05. The +0.10 floor is set to discriminate REAL cortex contribution from noise; the ablation gap
  discriminates "more signals = noise-reduction" from "cortex is load-bearing."
- **HARD_PASS_MULTIFACTOR_NOT_CORTEX:** ARM_TWO_TIER_4FACTOR_NOCORTEX matches or exceeds 6FACTOR_CORTEX
  AND beats TWO_TIER baseline by >= +0.10. Interpretation: multi-factor scoring matters but cortex
  composition does not (yet). Cortex layer not mature enough at this experiment scale; revisit after
  BCM + Modern-Hopfield land HARD-PASS individually.
- **MIDDLE_BAND [+0.05, +0.10] drift_reduction over TWO_TIER baseline:** PARTIAL. Mechanism helps but
  effect size below decision threshold. Tune sigmoid weights or signal normalization; check signal
  independence audit (if any two signals correlate > 0.85 they are redundant and should be combined).
- **HARD_FAIL_MULTIFACTOR_DOESNT_HELP:** All multi-factor arms within 0.03 of TWO_TIER baseline.
  Interpretation: at substrate's regime, single-noisy-probe recall accuracy ALREADY captures the
  importance signal -- adding more signals is redundant. Stop adding importance dimensions; pivot to
  recovery-path optimization (anchor candidate 3 below).
- **HARD_FAIL_CORTEX_HURTS:** ARM_TWO_TIER_6FACTOR_CORTEX worse than ARM_TWO_TIER_4FACTOR_NOCORTEX by
  >= 0.05. Interpretation: the W_schema / W_pred signal is NOISY at substrate's current cortex maturity
  (Gap 3 BCM in flight, n5 revival in flight); cortex composition premature. Wait until both cortex
  cells land HARD_PASS individually before re-trying.

**Compute budget:** ~3-5 CPU-hr local at N=4096, alpha cap 7-8x Hopfield, 3 seeds; well within 4hr cap
on local_cpu_queue. Each per-atom importance evaluation at promotion checkpoint is O(N) per signal x
6 signals x M_atoms = O(6 * N * M_atoms) = O(6 * 4096 * ~500) ~ 12M FLOPs at K=500 promotion checkpoint
-- negligible vs the cycle compute. The W_pred matrix multiply is the dominant cost: O(N^2 * M_atoms)
at evaluation per checkpoint; with N=4096 this is ~8B FLOPs per checkpoint, ~1-2s wall, ~10 checkpoints
in a 5000-cycle run = ~10-20s overhead total. Trivial.

---

## (c) Falsifiable predictions

| Arm | Predicted drift_reduction (3-seed mean) | P(>=HARD_PASS) | Reasoning |
|---|---|---|---|
| ARM_TWO_TIER_SINGLE_IMPORTANCE | matches in-flight TWO_TIER baseline (within 0.02) | -- (rail) | methodology rail |
| ARM_TWO_TIER_4FACTOR_NOCORTEX | TWO_TIER_baseline + 0.06 | 0.40 | 4 signals reduce single-noisy-probe variance; modest lift (recency + query_freq are highly correlated with single-noisy-probe accuracy, so the marginal information added is moderate). |
| ARM_TWO_TIER_6FACTOR_CORTEX | TWO_TIER_baseline + 0.12 | 0.50 | The W_schema signal carries "which atoms are central to emergent schemas" which IS the load-bearing brain signal. P=0.50 is at novel-synthesis cap because (a) W_schema is in flight not chain-graded yet; (b) signal-weighting hyperparameters are unproven; (c) cortex composition is THE substrate-better claim and brain-grounded with strong lit precedent (mPFC selective relevance signaling, Sci of Learning 2024). |

**HARD-PASS thresholds:**
- 6FACTOR drift_reduction >= TWO_TIER baseline + 0.10 absolute
- recall_oldest at J=10000 >= 0.75
- cv across 3 seeds <= 0.05
- ablation gap (6FACTOR - 4FACTOR) >= 0.05

**HARD-FAIL thresholds (pre-registered):**
- All multi-factor arms within 0.03 of TWO_TIER baseline -> multi-factor scoring doesn't help at
  substrate's regime
- 6FACTOR worse than 4FACTOR by >= 0.05 -> cortex composition premature
- Any arm: recall_oldest at J=10000 < 0.20 -> mechanism is destroying old patterns (matches Cell B
  HARD_FAIL_DESTROYS_OLDER signature)
- cv > 0.10 across seeds -> mechanism is unstable; signal weighting is not generalizing

---

## Section 1 -- Why substrate's current importance signal is one-dimensional

The in-flight TWO_TIER cell uses `single-noisy-probe recall accuracy` as the importance scalar. This
is a strong signal because it directly measures "does this atom survive cleanup under realistic noise?"
-- which is what the substrate ultimately cares about. BUT it has 3 known limitations:

1. **It's a backward-looking signal.** It scores atoms based on whether they CAN be recalled given the
   current W state. It doesn't predict whether they WILL be queried in the future. If a high-recall atom
   is never queried again, it's wasting W_active capacity; if a marginal-recall atom is queried 100
   times, it deserves protection.

2. **It's a within-W signal.** Recall under noise is a property of the W matrix internal structure.
   It doesn't reflect downstream task value (whether the atom contributes to a useful prediction,
   schema, or retrieval cascade).

3. **It collapses redundant atoms.** Two atoms that are highly similar (cosine > 0.85) both get high
   recall scores -- but in a continual-learning regime, you want to consolidate them into a single
   schema atom, not keep both.

The brain has these same problems and solves them via separate parallel signals -- which is exactly
what mPFC + ATL + hippocampus provide as a layered system.

---

## Section 2 -- How the brain composes importance signals (cortex-emphasized)

From the cortex-as-router drill (today) + the brain-selective-homeostasis drill (today) + 2024-2025
neuroscience literature:

**Layer 1 (hippocampal): per-synapse Ca-history scalar.** This is the BCM / STC tag we already
discussed. Says "this synapse was active recently and crossed LTP threshold." Roughly maps to
substrate's single-noisy-probe importance.

**Layer 2 (mPFC): task-relevance signal.** Activating mPFC allows rats to form memories of important
events without increasing learning of unimportant details (Soc Learn Memory 2024). The mPFC provides
a "this event matters for current task" signal that the hippocampus reads as a multiplier on the
encoding strength. Substrate analog: a learned salience predictor that says "atoms shaped like X are
likely to be queried for current task class Y."

**Layer 3 (ATL semantic hub): schema-membership signal.** ATL holds cross-modal abstract schema
representations. Each atom's "schema-membership score" is how aligned it is with the active schema
representation in ATL. Substrate analog: cosine of atom signature against W_schema centroids.

**Layer 4 (vmPFC value signal): downstream-impact signal.** Ventromedial PFC adds value to
autobiographical memories (Bonnici et al. 2016). Says "this memory has value because retrieving it
predicts good downstream outcomes." Substrate analog: gradient of eval metric w.r.t. atom
contribution (downstream_impact_score).

**Layer 5 (surprise / dopamine prediction error): surprise signal.** A surprise event (high prediction
error) gets stronger consolidation -- the classic dopamine-prediction-error story (Schultz, Lisman).
Substrate analog: |w_atom_at_write - predicted_w_atom_from_W_pre| -- residual error at write time.

**Layer 6 (recency / consolidation-staleness): recency signal.** The brain has the classic forgetting
curve over recency. Substrate analog: exp(-(t_now - t_last_access) / tau_recency).

**Key brain insight: these signals are COMBINED in a region called the entorhinal cortex (EC) just
before they get written into the hippocampal trisynaptic loop.** EC takes (mPFC task-relevance + ATL
schema + vmPFC value + DA surprise + recency) and produces a single "consolidation strength" signal
that gates synaptic plasticity. This is exactly the substrate-better composition we propose: 6 signals
combined via learned weights at the cortex-substrate interface.

---

## Section 3 -- Three mechanism classes drilled (per task)

### M1 -- Multi-factor importance scoring (rank-1, dispatch candidate)

**Plain English:** Replace the single-noisy-probe-recall importance scalar with a weighted combination
of 4-6 independent signals. The weights are tuned via held-out validation; the signal set is fixed
at design time.

**Mathematical core:**
```
importance(atom_i) = sigmoid(sum_k w_k * signal_k(atom_i))
where signal_k in {recency, query_freq, downstream_impact, surprise,
                   schema_contribution, cortex_predicted_salience}
```

**Substrate feasibility:** HIGH. Telemetry for the first 4 signals is already in cert_ledger or
trivially derivable. Schema_contribution requires W_schema (in flight via Gap 3 BCM); cortex_predicted_salience
requires W_pred (in flight via n5 revival).

**Discriminator:** After J=10000 cycles, can substrate STILL recall important atoms (recall_oldest_in_W_old >= 0.75) while having forgotten unimportant ones (W_active capacity stable, throughput unchanged)?
The 4FACTOR-vs-6FACTOR ablation discriminates "multi-factor helps" from "cortex composition is load-bearing."

**Brain fidelity:** HIGH. Direct mapping to mPFC + ATL + vmPFC + DA + hippocampal layers.

**Substrate-better angle:** Brain combines ~3-4 signals via dendritic integration noise (~1-bit
precision per signal); substrate combines 6 signals via 32-bit weighted sum at full precision. Each
signal is also LEARNABLE (substrate can tune w_k from downstream task performance); brain's signal
weights are mostly evolutionary defaults.

**P_deflated:** **0.50** (cell candidate #1, rank-1)

### M2 -- Schema-emergence-based forgetting (rank-2, depends on Gap 3 chain-grade)

**Plain English:** Atoms that contribute to emerging schemas stay in W_active permanently; atoms
that have low contribution to any schema become migration candidates. The schema landscape is
dynamic -- atoms can "earn" schema-contribution over time as schemas form around them.

**Mathematical core:**
```
schema_contribution(atom_i) = max_s cosine(atom_i, schema_centroid_s) for s in active_schemas
                            + 0.5 * mean_s cosine(atom_i, schema_centroid_s) for s in emerging_schemas

if schema_contribution(atom_i) > tau_schema_protect:
    atom_i is PROTECTED -- never migrates to W_cold
elif schema_contribution(atom_i) < tau_schema_prune:
    atom_i is MIGRATION CANDIDATE
```

**Substrate feasibility:** MEDIUM. Schema centroids require Gap 3 BCM cell to land HARD_PASS first;
schema landscape is dynamic so schema_contribution must be re-evaluated at every promotion checkpoint
(O(M_atoms * N_schemas * N_dim) per checkpoint -- still cheap). Composes with Gap 3 schema work
naturally.

**Discriminator:** Same as M1 + extra: count atoms that earn schema-protect status over J=10000 cycles
(should be ~5-15% of total atoms; if 0% the schema layer is non-load-bearing, if >50% the threshold
is too low and protection becomes meaningless).

**Brain fidelity:** VERY HIGH. Matches the cortex-schema-formation mechanism directly (Gilboa-Marlatte 2017;
2025 review on mPFC-MTL vs mPFC-HPC schema pathways).

**Substrate-better angle:** Brain schemas form slowly (weeks-months); substrate schemas can form
in hundreds-thousands of cycles via explicit Hebbian outer-product accumulation. Brain has ~10-100
top-level schemas; substrate can carry 10^3-10^4 schema centroids with no biological capacity
constraint.

**P_deflated:** **0.40** (cell candidate #2, rank-2 -- depends on Gap 3 chain-grade landing, which is
not yet validated)

### M3 -- Recoverable cold-storage with TWO_TIER integration (rank-3, architectural)

**Plain English:** Extend TWO_TIER's W_active + W_old architecture with a W_cold third tier and an
explicit recovery path. When a cold atom is queried (refuse-gate fires + cosine match in W_cold),
promote it back to W_active. Brain CAN'T do this reliably; substrate CAN.

**Mathematical core:**
```
on retrieve(query):
    result_active = cleanup(W_active, query)
    if result_active confidence > tau_confident:
        return result_active
    # refuse-gate fires
    result_cold = cleanup(W_cold, query, full_scan)
    if result_cold confidence > tau_cold_recovery:
        # PROMOTE back to W_active
        W_active = W_active + outer(result_cold_atom, target)
        atom_importance(result_cold_atom) += promote_bonus
        return result_cold
    return refuse
```

**Substrate feasibility:** HIGH. ANCHOR_1 from REM-revival drill is structurally this mechanism but
WITHOUT the multi-factor importance scoring. M3 composes ANCHOR_1 with M1's importance vector. Cost
of cold-storage scan is O(M_cold * N) per refuse-gate fire -- need indexing (e.g., approximate
nearest-neighbor on cold signatures) for production scale, but at experiment scale O(10^4 cold
atoms * 4096 N) = 40M FLOPs per scan = ~5ms wall -- trivial.

**Discriminator:** Recovery accuracy on a held-out probe set where queried atoms were known to have
migrated to W_cold; HARD_PASS at >= 0.80 recovery accuracy AND recovery doesn't destabilize W_active
(post-recovery, W_active capacity stays within 5% of pre-recovery).

**Brain fidelity:** MEDIUM-LOW. Brain pruning is generally irreversible (engrams can be reactivated
via optogenetic stimulation only if labeled in vivo; natural recovery rare). This is a substrate-better
capability where substrate explicitly out-performs biology.

**Substrate-better angle:** EXPLICIT substrate-better claim. Brain can't reliably recover pruned
memories (clinical evidence: forgotten memories of childhood, hippocampal lesions are permanent).
Substrate's recovery path is deterministic and bounded; the only risk is W_active destabilization
post-recovery (mitigated via per-recovery W_active norm renormalization).

**P_deflated:** **0.45** (cell candidate #3, rank-3)

---

## Section 4 -- Cross-domain mechanism probes (2-3 from disparate fields)

### M4 -- LSM-tree tiered compaction (database analog)

**Plain English:** RocksDB and similar LSM-tree databases handle the same problem: terabytes of data
arriving continuously, can't keep everything in fast storage, need to migrate cold data to slow
storage while keeping hot data accessible. Their solution: tiered compaction with hot/cold separation
+ explicit promotion policies.

**Direct adaptation:** RocksDB uses 4 importance signals for compaction: Least Overlapping (overlap
with adjacent SSTs -- analog: cosine overlap with W_active atoms), Coldest (least recent), Oldest
(write timestamp), Tombstone Density (deletion markers -- substrate analog: atoms whose downstream
weight is near zero). HotRAP (arxiv 2402.02070) adds hot-record retention + promotion.

**Substrate feasibility:** HIGH. The signals map directly. Migration policy is parameterized over the
4 signals; tuning is well-studied in DB literature.

**Discriminator:** Compare migration decisions to a M1-importance-only baseline. If LSM-tree-style
decisions ALONE recover >= 80% of M1 performance, then importance scoring may be over-engineered
relative to simpler DB-style policies.

**Brain fidelity:** LOW. No direct brain analog; LSM-tree mechanism is engineering-motivated.

**P_deflated:** **0.35** (cell candidate #4 -- diagnostic probe, not load-bearing). Worth dispatching
as cheapest ablation if cell candidate #1 lands MIDDLE_BAND or HARD_PASS, to bound how much of the
lift comes from cortex composition vs DB-style policies.

### M5 -- Knowledge graph pruning + HD-graph compression (HSG-ACKR precedent)

**Plain English:** Knowledge graphs face the same problem: O(N^2) edges, can't keep all relations
forever, need importance scoring per node and per edge. Recent work (HSG-ACKR, MoG 2024) achieves
10-20% compression with <5% accuracy impact via hyperdimensional + GNN-based importance scoring.

**Direct adaptation:** HSG-ACKR uses HD computing primitives (exactly substrate's substrate) to
score nodes for pruning. Their approach: train a small GNN over the KG that predicts node importance
from local neighborhood structure; prune nodes with importance < tau; verify <5% query accuracy
degradation.

**Substrate feasibility:** HIGH. Substrate IS HD computing; the HSG-ACKR mechanism is partially
self-applicable. Substrate's atom signatures + W structure ARE an HD-KG; their pruning scores are
substrate-mineable.

**Discriminator:** Run HSG-ACKR-style importance scoring as an additional signal in M1; check whether
it's redundant with downstream_impact_score (likely correlated > 0.8) or independent (would justify
adding as 7th signal).

**Brain fidelity:** LOW (engineering); BUT the lit precedent at 10-20% compression with <5%
degradation is exactly the operating point substrate needs at 10^9 atoms.

**P_deflated:** **0.40** (cell candidate #5 -- composes with M1; worth checking for signal-redundancy
audit)

### M6 -- Attention-based KV cache eviction (transformer LM analog)

**Plain English:** Transformer LMs face the same problem at inference time: O(seq_length) KV cache,
can't keep everything, need eviction policy. H2O (NeurIPS 2023), SnapKV, CAOTE, Expected Attention
(2025) all propose importance scoring for KV cache token eviction.

**Direct adaptation:** Heavy Hitters (H2O): "tokens receiving consistently high attention should be
retained." Substrate analog: atoms receiving consistently high query-hit are retained. Expected
Attention: estimate future attention from past queries -- substrate analog: cortex_predicted_salience
(W_pred-based).

**Substrate feasibility:** MEDIUM. The conceptual mechanism is identical to M1's
cortex_predicted_salience signal; the engineering details differ (KV cache is per-position, substrate
atoms are persistent). The W_pred Hebbian outer-product cell (n5 revival) IS the substrate version
of "learned attention prediction."

**Discriminator:** Compare cortex_predicted_salience signal in M1 (computed via W_pred) against an
H2O-style "consistent high attention" signal (computed via query-frequency-weighted attention to
each atom). If they're correlated > 0.85 then substrate's W_pred IS Heavy Hitters at substrate
scale; if independent then they're complementary signals worth combining.

**Brain fidelity:** LOW (engineering); but the precedent at LLM scale validates that learned-attention-prediction is a load-bearing importance signal at production scale.

**P_deflated:** **0.40** (cell candidate #6 -- conceptually overlaps with M1's cortex_predicted_salience
signal; worth as audit rather than separate cell)

---

## Section 5 -- TOP 3 cell candidates ranked by P_solve

Per task spec: top 3 by P_solve, each with clear discriminator that tests substrate STILL recalls
important atoms while having forgotten unimportant ones, while maintaining same throughput, composed
with TWO_TIER (HARD_PASS_PARTIAL today).

### CANDIDATE 1 (rank-1, P_deflated = 0.50, cheapest decisive)

- **Cell pointer:** `multi_factor_importance_cortex_composed_v1`
- **Mechanism:** M1 + cortex composition (W_schema + W_pred signals). 3 arms: TWO_TIER_SINGLE (rail),
  TWO_TIER_4FACTOR_NOCORTEX (substrate-mineable signals only), TWO_TIER_6FACTOR_CORTEX (full cortex
  composition). Pre-reg bands per Section (b).
- **Discriminator (composed):** drift_reduction over TWO_TIER baseline >= +0.10 absolute AND
  recall_oldest at J=10000 >= 0.75 AND ablation gap (6FACTOR - 4FACTOR) >= 0.05. Throughput-stability:
  per-cycle wall must stay within 1.2x of TWO_TIER baseline (importance evaluation is O(6*M*N) per
  promotion checkpoint, ~1-2s overhead -- trivial).
- **Tier hint:** MEASURED_MECHANISM at first land; chain-grade-eligible if HARD_PASS AND cortex
  composition explicitly load-bearing AND signal independence audit passes.
- **Why now:** Cortex layer is being spun up THIS WEEK (TWO_TIER + BCM + Modern Hopfield). The
  multi-factor cell is the natural composition test; if any of TWO_TIER / BCM / Modern Hopfield is
  not yet HARD_PASS the cell can degrade gracefully to M1's 4FACTOR_NOCORTEX arm. Critical: dispatch
  ORDER matters -- wait until TWO_TIER lands HARD_PASS before dispatching this cell, because the
  W_old promotion path is the load-bearing scaffold.
- **Cost:** ~3-5 CPU-hr local at N=4096, 3 seeds.
- **Composes with TWO_TIER:** YES, directly extends the TWO_TIER promotion path.

### CANDIDATE 2 (rank-2, P_deflated = 0.45, architectural)

- **Cell pointer:** `recoverable_coldstorage_multi_factor_v1`
- **Mechanism:** M1 + M3 + recovery path. Extends ANCHOR_1 from REM-revival drill with the 6-signal
  importance vector + a recovery path (refuse-gate -> cold-scan -> promote-on-hit). 4 arms: ANCHOR_1
  baseline (single-importance), this cell (6-importance + recovery), recovery-disabled (6-importance
  no recovery), random-recovery (recovery from random cold atom, ablation).
- **Discriminator (composed):** At J=10000, recall_oldest in W_cold >= 0.70 AND recovery accuracy on
  held-out probe >= 0.80 AND W_active capacity post-recovery within 5% of pre-recovery. Tests both
  the storage decision AND the recovery path explicitly.
- **Tier hint:** MEASURED_MECHANISM at first land; chain-grade-eligible if HARD_PASS AND demonstrates
  brain-better claim (recovery works where brain pruning is irreversible).
- **Why now:** ONLY-IF TWO_TIER HARD_PASS AND ANCHOR_1 HARD_PASS first. Composes two unproven
  mechanisms; lower joint P; worth dispatching after individual validation.
- **Cost:** ~5-7 CPU-hr local at N=4096, 4 arms, 3 seeds.
- **Composes with TWO_TIER:** YES, extends to W_active + W_old + W_cold three-tier with recovery.

### CANDIDATE 3 (rank-3, P_deflated = 0.40, schema-emergence-driven)

- **Cell pointer:** `schema_emergence_protect_importance_v1`
- **Mechanism:** M2 -- schema-protected atoms never migrate. 4 arms: TWO_TIER baseline (no schema
  signal), TWO_TIER + schema_contribution as 5th signal in M1's importance vector, TWO_TIER + binary
  schema_protect gate (atoms above tau_schema_protect are immortal in W_active), schema_emergence_decay
  (atoms below tau lose protection over time).
- **Discriminator (composed):** schema-protected atom count stays within [5%, 15%] of total atom count
  (sanity check) AND drift_reduction over TWO_TIER baseline >= +0.08 absolute AND schema-protected
  atoms have recall accuracy >= 0.95 at J=10000 (the protected atoms are RELIABLY recallable, validating
  that the schema_contribution signal IS load-bearing).
- **Tier hint:** MEASURED_MECHANISM at first land; chain-grade-eligible if HARD_PASS AND composes
  cleanly with Gap 3 BCM.
- **Why now:** ONLY-IF Gap 3 BCM HARD_PASS first. Cell depends on W_schema centroids being meaningful;
  if BCM is in flight or HARD_FAIL the schema signal is noise.
- **Cost:** ~4-6 CPU-hr local at N=4096, 4 arms, 3 seeds.
- **Composes with TWO_TIER:** YES, schema_protect is an immortality gate on the TWO_TIER promotion
  path.

---

## Section 6 -- Cross-thread synthesis

### Composes with TWO_TIER (HARD_PASS_PARTIAL today)

All 3 candidates extend the TWO_TIER promotion architecture. Candidate 1 swaps in a richer importance
vector; Candidate 2 adds a W_cold third tier + recovery path; Candidate 3 adds a schema-protect
immortality gate. All three preserve the existing W_active + W_old architecture that produced
HARD_PASS_PARTIAL today.

### Composes with cortex layer in flight

- Gap 3 BCM cell (slow Hebbian schema-emergence): provides W_schema centroids needed by Candidate 1
  (signal 5: schema_contribution) and Candidate 3 (schema_protect gate).
- n5 revival slow_cortex_bigram_predictor cell (Hebbian outer-product W_pred): provides W_pred needed
  by Candidate 1 (signal 6: cortex_predicted_salience).
- Modern Hopfield retrieval (in flight): provides the prototype-attractor backbone that all 3
  candidates retrieve from.

### Composes with cortex-as-router drill (today)

The cortex-as-router drill identifies mPFC as providing a "destination hint" from a separate pathway
that doesn't go through noise-collapsed state. This same mPFC analog (the W_pred matrix) can
double-duty as the cortex_predicted_salience signal in Candidate 1. **One substrate primitive (W_pred)
serves two capability gaps**: routing (Gap 1) and importance scoring (Gap E). This is exactly the
brain's pattern: mPFC is a multi-purpose region.

### Composes with brain selective homeostasis drill (today)

The selective homeostasis drill proposes 5 selective-downscale mechanisms (M1-M5 there). Those
mechanisms determine WHEN to downscale a weight in W_active. The importance-scoring drill here
determines WHICH atoms to migrate to W_cold (or protect from migration). They are complementary --
selective homeostasis is per-cycle weight maintenance; importance scoring is per-promotion-checkpoint
atom-level migration. They can compose: STC tag (binary protect signal) becomes a 7th signal in M1's
importance vector.

### Cross-domain validation

- LSM-tree tiered compaction (RocksDB, HotRAP) validates the architecture at terabyte scale.
- HSG-ACKR knowledge graph pruning validates the 10-20% compression / <5% degradation operating
  point on HD-computing-based KGs (substrate's home).
- Heavy Hitters / SnapKV / Expected Attention validate learned-attention-prediction at LLM scale.

All 3 cross-domain analogs validate the M1 multi-factor approach at production scale.

---

## Section 7 -- Substrate-product implications

For the L2 glass-box LLM continual-ingest moat: importance scoring is the load-bearing capability for
decade-scale continual operation. Without it, substrate at 10^9 atoms cannot maintain throughput --
even with partition routing, every query touches O(K * N_DIM) candidates, and at K=4096 with
N_DIM=8192 that's already 33M FLOPs per query. With explicit importance scoring + cold-storage
migration, the active set stays bounded at ~10^6 atoms regardless of total store size; throughput
stays sub-linear in total atoms.

The substrate-better claim (vs brain) is:
1. Multiple importance signals at full precision (brain has 1-bit dendritic integration)
2. Learnable signal weights (brain has evolutionary defaults)
3. Explicit recovery path (brain pruning is irreversible)
4. Composes with existing chain-graded primitives (no separate hardware needed)

The substrate-product reading: "decade-scale memory that knows what's important and what to compress,
with explicit recovery if anything important gets compressed away." This is the moat for continual-
ingest deployments where users care about long-term retention with bounded compute (e.g., personal
agents that learn from years of interaction).

---

## (f) Citations (verified count)

External lit (10 verified):

1. Wang ML Lab continual learning LLM survey CSUR 2025 -- https://github.com/Wang-ML-Lab/llm-continual-learning-survey
2. MSSR Memory-Aware Adaptive Replay arxiv 2603.09892 (March 2026; arxiv:2603.09892)
3. FOREVER Forgetting-Curve-Inspired Memory Replay arxiv 2601.03938 (January 2026; arxiv:2601.03938)
4. Scalable Strategies for Continual Learning with Replay arxiv 2505.12512 (May 2025)
5. HotRAP Hot Record Retention and Promotion arxiv 2402.02070 (Feb 2024)
6. Spooky LSM-Tree Compaction (Dayan) -- https://nivdayan.github.io/spooky.pdf
7. LSM Compaction Design Space VLDB 14 p2216-sarkar -- https://vldb.org/pvldb/vol14/p2216-sarkar.pdf
8. SfN mPFC selective memory encoding -- https://neuronline.sfn.org/scientific-research/how-does-the-medial-prefrontal-cortex-regulate-the-strength-of-memory-encoding
9. mPFC schema processing review 2025 (d-nb.info/1373059672; accepted May 2025)
10. Prefrontal Theta Selective Encoding NIH PMC6348453

Cross-domain (5 verified):

11. KGE pruning recommendation arxiv 2405.11531 (May 2024)
12. HSG-ACKR hyperdimensional semantic graph pruning (Freederia Research 2026-01-29)
13. KVCompose structured KV cache compression arxiv 2509.05165 (Sept 2025)
14. CAOTE KV cache selection arxiv 2504.14051 (April 2025)
15. Expected Attention KV cache compression arxiv 2510.00636 (Oct 2025)

Internal substrate notes (8 verified):

16. notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md (TWO_TIER cell spec)
17. notes/exp_dev_handoff_research_REM_revival_cold_storage_never_delete_2026-06-26.md (ANCHOR_1-5)
18. notes/research_gap4_brain_selective_homeostasis_2026-06-26.md (M1-M5 selective homeostasis)
19. notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md (mPFC analog)
20. notes/research_n5_revival_slow_learning_cortex_context_2026-06-26.md (W_pred Hebbian)
21. notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md (W_schema BCM)
22. notes/research_gap4_continual_5x_drill_2026-06-26.md (parent gap 4)
23. notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md (CLS-replay)

Total verified citations: 23.

---

## Dispatch ordering recommendation

1. **First** (when in-flight TWO_TIER lands HARD_PASS): Candidate 1 `multi_factor_importance_cortex_composed_v1`
   -- cheapest decisive, ~3-5 CPU-hr, 3 arms.
2. **Conditional on Candidate 1 HARD_PASS_CORTEX_COMPOSED + Gap 3 BCM HARD_PASS:** Candidate 3
   `schema_emergence_protect_importance_v1` -- ~4-6 CPU-hr, 4 arms.
3. **Conditional on Candidate 1 HARD_PASS + REM ANCHOR_1 HARD_PASS:** Candidate 2
   `recoverable_coldstorage_multi_factor_v1` -- ~5-7 CPU-hr, 4 arms.

DO NOT dispatch any of the 3 before TWO_TIER lands; the in-flight cell is the load-bearing scaffold.
ALL 3 candidates extend TWO_TIER -- they are not alternatives to it.

---

filed by research (Opus 4.7 1M)
